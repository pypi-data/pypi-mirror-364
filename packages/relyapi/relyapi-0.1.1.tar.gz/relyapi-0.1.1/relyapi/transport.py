import os

import httpx

RELY_API_ADDRESS = os.environ.get("RELY_API_ADDRESS", 'http://127.0.0.1:9000')


class ForwardingTransport(httpx.BaseTransport):
    def handle_request(self, request: httpx.Request) -> httpx.Response:
        payload = {
            "method": request.method,
            "url": str(request.url),
            "headers": dict(request.headers),
            "body": request.read().decode("utf-8") if request.content else None
        }

        forward_resp = httpx.post(f"{RELY_API_ADDRESS}/forward", json=payload)

        return httpx.Response(
            status_code=forward_resp.status_code,
            headers=forward_resp.headers,
            content=forward_resp.content,
            request=request
        )


class AsyncForwardingTransport(httpx.AsyncBaseTransport):
    async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
        payload = {
            "method": request.method,
            "url": str(request.url),
            "headers": dict(request.headers),
            "body": await request.aread()
        }

        async with httpx.AsyncClient() as client:
            forward_resp = await client.post(f"{RELY_API_ADDRESS}/forward", json=payload)

        return httpx.Response(
            status_code=forward_resp.status_code,
            headers=forward_resp.headers,
            content=forward_resp.content,
            request=request
        )
