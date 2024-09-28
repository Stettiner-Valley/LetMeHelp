import os

from dataclasses import dataclass
from functools import partial

from openai import OpenAI
from mistralai import Mistral

from baserat import utils


@dataclass(frozen=True)
class LLM_PROVIDER:
    OPENAI = "OPENAI"
    MISTRAL = "MISTRAL"


@dataclass(frozen=True)
class LLM:
    GPT40 = "gpt-4o"
    MISTRAL = "pixtral-12b-2409"


class LLM_HANDLER:
    def __init__(self, llm_provider: LLM_PROVIDER, llm: LLM):
        if llm_provider == LLM_PROVIDER.OPENAI:
            print(f"Using OPEN AI  {llm}..")
            client = OpenAI(api_key=os.getenv("OPEN_API_KEY"))
            self.invoke = partial(client.chat.completions.create, model = llm)
        elif llm_provider == LLM_PROVIDER.MISTRAL:
            print(f"Using MISTRAL {llm}..")
            client = Mistral(api_key=os.getenv("MISTRAL_API_KEY"))
            self.invoke = partial(client.chat.complete, model = llm)

    def send_msg_to_llm(self, base64_encoded_img, system_prompt, prompt):
        message = [
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_encoded_img}"
                        }
                    }
                ]
            }
        ]
        print("Sending image to LLM")
        response = self.invoke(
            messages=message
        )
        llm_response = response.choices[0].message.content.strip()
        print(llm_response)
        return utils.jsonify(llm_response)