import asyncio
import os
from grok3api.client import GrokClient


async def main():
    client = GrokClient(history_msg_count=5)
    client.history.set_main_system_prompt("Отвечай коротко и с эмодзи.")
    os.makedirs("images", exist_ok=True)
    while True:
        prompt = input("Ведите запрос: ")
        if prompt == "q": break
        result = await client.async_ask(prompt, "0")
        print(result.modelResponse.message)
        if result.modelResponse.generatedImages:
                image = result.modelResponse.generatedImages[0]
                await image.async_save_to(f"images/gen_img.jpg")
        await client.history.async_to_file()

if __name__ == '__main__':
    asyncio.run(main())