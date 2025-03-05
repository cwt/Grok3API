# 📚 Description of the `History` class

## 🚀 Manages chat history, system prompts, and saves data to a JSON file

The `History` class is designed to manage chat histories, system prompts, and save them to a JSON file. It allows adding messages, retrieving history in JSON format, setting system prompts, and saving/loading data from a file. Below is a detailed description of the initialization, attributes, and methods of the class.

---

### 📨 **Initialization**

The `History` class is initialized with two parameters, which are presented in the table below:

| Parameter           | Type  | Description                                          | Default                 |
|---------------------|-------|------------------------------------------------------|-------------------------|
| `history_msg_count` | `int` | Maximum number of messages in the chat history       | `0`                     |
| `file_path`         | `str` | Path to the JSON file for saving and loading history | `"chat_histories.json"` |

---

### 🎯 **Attributes**

| Attribute            | Type                              | Description                                                                                                                                                                                                |
|----------------------|-----------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `chat_histories`     | `Dict[str, List[Dict[str, str]]]` | A dictionary where keys are history identifiers (`history_id`), and values are lists of messages. Each message is represented by a dictionary with keys `role` (sender type) and `content` (message text). |
| `history_msg_count`  | `int`                             | The maximum number of messages that can be stored in the chat history for each identifier.                                                                                                                 |
| `system_prompts`     | `Dict[str, str]`                  | A dictionary where keys are history identifiers (`history_id`), and values are system prompts specific to these identifiers.                                                                               |
| `main_system_prompt` | `Optional[str]`                   | The main system prompt that is used if a specific prompt is not set for a particular `history_id`.                                                                                                         |
| `file_path`          | `str`                             | The path to the JSON file where history data is saved and loaded from.                                                                                                                                     |

---

### 📜 **Methods**

| Method                   | Parameters                     | Returns | Description                                                                                                                                                                                                                                                                |
|--------------------------|--------------------------------|---------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `set_main_system_prompt` | `text: str`                    | -       | Sets the main system prompt that will be used by default. If an error occurs, logs the exception via `logger.error`.                                                                                                                                                       |
| `set_system_prompt`      | `history_id: str`, `text: str` | -       | Sets the system prompt for a specific history identifier. Errors are logged via `logger.error`.                                                                                                                                                                            |
| `get_system_prompt`      | `history_id: str`              | `str`   | Returns the system prompt for the specified identifier or an empty string if the prompt is not set. Errors are logged via `logger.error`.                                                                                                                                  |
| `save_history`           | -                              | -       | Saves the current data (`chat_histories`, `system_prompts`, `main_system_prompt`) to a JSON file. Data is written with indentation and without forcing ASCII. Errors are logged via `logger.error`.                                                                        |
| `load_history`           | -                              | -       | Loads data from the JSON file and sets the values of the attributes `chat_histories`, `system_prompts`, and `main_system_prompt`. If the file is not found, a new one is created (logged via `logger.info`). For other errors, the exception is logged via `logger.error`. |

---

> 💡 **Important to understand:**  
> The `History` class provides a flexible way to manage chat history and system prompts. The main goal is to ensure data saving and recovery through JSON.

> ❗ **Note:**  
> Even if `history_msg_count` is `0`, but a system prompt is specified, it will be attached to the message.

> 🛠️ **Experiment!**  
> You can test the class by changing the initialization parameters or calling methods with different values to better understand how they work!
