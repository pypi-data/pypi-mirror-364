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
import sys
import re

def get_sysprompt_path() -> str:
    cwd = os.getcwd()
    config_path = os.path.join(cwd, ".gill", "sysprompt")
    return config_path

def sanitize_prompt(prompt: str):
    # Remove trailing newlines, spaces, or carriage returns for request
    prompt = prompt.rstrip('\n\r ')
    # Remove unwanted control chars except \n and tabs if you want:
    prompt = re.sub(r'[\x00-\x08\x0B-\x0C\x0E-\x1F]', '', prompt)
    return prompt

def gill_sysprompt() -> None:
    cwd = os.getcwd()
    dir_name = ".gill"
    gill_path = os.path.join(cwd, ".gill")
    sysprompt_path = get_sysprompt_path()

    if os.path.exists(gill_path):
        if os.path.isdir(gill_path):
            if os.path.exists(sysprompt_path):
                if os.path.isdir(sysprompt_path):
                    raise IsADirectoryError(f"Directory exists at {sysprompt_path}. Delete {gill_path}, initialize Gill, and try again.")
                else:
                    sys.stdout.write(sysprompt_path)
            else:
                raise FileNotFoundError(f"No file named sysprompt at {gill_path}. Delete {gill_path}, initialize Gill, and try again.")
        else:
            raise FileExistsError(f"A file named '{dir_name}' exists at {cwd}. Delete it, initialize Gill, and try again.")
    else:
        raise NotADirectoryError(f"No directory at {gill_path}. Initialize Git in working directory.")
    return