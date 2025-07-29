# limin-talk

A Python library for letting two LLMs talk to each other.

## Installation

Install the library using pip:

```bash
python -m pip install limin-talk
```

## Usage

After you've installed the library, you can use it by importing the `limin_talk` module and calling the functions you need.
You will also need to provide an API key for your API either by running `export OPENAI_API_KEY=$YOUR_API_KEY` or by creating an `.env` file in the root directory of your project and adding the following line:

```
OPENAI_API_KEY=$YOUR_API_KEY
```

Here's an example of how to use the library:

```python
from limin import ModelConfiguration
from limin_talk import Character, talk

user_character = Character(
    system_prompt="You are a helpful assistant who only speaks English.",
    model_configuration=ModelConfiguration(model="gpt-4o"),
)

assistant_character = Character(
    system_prompt="You are a helpful assistant who only speaks German.",
    model_configuration=ModelConfiguration(model="gpt-4o"),
)


async def main():
    conversation = await talk(user_character, assistant_character, 3)
    print(conversation.to_pretty_string())


if __name__ == "__main__":
    import asyncio
    import dotenv

    dotenv.load_dotenv()

    asyncio.run(main())
```

Basically, the library contains the following two components:

The `Character` class, which is used to create a character that can be used to talk to another character.
To instantiate a character, you need to provide a system prompt and a model configuration for the character.

The `talk` function, which is used to let two characters talk to each other.
To use the `talk` function, you need to provide two characters and the number of turns you want the conversation to have.

The `talk` function will return a `Conversation` object, which contains the conversation history.

You can find the example in [`examples/demo.py`](examples/demo.py).
