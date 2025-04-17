# Descriptions of the `ask` method

## 🚀 Sends a request to the Grok API and receives a response. There is an asynchronous variant `async_ask`.

### 📨 **Takes:**  
- 📜 `message`: The text of the request for the model.  
- ⚙ `**kwargs`: Additional parameters for configuration.  

### 🎯 **Returns:**  
- `GrokResponse` – an object containing the response from the Grok API.
- **[Description of the `GrokResponse`](GrokResponse.md)**

### Complete Parameter List:

| Parameter               | Type                                                                  | Description                                                                                                                              | Default    |
|-------------------------|-----------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------|------------|
| `message`               | `str`                                                                 | **Required**. The request text for Grok.                                                                                                 | -          |
| `history_id`            | `str`                                                                 | Identifier in the history dictionary (if auto saving history is used)                                                                    | `None`     |
| `timeout`               | `int`                                                                 | Timeout for one wait to receive a response (seconds).                                                                                    | `45`       |
| `temporary`             | `bool`                                                                | Indicates if the request or session is temporary.                                                                                        | `False`    |
| `modelName`             | `str`                                                                 | Name of the AI model (e.g., "grok-3").                                                                                                   | `"grok-3"` |
| `images`                | `str_path` / `str_base64` / `BytesIO` / `List[str]` / `List[BytesIO]` | Either the path to an image, a base64-encoded image, or a BytesIO (or a list of any of these) to send. fileAttachments must not be used. | `None`     |
| `fileAttachments`       | `List[str]`                                                           | List of file attachments (keys: `name`, `content`).                                                                                      | `[]`       |
| `imageAttachments`      | `List[]`                                                              | List of image attachments (keys: `name`, `content`).                                                                                     | `[]`       |
| `customInstructions`    | `str`                                                                 | Additional instructions for the model.                                                                                                   | `""`       |
| `disableSearch`         | `bool`                                                                | Disable search in model responses.                                                                                                       | `False`    |
| `enableImageGeneration` | `bool`                                                                | Enable image generation.                                                                                                                 | `True`     |
| `enableImageStreaming`  | `bool`                                                                | Enable image streaming.                                                                                                                  | `True`     |
| `enableSideBySide`      | `bool`                                                                | Enable side-by-side information display.                                                                                                 | `True`     |
| `imageGenerationCount`  | `int`                                                                 | Number of images to generate.                                                                                                            | `4`        |
| `isPreset`              | `bool`                                                                | Indicates if the message is preset.                                                                                                      | `False`    |
| `isReasoning`           | `bool`                                                                | Enable reasoning mode for the model.                                                                                                     | `False`    |
| `returnImageBytes`      | `bool`                                                                | Return images as bytes.                                                                                                                  | `False`    |
| `toolOverrides`         | `Dict[str, Any]`                                                      | Override tool settings.                                                                                                                  | `{}`       |

> 💡 It is important to understand that these parameters are obtained by reverse engineering browser requests. And, perhaps, some of them may not yet have functionality, especially considering the freshness of the `Grok3` model

> ❗ Descriptions of those parameters whose functionality could not be confirmed in testing are based on similar parameters in the official xAI API documentation.

> 🛠️ You can contribute by simply experimenting with different options!
