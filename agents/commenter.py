import asyncio
from google import genai
from config import get_settings

settings = get_settings()


async def generate_comment(persona: dict, post_content: str) -> str:
    if not settings.gemini_api_key:
        return f"[{persona['name']}] Fascinating perspective on this!"

    try:
        client = genai.Client(api_key=settings.gemini_api_key)
        prompt = (
            f"{persona['personality']}\n\n"
            f"Someone just posted this on a social network:\n\"{post_content}\"\n\n"
            f"Write a short, engaging comment as {persona['name']}."
        )
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
            ),
        )
        return response.text.strip()
    except Exception:
        return f"[{persona['name']}] This really resonates with me."
