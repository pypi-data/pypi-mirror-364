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

def aliases(command: str) -> list[str]:
    match command:
        case "sysprompt":
            aliases = [
                # Full phrase
                "systemprompt",
                "system-prompt",
                "system_prompt",
                # Abbrv "system"
                "sysprompt",
                "sys-prompt",
                "sys_prompt",
                # Abbrv "prompt"
                "systempmt",
                "system-pmt",
                "system_pmt",

                "systempmpt",
                "system-pmpt",
                "system_pmpt",
                # Abbrv both
                "syspmt",
                "sys-pmt",
                "sys_pmt",

                "syspmpt",
                "sys-pmpt",
                "sys_pmpt",
                ]
            return aliases
    return []