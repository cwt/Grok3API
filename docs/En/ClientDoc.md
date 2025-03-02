# 🛠️ Description of the `GrokClient` Class

## 🚀 The main class for interacting with the Grok API.

The `GrokClient` class is the primary tool for working with Grok. It is responsible for automatically obtaining `cookies`, setting up the environment, and initializing the `ChatCompletion` object, which is used to send requests to the model.

### 📨 **Accepts:**  
- 🍪 `cookies`: A string containing cookies for authorization. If not provided, cookies will be automatically obtained via Chrome.  
- 🖥️ `use_xvfb`: A flag to use Xvfb on Linux (default is `True`).  
- 🔄 `auto_close_xvfb`: A flag to automatically close Xvfb after use (default is `False`).  
- 📁 `cookies_file`: The path to the `cookies.txt` file to load cookies from if they are not provided (default is `"cookies.txt"`).  

### 🎯 **Returns:**  
- An instance of the `GrokClient` class, ready for use via `ChatCompletion`.

---

### Full list of parameters for `GrokClient`:

| Parameter         | Type            | Description                                                                                                                 | Default         |
|-------------------|-----------------|-----------------------------------------------------------------------------------------------------------------------------|-----------------|
| `cookies`         | `Optional[str]` | A string containing cookies for authorization. If not provided, cookies will be obtained via Chrome.                        | `None`          |
| `use_xvfb`        | `bool`          | A flag to use Xvfb on Linux.                                                                                                | `True`          |
| `auto_close_xvfb` | `bool`          | A flag to automatically close Xvfb each time after obtaining cookies (even if Xvfb is not present). Only relevant on Linux. | `False`         |
| `cookies_file`    | `Optional[str]` | The path to the `cookies.txt` file from which cookies will be loaded if they are not provided.                              | `"cookies.txt"` |

---

### 📋 **Additional information**

- **Automatic cookie retrieval**: If the `cookies` parameter is not specified, the class will first attempt to load cookies from the `cookies.txt` file (default is `"cookies.txt"`). If cookies are not found there or are invalid, they will be automatically obtained using Chrome.  
- **Linux support**: [Detailed description of operation on Linux](LinuxDoc)

> 💡 If cookies are not provided, they will be automatically obtained using Chrome. On Linux, it is recommended to use Xvfb for stable operation in headless mode.

> 🛠️ To start working with the Grok API, create an instance of `GrokClient` and use its methods, such as `ChatCompletion.create`, to send requests.

---

### 🌟 **Example usage**

```python
from grok3.client import GrokClient

# Create an instance of the client with automatic cookie retrieval
client = GrokClient()

# Or provide cookies manually
# client = GrokClient(cookies="your_cookies_here")

# Send a request via ChatCompletion
response = client.ChatCompletion.create(message="Hello, Grok!")
print(response.modelResponse.message)  # Prints the response from Grok
```

---

### 🔗 **Related objects**

- **`ChatCompletion`**: An object created within `GrokClient` that provides the `create` method for sending requests to the Grok model. For details, see **[Description of the `create` method](CreateDoc.md)**.

---

### 📌 **Notes**

- **Cookies and authorization**: Valid cookies are required for operation. If they are not provided, the class will automatically attempt to obtain them, which may take additional time.
- **Error handling**: Exceptions may occur during class initialization (e.g., if cookies could not be obtained). These are logged via `logger.error`.
