from grok3.client import GrokClient


def main():
    message = "Создай изображение корабля"
    client = GrokClient()

    result = client.ChatCompletion.create(message, timeout=10)
    print("Ответ Grok:", result.modelResponse.message)
    result.modelResponse.generatedImages[0].save_to("ship.jpg")

if __name__ == '__main__':
    main()