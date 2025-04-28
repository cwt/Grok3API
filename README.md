🚀 A Python library for interacting with the Grok 3 API without requiring login or manual cookie input. Perfect for out-of-the-box use.
## [➡ Ru ReadMe](docs/Ru/RuReadMe.md)

# 🤖 Grok3API: Client for Working with Grok

---

## [📦 Full Changelog](docs/En/ChangeLog.md)

### 🆕 v0.0.9b1

#### ✨ New:
- 💬 **Support for continuing conversations with Grok** — `client.ask` now uses `conversation_id` and `response_id` to continue conversations. See [issue](https://github.com/boykopovar/Grok3API/issues/4)
- ➕ **New conversation control parameters**:
  - `always_new_conversation` — always start a new chat.
  - `new_conversation` — start a new chat when sending a request.
- 🆙 **Extended `GrokResponse` object** — new fields added: `conversationId`, `title`, `conversationCreateTime`, `conversationModifyTime`, `temporary`.

#### 📋 Notes:
- ✅ Chats are now saved on Grok servers and loaded automatically during requests.
- ⚠️ Chats created with different cookies cannot be loaded.

---


**Grok3API** is a powerful and user-friendly unofficial tool for interacting with Grok models (including Grok3), allowing you to send requests, receive text responses, and, most excitingly, **generated images** — all with automatic cookie management! 🎨✨ The project is designed with simplicity and automation in mind, so you can focus on creativity rather than technical details.

---

## 🌟 Features

- 🚀 **Automatic cookie retrieval** via browser with Cloudflare bypass — no manual setup required!  
- 🖼️ **Convenient retrieval of generated images** with the `save_to` method, enabling one-click saving.  
- 🔧 **Flexible request customization**: model selection, image generation control, attachment support, and more.  
- 📦 **Attachment support**: send files and images along with requests.  
- 🛠️ **Error handling**: the client automatically resolves cookie issues and retries requests if something goes wrong.  
- 🤖 **[Example Telegram bot](tests/SimpleTgBot/SimpleTgBot.py) (`grok3api` + `aiogram`)**, capable of generating text responses and images.  
---

## 📦 Installation

To start using GrokClient, install the required dependencies. It’s simple:

```bash
pip install grok3api
```

> ⚠️ **Important**: Ensure **Google Chrome** is installed, as `undetected_chromedriver` relies on it.

After installation, you’re ready to go! 🎉

---

## 🚀 Usage

### Quick Start  

Here’s a complete example of sending a request and saving a generated image:

```python
from grok3api.client import GrokClient


def main():
    # Create a client (cookies are automatically retrieved if not provided)
    client = GrokClient()

    # Create a request
    message = "Create an image of a ship"

    # Send the request
    result = client.ask(message=message,
                        images="C:\\Users\\user\\Downloads\\photo1_to_grok.jpg") # You can send an image to Grok
    
    print("Grok's response:", result.modelResponse.message)

    # Save the first image, if available
    if result.modelResponse.generatedImages:
        result.modelResponse.generatedImages[0].save_to("ship.jpg")
        print("Image saved as ship.jpg! 🚀")


if __name__ == '__main__':
    main()
```

This code:  
1. **Creates a client** — automatically retrieves cookies if none are provided.  
2. **Sends a request** to generate an image.  
3. **Saves the image** to the file `ship.jpg`.  

📌 **What will we see?**  
Grok will generate an image of a **ship**, for example, something like this:  

<img src="assets/ship.jpg" alt="Ship example" width="500">

🐹 Or, for instance, if you request "**A gopher on Elbrus**":

<img src="assets/gopher.jpg" alt="Gopher on Elbrus" width="500">

> 💡 **Cool feature**: You don’t need to manually fetch cookies — the client handles it for you!

---

## 🔧 Request Parameters

The `GrokClient.ask` method accepts various parameters to customize your request. Here’s an example with settings:

```python
from grok3api.client import GrokClient


def main():
    
    # Create a client (cookies are automatically retrieved if not provided)
    client = GrokClient(history_msg_count=5, always_new_conversation=False) # to use conversation history from grok.com
    client.history.set_main_system_prompt("Respond briefly and with emojis.")

    # Send a request with settings
    result = client.ask(
        message="Draw a cat like in this picture",
        modelName="grok-3",  # Default is grok-3 anyway
        images=["C:\\Users\\user\\Downloads\\photo1_to_grok.jpg",
                "C:\\Users\\user\\Downloads\\photo2_to_grok.jpg"] # You can send multiple images to Grok!
    )
    print(f"Grok3 response: {result.modelResponse.message}")

    # Save all images
    for i, img in enumerate(result.modelResponse.generatedImages):
        img.save_to(f"cat_{i}.jpg")
        print(f"Saved: cat_{i}.jpg 🐾")


if __name__ == '__main__':
    main()
```

> 🌟 **The best part? It works with automatically retrieved cookies!** No need to worry about access — the client sets everything up for you.

---

## 🔄 Automatic Cookie Retrieval

If cookies are missing or expired, Grok3API automatically:  
1. Uses the Chrome browser (ensure it’s installed).  
2. Visits `https://grok.com/`.  
3. Bypasses Cloudflare protection.  
4. Continues operation.  

You don’t need to do anything manually — just run the code, and it works!

### [💼️ `GrokClient` Class Description](docs/En/ClientDoc.md)  
### [✈️ `ask` Method Description](docs/En/askDoc.md)  
### [📋 `History` Class Description](docs/En/HistoryDoc.md)  
### [📬 `GrokResponse` Class Description](docs/En/GrokResponse.md)  
### [🐧 Working with `Linux`](docs/En/LinuxDoc.md)  
### [🌐 Running an OpenAI-Compatible Server](docs/En/OpenAI_Server.md)  

---

## 🖼️ Convenient Image Retrieval

One of the standout features of GrokClient is its **super-convenient handling of generated images**. Here’s a complete example:

```python
from grok3api.client import GrokClient


def main():
    # Create a client (cookies are automatically retrieved if not provided)
    client = GrokClient()

    # Send a request
    result = client.ask("Draw a sunset over the sea")

    # Save all images
    for i, image in enumerate(result.modelResponse.generatedImages):
        image.save_to(f"sunset_{i}.jpg")
        print(f"Saved: sunset_{i}.jpg 🌅")


if __name__ == '__main__':
    main()
```

---

## 📋 Response Handling

The `ask` method returns a `GrokResponse` object. Here’s an example of working with it:

```python
from grok3api.client import GrokClient


def main():
    cookies = "YOUR_COOKIES_FROM_BROWSER"
    
    # Create a client
    client = GrokClient(cookies=cookies)

    # Send a request
    result = client.ask("Describe and draw a forest")

    # Process the response
    print(f"Text: {result.modelResponse.message}")
    result.modelResponse.generatedImages[0].save_to("forest.jpg")


if __name__ == '__main__':
    main()
```

Fields of the `GrokResponse` object:  
- **`modelResponse`**: The main model response.  
  - `message` (str): The text response.  
  - `generatedImages` (List[GeneratedImage]): List of images.  
- **`isThinking`**: Whether the model was thinking (bool).  
- **`isSoftStop`**: Soft stop (bool).  
- **`responseId`**: Response ID (str).  
- **`newTitle`**: New chat title, if available (Optional[str]).  

### [📬 Detailed `GrokResponse` Class Description](docs/En/GrokResponse.md)

---

If something’s unclear, feel free to raise an issue — we’ll figure it out together! 🌟

## Disclaimer
Grok3API has no affiliation with xAI or the Grok developers. It is an independent project created by a third party and is not supported, sponsored or endorsed by xAI. Any issues with Grok should be addressed directly to xAI.
You are responsible for ensuring that your use of Grok3API complies with all applicable laws and regulations. The developer does not encourage illegal use.
