import asyncio
import os
from grok3api.client import GrokClient

# not necessary
cookies_dict = {
    "i18nextLng": "ru",
    "sso-rw": "sso-rw-token-placeholder",
    "sso": "sso-token-placeholder",
    "cf_clearance": "cf_clearance-placeholder",
    "_ga": "ga-placeholder",
    "_ga_8FEWB057YH": "ga-8FEWB057YH-placeholder"
}

# not necessary
cookie_str = (
    "i18nextLng=ru; sso-rw=sso-rw-token-placeholder; sso=sso-token-placeholder; cf_clearance=cf_clearance-placeholder; _ga=ga-placeholder; _ga_8FEWB057YH=ga-8FEWB057YH-placeholder"
)

async def main():
    client = GrokClient(
        history_msg_count=0,            # You can add cookies as str or dict (or List[dict or str]) format
        always_new_conversation=False
    )
    client.history.set_main_system_prompt("Respond briefly and with emojis.")
    os.makedirs("images", exist_ok=True)
    while True:
        prompt = input("Enter your query: ")
        if prompt == "q": break
        result = await client.async_ask(message=prompt,
                            modelName="grok-3",
                            history_id="0",
                            # images=["C:\\Users\\user\\Downloads\\photo.jpg",
                            #         "C:\\Users\\user\\Downloads\\website_screenshot.png"],
                            )
        if result.error:
            print(f"An error occurred: {result.error}")
            continue
        print(result.modelResponse.message)
        if result.modelResponse.generatedImages:
            for index, image in enumerate(result.modelResponse.generatedImages, start=1):
                image.save_to(f"images/gen_img_{index}.jpg")
        await client.history.async_to_file()

if __name__ == '__main__':
    asyncio.run(main())
