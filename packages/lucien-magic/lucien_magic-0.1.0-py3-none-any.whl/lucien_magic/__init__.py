import os

from jsonrpc.proxy import JSONRPCProxy

_lucien = JSONRPCProxy.from_url(os.environ["LUCIEN_RPC_URL"])


def load_ipython_extension(ipython):
    ipython.user_ns["lucien"] = _lucien


def unload_ipython_extension(ipython):
    if "lucien" in ipython.user_ns:
        del ipython.user_ns["lucien"]
