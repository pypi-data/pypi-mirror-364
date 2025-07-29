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

from typing import Optional
import os

def gill_init(debug_bool: bool, arg: Optional[str]):
    """
    Initialize a new Gill project directory structure.

    Creates a `.gill` directory in the specified location (current working directory 
    or subdirectory if provided) along with an empty 'sysprompt' file inside it.

    Parameters:
        debug_bool (bool): If True, print debug information about directory and file creation.
        args (list[str]): List of arguments; if non-empty, the first argument is treated as 
                          a relative path from the current working directory where the 
                          `.gill` directory will be created.

    Raises:
        IsADirectoryError: If a directory named '.gill' already exists at the target path.
        FileExistsError: If a file named '.gill' (not a directory) exists at the target path.
        OSError: If there is an error creating the directory or the 'sysprompt' file.

    Side Effects:
        Creates a new `.gill` directory and an empty 'sysprompt' file in the target location.
        Prints initialization success message.

    Example:
        gill_init(False, [])  # creates .gill in current working directory
        gill_init(True, ['myproject'])  # creates ./myproject/.gill and prints debug info
    """
    dir_name = ".gill"
    cwd = os.getcwd()
    if arg:
        cwd = os.path.join(cwd, arg)
    gill_path = os.path.join(cwd, dir_name)
    # Now cwd is either cwd or cwd + arg

    # Creating .gill directory
    if os.path.exists(gill_path):
        if os.path.isdir(gill_path):
            raise IsADirectoryError(f"Directory already exists at {gill_path}. Delete or move it and try again.")
        else:
            raise FileExistsError(f"A file named '{dir_name}' exists at {cwd}. Delete or move it and try again.")
    else:
        try:
            os.makedirs(gill_path)
            if debug_bool:
                print(f"Directory '{dir_name}' created at {gill_path}")
        except OSError as e:
            raise OSError(f"Error creating directory '{dir_name}': {e}")

    # Creating sysprompt file
    sysprompt_path = os.path.join(gill_path, "sysprompt")
    try:
        # This opens (creates if doesn't exist) and immediately closes the file.
        with open(sysprompt_path, "w") as f:
            f.write("")  # or put some initial content here if you want
        if debug_bool:
            print(f"File 'sysprompt' created at {sysprompt_path}")
    except OSError as e:
        raise OSError(f"Error creating file 'sysprompt': {e}")
    
    # Creating config file
    config_path = os.path.join(gill_path, "config.toml")
    toml_content = """
[llm]
model = "gpt-4.1-mini"
"""
    try:
        # This opens and creates file of default settings
        with open(config_path, "w") as f:
            f.write(toml_content)
        if debug_bool:
            print(f"File 'config.toml' created at {config_path}")
    except OSError as e:
        raise OSError(f"Error creating file 'config.toml': {e}")
    
    # Creating chats dir
    chats_dir = os.path.join(gill_path, "chats")
    try:
        os.makedirs(chats_dir)
        if debug_bool:
            print(f"Directory 'chats' created at {chats_dir}")
    except OSError as e:
        raise OSError(f"Error creating directory 'chats': {e}")
    
    print(f"Initialized new Gill project at {cwd}")
