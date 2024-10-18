from openai import Client
from dotenv import load_dotenv
import os
import logging

load_dotenv()

# Uncomment the following line to enable debug logging
#logging.basicConfig(level=logging.DEBUG)

# Replace the base_url with your local instance of the Spice HTTP API
client = Client(api_key=os.getenv("SPICE_OPENAI_API_KEY"), base_url="http://localhost:8090/v1")

# Use the OpenAI SDK as you normally would
chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": "user",
            "content": "Say this is a test",
        }
    ],
    model="openai",
)

print(chat_completion.choices[0].message.content)