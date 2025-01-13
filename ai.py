import json
import os

from openai import NOT_GIVEN
from env import API_KEY

API_TYPE = "azure"
API_KEY = os.environ.get("OPENAI_API_KEY", API_KEY)
BASE_URL = "https://ol-ai-assistant-prod.openai.azure.com/openai/deployments/gpt-4o-testing/chat/completions?api-version=2024-08-01-preview"
MODEL = "gpt-4o-testing"

if API_TYPE == "azure":
    from openai import AzureOpenAI
    from urllib.parse import urlparse, parse_qs

    version = parse_qs(urlparse(BASE_URL).query)["api-version"][0]
    client = AzureOpenAI(api_key=API_KEY, base_url=BASE_URL, api_version=version)
else:
    from openai import OpenAI

    client = OpenAI(api_key=API_KEY, base_url=BASE_URL)


def request_ai_response(user, system=None, response_format=NOT_GIVEN):
    messages = []

    if system:
        messages.append(
            {
                "role": "system",
                "content": system,
            }
        )

    messages.append(
        {
            "role": "user",
            "content": user,
        }
    )

    # print()
    # print("-" * 80)
    # print("DEBUG: Calling AI with")
    # for message in messages:
    #     print(message["role"] + ":")
    #     print(message["content"])
    #     print()
    # print("-" * 20)
    # print()

    if response_format == NOT_GIVEN:
        completion = client.chat.completions.create(messages=messages, model=MODEL)
        # print(
        #     "DEBUG: AI response",
        #     completion.choices[0].message.content,
        # )
    else:
        completion = client.beta.chat.completions.parse(
            messages=messages, model=MODEL, response_format=response_format
        )
        # print(
        #     "DEBUG: AI response",
        #     json.dumps(completion.choices[0].message.parsed.model_dump(), indent=2),
        # )

    # print("-" * 80)
    # print()

    return completion.choices[0].message
