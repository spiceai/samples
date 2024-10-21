from openai import Client
from dotenv import load_dotenv
import os
import logging

load_dotenv()

# Uncomment the following line to enable debug logging
#logging.basicConfig(level=logging.DEBUG)

# Replace the base_url with your local instance of the Spice HTTP API
client = Client(api_key="anything", base_url="http://localhost:8090/v1")

# Use the OpenAI SDK as you normally would
chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": "user",
            "content": "What datasets do I have access to?",
        }
    ],
    model="openai",
)

print(chat_completion.choices[0].message.content)