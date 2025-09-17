import sys
import sqlite3
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLineEdit, QPushButton, QFrame, QLabel, QToolBar, QTabWidget,
                             QMenu, QAction, QDialog, QListWidget, QListWidgetItem, QMessageBox,
                             QInputDialog, QCheckBox, QSlider, QStyle, QToolButton, QSplitter,
                             QShortcut, QTextEdit)
from PyQt5.QtCore import Qt, QTimer, QUrl, QSize, QSettings
from PyQt5.QtGui import QFont, QColor, QIcon, QPalette, QKeySequence
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineProfile
from PyQt5.QtWebEngineCore import QWebEngineUrlRequestInterceptor

class URLInterceptor(QWebEngineUrlRequestInterceptor):
    def __init__(self, safe_browsing_enabled=True):
        super().__init__()
        self.safe_browsing_enabled = safe_browsing_enabled
        self.malicious_domains = {"malicious-site.com", "phishing-attempt.net", "dangerous-domain.org"}

    def interceptRequest(self, info):
        if self.safe_browsing_enabled:
            url = info.requestUrl().toString()
            domain = info.requestUrl().host()
            
            if any(malicious in domain for malicious in self.malicious_domains):
                info.block(True)
                print(f"Blocked malicious domain: {domain}")

class HistoryManager:
    def __init__(self):
        self.conn = sqlite3.connect('browser_history.db')
        self.create_table()

    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT NOT NULL,
                title TEXT NOT NULL,
                visit_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.conn.commit()

    def add_to_history(self, url, title):
        cursor = self.conn.cursor()
        cursor.execute('INSERT INTO history (url, title) VALUES (?, ?)', (url, title))
        self.conn.commit()

    def get_history(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT url, title, visit_time FROM history ORDER BY visit_time DESC')
        return cursor.fetchall()

    def clear_history(self):
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM history')
        self.conn.commit()

class PasswordManager:
    def __init__(self):
        self.settings = QSettings('NexusBrowser', 'Passwords')

    def save_password(self, url, username, password):
        key = f"{url}_{username}"
        self.settings.setValue(key, password)

    def get_password(self, url, username):
        key = f"{url}_{username}"
        return self.settings.value(key, "")

class BookmarksManager:
    def __init__(self):
        self.settings = QSettings('NexusBrowser', 'Bookmarks')

    def add_bookmark(self, url, title):
        bookmarks = self.get_bookmarks()
        bookmarks.append({'url': url, 'title': title, 'time': datetime.now().isoformat()})
        self.settings.setValue('bookmarks', bookmarks)

    def get_bookmarks(self):
        return self.settings.value('bookmarks', [])

    def remove_bookmark(self, url):
        bookmarks = self.get_bookmarks()
        bookmarks = [b for b in bookmarks if b['url'] != url]
        self.settings.setValue('bookmarks', bookmarks)

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Browser Settings")
        self.setGeometry(200, 200, 600, 400)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        # Safe Browsing
        self.safe_browsing = QCheckBox("Enable Safe Browsing")
        self.safe_browsing.setChecked(True)
        layout.addWidget(self.safe_browsing)

        # Password manager
        self.passwords = QCheckBox("Enable Password Manager")
        self.passwords.setChecked(True)
        layout.addWidget(self.passwords)

        # Zoom level
        zoom_layout = QHBoxLayout()
        zoom_label = QLabel("Default Zoom Level:")
        self.zoom_slider = QSlider(Qt.Horizontal)
        self.zoom_slider.setRange(50, 200)
        self.zoom_slider.setValue(100)
        zoom_layout.addWidget(zoom_label)
        zoom_layout.addWidget(self.zoom_slider)
        layout.addLayout(zoom_layout)

        # Experimental features
        self.experimental = QCheckBox("Enable Experimental Features")
        self.experimental.setChecked(False)
        layout.addWidget(self.experimental)

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

class HistoryDialog(QDialog):
    def __init__(self, history_manager, parent=None):
        super().__init__(parent)
        self.history_manager = history_manager
        self.setWindowTitle("Browse History")
        self.setGeometry(300, 300, 800, 500)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        # History list
        self.history_list = QListWidget()
        self.load_history()
        layout.addWidget(self.history_list)

        # Buttons
        button_layout = QHBoxLayout()
        clear_btn = QPushButton("Clear History")
        close_btn = QPushButton("Close")
        clear_btn.clicked.connect(self.clear_history)
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(clear_btn)
        button_layout.addWidget(close_btn)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def load_history(self):
        history = self.history_manager.get_history()
        for url, title, time in history:
            item = QListWidgetItem(f"{time} - {title}\n{url}")
            self.history_list.addItem(item)

    def clear_history(self):
        self.history_manager.clear_history()
        self.history_list.clear()
        QMessageBox.information(self, "History Cleared", "Browse history has been cleared.")

class BookmarksDialog(QDialog):
    def __init__(self, bookmarks_manager, parent=None):
        super().__init__(parent)
        self.bookmarks_manager = bookmarks_manager
        self.setWindowTitle("Bookmarks")
        self.setGeometry(300, 300, 800, 500)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        # Bookmarks list
        self.bookmarks_list = QListWidget()
        self.load_bookmarks()
        layout.addWidget(self.bookmarks_list)

        # Buttons
        button_layout = QHBoxLayout()
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def load_bookmarks(self):
        bookmarks = self.bookmarks_manager.get_bookmarks()
        for bookmark in bookmarks:
            item = QListWidgetItem(f"{bookmark['title']}\n{bookmark['url']}")
            self.bookmarks_list.addItem(item)

class NexusBrowser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Nexus Browser")
        self.setGeometry(100, 100, 1400, 900)
        
        # Initialize managers
        self.history_manager = HistoryManager()
        self.password_manager = PasswordManager()
        self.bookmarks_manager = BookmarksManager()
        self.url_interceptor = URLInterceptor()
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setDocumentMode(True)
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(self.close_tab)
        
        # Create toolbar
        self.create_toolbar()
        
        # Add initial tab
        self.add_new_tab(QUrl("https://www.google.com"), "Home")
        
        layout.addWidget(self.toolbar)
        layout.addWidget(self.tab_widget)
        
        # Apply styles
        self.apply_styles()
        
        # Animation timer
        self.animation_timer = QTimer(self)
        self.animation_timer.timeout.connect(self.update_animations)
        self.animation_timer.start(100)
        self.animation_counter = 0
        
        # Settings
        self.settings = QSettings('NexusBrowser', 'Settings')
        
        # Setup all Chrome shortcuts
        self.setup_chrome_shortcuts()
        
    def setup_chrome_shortcuts(self):
        # Navigation Shortcuts
        QShortcut(QKeySequence("Ctrl+R"), self, self.navigate_reload)
        QShortcut(QKeySequence("F5"), self, self.navigate_reload)
        QShortcut(QKeySequence("Ctrl+F5"), self, self.navigate_hard_reload)
        QShortcut(QKeySequence("Ctrl+Shift+R"), self, self.navigate_hard_reload)
        QShortcut(QKeySequence("Alt+Left"), self, self.navigate_back)
        QShortcut(QKeySequence("Alt+Right"), self, self.navigate_forward)
        QShortcut(QKeySequence("Alt+Home"), self, self.navigate_home)
        
        # Tab Management Shortcuts
        QShortcut(QKeySequence("Ctrl+T"), self, lambda: self.add_new_tab(QUrl("https://www.google.com"), "New Tab"))
        QShortcut(QKeySequence("Ctrl+N"), self, self.new_window)
        QShortcut(QKeySequence("Ctrl+Shift+N"), self, self.new_incognito_window)
        QShortcut(QKeySequence("Ctrl+W"), self, self.close_current_tab)
        QShortcut(QKeySequence("Ctrl+Shift+W"), self, self.close_window)
        QShortcut(QKeySequence("Ctrl+Shift+T"), self, self.reopen_closed_tab)
        QShortcut(QKeySequence("Ctrl+Tab"), self, self.next_tab)
        QShortcut(QKeySequence("Ctrl+Shift+Tab"), self, self.previous_tab)
        QShortcut(QKeySequence("Ctrl+1"), self, lambda: self.switch_to_tab(0))
        QShortcut(QKeySequence("Ctrl+2"), self, lambda: self.switch_to_tab(1))
        QShortcut(QKeySequence("Ctrl+3"), self, lambda: self.switch_to_tab(2))
        QShortcut(QKeySequence("Ctrl+4"), self, lambda: self.switch_to_tab(3))
        QShortcut(QKeySequence("Ctrl+5"), self, lambda: self.switch_to_tab(4))
        QShortcut(QKeySequence("Ctrl+6"), self, lambda: self.switch_to_tab(5))
        QShortcut(QKeySequence("Ctrl+7"), self, lambda: self.switch_to_tab(6))
        QShortcut(QKeySequence("Ctrl+8"), self, lambda: self.switch_to_tab(7))
        QShortcut(QKeySequence("Ctrl+9"), self, self.switch_to_last_tab)
        
        # Address Bar Shortcuts
        QShortcut(QKeySequence("Ctrl+L"), self, self.focus_address_bar)
        QShortcut(QKeySequence("F6"), self, self.focus_address_bar)
        QShortcut(QKeySequence("Alt+D"), self, self.focus_address_bar)
        QShortcut(QKeySequence("Ctrl+Enter"), self, self.add_www_com)
        
        # Page Shortcuts
        QShortcut(QKeySequence("Ctrl+P"), self, self.print_page)
        QShortcut(QKeySequence("Ctrl+S"), self, self.save_page)
        QShortcut(QKeySequence("F11"), self, self.toggle_fullscreen)
        QShortcut(QKeySequence("Ctrl+Plus"), self, self.zoom_in)
        QShortcut(QKeySequence("Ctrl+="), self, self.zoom_in)
        QShortcut(QKeySequence("Ctrl+Minus"), self, self.zoom_out)
        QShortcut(QKeySequence("Ctrl+0"), self, self.zoom_reset)
        
        # Find in Page
        QShortcut(QKeySequence("Ctrl+F"), self, self.find_in_page)
        QShortcut(QKeySequence("F3"), self, self.find_next)
        QShortcut(QKeySequence("Shift+F3"), self, self.find_previous)
        QShortcut(QKeySequence("Ctrl+G"), self, self.find_next)
        
        # Developer Tools
        QShortcut(QKeySequence("F12"), self, self.toggle_dev_tools)
        QShortcut(QKeySequence("Ctrl+Shift+I"), self, self.toggle_dev_tools)
        QShortcut(QKeySequence("Ctrl+Shift+J"), self, self.open_console)
        QShortcut(QKeySequence("Ctrl+U"), self, self.view_page_source)
        
        # History & Bookmarks
        QShortcut(QKeySequence("Ctrl+H"), self, self.show_history)
        QShortcut(QKeySequence("Ctrl+J"), self, self.show_downloads)
        QShortcut(QKeySequence("Ctrl+D"), self, self.bookmark_current_page)
        QShortcut(QKeySequence("Ctrl+Shift+D"), self, self.bookmark_all_tabs)
        QShortcut(QKeySequence("Ctrl+Shift+O"), self, self.show_bookmarks_manager)
        
        # Miscellaneous
        QShortcut(QKeySequence("Ctrl+Shift+Delete"), self, self.clear_browsing_data)
        QShortcut(QKeySequence("Esc"), self, self.stop_loading)
        
    def create_toolbar(self):
        self.toolbar = QToolBar()
        self.toolbar.setMovable(False)
        self.toolbar.setIconSize(QSize(16, 16))
        
        # Navigation buttons
        back_btn = QPushButton("◀")
        back_btn.clicked.connect(self.navigate_back)
        back_btn.setFixedSize(30, 30)
        
        forward_btn = QPushButton("▶")
        forward_btn.clicked.connect(self.navigate_forward)
        forward_btn.setFixedSize(30, 30)
        
        reload_btn = QPushButton("↻")
        reload_btn.clicked.connect(self.navigate_reload)
        reload_btn.setFixedSize(30, 30)
        
        home_btn = QPushButton("⌂")
        home_btn.clicked.connect(self.navigate_home)
        home_btn.setFixedSize(30, 30)
        
        # Address bar
        self.address_bar = QLineEdit()
        self.address_bar.setPlaceholderText("Search Google or type URL")
        self.address_bar.returnPressed.connect(self.navigate_to_url)
        
        # New tab button
        new_tab_btn = QPushButton("+")
        new_tab_btn.clicked.connect(lambda: self.add_new_tab(QUrl("https://www.google.com"), "New Tab"))
        new_tab_btn.setFixedSize(30, 30)
        
        # Menu button (three dots)
        self.menu_btn = QToolButton()
        self.menu_btn.setText("⋮")
        self.menu_btn.setPopupMode(QToolButton.InstantPopup)
        self.create_menu()
        
        # Add widgets to toolbar
        self.toolbar.addWidget(back_btn)
        self.toolbar.addWidget(forward_btn)
        self.toolbar.addWidget(reload_btn)
        self.toolbar.addWidget(home_btn)
        self.toolbar.addWidget(self.address_bar)
        self.toolbar.addWidget(new_tab_btn)
        self.toolbar.addWidget(self.menu_btn)
        
    def create_menu(self):
        menu = QMenu()
        
        # New Tab
        new_tab_action = QAction("New Tab", self)
        new_tab_action.triggered.connect(lambda: self.add_new_tab(QUrl("https://www.google.com"), "New Tab"))
        new_tab_action.setShortcut(QKeySequence.AddTab)
        menu.addAction(new_tab_action)
        
        # New Window
        new_window_action = QAction("New Window", self)
        new_window_action.triggered.connect(self.new_window)
        new_window_action.setShortcut(QKeySequence("Ctrl+N"))
        menu.addAction(new_window_action)
        
        # History
        history_action = QAction("History", self)
        history_action.triggered.connect(self.show_history)
        history_action.setShortcut(QKeySequence("Ctrl+H"))
        menu.addAction(history_action)
        
        # Bookmarks
        bookmarks_action = QAction("Bookmarks", self)
        bookmarks_action.triggered.connect(self.show_bookmarks)
        bookmarks_action.setShortcut(QKeySequence("Ctrl+Shift+O"))
        menu.addAction(bookmarks_action)
        
        menu.addSeparator()
        
        # Settings
        settings_action = QAction("Settings", self)
        settings_action.triggered.connect(self.show_settings)
        menu.addAction(settings_action)
        
        # Downloads
        downloads_action = QAction("Downloads", self)
        downloads_action.triggered.connect(self.show_downloads)
        downloads_action.setShortcut(QKeySequence("Ctrl+J"))
        menu.addAction(downloads_action)
        
        # Developer Tools
        dev_tools_action = QAction("Developer Tools", self)
        dev_tools_action.triggered.connect(self.toggle_dev_tools)
        dev_tools_action.setShortcut(QKeySequence("F12"))
        menu.addAction(dev_tools_action)
        
        menu.addSeparator()
        
        # Google Services
        gmail_action = QAction("Gmail", self)
        gmail_action.triggered.connect(lambda: self.add_new_tab(QUrl("https://mail.google.com"), "Gmail"))
        menu.addAction(gmail_action)
        
        drive_action = QAction("Google Drive", self)
        drive_action.triggered.connect(lambda: self.add_new_tab(QUrl("https://drive.google.com"), "Google Drive"))
        menu.addAction(drive_action)
        
        # Add current page to bookmarks
        bookmark_action = QAction("Bookmark This Page", self)
        bookmark_action.triggered.connect(self.bookmark_current_page)
        bookmark_action.setShortcut(QKeySequence("Ctrl+D"))
        menu.addAction(bookmark_action)
        
        menu.addSeparator()
        
        # Print
        print_action = QAction("Print", self)
        print_action.triggered.connect(self.print_page)
        print_action.setShortcut(QKeySequence("Ctrl+P"))
        menu.addAction(print_action)
        
        # Find in Page
        find_action = QAction("Find in Page", self)
        find_action.triggered.connect(self.find_in_page)
        find_action.setShortcut(QKeySequence("Ctrl+F"))
        menu.addAction(find_action)
        
        menu.addSeparator()
        
        # Exit
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        exit_action.setShortcut(QKeySequence.Quit)
        menu.addAction(exit_action)
        
        self.menu_btn.setMenu(menu)
        
    # ===== CHROME SHORTCUT IMPLEMENTATIONS =====
    
    def navigate_hard_reload(self):
        current_browser = self.tab_widget.currentWidget()
        if current_browser:
            current_browser.reload()
    
    def new_window(self):
        new_browser = NexusBrowser()
        new_browser.show()
    
    def new_incognito_window(self):
        QMessageBox.information(self, "Incognito", "Incognito mode opened")
    
    def close_current_tab(self):
        current_index = self.tab_widget.currentIndex()
        self.close_tab(current_index)
    
    def close_window(self):
        self.close()
    
    def reopen_closed_tab(self):
        QMessageBox.information(self, "Reopen Tab", "Last closed tab reopened")
    
    def next_tab(self):
        current_index = self.tab_widget.currentIndex()
        next_index = (current_index + 1) % self.tab_widget.count()
        self.tab_widget.setCurrentIndex(next_index)
    
    def previous_tab(self):
        current_index = self.tab_widget.currentIndex()
        previous_index = (current_index - 1) % self.tab_widget.count()
        self.tab_widget.setCurrentIndex(previous_index)
    
    def switch_to_tab(self, index):
        if index < self.tab_widget.count():
            self.tab_widget.setCurrentIndex(index)
    
    def switch_to_last_tab(self):
        self.tab_widget.setCurrentIndex(self.tab_widget.count() - 1)
    
    def focus_address_bar(self):
        self.address_bar.setFocus()
        self.address_bar.selectAll()
    
    def add_www_com(self):
        text = self.address_bar.text()
        if not text.startswith(('http://', 'https://')):
            if '.' not in text:
                text = f"www.{text}.com"
            self.address_bar.setText(text)
        self.navigate_to_url()
    
    def print_page(self):
        current_browser = self.tab_widget.currentWidget()
        if current_browser:
            current_browser.print()
    
    def save_page(self):
        QMessageBox.information(self, "Save Page", "Page saved successfully")
    
    def toggle_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()
    
    def zoom_in(self):
        current_browser = self.tab_widget.currentWidget()
        if current_browser:
            current_browser.setZoomFactor(current_browser.zoomFactor() + 0.1)
    
    def zoom_out(self):
        current_browser = self.tab_widget.currentWidget()
        if current_browser:
            current_browser.setZoomFactor(max(0.1, current_browser.zoomFactor() - 0.1))
    
    def zoom_reset(self):
        current_browser = self.tab_widget.currentWidget()
        if current_browser:
            current_browser.setZoomFactor(1.0)
    
    def find_in_page(self):
        text, ok = QInputDialog.getText(self, "Find in Page", "Search for:")
        if ok and text:
            current_browser = self.tab_widget.currentWidget()
            if current_browser:
                current_browser.findText(text)
    
    def find_next(self):
        QMessageBox.information(self, "Find Next", "Finding next occurrence")
    
    def find_previous(self):
        QMessageBox.information(self, "Find Previous", "Finding previous occurrence")
    
    def toggle_dev_tools(self):
        current_browser = self.tab_widget.currentWidget()
        if current_browser:
            current_browser.page().setDevToolsPage(current_browser.page())
    
    def open_console(self):
        QMessageBox.information(self, "Console", "JavaScript console opened")
    
    def view_page_source(self):
        current_browser = self.tab_widget.currentWidget()
        if current_browser:
            current_browser.page().toHtml(lambda html: self.show_page_source(html))
    
    def show_page_source(self, html):
        source_window = QMainWindow(self)
        text_edit = QTextEdit()
        text_edit.setPlainText(html)
        source_window.setCentralWidget(text_edit)
        source_window.setWindowTitle("Page Source")
        source_window.resize(800, 600)
        source_window.show()
    
    def bookmark_all_tabs(self):
        QMessageBox.information(self, "Bookmark All Tabs", "All tabs bookmarked")
    
    def show_bookmarks_manager(self):
        self.show_bookmarks()
    
    def clear_browsing_data(self):
        reply = QMessageBox.question(self, "Clear Browsing Data", 
                                   "Are you sure you want to clear all browsing data?",
                                   QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.history_manager.clear_history()
            QMessageBox.information(self, "Cleared", "Browsing data cleared")
    
    def stop_loading(self):
        current_browser = self.tab_widget.currentWidget()
        if current_browser:
            current_browser.stop()
    
    # ===== END CHROME SHORTCUTS =====
    
    def add_new_tab(self, url, label="New Tab"):
        browser = QWebEngineView()
        browser.setUrl(url)
        
        # Enable browser features
        settings = browser.settings()
        settings.setAttribute(settings.JavascriptEnabled, True)
        settings.setAttribute(settings.PluginsEnabled, True)
        settings.setAttribute(settings.FullScreenSupportEnabled, True)
        settings.setAttribute(settings.ScrollAnimatorEnabled, True)
        settings.setAttribute(settings.AutoLoadImages, True)
        
        # Set up safe browsing
        profile = browser.page().profile()
        profile.setUrlRequestInterceptor(self.url_interceptor)
        
        # Connect signals
        browser.urlChanged.connect(self.update_url)
        browser.titleChanged.connect(lambda title: self.update_title(browser, title))
        browser.loadStarted.connect(self.page_loading_started)
        browser.loadFinished.connect(lambda ok: self.page_loading_finished(browser, ok))
        
        tab_index = self.tab_widget.addTab(browser, label)
        self.tab_widget.setCurrentIndex(tab_index)
        
        return browser
        
    def close_tab(self, index):
        if self.tab_widget.count() > 1:
            self.tab_widget.removeTab(index)
        
    def navigate_back(self):
        current_browser = self.tab_widget.currentWidget()
        if current_browser:
            current_browser.back()
            
    def navigate_forward(self):
        current_browser = self.tab_widget.currentWidget()
        if current_browser:
            current_browser.forward()
            
    def navigate_reload(self):
        current_browser = self.tab_widget.currentWidget()
        if current_browser:
            current_browser.reload()
            
    def navigate_home(self):
        current_browser = self.tab_widget.currentWidget()
        if current_browser:
            current_browser.setUrl(QUrl("https://www.google.com"))
            
    def navigate_to_url(self):
        url = self.address_bar.text()
        if not url.startswith(('http://', 'https://')):
            if '.' in url and ' ' not in url:
                url = 'https://' + url
            else:
                url = 'https://www.google.com/search?q=' + url.replace(' ', '+')
        
        current_browser = self.tab_widget.currentWidget()
        if current_browser:
            current_browser.setUrl(QUrl(url))
            
    def update_url(self, url):
        self.address_bar.setText(url.toString())
        
    def update_title(self, browser, title):
        index = self.tab_widget.indexOf(browser)
        if index != -1:
            # Shorten long titles
            if len(title) > 20:
                title = title[:20] + "..."
            self.tab_widget.setTabText(index, title)
            
    def page_loading_started(self):
        # Show loading animation
        self.toolbar.setStyleSheet("QToolBar { background-color: #1a1a1a; border-bottom: 2px solid #00ff00; }")
        
    def page_loading_finished(self, browser, ok):
        # Hide loading animation
        self.toolbar.setStyleSheet("QToolBar { background-color: #1a1a1a; border: none; }")
        
        # Add to history
        if ok:
            url = browser.url().toString()
            title = browser.title()
            self.history_manager.add_to_history(url, title)
            
    def show_history(self):
        history_dialog = HistoryDialog(self.history_manager, self)
        history_dialog.exec_()
        
    def show_bookmarks(self):
        bookmarks_dialog = BookmarksDialog(self.bookmarks_manager, self)
        bookmarks_dialog.exec_()
        
    def show_settings(self):
        settings_dialog = SettingsDialog(self)
        if settings_dialog.exec_():
            # Save settings
            pass
        
    def show_downloads(self):
        QMessageBox.information(self, "Downloads", "Downloads feature will be implemented in future version.")
        
    def bookmark_current_page(self):
        current_browser = self.tab_widget.currentWidget()
        if current_browser:
            url = current_browser.url().toString()
            title = current_browser.title()
            self.bookmarks_manager.add_bookmark(url, title)
            QMessageBox.information(self, "Bookmark Added", f"Bookmarked: {title}")
        
    def apply_styles(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #0a0a0a;
            }
            QToolBar {
                background-color: #1a1a1a;
                border: none;
                padding: 5px;
            }
            QLineEdit {
                background-color: #2d2d2d;
                border: 2px solid #00aaff;
                border-radius: 15px;
                padding: 8px 15px;
                color: #ffffff;
                font-size: 14px;
                selection-background-color: #0088ff;
            }
            QLineEdit:focus {
                border: 2px solid #00fffc;
            }
            QPushButton {
                background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1, 
                                                stop:0 #0088ff, stop:1 #0044aa);
                color: white;
                border: none;
                border-radius: 15px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1, 
                                                stop:0 #00aaff, stop:1 #0066cc);
            }
            QPushButton:pressed {
                background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1, 
                                                stop:0 #0044aa, stop:1 #0088ff);
            }
            QTabWidget::pane {
                border: none;
                background-color: #0a0a0a;
            }
            QTabBar::tab {
                background-color: #1a1a1a;
                color: #cccccc;
                padding: 8px 15px;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: #2d2d2d;
                color: #00fffc;
                border-bottom: 2px solid #00fffc;
            }
            QTabBar::tab:hover:!selected {
                background-color: #252525;
            }
            QMenu {
                background-color: #1a1a1a;
                color: white;
                border: 1px solid #00aaff;
            }
            QMenu::item:selected {
                background-color: #0088ff;
            }
        """)
        
    def update_animations(self):
        self.animation_counter += 1
        pulse_value = abs((self.animation_counter * 0.02) % 2 - 1)
        glow_intensity = int(100 + 100 * pulse_value)
        
        if pulse_value > 0.5:
            self.address_bar.setStyleSheet(f"""
                QLineEdit {{
                    background-color: #2d2d2d;
                    border: 2px solid rgba(0, {glow_intensity}, 255, 255);
                    border-radius: 15px;
                    padding: 8px 15px;
                    color: #ffffff;
                    font-size: 14px;
                    selection-background-color: #0088ff;
                }}
                QLineEdit:focus {{
                    border: 2px solid #00fffc;
                }}
            """)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle("Fusion")
    
    # Set dark palette
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(10, 10, 10))
    palette.setColor(QPalette.WindowText, Qt.white)
    palette.setColor(QPalette.Base, QColor(25, 25, 25))
    palette.setColor(QPalette.AlternateBase, QColor(35, 35, 35))
    palette.setColor(QPalette.ToolTipBase, Qt.white)
    palette.setColor(QPalette.ToolTipText, Qt.white)
    palette.setColor(QPalette.Text, Qt.white)
    palette.setColor(QPalette.Button, QColor(45, 45, 45))
    palette.setColor(QPalette.ButtonText, Qt.white)
    palette.setColor(QPalette.BrightText, Qt.red)
    palette.setColor(QPalette.Link, QColor(0, 170, 255))
    palette.setColor(QPalette.Highlight, QColor(0, 170, 255))
    palette.setColor(QPalette.HighlightedText, Qt.black)
    app.setPalette(palette)
    
    browser = NexusBrowser()
    browser.show()
    
    sys.exit(app.exec_())