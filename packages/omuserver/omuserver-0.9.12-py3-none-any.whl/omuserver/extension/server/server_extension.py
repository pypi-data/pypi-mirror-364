from __future__ import annotations

import os
from asyncio import Future
from collections import defaultdict
from collections.abc import Callable
from typing import TYPE_CHECKING

from loguru import logger
from omu.address import get_lan_ip
from omu.app import App
from omu.errors import PermissionDenied
from omu.extension.dashboard.packets import PermissionRequestPacket
from omu.extension.permission.permission import PermissionType
from omu.extension.server.server_extension import (
    REMOTE_APP_REQUEST_ENDPOINT_TYPE,
    REQUIRE_APPS_PACKET_TYPE,
    SERVER_APP_TABLE_TYPE,
    SERVER_SESSION_TABLE_TYPE,
    SESSION_CONNECT_PACKET_TYPE,
    SESSION_DISCONNECT_PACKET_TYPE,
    SESSION_OBSERVE_PACKET_TYPE,
    SHUTDOWN_ENDPOINT_TYPE,
    TRUSTED_ORIGINS_REGISTRY_TYPE,
)
from omu.extension.server.types import RemoteAppRequestPayload, RequestRemoteAppResponse
from omu.identifier import Identifier
from omu.network.packet.packet_types import DisconnectType

from omuserver.session import Session

from .permissions import (
    REMOTE_APP_REQUEST_PERMISSION,
    SERVER_APPS_READ_PERMISSION,
    SERVER_SESSIONS_READ_PERMISSION,
    SERVER_SHUTDOWN_PERMISSION,
    SERVER_TRUSTED_ORIGINS_GET_PERMISSION,
)

if TYPE_CHECKING:
    from loguru import Message

    from omuserver.server import Server


class WaitHandle:
    def __init__(self, ids: list[Identifier]):
        self.future = Future()
        self.ids = ids


class LogHandler:
    def __init__(
        self,
        callback: Callable[[str], None],
    ) -> None:
        self.callback = callback

    def write(self, message: Message) -> None:
        self.callback(message)


class ServerExtension:
    def __init__(self, server: Server) -> None:
        self._server = server
        server.packets.register(
            REQUIRE_APPS_PACKET_TYPE,
            SESSION_OBSERVE_PACKET_TYPE,
            SESSION_CONNECT_PACKET_TYPE,
            SESSION_DISCONNECT_PACKET_TYPE,
        )
        server.security.register(
            SERVER_SHUTDOWN_PERMISSION,
            SERVER_APPS_READ_PERMISSION,
            SERVER_SESSIONS_READ_PERMISSION,
            SERVER_TRUSTED_ORIGINS_GET_PERMISSION,
            REMOTE_APP_REQUEST_PERMISSION,
        )
        server.endpoints.bind(SHUTDOWN_ENDPOINT_TYPE, self.handle_shutdown)
        server.endpoints.bind(REMOTE_APP_REQUEST_ENDPOINT_TYPE, self.handle_remote_app_request)
        server.packets.bind(REQUIRE_APPS_PACKET_TYPE, self.handle_require_apps)
        server.packets.bind(SESSION_OBSERVE_PACKET_TYPE, self.handle_observe_session)
        server.network.event.connected += self.on_connected
        server.network.event.disconnected += self.on_disconnected
        server.event.start += self.on_start
        self.apps = self._server.tables.register(SERVER_APP_TABLE_TYPE)
        self.sessions = self._server.tables.register(SERVER_SESSION_TABLE_TYPE)
        self.trusted_origins = self._server.registries.register(TRUSTED_ORIGINS_REGISTRY_TYPE)
        self._app_waiters: dict[Identifier, list[WaitHandle]] = defaultdict(list)
        self._session_observers: dict[Identifier, list[Session]] = defaultdict(list)

    async def handle_require_apps(self, session: Session, app_ids: list[Identifier]) -> None:
        for identifier in self._server.network._sessions.keys():
            if identifier not in app_ids:
                continue
            app_ids.remove(identifier)
        if len(app_ids) == 0:
            return

        async def task():
            waiter = WaitHandle(app_ids)
            for app_id in app_ids:
                self._app_waiters[app_id].append(waiter)
            await waiter.future

        session.add_ready_task(task)

    async def handle_observe_session(self, session: Session, app_ids: list[Identifier]) -> None:
        if not session.permissions.has(SERVER_SESSIONS_READ_PERMISSION.id):
            raise PermissionDenied(f"Pemission {SERVER_SESSIONS_READ_PERMISSION.id} required to observe session")
        for app_id in app_ids:
            self._session_observers[app_id].append(session)

            def on_disconnect(session, app_id=app_id):
                if session in self._session_observers[app_id]:
                    self._session_observers[app_id].remove(session)

            session.event.disconnected.listen(on_disconnect)

    async def handle_shutdown(self, session: Session, restart: bool = False) -> bool:
        await self.shutdown(restart)
        return True

    async def handle_remote_app_request(
        self, session: Session, request: RemoteAppRequestPayload
    ) -> RequestRemoteAppResponse:
        id = Identifier.from_key(request["id"])
        url = request["url"]
        metadata = request["metadata"]
        permission_ids = list(map(Identifier.from_key, request["permissions"]))
        permissions: list[PermissionType] = []
        for permission_id in permission_ids:
            permission = self._server.security.get_permission(permission_id)
            if permission is None:
                raise ValueError(f"Permission {permission_id} not found")
            permissions.append(permission)

        temp_app = App(
            id=id,
            url=url,
            metadata={
                "locale": metadata["locale"],
                "name": metadata.get("name"),
                "icon": metadata.get("icon"),
                "description": metadata.get("description"),
            },
        )
        permission_request = PermissionRequestPacket(
            request_id=self._server.dashboard.gen_next_request_id(),
            app=temp_app,
            permissions=permissions,
        )
        accepted = await self._server.dashboard.request_permissions(permission_request)
        if not accepted:
            return {"type": "error", "message": "Permission denied"}
        token = self._server.security.generate_remote_token(temp_app)
        self._server.security.set_permissions(token, *permission_ids)
        return {
            "type": "success",
            "token": token,
            "lan_ip": get_lan_ip(),
        }

    async def shutdown(self, restart: bool = False) -> None:
        try:
            if restart:
                for session in [*self._server.network._sessions.values()]:
                    if session.closed:
                        continue
                    await session.disconnect(DisconnectType.SERVER_RESTART, "Server is restarting")
                await self._server.restart()
            else:
                await self._server.stop()
        finally:
            os._exit(0)

    async def on_start(self) -> None:
        await self.sessions.clear()

    async def on_connected(self, session: Session) -> None:
        logger.info(f"Connected: {session.app.key()}")
        await self.sessions.add(session.app)
        await self.apps.add(session.app)

        unlisten = session.event.ready.listen(self.on_session_ready)
        session.event.disconnected.listen(lambda _: unlisten())

    async def on_session_ready(self, session: Session) -> None:
        for waiter in self._app_waiters.get(session.app.id, []):
            if session.app.id in waiter.ids:
                waiter.ids.remove(session.app.id)
            if len(waiter.ids) == 0:
                waiter.future.set_result(True)
        for observer in self._session_observers.get(session.app.id, []):
            await observer.send(
                SESSION_CONNECT_PACKET_TYPE,
                session.app,
            )

    async def on_disconnected(self, session: Session) -> None:
        logger.info(f"Disconnected: {session.app.key()}")
        await self.sessions.remove(session.app)

        for observer in self._session_observers.get(session.app.id, []):
            if session.closed:
                continue
            await observer.send(SESSION_DISCONNECT_PACKET_TYPE, session.app)
