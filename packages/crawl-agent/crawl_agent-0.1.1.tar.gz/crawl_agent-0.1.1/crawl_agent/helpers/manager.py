import importlib.util
import os
import sys
from typing import Dict, Type

from loguru import logger

from crawl_agent.helpers.drssionpage import DrissionPageBase


class ControlManager:
    def __init__(self):
        self.plugins: Dict[str, DrissionPageBase] = {}

    def register(self, plugin: Type[DrissionPageBase]):
        if not issubclass(plugin, DrissionPageBase):
            raise TypeError(f"{plugin.__name__} 必须继承自 DrissionPageBase")
        instance_obj = plugin()
        if isinstance(instance_obj.site_name, list):
            for domain in instance_obj.site_name:
                self.plugins[domain] = instance_obj
        else:
            self.plugins[instance_obj.site_name] = instance_obj

    def get(self, domain: str) -> DrissionPageBase:
        return self.plugins.get(domain)


control_manager = ControlManager()


def load_sites(plugins_path):
    logger.info(f"Recursively loading plugins from {plugins_path}")
    for root, dirs, files in os.walk(plugins_path):
        # 过滤掉 test 和 tests 目录
        dirs[:] = [d for d in dirs if d not in ("test", "tests")]

        for file in files:
            if file.endswith(".py") and file != "__init__.py":
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, os.getcwd())
                module_name = rel_path[:-3].replace(os.sep, ".")

                try:
                    spec = importlib.util.spec_from_file_location(module_name, file_path)
                    if spec and spec.loader:
                        module = importlib.util.module_from_spec(spec)
                        sys.modules[module_name] = module
                        spec.loader.exec_module(module)

                        for attr_name in dir(module):
                            attr = getattr(module, attr_name)
                            if (
                                    isinstance(attr, type)
                                    and issubclass(attr, DrissionPageBase)
                                    and attr is not DrissionPageBase
                            ):
                                logger.info(f"Registering {attr.__name__} from {module_name}")
                                control_manager.register(attr)
                except Exception as e:
                    logger.error(f"Failed to load {module_name}: {e}")
