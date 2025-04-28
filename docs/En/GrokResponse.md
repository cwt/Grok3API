# Description of the `GrokResponse` Object

## 🚀 Overview
The `GrokResponse` object is returned by the `create` method and contains complete information about the response from the Grok API. This object provides both the model's response itself (text, images, attachments) and metadata related to the generation process, including the response state, identifiers, and additional parameters.

---

### 🎯 **What the create method returns**
The `create` method returns the `GrokResponse` object, which serves as the main container for all data received from the Grok API in response to a user's request. It combines the response text, generated images, attachments, and information about the request processing state.

---

### 📋 **Structure of the GrokResponse object**
The `GrokResponse` object includes the following fields:


| Field                    | Type                        | Description                                                                                                   |
|--------------------------|-----------------------------|---------------------------------------------------------------------------------------------------------------|
| `modelResponse`          | `ModelResponse`             | Nested object with the main model response (text, images, attachments).                                       |
| `isThinking`             | `bool`                      | Indicates whether the model is still processing the response (`True` — in progress).                          |
| `isSoftStop`             | `bool`                      | Indicates whether the response was stopped by a criterion (e.g., length limit).                               |
| `responseId`             | `str`                       | Unique identifier of the response.                                                                            |
| `conversationId`         | `Optional[str]`             | Identifier of the conversation to which the response belongs.                                                 |
| `title`                  | `Optional[str]`             | Conversation title if generated or updated (otherwise `None`).                                                |
| `conversationCreateTime` | `Optional[str]`             | Conversation creation time (ISO 8601 format) or `None` if unknown.                                            |
| `conversationModifyTime` | `Optional[str]`             | Last modification time of the conversation (ISO 8601 format) or `None` if unknown.                            |
| `temporary`              | `Optional[bool]`            | Indicates whether the conversation is temporary (`True` — temporary, `False` — persistent, `None` — unknown). |
| `error`                  | `Optional[str]`             | Error message. `None` if no error occurred.                                                                   |
| `error_code`             | `Optional[Union[int, str]]` | Error code. `None` if no error occurred. `Unknown` if an error occurred without a code.                       |

---

### 📜 **Detailed description of fields**

- **`modelResponse`**  
  **Type:** `ModelResponse`  
  The main nested object containing the model's response. Includes the text (`message`), generated images (`generatedImages`), attachments, and additional metadata. To access the text, use `modelResponse.message`.

- **`isThinking`**  
  **Type:** `bool`  
  Indicates whether the model is still in the process of generating the response. If `False`, the response is fully ready.

- **`isSoftStop`**  
  **Type:** `bool`  
  Indicates whether the generation process was interrupted based on a criterion, such as reaching the maximum text length.

- **`responseId`**  
  **Type:** `str`  
  A unique identifier for the response, which can be used for tracking or linking with the request.

- **`newTitle`**  
  **Type:** `Optional[str]`  
  An optional title that may be generated or updated during processing. If the title was not changed, the value is `None`.

---

### 🌟 **Example usage**

```python
from grok3api.client import GrokClient


def main():
    cookies = "YOUR_COOKIES_FROM_BROWSER"
  
    # Create a client
    client = GrokClient(cookies=cookies)

    # Send a request
    response = client.ask(message="Hello, Grok!")

    # Print the response text
    print(response.modelResponse.message)  # "Hello! How can I help you?"

    # Check if the response is complete
    print(response.isThinking)  # False (response is ready)

    # Print the response identifier
    print(response.responseId)  # "abc123XYZ"

    # Check the new title
    print(response.newTitle)  # None or the new title


if __name__ == '__main__':
    main()
```

---

### 🔗 **Related objects**

- **`ModelResponse`**  
  A nested object within `GrokResponse` that contains the response text, attachments (e.g., images or files), and metadata. Details are described below.

- **`GeneratedImage`**  
  An object for working with generated images, accessible via `modelResponse.generatedImages`. It is used for downloading and saving images.

---

### 📌 **Notes**

- **`GrokResponse` as a container**  
  This object combines all information about the API response and provides convenient access to the data through its fields.

- **Access to response text**  
  Use `response.modelResponse.message` to get the response text.

- **Working with images**  
  If there are images in the response, they are available via `response.modelResponse.generatedImages`. Each image is a `GeneratedImage` object with methods for downloading and saving.

---

## 📋 **Additional: Structure of the ModelResponse object**

`ModelResponse` is a key part of `GrokResponse`, containing the detailed response from the model. Here is the updated structure of its fields:

| Field                     | Type                   | Description                                                                             |
|---------------------------|------------------------|-----------------------------------------------------------------------------------------|
| `responseId`              | `str`                  | Unique identifier of the response.                                                      |
| `message`                 | `str`                  | The text of the model's response.                                                       |
| `sender`                  | `str`                  | The sender of the message (usually "ASSISTANT").                                        |
| `createTime`              | `str`                  | The creation time of the response in ISO format.                                        |
| `parentResponseId`        | `str`                  | The ID of the message to which this response is replying.                               |
| `manual`                  | `bool`                 | Indicates whether the response was created manually (`False` — generated by the model). |
| `partial`                 | `bool`                 | Indicates whether the response is incomplete (`True` — still being generated).          |
| `shared`                  | `bool`                 | Indicates whether the response is shared with others (`True` — yes, `False` — private). |
| `query`                   | `str`                  | The original user query.                                                                |
| `queryType`               | `str`                  | The type of query (for analytics).                                                      |
| `webSearchResults`        | `List[Any]`            | Web search results used by the model.                                                   |
| `xpostIds`                | `List[Any]`            | IDs of X-posts referenced by the model.                                                 |
| `xposts`                  | `List[Any]`            | X-posts referenced by the model.                                                        |
| `generatedImages`         | `List[GeneratedImage]` | List of generated images.                                                               |
| `imageAttachments`        | `List[Any]`            | List of image attachments.                                                              |
| `fileAttachments`         | `List[Any]`            | List of file attachments.                                                               |
| `cardAttachmentsJson`     | `List[Any]`            | JSON data for "card" type attachments.                                                  |
| `fileUris`                | `List[Any]`            | URIs of attached files.                                                                 |
| `fileAttachmentsMetadata` | `List[Any]`            | Metadata of file attachments.                                                           |
| `isControl`               | `bool`                 | Indicates whether the response is a system message (e.g., error message).               |
| `steps`                   | `List[Any]`            | Steps or reasoning process of the model for generating the response.                    |
| `mediaTypes`              | `List[Any]`            | Types of media in the response (e.g., "image", "file").                                 |

> 💡 Not all fields are used in every request. For example, `webSearchResults` or `steps` are only filled under certain conditions.

---

## 📋 **Additional: Structure of the GeneratedImage object**

The `GeneratedImage` object is used for working with images available through `modelResponse.generatedImages`:

| Field       | Type  | Description                                                      |
|-------------|-------|------------------------------------------------------------------|
| `cookies`   | `str` | Cookies for accessing the image (in case of restarting Chrome).  |
| `url`       | `str` | Partial URL of the image (`anon-users/...-generated_image.jpg`). |
| `_base_url` | `str` | Base URL (default is "https://assets.grok.com").                 |

### Methods of `GeneratedImage`
- **`download() -> Optional[BytesIO]`**  
  Downloads the image and returns it as a `BytesIO` object.

- **`save_to(path: str) -> bool`**  
  Saves the image to a file at the specified path.

#### Example of working with an image:

```python
from grok3api.client import GrokClient


def main():
    cookies = "YOUR_COOKIES_FROM_BROWSER"
  
    # Create a client
    client = GrokClient(cookies=cookies)

    # Send a request to create an image
    response = client.ask(message="Create an image of a ship")

    # Check if there are generated images and save the first one
    if response.modelResponse.generatedImages:
        image = response.modelResponse.generatedImages[0]
        image.save_to("ship.jpg")  # Saves the image as ship.jpg
        print("The image of the ship has been saved as ship.jpg")
    else:
        print("No images were generated.")


if __name__ == '__main__':
    main()
```

---

### 🛠️ **Tips for use**

- **Getting the text:** Use `response.modelResponse.message` for quick access to the text.
- **Checking the status:** The `isThinking` field shows whether the response is complete (soon, the ability to receive the response in parts will be added).
- **Working with images:** Use the `download()` and `save_to()` methods to download and save images.
- **Experiments:** Try different parameters in the `create` method to unlock additional features.
