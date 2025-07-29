#!/usr/bin/env python3

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

from gill.help import print_help
from gill.gill_init import gill_init
from gill.aliases import aliases
from gill.gill_sysprompt import gill_sysprompt
from gill.gill_config import gill_config
from gill.gill_chat import gill_chat, head_chat, get_chat_path
from gill.prompt_parser import parse_prompt_args                     # Import the parser for prompt instructions
from gill.llm_api import ask_openai                                  # Import API call function

import sys
import os
import json

def main() -> None:
    DEBUG_BOOL: bool = False
    testBool: bool = False                                      # Set True with `--test` flag

    args = sys.argv
    if len(args) > 1:
        args = args[1:]                                         # Cut out the `gill` command
        if DEBUG_BOOL:
            print(f"args are: ", args)
    else: 
        # Deal with case of no commands
        print_help("gill")
        return

    match args[0]:
        case "init":
            args = args[1:]                                     # Cut out the `init` command
            if len(args) < 2:
                arg = args[0] if len(args) > 0 else None        # Either has one more command for directory or None
                try:
                    gill_init(DEBUG_BOOL, arg)
                    return
                except Exception as e:
                    print(f"Error: {e}", file=sys.stderr)
            print_help("gill init")
            sys.exit(1)
        case "config" | "configuration":
            args = args[1:]                                     # Cut out `config` command
            if len(args) > 0:
                try:
                    gill_config(args)
                    return
                except Exception as e:
                    print(f"Error: {e}", file=sys.stderr)
            print_help("gill_config")
            sys.exit(1)
        case value if value in aliases("sysprompt"):
            args = args[1:]                                     # Cut out `sysprompt` command
            if len(args) == 0:                                  # Only accept no commands
                try:
                    gill_sysprompt()
                    return
                except Exception as e:
                    print(f"Error: {e}", file=sys.stderr)
            print_help("gill sysprompt")
            sys.exit(1)
        case "chat"| "chats": # TODO: commands for new chat, switching chat, deleting chat, listing, showing
            args = args[1:]                                     # Cut out `chat` command
            if len(args) == 1:
                try:
                    gill_chat(args)
                    return
                except Exception as e:
                    print(f"Error: {e}", file=sys.stderr)
            print_help("gill chat")
            sys.exit(1)
        case "--test" | "-t":
            testBool = True
            args = args[1:]
        # TODO: --help command

    # Create prompt to send (or test)
    try:
        prompt = parse_prompt_args(args)
    except ValueError as e:
        print(f"Argument error: {e}", file=sys.stderr)
        sys.exit(1)
    if prompt == "":
        print("Error: Provide at least one -m or -f option with content.", file=sys.stderr)
        sys.exit(1)

    # If testing, just print
    if testBool:
        print(prompt)
        return
    
    # Check for chat head, 
    # this also creates a new head, with the current
    # sysprompt, if configs exist but head does not.
    head_name = head_chat()
    head_path = None
    if head_name:
        head_path = os.path.join(get_chat_path(), head_name)
        with open(head_path, "r", encoding="utf-8") as f:
            messages = json.load(f)  # Type Any!
    else:
        messages = [{"role": "developer", "content": ""},]
    
    messages.append({"role" : "user", "content" : prompt})

    # Get streaming response
    try:
        result = ""
        if DEBUG_BOOL:
            print("Messages to API: \n", messages)
        cc_stream = ask_openai(DEBUG_BOOL, messages)                # Call OpenAI API function
        for event in cc_stream:
            # Only accumulate the text deltas
            content_delta = event.choices[0].delta.content
            if content_delta:
                result += content_delta
                print(content_delta, end="", flush=True)
            # You can handle other event types if you want: e.g., done, content_part.done, etc.
        print() # flush newline at end of stream
    except Exception as e:
        print(f"OpenAI API error: {e}", file=sys.stderr)
        sys.exit(1)

    if head_path:
        messages.append({"role": "assistant", "content": result})
        with open(head_path, "w", encoding="utf-8") as f:
            json.dump(messages, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
