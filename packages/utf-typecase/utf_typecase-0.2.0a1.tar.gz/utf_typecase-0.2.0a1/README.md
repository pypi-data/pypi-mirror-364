![PyPI](https://img.shields.io/pypi/v/utf-typecase)

# utf-typecase

> ⚠️ utf-typecase is in early alpha. Use with care in trusted environments.

## 🌠 Vision: A Practical UTF-Typecase

**utf-typecase** is a utility for developers and typographers who regularly insert specific Unicode characters into text — without relying on clipboard juggling or obscure keyboard shortcuts.

It acts like a virtual typecase:  
- You open a web interface (on a tablet or phone).  
- You set up a grid of your most-used UTF characters.  
- Tap a button — the character appears on your main machine.

No revolutionary input method — just a streamlined way to “type” your go-to symbols when everything’s set up correctly.

🚧 This project is under active development. We’re just getting started — and there’s lots of room to grow.

![Server-Interface-0.2.0](https://raw.githubusercontent.com/lollybyte/utf-typecase/main/images/server-0_2_0.png)

## ✨ Features

- Customizable symbol grid hosted by the server
- Remote character selection via web browser
- Client polls the server and simulates keystrokes to insert characters
- Works across platforms with Python 3.8+ and modern browsers

## 📦 Installation
This installs the **early alpha release** of utf-typecase, which is still in **initial development**. Features may change, the interface may not be stable, and **security has not yet been implemented**. Please use this version only in **private environments**, and **avoid deploying it in production or over public networks**.

```bash
pip install --pre utf-typecase
utf-typecase --install-completion
```
### 🧠 Command-Line Completion

To enable tab-completion for the `utf-typecase` CLI tool, follow the instructions for your operating system:

#### Linux and Mac
```bash
eval "$(_UTF_TYPECASE_COMPLETE=bash_source utf-typecase)"
```

#### Windows
```powershell
python -m click_pwsh install utf-typecase Complete
```
### 🔓 Important: Server Port Access Required

To access utf-typecase from other devices (phone, tablet, remote client), you must open the correct port on the server machine.

> 📖 Full setup instructions are available in the 👉 [Opening Ports Guide](https://github.com/lollybyte/utf-typecase/blob/main/OPENING_PORTS.md)

## Run Application
```
# Run both client and server
utf-typecase --run-server --run-client --qrcode

# Run server only
utf-typecase --run-server --port 5000 --qrcode

# Run client only
utf-typecase --run-client --host http://192.168.1.100:5000 --token dev
```

### 🖥️ Linux Client Setup for PyAutoGUI (X11 Access)

If you're using PyAutoGUI or other GUI automation tools under Linux, you’ll need to grant display access to your user. 

Run:
```bash
xhost +SI:localuser:$(whoami)
```
This temporarily allows your user to interact with the X server (graphical display), which is required for simulating keyboard and mouse actions.

🔧 Make sure xhost is installed — it’s part of the x11-xserver-utils package on Debian/Ubuntu or xorg-xhost on Arch-based systems:

```bash
sudo apt install x11-xserver-utils     # Debian/Ubuntu
sudo pacman -S xorg-xhost              # Arch
nix-shell -p xorg.xhost                # Nix Temporary Environment
```
## 📱 Open Website with Tablet or Smartphone

To access the server from another device, such as a phone or tablet, use the correct IP address of the machine hosting the server.

```txt
http://192.168.1.100:5000
```
🖥️ When you start the server, its address is printed to the terminal 

## 🔢 Alpha Version Summary

| Version   | Highlights                                                                 |
|-----------|------------------------------------------------------------------------------|
| **0.1.0** | Initial placeholder to reserve the `utf-typecase` name on PyPI. No features yet. |
| **0.2.0** | CLI application implemented with a proof-of-concept workflow and minimal usable interface. |

## 📜 License

This project is licensed under the GNU General Public License v3.0 — see [`LICENSE`](https://github.com/lollybyte/utf-typecase/blob/main/LICENSE) for full details.

> 🧠 Reminder: If you modify or distribute utf-typecase, you must also distribute your source code under the same license terms.

## 🤝 Contributing

Want to help improve utf-typecase? Please read the [contribution guidelines](https://github.com/lollybyte/utf-typecase/blob/main/CONTRIBUTING.md) first.
