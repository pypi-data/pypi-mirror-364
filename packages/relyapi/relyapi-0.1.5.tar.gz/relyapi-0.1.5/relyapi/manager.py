import importlib
import os
from typing import Dict, Any

from loguru import logger

from relyapi.plugin import BasePlugin, RequestModel
from relyapi.utils import random_ua


class CommonPlugin(BasePlugin):
    use_proxy = True
    timeout = 10

    def invoke(self, url, method, headers: Dict[str, str], body: Dict[str, Any]) -> RequestModel:
        if 'user-agent' not in headers:
            headers['user-agent'] = random_ua
        return RequestModel(url=url, method=method, headers=headers, json=body)


class PluginManager:
    def __init__(self):
        self.plugins: Dict[str, BasePlugin] = {}

    def register(self, plugin):
        if not issubclass(plugin, BasePlugin):
            raise TypeError(f"{plugin.__name__} 必须继承自 BasePlugin")
        instance_obj = plugin()
        if isinstance(instance_obj.domain, list):
            for domain in instance_obj.domain:
                self.plugins[domain] = instance_obj
        else:
            self.plugins[instance_obj.domain] = instance_obj

    def get(self, domain: str) -> BasePlugin:
        return self.plugins.get(domain, CommonPlugin())


plugin_manager = PluginManager()


def load_plugins(plugins_path):
    logger.info(f"Loading plugins from {plugins_path}")
    for filename in os.listdir(os.path.join(plugins_path, "plugins")):
        if filename.endswith(".py") and filename != "__init__.py":
            module_name = f"plugins.{filename[:-3]}"
            module = importlib.import_module(module_name)

            for attr_name in dir(module):
                attr: BasePlugin = getattr(module, attr_name)
                if (
                        isinstance(attr, type)
                        and issubclass(attr, module.BasePlugin)
                        and attr is not module.BasePlugin
                ):
                    logger.info(f"Loading {attr.domain} from {module_name}")
                    plugin_manager.register(attr)
