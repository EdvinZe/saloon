from collections.abc import Awaitable

from starlette.types import ASGIApp, Message, Receive, Scope, Send


class SecurityHeadersMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        async def send_with_headers(message: Message) -> None:
            if message["type"] == "http.response.start":
                headers = list(message.get("headers", []))
                header_names = {name.lower() for name, _ in headers}
                security_headers = [
                    (b"x-content-type-options", b"nosniff"),
                    (b"x-frame-options", b"DENY"),
                    (b"referrer-policy", b"strict-origin-when-cross-origin"),
                    (
                        b"permissions-policy",
                        b"camera=(), microphone=(), geolocation=()",
                    ),
                ]
                headers.extend(
                    (name, value)
                    for name, value in security_headers
                    if name not in header_names
                )
                message["headers"] = headers

            await send(message)

        await self.app(scope, receive, send_with_headers)


class RequestBodySizeLimitMiddleware:
    def __init__(self, app: ASGIApp, max_body_bytes: int) -> None:
        self.app = app
        self.max_body_bytes = max(1, max_body_bytes)

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        body_messages: list[Message] = []
        total_body_bytes = 0

        while True:
            message = await receive()
            body_messages.append(message)

            if message["type"] == "http.request":
                total_body_bytes += len(message.get("body", b""))
                if total_body_bytes > self.max_body_bytes:
                    await self._send_too_large_response(send)
                    return

                if not message.get("more_body", False):
                    break
            elif message["type"] == "http.disconnect":
                break

        receive_replay = _ReceiveReplay(body_messages)
        await self.app(scope, receive_replay, send)

    async def _send_too_large_response(self, send: Send) -> None:
        body = b'{"detail":"Request body too large"}'
        await send(
            {
                "type": "http.response.start",
                "status": 413,
                "headers": [
                    (b"content-type", b"application/json"),
                    (b"content-length", str(len(body)).encode("ascii")),
                ],
            }
        )
        await send({"type": "http.response.body", "body": body})


class _ReceiveReplay:
    def __init__(self, messages: list[Message]) -> None:
        self.messages = messages
        self.index = 0

    def __call__(self) -> Awaitable[Message]:
        return self._next_message()

    async def _next_message(self) -> Message:
        if self.index < len(self.messages):
            message = self.messages[self.index]
            self.index += 1
            return message

        return {"type": "http.request", "body": b"", "more_body": False}
