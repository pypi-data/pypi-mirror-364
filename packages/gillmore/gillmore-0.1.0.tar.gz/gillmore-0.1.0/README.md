# gill

**gill** is a CLI between your code and an LLM. It provides low-level control and ergonomics for sending prompts with your code to OpenAI's API.

## Features

- **Flexible Prompt Building:** Compose and send prompts with messages (`-m`), whole files (`-f`) or line ranges within files (`-l`) using interleaved and stacked arguments:

```bash
gill -m "What does this function do?" -f src/main.py -l 14-23 45- -m "Explain line by line."
```

- **Test mode:** Learn what prompts your commands make without sending to the API with a `--test` flag:

```bash
gill --test -m "Please explain the bug in these lines." -f foo.py -l 33-86 -m "This, too:" -f bar.py -l 15-20
```
Output:
<pre>
<code>
Please explain the bug in these lines.

```foo.py, lines 33-86
# Code from foo.py lines 33-86...
```

This, too:

```bar.py, lines 15-20
# Code from bar.py lines 15-20...
```
</code>
</pre>

- **Save System Prompt:** Initialize gill at the project directory and edit the system prompt used in API calls:

```bash
gill init
nano $(gill sysprompt)
```

- **Project-Level Configs:** Change the system prompt and the current OpenAI model used by the API:

```bash
gill config list
```

Output:
```
[llm]
model = "gpt-4.1-mini"

[chats]
head = "7ea...827.chat"
```

Change the model used:
```bash
gill config set llm.model gpt-4.1
```

Clear the chat with:
```bash
gill chat clear
```

---

## Installation

The use of the OpenAI API assumes you have a saved environment key: ```OPENAI_API_KEY```.

Gill has no official package yet. To use the tool in ```bash``` or ```zsh```:

1. Clone repo, install dependencies and make executable. Something like (replace ```~/path/to/your/dir/gill/src_py/gill``` with the actual full path):

```bash
cd ~/path/to/your/dir/
git clone https://github.com/MAA-98/gill.git
cd gill
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
chmod +x src_py/gill # May require sudo
```

2. Add alias to your ```.bashrc``` or ```.zshrc```: open file and add the lines:

```bash
alias gill='~/path/to/your/dir/gill/src_py/gill'
```

Save, exit, and reload configuration:

```bash
source ~/.zshrc
```

---

## Basic Usage

**Order is preserved**.

```bash
gill ([-m|--message <text> ...]) [-f|--file <filename> ...] [-l|--line <range> ...] ...
```

### Test

Use ```--test``` flag to print the prompt created, rather than sending to API:

```bash
gill --test [-m|--message <text> ...] [-f|--file <filename> ...] [-l|--line <range> ...] ...
```

### 3 Rules:

1. Flags are stored until another is given, so arguments can always be stacked after a flag.

2. Files are stored until another is given and `-l` applies to the most recent file given. This gives the flexibility to insert messages in between lines without losing reference to file.

3. IMPORTANT: If a line of a file is never inserted before a new file, or before the end of the prompt, then the whole file is inserted at the position the file was given.

### Line Range Syntax

Line ranges for `-l` flags are always inclusive and can be specified in various ways:

- Single line: `-l 8`
- Finite Inclusive Range: `-l 12-15` or any of `-l 12--15`, `-l 12,15`, `-l 12.15`, `-l 12..15`
- From beginning or till end: start of file till line 12 with `-l -12` or line 12 till end of file with `-l 12-`. Or the other delimiters `--`, `,`, `.`, `..`
- Multiple `-l` flags/args can stack for multiple excerpts from one file.

---

## Advanced Usage

As in `git`, initialize a gill project with `gill init` or `gill init [<directory>]`.

### System Prompt

Access the file path to the system prompt used in API calls with `gill sysprompt`. Then read with `cat $(gill sysprompt)` or edit with your choice of editor, e.g. `nano $(gill sysprompt)`.

### Chats

Chat is automatically created with `git init` and tracked as you use. Clear the chat with a simple `gill chat clear`. Sending a new prompt will then use the updated `gill sysprompt` contents.

### Configs

Configurations may be changed with `gill config set <section.key> value`, currently the only valid `<section.key>` is `llm.model` (and `model.head` which should not be manually changed.) Print all configs with `gill config list` or a single value with `gill config <section.key>`.

Therefore, change the OpenAI model used by the API with `gill config set llm.model gpt-4.1`, or any other OpenAI model value.

---

## Examples

#### Simple prompt with a message

```bash
gill -m "What's the capital of Australia?"
```

#### Insert a whole file

```bash
gill -m "Explain this script line-by-line: " -f myscript.py
```

#### Insert just a range of lines from a file

```bash
gill -m "What does this function do?" -f ./src/main.cpp -l 120-145
```

#### Build a multi-part prompt

```bash
gill -m "Compare these two:" -f file1.py -l 2-10 -f file2.py -l 3-8
```

#### Mixing multiple messages and files

```bash
gill -m "A bug is happening in these segments." -f bug.py -l 14-23 45- -m "Here's the log:" -f error.log -l 2
```

#### Test mode (print prompt only, don’t send)

```bash
gill --test -m "Explain this function." -f my.py -l 22-40
```

---

## Example Output

Relevant file or line excerpts are embedded as Markdown fenced code blocks with filenames and line info for clarity. Messages are inserted as plain text sections, separated by new lines.

```bash
gill --test -m "Please explain the bug in these lines." -f foo.py -l 33-86 -m "This, too:" -f bar.py -l 15-20
```
Output:
<pre>
<code>
Please explain the bug in these lines.

```foo.py, lines 33-86
# foo.py lines 33-86...
```

This, too:

```bar.py, lines 15-20
# bar.py lines...
```
</code>
</pre>

---

## Contributions

Planned features, ordered by priority:
- More chat commands
- Insert webpage contents by URL
- Completions with Tab

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

While you are free to release derivative works under any compatible license, we *strongly encourage* using permissive licenses such as Apache 2.0 or MIT, and avoiding copyleft licenses like GPL if possible, to maximize compatibility and adoption.
