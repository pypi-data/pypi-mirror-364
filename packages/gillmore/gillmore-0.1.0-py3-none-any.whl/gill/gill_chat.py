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
from typing import Optional
import uuid
import toml
import json

from gill.gill_config import get_config_path, load_toml
from gill.gill_sysprompt import get_sysprompt_path, sanitize_prompt

def head_chat() -> Optional[str]:
    """
    If config file exists:
    - get the head chat or create new chat
    return (file path to chat, the chat as dict)

    If config file doesn't exist:
    return None
    """
    config_path = get_config_path()
    if os.path.exists(config_path):
        config = load_toml(config_path)
        chats = config.get("chats")

        if not chats:
            # No chats in config, so check chats dir exists and if not create it
            chats_path = get_chat_path()
            if not (os.path.exists(chats_path) and os.path.isdir(chats_path)):
                os.makedirs(chats_path)
        if chats:
            head = chats.get("head")
            if head:
                return head

        # Create chat file that's not already there
        new_chat_filename = f"{uuid.uuid4().hex}.chat"
        new_chat_path = os.path.join(get_chat_path(), new_chat_filename)
        messages = []
        with open(get_sysprompt_path(), "r", encoding="utf-8") as s:
            sysprompt_content = s.read()
            sanitized_sysprompt = sanitize_prompt(sysprompt_content)
            messages.append(
                {
                    "role": "developer",
                    "content": sanitized_sysprompt
                }
            )
        with open(new_chat_path, "w", encoding="utf-8") as f:
            json.dump(messages, f, indent=2)

        # Setup config dict with head pointing to this chat
        if not chats:
            config["chats"] = {"head": new_chat_filename}
        elif not chats.get("head"):
            config["chats"]["head"] = new_chat_filename
        
        # Save updated config back to disk
        with open(config_path, "w") as f:
            toml.dump(config, f)

        return new_chat_filename
    else:
        return None

def get_chat_path() -> str:
    cwd = os.getcwd()
    chats_path = os.path.join(cwd, ".gill", "chats")
    return chats_path

def gill_chat(args: list[str]) -> None:
    if args[0] == "clear":
        chats_dir = get_chat_path()
        if os.path.exists(chats_dir) and os.path.isdir(chats_dir):
                for filename in os.listdir(chats_dir):
                    file_path = os.path.join(chats_dir, filename)
                    if os.path.isfile(file_path):
                        os.remove(file_path)

        config_path = get_config_path()
        if os.path.exists(config_path):
            config = load_toml(config_path)
            chats = config.get("chats")

            if chats:
                if "head" in chats:
                    del chats["head"]
                # Save updated config back to disk
                with open(config_path, "w") as f:
                    toml.dump(config, f)
        return
    else:
        raise SyntaxError(f"Unknown command or incorrect arguments: {' '.join(args)}")
