import os
import httpx
import json

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"


async def call_openai(messages: list[dict]):
    prompt = (
        "Extract all passenger and ticket information from the following conversation for an airline booking. "
        "Return a JSON object with these fields:\n"
        "{\n"
        '  "airportName": string,\n'
        '  "travelDate": string,\n'
        '  "flightNumber": string,\n'
        '  "passengers": [\n'
        '    { "fullName": string, "nationalId": string, "luggageCount": number }\n'
        "  ]\n"
        "}\n"
        "If any field is missing, use an empty string or 0. Only return the JSON object, nothing else.\n\n"
        "Conversation:\n"
        + "\n".join(f"{m['sender']}: {m['content']}" for m in messages)
    )
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_API_KEY}",
    }
    data = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful assistant for airline ticket booking.",
            },
            {"role": "user", "content": prompt},
        ],
        "temperature": 0,
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(OPENAI_API_URL, headers=headers, json=data)
        response.raise_for_status()
        result = response.json()
        text = result["choices"][0]["message"]["content"]
        try:
            return json.loads(text)
        except Exception:
            import re

            match = re.search(r"\{[\s\S]*\}", text)
            if match:
                return json.loads(match.group(0))
            raise ValueError("Failed to parse OpenAI response")
