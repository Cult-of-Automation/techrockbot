# Original from Python Discord Bot
# https://github.com/python-discord/bot
import logging
import os
from collections.abc import Mapping
from pathlib import Path
from typing import Dict, List

import yaml

log = logging.getLogger(__name__)

def _env_var_constructor(loader, node):
    """
    Implements a custom YAML tag for loading optional environment
    variables. If the environment variable is set, returns the
    value of it. Otherwise, returns `None`.
    Example usage in the YAML configuration:
        # Optional app configuration. Set `MY_APP_KEY` in the environment to use it.
        application:
            key: !ENV 'MY_APP_KEY'
    """

    default = None

    # Check if the node is a plain string value
    if node.id == 'scalar':
        value = loader.construct_scalar(node)
        key = str(value)
    else:
        # The node value is a list
        value = loader.construct_sequence(node)

        if len(value) >= 2:
            # If we have at least two values, then we have both a key and a default value
            default = value[1]
            key = value[0]
        else:
            # Otherwise, we just have a key
            key = value[0]

    return os.getenv(key, default)

def _join_var_constructor(loader, node):
    """
    Implements a custom YAML tag for concatenating other tags in
    the document to strings. This allows for a much more DRY configuration
    file.
    """

    fields = loader.construct_sequence(node)
    return "".join(str(x) for x in fields)

yaml.SafeLoader.add_constructor('!ENV', _env_var_constructor)
yaml.SafeLoader.add_constructor('!JOIN', _join_var_constructor)

with open('config.yml', encoding="UTF-8") as f:
    _CONFIG_YAML = yaml.safe_load(f)

def check_required_keys(keys):
    """
    Verifies that keys that are set to be required are present in the
    loaded configuration.
    """
    for key_path in keys:
        lookup = _CONFIG_YAML
        try:
            for key in key_path.split('.'):
                lookup = lookup[key]
                if lookup is None:
                    raise KeyError(key)
        except KeyError:
            log.critical(
                f"A configuration for `{key_path}` is required, but was not found. "
                "Please set it in `config.yml` or setup an environment variable and try again."
            )
            raise

try:
    required_keys = _CONFIG_YAML['config']['required_keys']
except KeyError:
    pass
else:
    check_required_keys(required_keys)

class YAMLGetter(type):
    subsection = None

    def __getattr__(cls, name):
        name = name.lower()

        try:
            if cls.subsection is not None:
                return _CONFIG_YAML[cls.section][cls.subsection][name]
            return _CONFIG_YAML[cls.section][name]
        except KeyError:
            dotted_path = '.'.join(
                (cls.section, cls.subsection, name)
                if cls.subsection is not None else (cls.section, name)
            )
            log.critical(f"Tried accessing configuration variable at `{dotted_path}`, but it could not be found.")
            raise

    def __getitem__(cls, name):
        return cls.__getattr__(name)

# Dataclasses
class Bot(metaclass=YAMLGetter):
    section = 'bot'

    token: str
    test_token: str

class Colours(metaclass=YAMLGetter):
    section = 'style'
    subsection = 'colours'

    techrock: int

class Emojis(metaclass=YAMLGetter):
    section = 'style'
    subsection = 'emojis'

    thinking: str

    thumbs_up: str
    thumbs_down: str

    okay: str
    error: str
    warning: str
    loading: str

    circle_red: str
    circle_green: str
    circle_blue: str

class Icons(metaclass=YAMLGetter):
    section = 'style'
    subsection = 'icons'

    techrock: str
    techrock_square: str

class Server(metaclass=YAMLGetter):
    section = 'server'

    ftp: Dict[str, Dict[str, str]]