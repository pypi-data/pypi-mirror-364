#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cloud Notepad - Modern Notepad Uygulaması
PyQt6 ile geliştirilmiş gelişmiş notepad uygulaması
"""

import sys
import os
import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QTextEdit, QVBoxLayout, 
    QHBoxLayout, QWidget, QMenuBar, QMenu, QToolBar, QStatusBar,
    QFileDialog, QMessageBox, QInputDialog, QDialog, QLabel,
    QLineEdit, QPushButton, QGridLayout, QComboBox, QCheckBox,
    QSplitter, QListWidget, QListWidgetItem, QFontDialog, QColorDialog,
    QProgressBar, QFrame, QScrollArea, QGroupBox, QSpinBox
)
from PyQt6.QtCore import (
    Qt, QTimer, QThread, pyqtSignal, QSettings, QSize, QPoint,
    QPropertyAnimation, QEasingCurve
)
from PyQt6.QtGui import (
    QAction, QIcon, QFont, QTextCursor, QTextCharFormat, QColor,
    QPalette, QKeySequence, QPixmap, QPainter, QTextFormat
)

from syntax_highlighter import SyntaxHighlighter
from cloud_sync import CloudSync
from settings_dialog import SettingsDialog
from find_replace_dialog import FindReplaceDialog


class CloudNotepad(QMainWindow):
    """Ana Cloud Notepad uygulaması sınıfı"""
    
    def __init__(self):
        super().__init__()
        self.settings = QSettings('CloudNotepad', 'CloudNotepad')
        self.current_files = {}  # tab_id -> file_path
        self.unsaved_changes = set()
        self.cloud_sync = CloudSync()
        self.auto_save_timer = QTimer()
        self.auto_save_timer.timeout.connect(self.auto_save_all)
        
        self.init_ui()
        self.load_settings()
        self.setup_auto_save()
        
    def init_ui(self):
        """Kullanıcı arayüzünü başlat"""
        self.setWindowTitle("Cloud Notepad - Modern Notepad")
        self.setGeometry(100, 100, 1200, 800)
        
        # Ana widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Ana layout
        main_layout = QHBoxLayout(central_widget)
        
        # Sol panel (dosya gezgini)
        self.file_explorer = self.create_file_explorer()
        main_layout.addWidget(self.file_explorer, 1)
        
        # Orta panel (sekme widget)
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(self.close_tab)
        self.tab_widget.currentChanged.connect(self.tab_changed)
        main_layout.addWidget(self.tab_widget, 4)
        
        # Sağ panel (ayarlar ve bilgiler)
        self.right_panel = self.create_right_panel()
        main_layout.addWidget(self.right_panel, 1)
        
        # Menü çubuğu
        self.create_menu_bar()
        
        # Araç çubuğu
        self.create_toolbar()
        
        # Durum çubuğu
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Hazır")
        
        # İlk sekmeyi oluştur
        self.new_tab()
        
    def create_file_explorer(self):
        """Sol panel dosya gezginini oluştur"""
        # Ana panel
        panel = QFrame()
        panel.setFrameStyle(QFrame.Shape.StyledPanel)
        panel.setMaximumWidth(300)
        panel.setMinimumWidth(50)
        
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Başlık çubuğu (genişletme/daraltma için)
        title_bar = QFrame()
        title_bar.setStyleSheet("background-color: #f0f0f0; border-bottom: 1px solid #ccc;")
        title_bar.setFixedHeight(40)
        
        title_layout = QHBoxLayout(title_bar)
        title_layout.setContentsMargins(10, 5, 10, 5)
        
        # Başlık
        title = QLabel("📁 Dosya Gezgini")
        title.setStyleSheet("font-weight: bold; font-size: 14px;")
        title_layout.addWidget(title)
        
        # Genişletme/daraltma butonu
        self.expand_button = QPushButton("◀")
        self.expand_button.setFixedSize(20, 20)
        self.expand_button.setStyleSheet("""
            QPushButton {
                border: none;
                background-color: transparent;
                font-weight: bold;
                color: #666;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
                border-radius: 3px;
            }
        """)
        self.expand_button.clicked.connect(self.toggle_file_explorer)
        title_layout.addWidget(self.expand_button)
        
        layout.addWidget(title_bar)
        
        # İçerik paneli
        self.file_explorer_content = QFrame()
        self.file_explorer_content.setVisible(True)
        content_layout = QVBoxLayout(self.file_explorer_content)
        content_layout.setContentsMargins(5, 5, 5, 5)
        
        # Dosya listesi
        self.file_list = QListWidget()
        self.file_list.itemDoubleClicked.connect(self.open_file_from_list)
        self.file_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #ccc;
                border-radius: 3px;
                background-color: white;
            }
            QListWidget::item {
                padding: 5px;
                border-bottom: 1px solid #f0f0f0;
            }
            QListWidget::item:hover {
                background-color: #e8f4fd;
            }
            QListWidget::item:selected {
                background-color: #0078d4;
                color: white;
            }
        """)
        content_layout.addWidget(self.file_list)
        
        # Butonlar
        btn_layout = QHBoxLayout()
        
        new_file_btn = QPushButton("📄 Yeni")
        new_file_btn.setStyleSheet("""
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                padding: 5px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #106ebe;
            }
        """)
        new_file_btn.clicked.connect(self.new_tab)
        btn_layout.addWidget(new_file_btn)
        
        open_file_btn = QPushButton("📂 Aç")
        open_file_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                padding: 5px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        open_file_btn.clicked.connect(self.open_file)
        btn_layout.addWidget(open_file_btn)
        
        content_layout.addLayout(btn_layout)
        
        layout.addWidget(self.file_explorer_content)
        
        # Panel genişletilmiş durumda başla
        self.file_explorer_expanded = True
        
        return panel
        
    def create_right_panel(self):
        """Sağ panel oluştur"""
        panel = QFrame()
        panel.setFrameStyle(QFrame.Shape.StyledPanel)
        panel.setMaximumWidth(280)
        panel.setMinimumWidth(50)
        
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Başlık çubuğu
        title_bar = QFrame()
        title_bar.setStyleSheet("background-color: #f0f0f0; border-bottom: 1px solid #ccc;")
        title_bar.setFixedHeight(40)
        
        title_layout = QHBoxLayout(title_bar)
        title_layout.setContentsMargins(10, 5, 10, 5)
        
        # Başlık
        title = QLabel("⚙️ Ayarlar")
        title.setStyleSheet("font-weight: bold; font-size: 14px;")
        title_layout.addWidget(title)
        
        # Genişletme/daraltma butonu
        self.settings_expand_button = QPushButton("◀")
        self.settings_expand_button.setFixedSize(20, 20)
        self.settings_expand_button.setStyleSheet("""
            QPushButton {
                border: none;
                background-color: transparent;
                font-weight: bold;
                color: #666;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
                border-radius: 3px;
            }
        """)
        self.settings_expand_button.clicked.connect(self.toggle_settings_panel)
        title_layout.addWidget(self.settings_expand_button)
        
        layout.addWidget(title_bar)
        
        # İçerik paneli
        self.settings_content = QFrame()
        self.settings_content.setVisible(True)
        content_layout = QVBoxLayout(self.settings_content)
        content_layout.setContentsMargins(10, 10, 10, 10)
        
        # Scroll area için widget
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        
        # Dosya bilgileri grubu
        file_group = QGroupBox("📄 Dosya Bilgileri")
        file_layout = QVBoxLayout(file_group)
        
        self.file_info_label = QLabel("Dosya bilgisi yok")
        self.file_info_label.setWordWrap(True)
        self.file_info_label.setStyleSheet("padding: 5px; background-color: #f8f9fa; border-radius: 3px;")
        file_layout.addWidget(self.file_info_label)
        
        scroll_layout.addWidget(file_group)
        
        # İstatistikler grubu
        stats_group = QGroupBox("📊 İstatistikler")
        stats_layout = QVBoxLayout(stats_group)
        
        self.stats_label = QLabel("Satır: 0\nKelime: 0\nKarakter: 0")
        self.stats_label.setStyleSheet("padding: 5px; background-color: #f8f9fa; border-radius: 3px;")
        stats_layout.addWidget(self.stats_label)
        
        scroll_layout.addWidget(stats_group)
        
        # Tema ayarları grubu
        theme_group = QGroupBox("🎨 Tema")
        theme_layout = QGridLayout(theme_group)
        
        theme_layout.addWidget(QLabel("Tema:"), 0, 0)
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Açık", "Koyu", "Otomatik"])
        self.theme_combo.currentTextChanged.connect(self.change_theme)
        self.theme_combo.setStyleSheet("""
            QComboBox {
                padding: 5px;
                border: 1px solid #ccc;
                border-radius: 3px;
                background-color: white;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #666;
            }
        """)
        theme_layout.addWidget(self.theme_combo, 0, 1)
        
        scroll_layout.addWidget(theme_group)
        
        # Font ayarları grubu
        font_group = QGroupBox("🔤 Font Ayarları")
        font_layout = QGridLayout(font_group)
        
        # Font ailesi
        font_layout.addWidget(QLabel("Font:"), 0, 0)
        self.font_family_combo = QComboBox()
        self.font_family_combo.addItems(["Consolas", "Monaco", "Courier New", "DejaVu Sans Mono", "Source Code Pro", "Fira Code", "JetBrains Mono"])
        self.font_family_combo.currentTextChanged.connect(self.apply_font_settings)
        self.font_family_combo.setStyleSheet("""
            QComboBox {
                padding: 5px;
                border: 1px solid #ccc;
                border-radius: 3px;
                background-color: white;
            }
        """)
        font_layout.addWidget(self.font_family_combo, 0, 1)
        
        # Font boyutu
        font_layout.addWidget(QLabel("Boyut:"), 1, 0)
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(8, 72)
        self.font_size_spin.setValue(12)
        self.font_size_spin.valueChanged.connect(self.apply_font_settings)
        self.font_size_spin.setStyleSheet("""
            QSpinBox {
                padding: 5px;
                border: 1px solid #ccc;
                border-radius: 3px;
                background-color: white;
            }
        """)
        font_layout.addWidget(self.font_size_spin, 1, 1)
        
        # Font stili
        font_layout.addWidget(QLabel("Stil:"), 2, 0)
        self.font_style_combo = QComboBox()
        self.font_style_combo.addItems(["Normal", "Kalın", "İtalik", "Kalın İtalik"])
        self.font_style_combo.currentTextChanged.connect(self.apply_font_settings)
        self.font_style_combo.setStyleSheet("""
            QComboBox {
                padding: 5px;
                border: 1px solid #ccc;
                border-radius: 3px;
                background-color: white;
            }
        """)
        font_layout.addWidget(self.font_style_combo, 2, 1)
        
        # Font önizleme
        self.font_preview_label = QLabel("Font Önizleme: AaBbCcDd 123")
        self.font_preview_label.setStyleSheet("""
            padding: 10px;
            background-color: #f8f9fa;
            border: 1px solid #ccc;
            border-radius: 3px;
            margin-top: 5px;
        """)
        self.font_preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font_layout.addWidget(self.font_preview_label, 3, 0, 1, 2)
        
        # Font seçici butonu
        self.font_dialog_btn = QPushButton("🎨 Font Seçici")
        self.font_dialog_btn.clicked.connect(self.show_font_dialog)
        self.font_dialog_btn.setStyleSheet("""
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                padding: 8px;
                border-radius: 3px;
                margin-top: 5px;
            }
            QPushButton:hover {
                background-color: #106ebe;
            }
        """)
        font_layout.addWidget(self.font_dialog_btn, 4, 0, 1, 2)
        
        scroll_layout.addWidget(font_group)
        
        # Editör ayarları grubu
        editor_group = QGroupBox("✏️ Editör")
        editor_layout = QVBoxLayout(editor_group)
        
        self.show_line_numbers_cb = QCheckBox("Satır numaralarını göster")
        self.show_line_numbers_cb.setChecked(True)
        self.show_line_numbers_cb.toggled.connect(self.apply_editor_settings)
        editor_layout.addWidget(self.show_line_numbers_cb)
        
        self.word_wrap_cb = QCheckBox("Kelime kaydırma")
        self.word_wrap_cb.toggled.connect(self.apply_editor_settings)
        editor_layout.addWidget(self.word_wrap_cb)
        
        self.syntax_highlighting_cb = QCheckBox("Syntax highlighting")
        self.syntax_highlighting_cb.setChecked(True)
        self.syntax_highlighting_cb.toggled.connect(self.apply_editor_settings)
        editor_layout.addWidget(self.syntax_highlighting_cb)
        
        scroll_layout.addWidget(editor_group)
        
        # Scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)
        
        content_layout.addWidget(scroll_area)
        
        layout.addWidget(self.settings_content)
        
        # Panel genişletilmiş durumda başla
        self.settings_expanded = True
        
        return panel
        
    def create_menu_bar(self):
        """Menü çubuğunu oluştur"""
        menubar = self.menuBar()
        
        # Dosya menüsü
        file_menu = menubar.addMenu('&Dosya')
        
        new_action = QAction('&Yeni', self)
        new_action.setShortcut('Ctrl+N')
        new_action.triggered.connect(self.new_tab)
        file_menu.addAction(new_action)
        
        open_action = QAction('&Aç...', self)
        open_action.setShortcut('Ctrl+O')
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)
        
        save_action = QAction('&Kaydet', self)
        save_action.setShortcut('Ctrl+S')
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)
        
        save_as_action = QAction('Farklı &Kaydet...', self)
        save_as_action.setShortcut('Ctrl+Shift+S')
        save_as_action.triggered.connect(self.save_file_as)
        file_menu.addAction(save_as_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction('&Çıkış', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Düzenle menüsü
        edit_menu = menubar.addMenu('&Düzenle')
        
        undo_action = QAction('&Geri Al', self)
        undo_action.setShortcut('Ctrl+Z')
        undo_action.triggered.connect(self.undo)
        edit_menu.addAction(undo_action)
        
        redo_action = QAction('&Yinele', self)
        redo_action.setShortcut('Ctrl+Y')
        redo_action.triggered.connect(self.redo)
        edit_menu.addAction(redo_action)
        
        edit_menu.addSeparator()
        
        cut_action = QAction('&Kes', self)
        cut_action.setShortcut('Ctrl+X')
        cut_action.triggered.connect(self.cut)
        edit_menu.addAction(cut_action)
        
        copy_action = QAction('&Kopyala', self)
        copy_action.setShortcut('Ctrl+C')
        copy_action.triggered.connect(self.copy)
        edit_menu.addAction(copy_action)
        
        paste_action = QAction('&Yapıştır', self)
        paste_action.setShortcut('Ctrl+V')
        paste_action.triggered.connect(self.paste)
        edit_menu.addAction(paste_action)
        
        edit_menu.addSeparator()
        
        find_action = QAction('&Bul...', self)
        find_action.setShortcut('Ctrl+F')
        find_action.triggered.connect(self.show_find_dialog)
        edit_menu.addAction(find_action)
        
        replace_action = QAction('&Değiştir...', self)
        replace_action.setShortcut('Ctrl+H')
        replace_action.triggered.connect(self.show_replace_dialog)
        edit_menu.addAction(replace_action)
        
        # Görünüm menüsü
        view_menu = menubar.addMenu('&Görünüm')
        
        zoom_in_action = QAction('&Yakınlaştır', self)
        zoom_in_action.setShortcut('Ctrl++')
        zoom_in_action.triggered.connect(self.zoom_in)
        view_menu.addAction(zoom_in_action)
        
        zoom_out_action = QAction('&Uzaklaştır', self)
        zoom_out_action.setShortcut('Ctrl+-')
        zoom_out_action.triggered.connect(self.zoom_out)
        view_menu.addAction(zoom_out_action)
        
        reset_zoom_action = QAction('&Yakınlaştırmayı Sıfırla', self)
        reset_zoom_action.setShortcut('Ctrl+0')
        reset_zoom_action.triggered.connect(self.reset_zoom)
        view_menu.addAction(reset_zoom_action)
        
        # Araçlar menüsü
        tools_menu = menubar.addMenu('&Araçlar')
        
        settings_action = QAction('&Ayarlar...', self)
        settings_action.triggered.connect(self.show_settings)
        tools_menu.addAction(settings_action)
        
        sync_action = QAction('&Senkronize Et', self)
        sync_action.triggered.connect(self.sync_files)
        tools_menu.addAction(sync_action)
        
        # Yardım menüsü
        help_menu = menubar.addMenu('&Yardım')
        
        about_action = QAction('&Hakkında', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
    def create_toolbar(self):
        """Araç çubuğunu oluştur"""
        toolbar = QToolBar()
        self.addToolBar(toolbar)
        
        # Yeni dosya
        new_action = QAction('Yeni', self)
        new_action.triggered.connect(self.new_tab)
        toolbar.addAction(new_action)
        
        # Aç
        open_action = QAction('Aç', self)
        open_action.triggered.connect(self.open_file)
        toolbar.addAction(open_action)
        
        # Kaydet
        save_action = QAction('Kaydet', self)
        save_action.triggered.connect(self.save_file)
        toolbar.addAction(save_action)
        
        toolbar.addSeparator()
        
        # Bul
        find_action = QAction('Bul', self)
        find_action.triggered.connect(self.show_find_dialog)
        toolbar.addAction(find_action)
        
        # Zoom
        zoom_in_action = QAction('+', self)
        zoom_in_action.triggered.connect(self.zoom_in)
        toolbar.addAction(zoom_in_action)
        
        zoom_out_action = QAction('-', self)
        zoom_out_action.triggered.connect(self.zoom_out)
        toolbar.addAction(zoom_out_action)
        
    def new_tab(self, file_path: str = None):
        """Yeni sekme oluştur"""
        text_edit = QTextEdit()
        text_edit.setFont(QFont("Consolas", 12))
        text_edit.textChanged.connect(self.text_changed)
        
        # Syntax highlighter ekle
        highlighter = SyntaxHighlighter(text_edit.document())
        
        if file_path:
            self.load_file_content(text_edit, file_path)
            tab_title = os.path.basename(file_path)
            self.current_files[id(text_edit)] = file_path
        else:
            tab_title = f"Yeni Dosya {self.tab_widget.count() + 1}"
            
        tab_index = self.tab_widget.addTab(text_edit, tab_title)
        self.tab_widget.setCurrentIndex(tab_index)
        
        # Dosya listesine ekle
        if file_path:
            self.add_file_to_list(file_path)
            
    def load_file_content(self, text_edit: QTextEdit, file_path: str):
        """Dosya içeriğini yükle"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                text_edit.setPlainText(content)
        except Exception as e:
            QMessageBox.warning(self, "Hata", f"Dosya yüklenirken hata oluştu: {e}")
            
    def add_file_to_list(self, file_path: str):
        """Dosyayı sol panel listesine ekle"""
        item = QListWidgetItem(os.path.basename(file_path))
        item.setData(Qt.ItemDataRole.UserRole, file_path)
        self.file_list.addItem(item)
        
    def open_file_from_list(self, item: QListWidgetItem):
        """Listeden dosya aç"""
        file_path = item.data(Qt.ItemDataRole.UserRole)
        if file_path and os.path.exists(file_path):
            self.new_tab(file_path)
            
    def open_file(self):
        """Dosya aç dialog'u"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Dosya Aç", "", 
            "Tüm Dosyalar (*);;Metin Dosyaları (*.txt);;Python (*.py);;HTML (*.html);;CSS (*.css);;JavaScript (*.js)"
        )
        
        if file_path:
            self.new_tab(file_path)
            
    def save_file(self):
        """Dosyayı kaydet"""
        current_widget = self.tab_widget.currentWidget()
        if not current_widget:
            return
            
        tab_id = id(current_widget)
        file_path = self.current_files.get(tab_id)
        
        if file_path:
            self.save_file_content(current_widget, file_path)
        else:
            self.save_file_as()
            
    def save_file_as(self):
        """Dosyayı farklı kaydet"""
        current_widget = self.tab_widget.currentWidget()
        if not current_widget:
            return
            
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Farklı Kaydet", "", 
            "Tüm Dosyalar (*);;Metin Dosyaları (*.txt);;Python (*.py);;HTML (*.html);;CSS (*.css);;JavaScript (*.js)"
        )
        
        if file_path:
            self.save_file_content(current_widget, file_path)
            self.current_files[id(current_widget)] = file_path
            self.tab_widget.setTabText(self.tab_widget.currentIndex(), os.path.basename(file_path))
            self.add_file_to_list(file_path)
            
    def save_file_content(self, text_edit: QTextEdit, file_path: str):
        """Dosya içeriğini kaydet"""
        try:
            content = text_edit.toPlainText()
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Kaydedildi olarak işaretle
            tab_id = id(text_edit)
            if tab_id in self.unsaved_changes:
                self.unsaved_changes.remove(tab_id)
                
            self.status_bar.showMessage(f"Dosya kaydedildi: {file_path}", 3000)
            
        except Exception as e:
            QMessageBox.warning(self, "Hata", f"Dosya kaydedilirken hata oluştu: {e}")
            
    def close_tab(self, index: int):
        """Sekme kapat"""
        widget = self.tab_widget.widget(index)
        if not widget:
            return
            
        tab_id = id(widget)
        
        # Kaydedilmemiş değişiklikler var mı kontrol et
        if tab_id in self.unsaved_changes:
            reply = QMessageBox.question(
                self, "Kaydedilmemiş Değişiklikler",
                "Kaydedilmemiş değişiklikler var. Kaydetmek istiyor musunuz?",
                QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel
            )
            
            if reply == QMessageBox.StandardButton.Save:
                self.save_file()
            elif reply == QMessageBox.StandardButton.Cancel:
                return
                
        self.tab_widget.removeTab(index)
        
        # Temizlik
        if tab_id in self.current_files:
            del self.current_files[tab_id]
        if tab_id in self.unsaved_changes:
            self.unsaved_changes.remove(tab_id)
            
    def text_changed(self):
        """Metin değiştiğinde çağrılır"""
        current_widget = self.tab_widget.currentWidget()
        if current_widget:
            tab_id = id(current_widget)
            self.unsaved_changes.add(tab_id)
            
            # Sekme başlığına * ekle
            current_index = self.tab_widget.currentIndex()
            current_title = self.tab_widget.tabText(current_index)
            if not current_title.endswith('*'):
                self.tab_widget.setTabText(current_index, current_title + '*')
                
    def tab_changed(self, index: int):
        """Sekme değiştiğinde çağrılır"""
        if index >= 0:
            widget = self.tab_widget.widget(index)
            if widget:
                self.update_file_info(widget)
                
    def update_file_info(self, text_edit: QTextEdit):
        """Dosya bilgilerini güncelle"""
        tab_id = id(text_edit)
        file_path = self.current_files.get(tab_id)
        
        if file_path:
            # Dosya bilgileri
            file_size = os.path.getsize(file_path)
            file_info = f"Dosya: {os.path.basename(file_path)}\n"
            file_info += f"Boyut: {file_size} bytes\n"
            file_info += f"Yol: {file_path}"
            self.file_info_label.setText(file_info)
            
            # İstatistikler
            text = text_edit.toPlainText()
            lines = len(text.split('\n'))
            words = len(text.split())
            chars = len(text)
            
            stats = f"Satır: {lines}\nKelime: {words}\nKarakter: {chars}"
            self.stats_label.setText(stats)
        else:
            self.file_info_label.setText("Dosya bilgisi yok")
            
    def setup_auto_save(self):
        """Otomatik kaydetme ayarla"""
        auto_save_interval = self.settings.value('auto_save_interval', 300000)  # 5 dakika
        self.auto_save_timer.start(auto_save_interval)
        
    def auto_save_all(self):
        """Tüm dosyaları otomatik kaydet"""
        for tab_id, file_path in self.current_files.items():
            if tab_id in self.unsaved_changes:
                # Widget'ı bul
                for i in range(self.tab_widget.count()):
                    widget = self.tab_widget.widget(i)
                    if id(widget) == tab_id:
                        self.save_file_content(widget, file_path)
                        break
                        
    def load_settings(self):
        """Ayarları yükle"""
        # Tema
        theme = self.settings.value('theme', 'Açık')
        self.theme_combo.setCurrentText(theme)
        self.apply_theme(theme)
        
        # Font ayarları
        font_family = self.settings.value('font_family', 'Consolas')
        font_size = int(self.settings.value('font_size', 12))
        font_style = self.settings.value('font_style', 'Normal')
        
        # Font combo box'larını güncelle
        if hasattr(self, 'font_family_combo'):
            self.font_family_combo.setCurrentText(font_family)
        if hasattr(self, 'font_size_spin'):
            self.font_size_spin.setValue(font_size)
        if hasattr(self, 'font_style_combo'):
            self.font_style_combo.setCurrentText(font_style)
            
        # Font oluştur ve uygula
        font = QFont(font_family, font_size)
        if font_style == "Kalın":
            font.setBold(True)
        elif font_style == "İtalik":
            font.setItalic(True)
        elif font_style == "Kalın İtalik":
            font.setBold(True)
            font.setItalic(True)
            
        self.apply_font_to_all(font)
        
        # Font önizlemesini güncelle
        if hasattr(self, 'font_preview_label'):
            self.update_font_preview()
            
        # Editör ayarları
        if hasattr(self, 'show_line_numbers_cb'):
            show_line_numbers = self.settings.value('show_line_numbers', True, type=bool)
            self.show_line_numbers_cb.setChecked(show_line_numbers)
            
        if hasattr(self, 'word_wrap_cb'):
            word_wrap = self.settings.value('word_wrap', False, type=bool)
            self.word_wrap_cb.setChecked(word_wrap)
            
        if hasattr(self, 'syntax_highlighting_cb'):
            syntax_highlighting = self.settings.value('syntax_highlighting', True, type=bool)
            self.syntax_highlighting_cb.setChecked(syntax_highlighting)
        
    def apply_theme(self, theme: str):
        """Tema uygula"""
        if theme == "Koyu":
            self.set_dark_theme()
        else:
            self.set_light_theme()
            
    def set_dark_theme(self):
        """Koyu tema uygula"""
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(53, 53, 53))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.Base, QColor(25, 25, 25))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(53, 53, 53))
        palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.ToolTipText, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.Text, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.BrightText, QColor(255, 0, 0))
        palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
        palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))
        
        QApplication.setPalette(palette)
        
    def set_light_theme(self):
        """Açık tema uygula"""
        QApplication.setPalette(QApplication.style().standardPalette())
        
    def change_theme(self, theme: str):
        """Tema değiştir"""
        self.apply_theme(theme)
        self.settings.setValue('theme', theme)
        
    def toggle_settings_panel(self):
        """Ayarlar panelini genişlet/daralt"""
        if self.settings_expanded:
            # Daralt
            self.settings_content.setVisible(False)
            self.right_panel.setMaximumWidth(50)
            self.settings_expand_button.setText("▶")
            self.settings_expanded = False
        else:
            # Genişlet
            self.settings_content.setVisible(True)
            self.right_panel.setMaximumWidth(280)
            self.settings_expand_button.setText("◀")
            self.settings_expanded = True
            
    def show_font_dialog(self):
        """Font seçici dialog'unu göster"""
        font, ok = QFontDialog.getFont()
        if ok:
            self.apply_font_to_all(font)
            self.settings.setValue('font_family', font.family())
            self.settings.setValue('font_size', font.pointSize())
            
            # Combo box'ları güncelle
            self.font_family_combo.setCurrentText(font.family())
            self.font_size_spin.setValue(font.pointSize())
            
            # Font stilini güncelle
            if font.bold() and font.italic():
                self.font_style_combo.setCurrentText("Kalın İtalik")
            elif font.bold():
                self.font_style_combo.setCurrentText("Kalın")
            elif font.italic():
                self.font_style_combo.setCurrentText("İtalik")
            else:
                self.font_style_combo.setCurrentText("Normal")
                
            self.update_font_preview()
            
    def apply_font_settings(self):
        """Font ayarlarını uygula"""
        font_family = self.font_family_combo.currentText()
        font_size = self.font_size_spin.value()
        font_style = self.font_style_combo.currentText()
        
        # Font oluştur
        font = QFont(font_family, font_size)
        
        # Stil ayarla
        if font_style == "Kalın":
            font.setBold(True)
        elif font_style == "İtalik":
            font.setItalic(True)
        elif font_style == "Kalın İtalik":
            font.setBold(True)
            font.setItalic(True)
            
        # Font'u uygula
        self.apply_font_to_all(font)
        
        # Ayarları kaydet
        self.settings.setValue('font_family', font_family)
        self.settings.setValue('font_size', font_size)
        self.settings.setValue('font_style', font_style)
        
        # Önizlemeyi güncelle
        self.update_font_preview()
        
    def update_font_preview(self):
        """Font önizlemesini güncelle"""
        font_family = self.font_family_combo.currentText()
        font_size = self.font_size_spin.value()
        font_style = self.font_style_combo.currentText()
        
        # Font oluştur
        font = QFont(font_family, font_size)
        
        # Stil ayarla
        if font_style == "Kalın":
            font.setBold(True)
        elif font_style == "İtalik":
            font.setItalic(True)
        elif font_style == "Kalın İtalik":
            font.setBold(True)
            font.setItalic(True)
            
        self.font_preview_label.setFont(font)
        
    def apply_editor_settings(self):
        """Editör ayarlarını uygula"""
        # Satır numaraları
        show_line_numbers = self.show_line_numbers_cb.isChecked()
        self.settings.setValue('show_line_numbers', show_line_numbers)
        
        # Kelime kaydırma
        word_wrap = self.word_wrap_cb.isChecked()
        self.settings.setValue('word_wrap', word_wrap)
        
        # Syntax highlighting
        syntax_highlighting = self.syntax_highlighting_cb.isChecked()
        self.settings.setValue('syntax_highlighting', syntax_highlighting)
        
        # Editörlere uygula
        for i in range(self.tab_widget.count()):
            widget = self.tab_widget.widget(i)
            if isinstance(widget, QTextEdit):
                # Kelime kaydırma
                if word_wrap:
                    widget.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)
                else:
                    widget.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
                    
    def change_font(self):
        """Font değiştir (eski fonksiyon - geriye uyumluluk için)"""
        self.show_font_dialog()
            
    def apply_font_to_all(self, font: QFont):
        """Tüm editörlere font uygula"""
        for i in range(self.tab_widget.count()):
            widget = self.tab_widget.widget(i)
            if isinstance(widget, QTextEdit):
                widget.setFont(font)
                
    def zoom_in(self):
        """Yakınlaştır"""
        current_widget = self.tab_widget.currentWidget()
        if current_widget:
            font = current_widget.font()
            font.setPointSize(font.pointSize() + 1)
            current_widget.setFont(font)
            
    def zoom_out(self):
        """Uzaklaştır"""
        current_widget = self.tab_widget.currentWidget()
        if current_widget:
            font = current_widget.font()
            if font.pointSize() > 6:
                font.setPointSize(font.pointSize() - 1)
                current_widget.setFont(font)
                
    def reset_zoom(self):
        """Yakınlaştırmayı sıfırla"""
        current_widget = self.tab_widget.currentWidget()
        if current_widget:
            font = QFont("Consolas", 12)
            current_widget.setFont(font)
            
    def undo(self):
        """Geri al"""
        current_widget = self.tab_widget.currentWidget()
        if current_widget:
            current_widget.undo()
            
    def redo(self):
        """Yinele"""
        current_widget = self.tab_widget.currentWidget()
        if current_widget:
            current_widget.redo()
            
    def cut(self):
        """Kes"""
        current_widget = self.tab_widget.currentWidget()
        if current_widget:
            current_widget.cut()
            
    def copy(self):
        """Kopyala"""
        current_widget = self.tab_widget.currentWidget()
        if current_widget:
            current_widget.copy()
            
    def paste(self):
        """Yapıştır"""
        current_widget = self.tab_widget.currentWidget()
        if current_widget:
            current_widget.paste()
            
    def show_find_dialog(self):
        """Bul dialog'unu göster"""
        dialog = FindReplaceDialog(self, find_only=True)
        dialog.exec()
        
    def show_replace_dialog(self):
        """Değiştir dialog'unu göster"""
        dialog = FindReplaceDialog(self, find_only=False)
        dialog.exec()
        
    def show_settings(self):
        """Ayarlar dialog'unu göster"""
        dialog = SettingsDialog(self)
        dialog.exec()
        
    def toggle_file_explorer(self):
        """Dosya gezginini genişlet/daralt"""
        if self.file_explorer_expanded:
            # Daralt
            self.file_explorer_content.setVisible(False)
            self.file_explorer.setMaximumWidth(50)
            self.expand_button.setText("▶")
            self.file_explorer_expanded = False
        else:
            # Genişlet
            self.file_explorer_content.setVisible(True)
            self.file_explorer.setMaximumWidth(300)
            self.expand_button.setText("◀")
            self.file_explorer_expanded = True
            
    def sync_files(self):
        """Dosyaları senkronize et"""
        # Cloud sync işlemi burada yapılacak
        self.status_bar.showMessage("Dosyalar senkronize ediliyor...", 3000)
        
    def show_about(self):
        """Hakkında dialog'u"""
        QMessageBox.about(
            self, "Cloud Notepad Hakkında",
            "Cloud Notepad v1.0\n\n"
            "Modern ve gelişmiş notepad uygulaması\n"
            "PyQt6 ile geliştirilmiştir.\n\n"
            "Özellikler:\n"
            "- Çoklu sekme desteği\n"
            "- Syntax highlighting\n"
            "- Tema desteği\n"
            "- Cloud senkronizasyon\n"
            "- Otomatik kaydetme"
        )
        
    def closeEvent(self, event):
        """Uygulama kapatılırken"""
        # Kaydedilmemiş değişiklikleri kontrol et
        if self.unsaved_changes:
            reply = QMessageBox.question(
                self, "Kaydedilmemiş Değişiklikler",
                "Kaydedilmemiş değişiklikler var. Çıkmak istediğinizden emin misiniz?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.No:
                event.ignore()
                return
                
        # Ayarları kaydet
        self.settings.sync()
        event.accept()


def main():
    """Ana fonksiyon"""
    app = QApplication(sys.argv)
    app.setApplicationName("Cloud Notepad")
    app.setApplicationVersion("1.0")
    
    # Stil ayarla
    app.setStyle('Fusion')
    
    # Ana pencereyi oluştur
    window = CloudNotepad()
    window.show()
    
    # Uygulamayı çalıştır
    sys.exit(app.exec())


if __name__ == '__main__':
    main() 