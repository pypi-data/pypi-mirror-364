#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Settings Dialog - Ayarlar dialog'u
Uygulama ayarlarını yönetme
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QCheckBox, QGroupBox, QGridLayout, QSpinBox,
    QComboBox, QTabWidget, QWidget, QFontDialog, QColorDialog,
    QSlider, QTextEdit, QListWidget, QListWidgetItem
)
from PyQt6.QtCore import Qt, QSettings
from PyQt6.QtGui import QFont, QColor


class SettingsDialog(QDialog):
    """Ayarlar dialog'u"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.settings = QSettings('CloudNotepad', 'CloudNotepad')
        
        self.init_ui()
        self.load_settings()
        
    def init_ui(self):
        """Kullanıcı arayüzünü başlat"""
        self.setWindowTitle("Ayarlar")
        self.setModal(True)
        self.setFixedSize(600, 500)
        
        layout = QVBoxLayout(self)
        
        # Tab widget
        tab_widget = QTabWidget()
        
        # Genel ayarlar
        general_tab = self.create_general_tab()
        tab_widget.addTab(general_tab, "Genel")
        
        # Editör ayarları
        editor_tab = self.create_editor_tab()
        tab_widget.addTab(editor_tab, "Editör")
        
        # Cloud ayarları
        cloud_tab = self.create_cloud_tab()
        tab_widget.addTab(cloud_tab, "Cloud")
        
        # Gelişmiş ayarlar
        advanced_tab = self.create_advanced_tab()
        tab_widget.addTab(advanced_tab, "Gelişmiş")
        
        layout.addWidget(tab_widget)
        
        # Butonlar
        button_layout = QHBoxLayout()
        
        self.ok_button = QPushButton("Tamam")
        self.ok_button.clicked.connect(self.accept)
        button_layout.addWidget(self.ok_button)
        
        self.cancel_button = QPushButton("İptal")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
        self.apply_button = QPushButton("Uygula")
        self.apply_button.clicked.connect(self.apply_settings)
        button_layout.addWidget(self.apply_button)
        
        layout.addLayout(button_layout)
        
    def create_general_tab(self):
        """Genel ayarlar sekmesi"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Tema ayarları
        theme_group = QGroupBox("Tema")
        theme_layout = QGridLayout(theme_group)
        
        theme_layout.addWidget(QLabel("Tema:"), 0, 0)
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Açık", "Koyu", "Otomatik"])
        theme_layout.addWidget(self.theme_combo, 0, 1)
        
        layout.addWidget(theme_group)
        
        # Dil ayarları
        language_group = QGroupBox("Dil")
        language_layout = QGridLayout(language_group)
        
        language_layout.addWidget(QLabel("Dil:"), 0, 0)
        self.language_combo = QComboBox()
        self.language_combo.addItems(["Türkçe", "English"])
        language_layout.addWidget(self.language_combo, 0, 1)
        
        layout.addWidget(language_group)
        
        # Başlangıç ayarları
        startup_group = QGroupBox("Başlangıç")
        startup_layout = QGridLayout(startup_group)
        
        self.startup_new_file = QCheckBox("Başlangıçta yeni dosya aç")
        startup_layout.addWidget(self.startup_new_file, 0, 0, 1, 2)
        
        self.remember_files = QCheckBox("Son açılan dosyaları hatırla")
        startup_layout.addWidget(self.remember_files, 1, 0, 1, 2)
        
        self.max_recent_files = QSpinBox()
        self.max_recent_files.setRange(1, 20)
        self.max_recent_files.setValue(10)
        startup_layout.addWidget(QLabel("Maksimum son dosya sayısı:"), 2, 0)
        startup_layout.addWidget(self.max_recent_files, 2, 1)
        
        layout.addWidget(startup_group)
        
        layout.addStretch()
        return widget
        
    def create_editor_tab(self):
        """Editör ayarları sekmesi"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Font ayarları
        font_group = QGroupBox("Font")
        font_layout = QGridLayout(font_group)
        
        font_layout.addWidget(QLabel("Font:"), 0, 0)
        self.font_button = QPushButton("Font Seç...")
        self.font_button.clicked.connect(self.select_font)
        font_layout.addWidget(self.font_button, 0, 1)
        
        self.font_preview = QLabel("Consolas, 12pt")
        self.font_preview.setStyleSheet("border: 1px solid gray; padding: 5px;")
        font_layout.addWidget(self.font_preview, 1, 0, 1, 2)
        
        layout.addWidget(font_group)
        
        # Editör ayarları
        editor_group = QGroupBox("Editör")
        editor_layout = QGridLayout(editor_group)
        
        self.show_line_numbers = QCheckBox("Satır numaralarını göster")
        editor_layout.addWidget(self.show_line_numbers, 0, 0, 1, 2)
        
        self.show_whitespace = QCheckBox("Boşlukları göster")
        editor_layout.addWidget(self.show_whitespace, 1, 0, 1, 2)
        
        self.word_wrap = QCheckBox("Kelime kaydırma")
        editor_layout.addWidget(self.word_wrap, 2, 0, 1, 2)
        
        self.auto_indent = QCheckBox("Otomatik girinti")
        editor_layout.addWidget(self.auto_indent, 3, 0, 1, 2)
        
        self.syntax_highlighting = QCheckBox("Syntax highlighting")
        editor_layout.addWidget(self.syntax_highlighting, 4, 0, 1, 2)
        
        layout.addWidget(editor_group)
        
        # Otomatik kaydetme
        autosave_group = QGroupBox("Otomatik Kaydetme")
        autosave_layout = QGridLayout(autosave_group)
        
        self.enable_autosave = QCheckBox("Otomatik kaydetmeyi etkinleştir")
        autosave_layout.addWidget(self.enable_autosave, 0, 0, 1, 2)
        
        autosave_layout.addWidget(QLabel("Kaydetme aralığı (saniye):"), 1, 0)
        self.autosave_interval = QSpinBox()
        self.autosave_interval.setRange(30, 3600)
        self.autosave_interval.setValue(300)
        autosave_layout.addWidget(self.autosave_interval, 1, 1)
        
        layout.addWidget(autosave_group)
        
        layout.addStretch()
        return widget
        
    def create_cloud_tab(self):
        """Cloud ayarları sekmesi"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Cloud servis ayarları
        cloud_group = QGroupBox("Cloud Servis")
        cloud_layout = QGridLayout(cloud_group)
        
        cloud_layout.addWidget(QLabel("Servis:"), 0, 0)
        self.cloud_service = QComboBox()
        self.cloud_service.addItems(["Google Drive", "Dropbox", "OneDrive", "Local Sync"])
        cloud_layout.addWidget(self.cloud_service, 0, 1)
        
        cloud_layout.addWidget(QLabel("API Key:"), 1, 0)
        self.api_key_edit = QLineEdit()
        self.api_key_edit.setEchoMode(QLineEdit.EchoMode.Password)
        cloud_layout.addWidget(self.api_key_edit, 1, 1)
        
        cloud_layout.addWidget(QLabel("Sync Klasörü:"), 2, 0)
        self.sync_folder_edit = QLineEdit()
        cloud_layout.addWidget(self.sync_folder_edit, 2, 1)
        
        self.browse_folder_button = QPushButton("Gözat...")
        self.browse_folder_button.clicked.connect(self.browse_sync_folder)
        cloud_layout.addWidget(self.browse_folder_button, 2, 2)
        
        layout.addWidget(cloud_group)
        
        # Senkronizasyon ayarları
        sync_group = QGroupBox("Senkronizasyon")
        sync_layout = QGridLayout(sync_group)
        
        self.auto_sync = QCheckBox("Otomatik senkronizasyon")
        sync_layout.addWidget(self.auto_sync, 0, 0, 1, 2)
        
        sync_layout.addWidget(QLabel("Senkronizasyon aralığı (dakika):"), 1, 0)
        self.sync_interval = QSpinBox()
        self.sync_interval.setRange(1, 1440)
        self.sync_interval.setValue(30)
        sync_layout.addWidget(self.sync_interval, 1, 1)
        
        self.sync_on_startup = QCheckBox("Başlangıçta senkronize et")
        sync_layout.addWidget(self.sync_on_startup, 2, 0, 1, 2)
        
        self.sync_on_save = QCheckBox("Kaydetme sırasında senkronize et")
        sync_layout.addWidget(self.sync_on_save, 3, 0, 1, 2)
        
        layout.addWidget(sync_group)
        
        # Test butonu
        self.test_connection_button = QPushButton("Bağlantıyı Test Et")
        self.test_connection_button.clicked.connect(self.test_connection)
        layout.addWidget(self.test_connection_button)
        
        layout.addStretch()
        return widget
        
    def create_advanced_tab(self):
        """Gelişmiş ayarlar sekmesi"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Performans ayarları
        performance_group = QGroupBox("Performans")
        performance_layout = QGridLayout(performance_group)
        
        performance_layout.addWidget(QLabel("Maksimum dosya boyutu (MB):"), 0, 0)
        self.max_file_size = QSpinBox()
        self.max_file_size.setRange(1, 1000)
        self.max_file_size.setValue(100)
        performance_layout.addWidget(self.max_file_size, 0, 1)
        
        performance_layout.addWidget(QLabel("Maksimum sekme sayısı:"), 1, 0)
        self.max_tabs = QSpinBox()
        self.max_tabs.setRange(1, 50)
        self.max_tabs.setValue(20)
        performance_layout.addWidget(self.max_tabs, 1, 1)
        
        layout.addWidget(performance_group)
        
        # Geçmiş ayarları
        history_group = QGroupBox("Geçmiş")
        history_layout = QGridLayout(history_group)
        
        self.keep_history = QCheckBox("Düzenleme geçmişini sakla")
        history_layout.addWidget(self.keep_history, 0, 0, 1, 2)
        
        history_layout.addWidget(QLabel("Geçmiş gün sayısı:"), 1, 0)
        self.history_days = QSpinBox()
        self.history_days.setRange(1, 365)
        self.history_days.setValue(30)
        history_layout.addWidget(self.history_days, 1, 1)
        
        layout.addWidget(history_group)
        
        # Debug ayarları
        debug_group = QGroupBox("Debug")
        debug_layout = QGridLayout(debug_group)
        
        self.enable_logging = QCheckBox("Logging'i etkinleştir")
        debug_layout.addWidget(self.enable_logging, 0, 0, 1, 2)
        
        self.log_level = QComboBox()
        self.log_level.addItems(["INFO", "DEBUG", "WARNING", "ERROR"])
        debug_layout.addWidget(QLabel("Log seviyesi:"), 1, 0)
        debug_layout.addWidget(self.log_level, 1, 1)
        
        layout.addWidget(debug_group)
        
        # Ayarları sıfırla
        self.reset_button = QPushButton("Ayarları Sıfırla")
        self.reset_button.clicked.connect(self.reset_settings)
        layout.addWidget(self.reset_button)
        
        layout.addStretch()
        return widget
        
    def select_font(self):
        """Font seç"""
        font, ok = QFontDialog.getFont()
        if ok:
            self.font_preview.setText(f"{font.family()}, {font.pointSize()}pt")
            self.font_preview.setFont(font)
            
    def browse_sync_folder(self):
        """Senkronizasyon klasörü seç"""
        from PyQt6.QtWidgets import QFileDialog
        folder = QFileDialog.getExistingDirectory(self, "Senkronizasyon Klasörü Seç")
        if folder:
            self.sync_folder_edit.setText(folder)
            
    def test_connection(self):
        """Cloud bağlantısını test et"""
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.information(self, "Test", "Cloud bağlantısı test ediliyor...")
        
    def reset_settings(self):
        """Ayarları sıfırla"""
        from PyQt6.QtWidgets import QMessageBox
        reply = QMessageBox.question(
            self, "Ayarları Sıfırla",
            "Tüm ayarları varsayılan değerlere sıfırlamak istediğinizden emin misiniz?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.settings.clear()
            self.load_settings()
            
    def load_settings(self):
        """Ayarları yükle"""
        # Genel ayarlar
        theme = self.settings.value('theme', 'Açık')
        self.theme_combo.setCurrentText(theme)
        
        language = self.settings.value('language', 'Türkçe')
        self.language_combo.setCurrentText(language)
        
        self.startup_new_file.setChecked(self.settings.value('startup_new_file', True, type=bool))
        self.remember_files.setChecked(self.settings.value('remember_files', True, type=bool))
        self.max_recent_files.setValue(int(self.settings.value('max_recent_files', 10)))
        
        # Editör ayarları
        font_family = self.settings.value('font_family', 'Consolas')
        font_size = int(self.settings.value('font_size', 12))
        font = QFont(font_family, font_size)
        self.font_preview.setText(f"{font.family()}, {font.pointSize()}pt")
        self.font_preview.setFont(font)
        
        self.show_line_numbers.setChecked(self.settings.value('show_line_numbers', True, type=bool))
        self.show_whitespace.setChecked(self.settings.value('show_whitespace', False, type=bool))
        self.word_wrap.setChecked(self.settings.value('word_wrap', False, type=bool))
        self.auto_indent.setChecked(self.settings.value('auto_indent', True, type=bool))
        self.syntax_highlighting.setChecked(self.settings.value('syntax_highlighting', True, type=bool))
        
        self.enable_autosave.setChecked(self.settings.value('enable_autosave', True, type=bool))
        self.autosave_interval.setValue(int(self.settings.value('autosave_interval', 300)))
        
        # Cloud ayarları
        cloud_service = self.settings.value('cloud_service', 'Local Sync')
        self.cloud_service.setCurrentText(cloud_service)
        
        self.api_key_edit.setText(self.settings.value('api_key', ''))
        self.sync_folder_edit.setText(self.settings.value('sync_folder', ''))
        
        self.auto_sync.setChecked(self.settings.value('auto_sync', False, type=bool))
        self.sync_interval.setValue(int(self.settings.value('sync_interval', 30)))
        self.sync_on_startup.setChecked(self.settings.value('sync_on_startup', False, type=bool))
        self.sync_on_save.setChecked(self.settings.value('sync_on_save', False, type=bool))
        
        # Gelişmiş ayarlar
        self.max_file_size.setValue(int(self.settings.value('max_file_size', 100)))
        self.max_tabs.setValue(int(self.settings.value('max_tabs', 20)))
        
        self.keep_history.setChecked(self.settings.value('keep_history', True, type=bool))
        self.history_days.setValue(int(self.settings.value('history_days', 30)))
        
        self.enable_logging.setChecked(self.settings.value('enable_logging', False, type=bool))
        log_level = self.settings.value('log_level', 'INFO')
        self.log_level.setCurrentText(log_level)
        
    def save_settings(self):
        """Ayarları kaydet"""
        # Genel ayarlar
        self.settings.setValue('theme', self.theme_combo.currentText())
        self.settings.setValue('language', self.language_combo.currentText())
        self.settings.setValue('startup_new_file', self.startup_new_file.isChecked())
        self.settings.setValue('remember_files', self.remember_files.isChecked())
        self.settings.setValue('max_recent_files', self.max_recent_files.value())
        
        # Editör ayarları
        font = self.font_preview.font()
        self.settings.setValue('font_family', font.family())
        self.settings.setValue('font_size', font.pointSize())
        
        self.settings.setValue('show_line_numbers', self.show_line_numbers.isChecked())
        self.settings.setValue('show_whitespace', self.show_whitespace.isChecked())
        self.settings.setValue('word_wrap', self.word_wrap.isChecked())
        self.settings.setValue('auto_indent', self.auto_indent.isChecked())
        self.settings.setValue('syntax_highlighting', self.syntax_highlighting.isChecked())
        
        self.settings.setValue('enable_autosave', self.enable_autosave.isChecked())
        self.settings.setValue('autosave_interval', self.autosave_interval.value())
        
        # Cloud ayarları
        self.settings.setValue('cloud_service', self.cloud_service.currentText())
        self.settings.setValue('api_key', self.api_key_edit.text())
        self.settings.setValue('sync_folder', self.sync_folder_edit.text())
        
        self.settings.setValue('auto_sync', self.auto_sync.isChecked())
        self.settings.setValue('sync_interval', self.sync_interval.value())
        self.settings.setValue('sync_on_startup', self.sync_on_startup.isChecked())
        self.settings.setValue('sync_on_save', self.sync_on_save.isChecked())
        
        # Gelişmiş ayarlar
        self.settings.setValue('max_file_size', self.max_file_size.value())
        self.settings.setValue('max_tabs', self.max_tabs.value())
        
        self.settings.setValue('keep_history', self.keep_history.isChecked())
        self.settings.setValue('history_days', self.history_days.value())
        
        self.settings.setValue('enable_logging', self.enable_logging.isChecked())
        self.settings.setValue('log_level', self.log_level.currentText())
        
        self.settings.sync()
        
    def apply_settings(self):
        """Ayarları uygula"""
        self.save_settings()
        
        # Ana pencereye ayarları uygula
        if self.parent:
            self.parent.load_settings()
            
    def accept(self):
        """Tamam butonuna basıldığında"""
        self.save_settings()
        super().accept() 