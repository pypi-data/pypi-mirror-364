![LLMAID](attachments/llmaid.png)

*A zero‑dependency wrapper that turns any OpenAI‑compatible endpoint into a one‑liner.*

---

This README features a quick start guide, and simple examples for main features. Do checkout other documentation as needed:
- [Full API reference](./docs/Public API Reference.md)
- [Test specifications](./specs/spec.md) (Gherkin-style exhaustive tests for all public API features)
- [Contributing guide for all](./CONTRIBUTING.md) (how to run tests, add new features, etc.)
- [Contributing guide for humans ONLY. ANY AI IS FORBIDDEN.](./CONTRIBUTING_HUMAN.md) (how to effectively collaborate with AI tools while ensuring code quality and project integrity)

## Installation

```bash
pip install llmaid
```

### Environment‑variable fallback

LLMAid will look for these variables at import time—pass arguments only when you want to override them.

| Variable                 | Purpose                                            | Default                   |
| ------------------------ | -------------------------------------------------- | ------------------------- |
| `LLMAID_BASE_URL`        | Backend URL                                        | `http://127.0.0.1:17434`  |
| `LLMAID_SECRET`          | Auth key / token                                   | *(none)*                  |
| `LLMAID_MODEL`           | Model name                                         | `mistral-large-v0.1`      |

More in [Public API Reference](docs/Public%20API%20Reference.md#environment-variables).

---

## Quick start

### One‑liner

```python
# import your environment variables before using llmaid
from llmaid import llmaid

llmaid().completion("You are a hello machine, only say hello!")
# -> "hello!"
```

### Manual configuration

```python
from llmaid import llmaid

hello_machine = llmaid(
    base_url="https://openrouter.ai/api/v1",
    secret="<your-secret>",
    model="mistral-large-v0.1",
)

hello_machine.completion("You are a hello machine, only say hello!")
# -> "hello!"
```

## Cloning instances 

Need a new instance with different config? `llmaid` is **callable**:
- settings can be overridden at call time, e.g. `base_url`, `secret`, `model`, etc.
- the call returns a *clone* with merged settings from the instance that was called.

```python
# point the same instance at another model just for this call
hello_machine(
    model="qwen-2.5b-instruct"
).completion("You are a hello machine, only say hello!")
# -> "hello!"

# or save a derived clone for later
another_machine = hello_machine(
    base_url="https://another-backend.ai/api/v1",
    secret="<another-secret>",
    model="deepseek-2.7b-instruct"
)
```

---

## Prompt templating

You can use prompt templates to create reusable prompts with placeholders for parameters. This allows you to define a prompt once and fill in the parameters dynamically when making completions.

```python
# import your environment variables before using llmaid
from llmaid import llmaid

anything_machine = llmaid().prompt_template("You are a {{role}} machine, only say {{action}}!")
# you can also use llmaid().system_prompt(...) as an alias for prompt_template

anything_machine.completion(role="hello", action="hello")  # -> "hello!"
anything_machine.completion(role="goodbye", action="goodbye")  # -> "goodbye!"

# Derive a new independant llmaid instance with a different prompt and same settings on the fly
doer = anything_machine.prompt_template(
    "You are a {{role}}. Do your best to {{action}}!"
)

doer.completion("Why is the sky blue?", role="scientist", action="explain")
```

`llmaid.completion()` supports any number of positional and keyword arguments.
- Positional arguments are joined with a newline character and appended to the end of the prompt template.
- Keyword arguments are used to fill in the placeholders in the prompt template.

Here is an example to illustrate this:

```python
doer.completion(
    "Why is the sky blue?",
    "No really, why?",
    role="scientist",
    action="explain"
)
# will result in following prompt being passed to the LLM backend:
"""
You are a scientist. Do your best to explain!
Why is the sky blue?
No really, why?
"""
```

Note from the author: I have designed llmaid with text completion in mind rather than chat completion. Which explains the logic illustrated above. I do plan to add chat completion support in the future. Also checkout the [chat history handling example](#handling-chat-history) below.

---

## Streaming responses

Minimum working example using asyncio.

```python
# prepare your environment variables before using llmaid
import asyncio, llmaid

async def main():
    anything_machine = llmaid().prompt_template("You are a {{role}} machine, only say {{action}}!")

    async for token in anything_machine.stream(role="hello", action="hello"):
        print(token, end="", flush=True)

asyncio.run(main())
```

## Async support

All LLMAid completion methods have an async counterpart that can be used with `await`:
- `completion(input: str, **kwargs) -> str` - synchronous completion method that returns the full response as a string.
- `acompletion(input: str, **kwargs) -> str` - asynchronous completion method that returns the full response as a string. You can use it with `await`.
- `stream(input: str, **kwargs) -> AsyncIterator[str]` - asynchronous streaming method that returns an async iterator yielding response tokens as they arrive. You can use it with `async for`.

---

---

## More Examples

### Advance prompt templating

You don't **have** to pass `llmaid.completion` any arguments at all, it all depends on how you set up your prompt template.

```python
# import your environment variables before using llmaid
from llmaid import llmaid

spanish_translator = llmaid().prompt_template("""You are a master spanish translator.
Translate Any text you're given without any explanation or comments.

The text that follow right after the triple dash is the text you should translate to spanish.
---""")
spanish_translator.completion("The sky is blue because of the way the Earth's atmosphere scatters light from the sun.")
# -> "El cielo es azul debido a la forma en que la atmósfera de la Tierra dispersa la luz del sol."
```

Also, you can use only keyword arguments, but still have a user input in the prompt template.

```python
spanish_translator2 = spanish_translator.prompt_template(
    "Translate this text to spanish: {{user_input}}",
)

spanish_translator2.completion(user_input="The sky is blue because of the way the Earth's atmosphere scatters light from the sun.")
# -> "El cielo es azul debido a la forma en que la atmósfera de la Tierra dispersa la luz del sol."
```

### Handling chat history

As a text-completion first module, LLMAid does not have built-in chat history management (yet), but you can easily implement it using the prompt templating feature. Here's a simple example:

```python
# import your environment variables before using llmaid
from llmaid import llmaid

helpful_assistant = llmaid().prompt_template("""
    You are a helpful assistant. You will be given a chat history and the next user input.
    Your task is to respond to the user input based on your knowledge and taking into account the chat history.

    Chat history:
    {{chat_history}}
    End of chat history.

    User input:
    {{user_input}}
    End of user input.

    Your response should be concise and relevant to the user input.
    Only refer to the chat history if it is relevant to the user input.
""")

chat_history = [
    "User: What is the capital of France?",
    "Assistant: The capital of France is Paris.",
].join("\n")

response = helpful_assistant.completion(
    chat_history=chat_history,
    user_input="How old are you?"
)
# -> "I am an AI and do not have an age like humans do, but I can provide more information about Paris or any other topic you are interested in."
```

### Advanced prompt management

Prompt files can become lengthy and cumbersome to manage when modularizing your prompts. LLMAid supports concatenating multiple prompt files together, allowing you to split your prompts into smaller, manageable pieces.

```python
# import your environment variables before using llmaid
from pathlib import Path
from llmaid import llmaid

scientist_summary = llmaid(prompt_template_dir=Path("./prompts")).prompt_template(
    "scientist_prompt.txt",  # roles/contexts can be split up
    "summary_prompt.txt"      # and concatenated in order
)

scientist_summary.completion("Why is the sky blue?")
# -> "The sky appears blue due to the scattering of sunlight by the Earth's atmosphere. This phenomenon is known as Rayleigh scattering, which causes shorter wavelengths of light (blue) to be scattered more than longer wavelengths (red)."
```

## Feature matrix

| Feature                            | Status | Notes                       |
| ---------------------------------- | ------ | --------------------------- |
| Synchronous completion             | ✅      | `completion()`              |
| Asynchronous completion            | ✅      | `await acompletion()`       |
| Streaming tokens                   | ✅      | `async for ... in stream()` |
| Prompt templating (Jinja‑like)     | ✅      | File or inline strings      |
| Prompt directories & concatenation | ✅      | Pass multiple paths         |
| Environment‑variable config        | ✅      | Zero‑code setup             |
| Exponential back‑off & retry       | ✅      | Built‑in, configurable      |
| Easy logging and debugging         | 🕗     | Planned                     |
| Output‑format enforcement          | 🕗     | Planned (JSON/YAML/XML)     |
| Output critic and validation       | 🕗     | Planned (guards, quality control...)     |
| Built-in chat history handling     | 🕗     | Planned                     |
| Pydantic template validation       | 🕗     | Planned                     |
| File attachments                   | 🕗     | Planned                     |
| Tools / agent actions              | 🕗     | Planned                     |
| MCP support                        | ❓      | Considering               |

## Other todos for later

- quickstart video in terminal
- auto deploy to PyPI with github actions

---

## License

LLMAid is released under the **MIT License**—see the [`LICENSE`](./LICENSE.MD) file for full text.

---

## Building for PyPI

To build LLMAid for PyPI, run the following commands in the root directory of the project:

```bash
.venv/bin/pip install --upgrade build
.venv/bin/python -m build
.venv/bin/pip install --upgrade twine
.venv/bin/twine upload dist/*
```

## About

I built LLMAid because I kept rewriting the same boilerplate for different OpenAI‑compatible backends. The goals are:

* **Simplicity** – no runtime dependencies, no hidden magic.
* **Flexibility** – override anything at call‑time.
* **Speed** – prototype in one import.

[Full reference documentation](docs/Public%20API%20Reference.md) is available 
