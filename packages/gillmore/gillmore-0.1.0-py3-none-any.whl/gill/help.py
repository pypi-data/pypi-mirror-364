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

def print_help(command: str) -> None:
    match command:
        case "gill":
            help_text = """
Usage:
  gill ([-m|--message <text> ...]) [-f|--file <filename> ...] [-l|--line <range> ...] ...
  gill --test [-m|--message <text> ...] [-f|--file <filename> ...] [-l|--line <range> ...]

Options:
  -m, --message <text>    Add a message to the prompt
  -f, --file <filename>   Insert whole file contents
  -l, --line <range>      Insert line range(s) from the most recent file
  --test                  Print the prompt instead of sending to API

Examples:
  gill -m "What's the capital of Australia?"
  gill -m "Explain this script line-by-line:" -f myscript.py
  gill -m "What does this function do?" -f ./src/main.cpp -l 120-145
  gill --test -m "Explain this function." -f my.py -l 22-40

For detailed docs visit: https://github.com/MAA-98/gill
"""
        case "gill init":
            help_text = """
Usage: gill init [<directory>]

Initializes a new Gill project in the current working directory or, 
if specified, the directory given relative to the current working directory.

Examples:
  gill init
  gill init myproject_dir
"""
        case "gill sysprompt":
            help_text = """
Usage: gill sysprompt

Outputs the file path to the current system prompt used in API calls.

You can then read or edit this file easily. For example:

  cat $(gill sysprompt)
  nano $(gill sysprompt)
  vim $(gill sysprompt)

This allows you to view or modify the contents of the system prompt directly.

Typically, this file is located inside the `.gill` directory created by `gill init`.
"""
        case "gill config":
            help_text = """
Usage:
  gill config set <section.key> <value>
  gill config <section.key>
  gill config --list

Manages configuration values for your Gill project.

Commands:
  set <section.key> <value>     Set the given configuration key to a new value.
  <section.key>                 Print the value of the specified key.
  --list                        List all current configuration values.

Notes:
  - Keys must be specified in the '<section.key>' format (e.g., llm.model).
  - Config file is typically stored at .gill/config.toml in your project directory.

Examples:
  gill config set llm.provider OpenAI
  gill config set llm.model gpt-4-turbo
  gill config llm.model
  gill config --list
"""
        case _:
            help_text = ""
    print(help_text)