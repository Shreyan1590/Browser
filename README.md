# ![Nexus Browser](https://img.shields.io/badge/Nexus-Browser-blue?style=for-the-badge&logo=google-chrome) ![Python](https://img.shields.io/badge/Python-3.13-green?style=for-the-badge&logo=python) ![PyQt5](https://img.shields.io/badge/PyQt5-5.15-purple?style=for-the-badge&logo=qt) ![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)

# Nexus Browser

A futuristic, immersive web browser built with Python and PyQt5 that combines Chrome-like functionality with cutting-edge UI design and advanced features.

## 🌟 Features

### 🎨 Immersive User Interface
- Futuristic Dark Theme with glowing elements and animations  
- Smooth Animations with pulsing address bar and dynamic effects  
- Modern Tab System with Chrome-like tab management  
- Responsive Design that adapts to different screen sizes  

### 🔍 Advanced Browsing Capabilities
- Web Engine Powered by Qt WebEngine (Chromium-based)  
- Multi-Tab Support with tab previews and management  
- Smart Address Bar with URL auto-completion and search integration  
- Navigation Controls with back, forward, reload, and home buttons  

### ⚡ Chrome Shortcuts Integration
Full keyboard shortcut support matching Google Chrome:
- Tab Management: `Ctrl+T`, `Ctrl+W`, `Ctrl+Tab`, `Ctrl+1-9`  
- Navigation: `Alt+Left/Right`, `Ctrl+R`, `F5`  
- Page Operations: `Ctrl+P`, `Ctrl+S`, `F11`  
- Developer Tools: `F12`, `Ctrl+Shift+I`  
- Find in Page: `Ctrl+F`, `F3`  
- And many more...

### 🛡️ Security & Privacy
- Safe Browsing with malicious URL detection  
- Privacy-Focused with local data storage  
- Ad-Blocker Ready architecture  
- HTTPS Enforcement for secure connections  

### 🔧 Developer Features
- Developer Tools integration  
- Page Source Viewer  
- JavaScript Console  
- Network Inspector  

## 🚀 Quick Start

### Prerequisites
- Python 3.8+  
- pip package manager  
- 4GB RAM minimum  
- 500MB disk space  

### Installation

#### Clone the Repository
```bash
git clone https://github.com/Shreyan1590/Browser.git
cd Browser
```

#### Install Dependencies
```bash
pip install -r requirements.txt
```

#### Run the Browser
```bash
python Browser.py
```

#### Building from Source
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -r requirements-dev.txt

# Run with debugging
python -m debugpy --listen 5678 Browser.py
```

## 🏗️ Architecture

```
Browser/
├── src/
│   ├── core/
│   │   ├── browser.py
│   │   ├── tab_manager.py
│   │   └── navigation.py
│   ├── ui/
│   │   ├── main_window.py
│   │   ├── address_bar.py
│   │   └── tab_widget.py
│   ├── features/
│   │   ├── security.py
│   │   ├── shortcuts.py
│   │   └── history.py
│   └── utils/
│       ├── animations.py
│       ├── config.py
│       └── logger.py
├── resources/
│   ├── icons/
│   ├── styles/
│   └── themes/
├── tests/
├── docs/
```

## 🎯 Usage

### Basic Navigation
- Enter URLs in the address bar or search directly  
- Use tabs for multi-page browsing (`Ctrl+T` for new tab)  
- Navigate with back/forward buttons or keyboard shortcuts  
- Bookmark pages with `Ctrl+D`  

### Advanced Features
- Private Browsing: `Ctrl+Shift+N`  
- Developer Tools: `F12` or `Ctrl+Shift+I`  
- Find in Page: `Ctrl+F`  
- Zoom Controls: `Ctrl++`, `Ctrl+-`, `Ctrl+0`  

### Customization
Edit `config/settings.json` to customize:
```json
{
  "general": {
    "home_page": "https://www.google.com",
    "search_engine": "google",
    "default_zoom": 100
  },
  "privacy": {
    "cookies": true,
    "javascript": true,
    "images": true,
    "safe_browsing": true
  },
  "appearance": {
    "theme": "dark",
    "animations": true,
    "font_size": 14
  }
}
```

### Environment Variables
```bash
export NEXUS_DATA_DIR="$HOME/.Browser"
export NEXUS_CACHE_SIZE="1024"
export NEXUS_LOG_LEVEL="INFO"
```

## 🔧 Development

### Code Structure
MVC Architecture:
- **Model:** Data management (history, bookmarks, settings)  
- **View:** PyQt5 UI components  
- **Controller:** Business logic and event handling  

### Adding New Features
- Create feature module in `src/features/`  
- Register shortcuts in `src/core/shortcuts.py`  
- Add UI components in `src/ui/`  
- Update configuration system if needed  

### Testing
```bash
# Run all tests
python -m pytest tests/ -v  

# Run specific test module
python -m pytest tests/test_browser.py -v  

# Code coverage
python -m pytest tests/ --cov=src
```

## 📊 Performance

- **Memory Usage**  
  Base Memory: ~150MB  
  Per Tab: ~50-100MB  
  Cached Pages: Configurable up to 1GB  

- **Loading Times**  
  Cold Start: < 2 seconds  
  Tab Creation: < 200ms  
  Page Load: Dependent on network speed  

## 🌐 Supported Technologies
- HTML5  
- CSS3 (animations and transforms)  
- JavaScript ES2022  
- WebGL  
- WebRTC  
- WebAssembly  

## 🛡️ Security Features

### Protection Layers
- Sandboxed Tabs  
- HTTPS Enforcement  
- Malware Detection  
- Privacy Controls  

### Privacy Options
- Do Not Track header  
- Third-party cookie blocking  
- JavaScript control per site  
- Camera/Microphone access management  

## 📦 Distribution

### Standalone Executable
```bash
pyinstaller --name="Nexus Browser" \
            --icon=resources/icon.ico \
            --windowed \
            --add-data="resources;resources" \
            Browser.py
```

### Package Formats
- Windows: EXE installer with NSIS  
- macOS: DMG package  
- Linux: AppImage and DEB packages  

## 🤝 Contributing

We welcome contributions! See our Contributing Guide.

### Development Setup
```bash
# Fork the repository
git checkout -b feature/amazing-feature
git commit -m 'Add amazing feature'
git push origin feature/amazing-feature
# Open a Pull Request
```

### Code Style
- Black for formatting  
- Flake8 for linting  
- mypy for type checking  
- PEP8 compliance  

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments
- Qt Company for PyQt5  
- Chromium Project for WebEngine  
- Python Community  
- Open Source Contributors  

## 📞 Support
- Documentation: Read the Docs  
- Issues: GitHub Issues  
- Discussions: GitHub Discussions  
- Email: shreyanofficial25@gmail.com  

---

🚀 Nexus Browser - Redefining web browsing with Python power and futuristic design.  
Built by [Shreyan S](https:shreyan-portfolio.vercel.app) with ❤️ and Python
