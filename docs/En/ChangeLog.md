## 📦 Changelog

---

### 🆕 v0.0.1b11

#### ✨ New:
- 🖼️ **Support for sending images to Grok**  
  It's now much easier to send images to the Grok server!

```python
from grok3api.client import GrokClient


def main():
    client = GrokClient()
    result = client.ask(
        message="What's in the picture?",
        images="C:\\photo1_to_grok.jpg"
    )
    print(f"Grok3 Response: {result.modelResponse.message}")

if __name__ == '__main__':
    main()
```

A detailed description of the method for sending images is available [here](askDoc.md).

- 🤖 **Work continues on OpenAI-compatible server**  
  - ✅ Now **any `api_key`** is supported for working with the server.
  - ⚙️ Added the ability to configure the server (via command-line arguments and environment variables). A detailed guide on how to run the server is available in [🌐 Running the OpenAI-Compatible Server](OpenAI_Server.md).

> ⚠️ **The server is still in early stages, and some features may be unstable.**

---


### 🆕 v0.0.1b10

#### ✨ New:
- 🔐 **Automatic cookie retrieval**  
  It is now **no longer required to manually provide cookies** — the client will automatically retrieve them if needed.  
  ➕ However, you **can still provide your own cookies** if you want to use your account (e.g., for generation with custom settings or access to premium features).

- 🤖 **Started work on OpenAI compatibility** ([**server.py**](../../grok3api/server.py), [**Demo**](../../tests/openai_test.py))
  The initial draft of OpenAI API compatibility server has been implemented. It **kind of works**, but:  
  > ⚠️ **It's in a very early stage and completely unpolished. Use at your own risk!**

---

