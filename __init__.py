"""
@author: Dries
@title: X-Design
@nickname: X-Design
@description: X-Design Node
"""

import importlib
import logging

version_code = [1, 2, 9]
version_str = f"V{version_code[0]}.{version_code[1]}" + (f'.{version_code[2]}' if len(version_code) > 2 else '')
logging.info(f"### Loading: comfyui-xdesign-nodes ({version_str})")

node_list = [
    "image_loader_nodes",
]

NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}

for module_name in node_list:
    imported_module = importlib.import_module(".modules.{}".format(module_name), __name__)

    NODE_CLASS_MAPPINGS = {**NODE_CLASS_MAPPINGS, **imported_module.NODE_CLASS_MAPPINGS}
    NODE_DISPLAY_NAME_MAPPINGS = {**NODE_DISPLAY_NAME_MAPPINGS, **imported_module.NODE_DISPLAY_NAME_MAPPINGS}

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]

try:
    import cm_global
    cm_global.register_extension('comfyui-xdesign-nodes',
                                 {'version': version_code,
                                  'name': 'X Design',
                                  'nodes': set(NODE_CLASS_MAPPINGS.keys()),
                                  'description': 'X-Design customer node.', })
except:
    pass