# 🧠 Grok3API OpenAI-Compatible Server

> 🤖 **Early stage of server development**

The first draft of a server compatible with the OpenAI API (`/v1/chat/completions`) has been implemented.

> ⚠️ **It's in the early stage and not fully debugged. Use it at your own risk!**

---

### ⚙️ Running the Server

> Make sure you have `fastapi`, `uvicorn`, `pydantic`, and `grok3api` installed.

```bash
# From the project root:
python -m grok3api.server
```

```bash
# Or you can configure the host and port
python -m grok3api.server --host 127.0.0.1 --port 9000
```

🎉 The server will start at `http://127.0.0.1:9000`.

> Uses `uvicorn` under the hood. Make sure the project structure allows for module-based execution (via `-m`).

---

## 🔁 Endpoint: `/v1/chat/completions`

Compatible with the OpenAI request format:

### 📥 Example request:

```python
from openai import OpenAI
from openai import OpenAIError

# Creating a client with the specified URL and key
client = OpenAI(
    base_url="http://localhost:9000/v1",
    api_key="dummy"
)

try:
    # Sending a request to the server
    response = client.chat.completions.create(
        model="grok-3",
        messages=[{"role": "user", "content": "What is Python?"}]
    )

    # Displaying the response from the server
    print("Server Response:")
    print(f"Model: {response.model}")
    print(f"Message: {response.choices[0].message.content}")
    print(f"Finish Reason: {response.choices[0].finish_reason}")
    print(f"Usage: {response.usage}")

except OpenAIError as e:
    print(f"Error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

> `stream` is not supported, a `400 Bad Request` will be returned.

---

### 📤 Output:

```
Server Response:
Model: grok-3
Message: Python is a high-level, interpreted programming language with a simple and readable syntax. It supports multiple programming paradigms (object-oriented, functional, procedural) and is widely used for web development, data analysis, task automation, machine learning, and more. Python is popular for its versatility, extensive standard library, and large developer community.
Finish Reason: stop
Usage: CompletionUsage(completion_tokens=46, prompt_tokens=3, total_tokens=49, completion_tokens_details=None, prompt_tokens_details=None)
```

---


## 🧵 Endpoint: `/v1/string` (GET)

A simple text GET request. Accepts a string as a query parameter and returns a response from Grok without JSON wrapping.

### 📥 Example Request:

Open in a browser or use `curl`:

```bash
curl http://localhost:9000/v1/string?q=Hello
```

### 📤 Example Response:

```
Hello! How can I help?
```

### 🐍 Example in Python:

```python
import requests

response = requests.get("http://localhost:9000/v1/string", params={"q": "Tell a joke"})
print(response.text)  # Just text, no JSON
```

---

## 🧵 Endpoint: `/v1/string` (POST)

A simple text POST request. Accepts a string in the request body and returns a response from Grok without JSON wrapping.

### 📥 Example Request:

Use `curl` or another tool:

```bash
curl -X POST http://localhost:9000/v1/string -d "Hello"
```

### 📤 Example Response:

```
Hello! How can I help?
```

### 🐍 Example in Python:

```python
import requests

response = requests.post("http://localhost:9000/v1/string", data="Tell a joke")
print(response.text)  # Just text, no JSON
```

---



## ⚙️ Environment Variables (optional)

| Variable           | Description                                 | Default Value |
|--------------------|---------------------------------------------|---------------|
| `GROK_COOKIES`     | Cookies file for GrokClient                 | `None`        |
| `GROK_PROXY`       | Proxy (e.g., `http://localhost:8080`)       | `None`        |
| `GROK_TIMEOUT`     | Grok request timeout (in seconds)           | `120`         |
| `GROK_SERVER_HOST` | IP address for running the server           | `0.0.0.0`     |
| `GROK_SERVER_PORT` | Port for running the server                 | `8000`        |

---

## 📂 Project Structure

```
Grok3API/
├── grok3api/
│   ├── server.py          # <--- running the server
│   ├── client.py
│   ├── types/
│   └── ...
├── tests/
│   └── openai_test.py     # <--- compatibility test
└── README.md
```

---

## ❗ TODO / Known Issues

- [ ] 🔄 Streaming support (`stream=True`)
- [ ] 🧪 More tests and validation
- [ ] 🧼 Refactor `message_payload` and history logic
- [ ] 🧩 Custom instructions, images, and additional features

---

💬 For questions and suggestions — feel free to open an issue!