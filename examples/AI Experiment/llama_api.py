from openai import OpenAI

client = OpenAI(
    api_key="LA-5dadfd9796ea4d6b9273d3fc4a0cd55f3f0130003ccd483180586be48e47d859",
    base_url="https://api.llama-api.com",
)


def generate_llama(prompt, model="llama3.1-70b", max_tokens=5):
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=max_tokens,
        temperature=1,
    )

    return response.choices[0].message.content
