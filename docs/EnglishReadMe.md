# Grok3API: Client for Working with Grok 🤖

**Grok3API** is a powerful and convenient unofficial client for interacting with Grok models (including Grok3), allowing you to send requests, receive text responses, and, most notably, **generated images** — all with automatic cookie management! 🎨✨ The project is designed with a focus on ease of use and automation, so you can concentrate on creativity rather than technical details.

---

## 🌟 Features

- 🚀 **Automatic cookie retrieval** via browser to bypass Cloudflare — no manual setup required! However, you can provide your own if desired.
- 🖼️ **Convenient retrieval of generated images** with the `save_to` method, enabling you to save them with a single click.
- 🔄 **Automatic cookie updates** for errors like "Too Many Requests" (HTTP 429).
- 💾 **Saving cookies to a .env file** for hassle-free reuse.
- 🔧 **Flexible request configuration**: model selection, image generation management, attachment addition, and more.
- 📦 **Attachment support**: send files and images along with your requests.
- 🛠️ **Error handling**: the client resolves cookie issues and retries requests if something goes wrong.

---

## 📦 Installation

To start using GrokClient, install the necessary dependencies. It’s simple:

```bash
pip install Grok3API
pip install undetected-chromedriver==3.5.5
```

### Dependencies:
- **undetected_chromedriver**: Used for automatic cookie retrieval while bypassing Cloudflare protection.

> ⚠️ **Important**: Ensure you have **Google Chrome** installed, as `undetected_chromedriver` works specifically with it.

Once the dependencies are installed, you’re ready to begin! 🎉

---

## 🚀 Usage

### Quick Start

Here’s a complete example of how to send a request and save a generated image:

```python
from grok3.client import GrokClient

def main():
    # Create a client (cookies will be automatically retrieved if not present)
    client = GrokClient()
    
    # Create a request
    message = "Create an image of a spaceship"
    
    # Send the request
    result = client.ChatCompletion.create(message)
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

> 💡 **Tip**: You don’t need to manually obtain cookies — the client handles it for you and saves them in `.env`!

---

## 🔧 Request Parameters

The `ChatCompletion.create` method accepts numerous parameters to customize your request. Here’s an example with settings:

```python
from grok3.client import GrokClient

def main():
    # Create a client
    client = GrokClient()
    
    # Send a request with settings
    result = client.ChatCompletion.create(
        message="Draw a cat",
        modelName="grok-3",      # Default is grok-3
        imageGenerationCount=3,  # I want 3 cat images!
    )
    print(f"Grok3's response: {result.modelResponse.message}")
    
    # Save all images
    for i, img in enumerate(result.modelResponse.generatedImages):
        img.save_to(f"cat_{i}.jpg")
        print(f"Saved: cat_{i}.jpg 🐾")

if __name__ == '__main__':
    main()
```

### Complete Parameter List:

| Parameter               | Type             | Description                                             | Default      |
|-------------------------|------------------|---------------------------------------------------------|--------------|
| `message`               | `str`            | **Required**. The request text for Grok.                | -            |
| `auto_update_cookies`   | `bool`           | Automatically update cookies on errors.                 | `True`       |
| `env_file`              | `str`            | Path to the `.env` file for storing cookies.            | `".env"`     |
| `temporary`             | `bool`           | Indicates if the request or session is temporary.       | `False`      |
| `modelName`             | `str`            | Name of the AI model (e.g., "grok-3").                  | `"grok-3"`   |
| `fileAttachments`       | `List[Dict]`     | List of file attachments (keys: `name`, `content`).     | `[]`         |
| `imageAttachments`      | `List[Dict]`     | List of image attachments (keys: `name`, `content`).    | `[]`         |
| `customInstructions`    | `str`            | Additional instructions for the model.                  | `""`         |
| `disableSearch`         | `bool`           | Disable search in model responses.                      | `False`      |
| `enableImageGeneration` | `bool`           | Enable image generation.                                | `True`       |
| `enableImageStreaming`  | `bool`           | Enable image streaming.                                 | `True`       |
| `enableSideBySide`      | `bool`           | Enable side-by-side information display.                | `True`       |
| `imageGenerationCount`  | `int`            | Number of images to generate.                           | `2`          |
| `isPreset`              | `bool`           | Indicates if the message is preset.                     | `False`      |
| `isReasoning`           | `bool`           | Enable reasoning mode for the model.                    | `False`      |
| `returnImageBytes`      | `bool`           | Return images as bytes.                                 | `False`      |
| `toolOverrides`         | `Dict[str, Any]` | Override tool settings.                                 | `{}`         |

---

## 🖼️ Convenient Image Handling

One of the standout features of GrokClient is its **super-convenient handling of generated images**. Here’s a complete example:

```python
from grok3.client import GrokClient

def main():
    # Create a client
    client = GrokClient()
    
    # Send a request
    result = client.ChatCompletion.create("Draw a sunset over the sea")
    
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
1. Launches a Chrome browser (ensure it’s installed).
2. Visits `https://grok.com/`.
3. Bypasses Cloudflare protection.
4. Saves cookies to `.env`.

You don’t need to do anything manually — just run the code, and it will work!

---

## 💾 Saving Cookies

After retrieval, cookies are saved to the `.env` file under the key `INCOGNITO_COOKIES`. Example:

```
INCOGNITO_COOKIES="cookie1=value1; cookie2=value2"
```

On subsequent runs, the client will automatically use them unless you provide your own.

---

## 📋 Response Processing

The `create` method returns a `GrokResponse` object. Here’s an example of working with it:

```python
from grok3.client import GrokClient

def main():
    # Create a client
    client = GrokClient()
    
    # Send a request
    result = client.ChatCompletion.create("Describe and draw a forest")
    
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

## 🚨 Error Handling

GrokClient is equipped to handle issues:
- **HTTP 429 (Too Many Requests)**: Automatically updates cookies and retries the request.
- **Missing cookies**: Retrieves them via the browser.
- **Other errors**: Logged for debugging.

---

## 📄 License

The project is distributed under the **MIT** license. Details are available in the [LICENSE](../LICENSE) file.

If anything is unclear, feel free to open an issue — we’ll sort it out together! 🌟

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
