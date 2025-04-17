from openai import OpenAI
from openai import OpenAIError

def send_message( message):
    """Отправляет сообщение на сервер через OpenAI клиент."""
    client = OpenAI(
        base_url="http://localhost:9000/v1",
        api_key="dummy"
    )
    try:
        response = client.chat.completions.create(
            model="grok-3",
            messages=[{"role": "user", "content": message}]
        )
        print("Ответ сервера:")
        print(f"Модель: {response.model}")
        print(f"Сообщение: {response.choices[0].message.content}")
        print(f"Причина завершения: {response.choices[0].finish_reason}")
        print(f"Использование: {response.usage}")
    except OpenAIError as e:
        print(f"Ошибка: {e}")
    except Exception as e:
        print(f"Неожиданная ошибка: {e}")

def main():
    """Запрашивает куки и сообщение у пользователя и отправляет запрос."""
    print("Введите сообщение:")
    message = input().strip()
    if not message:
        print("Сообщение не может быть пустым.")
        return
    send_message(message)

if __name__ == "__main__":
    main()