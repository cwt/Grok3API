import os
from grok3api.client import GrokClient


def main():
    message = "Create an image of a ship"
    client = GrokClient()
    os.makedirs("images", exist_ok=True)

    for i in range(5):
        result = client.ask(message)

        if result and result.modelResponse and result.modelResponse.generatedImages:
            image = result.modelResponse.generatedImages[0]
            image.save_to(f"images/{i}.png")
        else:
            print(f"Error: failed to obtain image for iteration {i}.")

if __name__ == '__main__':
    main()
