from __future__ import annotations

import abc
import asyncio
from dataclasses import dataclass
from typing import TYPE_CHECKING

from loguru import logger
from omu import App
from omu.app import AppType
from omu.errors import DisconnectReason
from omu.event_emitter import EventEmitter
from omu.helper import Coro
from omu.identifier import Identifier
from omu.network.packet import PACKET_TYPES, Packet, PacketType
from omu.network.packet.packet_types import DisconnectPacket, DisconnectType
from omu.network.packet_mapper import PacketMapper
from omu.result import Err, Ok, Result

from omuserver.error import ServerError

if TYPE_CHECKING:
    from omuserver.security import PermissionHandle
    from omuserver.server import Server


class ConnectionClosed(ServerError): ...


class ErrorReceiving(ServerError): ...


class InvalidPacket(ServerError): ...


type ReceiveError = ConnectionClosed | ErrorReceiving | InvalidPacket


class SessionConnection(abc.ABC):
    @abc.abstractmethod
    async def send(self, packet: Packet, packet_mapper: PacketMapper) -> None: ...

    @abc.abstractmethod
    async def receive(self, packet_mapper: PacketMapper) -> Result[Packet, ReceiveError]: ...

    async def receive_as[T](self, packet_mapper: PacketMapper, packet_type: PacketType[T]) -> Result[T, ReceiveError]:
        packet = await self.receive(packet_mapper)
        if packet.is_err is True:
            return Err(packet.err)
        packet = packet.value
        if packet.type != packet_type:
            return Err(InvalidPacket(f"Expected {packet_type.id} but got {packet.type}"))
        return Ok(packet.data)

    @abc.abstractmethod
    async def close(self) -> None: ...

    @property
    @abc.abstractmethod
    def closed(self) -> bool: ...


class SessionEvents:
    def __init__(self) -> None:
        self.packet = EventEmitter[Session, Packet]()
        self.disconnected = EventEmitter[Session](catch_errors=True)
        self.ready = EventEmitter[Session]()


@dataclass(frozen=True, slots=True)
class SessionTask:
    session: Session
    coro: Coro[[], None]
    name: str


class Session:
    def __init__(
        self,
        packet_mapper: PacketMapper,
        app: App,
        permission_handle: PermissionHandle,
        kind: AppType,
        connection: SessionConnection,
    ) -> None:
        self.packet_mapper = packet_mapper
        self.app = app
        self.permissions = permission_handle
        self.kind = kind
        self.connection = connection
        self.event = SessionEvents()
        self.ready_tasks: list[SessionTask] = []
        self.ready_waiters: list[asyncio.Future[None]] = []
        self.ready = False

    @classmethod
    async def from_connection(
        cls,
        server: Server,
        packet_mapper: PacketMapper,
        connection: SessionConnection,
    ) -> Session:
        received = await connection.receive_as(packet_mapper, PACKET_TYPES.CONNECT)
        if received.is_err is True:
            await connection.send(
                Packet(PACKET_TYPES.DISCONNECT, DisconnectPacket(DisconnectType.INVALID_PACKET, received.err.message)),
                packet_mapper,
            )
            await connection.close()
            raise RuntimeError(f"Invalid packet received while connecting: {received.err}")
        else:
            packet = received.value

        verify_result = await server.security.verify_token(packet.app, packet.token)
        if verify_result.is_err is True:
            await connection.send(
                Packet(PACKET_TYPES.DISCONNECT, DisconnectPacket(DisconnectType.INVALID_TOKEN, verify_result.err)),
                packet_mapper,
            )
            await connection.close()
            raise RuntimeError(f"Invalid token for {packet.app}: {verify_result.err}")
        permission_handle, new_token = verify_result.value
        session = Session(
            packet_mapper=packet_mapper,
            app=packet.app,
            permission_handle=permission_handle,
            kind=packet.app.type or AppType.APP,
            connection=connection,
        )
        if session.kind != AppType.PLUGIN:
            await session.send(PACKET_TYPES.TOKEN, new_token)
        return session

    @property
    def closed(self) -> bool:
        return self.connection.closed

    async def disconnect(self, disconnect_type: DisconnectType, message: str | None = None) -> None:
        if not self.connection.closed:
            await self.send(PACKET_TYPES.DISCONNECT, DisconnectPacket(disconnect_type, message))
        await self.connection.close()
        await self.event.disconnected.emit(self)

    async def listen(self) -> None:
        while not self.connection.closed:
            received = await self.connection.receive(self.packet_mapper)
            if received.is_err is True:
                await self.disconnect(DisconnectType.INVALID_PACKET, received.err.message)
                return
            asyncio.create_task(self.dispatch_packet(received.value))

    async def dispatch_packet(self, packet: Packet) -> None:
        try:
            await self.event.packet.emit(self, packet)
        except DisconnectReason as reason:
            logger.opt(exception=reason).error("Disconnecting session")
            await self.disconnect(reason.type, reason.message)

    async def send[T](self, packet_type: PacketType[T], data: T) -> None:
        await self.connection.send(Packet(packet_type, data), self.packet_mapper)

    def add_ready_task(self, coro: Coro[[], None]):
        if self.ready:
            raise RuntimeError("Session is already ready")
        task = SessionTask(session=self, coro=coro, name=coro.__name__)
        self.ready_tasks.append(task)

    async def wait_ready(self) -> None:
        if self.ready:
            return
        waiter = asyncio.get_running_loop().create_future()
        self.ready_waiters.append(waiter)
        await waiter

    async def process_ready_tasks(self) -> None:
        if self.ready:
            raise RuntimeError("Session is already ready")
        self.ready = True
        for task in self.ready_tasks:
            try:
                await task.coro()
            except Exception as e:
                logger.opt(exception=e).error(f"Error while processing ready task {task.name}")
                await self.disconnect(DisconnectType.INTERNAL_ERROR, "Error while processing ready tasks")
                return
        self.ready_tasks.clear()
        for waiter in self.ready_waiters:
            waiter.set_result(None)
        await self.event.ready.emit(self)

    def is_app_id(self, id: Identifier) -> bool:
        return self.app.id.is_namepath_equal(id, max_depth=1)

    def __repr__(self) -> str:
        return f"Session({self.app.key()}, kind={self.kind}, ready={self.ready})"
