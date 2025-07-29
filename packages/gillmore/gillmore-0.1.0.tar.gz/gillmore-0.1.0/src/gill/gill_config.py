# Copyright 2025 Marek Antoni Kurczynski (also known as Mark Alexander Anthony)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os

import tomllib                          # For reading
import toml                             # For writing

def load_toml(toml_path: str) -> dict[str, dict[str, str]]:
    try:
        with open(toml_path, "rb") as f:
            return tomllib.load(f)
    except Exception as e:
        raise ConfigError(f"Failed to load TOML file'{toml_path}': {e}")
    
def get_config_path() -> str:
    cwd = os.getcwd()
    config_path = os.path.join(cwd, ".gill", "config.toml")
    return config_path

class ConfigError(Exception):
    """Custom exception for config errors."""
    pass

def gill_config(args: list[str]) -> None:
    """
    Handle config commands like setting and listing config entries.
    Expected usage examples:
        gill_config(["set", "llm.provider", "OpenAI"])
        gill_config(["llm.model"])
        gill_config(["--list"])

        See list of OpenAI models at : https://platform.openai.com/docs/models
    """
    if not args:
        raise ConfigError("No command specified. Use 'set', or 'list', or a section.key to get a value.")

    config_path = get_config_path()

    if not os.path.isfile(config_path):                                             # Checking config file exists
        raise ConfigError(f"No config file found at '{config_path}'. Try initializing in the working directory again.")
    config = load_toml(config_path)                                               # Load existing config as Python dict with string keys

    command = args[0]

    # Changing the config:
    if command == "set": 
        if len(args) != 3:
            raise ConfigError("Usage: set <section.key> <value>")
        try:
            section, key = args[1].split(".", 1)  # Only split on first dot
        except ValueError:
            raise ConfigError("Config key must be in the format <section.key>")
        value = args[2]
        update_toml_file(config_path, section, key, value, config)
        return

    # Displaying config values
    elif command == "--list" or "list":
        if not len(args) == 1:
            raise ConfigError("Use `list` to display config values.")
        # Pretty print the entire config
        print_toml(config)

    elif len(args) == 1:
        # If neither, check is a section.key pair and show value
        try:
            section, key = args[0].split(".", 1)  # Only split on first dot
        except ValueError:
            raise ConfigError("Config key must be in the format <section.key>")
        
        if section not in config or not isinstance(config[section], dict):
            raise ConfigError(f"The section '{section}' is not part of the config.")
        if key not in config[section]:
            raise ConfigError(f"The key '{key}' is not found under section '{section}'.")

        value = config[section][key]
        print(value)

    else:
        raise SyntaxError(f"Unknown command or incorrect arguments: {' '.join(args)}")

    return

def print_toml(toml_as_dict: dict) -> None:
    """Pretty-print TOML config dictionary."""
    toml_string = toml.dumps(toml_as_dict).strip()
    print(toml_string)

def update_toml_file(path: str, section: str, key: str, value: str, current_config: dict) -> None:
    # Mutable copy
    config = dict(current_config)

    if section not in config or not isinstance(config[section], dict):
        raise ConfigError(f"The section '{section}' is not part of the config.")
    if key not in config[section]:
        raise ConfigError(f"The key '{key}' is not found under section '{section}'.")

    # Update value - note: value is stored as string; consider casting if needed later. For now just strings used.
    config[section][key] = value

    try:
        with open(path, "w") as f:
            toml.dump(config, f)
    except Exception as e:
        raise ConfigError(f"Failed to write config file '{path}': {e}")
