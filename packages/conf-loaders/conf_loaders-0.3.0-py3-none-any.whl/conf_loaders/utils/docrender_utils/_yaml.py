
"""
creates yaml-based functions according to existing machine configuration state
"""

from typing import Dict

import yaml

try:
    from yaml import CLoader as Loader, CDumper as Dumper
    LIBYAML_AVAILABLE = True
except ImportError:
    from yaml import Loader, Dumper
    LIBYAML_AVAILABLE = False

# to ignore &id001 like links
Dumper.ignore_aliases = lambda *args: True

_dump_kwargs = dict(
    default_flow_style=False
)


def yaml_load(stream) -> Dict:
    return yaml.load(stream, Loader=Loader)


def yaml_dump(data, **kwargs) -> str:
    return yaml.dump(
        data, Dumper=Dumper, encoding='utf-8', allow_unicode=True, **{**_dump_kwargs, **kwargs}
    ).decode()
