import os
from grok3.client import GrokClient


def main():
    message = "Создай изображение корабля"
    client = GrokClient()
    os.makedirs("images", exist_ok=True)
    result = client.ChatCompletion.create(message)
    if result and result.modelResponse and result.modelResponse.generatedImages:
            image = result.modelResponse.generatedImages[0]
            image.save_to(f"images/top_ship.jpg")


if __name__ == '__main__':
    main()