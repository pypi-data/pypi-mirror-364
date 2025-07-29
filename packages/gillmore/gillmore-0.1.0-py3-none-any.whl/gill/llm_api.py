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

from openai import OpenAI
from openai.types.chat import ChatCompletionChunk, ChatCompletionMessageParam

from typing import Iterator, cast, Any
import os

from gill.gill_config import get_config_path, load_toml

client = OpenAI()

# See general docs at: https://platform.openai.com/docs/guides/
# For streaming CC: https://platform.openai.com/docs/api-reference/chat-streaming

def ask_openai(debug: bool, raw_messages: Any) -> Iterator[ChatCompletionChunk]:
    config_path = get_config_path()
    try:
        config = load_toml(config_path)
        model = config["llm"]["model"] or "gpt-4.1-mini"
    except:
        model = "gpt-4.1-mini"

    # Cast loaded JSON to the expected OpenAI message param type
    messages = cast(list[ChatCompletionMessageParam], raw_messages)

    if debug:
        print("Cast messages: \n", messages)

    return client.chat.completions.create(
        model=model,
        messages=messages,
        stream=True,
    )
