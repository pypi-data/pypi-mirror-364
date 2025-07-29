"""
PyCloud OS Rain Widgets
Kullanıcının masaüstüne etkileşimli widget'lar eklemesini sağlayan sistem
"""

import os
import json
import logging
import threading
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum

try:
    from PyQt6.QtWidgets import (QWidget, QLabel, QVBoxLayout, QHBoxLayout, 
                                QPushButton, QFrame, QScrollArea, QGridLayout,
                                QSlider, QSpinBox, QComboBox, QTextEdit, QProgressBar)
    from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal, QRect, QPoint, QSize
    from PyQt6.QtGui import QFont, QPixmap, QPainter, QColor, QPalette
    PYQT_AVAILABLE = True
except ImportError:
    PYQT_AVAILABLE = False

class WidgetType(Enum):
    """Widget türleri"""
    CLOCK = "clock"
    CALENDAR = "calendar"
    WEATHER = "weather"
    SYSTEM_INFO = "system_info"
    CPU_MONITOR = "cpu_monitor"
    MEMORY_MONITOR = "memory_monitor"
    NOTES = "notes"
    CALCULATOR = "calculator"
    RSS_READER = "rss_reader"
    TODO_LIST = "todo_list"

class WidgetState(Enum):
    """Widget durumları"""
    ACTIVE = "active"
    MINIMIZED = "minimized"
    HIDDEN = "hidden"
    LOADING = "loading"
    ERROR = "error"

@dataclass
class WidgetConfig:
    """Widget yapılandırması"""
    widget_id: str
    widget_type: WidgetType
    title: str
    position: tuple = (100, 100)
    size: tuple = (200, 150)
    state: WidgetState = WidgetState.ACTIVE
    settings: Dict = None
    refresh_interval: int = 30  # saniye
    always_on_top: bool = False
    transparency: float = 1.0
    theme: str = "auto"
    
    def __post_init__(self):
        if self.settings is None:
            self.settings = {}
    
    def to_dict(self) -> Dict:
        """Dict'e çevir"""
        data = asdict(self)
        data['widget_type'] = self.widget_type.value
        data['state'] = self.state.value
        return data
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'WidgetConfig':
        """Dict'ten oluştur"""
        data['widget_type'] = WidgetType(data.get('widget_type', 'clock'))
        data['state'] = WidgetState(data.get('state', 'active'))
        return cls(**data)

class BaseWidget(QWidget if PYQT_AVAILABLE else object):
    """Temel widget sınıfı"""
    
    def __init__(self, config: WidgetConfig, widget_manager=None):
        if PYQT_AVAILABLE:
            super().__init__()
        
        self.config = config
        self.widget_manager = widget_manager
        self.logger = logging.getLogger(f"Widget-{config.widget_id}")
        
        # Widget durumu
        self.is_running = False
        self.last_update = None
        self.update_timer = None
        self.data_sources = {}
        
        # UI bileşenleri
        if PYQT_AVAILABLE:
            self.init_ui()
            self.setup_timer()
    
    def init_ui(self):
        """UI'yı başlat"""
        self.setWindowTitle(self.config.title)
        self.setGeometry(*self.config.position, *self.config.size)
        
        # Ana layout
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        
        # Başlık çubuğu
        self.title_bar = self.create_title_bar()
        self.layout.addWidget(self.title_bar)
        
        # İçerik alanı
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout()
        self.content_widget.setLayout(self.content_layout)
        self.layout.addWidget(self.content_widget)
        
        # Widget-specific UI
        self.setup_content()
        
        # Stil uygula
        self.apply_theme()
    
    def create_title_bar(self) -> QWidget:
        """Başlık çubuğu oluştur"""
        title_bar = QFrame()
        title_bar.setFixedHeight(30)
        title_bar.setStyleSheet("background-color: #2b2b2b; border-radius: 5px;")
        
        layout = QHBoxLayout()
        layout.setContentsMargins(5, 0, 5, 0)
        
        # Başlık
        title_label = QLabel(self.config.title)
        title_label.setStyleSheet("color: white; font-weight: bold;")
        layout.addWidget(title_label)
        
        layout.addStretch()
        
        # Ayarlar butonu
        settings_btn = QPushButton("⚙")
        settings_btn.setFixedSize(20, 20)
        settings_btn.setStyleSheet("background-color: #404040; border: none; color: white;")
        settings_btn.clicked.connect(self.show_settings)
        layout.addWidget(settings_btn)
        
        # Kapat butonu
        close_btn = QPushButton("✕")
        close_btn.setFixedSize(20, 20)
        close_btn.setStyleSheet("background-color: #ff5555; border: none; color: white;")
        close_btn.clicked.connect(self.close_widget)
        layout.addWidget(close_btn)
        
        title_bar.setLayout(layout)
        return title_bar
    
    def setup_content(self):
        """Widget içeriğini ayarla (alt sınıflarda override edilir)"""
        label = QLabel("Temel Widget")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.content_layout.addWidget(label)
    
    def setup_timer(self):
        """Güncelleme timer'ını ayarla"""
        if self.config.refresh_interval > 0:
            self.update_timer = QTimer()
            self.update_timer.timeout.connect(self.update_data)
            self.update_timer.start(self.config.refresh_interval * 1000)
    
    def apply_theme(self):
        """Tema uygula"""
        # Temel stil
        style = """
        QWidget {
            background-color: #3c3c3c;
            color: white;
            border: 1px solid #555;
            border-radius: 8px;
        }
        QLabel {
            border: none;
            padding: 2px;
        }
        """
        
        if self.config.transparency < 1.0:
            self.setWindowOpacity(self.config.transparency)
        
        self.setStyleSheet(style)
    
    def update_data(self):
        """Veriyi güncelle"""
        try:
            self.last_update = datetime.now()
            # Alt sınıflarda implement edilir
            self.on_data_update()
        except Exception as e:
            self.logger.error(f"Data update error: {e}")
    
    def on_data_update(self):
        """Veri güncellemesi (alt sınıflarda override edilir)"""
        pass
    
    def show_settings(self):
        """Ayarları göster"""
        if self.widget_manager:
            self.widget_manager.show_widget_settings(self.config.widget_id)
    
    def close_widget(self):
        """Widget'ı kapat"""
        if self.widget_manager:
            self.widget_manager.remove_widget(self.config.widget_id)
        self.close()
    
    def get_settings_schema(self) -> Dict:
        """Ayar şemasını döndür"""
        return {
            "refresh_interval": {
                "type": "int",
                "label": "Yenileme Aralığı (saniye)",
                "default": 30,
                "min": 5,
                "max": 3600
            },
            "transparency": {
                "type": "float",
                "label": "Şeffaflık",
                "default": 1.0,
                "min": 0.1,
                "max": 1.0
            }
        }
    
    def apply_settings(self, settings: Dict):
        """Ayarları uygula"""
        if "refresh_interval" in settings:
            self.config.refresh_interval = settings["refresh_interval"]
            if self.update_timer:
                self.update_timer.setInterval(self.config.refresh_interval * 1000)
        
        if "transparency" in settings:
            self.config.transparency = settings["transparency"]
            self.setWindowOpacity(self.config.transparency)

class ClockWidget(BaseWidget):
    """Saat widget'ı"""
    
    def setup_content(self):
        """Saat içeriğini ayarla"""
        self.time_label = QLabel()
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.time_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        self.content_layout.addWidget(self.time_label)
        
        self.date_label = QLabel()
        self.date_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.date_label.setFont(QFont("Arial", 10))
        self.content_layout.addWidget(self.date_label)
    
    def on_data_update(self):
        """Saat verilerini güncelle"""
        now = datetime.now()
        
        # Locale manager'dan format al
        if self.widget_manager and self.widget_manager.kernel:
            locale_manager = self.widget_manager.kernel.get_module("locale")
            if locale_manager:
                time_str = locale_manager.format_time(now)
                date_str = locale_manager.format_date(now)
            else:
                time_str = now.strftime("%H:%M")
                date_str = now.strftime("%d.%m.%Y")
        else:
            time_str = now.strftime("%H:%M")
            date_str = now.strftime("%d.%m.%Y")
        
        self.time_label.setText(time_str)
        self.date_label.setText(date_str)

class SystemInfoWidget(BaseWidget):
    """Sistem bilgisi widget'ı"""
    
    def setup_content(self):
        """Sistem bilgisi içeriğini ayarla"""
        self.cpu_label = QLabel("CPU: -")
        self.memory_label = QLabel("RAM: -")
        self.uptime_label = QLabel("Uptime: -")
        
        for label in [self.cpu_label, self.memory_label, self.uptime_label]:
            label.setFont(QFont("Arial", 9))
            self.content_layout.addWidget(label)
    
    def on_data_update(self):
        """Sistem bilgilerini güncelle"""
        try:
            if self.widget_manager and self.widget_manager.kernel:
                # CPU bilgisi
                process_manager = self.widget_manager.kernel.get_module("process")
                if process_manager:
                    cpu_percent = process_manager.get_system_cpu_usage()
                    self.cpu_label.setText(f"CPU: {cpu_percent:.1f}%")
                
                # Bellek bilgisi
                memory_manager = self.widget_manager.kernel.get_module("memory")
                if memory_manager:
                    memory_info = memory_manager.get_memory_info()
                    used_mb = memory_info.get("used_mb", 0)
                    total_mb = memory_info.get("total_mb", 0)
                    percent = (used_mb / total_mb * 100) if total_mb > 0 else 0
                    self.memory_label.setText(f"RAM: {percent:.1f}% ({used_mb:.0f}MB)")
                
                # Uptime
                uptime = self.widget_manager.kernel.get_uptime()
                hours = int(uptime // 3600)
                minutes = int((uptime % 3600) // 60)
                self.uptime_label.setText(f"Uptime: {hours:02d}:{minutes:02d}")
                
        except Exception as e:
            self.logger.error(f"System info update error: {e}")

class NotesWidget(BaseWidget):
    """Not widget'ı"""
    
    def setup_content(self):
        """Not içeriğini ayarla"""
        self.notes_edit = QTextEdit()
        self.notes_edit.setPlaceholderText("Notlarınızı buraya yazın...")
        self.notes_edit.textChanged.connect(self.save_notes)
        self.content_layout.addWidget(self.notes_edit)
        
        # Kayıtlı notları yükle
        self.load_notes()
    
    def load_notes(self):
        """Notları yükle"""
        notes_file = Path(f"users/widgets/{self.config.widget_id}.txt")
        if notes_file.exists():
            try:
                with open(notes_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    self.notes_edit.setPlainText(content)
            except Exception as e:
                self.logger.error(f"Failed to load notes: {e}")
    
    def save_notes(self):
        """Notları kaydet"""
        notes_file = Path(f"users/widgets/{self.config.widget_id}.txt")
        notes_file.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(notes_file, 'w', encoding='utf-8') as f:
                f.write(self.notes_edit.toPlainText())
        except Exception as e:
            self.logger.error(f"Failed to save notes: {e}")

class WeatherWidget(BaseWidget):
    """Hava durumu widget'ı"""
    
    def setup_content(self):
        """Hava durumu içeriğini ayarla"""
        self.location_label = QLabel("📍 Konum belirsiz")
        self.temp_label = QLabel("🌡️ --°C")
        self.condition_label = QLabel("☁️ Bekleniyor...")
        
        for label in [self.location_label, self.temp_label, self.condition_label]:
            label.setFont(QFont("Arial", 9))
            self.content_layout.addWidget(label)
    
    def on_data_update(self):
        """Hava durumu verilerini güncelle (demo)"""
        # Demo veri (gerçek API entegrasyonu yapılabilir)
        import random
        temp = random.randint(15, 35)
        conditions = ["☀️ Güneşli", "☁️ Bulutlu", "🌧️ Yağmurlu", "❄️ Karlı"]
        condition = random.choice(conditions)
        
        self.location_label.setText("📍 İstanbul")
        self.temp_label.setText(f"🌡️ {temp}°C")
        self.condition_label.setText(condition)

class WidgetFactory:
    """Widget fabrikası"""
    
    @staticmethod
    def create_widget(config: WidgetConfig, widget_manager=None) -> Optional[BaseWidget]:
        """Widget oluştur"""
        if not PYQT_AVAILABLE:
            return None
        
        widget_classes = {
            WidgetType.CLOCK: ClockWidget,
            WidgetType.SYSTEM_INFO: SystemInfoWidget,
            WidgetType.NOTES: NotesWidget,
            WidgetType.WEATHER: WeatherWidget,
        }
        
        widget_class = widget_classes.get(config.widget_type)
        if widget_class:
            return widget_class(config, widget_manager)
        
        return None

class WidgetManager:
    """Widget yöneticisi"""
    
    def __init__(self, kernel=None):
        self.kernel = kernel
        self.logger = logging.getLogger("WidgetManager")
        
        # Widget verileri
        self.widgets: Dict[str, BaseWidget] = {}
        self.widget_configs: Dict[str, WidgetConfig] = {}
        
        # Dosya yolları
        self.widgets_dir = Path("users/widgets")
        self.widgets_dir.mkdir(parents=True, exist_ok=True)
        self.config_file = self.widgets_dir / "widgets.json"
        
        # Widget ayarları
        self.max_widgets = 20
        self.default_refresh_interval = 30
        
        # Başlangıç
        self.load_widget_configs()
        self.restore_widgets()
    
    def create_widget(self, widget_type: WidgetType, title: str = None, 
                     position: tuple = None, **kwargs) -> Optional[str]:
        """Yeni widget oluştur"""
        try:
            if len(self.widgets) >= self.max_widgets:
                self.logger.warning("Maximum widget limit reached")
                return None
            
            # Widget ID oluştur
            import uuid
            widget_id = str(uuid.uuid4())[:8]
            
            # Varsayılan değerler
            if title is None:
                title = widget_type.value.replace("_", " ").title()
            
            if position is None:
                position = (100 + len(self.widgets) * 50, 100 + len(self.widgets) * 50)
            
            # Konfigürasyon oluştur
            config = WidgetConfig(
                widget_id=widget_id,
                widget_type=widget_type,
                title=title,
                position=position,
                **kwargs
            )
            
            # Widget oluştur
            widget = WidgetFactory.create_widget(config, self)
            if not widget:
                self.logger.error(f"Failed to create widget: {widget_type}")
                return None
            
            # Kaydet
            self.widgets[widget_id] = widget
            self.widget_configs[widget_id] = config
            self.save_widget_configs()
            
            # Göster
            widget.show()
            widget.update_data()
            
            self.logger.info(f"Widget created: {widget_id} ({widget_type.value})")
            return widget_id
            
        except Exception as e:
            self.logger.error(f"Failed to create widget: {e}")
            return None
    
    def remove_widget(self, widget_id: str) -> bool:
        """Widget'ı kaldır"""
        try:
            if widget_id not in self.widgets:
                return False
            
            # Widget'ı kapat
            widget = self.widgets[widget_id]
            if hasattr(widget, 'update_timer') and widget.update_timer:
                widget.update_timer.stop()
            
            widget.close()
            
            # Veriyi temizle
            del self.widgets[widget_id]
            del self.widget_configs[widget_id]
            
            # Widget dosyasını sil
            widget_file = self.widgets_dir / f"{widget_id}.txt"
            if widget_file.exists():
                widget_file.unlink()
            
            self.save_widget_configs()
            
            self.logger.info(f"Widget removed: {widget_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to remove widget {widget_id}: {e}")
            return False
    
    def get_widget(self, widget_id: str) -> Optional[BaseWidget]:
        """Widget'ı al"""
        return self.widgets.get(widget_id)
    
    def list_widgets(self) -> List[Dict]:
        """Widget listesi"""
        return [config.to_dict() for config in self.widget_configs.values()]
    
    def update_widget_config(self, widget_id: str, **kwargs) -> bool:
        """Widget konfigürasyonunu güncelle"""
        try:
            if widget_id not in self.widget_configs:
                return False
            
            config = self.widget_configs[widget_id]
            
            # Güncelle
            for key, value in kwargs.items():
                if hasattr(config, key):
                    setattr(config, key, value)
            
            # Widget'a uygula
            if widget_id in self.widgets:
                widget = self.widgets[widget_id]
                if hasattr(widget, 'apply_settings'):
                    widget.apply_settings(kwargs)
            
            self.save_widget_configs()
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to update widget config {widget_id}: {e}")
            return False
    
    def show_widget_settings(self, widget_id: str):
        """Widget ayarlarını göster"""
        # Bu bir dialog açacak (widget ayar penceresi)
        self.logger.info(f"Opening settings for widget: {widget_id}")
        # TODO: Ayar dialogu implementasyonu
    
    def save_widget_configs(self):
        """Widget konfigürasyonlarını kaydet"""
        try:
            configs_data = {
                widget_id: config.to_dict() 
                for widget_id, config in self.widget_configs.items()
            }
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(configs_data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            self.logger.error(f"Failed to save widget configs: {e}")
    
    def load_widget_configs(self):
        """Widget konfigürasyonlarını yükle"""
        try:
            if not self.config_file.exists():
                return
            
            with open(self.config_file, 'r', encoding='utf-8') as f:
                configs_data = json.load(f)
            
            for widget_id, config_data in configs_data.items():
                try:
                    config = WidgetConfig.from_dict(config_data)
                    self.widget_configs[widget_id] = config
                except Exception as e:
                    self.logger.error(f"Failed to load widget config {widget_id}: {e}")
            
            self.logger.info(f"Loaded {len(self.widget_configs)} widget configurations")
            
        except Exception as e:
            self.logger.error(f"Failed to load widget configs: {e}")
    
    def restore_widgets(self):
        """Widget'ları geri yükle"""
        try:
            for widget_id, config in self.widget_configs.items():
                if config.state == WidgetState.ACTIVE:
                    widget = WidgetFactory.create_widget(config, self)
                    if widget:
                        self.widgets[widget_id] = widget
                        widget.show()
                        widget.update_data()
            
            self.logger.info(f"Restored {len(self.widgets)} widgets")
            
        except Exception as e:
            self.logger.error(f"Failed to restore widgets: {e}")
    
    def get_available_widget_types(self) -> List[Dict]:
        """Mevcut widget türleri"""
        return [
            {
                "type": WidgetType.CLOCK.value,
                "name": "Saat",
                "description": "Dijital saat ve tarih göstergesi",
                "icon": "🕐"
            },
            {
                "type": WidgetType.SYSTEM_INFO.value,
                "name": "Sistem Bilgisi",
                "description": "CPU, RAM ve uptime izleme",
                "icon": "💻"
            },
            {
                "type": WidgetType.WEATHER.value,
                "name": "Hava Durumu",
                "description": "Anlık hava durumu bilgisi",
                "icon": "🌤️"
            },
            {
                "type": WidgetType.NOTES.value,
                "name": "Notlar",
                "description": "Hızlı not alma aracı",
                "icon": "📝"
            }
        ]
    
    def hide_all_widgets(self):
        """Tüm widget'ları gizle"""
        for widget in self.widgets.values():
            widget.hide()
    
    def show_all_widgets(self):
        """Tüm widget'ları göster"""
        for widget in self.widgets.values():
            widget.show()
    
    def refresh_all_widgets(self):
        """Tüm widget'ları yenile"""
        for widget in self.widgets.values():
            widget.update_data()
    
    def shutdown(self):
        """Widget manager'ı kapat"""
        try:
            # Tüm widget'ları kapat
            for widget_id in list(self.widgets.keys()):
                self.remove_widget(widget_id)
            
            # Konfigürasyonları kaydet
            self.save_widget_configs()
            
            self.logger.info("Widget manager shutdown completed")
            
        except Exception as e:
            self.logger.error(f"Widget manager shutdown failed: {e}")

# Kolaylık fonksiyonları
_widget_manager = None

def init_widget_manager(kernel=None) -> WidgetManager:
    """Widget manager'ı başlat"""
    global _widget_manager
    _widget_manager = WidgetManager(kernel)
    return _widget_manager

def get_widget_manager() -> Optional[WidgetManager]:
    """Widget manager'ı al"""
    return _widget_manager

def create_widget(widget_type: str, **kwargs) -> Optional[str]:
    """Widget oluştur (kısayol)"""
    if _widget_manager:
        try:
            widget_type_enum = WidgetType(widget_type)
            return _widget_manager.create_widget(widget_type_enum, **kwargs)
        except ValueError:
            return None
    return None

def remove_widget(widget_id: str) -> bool:
    """Widget kaldır (kısayol)"""
    if _widget_manager:
        return _widget_manager.remove_widget(widget_id)
    return False 