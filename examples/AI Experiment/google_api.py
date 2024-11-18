"""
To use this script, you need to be logged in to the Vertex AI platform:
See https://cloud.google.com/sdk/gcloud/reference/auth/application-default/login
```bash
gcloud auth application-default login
```
"""
import vertexai
from vertexai.generative_models import GenerativeModel, SafetySetting


def generate(prompt, model="gemini-1.5-flash-002", max_tokens=5):
    generation_config = {
        "max_output_tokens": max_tokens,
        "temperature": 1,
        "top_p": 0.95,
        "stop_sequences": [">>"],
    }
    vertexai.init(project="auto-centauer", location="us-central1")
    model = GenerativeModel(
        model,
    )
    responses = model.generate_content(
        [prompt],
        generation_config=generation_config,
        safety_settings=safety_settings,
        stream=True,
    )

    return "".join([response.text for response in responses])


def multiturn_generate(system_instruction, prompt):
    generation_config = {
        "max_output_tokens": 5,
        "temperature": 1,
        "top_p": 0.95,
        "stop_sequences": [">>"],
    }
    vertexai.init(project="auto-centauer", location="us-central1")
    model = GenerativeModel(
        "gemini-1.5-flash-002", system_instruction=[system_instruction]
    )
    chat = model.start_chat()
    print(
        chat.send_message(
            [prompt],
            generation_config=generation_config,
            safety_settings=safety_settings,
        )
    )


safety_settings = [
    SafetySetting(
        category=SafetySetting.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
        threshold=SafetySetting.HarmBlockThreshold.OFF,
    ),
    SafetySetting(
        category=SafetySetting.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
        threshold=SafetySetting.HarmBlockThreshold.OFF,
    ),
    SafetySetting(
        category=SafetySetting.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
        threshold=SafetySetting.HarmBlockThreshold.OFF,
    ),
    SafetySetting(
        category=SafetySetting.HarmCategory.HARM_CATEGORY_HARASSMENT,
        threshold=SafetySetting.HarmBlockThreshold.OFF,
    ),
]
