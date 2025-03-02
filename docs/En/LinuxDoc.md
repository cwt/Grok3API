## 🐧 **Specifics of Working with Linux**

### 🌟 **Basic Requirements**

For `GrokClient` to work on **Linux**, it is necessary to have **Google Chrome** installed. If you are using a server version of Linux (e.g., **Ubuntu Server**) without a graphical interface, you will need to install **Xvfb** to emulate a virtual display, which will ensure that Chrome operates in headless mode. ✨

---

### 🛠️ **Installing Google Chrome on Linux**

To install **Google Chrome**, open a terminal and execute the following command (example):

```bash
sudo apt update && sudo apt install -y google-chrome-stable
```

> 💡 **Note:** If you encounter issues, ensure that the Chrome repository is correctly connected.

---

### 🎥 **Installing Xvfb for Headless Mode**

On systems without a graphical interface, installing **Xvfb** allows you to create a virtual display. To install, execute:

```bash
sudo apt update && sudo apt install -y xvfb
```

> 🌟 **Note:** Xvfb creates a virtual display with minimal specifications, enabling Chrome to run without the need for a physical display.

---

### ⚙️ **Parameters for Using Xvfb**

When creating an instance of `GrokClient`, the following parameters are available to configure the use of Xvfb:

| Parameter         | Type   | Description                                                                                                  | Default Value |
|-------------------|--------|--------------------------------------------------------------------------------------------------------------|---------------|
| `use_xvfb`        | `bool` | A flag determining the use of Xvfb on Linux.                                                                 | `True`        |
| `auto_close_xvfb` | `bool` | A flag determining the automatic shutdown of Xvfb after use.                                                 | `False`       |

> ❗ **Important:** On Linux, `use_xvfb=True` is used by default. If a graphical interface is present, it is recommended to disable this option.

---

### 🌟 **Example: Disabling Xvfb When a Graphical Interface is Present**

If a graphical interface is available, you can create an instance of the client as follows:

```python
from grok3.client import GrokClient

client = GrokClient(use_xvfb=False)
```

> 💡 In this case, the application will use the real graphical interface.

---

### 📌 **Summary**

- **Google Chrome** is a mandatory component for `GrokClient` to work **only if you need automatic cookie retrieval**.
- **Xvfb** is used to emulate a graphical display on systems without a GUI.
- By default, `use_xvfb=True`; if a graphical interface is present, this option should be disabled.
- The parameter `auto_close_xvfb=False` allows Xvfb to remain running after the client has finished its work.
