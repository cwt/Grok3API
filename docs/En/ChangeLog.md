## 📦 Changelog



---

### 🆕 v0.0.9b1

#### ✨ New:
- 💬 **Support for continuing existing conversations with Grok ([issue](https://github.com/boykopovar/Grok3API/issues/4))**  
  `client.ask` can now automatically continue an existing conversation using `conversation_id` and `response_id`. These parameters are retrieved automatically after sending the first message but can also be manually set when creating the client.  
  If valid, requests are sent to the current conversation instead of creating a new one, which improves history management and responsiveness.

- ➕ **New parameters for conversation control**  
  - `always_new_conversation` — client parameter: always starts a new chat regardless of previous messages.
  - `new_conversation` — `ask` method parameter: manually starts a new chat for the current request (does not affect the saved History).  
    When using server-side history, the History from the class will only be added to the first message of each server-side chat (e.g., when cookies are rotated, a new server chat is created).

- 🆙 **Extended `GrokResponse` object**  
  Now also includes additional conversation-related fields:
  - `conversationId` — conversation identifier.
  - `title` — chat title if generated or updated.
  - `conversationCreateTime` — conversation creation timestamp.
  - `conversationModifyTime` — last conversation modification timestamp.
  - `temporary` — temporary chat flag (`True` — temporary, `False` — permanent, `None` — unknown).

---

#### 📋 Notes:
- ✅ Chats are now saved on Grok servers and loaded automatically during requests even without using the built-in `History`.
- ⚠️ Chats created with different cookies cannot be loaded — this is a server-side limitation (rotating cookies automatically creates a new server chat).

#### 📚 More:
- [💼️ GrokClient class description](ClientDoc.md)
- [✈️ `ask` method description](askDoc.md)
- [📋 History class description](HistoryDoc.md)
- [📬 GrokResponse class description](GrokResponse.md)

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

