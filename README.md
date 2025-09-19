# 🌐 Nexus Browser - Complete User Guide  

![Version](https://img.shields.io/badge/Version-1.0.0-blue.svg)  
![Python](https://img.shields.io/badge/Python-3.6%2B-green.svg)  
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)  

---

## 📋 Table of Contents
- [Introduction](#-introduction)  
- [System Requirements](#-system-requirements)  
- [Installation Guide](#-installation-guide)  
- [First Time Setup](#️-first-time-setup)  
- [Features Overview](#-features-overview)  
- [User Interface Guide](#-user-interface-guide)  
- [Keyboard Shortcuts](#-keyboard-shortcuts)  
- [Privacy & Security](#-privacy--security)  
- [Troubleshooting](#-troubleshooting)  
- [Frequently Asked Questions](#-frequently-asked-questions)  
- [Support](#-support)  
- [Development](#-development)  
- [License](#-license)  

---

## 🌟 Introduction
**Nexus Browser** is a modern, open-source web browser built with Python and PyQt5, designed for speed, security, and simplicity.  

It combines the power of Chromium's rendering engine with a lightweight Python backend, offering a seamless browsing experience with advanced features.  

### Key Features
- ⚡ **Lightweight & Fast** – Built on efficient technologies  
- 🛡️ **Privacy Focused** – Built-in ad blocking and tracking protection  
- 🎨 **Customizable** – Multiple themes and extensive settings  
- 🖥️ **Modern UI** – Clean, intuitive interface with smooth animations  
- 🌍 **Cross-Platform** – Works on Windows, macOS, and Linux  

---

## 💻 System Requirements

### Minimum
- **OS:** Windows 7+, macOS 10.12+, or Linux (Ubuntu 16.04+)  
- **Processor:** 1.5 GHz dual-core  
- **Memory:** 2 GB RAM  
- **Storage:** 200 MB  
- **Python:** 3.6+ (for source installation)  

### Recommended
- **OS:** Windows 10+, macOS 11+, Ubuntu 18.04+  
- **Processor:** 2.0 GHz quad-core  
- **Memory:** 4 GB+  
- **Storage:** 500 MB (cache and extensions)  
- **Display:** 1366×768 or higher  

---

## 📥 Installation Guide

### Method 1: Using Pre-built Installer (Recommended)
1. Download from **Releases Page** (`NexusBrowser_Installer_*.zip`)  
2. Extract & run installer:  

```bash
# Extract the ZIP
unzip NexusBrowser_Installer_*.zip  

# Run installer
# Windows
install.bat (Run as Administrator)

# macOS/Linux
chmod +x install.sh
sudo ./install.sh
```

Follow the Installation Wizard:  
- Accept license agreement  
- Choose directory (default: `C:\Program Files\Nexus Browser`)  
- Select shortcuts  
- Finish install  

---

### Method 2: From Source (For Developers)

**Prerequisites:**
- Python 3.6+  
- pip  
- Git  

**Steps:**
```bash
# 1. Clone repository
git clone https://github.com/Shreyan1590/Browser.git
cd NexusBrowser  

# 2. Install dependencies
pip install -r requirements.txt  

# 3. Run the browser
python browser.py
```

**Manual Dependency Install:**
```bash
pip install PyQt5 PyQtWebEngine pillow
# Or specific versions:
pip install PyQt5==5.15.7 PyQtWebEngine==5.15.6 Pillow==9.0.0
```

---

### Method 3: Using Package Managers
```bash
# Windows (Chocolatey)
choco install nexus-browser  

# macOS (Homebrew)
brew install nexus-browser  

# Linux (APT)
sudo add-apt-repository ppa:nexus-browser/stable
sudo apt update
sudo apt install nexus-browser
```

---

## ⚙️ First Time Setup

On first launch:
- 🌐 Choose language  
- 📥 Import from other browsers  
- 🔒 Configure ad blocking & privacy  
- 🔍 Set search engine  
- 🔗 Sign in or create Nexus account  

**Recommended Settings:**
- Search Engine: Google (default)  
- Theme: Dark  
- Ad Blocking: Enabled  
- Safe Browsing: Enabled  

---

## 🚀 Features Overview

### Core
- Tab management (previews, groups)  
- Bookmarks with folders/tags  
- History with search  
- Download manager (pause/resume)  

### Privacy
- Ad blocking  
- Tracker protection  
- HTTPS enforcement  
- Private browsing  

### Productivity
- Password manager  
- Form autofill  
- Chrome extensions supported  
- Developer tools  

### Customization
- Themes: Dark, Light, Blue  
- Customizable UI layout  
- Custom keyboard shortcuts  
- Per-site zoom  

---

## 🎨 User Interface Guide

- **Main Toolbar:** Back/Forward, Address Bar, Refresh/Stop, Home, Bookmarks  
- **Tabs:** `Ctrl+T`, previews, right-click menu, tab groups  
- **Menus:**  
  - File → New window, save, print  
  - Edit → Copy, paste, find  
  - View → Zoom, fullscreen, dev tools  
  - History → Recent, closed  
  - Bookmarks → Manage/import/export  
  - Tools → Extensions, downloads, settings  
  - Help → About, support, updates  

---

## ⌨️ Keyboard Shortcuts

### Navigation
| Shortcut       | Action             |
|----------------|--------------------|
| Ctrl+T         | New Tab            |
| Ctrl+W         | Close Tab          |
| Ctrl+Shift+T   | Reopen Closed Tab  |
| Ctrl+Tab       | Next Tab           |
| Ctrl+Shift+Tab | Previous Tab       |
| Ctrl+1–8       | Switch to Tab 1–8  |
| Ctrl+9         | Switch to Last Tab |
| Alt+Left       | Back               |
| Alt+Right      | Forward            |
| F5             | Reload             |
| Ctrl+F5        | Hard Reload        |

### Address Bar
| Shortcut   | Action                   |
|------------|--------------------------|
| Ctrl+L     | Focus Address Bar        |
| Alt+Enter  | Open in New Tab          |
| Ctrl+Enter | Add `www.` + `.com`      |

### Page Navigation
| Shortcut     | Action          |
|--------------|-----------------|
| Space        | Scroll Down     |
| Shift+Space  | Scroll Up       |
| Home         | Top of Page     |
| End          | Bottom of Page  |
| Ctrl+F       | Find in Page    |

### Developer Tools
| Shortcut       | Action            |
|----------------|-------------------|
| F12            | Developer Tools   |
| Ctrl+Shift+I   | Inspector         |
| Ctrl+Shift+J   | JS Console        |
| Ctrl+U         | View Source       |

---

## 🔒 Privacy & Security

### Privacy
- Do Not Track requests  
- Third-party cookie blocking  
- Fingerprinting protection  
- Clear browsing data  

### Security
- Phishing & malware protection  
- Password monitoring  
- Secure DNS (DoH)  

### Data Management
- Local storage by default  
- Export bookmarks/settings/passwords  
- Selective sync across devices  
- Auto-clean after chosen period  

---

## 🛠️ Troubleshooting

### Browser Won’t Start
```bash
python --version
pip uninstall PyQt5 PyQtWebEngine
pip install PyQt5 PyQtWebEngine
```

### Pages Not Loading
- Check internet connection  
- Disable extensions  
- Clear cache/cookies  

### Performance Issues
- Close unused tabs  
- Disable heavy extensions  
- Clear browsing data  

### Crash Recovery
- Auto session restore  
- Manual: `Settings → History → Recently Closed`  

### Reset Browser
```text
# Windows
%APPDATA%\NexusBrowser\

# macOS
~/Library/Application Support/NexusBrowser/

# Linux
~/.nexusbrowser/
```

---

## ❓ Frequently Asked Questions

- **Q: Is Nexus Browser free?**  
  **A:** Yes, open-source under MIT License.  

- **Q: Can I use Chrome extensions?**  
  **A:** Yes, most are compatible.  

- **Q: How often is it updated?**  
  **A:** Security monthly, features quarterly.  

- **Q: Can I sync between devices?**  
  **A:** Yes, via Nexus Sync.  

- **Q: Is my data collected?**  
  **A:** No, local only (unless sync enabled).  

- **Q: Can I import from other browsers?**  
  **A:** Yes – Chrome, Firefox, Edge, Safari.  

---

## 📞 Support

### Documentation
- User Manual  
- FAQ Page  
- Video Tutorials  

### Community Support
- GitHub Issues  
- Discord  
- Forums  

### Official Support
- 📧 shreyanofficial25@gmail.com  
- 🏢 shreyanofficial25@gmail.com  
- 🔐 shreyanofficial25@gmail.com (for vulnerabilities)  

---

## 🏗️ Development

### Build from Source
```bash
git clone https://github.com/yourusername/NexusBrowser.git
cd NexusBrowser
python -m venv venv
source venv/bin/activate   # Linux/macOS
venv\Scripts\activate      # Windows
pip install -r requirements-dev.txt
```

### Contributing
1. Fork repository  
2. Create branch (`git checkout -b feature/xyz`)  
3. Commit changes  
4. Push (`git push origin feature/xyz`)  
5. Open Pull Request  

### Code Structure
```text
NexusBrowser/
├── browser.py        # Main application
├── components/       # UI components
├── managers/         # Data managers
├── tests/            # Test suite
├── docs/             # Documentation
└── assets/           # Resources/icons
```

---

## 📜 License
- MIT License – see [LICENSE](LICENSE).  
- **Version:** 1.0.0  
- **Last Updated:** September 19, 2025  
- **© 2025 Nexus Browser. All rights reserved.**  
