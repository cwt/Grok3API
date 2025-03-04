# 🛠️ Description of the `GrokClient` Class

## 🚀 The main class for interacting with the Grok API.

The `GrokClient` class is the primary tool for working with Grok. It is responsible for initializing the `ChatCompletion` object, which is used to send requests to the model.

### 📨 **Accepts:**
- 🖥️ `use_xvfb`: A flag to use Xvfb on Linux (default is `True`).  

### 🎯 **Returns:**  
- An instance of the `GrokClient` class, ready for use via `ChatCompletion`.

---

### Full list of parameters for `GrokClient`:

| Parameter         | Type            | Description                                                                                                                 | Default         |
|-------------------|-----------------|-----------------------------------------------------------------------------------------------------------------------------|-----------------|
| `use_xvfb`        | `bool`          | A flag to use Xvfb on Linux.                                                                                                | `True`          |

---

### 📋 **Additional information**

- **Automatic browser initialization**: When the client is initialized, a Chrome session will be started automatically to prepare everything for sending requests.
- **Linux support**: [Detailed description of operation on Linux](LinuxDoc)

> 💡 On Linux without GUI, it is recommended to use Xvfb for stable operation in headless mode.

> 🛠️ To start working with the Grok API, create an instance of `GrokClient` and use its methods, such as `ChatCompletion.create`, to send requests.

---

### 🌟 **Example usage**

```python
from grok3api.client import GrokClient

def main():
    # Create an instance of the client
    client = GrokClient()
    
    # Send a request via ChatCompletion
    response = client.ChatCompletion.create(message="Hello, Grok!")
    print(response.modelResponse.message)  # Prints the response from Grok

if __name__ == '__main__':
    main()
```

---

### 🔗 **Related objects**

- **`ChatCompletion`**: An object created within `GrokClient` that provides the `create` method for sending requests to the Grok model. For details, see **[Description of the `create` method](CreateDoc.md)**.

---

### 📌 **Notes**

- **Error handling**: Exceptions may occur during class initialization (e.g., if cookies could not be obtained). These are logged via `logger.error`.
