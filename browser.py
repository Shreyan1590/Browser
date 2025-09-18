import sys
import sqlite3
import os
import json
import zipfile
import tempfile
import shutil
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLineEdit, QPushButton, QFrame, QLabel, QToolBar, QTabWidget,
                             QMenu, QAction, QDialog, QListWidget, QListWidgetItem, QMessageBox,
                             QInputDialog, QCheckBox, QSlider, QStyle, QToolButton, QSplitter,
                             QShortcut, QTextEdit, QProgressBar, QStatusBar, QFileDialog,
                             QDialogButtonBox, QGroupBox, QComboBox, QSpinBox, QDoubleSpinBox,
                             QFormLayout, QScrollArea, QSizePolicy, QStackedWidget, QTreeWidget,
                             QTreeWidgetItem, QHeaderView, QDockWidget, QToolBar, QSystemTrayIcon,
                             QSplashScreen, QGraphicsDropShadowEffect, QButtonGroup, QRadioButton,
                             QGridLayout, QSpacerItem, QTabBar, QStylePainter, QStyleOptionTab)
from PyQt5.QtCore import (Qt, QTimer, QUrl, QSize, QSettings, QPoint, QRect, QPropertyAnimation, 
                          QEasingCurve, QThread, pyqtSignal, QDateTime, QTime, QDate, QEvent, QSizeF)
from PyQt5.QtGui import (QFont, QColor, QIcon, QPalette, QKeySequence, QPainter, QPen, QBrush,
                         QLinearGradient, QRadialGradient, QConicalGradient, QPixmap, QMovie,
                         QDesktopServices, QFontDatabase, QClipboard, QGuiApplication)
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineProfile, QWebEnginePage, QWebEngineSettings
from PyQt5.QtWebEngineCore import QWebEngineUrlRequestInterceptor, QWebEngineHttpRequest
from PyQt5.QtPrintSupport import QPrintDialog, QPrinter

# ==============================
# ENHANCED COMPONENTS
# ==============================

class FancyTabBar(QTabBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMovable(True)
        self.setExpanding(False)
        self.setDrawBase(False)
        self.setElideMode(Qt.ElideRight)
        self.setUsesScrollButtons(True)
        
        # Animation for tab changes
        self.animation = QPropertyAnimation(self, b"currentColor")
        self.animation.setDuration(300)
        self.animation.setEasingCurve(QEasingCurve.OutCubic)
        self.currentColor = QColor(0, 170, 255)
        
    def paintEvent(self, event):
        painter = QStylePainter(self)
        option = QStyleOptionTab()
        
        for index in range(self.count()):
            self.initStyleOption(option, index)
            
            # Custom painting for selected tab
            if index == self.currentIndex():
                # Draw gradient background for selected tab
                gradient = QLinearGradient(option.rect.topLeft(), option.rect.bottomLeft())
                gradient.setColorAt(0, QColor(0, 150, 255))
                gradient.setColorAt(1, QColor(0, 100, 200))
                painter.fillRect(option.rect, gradient)
                
                # Draw highlight border
                painter.setPen(QPen(QColor(0, 200, 255), 2))
                painter.drawRect(option.rect.adjusted(1, 1, -1, 0))
                
                # Draw text with shadow
                painter.setPen(QColor(255, 255, 255))
                text_rect = option.rect.adjusted(5, 0, -20, 0)
                painter.drawText(text_rect, Qt.AlignLeft | Qt.AlignVCenter, option.text)
            else:
                # Draw normal tab
                painter.setPen(QColor(200, 200, 200))
                painter.drawText(option.rect.adjusted(5, 0, -20, 0), Qt.AlignLeft | Qt.AlignVCenter, option.text)
                
        painter.end()

class AnimatedButton(QPushButton):
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self._animation = QPropertyAnimation(self, b"geometry")
        self._animation.setDuration(200)
        self._animation.setEasingCurve(QEasingCurve.OutCubic)
        
        self.setMouseTracking(True)
        
    def enterEvent(self, event):
        self._animation.stop()
        self._animation.setStartValue(self.geometry())
        self._animation.setEndValue(QRect(self.x()-2, self.y()-2, self.width()+4, self.height()+4))
        self._animation.start()
        super().enterEvent(event)
        
    def leaveEvent(self, event):
        self._animation.stop()
        self._animation.setStartValue(self.geometry())
        self._animation.setEndValue(QRect(self.x()+2, self.y()+2, self.width()-4, self.height()-4))
        self._animation.start()
        super().leaveEvent(event)

class DownloadManager(QDialog):
    downloadProgress = pyqtSignal(int, int, str)
    downloadFinished = pyqtSignal(str, str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Downloads")
        self.setGeometry(400, 400, 800, 500)
        self.downloads = []
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Downloads list
        self.downloads_list = QTreeWidget()
        self.downloads_list.setHeaderLabels(["File", "Progress", "Size", "Time", "Status"])
        self.downloads_list.header().setSectionResizeMode(0, QHeaderView.Stretch)
        self.downloads_list.setAlternatingRowColors(True)
        layout.addWidget(self.downloads_list)
        
        # Buttons
        button_layout = QHBoxLayout()
        open_btn = QPushButton("Open")
        open_folder_btn = QPushButton("Open Folder")
        clear_btn = QPushButton("Clear Completed")
        close_btn = QPushButton("Close")
        
        open_btn.clicked.connect(self.open_file)
        open_folder_btn.clicked.connect(self.open_download_folder)
        clear_btn.clicked.connect(self.clear_completed)
        close_btn.clicked.connect(self.accept)
        
        button_layout.addWidget(open_btn)
        button_layout.addWidget(open_folder_btn)
        button_layout.addWidget(clear_btn)
        button_layout.addWidget(close_btn)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
    def add_download(self, path, url, started_at=None):
        if started_at is None:
            started_at = datetime.now()
            
        item = QTreeWidgetItem(self.downloads_list)
        item.setText(0, os.path.basename(path))
        item.setText(1, "0%")
        item.setText(2, "Unknown")
        item.setText(3, started_at.strftime("%H:%M:%S"))
        item.setText(4, "Downloading")
        
        # Store download info
        item.setData(0, Qt.UserRole, {
            "path": path,
            "url": url,
            "started_at": started_at,
            "received": 0,
            "total": 0,
            "finished": False
        })
        
        self.downloads.append(item)
        return item
        
    def update_download(self, item, received, total):
        data = item.data(0, Qt.UserRole)
        data["received"] = received
        data["total"] = total
        
        if total > 0:
            percent = int(received * 100 / total)
            item.setText(1, f"{percent}%")
            
            # Format size
            size_str = self.format_size(total)
            item.setText(2, size_str)
            
            # Update progress bar if we have one
            if hasattr(item, "progress_bar"):
                item.progress_bar.setValue(percent)
                
    def finish_download(self, item, success=True):
        data = item.data(0, Qt.UserRole)
        data["finished"] = True
        
        if success:
            item.setText(4, "Completed")
            # Change row color to indicate completion
            for i in range(5):
                item.setBackground(i, QBrush(QColor(220, 255, 220)))
        else:
            item.setText(4, "Failed")
            for i in range(5):
                item.setBackground(i, QBrush(QColor(255, 220, 220)))
                
    def open_file(self):
        current_item = self.downloads_list.currentItem()
        if current_item:
            data = current_item.data(0, Qt.UserRole)
            if data["finished"]:
                QDesktopServices.openUrl(QUrl.fromLocalFile(data["path"]))
                
    def open_download_folder(self):
        # Open the default download folder
        path = QStandardPaths.writableLocation(QStandardPaths.DownloadLocation)
        QDesktopServices.openUrl(QUrl.fromLocalFile(path))
        
    def clear_completed(self):
        root = self.downloads_list.invisibleRootItem()
        for i in range(root.childCount() - 1, -1, -1):
            item = root.child(i)
            data = item.data(0, Qt.UserRole)
            if data["finished"]:
                root.removeChild(item)
                self.downloads.remove(item)
                
    def format_size(self, size):
        # Convert bytes to human readable format
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.2f} {unit}"
            size /= 1024.0
        return f"{size:.2f} TB"

class PasswordDialog(QDialog):
    def __init__(self, url, username, password, remember, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Password Required")
        self.setGeometry(400, 400, 500, 300)
        self.url = url
        self.username = username
        self.password = password
        self.remember = remember
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Message
        message = QLabel(f"The site {self.url} requires a username and password.")
        message.setWordWrap(True)
        layout.addWidget(message)
        
        # Form
        form_layout = QFormLayout()
        
        self.username_edit = QLineEdit(self.username if self.username else "")
        self.password_edit = QLineEdit(self.password if self.password else "")
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.remember_check = QCheckBox("Remember password")
        self.remember_check.setChecked(self.remember)
        
        form_layout.addRow("Username:", self.username_edit)
        form_layout.addRow("Password:", self.password_edit)
        form_layout.addRow("", self.remember_check)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        ok_btn = QPushButton("OK")
        cancel_btn = QPushButton("Cancel")
        
        ok_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(ok_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
    def get_credentials(self):
        return {
            "username": self.username_edit.text(),
            "password": self.password_edit.text(),
            "remember": self.remember_check.isChecked()
        }

class ExtensionsManager(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Extensions")
        self.setGeometry(400, 400, 800, 500)
        self.extensions = []
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Toolbar
        toolbar = QToolBar()
        install_btn = QAction("Install Extension", self)
        install_btn.triggered.connect(self.install_extension)
        toolbar.addAction(install_btn)
        
        remove_btn = QAction("Remove Selected", self)
        remove_btn.triggered.connect(self.remove_extension)
        toolbar.addAction(remove_btn)
        
        layout.addWidget(toolbar)
        
        # Extensions list
        self.extensions_list = QTreeWidget()
        self.extensions_list.setHeaderLabels(["Name", "Version", "Description", "Status"])
        self.extensions_list.header().setSectionResizeMode(0, QHeaderView.Stretch)
        self.extensions_list.setAlternatingRowColors(True)
        layout.addWidget(self.extensions_list)
        
        # Buttons
        button_layout = QHBoxLayout()
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        self.load_extensions()
        
    def load_extensions(self):
        # Load installed extensions
        settings = QSettings('NexusBrowser', 'Extensions')
        extensions = settings.value('extensions', [])
        
        for ext in extensions:
            item = QTreeWidgetItem(self.extensions_list)
            item.setText(0, ext.get('name', 'Unknown'))
            item.setText(1, ext.get('version', '1.0'))
            item.setText(2, ext.get('description', ''))
            item.setText(3, "Enabled" if ext.get('enabled', True) else "Disabled")
            item.setData(0, Qt.UserRole, ext)
            
    def install_extension(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Extension File", "", "Extension Files (*.crx *.zip);;All Files (*)"
        )
        
        if file_path:
            # Extract extension info
            try:
                with zipfile.ZipFile(file_path, 'r') as zip_ref:
                    # Check for manifest.json
                    if 'manifest.json' in zip_ref.namelist():
                        manifest_data = zip_ref.read('manifest.json')
                        manifest = json.loads(manifest_data.decode('utf-8'))
                        
                        # Create extension directory
                        ext_dir = os.path.join(
                            QStandardPaths.writableLocation(QStandardPaths.AppDataLocation),
                            'extensions',
                            manifest.get('name', 'unknown').replace(' ', '_')
                        )
                        
                        if not os.path.exists(ext_dir):
                            os.makedirs(ext_dir)
                            
                        # Extract files
                        zip_ref.extractall(ext_dir)
                        
                        # Add to list
                        settings = QSettings('NexusBrowser', 'Extensions')
                        extensions = settings.value('extensions', [])
                        
                        extension = {
                            'name': manifest.get('name', 'Unknown'),
                            'version': manifest.get('version', '1.0'),
                            'description': manifest.get('description', ''),
                            'path': ext_dir,
                            'enabled': True
                        }
                        
                        extensions.append(extension)
                        settings.setValue('extensions', extensions)
                        
                        # Add to UI
                        item = QTreeWidgetItem(self.extensions_list)
                        item.setText(0, extension['name'])
                        item.setText(1, extension['version'])
                        item.setText(2, extension['description'])
                        item.setText(3, "Enabled")
                        item.setData(0, Qt.UserRole, extension)
                        
                        QMessageBox.information(self, "Success", "Extension installed successfully!")
                    else:
                        QMessageBox.warning(self, "Error", "No manifest.json found in extension file!")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to install extension: {str(e)}")
                
    def remove_extension(self):
        current_item = self.extensions_list.currentItem()
        if current_item:
            extension = current_item.data(0, Qt.UserRole)
            
            reply = QMessageBox.question(
                self, "Confirm Removal",
                f"Are you sure you want to remove {extension['name']}?",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                # Remove from filesystem
                try:
                    if os.path.exists(extension['path']):
                        shutil.rmtree(extension['path'])
                except Exception as e:
                    QMessageBox.warning(self, "Warning", f"Could not remove extension files: {str(e)}")
                
                # Remove from settings
                settings = QSettings('NexusBrowser', 'Extensions')
                extensions = settings.value('extensions', [])
                extensions = [ext for ext in extensions if ext['path'] != extension['path']]
                settings.setValue('extensions', extensions)
                
                # Remove from UI
                self.extensions_list.takeTopLevelItem(self.extensions_list.indexOfTopLevelItem(current_item))
                
                QMessageBox.information(self, "Success", "Extension removed successfully!")

class ThemeManager:
    def __init__(self):
        self.settings = QSettings('NexusBrowser', 'Themes')
        self.current_theme = self.settings.value('current_theme', 'dark')
        
    def get_theme(self, name=None):
        if name is None:
            name = self.current_theme
            
        themes = {
            'dark': {
                'window_bg': '#0a0a0a',
                'toolbar_bg': '#1a1a1a',
                'tab_bg': '#1a1a1a',
                'tab_selected_bg': '#2d2d2d',
                'tab_selected_border': '#00fffc',
                'text_color': '#ffffff',
                'text_secondary': '#cccccc',
                'accent_color': '#00aaff',
                'accent_light': '#00fffc',
                'button_bg': 'qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1, stop:0 #0088ff, stop:1 #0044aa)',
                'button_hover_bg': 'qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1, stop:0 #00aaff, stop:1 #0066cc)',
                'button_pressed_bg': 'qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1, stop:0 #0044aa, stop:1 #0088ff)',
                'address_bar_bg': '#2d2d2d',
                'address_bar_border': '#00aaff',
                'address_bar_focus_border': '#00fffc',
                'menu_bg': '#1a1a1a',
                'menu_border': '#00aaff',
                'menu_item_selected_bg': '#0088ff'
            },
            'light': {
                'window_bg': '#f0f0f0',
                'toolbar_bg': '#ffffff',
                'tab_bg': '#e0e0e0',
                'tab_selected_bg': '#ffffff',
                'tab_selected_border': '#007acc',
                'text_color': '#000000',
                'text_secondary': '#555555',
                'accent_color': '#007acc',
                'accent_light': '#0099ff',
                'button_bg': 'qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1, stop:0 #f5f5f5, stop:1 #e0e0e0)',
                'button_hover_bg': 'qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1, stop:0 #ffffff, stop:1 #f0f0f0)',
                'button_pressed_bg': 'qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1, stop:0 #e0e0e0, stop:1 #f5f5f5)',
                'address_bar_bg': '#ffffff',
                'address_bar_border': '#cccccc',
                'address_bar_focus_border': '#007acc',
                'menu_bg': '#ffffff',
                'menu_border': '#cccccc',
                'menu_item_selected_bg': '#e0e0e0'
            },
            'blue': {
                'window_bg': '#0a1a2a',
                'toolbar_bg': '#1a2a3a',
                'tab_bg': '#1a2a3a',
                'tab_selected_bg': '#2a3a4a',
                'tab_selected_border': '#00ccff',
                'text_color': '#ffffff',
                'text_secondary': '#aaccff',
                'accent_color': '#00ccff',
                'accent_light': '#00ffff',
                'button_bg': 'qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1, stop:0 #0088ff, stop:1 #0044aa)',
                'button_hover_bg': 'qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1, stop:0 #00aaff, stop:1 #0066cc)',
                'button_pressed_bg': 'qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1, stop:0 #0044aa, stop:1 #0088ff)',
                'address_bar_bg': '#2a3a4a',
                'address_bar_border': '#00aaff',
                'address_bar_focus_border': '#00ffff',
                'menu_bg': '#1a2a3a',
                'menu_border': '#00aaff',
                'menu_item_selected_bg': '#0088ff'
            }
        }
        
        return themes.get(name, themes['dark'])
        
    def set_theme(self, name):
        if name in ['dark', 'light', 'blue']:
            self.current_theme = name
            self.settings.setValue('current_theme', name)
            return True
        return False
        
    def get_available_themes(self):
        return ['dark', 'light', 'blue']

class AdvancedWebView(QWebEngineView):
    # Custom signals
    faviconChanged = pyqtSignal(QIcon)
    loadingProgress = pyqtSignal(int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._favicon = QIcon()
        self.loadProgress.connect(self.on_load_progress)
        self.iconChanged.connect(self.on_icon_changed)
        
        # Enable developer tools
        self.settings().setAttribute(QWebEngineSettings.JavascriptEnabled, True)
        self.settings().setAttribute(QWebEngineSettings.PluginsEnabled, True)
        self.settings().setAttribute(QWebEngineSettings.FullScreenSupportEnabled, True)
        self.settings().setAttribute(QWebEngineSettings.ScrollAnimatorEnabled, True)
        self.settings().setAttribute(QWebEngineSettings.AutoLoadImages, True)
        self.settings().setAttribute(QWebEngineSettings.JavascriptCanOpenWindows, True)
        self.settings().setAttribute(QWebEngineSettings.JavascriptCanAccessClipboard, True)
        self.settings().setAttribute(QWebEngineSettings.LocalStorageEnabled, True)
        self.settings().setAttribute(QWebEngineSettings.LocalContentCanAccessRemoteUrls, True)
        self.settings().setAttribute(QWebEngineSettings.XSSAuditingEnabled, True)
        self.settings().setAttribute(QWebEngineSettings.SpatialNavigationEnabled, True)
        self.settings().setAttribute(QWebEngineSettings.HyperlinkAuditingEnabled, True)
        
    def on_load_progress(self, progress):
        self.loadingProgress.emit(progress)
        
    def on_icon_changed(self, icon):
        self._favicon = icon
        self.faviconChanged.emit(icon)
        
    def favicon(self):
        return self._favicon
        
    def createWindow(self, type):
        # Handle requests to open new windows
        new_browser = AdvancedWebView()
        new_browser.page().setUrl(self.page().requestedUrl())
        return new_browser

class EnhancedURLInterceptor(QWebEngineUrlRequestInterceptor):
    def __init__(self, adblock_enabled=True, safe_browsing_enabled=True):
        super().__init__()
        self.adblock_enabled = adblock_enabled
        self.safe_browsing_enabled = safe_browsing_enabled
        
        # Load adblock rules
        self.adblock_rules = self.load_adblock_rules()
        self.malicious_domains = {"malicious-site.com", "phishing-attempt.net", "dangerous-domain.org"}
        
    def load_adblock_rules(self):
        # Load adblock rules from file
        rules = set()
        try:
            rules_file = os.path.join(
                QStandardPaths.writableLocation(QStandardPaths.AppDataLocation),
                'adblock_rules.txt'
            )
            
            if os.path.exists(rules_file):
                with open(rules_file, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('!'):
                            rules.add(line)
        except:
            pass
            
        return rules
        
    def interceptRequest(self, info):
        url = info.requestUrl().toString()
        domain = info.requestUrl().host()
        
        # Safe browsing check
        if self.safe_browsing_enabled:
            if any(malicious in domain for malicious in self.malicious_domains):
                info.block(True)
                print(f"Blocked malicious domain: {domain}")
                return
                
        # Adblock check
        if self.adblock_enabled:
            for rule in self.adblock_rules:
                if rule in url:
                    info.block(True)
                    print(f"Blocked ad/tracker: {url}")
                    return

class EnhancedHistoryManager:
    def __init__(self):
        self.conn = sqlite3.connect('browser_history.db')
        self.create_tables()
        
    def create_tables(self):
        cursor = self.conn.cursor()
        
        # Check if the old table exists and migrate it
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='history'")
        old_table_exists = cursor.fetchone()
        
        if old_table_exists:
            # Check if the old table has the old schema
            cursor.execute("PRAGMA table_info(history)")
            columns = [column[1] for column in cursor.fetchall()]
            
            if 'visit_count' not in columns:
                # This is the old schema, we need to migrate
                print("Migrating history database to new schema...")
                
                # Create a temporary table with the new schema
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS history_new (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        url TEXT NOT NULL,
                        title TEXT NOT NULL,
                        visit_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        visit_count INTEGER DEFAULT 1
                    )
                ''')
                
                # Copy data from old table to new table
                cursor.execute('''
                    INSERT INTO history_new (url, title, visit_time, visit_count)
                    SELECT url, title, visit_time, 1 FROM history
                ''')
                
                # Drop the old table
                cursor.execute('DROP TABLE history')
                
                # Rename the new table
                cursor.execute('ALTER TABLE history_new RENAME TO history')
                
                # Create frequent_sites table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS frequent_sites (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        url TEXT NOT NULL UNIQUE,
                        title TEXT NOT NULL,
                        visit_count INTEGER DEFAULT 1,
                        last_visit TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Populate frequent_sites from history
                cursor.execute('''
                    INSERT INTO frequent_sites (url, title, visit_count, last_visit)
                    SELECT url, title, COUNT(*) as visit_count, MAX(visit_time) as last_visit
                    FROM history
                    GROUP BY url, title
                ''')
                
                self.conn.commit()
                print("Database migration completed successfully.")
        
        # Create tables if they don't exist (for new installations)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT NOT NULL,
                title TEXT NOT NULL,
                visit_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                visit_count INTEGER DEFAULT 1
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS frequent_sites (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT NOT NULL UNIQUE,
                title TEXT NOT NULL,
                visit_count INTEGER DEFAULT 1,
                last_visit TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        self.conn.commit()
        
    def add_to_history(self, url, title):
        cursor = self.conn.cursor()
        
        # Check if URL already exists in history
        cursor.execute('SELECT id, visit_count FROM history WHERE url = ? ORDER BY visit_time DESC LIMIT 1', (url,))
        result = cursor.fetchone()
        
        if result:
            # Update existing entry
            history_id, visit_count = result
            cursor.execute(
                'UPDATE history SET visit_time = CURRENT_TIMESTAMP, visit_count = ? WHERE id = ?',
                (visit_count + 1, history_id)
            )
        else:
            # Insert new entry
            cursor.execute('INSERT INTO history (url, title) VALUES (?, ?)', (url, title))
            
        # Update frequent sites
        cursor.execute('SELECT id, visit_count FROM frequent_sites WHERE url = ?', (url,))
        result = cursor.fetchone()
        
        if result:
            freq_id, visit_count = result
            cursor.execute(
                'UPDATE frequent_sites SET visit_count = ?, last_visit = CURRENT_TIMESTAMP WHERE id = ?',
                (visit_count + 1, freq_id)
            )
        else:
            cursor.execute('INSERT INTO frequent_sites (url, title, visit_count) VALUES (?, ?, 1)', (url, title))
            
        self.conn.commit()
        
    def get_history(self, limit=100):
        cursor = self.conn.cursor()
        cursor.execute('SELECT url, title, visit_time, visit_count FROM history ORDER BY visit_time DESC LIMIT ?', (limit,))
        return cursor.fetchall()
        
    def get_frequent_sites(self, limit=10):
        cursor = self.conn.cursor()
        cursor.execute('SELECT url, title, visit_count FROM frequent_sites ORDER BY visit_count DESC LIMIT ?', (limit,))
        return cursor.fetchall()
        
    def search_history(self, query, limit=20):
        cursor = self.conn.cursor()
        cursor.execute(
            'SELECT url, title, visit_time FROM history WHERE url LIKE ? OR title LIKE ? ORDER BY visit_time DESC LIMIT ?',
            (f'%{query}%', f'%{query}%', limit)
        )
        return cursor.fetchall()
        
    def clear_history(self, timeframe=None):
        cursor = self.conn.cursor()
        
        if timeframe:
            # Clear history for a specific timeframe
            if timeframe == 'last_hour':
                cursor.execute('DELETE FROM history WHERE visit_time > datetime("now", "-1 hour")')
            elif timeframe == 'last_day':
                cursor.execute('DELETE FROM history WHERE visit_time > datetime("now", "-1 day")')
            elif timeframe == 'last_week':
                cursor.execute('DELETE FROM history WHERE visit_time > datetime("now", "-7 days")')
            elif timeframe == 'last_month':
                cursor.execute('DELETE FROM history WHERE visit_time > datetime("now", "-30 days")')
        else:
            # Clear all history
            cursor.execute('DELETE FROM history')
            
        self.conn.commit()
        
    def delete_history_item(self, url):
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM history WHERE url = ?', (url,))
        self.conn.commit()

class EnhancedPasswordManager:
    def __init__(self):
        self.settings = QSettings('NexusBrowser', 'Passwords')
        
    def save_password(self, url, username, password):
        key = f"{url}_{username}"
        encrypted_password = self.encrypt_password(password)
        self.settings.setValue(key, encrypted_password)
        
    def get_password(self, url, username):
        key = f"{url}_{username}"
        encrypted_password = self.settings.value(key, "")
        if encrypted_password:
            return self.decrypt_password(encrypted_password)
        return ""
        
    def get_saved_logins(self, url=None):
        logins = []
        all_keys = self.settings.allKeys()
        
        for key in all_keys:
            if key.endswith('_username') or key.endswith('_password'):
                continue
                
            if '_' in key:
                parts = key.split('_')
                if len(parts) >= 2:
                    site_url = '_'.join(parts[:-1])
                    username = parts[-1]
                    
                    if url is None or url in site_url:
                        password = self.get_password(site_url, username)
                        logins.append({
                            'url': site_url,
                            'username': username,
                            'password': password
                        })
                        
        return logins
        
    def delete_password(self, url, username):
        key = f"{url}_{username}"
        self.settings.remove(key)
        
    def encrypt_password(self, password):
        # Simple encryption (in a real application, use proper encryption)
        return ''.join(chr(ord(c) + 3) for c in password)
        
    def decrypt_password(self, encrypted):
        # Simple decryption
        return ''.join(chr(ord(c) - 3) for c in encrypted)

class EnhancedBookmarksManager:
    def __init__(self):
        self.settings = QSettings('NexusBrowser', 'Bookmarks')
        
    def add_bookmark(self, url, title, folder="", tags=""):
        bookmarks = self.get_bookmarks()
        
        # Check if bookmark already exists
        for bookmark in bookmarks:
            if bookmark['url'] == url:
                # Update existing bookmark
                bookmark['title'] = title
                bookmark['folder'] = folder
                bookmark['tags'] = tags
                bookmark['time'] = datetime.now().isoformat()
                break
        else:
            # Add new bookmark
            bookmarks.append({
                'url': url,
                'title': title,
                'folder': folder,
                'tags': tags,
                'time': datetime.now().isoformat()
            })
            
        self.settings.setValue('bookmarks', bookmarks)
        
    def get_bookmarks(self, folder=None, tag=None):
        bookmarks = self.settings.value('bookmarks', [])
        
        if folder:
            bookmarks = [b for b in bookmarks if b.get('folder', '') == folder]
            
        if tag:
            bookmarks = [b for b in bookmarks if tag in b.get('tags', '').split(',')]
            
        return bookmarks
        
    def get_folders(self):
        bookmarks = self.get_bookmarks()
        folders = set()
        
        for bookmark in bookmarks:
            folder = bookmark.get('folder', '')
            if folder:
                folders.add(folder)
                
        return sorted(list(folders))
        
    def get_tags(self):
        bookmarks = self.get_bookmarks()
        tags = set()
        
        for bookmark in bookmarks:
            for tag in bookmark.get('tags', '').split(','):
                if tag.strip():
                    tags.add(tag.strip())
                    
        return sorted(list(tags))
        
    def remove_bookmark(self, url):
        bookmarks = self.get_bookmarks()
        bookmarks = [b for b in bookmarks if b['url'] != url]
        self.settings.setValue('bookmarks', bookmarks)
        
    def export_bookmarks(self, file_path):
        bookmarks = self.get_bookmarks()
        with open(file_path, 'w') as f:
            json.dump(bookmarks, f, indent=2)
            
    def import_bookmarks(self, file_path):
        try:
            with open(file_path, 'r') as f:
                bookmarks = json.load(f)
                
            current_bookmarks = self.get_bookmarks()
            current_urls = {b['url'] for b in current_bookmarks}
            
            # Merge bookmarks, avoiding duplicates
            for bookmark in bookmarks:
                if bookmark['url'] not in current_urls:
                    current_bookmarks.append(bookmark)
                    
            self.settings.setValue('bookmarks', current_bookmarks)
            return True
        except:
            return False

class EnhancedSettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Browser Settings")
        self.setGeometry(200, 200, 800, 600)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Tab widget for different settings categories
        self.tab_widget = QTabWidget()
        
        # General tab
        general_tab = QWidget()
        general_layout = QVBoxLayout()
        
        # Search engine
        search_group = QGroupBox("Search Engine")
        search_layout = QVBoxLayout()
        
        self.search_engine = QComboBox()
        self.search_engine.addItems(["Google", "Bing", "DuckDuckGo", "Yahoo", "Custom"])
        search_layout.addWidget(QLabel("Default Search Engine:"))
        search_layout.addWidget(self.search_engine)
        
        self.custom_search = QLineEdit()
        self.custom_search.setPlaceholderText("https://www.example.com/search?q=%s")
        search_layout.addWidget(QLabel("Custom Search URL:"))
        search_layout.addWidget(self.custom_search)
        
        search_group.setLayout(search_layout)
        general_layout.addWidget(search_group)
        
        # Home page
        home_group = QGroupBox("Home Page")
        home_layout = QVBoxLayout()
        
        self.home_page = QLineEdit()
        self.home_page.setPlaceholderText("https://www.google.com")
        home_layout.addWidget(QLabel("Home Page URL:"))
        home_layout.addWidget(self.home_page)
        
        home_group.setLayout(home_layout)
        general_layout.addWidget(home_group)
        
        # Theme
        theme_group = QGroupBox("Appearance")
        theme_layout = QVBoxLayout()
        
        self.theme = QComboBox()
        self.theme.addItems(["Dark", "Light", "Blue"])
        theme_layout.addWidget(QLabel("Theme:"))
        theme_layout.addWidget(self.theme)
        
        theme_group.setLayout(theme_layout)
        general_layout.addWidget(theme_group)
        
        general_tab.setLayout(general_layout)
        self.tab_widget.addTab(general_tab, "General")
        
        # Privacy tab
        privacy_tab = QWidget()
        privacy_layout = QVBoxLayout()
        
        # Tracking protection
        tracking_group = QGroupBox("Tracking Protection")
        tracking_layout = QVBoxLayout()
        
        self.ad_block = QCheckBox("Block ads and trackers")
        self.ad_block.setChecked(True)
        tracking_layout.addWidget(self.ad_block)
        
        self.safe_browsing = QCheckBox("Safe browsing protection")
        self.safe_browsing.setChecked(True)
        tracking_layout.addWidget(self.safe_browsing)
        
        self.do_not_track = QCheckBox("Send Do Not Track requests")
        tracking_layout.addWidget(self.do_not_track)
        
        tracking_group.setLayout(tracking_layout)
        privacy_layout.addWidget(tracking_group)
        
        # Cookies
        cookies_group = QGroupBox("Cookies")
        cookies_layout = QVBoxLayout()
        
        self.cookie_policy = QComboBox()
        self.cookie_policy.addItems(["Allow all cookies", "Block third-party cookies", "Block all cookies"])
        cookies_layout.addWidget(QLabel("Cookie Policy:"))
        cookies_layout.addWidget(self.cookie_policy)
        
        cookies_group.setLayout(cookies_layout)
        privacy_layout.addWidget(cookies_group)
        
        privacy_tab.setLayout(privacy_layout)
        self.tab_widget.addTab(privacy_tab, "Privacy")
        
        # Advanced tab
        advanced_tab = QWidget()
        advanced_layout = QVBoxLayout()
        
        # JavaScript
        js_group = QGroupBox("JavaScript")
        js_layout = QVBoxLayout()
        
        self.enable_js = QCheckBox("Enable JavaScript")
        self.enable_js.setChecked(True)
        js_layout.addWidget(self.enable_js)
        
        js_group.setLayout(js_layout)
        advanced_layout.addWidget(js_group)
        
        # Hardware acceleration
        hw_group = QGroupBox("Performance")
        hw_layout = QVBoxLayout()
        
        self.hw_acceleration = QCheckBox("Enable hardware acceleration")
        self.hw_acceleration.setChecked(True)
        hw_layout.addWidget(self.hw_acceleration)
        
        hw_group.setLayout(hw_layout)
        advanced_layout.addWidget(hw_group)
        
        advanced_tab.setLayout(advanced_layout)
        self.tab_widget.addTab(advanced_tab, "Advanced")
        
        layout.addWidget(self.tab_widget)
        
        # Buttons
        button_layout = QHBoxLayout()
        save_btn = QPushButton("Save")
        cancel_btn = QPushButton("Cancel")
        
        save_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        self.load_settings()
        
    def load_settings(self):
        settings = QSettings('NexusBrowser', 'Settings')
        
        # General
        search_engine = settings.value('search_engine', 'Google')
        self.search_engine.setCurrentText(search_engine)
        self.custom_search.setText(settings.value('custom_search', ''))
        self.home_page.setText(settings.value('home_page', 'https://www.google.com'))
        self.theme.setCurrentText(settings.value('theme', 'Dark'))
        
        # Privacy
        self.ad_block.setChecked(settings.value('ad_block', True, type=bool))
        self.safe_browsing.setChecked(settings.value('safe_browsing', True, type=bool))
        self.do_not_track.setChecked(settings.value('do_not_track', False, type=bool))
        self.cookie_policy.setCurrentText(settings.value('cookie_policy', 'Allow all cookies'))
        
        # Advanced
        self.enable_js.setChecked(settings.value('enable_js', True, type=bool))
        self.hw_acceleration.setChecked(settings.value('hw_acceleration', True, type=bool))
        
    def save_settings(self):
        settings = QSettings('NexusBrowser', 'Settings')
        
        # General
        settings.setValue('search_engine', self.search_engine.currentText())
        settings.setValue('custom_search', self.custom_search.text())
        settings.setValue('home_page', self.home_page.text())
        settings.setValue('theme', self.theme.currentText())
        
        # Privacy
        settings.setValue('ad_block', self.ad_block.isChecked())
        settings.setValue('safe_browsing', self.safe_browsing.isChecked())
        settings.setValue('do_not_track', self.do_not_track.isChecked())
        settings.setValue('cookie_policy', self.cookie_policy.currentText())
        
        # Advanced
        settings.setValue('enable_js', self.enable_js.isChecked())
        settings.setValue('hw_acceleration', self.hw_acceleration.isChecked())
        
    def accept(self):
        self.save_settings()
        super().accept()

class EnhancedBrowser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Nexus Browser")
        self.setGeometry(100, 100, 1200, 800)
        
        # Initialize managers
        self.history_manager = EnhancedHistoryManager()
        self.password_manager = EnhancedPasswordManager()
        self.bookmarks_manager = EnhancedBookmarksManager()
        self.theme_manager = ThemeManager()
        self.download_manager = DownloadManager()
        
        # Setup UI
        self.setup_ui()
        
        # Apply theme
        self.apply_theme()
        
        # Setup connections
        self.setup_connections()
        
        # Load home page
        self.load_home_page()
        
    def setup_ui(self):
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.setMovable(True)
        self.tab_widget.setDocumentMode(True)
        self.tab_widget.tabBar().setExpanding(False)
        
        # Create initial tab
        self.add_new_tab()
        
        main_layout.addWidget(self.tab_widget)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximumHeight(3)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setVisible(False)
        self.status_bar.addPermanentWidget(self.progress_bar, 1)
        
        # Create toolbar
        self.create_toolbar()
        
        # Create menu bar
        self.create_menu_bar()
        
        # Apply styling
        self.apply_styling()
        
    def create_toolbar(self):
        # Navigation toolbar
        nav_toolbar = QToolBar("Navigation")
        nav_toolbar.setMovable(False)
        nav_toolbar.setFloatable(False)
        nav_toolbar.setIconSize(QSize(24, 24))
        self.addToolBar(nav_toolbar)
        
        # Back button
        back_btn = QAction(QIcon.fromTheme("go-previous"), "Back", self)
        back_btn.setShortcut(QKeySequence.Back)
        nav_toolbar.addAction(back_btn)
        
        # Forward button
        forward_btn = QAction(QIcon.fromTheme("go-next"), "Forward", self)
        forward_btn.setShortcut(QKeySequence.Forward)
        nav_toolbar.addAction(forward_btn)
        
        # Reload button
        reload_btn = QAction(QIcon.fromTheme("view-refresh"), "Reload", self)
        reload_btn.setShortcut(QKeySequence.Refresh)
        nav_toolbar.addAction(reload_btn)
        
        # Home button
        home_btn = QAction(QIcon.fromTheme("go-home"), "Home", self)
        home_btn.setShortcut("Ctrl+H")
        nav_toolbar.addAction(home_btn)
        
        # Address bar
        self.url_bar = QLineEdit()
        self.url_bar.setPlaceholderText("Enter URL or search terms...")
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        nav_toolbar.addWidget(self.url_bar)
        
        # Go button
        go_btn = QAction(QIcon.fromTheme("go-jump"), "Go", self)
        go_btn.triggered.connect(self.navigate_to_url)
        nav_toolbar.addAction(go_btn)
        
        # Bookmarks button
        bookmarks_btn = QAction(QIcon.fromTheme("emblem-favorite"), "Bookmarks", self)
        bookmarks_btn.triggered.connect(self.show_bookmarks)
        nav_toolbar.addAction(bookmarks_btn)
        
        # History button
        history_btn = QAction(QIcon.fromTheme("view-history"), "History", self)
        history_btn.triggered.connect(self.show_history)
        nav_toolbar.addAction(history_btn)
        
        # Downloads button
        downloads_btn = QAction(QIcon.fromTheme("folder-downloads"), "Downloads", self)
        downloads_btn.triggered.connect(self.show_downloads)
        nav_toolbar.addAction(downloads_btn)
        
        # Settings button
        settings_btn = QAction(QIcon.fromTheme("preferences-system"), "Settings", self)
        settings_btn.triggered.connect(self.show_settings)
        nav_toolbar.addAction(settings_btn)
        
        # Connect actions
        back_btn.triggered.connect(self.navigate_back)
        forward_btn.triggered.connect(self.navigate_forward)
        reload_btn.triggered.connect(self.reload_page)
        home_btn.triggered.connect(self.load_home_page)
        
    def create_menu_bar(self):
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        new_tab_action = QAction("New Tab", self)
        new_tab_action.setShortcut("Ctrl+T")
        new_tab_action.triggered.connect(self.add_new_tab)
        file_menu.addAction(new_tab_action)
        
        new_window_action = QAction("New Window", self)
        new_window_action.setShortcut("Ctrl+N")
        new_window_action.triggered.connect(self.new_window)
        file_menu.addAction(new_window_action)
        
        file_menu.addSeparator()
        
        open_file_action = QAction("Open File", self)
        open_file_action.setShortcut("Ctrl+O")
        open_file_action.triggered.connect(self.open_file)
        file_menu.addAction(open_file_action)
        
        save_page_action = QAction("Save Page", self)
        save_page_action.setShortcut("Ctrl+S")
        save_page_action.triggered.connect(self.save_page)
        file_menu.addAction(save_page_action)
        
        file_menu.addSeparator()
        
        print_action = QAction("Print", self)
        print_action.setShortcut("Ctrl+P")
        print_action.triggered.connect(self.print_page)
        file_menu.addAction(print_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Edit menu
        edit_menu = menubar.addMenu("Edit")
        
        undo_action = QAction("Undo", self)
        undo_action.setShortcut("Ctrl+Z")
        undo_action.triggered.connect(self.undo)
        edit_menu.addAction(undo_action)
        
        redo_action = QAction("Redo", self)
        redo_action.setShortcut("Ctrl+Y")
        redo_action.triggered.connect(self.redo)
        edit_menu.addAction(redo_action)
        
        edit_menu.addSeparator()
        
        cut_action = QAction("Cut", self)
        cut_action.setShortcut("Ctrl+X")
        cut_action.triggered.connect(self.cut)
        edit_menu.addAction(cut_action)
        
        copy_action = QAction("Copy", self)
        copy_action.setShortcut("Ctrl+C")
        copy_action.triggered.connect(self.copy)
        edit_menu.addAction(copy_action)
        
        paste_action = QAction("Paste", self)
        paste_action.setShortcut("Ctrl+V")
        paste_action.triggered.connect(self.paste)
        edit_menu.addAction(paste_action)
        
        edit_menu.addSeparator()
        
        find_action = QAction("Find", self)
        find_action.setShortcut("Ctrl+F")
        find_action.triggered.connect(self.find_text)
        edit_menu.addAction(find_action)
        
        # View menu
        view_menu = menubar.addMenu("View")
        
        zoom_in_action = QAction("Zoom In", self)
        zoom_in_action.setShortcut("Ctrl++")
        zoom_in_action.triggered.connect(self.zoom_in)
        view_menu.addAction(zoom_in_action)
        
        zoom_out_action = QAction("Zoom Out", self)
        zoom_out_action.setShortcut("Ctrl+-")
        zoom_out_action.triggered.connect(self.zoom_out)
        view_menu.addAction(zoom_out_action)
        
        reset_zoom_action = QAction("Reset Zoom", self)
        reset_zoom_action.setShortcut("Ctrl+0")
        reset_zoom_action.triggered.connect(self.reset_zoom)
        view_menu.addAction(reset_zoom_action)
        
        view_menu.addSeparator()
        
        fullscreen_action = QAction("Fullscreen", self)
        fullscreen_action.setShortcut("F11")
        fullscreen_action.triggered.connect(self.toggle_fullscreen)
        view_menu.addAction(fullscreen_action)
        
        # History menu
        history_menu = menubar.addMenu("History")
        
        show_history_action = QAction("Show History", self)
        show_history_action.triggered.connect(self.show_history)
        history_menu.addAction(show_history_action)
        
        clear_history_action = QAction("Clear History", self)
        clear_history_action.triggered.connect(self.clear_history)
        history_menu.addAction(clear_history_action)
        
        # Bookmarks menu
        bookmarks_menu = menubar.addMenu("Bookmarks")
        
        show_bookmarks_action = QAction("Show Bookmarks", self)
        show_bookmarks_action.triggered.connect(self.show_bookmarks)
        bookmarks_menu.addAction(show_bookmarks_action)
        
        add_bookmark_action = QAction("Add Bookmark", self)
        add_bookmark_action.setShortcut("Ctrl+D")
        add_bookmark_action.triggered.connect(self.add_current_bookmark)
        bookmarks_menu.addAction(add_bookmark_action)
        
        # Tools menu
        tools_menu = menubar.addMenu("Tools")
        
        downloads_action = QAction("Downloads", self)
        downloads_action.triggered.connect(self.show_downloads)
        tools_menu.addAction(downloads_action)
        
        extensions_action = QAction("Extensions", self)
        extensions_action.triggered.connect(self.show_extensions)
        tools_menu.addAction(extensions_action)
        
        developer_tools_action = QAction("Developer Tools", self)
        developer_tools_action.setShortcut("F12")
        developer_tools_action.triggered.connect(self.show_developer_tools)
        tools_menu.addAction(developer_tools_action)
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
    def setup_connections(self):
        # Tab widget connections
        self.tab_widget.tabCloseRequested.connect(self.close_tab)
        self.tab_widget.currentChanged.connect(self.tab_changed)
        
        # Download manager connections - FIXED: Use correct method names
        self.download_manager.downloadProgress.connect(self.download_progress)
        self.download_manager.downloadFinished.connect(self.download_finished)
        
    def apply_styling(self):
        # Set application style
        self.setStyleSheet("""
            QMainWindow {
                background-color: #0a0a0a;
            }
            QToolBar {
                background-color: #1a1a1a;
                border: none;
                padding: 4px;
            }
            QToolButton {
                background-color: transparent;
                border: 1px solid transparent;
                border-radius: 4px;
                padding: 4px;
            }
            QToolButton:hover {
                background-color: #2d2d2d;
                border: 1px solid #00aaff;
            }
            QToolButton:pressed {
                background-color: #0044aa;
            }
            QLineEdit {
                background-color: #2d2d2d;
                border: 1px solid #00aaff;
                border-radius: 4px;
                padding: 6px;
                color: white;
                selection-background-color: #00aaff;
            }
            QLineEdit:focus {
                border: 2px solid #00fffc;
            }
            QTabWidget::pane {
                border: none;
                background-color: #0a0a0a;
            }
            QTabBar::tab {
                background-color: #1a1a1a;
                color: #cccccc;
                padding: 8px 12px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background-color: #2d2d2d;
                color: white;
                border-bottom: 2px solid #00fffc;
            }
            QTabBar::tab:hover:!selected {
                background-color: #2a2a2a;
            }
            QMenu {
                background-color: #1a1a1a;
                color: white;
                border: 1px solid #00aaff;
            }
            QMenu::item:selected {
                background-color: #0088ff;
            }
            QStatusBar {
                background-color: #1a1a1a;
                color: #cccccc;
            }
            QProgressBar {
                border: none;
                background-color: #2d2d2d;
            }
            QProgressBar::chunk {
                background-color: #00aaff;
            }
        """)
        
    def apply_theme(self):
        theme = self.theme_manager.get_theme()
        
        # Apply theme colors to specific elements
        style = f"""
            QMainWindow {{
                background-color: {theme['window_bg']};
            }}
            QToolBar {{
                background-color: {theme['toolbar_bg']};
                border: none;
                padding: 4px;
                color: {theme['text_color']};
            }}
            QToolButton {{
                background-color: transparent;
                border: 1px solid transparent;
                border-radius: 4px;
                padding: 4px;
                color: {theme['text_color']};
            }}
            QToolButton:hover {{
                background-color: {theme['button_hover_bg']};
                border: 1px solid {theme['accent_color']};
            }}
            QToolButton:pressed {{
                background-color: {theme['button_pressed_bg']};
            }}
            QLineEdit {{
                background-color: {theme['address_bar_bg']};
                border: 1px solid {theme['address_bar_border']};
                border-radius: 4px;
                padding: 6px;
                color: {theme['text_color']};
                selection-background-color: {theme['accent_color']};
            }}
            QLineEdit:focus {{
                border: 2px solid {theme['address_bar_focus_border']};
            }}
            QTabWidget::pane {{
                border: none;
                background-color: {theme['window_bg']};
            }}
            QTabBar::tab {{
                background-color: {theme['tab_bg']};
                color: {theme['text_secondary']};
                padding: 8px 12px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }}
            QTabBar::tab:selected {{
                background-color: {theme['tab_selected_bg']};
                color: {theme['text_color']};
                border-bottom: 2px solid {theme['tab_selected_border']};
            }}
            QTabBar::tab:hover:!selected {{
                background-color: {theme['tab_selected_bg']};
            }}
            QMenu {{
                background-color: {theme['menu_bg']};
                color: {theme['text_color']};
                border: 1px solid {theme['menu_border']};
            }}
            QMenu::item:selected {{
                background-color: {theme['menu_item_selected_bg']};
            }}
            QStatusBar {{
                background-color: {theme['toolbar_bg']};
                color: {theme['text_secondary']};
            }}
            QProgressBar {{
                border: none;
                background-color: {theme['address_bar_bg']};
            }}
            QProgressBar::chunk {{
                background-color: {theme['accent_color']};
            }}
        """
        
        self.setStyleSheet(style)
        
    def add_new_tab(self, url=None):
        # Create web view
        web_view = AdvancedWebView()
        
        # Create tab
        tab_index = self.tab_widget.addTab(web_view, "New Tab")
        self.tab_widget.setCurrentIndex(tab_index)
        
        # Set up web view
        if url:
            web_view.setUrl(QUrl(url))
        else:
            web_view.setUrl(QUrl("about:blank"))
            
        # Connect signals
        web_view.urlChanged.connect(lambda url, view=web_view: self.update_urlbar(url, view))
        web_view.loadFinished.connect(lambda ok, view=web_view: self.on_load_finished(ok, view))
        web_view.loadingProgress.connect(self.update_progress)
        web_view.faviconChanged.connect(lambda icon, view=web_view: self.update_tab_icon(icon, view))
        
        # Set up context menu
        web_view.setContextMenuPolicy(Qt.CustomContextMenu)
        web_view.customContextMenuRequested.connect(self.show_context_menu)
        
        return web_view
        
    def close_tab(self, index):
        if self.tab_widget.count() > 1:
            self.tab_widget.removeTab(index)
        else:
            self.close()
            
    def tab_changed(self, index):
        if index >= 0:
            web_view = self.tab_widget.widget(index)
            self.url_bar.setText(web_view.url().toString())
            
    def update_urlbar(self, url, web_view=None):
        if web_view != self.tab_widget.currentWidget():
            return
            
        self.url_bar.setText(url.toString())
        
    def on_load_finished(self, ok, web_view):
        if web_view != self.tab_widget.currentWidget():
            return
            
        # Update tab title
        title = web_view.page().title()
        index = self.tab_widget.indexOf(web_view)
        self.tab_widget.setTabText(index, title[:15] + "..." if len(title) > 15 else title)
        
        # Add to history
        if ok and web_view.url().scheme() in ['http', 'https']:
            self.history_manager.add_to_history(web_view.url().toString(), title)
            
    def update_progress(self, progress):
        if progress < 100:
            self.progress_bar.setValue(progress)
            self.progress_bar.setVisible(True)
        else:
            self.progress_bar.setVisible(False)
            
    def update_tab_icon(self, icon, web_view):
        index = self.tab_widget.indexOf(web_view)
        self.tab_widget.setTabIcon(index, icon)
        
    def navigate_to_url(self):
        url = self.url_bar.text()
        
        # Check if it's a search query
        if not url.startswith(('http://', 'https://', 'file://', 'about:')):
            # Use search engine
            search_engine = QSettings('NexusBrowser', 'Settings').value('search_engine', 'Google')
            search_urls = {
                'Google': 'https://www.google.com/search?q={}',
                'Bing': 'https://www.bing.com/search?q={}',
                'DuckDuckGo': 'https://duckduckgo.com/?q={}',
                'Yahoo': 'https://search.yahoo.com/search?p={}',
                'Custom': QSettings('NexusBrowser', 'Settings').value('custom_search', 'https://www.google.com/search?q={}')
            }
            
            url = search_urls.get(search_engine, 'https://www.google.com/search?q={}').format(url)
            
        # Load URL
        web_view = self.tab_widget.currentWidget()
        if web_view:
            web_view.setUrl(QUrl(url))
            
    def navigate_back(self):
        web_view = self.tab_widget.currentWidget()
        if web_view:
            web_view.back()
            
    def navigate_forward(self):
        web_view = self.tab_widget.currentWidget()
        if web_view:
            web_view.forward()
            
    def reload_page(self):
        web_view = self.tab_widget.currentWidget()
        if web_view:
            web_view.reload()
            
    def load_home_page(self):
        home_page = QSettings('NexusBrowser', 'Settings').value('home_page', 'https://www.google.com')
        web_view = self.tab_widget.currentWidget()
        if web_view:
            web_view.setUrl(QUrl(home_page))
            
    def show_bookmarks(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Bookmarks")
        dialog.setGeometry(400, 400, 600, 400)
        
        layout = QVBoxLayout()
        
        # Bookmarks list
        bookmarks_list = QListWidget()
        bookmarks = self.bookmarks_manager.get_bookmarks()
        
        for bookmark in bookmarks:
            item = QListWidgetItem(bookmark['title'])
            item.setData(Qt.UserRole, bookmark['url'])
            bookmarks_list.addItem(item)
            
        layout.addWidget(bookmarks_list)
        
        # Buttons
        button_layout = QHBoxLayout()
        open_btn = QPushButton("Open")
        open_btn.clicked.connect(lambda: self.open_bookmark(bookmarks_list, dialog))
        
        add_btn = QPushButton("Add Current")
        add_btn.clicked.connect(self.add_current_bookmark)
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dialog.accept)
        
        button_layout.addWidget(open_btn)
        button_layout.addWidget(add_btn)
        button_layout.addWidget(close_btn)
        layout.addLayout(button_layout)
        
        dialog.setLayout(layout)
        dialog.exec_()
        
    def open_bookmark(self, bookmarks_list, dialog):
        current_item = bookmarks_list.currentItem()
        if current_item:
            url = current_item.data(Qt.UserRole)
            web_view = self.tab_widget.currentWidget()
            if web_view:
                web_view.setUrl(QUrl(url))
            dialog.accept()
            
    def add_current_bookmark(self):
        web_view = self.tab_widget.currentWidget()
        if web_view:
            url = web_view.url().toString()
            title = web_view.page().title()
            
            # Show dialog to get folder and tags
            dialog = QDialog(self)
            dialog.setWindowTitle("Add Bookmark")
            dialog.setGeometry(400, 400, 400, 200)
            
            layout = QVBoxLayout()
            
            form_layout = QFormLayout()
            
            title_edit = QLineEdit(title)
            url_edit = QLineEdit(url)
            url_edit.setReadOnly(True)
            folder_edit = QLineEdit()
            tags_edit = QLineEdit()
            
            form_layout.addRow("Title:", title_edit)
            form_layout.addRow("URL:", url_edit)
            form_layout.addRow("Folder:", folder_edit)
            form_layout.addRow("Tags:", tags_edit)
            
            layout.addLayout(form_layout)
            
            button_layout = QHBoxLayout()
            save_btn = QPushButton("Save")
            save_btn.clicked.connect(dialog.accept)
            
            cancel_btn = QPushButton("Cancel")
            cancel_btn.clicked.connect(dialog.reject)
            
            button_layout.addWidget(save_btn)
            button_layout.addWidget(cancel_btn)
            layout.addLayout(button_layout)
            
            dialog.setLayout(layout)
            
            if dialog.exec_() == QDialog.Accepted:
                self.bookmarks_manager.add_bookmark(
                    url, title_edit.text(), folder_edit.text(), tags_edit.text()
                )
                
    def show_history(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("History")
        dialog.setGeometry(400, 400, 800, 500)
        
        layout = QVBoxLayout()
        
        # Search box
        search_layout = QHBoxLayout()
        search_edit = QLineEdit()
        search_edit.setPlaceholderText("Search history...")
        search_btn = QPushButton("Search")
        
        search_layout.addWidget(search_edit)
        search_layout.addWidget(search_btn)
        layout.addLayout(search_layout)
        
        # History list
        history_tree = QTreeWidget()
        history_tree.setHeaderLabels(["Title", "URL", "Visit Time", "Visit Count"])
        history_tree.header().setSectionResizeMode(0, QHeaderView.Stretch)
        history_tree.setAlternatingRowColors(True)
        
        # Load history
        history = self.history_manager.get_history(100)
        for url, title, visit_time, visit_count in history:
            item = QTreeWidgetItem(history_tree)
            item.setText(0, title)
            item.setText(1, url)
            item.setText(2, visit_time)
            item.setText(3, str(visit_count))
            
        layout.addWidget(history_tree)
        
        # Buttons
        button_layout = QHBoxLayout()
        open_btn = QPushButton("Open")
        open_btn.clicked.connect(lambda: self.open_history_item(history_tree, dialog))
        
        clear_btn = QPushButton("Clear History")
        clear_btn.clicked.connect(self.clear_history)
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dialog.accept)
        
        button_layout.addWidget(open_btn)
        button_layout.addWidget(clear_btn)
        button_layout.addWidget(close_btn)
        layout.addLayout(button_layout)
        
        # Connect search
        search_btn.clicked.connect(lambda: self.search_history(search_edit.text(), history_tree))
        search_edit.returnPressed.connect(lambda: self.search_history(search_edit.text(), history_tree))
        
        dialog.setLayout(layout)
        dialog.exec_()
        
    def open_history_item(self, history_tree, dialog):
        current_item = history_tree.currentItem()
        if current_item:
            url = current_item.text(1)
            web_view = self.tab_widget.currentWidget()
            if web_view:
                web_view.setUrl(QUrl(url))
            dialog.accept()
            
    def search_history(self, query, history_tree):
        history_tree.clear()
        results = self.history_manager.search_history(query)
        
        for url, title, visit_time in results:
            item = QTreeWidgetItem(history_tree)
            item.setText(0, title)
            item.setText(1, url)
            item.setText(2, visit_time)
            
    def clear_history(self):
        reply = QMessageBox.question(
            self, "Clear History",
            "Are you sure you want to clear your browsing history?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.history_manager.clear_history()
            QMessageBox.information(self, "History Cleared", "Your browsing history has been cleared.")
            
    def show_downloads(self):
        self.download_manager.exec_()
        
    def show_settings(self):
        dialog = EnhancedSettingsDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            # Apply new settings
            self.apply_theme()
            
    def show_extensions(self):
        dialog = ExtensionsManager(self)
        dialog.exec_()
        
    def show_developer_tools(self):
        web_view = self.tab_widget.currentWidget()
        if web_view:
            web_view.page().triggerAction(QWebEnginePage.InspectElement)
            
    def show_about(self):
        QMessageBox.about(
            self, "About Nexus Browser",
            "Nexus Browser\n\n"
            "A modern web browser built with PyQt5 and QtWebEngine.\n\n"
            "Version 1.0.0\n"
            "© 2023 Nexus Browser Team"
        )
        
    def show_context_menu(self, pos):
        web_view = self.sender()
        if not isinstance(web_view, AdvancedWebView):
            return
            
        menu = QMenu(self)
        
        # Back action
        back_action = QAction("Back", self)
        back_action.triggered.connect(web_view.back)
        back_action.setEnabled(web_view.history().canGoBack())
        menu.addAction(back_action)
        
        # Forward action
        forward_action = QAction("Forward", self)
        forward_action.triggered.connect(web_view.forward)
        forward_action.setEnabled(web_view.history().canGoForward())
        menu.addAction(forward_action)
        
        menu.addSeparator()
        
        # Reload action
        reload_action = QAction("Reload", self)
        reload_action.triggered.connect(web_view.reload)
        menu.addAction(reload_action)
        
        menu.addSeparator()
        
        # Open link in new tab
        hit_test = web_view.page().hitTestContent(pos)
        if hit_test.isContentEditable():
            # Editable content actions
            undo_action = QAction("Undo", self)
            undo_action.triggered.connect(web_view.page().undo)
            menu.addAction(undo_action)
            
            redo_action = QAction("Redo", self)
            redo_action.triggered.connect(web_view.page().redo)
            menu.addAction(redo_action)
            
            menu.addSeparator()
            
            cut_action = QAction("Cut", self)
            cut_action.triggered.connect(web_view.page().cut)
            menu.addAction(cut_action)
            
            copy_action = QAction("Copy", self)
            copy_action.triggered.connect(web_view.page().copy)
            menu.addAction(copy_action)
            
            paste_action = QAction("Paste", self)
            paste_action.triggered.connect(web_view.page().paste)
            menu.addAction(paste_action)
            
            menu.addSeparator()
            
            select_all_action = QAction("Select All", self)
            select_all_action.triggered.connect(web_view.page().selectAll)
            menu.addAction(select_all_action)
        elif hit_test.linkUrl().isValid():
            # Link actions
            open_link_action = QAction("Open Link", self)
            open_link_action.triggered.connect(lambda: web_view.setUrl(hit_test.linkUrl()))
            menu.addAction(open_link_action)
            
            open_new_tab_action = QAction("Open Link in New Tab", self)
            open_new_tab_action.triggered.connect(lambda: self.add_new_tab(hit_test.linkUrl().toString()))
            menu.addAction(open_new_tab_action)
            
            copy_link_action = QAction("Copy Link Address", self)
            copy_link_action.triggered.connect(lambda: QApplication.clipboard().setText(hit_test.linkUrl().toString()))
            menu.addAction(copy_link_action)
            
            menu.addSeparator()
            
            save_link_action = QAction("Save Link As...", self)
            save_link_action.triggered.connect(lambda: self.download_url(hit_test.linkUrl()))
            menu.addAction(save_link_action)
        elif hit_test.imageUrl().isValid():
            # Image actions
            view_image_action = QAction("View Image", self)
            view_image_action.triggered.connect(lambda: self.add_new_tab(hit_test.imageUrl().toString()))
            menu.addAction(view_image_action)
            
            copy_image_action = QAction("Copy Image", self)
            copy_image_action.triggered.connect(lambda: self.copy_image(hit_test.imageUrl()))
            menu.addAction(copy_image_action)
            
            save_image_action = QAction("Save Image As...", self)
            save_image_action.triggered.connect(lambda: self.download_url(hit_test.imageUrl()))
            menu.addAction(save_image_action)
        else:
            # Page actions
            view_source_action = QAction("View Page Source", self)
            view_source_action.triggered.connect(lambda: self.view_page_source(web_view))
            menu.addAction(view_source_action)
            
            inspect_action = QAction("Inspect Element", self)
            inspect_action.triggered.connect(lambda: web_view.page().triggerAction(QWebEnginePage.InspectElement))
            menu.addAction(inspect_action)
            
            menu.addSeparator()
            
            save_page_action = QAction("Save Page As...", self)
            save_page_action.triggered.connect(self.save_page)
            menu.addAction(save_page_action)
            
        menu.exec_(web_view.mapToGlobal(pos))
        
    def download_url(self, url):
        # Show save dialog
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save File", 
            os.path.basename(url.toString()),
            "All Files (*)"
        )
        
        if file_path:
            # Start download
            download_item = self.download_manager.add_download(file_path, url.toString())
            
            # Create download request
            download = web_view.page().profile().downloadRequested.connect(
                lambda download: self.handle_download(download, download_item)
            )
            
    def handle_download(self, download, item):
        # Connect download signals
        download.finished.connect(lambda: self.download_finished(download, item))
        download.downloadProgress.connect(lambda received, total: self.download_progress(received, total, item))
        
        # Set download path
        data = item.data(0, Qt.UserRole)
        download.setPath(data['path'])
        download.accept()
        
    def download_progress(self, received, total, item):
        self.download_manager.update_download(item, received, total)
        
    def download_finished(self, download, item):
        success = download.state() == QWebEngineDownloadItem.DownloadCompleted
        self.download_manager.finish_download(item, success)
        
    def copy_image(self, image_url):
        # Download image and copy to clipboard
        def image_downloaded(data):
            pixmap = QPixmap()
            pixmap.loadFromData(data)
            QApplication.clipboard().setPixmap(pixmap)
            
        web_view = self.tab_widget.currentWidget()
        if web_view:
            web_view.page().profile().downloadRequested.connect(
                lambda download: download.finished.connect(
                    lambda: image_downloaded(download.receivedData())
                )
            )
            
    def view_page_source(self, web_view):
        def source_received(content):
            source_view = QTextEdit()
            source_view.setPlainText(content)
            source_view.setReadOnly(True)
            source_view.setWindowTitle("Page Source - " + web_view.url().toString())
            source_view.resize(800, 600)
            source_view.show()
            
        web_view.page().toHtml(source_received)
        
    def new_window(self):
        new_browser = EnhancedBrowser()
        new_browser.show()
        
    def open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open HTML File", "", "HTML Files (*.html *.htm);;All Files (*)"
        )
        
        if file_path:
            web_view = self.tab_widget.currentWidget()
            if web_view:
                web_view.setUrl(QUrl.fromLocalFile(file_path))
                
    def save_page(self):
        web_view = self.tab_widget.currentWidget()
        if web_view:
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Save Page", 
                web_view.page().title() + ".html",
                "HTML Files (*.html *.htm);;Web Archive (*.mhtml);;Text Files (*.txt);;All Files (*)"
            )
            
            if file_path:
                if file_path.endswith('.mhtml'):
                    web_view.page().save(file_path, QWebEngineDownloadItem.MimeHtmlSaveFormat)
                else:
                    web_view.page().save(file_path, QWebEngineDownloadItem.CompleteHtmlSaveFormat)
                    
    def print_page(self):
        web_view = self.tab_widget.currentWidget()
        if web_view:
            printer = QPrinter()
            dialog = QPrintDialog(printer, self)
            if dialog.exec_() == QDialog.Accepted:
                web_view.print_(printer)
                
    def undo(self):
        web_view = self.tab_widget.currentWidget()
        if web_view:
            web_view.page().undo()
            
    def redo(self):
        web_view = self.tab_widget.currentWidget()
        if web_view:
            web_view.page().redo()
            
    def cut(self):
        web_view = self.tab_widget.currentWidget()
        if web_view:
            web_view.page().cut()
            
    def copy(self):
        web_view = self.tab_widget.currentWidget()
        if web_view:
            web_view.page().copy()
            
    def paste(self):
        web_view = self.tab_widget.currentWidget()
        if web_view:
            web_view.page().paste()
            
    def find_text(self):
        text, ok = QInputDialog.getText(self, "Find Text", "Enter text to find:")
        if ok and text:
            web_view = self.tab_widget.currentWidget()
            if web_view:
                web_view.findText(text)
                
    def zoom_in(self):
        web_view = self.tab_widget.currentWidget()
        if web_view:
            web_view.setZoomFactor(web_view.zoomFactor() + 0.1)
            
    def zoom_out(self):
        web_view = self.tab_widget.currentWidget()
        if web_view:
            web_view.setZoomFactor(web_view.zoomFactor() - 0.1)
            
    def reset_zoom(self):
        web_view = self.tab_widget.currentWidget()
        if web_view:
            web_view.setZoomFactor(1.0)
            
    def toggle_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

# ==============================
# MAIN APPLICATION
# ==============================

def main():
    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName("Nexus Browser")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("NexusBrowser")
    
    # Create and show browser
    browser = EnhancedBrowser()
    browser.show()
    
    # Run application
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()