import os
from grok3api.client import GrokClient


def main():
    client = GrokClient()
    os.makedirs("images", exist_ok=True)
    while(True):
        result = client.ChatCompletion.create(input())
        print(result.modelResponse.message)
        if result and result.modelResponse and result.modelResponse.generatedImages:
                image = result.modelResponse.generatedImages[0]
                image.save_to(f"images/top_ship.jpg")
if __name__ == '__main__':
    main()