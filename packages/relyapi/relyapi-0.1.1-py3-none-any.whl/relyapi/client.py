import httpx

from relyapi.transport import ForwardingTransport


class Client(httpx.Client):
    def __init__(self, *args, **kwargs):
        kwargs["transport"] = ForwardingTransport()
        super().__init__(*args, **kwargs)
