# Spice with the OpenAI ASK

One of Spice's best features is to act in place of the OpenAI API. Even better, you don't even have to be running OpenAI behind Spice! You can run OpenAI, Anthropic or HuggingFace models over your data and use existing tools that are compatible with the OpenAI API.

## Prerequisites

1. Python >= 3.10
2. Python package manager (`pip` or `uv`)
3. Spice [installed](https://docs.spiceai.org/getting-started)
3. OpenAI API Key
4. A clone of this repository on your local machine

## Starting Spice

The first step is to get the Spice instance up and running.

1. Copy `.env` to a new filed called `.env.local`
2. Replace `SPICE_OPENAI_API_KEY` in `.env.local` with your OpenAI API key
3. Start Spice with `spice run`

Spice will use your OpenAI API key to communicate with OpenAI on your client code's behalf.

## Client prerequisites

These steps only need to be done once. It's highly suggested to use a Python `virutalenv` to keep your projects isolated from each other.

### Using pip

1. (Optional) Activate your virtual environment (`source .venv/bin/activate`)
2. Install the required packages: `pip install -r requirements.txt`

To run the client, simply use `python spice_openai_sdk.py`

### Using uv

1. Use `uv venv` to create the virtual environment
2. Ensure the packages are installed: `uv sync`

To run the client, simply use `uv run spice_openai_sdk.py`

## About the client

The client is fairly simple, but it demonstrates how you can integrate existing tooling with Spice's AI Gateway.

First, we construct the client:

```python
client = Client(api_key="anything", base_url="http://localhost:8090/v1")
```

Notice that we can use any string we want for the `api_key`, because it's Spice that's responsible for communicating with the OpenAI API, not our client code, meaning less secrets to have to store and manage for your client application.

```python
chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": "user",
            "content": "What datasets do I have access to?",
        }
    ],
    model="openai",
)
```

Here we're using the chat completions API to ask a question. Notice that we're asking a question about our Datasets. This is a question that only Spice can answer, and that's exactly what it does:

```python
print(chat_completion.choices[0].message.content)
```

```shell
You have access to the following dataset:

- **Table Name:** taxi_trips
  - **Description:** Taxi trips data stored in S3.

This dataset is available in the SQL database.
```