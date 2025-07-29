"""
PyCloud OS Rain Context Menu
Masaüstü, dosya yöneticisi ve uygulama ikonları için dinamik sağ tık menü sistemi
"""

import os
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass
from enum import Enum
import json

try:
    from PyQt6.QtWidgets import (QMenu, QAction, QWidget, QApplication, 
                                QMessageBox, QInputDialog, QFileDialog)
    from PyQt6.QtCore import Qt, QPoint, pyqtSignal, QObject
    from PyQt6.QtGui import QIcon, QPixmap, QKeySequence
    PYQT_AVAILABLE = True
except ImportError:
    # Dummy classes for when PyQt6 is not available
    class QMenu:
        def __init__(self, *args, **kwargs): pass
        def addAction(self, *args, **kwargs): return QAction()
        def addSeparator(self): pass
        def addMenu(self, *args, **kwargs): return QMenu()
        def exec(self, *args, **kwargs): return None
        def setStyleSheet(self, *args, **kwargs): pass
    
    class QAction:
        def __init__(self, *args, **kwargs): pass
        def triggered(self): return pyqtSignal()
        def setIcon(self, *args, **kwargs): pass
        def setEnabled(self, *args, **kwargs): pass
    
    class QWidget:
        def __init__(self, *args, **kwargs): pass
    
    class QObject:
        def __init__(self, *args, **kwargs): pass
    
    class pyqtSignal:
        def __init__(self, *args, **kwargs): pass
        def connect(self, *args, **kwargs): pass
        def emit(self, *args, **kwargs): pass
    
    class QIcon:
        def __init__(self, *args, **kwargs): pass
    
    class QPoint:
        def __init__(self, *args, **kwargs): pass
    
    PYQT_AVAILABLE = False

class MenuType(Enum):
    """Menü türleri"""
    DESKTOP = "desktop"
    FILE = "file"
    FOLDER = "folder"
    APPLICATION = "application"
    WIDGET = "widget"
    SELECTION = "selection"  # Çoklu seçim

class MenuContext(Enum):
    """Menü bağlamları"""
    DESKTOP_EMPTY = "desktop_empty"
    DESKTOP_FILE = "desktop_file"
    DESKTOP_FOLDER = "desktop_folder"
    FILES_APP = "files_app"
    DOCK_APP = "dock_app"
    WIDGET_AREA = "widget_area"
    APP_PACKAGE = "app_package"

@dataclass
class MenuAction:
    """Menü eylemi"""
    id: str
    text: str
    icon: str = ""
    shortcut: str = ""
    enabled: bool = True
    visible: bool = True
    separator_after: bool = False
    submenu: List['MenuAction'] = None
    callback: Callable = None
    
    def __post_init__(self):
        if self.submenu is None:
            self.submenu = []

@dataclass
class MenuRequest:
    """Menü isteği"""
    menu_type: MenuType
    context: MenuContext
    target_path: str = ""
    target_paths: List[str] = None
    position: Optional[Any] = None
    widget: Optional[Any] = None
    extra_data: Dict = None
    
    def __post_init__(self):
        if self.target_paths is None:
            self.target_paths = []
        if self.extra_data is None:
            self.extra_data = {}

class ContextMenuManager(QObject):
    """Bağlam menüsü yöneticisi"""
    
    # Sinyaller
    action_triggered = pyqtSignal(str, dict)  # action_id, data
    
    def __init__(self, kernel=None):
        super().__init__()
        self.kernel = kernel
        self.logger = logging.getLogger("ContextMenuManager")
        
        # Menü şablonları
        self.menu_templates: Dict[MenuContext, List[MenuAction]] = {}
        
        # Eylem callback'leri
        self.action_callbacks: Dict[str, Callable] = {}
        
        # Clipboard
        self.clipboard_files: List[str] = []
        self.clipboard_operation = ""  # "copy" veya "cut"
        
        # Başlangıç
        self.create_default_templates()
        self.register_default_actions()
    
    def create_default_templates(self):
        """Varsayılan menü şablonları oluştur"""
        
        # Masaüstü boş alan menüsü
        self.menu_templates[MenuContext.DESKTOP_EMPTY] = [
            MenuAction("new_file", "📄 Yeni", submenu=[
                MenuAction("new_text", "📝 Metin Belgesi"),
                MenuAction("new_python", "🐍 Python Dosyası"),
                MenuAction("new_folder", "📁 Klasör"),
            ]),
            MenuAction("paste", "📋 Yapıştır", shortcut="Ctrl+V", enabled=False),
            MenuAction("", "", separator_after=True),
            MenuAction("refresh", "🔄 Yenile", shortcut="F5"),
            MenuAction("properties", "🎨 Masaüstü Ayarları"),
            MenuAction("wallpaper", "🖼️ Duvar Kağıdı Değiştir"),
        ]
        
        # Dosya menüsü
        self.menu_templates[MenuContext.DESKTOP_FILE] = [
            MenuAction("open", "📂 Aç", shortcut="Enter"),
            MenuAction("open_with", "🔧 Aç ile...", submenu=[]),
            MenuAction("", "", separator_after=True),
            MenuAction("copy", "📋 Kopyala", shortcut="Ctrl+C"),
            MenuAction("cut", "✂️ Kes", shortcut="Ctrl+X"),
            MenuAction("", "", separator_after=True),
            MenuAction("rename", "✏️ Yeniden Adlandır", shortcut="F2"),
            MenuAction("delete", "🗑️ Sil", shortcut="Delete"),
            MenuAction("", "", separator_after=True),
            MenuAction("properties", "ℹ️ Özellikler", shortcut="Alt+Enter"),
        ]
        
        # Klasör menüsü
        self.menu_templates[MenuContext.DESKTOP_FOLDER] = [
            MenuAction("open", "📂 Aç", shortcut="Enter"),
            MenuAction("open_new_window", "🪟 Yeni Pencerede Aç"),
            MenuAction("", "", separator_after=True),
            MenuAction("copy", "📋 Kopyala", shortcut="Ctrl+C"),
            MenuAction("cut", "✂️ Kes", shortcut="Ctrl+X"),
            MenuAction("", "", separator_after=True),
            MenuAction("rename", "✏️ Yeniden Adlandır", shortcut="F2"),
            MenuAction("delete", "🗑️ Sil", shortcut="Delete"),
            MenuAction("", "", separator_after=True),
            MenuAction("properties", "ℹ️ Özellikler", shortcut="Alt+Enter"),
        ]
        
        # Uygulama menüsü (Dock)
        self.menu_templates[MenuContext.DOCK_APP] = [
            MenuAction("launch", "🚀 Başlat"),
            MenuAction("", "", separator_after=True),
            MenuAction("pin", "📌 Dock'a Sabitle"),
            MenuAction("unpin", "📌 Dock'tan Kaldır"),
            MenuAction("", "", separator_after=True),
            MenuAction("app_info", "ℹ️ Uygulama Bilgileri"),
            MenuAction("app_settings", "⚙️ Uygulama Ayarları"),
        ]
        
        # Dosya yöneticisi menüsü
        self.menu_templates[MenuContext.FILES_APP] = [
            MenuAction("open", "📂 Aç", shortcut="Enter"),
            MenuAction("open_with", "🔧 Aç ile...", submenu=[]),
            MenuAction("", "", separator_after=True),
            MenuAction("copy", "📋 Kopyala", shortcut="Ctrl+C"),
            MenuAction("cut", "✂️ Kes", shortcut="Ctrl+X"),
            MenuAction("paste", "📄 Yapıştır", shortcut="Ctrl+V"),
            MenuAction("", "", separator_after=True),
            MenuAction("rename", "✏️ Yeniden Adlandır", shortcut="F2"),
            MenuAction("delete", "🗑️ Sil", shortcut="Delete"),
            MenuAction("", "", separator_after=True),
            MenuAction("compress", "📦 Arşivle"),
            MenuAction("properties", "ℹ️ Özellikler", shortcut="Alt+Enter"),
        ]
        
        # Widget menüsü
        self.menu_templates[MenuContext.WIDGET_AREA] = [
            MenuAction("widget_settings", "⚙️ Widget Ayarları"),
            MenuAction("widget_resize", "📏 Yeniden Boyutlandır"),
            MenuAction("", "", separator_after=True),
            MenuAction("widget_close", "✕ Kapat"),
        ]
        
        # .app dosyası menüsü
        self.menu_templates[MenuContext.APP_PACKAGE] = [
            MenuAction("install_app", "📦 Uygulamayı Kur", shortcut="Enter"),
            MenuAction("", "", separator_after=True),
            MenuAction("copy", "📋 Kopyala", shortcut="Ctrl+C"),
            MenuAction("cut", "✂️ Kes", shortcut="Ctrl+X"),
            MenuAction("", "", separator_after=True),
            MenuAction("rename", "✏️ Yeniden Adlandır", shortcut="F2"),
            MenuAction("delete", "🗑️ Sil", shortcut="Delete"),
            MenuAction("", "", separator_after=True),
            MenuAction("app_package_info", "ℹ️ Paket Bilgileri"),
            MenuAction("properties", "📋 Özellikler", shortcut="Alt+Enter"),
        ]
    
    def register_default_actions(self):
        """Varsayılan eylem callback'lerini kaydet"""
        self.action_callbacks.update({
            # Dosya işlemleri
            "new_text": self.create_new_text_file,
            "new_python": self.create_new_python_file,
            "new_folder": self.create_new_folder,
            "open": self.open_item,
            "copy": self.copy_items,
            "cut": self.cut_items,
            "paste": self.paste_items,
            "rename": self.rename_item,
            "delete": self.delete_items,
            "properties": self.show_properties,
            
            # Masaüstü işlemleri
            "refresh": self.refresh_desktop,
            "wallpaper": self.change_wallpaper,
            
            # Uygulama işlemleri
            "launch": self.launch_app,
            "pin": self.pin_app,
            "unpin": self.unpin_app,
            "app_info": self.show_app_info,
            "app_settings": self.show_app_settings,
            
            # Widget işlemleri
            "widget_settings": self.show_widget_settings,
            "widget_resize": self.resize_widget,
            "widget_close": self.close_widget,
            
            # .app paketi işlemleri
            "install_app": self.install_app_from_context,
            "app_package_info": self.show_app_package_info,
        })
    
    def show_context_menu(self, request: MenuRequest) -> bool:
        """Bağlam menüsünü göster"""
        try:
            self.logger.info(f"show_context_menu called with context: {request.context}")
            
            # Runtime PyQt6 kontrolü
            pyqt_available = self._check_pyqt_availability()
            self.logger.info(f"Runtime PYQT_AVAILABLE: {pyqt_available}, position: {request.position}")
            
            if not pyqt_available or not request.position:
                self.logger.warning(f"Cannot show menu: PYQT_AVAILABLE={pyqt_available}, position={request.position}")
                return False
            
            # Menü şablonunu al
            template = self.menu_templates.get(request.context, [])
            if not template:
                self.logger.warning(f"No template found for context: {request.context}")
                return False
            
            self.logger.info(f"Found template with {len(template)} items")
            
            # Menüyü oluştur
            menu = self.create_menu(template, request)
            if not menu:
                self.logger.error("Failed to create menu")
                return False
            
            self.logger.info("Menu created successfully, showing...")
            
            # Menüyü göster - artık lambda'lar action'ları handle ediyor
            menu.exec(request.position)
            
            self.logger.info("Menu execution completed")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to show context menu: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
            return False
    
    def _check_pyqt_availability(self) -> bool:
        """Runtime PyQt6 kontrolü"""
        try:
            from PyQt6.QtWidgets import QMenu
            return True
        except ImportError:
            return False
    
    def create_menu(self, template: List[MenuAction], request: MenuRequest) -> Optional[QMenu]:
        """Menü oluştur"""
        try:
            from PyQt6.QtWidgets import QMenu
            from PyQt6.QtGui import QAction, QKeySequence
            
            menu = QMenu()
            menu.setStyleSheet(self.get_menu_stylesheet())
            
            for action_def in template:
                if not action_def.visible:
                    continue
                
                if action_def.id == "":  # Ayırıcı
                    menu.addSeparator()
                    continue
                
                # Alt menü varsa
                if action_def.submenu:
                    submenu = QMenu(action_def.text, menu)
                    submenu.setStyleSheet(self.get_menu_stylesheet())
                    
                    for sub_action in action_def.submenu:
                        if sub_action.visible:
                            sub_qaction = QAction(sub_action.text, submenu)
                            # Lambda ile action_id'yi bağla
                            sub_qaction.triggered.connect(
                                lambda checked, aid=sub_action.id: self.execute_action(aid, request)
                            )
                            sub_qaction.setEnabled(sub_action.enabled)
                            submenu.addAction(sub_qaction)
                    
                    menu.addMenu(submenu)
                else:
                    # Normal eylem
                    qaction = QAction(action_def.text, menu)
                    # Lambda ile action_id'yi bağla
                    qaction.triggered.connect(
                        lambda checked, aid=action_def.id: self.execute_action(aid, request)
                    )
                    qaction.setEnabled(self.is_action_enabled(action_def.id, request))
                    
                    # Shortcut ekle
                    if action_def.shortcut:
                        try:
                            qaction.setShortcut(QKeySequence(action_def.shortcut))
                        except Exception as e:
                            self.logger.warning(f"Failed to set shortcut {action_def.shortcut}: {e}")
                    
                    menu.addAction(qaction)
                
                if action_def.separator_after:
                    menu.addSeparator()
            
            # Dinamik menü öğeleri ekle (paste action güncelleme)
            self.update_paste_action_new(menu, request)
            
            return menu
            
        except Exception as e:
            self.logger.error(f"Failed to create menu: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
            return None
    
    def add_dynamic_items(self, menu: QMenu, request: MenuRequest):
        """Dinamik menü öğeleri ekle"""
        try:
            # "Aç ile" alt menüsünü doldur
            if request.target_path and Path(request.target_path).is_file():
                self.populate_open_with_menu(menu, request.target_path)
            
            # Clipboard durumuna göre yapıştır'ı etkinleştir
            self.update_paste_action(menu)
            
        except Exception as e:
            self.logger.error(f"Failed to add dynamic items: {e}")
    
    def populate_open_with_menu(self, menu: QMenu, file_path: str):
        """Aç ile menüsünü doldur"""
        try:
            # Menüde "Aç ile" eylemini bul
            for action in menu.actions():
                if action.text().endswith("Aç ile..."):
                    submenu = action.menu()
                    if submenu:
                        submenu.clear()
                        
                        # Dosya uzantısına göre uygulamaları öner
                        file_ext = Path(file_path).suffix.lower()
                        suggested_apps = self.get_suggested_apps(file_ext)
                        
                        for app_info in suggested_apps:
                            app_action = QAction(f"{app_info['icon']} {app_info['name']}", submenu)
                            app_action.setData(f"open_with:{app_info['id']}")
                            submenu.addAction(app_action)
                        
                        if suggested_apps:
                            submenu.addSeparator()
                        
                        # Diğer uygulama seç
                        choose_action = QAction("🔍 Diğer Uygulama Seç...", submenu)
                        choose_action.setData("open_with:choose")
                        submenu.addAction(choose_action)
                    break
                    
        except Exception as e:
            self.logger.error(f"Failed to populate open with menu: {e}")
    
    def get_suggested_apps(self, file_ext: str) -> List[Dict]:
        """Dosya uzantısına göre önerilen uygulamalar"""
        app_suggestions = {
            ".txt": [{"id": "cloud.notepad", "name": "Notepad", "icon": "📝"}],
            ".py": [{"id": "cloud.pyide", "name": "Python IDE", "icon": "🐍"}],
            ".md": [{"id": "cloud.notepad", "name": "Notepad", "icon": "📝"}],
            ".json": [{"id": "cloud.notepad", "name": "Notepad", "icon": "📝"}],
            ".log": [{"id": "cloud.notepad", "name": "Notepad", "icon": "📝"}],
            ".html": [{"id": "cloud.browser", "name": "Browser", "icon": "🌐"}],
            ".pdf": [{"id": "cloud.browser", "name": "Browser", "icon": "🌐"}],
            ".app": [{"id": "install_app", "name": "Uygulamayı Kur", "icon": "📦"}],
        }
        
        return app_suggestions.get(file_ext, [])
    
    def update_paste_action(self, menu: QMenu):
        """Yapıştır eylemini güncelle"""
        try:
            for action in menu.actions():
                if action.data() == "paste":
                    action.setEnabled(len(self.clipboard_files) > 0)
                    break
        except Exception as e:
            self.logger.error(f"Failed to update paste action: {e}")
    
    def is_action_enabled(self, action_id: str, request: MenuRequest) -> bool:
        """Eylemin etkin olup olmadığını kontrol et"""
        try:
            # Genel kontroller
            if action_id == "paste":
                return len(self.clipboard_files) > 0
            
            if action_id in ["copy", "cut", "delete", "rename", "properties"]:
                return bool(request.target_path or request.target_paths)
            
            if action_id == "open":
                return bool(request.target_path)
            
            # Uygulama kontrolleri
            if action_id in ["launch", "pin", "unpin"]:
                return bool(request.extra_data.get("app_id"))
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to check action enabled: {e}")
            return False
    
    def execute_action(self, action_id: str, request: MenuRequest):
        """Eylemi çalıştır"""
        try:
            self.logger.info(f"Executing action: {action_id}")
            
            # Özel eylemler (open_with gibi)
            if ":" in action_id:
                action_type, action_data = action_id.split(":", 1)
                if action_type == "open_with":
                    self.open_with_app(request.target_path, action_data)
                return
            
            # Normal eylemler
            callback = self.action_callbacks.get(action_id)
            if callback:
                self.logger.info(f"Found callback for action: {action_id}")
                callback(request)
            else:
                self.logger.warning(f"No callback found for action: {action_id}")
            
            # Sinyal yayınla
            self.action_triggered.emit(action_id, {
                "target_path": request.target_path,
                "target_paths": request.target_paths,
                "context": request.context.value,
                "extra_data": request.extra_data
            })
            
        except Exception as e:
            self.logger.error(f"Failed to execute action {action_id}: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
    
    def get_menu_stylesheet(self) -> str:
        """Menü stil sayfası"""
        return """
        QMenu {
            background-color: rgba(45, 45, 45, 0.95);
            border: 1px solid rgba(80, 80, 80, 0.8);
            border-radius: 8px;
            padding: 6px;
            color: #ffffff;
        }
        
        QMenu::item {
            background-color: transparent;
            padding: 10px 18px;
            border-radius: 6px;
            margin: 1px;
            color: #ffffff;
        }
        
        QMenu::item:selected {
            background-color: rgba(70, 70, 70, 0.8);
            color: #ffffff;
        }
        
        QMenu::item:disabled {
            color: #888888;
            background-color: transparent;
        }
        
        QMenu::separator {
            height: 1px;
            background-color: rgba(100, 100, 100, 0.6);
            margin: 6px 12px;
        }
        
        QMenu::indicator {
            width: 16px;
            height: 16px;
        }
        """
    
    # Eylem callback'leri
    def create_new_text_file(self, request: MenuRequest):
        """Yeni metin dosyası oluştur"""
        try:
            from PyQt6.QtWidgets import QInputDialog
            
            name, ok = QInputDialog.getText(None, "Yeni Dosya", "Dosya adı:", text="Yeni Metin Belgesi.txt")
            if ok and name:
                if not name.endswith('.txt'):
                    name += '.txt'
                
                # Masaüstüne dosya oluştur
                desktop_path = Path("users/default/Desktop")
                desktop_path.mkdir(parents=True, exist_ok=True)
                file_path = desktop_path / name
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write("")
                
                self.logger.info(f"Created text file: {file_path}")
                
                # Desktop'u yenile
                self.refresh_desktop(request)
                        
        except Exception as e:
            self.logger.error(f"Failed to create text file: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
    
    def create_new_python_file(self, request: MenuRequest):
        """Yeni Python dosyası oluştur"""
        try:
            from PyQt6.QtWidgets import QInputDialog
            
            name, ok = QInputDialog.getText(None, "Yeni Python Dosyası", "Dosya adı:", text="yeni_dosya.py")
            if ok and name:
                if not name.endswith('.py'):
                    name += '.py'
                
                # Masaüstüne dosya oluştur
                desktop_path = Path("users/default/Desktop")
                desktop_path.mkdir(parents=True, exist_ok=True)
                file_path = desktop_path / name
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write('#!/usr/bin/env python3\n# -*- coding: utf-8 -*-\n\n')
                
                self.logger.info(f"Created Python file: {file_path}")
                
                # Desktop'u yenile
                self.refresh_desktop(request)
                        
        except Exception as e:
            self.logger.error(f"Failed to create Python file: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
    
    def create_new_folder(self, request: MenuRequest):
        """Yeni klasör oluştur"""
        try:
            from PyQt6.QtWidgets import QInputDialog
            
            name, ok = QInputDialog.getText(None, "Yeni Klasör", "Klasör adı:", text="Yeni Klasör")
            if ok and name:
                # Masaüstüne klasör oluştur
                desktop_path = Path("users/default/Desktop")
                desktop_path.mkdir(parents=True, exist_ok=True)
                folder_path = desktop_path / name
                folder_path.mkdir(exist_ok=True)
                
                self.logger.info(f"Created folder: {folder_path}")
                
                # Desktop'u yenile
                self.refresh_desktop(request)
                        
        except Exception as e:
            self.logger.error(f"Failed to create folder: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
    
    def open_item(self, request: MenuRequest):
        """Öğeyi aç"""
        try:
            if not request.target_path:
                return
            
            path = Path(request.target_path)
            
            if path.is_dir():
                # Klasörü dosya yöneticisi ile aç
                self.open_folder_in_files(request.target_path)
            else:
                # Dosyayı varsayılan uygulama ile aç
                self.open_file_with_default(request.target_path)
                
        except Exception as e:
            self.logger.error(f"Failed to open item: {e}")
    
    def open_folder_in_files(self, folder_path: str):
        """Klasörü dosya yöneticisinde aç"""
        try:
            if self.kernel:
                launcher = self.kernel.get_module("launcher")
                if launcher:
                    # PyCloud OS sanal dosya sistemi yolunu kullan
                    pycloud_path = folder_path
                    if not folder_path.startswith(("users/", "apps/", "system/", "temp/")):
                        # Eğer gerçek dosya sistemi yolu ise, PyCloud OS yoluna çevir
                        pycloud_path = str(Path("users") / "default" / "Desktop")
                    
                    launcher.launch_app("cloud_files", {"open_path": pycloud_path})
                    
        except Exception as e:
            self.logger.error(f"Failed to open folder in files: {e}")
    
    def open_file_with_default(self, file_path: str):
        """Dosyayı varsayılan uygulama ile aç"""
        try:
            file_ext = Path(file_path).suffix.lower()
            file_name = Path(file_path).name.lower()
            
            # .app dosyası mı kontrol et
            if file_name.endswith('.app') or file_path.endswith('.app'):
                # .app dosyası - kurulum işlemi başlat
                self.install_app_package(file_path)
                return
            
            # Varsayılan uygulamalar - .py dosyaları için PyIDE eklendi
            default_apps = {
                ".txt": "cloud_notepad",
                ".py": "cloud_pyide",  # Python dosyaları PyIDE ile açılsın
                ".js": "cloud_pyide",  # JavaScript dosyaları da PyIDE ile
                ".html": "cloud_browser",
                ".css": "cloud_pyide",  # CSS dosyaları PyIDE ile
                ".md": "cloud_notepad",
                ".json": "cloud_pyide",  # JSON dosyaları PyIDE ile
                ".log": "cloud_notepad",
                ".pdf": "cloud_browser",
            }
            
            app_id = default_apps.get(file_ext, "cloud_notepad")
            
            if self.kernel:
                launcher = self.kernel.get_module("launcher")
                if launcher:
                    # ÇÖZÜM: Absolute path kullan - boş açılma sorununu çözer
                    absolute_path = str(Path(file_path).resolve().absolute())
                    
                    self.logger.info(f"🚀 Masaüstünden dosya açılıyor: {app_id} -> {absolute_path}")
                    
                    # Launcher API ile dosyayı aç
                    launch_success = launcher.launch_app(app_id, open_file=absolute_path)
                    
                    if launch_success:
                        self.logger.info(f"✅ Dosya başarıyla açıldı: {absolute_path}")
                    else:
                        self.logger.warning(f"⚠️ Dosya açma başarısız")
                        # Fallback olarak sistem uygulamasını dene
                        self._open_with_system_app(absolute_path)
                else:
                    self.logger.warning("⚠️ Launcher modülü bulunamadı")
                    self._open_with_system_app(str(Path(file_path).absolute()))
            else:
                self.logger.warning("⚠️ Kernel bulunamadı")
                self._open_with_system_app(str(Path(file_path).absolute()))
                    
        except Exception as e:
            self.logger.error(f"Failed to open file with default app: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
    
    def _open_with_system_app(self, absolute_path: str):
        """Sistem uygulamasıyla dosyayı aç"""
        try:
            import subprocess
            import platform
            
            system = platform.system()
            self.logger.info(f"🔄 Sistem uygulamasıyla açılıyor: {absolute_path}")
            
            if system == "Darwin":  # macOS
                subprocess.run(["open", absolute_path], check=True)
            elif system == "Windows":
                subprocess.run(["start", absolute_path], shell=True, check=True)
            else:  # Linux
                subprocess.run(["xdg-open", absolute_path], check=True)
            
            self.logger.info(f"✅ Sistem uygulamasıyla açıldı: {absolute_path}")
            
        except Exception as e:
            self.logger.error(f"❌ Sistem uygulamasıyla açma hatası: {e}")
    
    def install_app_package(self, app_path: str):
        """Uygulama paketini kur"""
        try:
            from PyQt6.QtWidgets import QMessageBox
            
            app_name = Path(app_path).stem
            
            # Onay dialogu
            reply = QMessageBox.question(None, "Uygulama Kurulumu", 
                                       f"'{app_name}' uygulamasını kurmak istediğinizden emin misiniz?",
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            
            if reply != QMessageBox.StandardButton.Yes:
                return
            
            # AppKit ile kurulum yap
            if self.kernel:
                appkit = self.kernel.get_module("appkit")
                if appkit:
                    # İlerleme mesajı göster
                    progress_msg = QMessageBox(None)
                    progress_msg.setWindowTitle("Kurulum")
                    progress_msg.setText(f"'{app_name}' kuruluyor...")
                    progress_msg.setStandardButtons(QMessageBox.StandardButton.NoButton)
                    progress_msg.show()
                    
                    # Kurulum işlemi
                    result, message = appkit.install_app(app_path, force=False)
                    
                    progress_msg.close()
                    
                    # Sonuç mesajı
                    if result.name == "SUCCESS":
                        QMessageBox.information(None, "Başarılı", f"✅ {message}")
                        
                        # AppExplorer'ı yenile
                        app_explorer = self.kernel.get_module("appexplorer")
                        if app_explorer:
                            app_explorer.force_discovery()
                        
                        # Desktop'u yenile
                        self.refresh_desktop(None)
                        
                    elif result.name == "ALREADY_INSTALLED":
                        reply = QMessageBox.question(None, "Zaten Kurulu", 
                                                   f"'{app_name}' zaten kurulu. Güncellemek istediğinizden emin misiniz?",
                                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                        
                        if reply == QMessageBox.StandardButton.Yes:
                            # Zorla kurulum (güncelleme)
                            result, message = appkit.install_app(app_path, force=True)
                            if result.name == "SUCCESS":
                                QMessageBox.information(None, "Güncellendi", f"✅ {message}")
                            else:
                                QMessageBox.critical(None, "Hata", f"❌ {message}")
                    else:
                        QMessageBox.critical(None, "Kurulum Hatası", f"❌ {message}")
                else:
                    QMessageBox.critical(None, "Hata", "AppKit modülü bulunamadı!")
            else:
                QMessageBox.critical(None, "Hata", "Sistem çekirdeği bulunamadı!")
                
        except Exception as e:
            self.logger.error(f"Failed to install app package: {e}")
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.critical(None, "Hata", f"Kurulum sırasında hata oluştu: {str(e)}")
    
    def open_with_app(self, file_path: str, app_id: str):
        """Dosyayı belirtilen uygulama ile aç"""
        try:
            if app_id == "choose":
                # Uygulama seçim dialogu
                self.show_app_chooser(file_path)
                return
            
            if self.kernel:
                launcher = self.kernel.get_module("launcher")
                if launcher:
                    launcher.launch_app(app_id, {"open_file": file_path})
                    
        except Exception as e:
            self.logger.error(f"Failed to open file with app {app_id}: {e}")
    
    def show_app_chooser(self, file_path: str):
        """Uygulama seçici dialogu göster"""
        # TODO: Uygulama seçici dialog implementasyonu
        self.logger.info(f"Show app chooser for: {file_path}")
    
    def copy_items(self, request: MenuRequest):
        """Öğeleri kopyala"""
        try:
            self.clipboard_files = request.target_paths if request.target_paths else [request.target_path]
            self.clipboard_operation = "copy"
            
            self.logger.info(f"Copied {len(self.clipboard_files)} items to clipboard")
            
        except Exception as e:
            self.logger.error(f"Failed to copy items: {e}")
    
    def cut_items(self, request: MenuRequest):
        """Öğeleri kes"""
        try:
            self.clipboard_files = request.target_paths if request.target_paths else [request.target_path]
            self.clipboard_operation = "cut"
            
            self.logger.info(f"Cut {len(self.clipboard_files)} items to clipboard")
            
        except Exception as e:
            self.logger.error(f"Failed to cut items: {e}")
    
    def paste_items(self, request: MenuRequest):
        """Öğeleri yapıştır"""
        try:
            if not self.clipboard_files:
                return
            
            target_dir = request.extra_data.get("current_dir", "users/demo/Desktop")
            
            for file_path in self.clipboard_files:
                source = Path(file_path)
                target = Path(target_dir) / source.name
                
                if self.clipboard_operation == "copy":
                    if source.is_dir():
                        import shutil
                        shutil.copytree(source, target, dirs_exist_ok=True)
                    else:
                        import shutil
                        shutil.copy2(source, target)
                elif self.clipboard_operation == "cut":
                    source.rename(target)
            
            if self.clipboard_operation == "cut":
                self.clipboard_files.clear()
            
            self.logger.info(f"Pasted {len(self.clipboard_files)} items")
            
        except Exception as e:
            self.logger.error(f"Failed to paste items: {e}")
    
    def rename_item(self, request: MenuRequest):
        """Öğeyi yeniden adlandır"""
        try:
            from PyQt6.QtWidgets import QInputDialog
            
            if not request.target_path:
                self.logger.warning("No target path for rename")
                return
            
            path = Path(request.target_path)
            if not path.exists():
                self.logger.warning(f"Target path does not exist: {path}")
                return
                
            current_name = path.name
            
            new_name, ok = QInputDialog.getText(None, "Yeniden Adlandır", 
                                              "Yeni ad:", text=current_name)
            if ok and new_name and new_name != current_name:
                new_path = path.parent / new_name
                path.rename(new_path)
                
                self.logger.info(f"Renamed {current_name} to {new_name}")
                
                # Desktop'u yenile
                self.refresh_desktop(request)
                
        except Exception as e:
            self.logger.error(f"Failed to rename item: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
    
    def delete_items(self, request: MenuRequest):
        """Öğeleri sil"""
        try:
            from PyQt6.QtWidgets import QMessageBox
            
            items = request.target_paths if request.target_paths else [request.target_path]
            if not items or not items[0]:
                self.logger.warning("No items to delete")
                return
            
            # Onay dialogu
            reply = QMessageBox.question(None, "Silme Onayı", 
                                       f"{len(items)} öğe silinecek. Emin misiniz?",
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            
            if reply == QMessageBox.StandardButton.Yes:
                for item_path in items:
                    if not item_path:
                        continue
                        
                    path = Path(item_path)
                    if not path.exists():
                        self.logger.warning(f"Item does not exist: {path}")
                        continue
                        
                    if path.is_dir():
                        import shutil
                        shutil.rmtree(path)
                    else:
                        path.unlink()
                
                self.logger.info(f"Deleted {len(items)} items")
                
                # Desktop'u yenile
                self.refresh_desktop(request)
                
        except Exception as e:
            self.logger.error(f"Failed to delete items: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
    
    def show_properties(self, request: MenuRequest):
        """Özellikler dialogu göster"""
        # TODO: Özellikler dialog implementasyonu
        self.logger.info(f"Show properties for: {request.target_path}")
    
    def refresh_desktop(self, request: MenuRequest):
        """Masaüstünü yenile"""
        try:
            self.logger.info("Refreshing desktop...")
            
            if self.kernel:
                # rain_ui modülünü dene
                ui = self.kernel.get_module("rain_ui")
                if ui and hasattr(ui, 'desktop'):
                    if hasattr(ui.desktop, 'refresh_desktop'):
                        ui.desktop.refresh_desktop()
                        self.logger.info("Desktop refreshed via rain_ui module")
                        return
                    elif hasattr(ui.desktop, 'load_desktop_items'):
                        ui.desktop.load_desktop_items()
                        self.logger.info("Desktop refreshed via load_desktop_items")
                        return
                    else:
                        self.logger.warning("No refresh method found on desktop")
                
                # Alternatif: QApplication üzerinden tüm widget'ları yenile
                try:
                    from PyQt6.QtWidgets import QApplication
                    app = QApplication.instance()
                    if app:
                        # Tüm widget'ları yenile
                        for widget in app.allWidgets():
                            if hasattr(widget, 'load_desktop_items'):
                                widget.load_desktop_items()
                                self.logger.info("Desktop refreshed via QApplication widget search")
                                return
                            elif hasattr(widget, 'refresh_desktop'):
                                widget.refresh_desktop()
                                self.logger.info("Desktop refreshed via QApplication widget search")
                                return
                except Exception as e:
                    self.logger.warning(f"QApplication refresh failed: {e}")
                
                self.logger.warning("No UI module or desktop found for refresh")
            else:
                self.logger.warning("No kernel available for refresh")
                
        except Exception as e:
            self.logger.error(f"Failed to refresh desktop: {e}")
    
    def change_wallpaper(self, request: MenuRequest):
        """Duvar kağıdı değiştir - PyCloud OS dosya sistemi kullan"""
        try:
            # PyCloud OS wallpaper manager'ı kullan
            if self.kernel:
                wallpaper_manager = self.kernel.get_module("wallpaper")
                if wallpaper_manager:
                    # Wallpaper dialog'unu göster
                    success = wallpaper_manager.show_wallpaper_dialog()
                    if success:
                        self.logger.info("Wallpaper changed via wallpaper manager")
                        return
                    else:
                        self.logger.info("Wallpaper dialog cancelled")
                        return
            
            # Fallback - PyCloud OS dosya sistemi ile manuel seçim
            from PyQt6.QtWidgets import QFileDialog, QMessageBox
            
            # PyCloud OS wallpaper dizinleri
            system_wallpapers = Path("system/wallpapers")
            user_wallpapers = Path("users/default/wallpapers")
            
            # Dizinleri oluştur
            system_wallpapers.mkdir(parents=True, exist_ok=True)
            user_wallpapers.mkdir(parents=True, exist_ok=True)
            
            # Mevcut duvar kağıtlarını kontrol et
            available_wallpapers = []
            
            # Sistem duvar kağıtları
            for wallpaper in system_wallpapers.glob("*"):
                if wallpaper.suffix.lower() in ['.png', '.jpg', '.jpeg', '.bmp', '.webp']:
                    available_wallpapers.append(str(wallpaper))
            
            # Kullanıcı duvar kağıtları
            for wallpaper in user_wallpapers.glob("*"):
                if wallpaper.suffix.lower() in ['.png', '.jpg', '.jpeg', '.bmp', '.webp']:
                    available_wallpapers.append(str(wallpaper))
            
            if available_wallpapers:
                # Mevcut duvar kağıtlarından seç
                from PyQt6.QtWidgets import QInputDialog
                
                wallpaper_names = [Path(wp).name for wp in available_wallpapers]
                
                selected_name, ok = QInputDialog.getItem(
                    None,
                    "Duvar Kağıdı Seç",
                    "Mevcut duvar kağıtlarından birini seçin:",
                    wallpaper_names,
                    0,
                    False
                )
                
                if ok and selected_name:
                    # Seçilen duvar kağıdının tam yolunu bul
                    selected_path = None
                    for wp in available_wallpapers:
                        if Path(wp).name == selected_name:
                            selected_path = wp
                            break
                    
                    if selected_path:
                        # Wallpaper manager ile ayarla
                        if wallpaper_manager:
                            wallpaper_manager.set_wallpaper(selected_path)
                            self.logger.info(f"Wallpaper set to: {selected_path}")
                        else:
                            # Rain UI'dan wallpaper değiştir
                            ui = self.kernel.get_module("ui")
                            if ui and hasattr(ui, 'set_wallpaper'):
                                ui.set_wallpaper(selected_path)
                                self.logger.info("Wallpaper changed via rain_ui")
                        
                        QMessageBox.information(
                            None,
                            "Duvar Kağıdı Değiştirildi",
                            f"Duvar kağıdı '{selected_name}' olarak ayarlandı."
                        )
                        return
            
            # Yeni duvar kağıdı ekleme seçeneği
            reply = QMessageBox.question(
                None,
                "Duvar Kağıdı Bulunamadı",
                "Sistem duvar kağıdı bulunamadı. Yeni bir duvar kağıdı eklemek ister misiniz?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                # PyCloud OS dosya sistemi içinden seç
                file_path, _ = QFileDialog.getOpenFileName(
                    None,
                    "Duvar Kağıdı Seç - PyCloud OS",
                    str(user_wallpapers),  # PyCloud OS kullanıcı wallpaper dizini
                    "Resim Dosyaları (*.png *.jpg *.jpeg *.bmp *.webp);;Tüm Dosyalar (*)"
                )
                
                if file_path:
                    # Eğer PyCloud OS dışından seçildiyse, kopyala
                    file_path_obj = Path(file_path)
                    
                    if not str(file_path).startswith(str(Path.cwd())):
                        # Dosyayı PyCloud OS'a kopyala
                        dest_path = user_wallpapers / file_path_obj.name
                        
                        try:
                            import shutil
                            shutil.copy2(file_path_obj, dest_path)
                            file_path = str(dest_path)
                            
                            QMessageBox.information(
                                None,
                                "Duvar Kağıdı Kopyalandı",
                                f"Duvar kağıdı PyCloud OS'a kopyalandı:\n{dest_path}"
                            )
                        except Exception as e:
                            QMessageBox.critical(
                                None,
                                "Kopyalama Hatası",
                                f"Duvar kağıdı kopyalanamadı:\n{e}"
                            )
                            return
                    
                    # Wallpaper'ı ayarla
                    if wallpaper_manager:
                        wallpaper_manager.set_wallpaper(file_path)
                        self.logger.info(f"New wallpaper set: {file_path}")
                    else:
                        # Rain UI'dan wallpaper değiştir
                        ui = self.kernel.get_module("ui")
                        if ui and hasattr(ui, 'set_wallpaper'):
                            ui.set_wallpaper(file_path)
                            self.logger.info("New wallpaper changed via rain_ui")
                    
                    QMessageBox.information(
                        None,
                        "Duvar Kağıdı Ayarlandı",
                        f"Yeni duvar kağıdı başarıyla ayarlandı!"
                    )
                    
        except Exception as e:
            self.logger.error(f"Failed to change wallpaper: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
            
            # Hata mesajı göster
            try:
                from PyQt6.QtWidgets import QMessageBox
                QMessageBox.critical(
                    None,
                    "Duvar Kağıdı Hatası",
                    f"Duvar kağıdı değiştirilemedi:\n{e}"
                )
            except:
                pass
    
    def launch_app(self, request: MenuRequest):
        """Uygulamayı başlat"""
        try:
            app_id = request.extra_data.get("app_id")
            if app_id and self.kernel:
                launcher = self.kernel.get_module("launcher")
                if launcher:
                    launcher.launch_app(app_id)
                    
        except Exception as e:
            self.logger.error(f"Failed to launch app: {e}")
    
    def pin_app(self, request: MenuRequest):
        """Uygulamayı dock'a sabitle"""
        try:
            app_id = request.extra_data.get("app_id")
            if app_id and self.kernel:
                ui = self.kernel.get_module("ui")
                if ui and hasattr(ui, 'dock'):
                    ui.dock.pin_app(app_id)
                    
        except Exception as e:
            self.logger.error(f"Failed to pin app: {e}")
    
    def unpin_app(self, request: MenuRequest):
        """Uygulamayı dock'tan kaldır"""
        try:
            app_id = request.extra_data.get("app_id")
            if app_id and self.kernel:
                ui = self.kernel.get_module("ui")
                if ui and hasattr(ui, 'dock'):
                    ui.dock.unpin_app(app_id)
                    
        except Exception as e:
            self.logger.error(f"Failed to unpin app: {e}")
    
    def show_app_info(self, request: MenuRequest):
        """Uygulama bilgilerini göster"""
        # TODO: Uygulama bilgi dialogu implementasyonu
        app_id = request.extra_data.get("app_id")
        self.logger.info(f"Show app info for: {app_id}")
    
    def show_app_settings(self, request: MenuRequest):
        """Uygulama ayarlarını göster"""
        # TODO: Uygulama ayar dialogu implementasyonu
        app_id = request.extra_data.get("app_id")
        self.logger.info(f"Show app settings for: {app_id}")
    
    def show_widget_settings(self, request: MenuRequest):
        """Widget ayarlarını göster"""
        try:
            widget_id = request.extra_data.get("widget_id")
            if widget_id and self.kernel:
                widget_manager = self.kernel.get_module("widgets")
                if widget_manager:
                    widget_manager.show_widget_settings(widget_id)
                    
        except Exception as e:
            self.logger.error(f"Failed to show widget settings: {e}")
    
    def resize_widget(self, request: MenuRequest):
        """Widget'ı yeniden boyutlandır"""
        # TODO: Widget boyutlandırma implementasyonu
        widget_id = request.extra_data.get("widget_id")
        self.logger.info(f"Resize widget: {widget_id}")
    
    def close_widget(self, request: MenuRequest):
        """Widget'ı kapat"""
        try:
            widget_id = request.extra_data.get("widget_id")
            if widget_id and self.kernel:
                widget_manager = self.kernel.get_module("widgets")
                if widget_manager:
                    widget_manager.remove_widget(widget_id)
                    
        except Exception as e:
            self.logger.error(f"Failed to close widget: {e}")
    
    def register_action(self, action_id: str, callback: Callable):
        """Özel eylem kaydet"""
        self.action_callbacks[action_id] = callback
    
    def add_menu_template(self, context: MenuContext, template: List[MenuAction]):
        """Menü şablonu ekle"""
        self.menu_templates[context] = template
    
    def shutdown(self):
        """Context menu manager'ı kapat"""
        try:
            self.clipboard_files.clear()
            self.action_callbacks.clear()
            self.menu_templates.clear()
            
            self.logger.info("Context menu manager shutdown completed")
            
        except Exception as e:
            self.logger.error(f"Context menu manager shutdown failed: {e}")

    def update_paste_action_new(self, menu, request):
        """Yapıştır eylemini güncelle (PyQt6 uyumlu)"""
        try:
            # Menu'daki tüm action'ları kontrol et
            for action in menu.actions():
                if action.text() == "📋 Yapıştır":
                    action.setEnabled(len(self.clipboard_files) > 0)
                    break
            
            # Alt menüleri de kontrol et
            for action in menu.actions():
                if action.menu():
                    self.update_paste_action_new(action.menu(), request)
                    
        except Exception as e:
            self.logger.warning(f"Failed to update paste action: {e}")

    def install_app_from_context(self, request: MenuRequest):
        """Context menu'den uygulama kur"""
        if request.target_path:
            self.install_app_package(request.target_path)
    
    def show_app_package_info(self, request: MenuRequest):
        """Uygulama paketi bilgilerini göster"""
        try:
            from PyQt6.QtWidgets import QMessageBox
            
            if not request.target_path:
                return
            
            app_path = Path(request.target_path)
            app_json_path = app_path / "app.json"
            
            if not app_json_path.exists():
                QMessageBox.warning(None, "Hata", "app.json dosyası bulunamadı!")
                return
            
            try:
                with open(app_json_path, 'r', encoding='utf-8') as f:
                    app_data = json.load(f)
                
                # Bilgi mesajı oluştur
                info_text = f"""
📦 Uygulama Paketi Bilgileri

🆔 ID: {app_data.get('id', 'Bilinmiyor')}
📝 Ad: {app_data.get('name', 'Bilinmiyor')}
🔢 Sürüm: {app_data.get('version', 'Bilinmiyor')}
👤 Geliştirici: {app_data.get('developer', 'Bilinmiyor')}
📋 Açıklama: {app_data.get('description', 'Açıklama yok')}
🏷️ Kategori: {app_data.get('category', 'Bilinmiyor')}
📄 Giriş Dosyası: {app_data.get('entry', 'main.py')}
🏷️ Etiketler: {', '.join(app_data.get('tags', []))}
📦 Boyut: {self._get_directory_size(app_path):.2f} MB
                """.strip()
                
                QMessageBox.information(None, "Paket Bilgileri", info_text)
                
            except json.JSONDecodeError:
                QMessageBox.critical(None, "Hata", "app.json dosyası geçersiz!")
            except Exception as e:
                QMessageBox.critical(None, "Hata", f"Bilgi okunamadı: {str(e)}")
                
        except Exception as e:
            self.logger.error(f"Failed to show app package info: {e}")
    
    def _get_directory_size(self, directory: Path) -> float:
        """Dizin boyutunu MB cinsinden hesapla"""
        try:
            total_size = 0
            for file_path in directory.rglob("*"):
                if file_path.is_file():
                    total_size += file_path.stat().st_size
            return total_size / 1024 / 1024
        except Exception:
            return 0.0

# Kolaylık fonksiyonları
_context_menu_manager = None

def init_context_menu_manager(kernel=None) -> ContextMenuManager:
    """Context menu manager'ı başlat"""
    global _context_menu_manager
    
    # Debug: PyQt6 durumunu kontrol et
    logger = logging.getLogger("ContextMenuInit")
    logger.info(f"Initializing context menu manager, PYQT_AVAILABLE: {PYQT_AVAILABLE}")
    
    try:
        # PyQt6 import'unu tekrar test et
        from PyQt6.QtWidgets import QMenu
        logger.info("PyQt6 import test successful")
    except ImportError as e:
        logger.error(f"PyQt6 import test failed: {e}")
    
    _context_menu_manager = ContextMenuManager(kernel)
    logger.info("Context menu manager created successfully")
    return _context_menu_manager

def get_context_menu_manager() -> Optional[ContextMenuManager]:
    """Context menu manager'ı al"""
    return _context_menu_manager

def show_context_menu(menu_type: MenuType, context: MenuContext, 
                     position: QPoint, target_path: str = "", 
                     **kwargs) -> bool:
    """Bağlam menüsü göster (kısayol)"""
    if _context_menu_manager:
        request = MenuRequest(
            menu_type=menu_type,
            context=context,
            target_path=target_path,
            position=position,
            **kwargs
        )
        return _context_menu_manager.show_context_menu(request)
    return False 