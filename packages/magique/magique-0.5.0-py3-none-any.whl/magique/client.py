import typing as T
import asyncio
import uuid
import inspect
import websockets

from .protocol import (
    ServiceInfo, InvokeServiceRequest, InvokeServiceResponse,
    InvokeFuture, GetFutureResultRequest, RegisterClientRequest,
)
from .utils.log import logger
from .ser import DefaultSerializer
from .utils.network import ws_connect
from .base import NetworkObject


class MagiqueError(Exception):
    pass


class MagiqueFutureError(MagiqueError):
    pass


class LoginError(MagiqueError):
    pass


class PyFunction:
    def __init__(self, func: T.Callable):
        self.func = func


class ServiceProxy(NetworkObject):
    def __init__(
        self,
        server_proxy: "ServerProxy",
        service_info: T.Optional[ServiceInfo] = None,
    ):
        super().__init__(server_proxy.serializer)
        self.server_proxy = server_proxy
        self.service_info = service_info
        self._recv_queues = {}

    async def ensure_connection(self):
        return await self.server_proxy.ensure_connection()

    async def _recv_invoke(self, websocket, invoke_id: str):
        while True:
            try:
                resp = await self.receive_message(websocket)
                r_id = resp.get("invoke_id")
                self._recv_queues[r_id].put_nowait(resp)
            except websockets.exceptions.ConcurrencyError:
                await asyncio.sleep(0.1)
                continue
            queue = self._recv_queues[invoke_id]
            resp = await queue.get()
            return resp

    async def invoke(
        self,
        function_name: str,
        parameters: dict | None = None,
        return_future: bool = False,
    ) -> T.Any:
        invoke_id = str(uuid.uuid4())
        if parameters is None:
            parameters = {}
        reverse_callables = {}
        for k, v in parameters.items():
            if isinstance(v, T.Callable):
                reverse_callables[k] = v
                _parameters = inspect.signature(v).parameters
                parameters[k] = {
                    "reverse_callable": True,
                    "name": k,
                    "invoke_id": invoke_id,
                    "parameters": list(_parameters.keys()),
                    "is_async": inspect.iscoroutinefunction(v),
                }
            elif isinstance(v, PyFunction):
                parameters[k] = v.func  # pass the function object

        request = InvokeServiceRequest(
            client_id=self.server_proxy.client_id,
            service_id=self.service_info.service_id,
            function_name=function_name,
            parameters=parameters,
            return_future=return_future,
            invoke_id=invoke_id,
        )
        websocket = await self.ensure_connection()
        await self.send_message(websocket, request.encode())
        self._recv_queues[invoke_id] = asyncio.Queue()
        response = None
        while True:
            resp = await self._recv_invoke(websocket, invoke_id)
            action = resp.get("action")
            logger.debug(f"Received action while waiting for result: {action}")
            if action == "reverse_invoke":
                await self.handle_reverse_invoke(websocket, resp, reverse_callables)
            else:
                if return_future:
                    response = InvokeFuture.decode(resp)
                else:
                    response = InvokeServiceResponse.decode(resp)
                    if resp.get("status") == "error":
                        raise MagiqueError(resp.get("message") or resp.get("result"))
                    response = response.result
                break
        del self._recv_queues[invoke_id]
        return response

    async def handle_reverse_invoke(self, websocket, request: dict, reverse_callables: dict):
        name = request["name"]
        parameters = request["parameters"]
        func = reverse_callables[name]
        try:
            if inspect.iscoroutinefunction(func):
                result = await func(**parameters)
            else:
                result = func(**parameters)
            status = "success"
        except Exception as e:
            result = str(e)
            status = "error"
        await self.send_message(websocket, {
            "action": "reverse_invoke_result",
            "result": result,
            "status": status,
            "reverse_invoke_id": request["reverse_invoke_id"],
            "service_id": request["service_id"],
        })

    async def fetch_service_info(self) -> ServiceInfo:
        request = {"action": "get_service_info"}
        if self.service_info is not None:
            request["name_or_id"] = self.service_info.service_id
        websocket = await self.ensure_connection()
        await self.send_message(websocket, request)
        resp = await self.receive_message(websocket)
        if resp.get("status") == "error":
            raise MagiqueError(resp.get("message"))
        response = ServiceInfo.decode(resp["service"])
        self.service_info = response
        return response

    async def fetch_future_result(self, future: InvokeFuture) -> T.Any:
        request = GetFutureResultRequest(future)
        websocket = await self.ensure_connection()
        await self.send_message(websocket, request.encode())
        resp = await self.receive_message(websocket)
        if resp.get("status") == "error":
            raise MagiqueFutureError(resp.get("message"))
        response = InvokeServiceResponse.decode(resp)
        return response.result

    async def close_connection(self):
        await self.server_proxy.close_connection()


class ServerProxy(NetworkObject):
    def __init__(
        self,
        url: str,
        serializer: T.Optional[DefaultSerializer] = None,
    ):
        super().__init__(serializer or DefaultSerializer())
        self.url = url
        self.jwt = None
        self.client_id = str(uuid.uuid4())
        self._connection = None

    async def register(self):
        request = RegisterClientRequest(client_id=self.client_id)
        websocket = await ws_connect(self.url)
        self._connection = websocket
        await self.send_message(websocket, request.encode())
        response = await self.receive_message(websocket)
        if response.get("status") == "error":
            raise MagiqueError(response.get("message"))
        logger.info(f"Connected to server at {self.url}")

    async def is_connected(self) -> bool:
        if self._connection is None:
            return False
        try:
            await self._connection.ping()
        except Exception:
            return False
        return True

    async def ensure_connection(self, retry_count: int = 3, retry_delay: float = 0.5):
        for _ in range(retry_count):
            if (await self.is_connected()):
                return self._connection
            try:
                await self.register()
                return self._connection
            except Exception as e:
                logger.error(f"Failed to connect to server: {e}, retrying...")
                await asyncio.sleep(retry_delay)
        raise MagiqueError("Failed to connect to server")

    async def list_services(self) -> T.List[ServiceInfo]:
        await self.ensure_connection()
        await self.send_message(
            self._connection,
            {"action": "get_services", "jwt": self.jwt}
        )
        response = await self.receive_message(self._connection)
        services = [
            ServiceInfo.decode(service)
            for service in response["services"]
        ]
        return services

    async def get_service(
        self,
        name_or_id: str,
        choice_strategy: T.Literal["random", "first"] = "first",
    ) -> ServiceProxy:
        request = {
            "action": "get_service_info",
            "name_or_id": name_or_id,
            "choice_strategy": choice_strategy,
            "jwt": self.jwt,
        }
        await self.ensure_connection()
        await self.send_message(self._connection, request)
        resp = await self.receive_message(self._connection)
        if resp.get("status") == "error":
            raise MagiqueError(resp.get("message"))
        service = ServiceInfo.decode(resp["service"])
        proxy = ServiceProxy(
            self,
            service,
        )
        return proxy

    async def ping(self):
        await self.ensure_connection()
        await self.send_message(self._connection, {"action": "ping"})
        msg = await self.receive_message(self._connection)
        assert msg["message"] == "pong"

    async def login(self):
        if self.jwt is not None:
            logger.info("Already logged in.")
            return
        await self.ensure_connection()
        await self.send_message(self._connection, {"action": "login"})
        msg = await self.receive_message(self._connection)
        auth_url = msg["auth_url"]
        logger.info(f"Open this URL in your browser to log in:\n{auth_url}")
        msg = await self.receive_message(self._connection)
        if msg.get("status") == "error":
            raise LoginError(msg.get("message"))
        jwt = msg.get("jwt")
        self.jwt = jwt
        logger.info("Login successful!")

    async def close_connection(self):
        if self._connection is not None:
            await self._connection.close()
            self._connection = None


async def connect_to_server(
    url: str,
    **kwargs,
) -> ServerProxy:
    server = ServerProxy(
        url,
        **kwargs,
    )
    await server.ensure_connection()
    return server

