"""
PyCloud OS Rain Theme
Arayüz bileşenleri için görsel temalar ve ikon paketleri yönetimi
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from enum import Enum

try:
    from PyQt6.QtGui import QColor, QPalette, QFont, QPixmap, QIcon
    from PyQt6.QtCore import Qt
    from PyQt6.QtWidgets import QApplication
    PYQT_AVAILABLE = True
except ImportError:
    PYQT_AVAILABLE = False

class ThemeMode(Enum):
    """Tema modları"""
    LIGHT = "light"
    DARK = "dark"
    AUTO = "auto"

class IconTheme(Enum):
    """İkon temaları"""
    SYSTEM = "system"
    FLAT = "flat"
    MODERN = "modern"
    CLASSIC = "classic"

@dataclass
class ColorScheme:
    """Renk şeması"""
    primary: str = "#2196F3"
    secondary: str = "#FFC107"
    success: str = "#4CAF50"
    warning: str = "#FF9800"
    error: str = "#F44336"
    info: str = "#00BCD4"
    
    # Arka plan renkleri
    background: str = "#FFFFFF"
    surface: str = "#F5F5F5"
    card: str = "#FFFFFF"
    
    # Metin renkleri
    text_primary: str = "#212121"
    text_secondary: str = "#757575"
    text_disabled: str = "#BDBDBD"
    
    # Sınır ve ayırıcı renkleri
    border: str = "#E0E0E0"
    divider: str = "#E0E0E0"
    
    def to_dict(self) -> Dict:
        """Dict'e çevir"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'ColorScheme':
        """Dict'ten oluştur"""
        return cls(**data)

@dataclass
class ThemeConfig:
    """Tema yapılandırması"""
    name: str
    display_name: str
    mode: ThemeMode
    colors: ColorScheme
    fonts: Dict[str, str] = None
    borders: Dict[str, str] = None
    shadows: Dict[str, str] = None
    animations: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.fonts is None:
            self.fonts = {
                "default": "Arial",
                "heading": "Arial",
                "monospace": "Courier New",
                "size_small": "9",
                "size_normal": "10",
                "size_large": "12",
                "size_heading": "14"
            }
        
        if self.borders is None:
            self.borders = {
                "radius": "4px",
                "width": "1px",
                "style": "solid"
            }
        
        if self.shadows is None:
            self.shadows = {
                "small": "0 1px 3px rgba(0,0,0,0.12)",
                "medium": "0 4px 6px rgba(0,0,0,0.15)",
                "large": "0 10px 20px rgba(0,0,0,0.19)"
            }
        
        if self.animations is None:
            self.animations = {
                "duration_fast": 150,
                "duration_normal": 250,
                "duration_slow": 400,
                "easing": "ease-in-out"
            }
    
    def to_dict(self) -> Dict:
        """Dict'e çevir"""
        data = asdict(self)
        data['mode'] = self.mode.value
        data['colors'] = self.colors.to_dict()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'ThemeConfig':
        """Dict'ten oluştur"""
        data['mode'] = ThemeMode(data.get('mode', 'auto'))
        data['colors'] = ColorScheme.from_dict(data.get('colors', {}))
        return cls(**data)

class IconManager:
    """İkon yöneticisi"""
    
    def __init__(self, theme_manager=None):
        self.theme_manager = theme_manager
        self.logger = logging.getLogger("IconManager")
        
        # İkon dizinleri
        self.system_icons_dir = Path("system/icons")
        self.user_icons_dir = Path("users/icons")
        self.system_icons_dir.mkdir(parents=True, exist_ok=True)
        self.user_icons_dir.mkdir(parents=True, exist_ok=True)
        
        # İkon cache
        self.icon_cache: Dict[str, Any] = {}
        self.icon_mappings: Dict[str, str] = {}
        
        # Mevcut tema
        self.current_theme = IconTheme.SYSTEM
        
        # Başlangıç
        self.load_icon_mappings()
        self.create_default_icons()
    
    def load_icon_mappings(self):
        """İkon eşleştirmelerini yükle"""
        try:
            mappings_file = self.system_icons_dir / "mappings.json"
            
            if mappings_file.exists():
                with open(mappings_file, 'r', encoding='utf-8') as f:
                    self.icon_mappings = json.load(f)
            else:
                self.create_default_mappings()
                
        except Exception as e:
            self.logger.error(f"Failed to load icon mappings: {e}")
    
    def create_default_mappings(self):
        """Varsayılan ikon eşleştirmeleri oluştur"""
        default_mappings = {
            # Dosya türleri
            "file.txt": "📄",
            "file.py": "🐍",
            "file.js": "📜",
            "file.html": "🌐",
            "file.css": "🎨",
            "file.json": "📋",
            "file.md": "📝",
            "file.pdf": "📕",
            "file.doc": "📘",
            "file.xls": "📊",
            "file.zip": "📦",
            "file.rar": "📦",
            "file.exe": "⚙️",
            "file.app": "📱",
            "file.dmg": "💿",
            "file.iso": "💿",
            
            # Klasörler
            "folder": "📁",
            "folder.open": "📂",
            "folder.home": "🏠",
            "folder.documents": "📑",
            "folder.downloads": "⬇️",
            "folder.pictures": "🖼️",
            "folder.music": "🎵",
            "folder.videos": "🎬",
            "folder.desktop": "🖥️",
            "folder.trash": "🗑️",
            
            # Uygulamalar
            "app.files": "📁",
            "app.terminal": "💻",
            "app.settings": "⚙️",
            "app.browser": "🌐",
            "app.editor": "📝",
            "app.calculator": "🔢",
            "app.calendar": "📅",
            "app.clock": "🕐",
            "app.notes": "📓",
            "app.weather": "🌤️",
            
            # Sistem
            "system.warning": "⚠️",
            "system.error": "❌",
            "system.info": "ℹ️",
            "system.success": "✅",
            "system.loading": "⏳",
            "system.refresh": "🔄",
            "system.search": "🔍",
            "system.menu": "☰",
            "system.close": "✕",
            "system.minimize": "−",
            "system.maximize": "□",
            
            # Eylemler
            "action.copy": "📋",
            "action.cut": "✂️",
            "action.paste": "📄",
            "action.delete": "🗑️",
            "action.rename": "✏️",
            "action.new": "📄",
            "action.save": "💾",
            "action.open": "📂",
            "action.print": "🖨️",
            "action.share": "📤",
            
            # Navigasyon
            "nav.back": "⬅️",
            "nav.forward": "➡️",
            "nav.up": "⬆️",
            "nav.down": "⬇️",
            "nav.home": "🏠",
            "nav.refresh": "🔄",
        }
        
        try:
            mappings_file = self.system_icons_dir / "mappings.json"
            with open(mappings_file, 'w', encoding='utf-8') as f:
                json.dump(default_mappings, f, indent=2, ensure_ascii=False)
            
            self.icon_mappings = default_mappings
            self.logger.info("Default icon mappings created")
            
        except Exception as e:
            self.logger.error(f"Failed to create default mappings: {e}")
    
    def create_default_icons(self):
        """Varsayılan ikonları oluştur (emoji tabanlı)"""
        # Emoji tabanlı ikonlar zaten mappings'te var
        # Bu metod gelecekte gerçek ikon dosyaları için kullanılabilir
        pass
    
    def get_icon(self, icon_id: str, size: int = 16) -> Any:
        """İkon al"""
        try:
            # Cache'de var mı?
            cache_key = f"{icon_id}_{size}_{self.current_theme.value}"
            if cache_key in self.icon_cache:
                return self.icon_cache[cache_key]
            
            # Emoji ikon
            if icon_id in self.icon_mappings:
                emoji = self.icon_mappings[icon_id]
                
                if PYQT_AVAILABLE:
                    # PyQt6 için emoji'yi QIcon'a çevir
                    pixmap = QPixmap(size, size)
                    pixmap.fill(Qt.GlobalColor.transparent)
                    
                    # Bu basit bir implementasyon, gerçek uygulamada
                    # emoji'yi bitmap'e çeviren bir kütüphane kullanılmalı
                    icon = QIcon()
                    self.icon_cache[cache_key] = icon
                    return icon
                else:
                    # PyQt yok, emoji string döndür
                    self.icon_cache[cache_key] = emoji
                    return emoji
            
            # Dosya ikonu ara
            icon_file = self.get_icon_file(icon_id, size)
            if icon_file and icon_file.exists():
                if PYQT_AVAILABLE:
                    icon = QIcon(str(icon_file))
                    self.icon_cache[cache_key] = icon
                    return icon
                else:
                    self.icon_cache[cache_key] = str(icon_file)
                    return str(icon_file)
            
            # Varsayılan ikon
            default_icon = self.icon_mappings.get("file", "📄")
            self.icon_cache[cache_key] = default_icon
            return default_icon
            
        except Exception as e:
            self.logger.error(f"Failed to get icon {icon_id}: {e}")
            return "📄"  # Varsayılan
    
    def get_icon_file(self, icon_id: str, size: int = 16) -> Optional[Path]:
        """İkon dosya yolunu al"""
        # Theme klasörlerinde ara
        theme_dirs = [
            self.system_icons_dir / self.current_theme.value,
            self.system_icons_dir / "default",
            self.user_icons_dir
        ]
        
        for theme_dir in theme_dirs:
            if not theme_dir.exists():
                continue
            
            # Farklı dosya formatlarını dene
            for ext in ['.png', '.svg', '.ico', '.jpg']:
                icon_file = theme_dir / f"{icon_id}_{size}{ext}"
                if icon_file.exists():
                    return icon_file
                
                # Boyut belirtilmemiş dosya
                icon_file = theme_dir / f"{icon_id}{ext}"
                if icon_file.exists():
                    return icon_file
        
        return None
    
    def get_file_icon(self, file_path: str) -> Any:
        """Dosya tipine göre ikon al"""
        path = Path(file_path)
        
        if path.is_dir():
            # Özel klasör isimleri
            folder_names = {
                "Desktop": "folder.desktop",
                "Documents": "folder.documents",
                "Downloads": "folder.downloads",
                "Pictures": "folder.pictures",
                "Music": "folder.music",
                "Videos": "folder.videos",
                "Trash": "folder.trash"
            }
            
            folder_icon = folder_names.get(path.name, "folder")
            return self.get_icon(folder_icon)
        else:
            # Dosya uzantısına göre
            extension = path.suffix.lower()
            icon_id = f"file{extension}" if extension else "file"
            
            return self.get_icon(icon_id)
    
    def set_icon_theme(self, theme: IconTheme):
        """İkon temasını değiştir"""
        if theme != self.current_theme:
            self.current_theme = theme
            self.icon_cache.clear()  # Cache'i temizle
            self.logger.info(f"Icon theme changed to: {theme.value}")
    
    def add_custom_icon(self, icon_id: str, icon_path: str) -> bool:
        """Özel ikon ekle"""
        try:
            source_path = Path(icon_path)
            if not source_path.exists():
                return False
            
            # Kullanıcı ikon dizinine kopyala
            target_path = self.user_icons_dir / f"{icon_id}{source_path.suffix}"
            
            import shutil
            shutil.copy2(source_path, target_path)
            
            # Cache'i temizle
            cache_keys_to_remove = [key for key in self.icon_cache.keys() 
                                  if key.startswith(icon_id)]
            for key in cache_keys_to_remove:
                del self.icon_cache[key]
            
            self.logger.info(f"Custom icon added: {icon_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to add custom icon {icon_id}: {e}")
            return False

class ThemeManager:
    """Ana tema yöneticisi"""
    
    def __init__(self, kernel=None):
        self.kernel = kernel
        self.logger = logging.getLogger("ThemeManager")
        
        # Tema dizinleri
        self.themes_dir = Path("system/themes")
        self.user_themes_dir = Path("users/themes")
        self.themes_dir.mkdir(parents=True, exist_ok=True)
        self.user_themes_dir.mkdir(parents=True, exist_ok=True)
        
        # Tema verileri
        self.themes: Dict[str, ThemeConfig] = {}
        self.current_theme_name = "dark"
        self.current_mode = ThemeMode.AUTO
        
        # İkon yöneticisi
        self.icon_manager = IconManager(self)
        
        # Tema değişim callback'leri
        self.theme_callbacks: List[Callable] = []
        
        # Başlangıç
        self.create_default_themes()
        self.load_themes()
        self.load_current_theme()
    
    def create_default_themes(self):
        """Varsayılan temaları oluştur"""
        # Koyu tema
        dark_colors = ColorScheme(
            primary="#2196F3",
            secondary="#FFC107",
            success="#4CAF50",
            warning="#FF9800",
            error="#F44336",
            info="#00BCD4",
            background="#1e1e1e",
            surface="#2d2d2d",
            card="#3c3c3c",
            text_primary="#ffffff",
            text_secondary="#b0b0b0",
            text_disabled="#666666",
            border="#555555",
            divider="#444444"
        )
        
        dark_theme = ThemeConfig(
            name="dark",
            display_name="Koyu Tema",
            mode=ThemeMode.DARK,
            colors=dark_colors
        )
        
        # Açık tema
        light_colors = ColorScheme(
            primary="#2196F3",
            secondary="#FFC107",
            success="#4CAF50",
            warning="#FF9800",
            error="#F44336",
            info="#00BCD4",
            background="#ffffff",
            surface="#f5f5f5",
            card="#ffffff",
            text_primary="#212121",
            text_secondary="#757575",
            text_disabled="#bdbdbd",
            border="#e0e0e0",
            divider="#e0e0e0"
        )
        
        light_theme = ThemeConfig(
            name="light",
            display_name="Açık Tema",
            mode=ThemeMode.LIGHT,
            colors=light_colors
        )
        
        # Temaları kaydet
        themes = {"dark": dark_theme, "light": light_theme}
        
        for theme_name, theme in themes.items():
            theme_file = self.themes_dir / f"{theme_name}.json"
            try:
                with open(theme_file, 'w', encoding='utf-8') as f:
                    json.dump(theme.to_dict(), f, indent=2, ensure_ascii=False)
            except Exception as e:
                self.logger.error(f"Failed to save theme {theme_name}: {e}")
    
    def load_themes(self):
        """Temaları yükle"""
        try:
            # Sistem temaları
            for theme_file in self.themes_dir.glob("*.json"):
                try:
                    with open(theme_file, 'r', encoding='utf-8') as f:
                        theme_data = json.load(f)
                    
                    theme = ThemeConfig.from_dict(theme_data)
                    self.themes[theme.name] = theme
                    
                except Exception as e:
                    self.logger.error(f"Failed to load theme {theme_file}: {e}")
            
            # Kullanıcı temaları
            for theme_file in self.user_themes_dir.glob("*.json"):
                try:
                    with open(theme_file, 'r', encoding='utf-8') as f:
                        theme_data = json.load(f)
                    
                    theme = ThemeConfig.from_dict(theme_data)
                    self.themes[theme.name] = theme
                    
                except Exception as e:
                    self.logger.error(f"Failed to load user theme {theme_file}: {e}")
            
            self.logger.info(f"Loaded {len(self.themes)} themes")
            
        except Exception as e:
            self.logger.error(f"Failed to load themes: {e}")
    
    def load_current_theme(self):
        """Mevcut temayı yükle"""
        try:
            if self.kernel:
                config_manager = self.kernel.get_module("config")
                if config_manager:
                    self.current_theme_name = config_manager.get("ui.theme", "dark")
                    mode_str = config_manager.get("ui.theme_mode", "auto")
                    self.current_mode = ThemeMode(mode_str)
            
            # Otomatik mod kontrolü
            if self.current_mode == ThemeMode.AUTO:
                # Sistem saatine göre koyu/açık tema seç
                from datetime import datetime
                hour = datetime.now().hour
                if 6 <= hour <= 18:  # Gündüz
                    auto_theme = "light"
                else:  # Gece
                    auto_theme = "dark"
                
                if auto_theme in self.themes:
                    self.current_theme_name = auto_theme
            
            self.logger.info(f"Current theme: {self.current_theme_name} (mode: {self.current_mode.value})")
            
        except Exception as e:
            self.logger.error(f"Failed to load current theme: {e}")
    
    def get_current_theme(self) -> Optional[ThemeConfig]:
        """Mevcut temayı al"""
        return self.themes.get(self.current_theme_name)
    
    def set_theme(self, theme_name: str, save: bool = True) -> bool:
        """Tema değiştir"""
        try:
            if theme_name not in self.themes:
                self.logger.warning(f"Theme not found: {theme_name}")
                return False
            
            old_theme = self.current_theme_name
            self.current_theme_name = theme_name
            
            # Config'e kaydet
            if save and self.kernel:
                config_manager = self.kernel.get_module("config")
                if config_manager:
                    config_manager.set("ui.theme", theme_name)
            
            # Tema uygula
            self.apply_current_theme()
            
            # Callback'leri çağır
            self.call_theme_callbacks(old_theme, theme_name)
            
            self.logger.info(f"Theme changed from {old_theme} to {theme_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to set theme {theme_name}: {e}")
            return False
    
    def set_theme_mode(self, mode: ThemeMode, save: bool = True) -> bool:
        """Tema modunu değiştir"""
        try:
            old_mode = self.current_mode
            self.current_mode = mode
            
            # Config'e kaydet
            if save and self.kernel:
                config_manager = self.kernel.get_module("config")
                if config_manager:
                    config_manager.set("ui.theme_mode", mode.value)
            
            # Mevcut temayı yeniden yükle
            self.load_current_theme()
            self.apply_current_theme()
            
            self.logger.info(f"Theme mode changed from {old_mode.value} to {mode.value}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to set theme mode {mode.value}: {e}")
            return False
    
    def apply_current_theme(self):
        """Mevcut temayı uygula"""
        try:
            theme = self.get_current_theme()
            if not theme or not PYQT_AVAILABLE:
                return
            
            app = QApplication.instance()
            if not app:
                return
            
            # Renk paleti oluştur
            palette = QPalette()
            
            # Ana renkler
            palette.setColor(QPalette.ColorRole.Window, QColor(theme.colors.background))
            palette.setColor(QPalette.ColorRole.WindowText, QColor(theme.colors.text_primary))
            palette.setColor(QPalette.ColorRole.Base, QColor(theme.colors.surface))
            palette.setColor(QPalette.ColorRole.AlternateBase, QColor(theme.colors.card))
            palette.setColor(QPalette.ColorRole.Text, QColor(theme.colors.text_primary))
            palette.setColor(QPalette.ColorRole.Button, QColor(theme.colors.surface))
            palette.setColor(QPalette.ColorRole.ButtonText, QColor(theme.colors.text_primary))
            palette.setColor(QPalette.ColorRole.Highlight, QColor(theme.colors.primary))
            palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#ffffff"))
            
            # Devre dışı renkler
            palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, QColor(theme.colors.text_disabled))
            palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, QColor(theme.colors.text_disabled))
            
            # Paleti uygula
            app.setPalette(palette)
            
            # Global stylesheet
            stylesheet = self.generate_stylesheet(theme)
            app.setStyleSheet(stylesheet)
            
            self.logger.debug(f"Theme applied: {theme.name}")
            
        except Exception as e:
            self.logger.error(f"Failed to apply theme: {e}")
    
    def generate_stylesheet(self, theme: ThemeConfig) -> str:
        """Tema için stylesheet oluştur"""
        colors = theme.colors
        fonts = theme.fonts
        borders = theme.borders
        
        stylesheet = f"""
        /* Genel stil */
        QWidget {{
            background-color: {colors.background};
            color: {colors.text_primary};
            font-family: '{fonts['default']}';
            font-size: {fonts['size_normal']}pt;
        }}
        
        /* Butonlar */
        QPushButton {{
            background-color: {colors.surface};
            border: {borders['width']} {borders['style']} {colors.border};
            border-radius: {borders['radius']};
            padding: 6px 12px;
            min-height: 20px;
        }}
        
        QPushButton:hover {{
            background-color: {colors.primary};
            color: white;
        }}
        
        QPushButton:pressed {{
            background-color: {colors.primary};
            border: {borders['width']} {borders['style']} {colors.primary};
        }}
        
        QPushButton:disabled {{
            background-color: {colors.surface};
            color: {colors.text_disabled};
            border-color: {colors.text_disabled};
        }}
        
        /* Metin kutuları */
        QLineEdit, QTextEdit, QPlainTextEdit {{
            background-color: {colors.card};
            border: {borders['width']} {borders['style']} {colors.border};
            border-radius: {borders['radius']};
            padding: 4px 8px;
            selection-background-color: {colors.primary};
        }}
        
        QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{
            border-color: {colors.primary};
        }}
        
        /* Listeler */
        QListWidget, QTreeWidget {{
            background-color: {colors.card};
            border: {borders['width']} {borders['style']} {colors.border};
            border-radius: {borders['radius']};
            alternate-background-color: {colors.surface};
        }}
        
        QListWidget::item, QTreeWidget::item {{
            padding: 4px;
            border-bottom: 1px solid {colors.divider};
        }}
        
        QListWidget::item:selected, QTreeWidget::item:selected {{
            background-color: {colors.primary};
            color: white;
        }}
        
        QListWidget::item:hover, QTreeWidget::item:hover {{
            background-color: {colors.surface};
        }}
        
        /* Menüler */
        QMenuBar {{
            background-color: {colors.surface};
            border-bottom: 1px solid {colors.border};
        }}
        
        QMenuBar::item {{
            background-color: transparent;
            padding: 4px 8px;
        }}
        
        QMenuBar::item:selected {{
            background-color: {colors.primary};
            color: white;
        }}
        
        QMenu {{
            background-color: {colors.card};
            border: {borders['width']} {borders['style']} {colors.border};
            border-radius: {borders['radius']};
        }}
        
        QMenu::item {{
            padding: 6px 12px;
        }}
        
        QMenu::item:selected {{
            background-color: {colors.primary};
            color: white;
        }}
        
        /* Scroll barlar */
        QScrollBar:vertical {{
            background-color: {colors.surface};
            width: 12px;
            border-radius: 6px;
        }}
        
        QScrollBar::handle:vertical {{
            background-color: {colors.text_secondary};
            border-radius: 6px;
            min-height: 20px;
        }}
        
        QScrollBar::handle:vertical:hover {{
            background-color: {colors.primary};
        }}
        
        /* Tab widget */
        QTabWidget::pane {{
            border: {borders['width']} {borders['style']} {colors.border};
            border-radius: {borders['radius']};
            background-color: {colors.card};
        }}
        
        QTabBar::tab {{
            background-color: {colors.surface};
            border: {borders['width']} {borders['style']} {colors.border};
            padding: 6px 12px;
            margin-right: 2px;
        }}
        
        QTabBar::tab:selected {{
            background-color: {colors.primary};
            color: white;
        }}
        
        QTabBar::tab:hover {{
            background-color: {colors.text_secondary};
        }}
        
        /* Başlık çubukları */
        QFrame[class="title-bar"] {{
            background-color: {colors.surface};
            border-bottom: 1px solid {colors.border};
        }}
        
        /* Dock */
        QFrame[class="dock"] {{
            background-color: {colors.surface};
            border: {borders['width']} {borders['style']} {colors.border};
            border-radius: 8px;
        }}
        
        /* Topbar */
        QFrame[class="topbar"] {{
            background-color: {colors.surface};
            border-bottom: 1px solid {colors.border};
        }}
        """
        
        return stylesheet
    
    def get_available_themes(self) -> List[Dict]:
        """Mevcut temaları al"""
        themes_list = []
        for theme_name, theme in self.themes.items():
            themes_list.append({
                "name": theme.name,
                "display_name": theme.display_name,
                "mode": theme.mode.value,
                "is_current": theme_name == self.current_theme_name
            })
        
        return themes_list
    
    def add_theme_callback(self, callback: Callable):
        """Tema değişim callback'i ekle"""
        self.theme_callbacks.append(callback)
    
    def remove_theme_callback(self, callback: Callable):
        """Tema değişim callback'ini kaldır"""
        if callback in self.theme_callbacks:
            self.theme_callbacks.remove(callback)
    
    def call_theme_callbacks(self, old_theme: str, new_theme: str):
        """Tema callback'lerini çağır"""
        for callback in self.theme_callbacks:
            try:
                callback(old_theme, new_theme)
            except Exception as e:
                self.logger.error(f"Theme callback failed: {e}")
    
    def export_theme(self, theme_name: str, export_path: str) -> bool:
        """Temayı dışa aktar"""
        try:
            if theme_name not in self.themes:
                return False
            
            theme = self.themes[theme_name]
            export_file = Path(export_path)
            
            with open(export_file, 'w', encoding='utf-8') as f:
                json.dump(theme.to_dict(), f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Theme exported: {theme_name} to {export_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to export theme {theme_name}: {e}")
            return False
    
    def import_theme(self, import_path: str) -> bool:
        """Tema içe aktar"""
        try:
            import_file = Path(import_path)
            if not import_file.exists():
                return False
            
            with open(import_file, 'r', encoding='utf-8') as f:
                theme_data = json.load(f)
            
            theme = ThemeConfig.from_dict(theme_data)
            
            # Kullanıcı tema dizinine kaydet
            theme_file = self.user_themes_dir / f"{theme.name}.json"
            with open(theme_file, 'w', encoding='utf-8') as f:
                json.dump(theme.to_dict(), f, indent=2, ensure_ascii=False)
            
            # Tema listesine ekle
            self.themes[theme.name] = theme
            
            self.logger.info(f"Theme imported: {theme.name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to import theme: {e}")
            return False
    
    def shutdown(self):
        """Theme manager'ı kapat"""
        try:
            # Mevcut ayarları kaydet
            if self.kernel:
                config_manager = self.kernel.get_module("config")
                if config_manager:
                    config_manager.set("ui.theme", self.current_theme_name)
                    config_manager.set("ui.theme_mode", self.current_mode.value)
            
            self.logger.info("Theme manager shutdown completed")
            
        except Exception as e:
            self.logger.error(f"Theme manager shutdown failed: {e}")

# Kolaylık fonksiyonları
_theme_manager = None

def init_theme_manager(kernel=None) -> ThemeManager:
    """Theme manager'ı başlat"""
    global _theme_manager
    _theme_manager = ThemeManager(kernel)
    return _theme_manager

def get_theme_manager() -> Optional[ThemeManager]:
    """Theme manager'ı al"""
    return _theme_manager

def get_icon(icon_id: str, size: int = 16) -> Any:
    """İkon al (kısayol)"""
    if _theme_manager:
        return _theme_manager.icon_manager.get_icon(icon_id, size)
    return "📄"

def get_file_icon(file_path: str) -> Any:
    """Dosya ikonu al (kısayol)"""
    if _theme_manager:
        return _theme_manager.icon_manager.get_file_icon(file_path)
    return "📄"

def set_theme(theme_name: str) -> bool:
    """Tema değiştir (kısayol)"""
    if _theme_manager:
        return _theme_manager.set_theme(theme_name)
    return False 