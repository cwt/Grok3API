🚀 A Python library for interacting with Grok 3 API without login or cookies required. Perfect for using out of the box.

## [➡️ Russian ReadMe](docs/Ru/RuReadMe.md)

# Grok3API: Client for Working with Grok 🤖

---

## 📦 Changelog

### 🆕 v0.0.1b10

#### ✨ New:
- 🔐 **Automatic cookie retrieval**  
  It is now **no longer required to manually provide cookies** — the client will automatically retrieve them if needed.  
  ➕ However, you **can still provide your own cookies** if you want to use your account (e.g., for generation with custom settings or access to premium features).

- 🤖 **Started work on OpenAI compatibility** ([**server.py**](grok3api/server.py), [**Demo**](tests/openai_test.py))
  The initial draft of OpenAI API compatibility server has been implemented. It **kind of works**, but:  
  > ⚠️ **It's in a very early stage and completely unpolished. Use at your own risk!**

---

**Grok3API** is a powerful and convenient unofficial client for interacting with Grok models (including Grok3), allowing you to send requests, receive text responses, and, most notably, **generated images** — all with automatic cookie management! 🎨✨ The project is designed with a focus on ease of use and automation, so you can concentrate on creativity rather than technical details.

---

## 🌟 Features

- 🚀 **Automatic cookie retrieval** via browser with bypassing Cloudflare — no manual setup required!
- 🖼️ **Convenient retrieval of generated images** with the `save_to` method, enabling you to save them with a single click.
- 🔧 **Flexible request configuration**: model selection, image generation management, attachment addition, and more.
- 📦 **Attachment support**: send files and images along with your requests.
- 🛠️ **Error handling**: the client itself solves problems with cookies and repeats requests if something goes wrong.
- 🤖 **[Telegram bot example](tests/SimpleTgBot/SimpleTgBot.py) (`grok3api` + `aiogram`)**, with the ability to create text replies and images.

---

## 📦 Installation

To start using Grok3API, install the necessary dependencies. It’s simple:

```bash
pip install grok3api
```

> ⚠️ **Important**: Ensure you have **Google Chrome** installed, as `undetected_chromedriver` works specifically with it.

After installing, you’re ready to begin! 🎉

---

## 🚀 Usage

### Quick Start

Here’s a complete example of how to send a request and save a generated image:

```python
from grok3api.client import GrokClient


def main():
  
  # You can add a list of strings/dictionaries to automatically change when the limit is reached
  #client = GrokClient(cookies="YOUR_COOKIES_FROM_BROWSER")
  
  # Create a client (cookies will be automatically retrieved if not present)
  client = GrokClient()

  # Create a request
  message = "Create an image of a ship"

  # Send the request
  result = client.ask(message)
  print("Grok's response:", result.modelResponse.message)

  # Save the first image if available
  if result.modelResponse.generatedImages:
    result.modelResponse.generatedImages[0].save_to("ship.jpg")
    print("Image saved as ship.jpg! 🚀")


if __name__ == '__main__':
  main()
```

This code:
1. Creates a client (cookies are fetched automatically if absent).
2. Sends a request to generate an image.
3. Saves the result to the file `ship.jpg`.

**📌 What will we see?**  
Grok will generate an image of a **ship**, for example, something like this:  

<img src="assets/ship.jpg" alt="Example spaceship" width="500">

> 💡 **Tip**: You don’t need to manually obtain cookies — the client handles it for you!

---

## 🔧 Request Parameters

The `GrokCLient.ask` method accepts numerous parameters to customize your request. Here’s an example with settings:

```python
from grok3api.client import GrokClient


def main():
  # Create a client
  client = GrokClient()

  # Send a request with settings
  result = client.ask(
    message="Draw a cat",
    modelName="grok-3",  # Default is grok-3
    imageGenerationCount=2,  # I want 2 cat image!
  )
  print(f"Grok3's response: {result.modelResponse.message}")

  # Save all images
  for i, img in enumerate(result.modelResponse.generatedImages):
    img.save_to(f"cat_{i}.jpg")
    print(f"Saved: cat_{i}.jpg 🐾")


if __name__ == '__main__':
  main()
```


### [💼️ Descriptions of the `GrokClient` class](docs/En/ClientDoc.md)
### [✈️ Descriptions of the `ask` method](docs/En/askDoc.md)
### [📋 Description of the `History` class](docs/En/HistoryDoc.md)
### [📬 Descriptions of the `GrokResponse` class](docs/En/GrokResponse.md)
### [🐧 Working with `Linux`](docs/En/LinuxDoc.md)

---

## 🖼️ Convenient Image Handling

One of the standout features of GrokClient is its **super-convenient handling of generated images**. Here’s a complete example:

```python
from grok3api.client import GrokClient


def main():
  # Create a client
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

> 🌟 **Cool Fact**: This works with automatically retrieved cookies! You don’t need to worry about access — the client sets everything up for you.
 
 ---
 
 ## 🔄 Automatic Cookie Retrieval
 
 If cookies are missing or outdated, GrokClient automatically:
 1. Uses a Chrome browser (ensure it’s installed).
 2. Visits `https://grok.com/`.
 3. Bypasses Cloudflare protection.
 4. Will continue to work.
 
 You don’t need to do anything manually — just run the code, and it will work!


---

## 📋 Response Processing

The `ask` method returns a `GrokResponse` object. Here’s an example of working with it:

```python
from grok3api.client import GrokClient


def main():
  
  # Create a client
  client = GrokClient()

  # Send a request
  result = client.ask("Describe and draw a forest")

  # Process the response
  print(f"Text: {result.modelResponse.message}")
  if result.modelResponse.generatedImages:
    result.modelResponse.generatedImages[0].save_to("forest.jpg")


if __name__ == '__main__':
  main()
```

**Fields of the `GrokResponse` object:**
- **`modelResponse`**: The main model response.
  - `message` (str): The text response.
  - `generatedImages` (List[GeneratedImage]): List of images.
- **`isThinking`**: Whether the model was thinking (bool).
- **`isSoftStop`**: Soft stop (bool).
- **`responseId`**: Response ID (str).
- **`newTitle`**: New chat title, if available (Optional[str]).

---

If anything is unclear, feel free to open an issue — we’ll sort it out together! 🌟

## 📄 License

The project is distributed under the **MIT** license. Details are available in the [LICENSE](LICENSE) file.

---

## Disclaimer

### Introduction

Grok3API is a third-party client for interacting with Grok.

Grok3API has no affiliation with xAI or the developers of Grok. It is an independent project created by a third party and is not supported, sponsored, or endorsed by xAI. Any issues related to the Grok API should be addressed directly to xAI.

### Responsibility and Warranties

The software is provided "as is," without any warranties, including fitness for a particular purpose or absence of errors. The creator of Grok3API is not liable for any losses or damages resulting from the use of the client. You use it at your own risk.

### Compliance with Laws

You are responsible for ensuring that your use of Grok3API complies with all applicable laws and regulations. The creator does not encourage illegal use.

Grok3API requires full compliance with the xAI API rules.
