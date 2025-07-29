# SYSTEM-SELL

**SYSTEM-SELL** is a secure, terminal-based peer-to-peer (P2P) file sharing tool that enables direct file transfers between two computers, with no reliance on any central server or cloud. Built for developers and privacy-conscious users, SYSTEM-SELL delivers encrypted, cross-platform sharing via a simple session code—all from your command line.

## 🌟 Features

- **Peer-to-Peer Transfer:** Direct, no cloud or server intermediaries.
- **End-to-End Encryption:** Files are encrypted in transit with AES-256.
- **NAT Traversal:** Connect behind firewalls using STUN and hole punching.
- **Cross-Platform:** Works on Windows, Linux, and macOS.
- **Session Codes:** Simple session code system for easy connections.
- **No Signups, No Tracking:** Zero accounts, no logs, and full privacy.
- **Terminal Focused:** Operates entirely in the terminal for maximum flexibility.

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/system-sell.git
cd system-sell
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Send a File

```bash
python system_sell.py send path/to/file.zip
```

- The sender will see:
  ```
  [✓] Waiting for receiver...
  [✓] Share this code: S3LLX
  ```

### 4. Receive a File

```bash
python system_sell.py receive S3LLX
```

## 📦 Platform Support

- Windows
- Linux
- macOS

## 💡 Under the Hood

- **Language:** Python (with possible Go alternative).
- **Technologies:** asyncio, sockets, cryptography.
- **NAT Traversal:** Utilizes public STUN servers for hole punching and firewall navigation.
- **Encryption:** End-to-end AES-256 for every transfer.
- **QR Codes:** Optional session code sharing via QR for convenience.

## 👥 User Testing

- Tested with 10+ users on various networks and platforms.
- Reliable for files up to 500MB.

## 📚 Build & Run Instructions

1. Ensure Python 3.10+ is installed.
2. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Use `send` and `receive` commands in your favorite terminal (bash, PowerShell, Zsh, etc.).

## 🔐 Security

- **AES-256 Encryption:** Ensures files remain confidential.
- **No Persistent Sessions:** Session keys are ephemeral and deleted after use.
- **No Logging:** No activity or file logs are kept.
- **Temporary Connections:** Each transfer requires a new session code.

## 🧠 Project Details

- **Time Spent:** 20+ hours logged via HackaTime.
- **License:** MIT—free to use and contribute to.
- **Contributing:** Pull requests and suggestions are very welcome!

## 🤝 Contributing

We welcome all contributions and feedback. Fork the repository, open an issue, or submit a pull request to help improve SYSTEM-SELL.

## 📄 License

This project is licensed under the MIT License.

For demo requests, logo design, or ideas on repo structure, feel free to open an issue or reach out!