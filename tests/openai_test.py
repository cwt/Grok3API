from openai import OpenAI
from openai import OpenAIError

def send_message(message):
    """Sends a message to the server via the OpenAI client."""
    client = OpenAI(
        base_url="http://localhost:9000/v1",
        api_key="dummy"
    )
    try:
        response = client.chat.completions.create(
            model="grok-3",
            messages=[{"role": "user", "content": message}]
        )
        print("Server response:")
        print(f"Model: {response.model}")
        print(f"Message: {response.choices[0].message.content}")
        print(f"Finish reason: {response.choices[0].finish_reason}")
        print(f"Usage: {response.usage}")
    except OpenAIError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

def main():
    """Prompts the user for cookies and a message and sends the request."""
    print("Enter a message:")
    message = input().strip()
    if not message:
        print("Message cannot be empty.")
        return
    send_message(message)

if __name__ == "__main__":
    main()
