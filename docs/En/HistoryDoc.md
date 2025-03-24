# 📚 Description of the `History` class

## 🚀 Manages chat history with support for images, system prompts, and saving to JSON

The `History` class is designed to manage chat histories, including support for system prompts, as well as their saving and loading from a JSON file.

> ❗ **Important**:  
> Grok may misinterpret the history. Experiment with `history_as_json`. You can always disable automatic history saving by setting `history_msg_count` to `0` (by default, `history_msg_count = 0`).

> 📁 **Saving to a file**:  
> The history is automatically loaded from the file when initializing `GrokClient`, but you need to save it manually by calling `client.history.to_file`.

---

### 🌟 Example

```python
from grok3api.client import GrokClient


def main():
    # Activate auto-saving of history for 5 messages
    client = GrokClient(history_msg_count=5)

    # Set the main system prompt
    client.history.set_main_system_prompt("Imagine you are a basketball player")
    while True:
        prompt = input("Enter your query: ")
        if prompt == "q": break
        result = client.ask(prompt, "0")
        print(result.modelResponse.message)

        # Manually save the history to a file
        client.history.to_file()


if __name__ == '__main__':
    main()
```

---

### 📨 **Initialization**

The `History` class is automatically initialized when creating a `GrokClient` with the following parameters:

| Parameter           | Type   | Description                                                 | Default                 |
|---------------------|--------|-------------------------------------------------------------|-------------------------|
| `history_msg_count` | `int`  | Maximum number of messages in the chat history              | `0`                     |
| `history_path`      | `str`  | Path to the JSON file for saving and loading the history    | `"chat_histories.json"` |
| `history_as_json`   | `bool` | Format of history output: JSON (`True`) or string (`False`) | `True`                  |
| `history_auto_save` | `bool` | Automatically rewrite history to file after each message.   | `True`                  |

---

### 🎯 **Attributes**

| Attribute            | Type                                                 | Description                                                                                                                                                                              |
|----------------------|------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `chat_histories`     | `Dict[str, List[Dict[str, Union[str, List[Dict]]]]]` | Dictionary where keys are history identifiers (`history_id`), and values are lists of messages. Each message contains `role` (sender type) and `content` (list with text and/or images). |
| `history_msg_count`  | `int`                                                | Maximum number of messages in the history for each `history_id`.                                                                                                                         |
| `system_prompts`     | `Dict[str, str]`                                     | Dictionary of system prompts, where keys are `history_id`, and values are text prompts for specific histories.                                                                           |
| `main_system_prompt` | `Optional[str]`                                      | Main system prompt used if no specific prompt is set for a `history_id`.                                                                                                                 |
| `history_path`       | `str`                                                | Path to the JSON file for storing history.                                                                                                                                               |
| `history_as_json`    | `bool`                                               | Indicates whether to return the history in JSON format (`True`) or as a string with sender indication (`False`).                                                                         |

---

### 📜 **Methods**

| Method                   | Parameters                     | Returns | Description                                                                                                                                                                                     |
|--------------------------|--------------------------------|---------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `set_main_system_prompt` | `text: str`                    | -       | Sets the main system prompt, which will be used by default. Logs errors via `logger.error`.                                                                                                     |
| `set_system_prompt`      | `history_id: str`, `text: str` | -       | Sets the system prompt for a specific history identifier. Logs errors via `logger.error`.                                                                                                       |
| `get_system_prompt`      | `history_id: str`              | `str`   | Returns the system prompt for the specified identifier or an empty string if not set. Logs errors via `logger.error`.                                                                           |
| `to_file`                | -                              | -       | Saves the current data (`chat_histories`, `system_prompts`, `main_system_prompt`) to the JSON file. Data is written with indentation and without forcing ASCII. Logs errors via `logger.error`. |

---

> 💡 **Note**:  
> If `history_msg_count = 0`, the history will contain only the system prompt (if present).

---
