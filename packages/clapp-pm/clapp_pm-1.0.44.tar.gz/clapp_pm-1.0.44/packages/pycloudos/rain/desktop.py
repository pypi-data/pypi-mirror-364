"""
Rain Desktop - Masaüstü Alanı
PyCloud OS için masaüstü simgeleri ve etkileşim alanı
"""

import logging
import os
from typing import List, Dict, Optional
from pathlib import Path

try:
    from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                                QPushButton, QGridLayout, QScrollArea,
                                QFrame)
    from PyQt6.QtCore import Qt, QSize, pyqtSignal, QTimer
    from PyQt6.QtGui import QFont, QPixmap, QPainter, QColor, QBrush
    PYQT_AVAILABLE = True
except ImportError:
    PYQT_AVAILABLE = False

class DesktopIcon(QPushButton):
    """Masaüstü simgesi widget'ı"""
    
    double_clicked = pyqtSignal(str)  # file_path
    
    def __init__(self, name: str, file_path: str, icon_text: str = "📄"):
        super().__init__()
        self.name = name
        self.file_path = file_path
        self.icon_text = icon_text
        
        self.setup_ui()
    
    def setup_ui(self):
        """Simge arayüzünü kur"""
        self.setFixedSize(90, 120)
        self.setText(f"{self.icon_text}\n{self.name}")
        self.setFont(QFont("Arial", 10))
        self.setToolTip(self.file_path)
        
        self.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: 2px solid transparent;
                border-radius: 10px;
                color: #ffffff;
                text-align: center;
                padding: 8px;
                font-weight: bold;
            }
            
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.1);
                border-color: rgba(255, 255, 255, 0.2);
            }
            
            QPushButton:pressed {
                background-color: rgba(255, 255, 255, 0.15);
            }
        """)
    
    def mouseDoubleClickEvent(self, event):
        """Çift tıklama olayı"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.double_clicked.emit(self.file_path)
        super().mouseDoubleClickEvent(event)

class RainDesktop(QWidget):
    """Rain UI Desktop bileşeni"""
    
    def __init__(self, kernel):
        super().__init__()
        self.kernel = kernel
        self.logger = logging.getLogger("RainDesktop")
        
        if not PYQT_AVAILABLE:
            return
        
        self.desktop_icons: List[DesktopIcon] = []
        self.desktop_files: List[Dict] = []
        
        self.setup_ui()
        self.load_desktop_items()
        
        # Periyodik güncelleme
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.refresh_desktop)
        self.update_timer.start(10000)  # Her 10 saniyede güncelle
    
    def setup_ui(self):
        """Arayüzü kur"""
        self.setStyleSheet("""
            QWidget {
                background-color: transparent;
                color: #ffffff;
            }
        """)
        
        # Ana layout - sadece simgeler için
        main_layout = QGridLayout(self)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        
        # Layout'u kaydet
        self.desktop_layout = main_layout
    
    def load_desktop_items(self):
        """Masaüstü öğelerini yükle"""
        try:
            # Basitleştirilmiş desktop path - doğrudan pycloud_fs/home/Desktop
            desktop_path = Path("pycloud_fs/home/Desktop")
            desktop_path.mkdir(parents=True, exist_ok=True)
            
            self.desktop_files = []
            
            # Gerçek dosyaları yükle
            if desktop_path.exists():
                for item in desktop_path.iterdir():
                    if not item.name.startswith('.'):  # Gizli dosyaları atla
                        self.desktop_files.append({
                            "name": item.name,
                            "path": str(item),
                            "type": "folder" if item.is_dir() else "file",
                            "icon": self.get_file_icon(item.name)
                        })
            
            # Demo dosyaları ekle (eğer masaüstü boşsa)
            if not self.desktop_files:
                # Hoş geldin dosyası oluştur
                welcome_file = desktop_path / "PyCloud OS'e Hoş Geldiniz.md"
                if not welcome_file.exists():
                    welcome_content = """# PyCloud OS'e Hoş Geldiniz! 🎉

Bu dosya sizin kişisel masaüstünüzde yer almaktadır.

## Hızlı Başlangıç

- 📁 **Dosyalar**: Dock'taki Dosyalar simgesine tıklayarak dosya yöneticinizi açabilirsiniz
- 💻 **Terminal**: Sistem komutları için terminal uygulamasını kullanın
- 🐍 **Python IDE**: Python geliştirme için IDE'yi açın
- ⚙️ **Ayarlar**: Sistem ayarlarını topbar'daki bulut menüsünden erişebilirsiniz

## Klasörleriniz

- **Belgeler**: Dokümanlarınız için
- **İndirilenler**: İndirilen dosyalar
- **Projeler**: Geliştirme projeleri
- **Resimler**: Görseller ve fotoğraflar

Keyifli kullanımlar! 😊
"""
                    with open(welcome_file, 'w', encoding='utf-8') as f:
                        f.write(welcome_content)
                
                # Belgelerim klasörü oluştur - yeni yapıya göre
                documents_folder = Path("pycloud_fs/home/Documents")
                documents_folder.mkdir(parents=True, exist_ok=True)
                
                self.desktop_files = [
                    {
                        "name": "PyCloud OS'e Hoş Geldiniz.md",
                        "path": str(welcome_file),
                        "type": "file",
                        "icon": "📋"
                    },
                    {
                        "name": "Belgelerim",
                        "path": str(documents_folder),
                        "type": "folder",
                        "icon": "📁"
                    }
                ]
            
            self.update_desktop_icons()
            
        except Exception as e:
            self.logger.error(f"Failed to load desktop items: {e}")
    
    def get_file_icon(self, filename: str) -> str:
        """Dosya türüne göre ikon döndür"""
        ext = filename.split('.')[-1].lower() if '.' in filename else ''
        
        icon_map = {
            'txt': '📝',
            'md': '📋',
            'py': '🐍',
            'json': '📋',
            'png': '🖼️',
            'jpg': '🖼️',
            'jpeg': '🖼️',
            'pdf': '📄',
            'zip': '📦',
            'folder': '📁'
        }
        
        return icon_map.get(ext, '📄')
    
    def update_desktop_icons(self):
        """Desktop simgelerini güncelle"""
        # Mevcut simgeleri temizle
        for icon in self.desktop_icons:
            icon.setParent(None)
            icon.deleteLater()
        
        self.desktop_icons.clear()
        
        # Yeni simgeleri oluştur - normal desktop düzeni
        row, col = 0, 0
        max_cols = 8  # Daha geniş alan kullan
        
        for file_info in self.desktop_files:
            icon = DesktopIcon(
                name=file_info["name"],
                file_path=file_info["path"],
                icon_text=file_info["icon"]
            )
            
            icon.double_clicked.connect(self.open_desktop_item)
            
            self.desktop_layout.addWidget(icon, row, col)
            self.desktop_icons.append(icon)
            
            col += 1
            if col >= max_cols:
                col = 0
                row += 1
    
    def open_desktop_item(self, file_path: str):
        """Masaüstü öğesini aç"""
        self.logger.info(f"Opening desktop item: {file_path}")
        
        try:
            # Dosya türüne göre uygun uygulamayı başlat
            if file_path.endswith('.txt') or file_path.endswith('.md'):
                self.launch_app_for_file("cloud_notepad", file_path)
            elif file_path.endswith('.py'):
                self.launch_app_for_file("cloud_pyide", file_path)
            elif "folder" in file_path.lower() or os.path.isdir(file_path):
                self.launch_app_for_file("cloud.files", file_path)
            else:
                # Varsayılan dosya yöneticisi ile aç
                self.launch_app_for_file("cloud.files", file_path)
                
        except Exception as e:
            self.logger.error(f"Failed to open desktop item {file_path}: {e}")
    
    def launch_app_for_file(self, app_id: str, file_path: str):
        """Dosya için uygulama başlat"""
        try:
            if self.kernel:
                launcher = self.kernel.get_module("launcher")
                if launcher:
                    # PyCloud OS sanal dosya sistemi yolunu kullan
                    pycloud_path = file_path
                    if not file_path.startswith(("users/", "apps/", "system/", "temp/")):
                        # Eğer gerçek dosya sistemi yolu ise, PyCloud OS yoluna çevir
                        pycloud_path = str(Path("users") / "default" / "Desktop" / Path(file_path).name)
                    
                    # Dosya yolu argümanı ile uygulama başlat
                    launcher.launch_app(app_id, {"open_file": pycloud_path})
                    self.logger.info(f"Launched {app_id} for file: {pycloud_path}")
                else:
                    self.logger.warning("Launcher module not available")
            
        except Exception as e:
            self.logger.error(f"Failed to launch app {app_id} for file {file_path}: {e}")
    
    def refresh_desktop(self):
        """Masaüstünü yenile"""
        try:
            self.load_desktop_items()
        except Exception as e:
            self.logger.error(f"Failed to refresh desktop: {e}")
    
    def add_desktop_item(self, name: str, path: str, file_type: str):
        """Masaüstüne yeni öğe ekle"""
        new_item = {
            "name": name,
            "path": path,
            "type": file_type,
            "icon": self.get_file_icon(name)
        }
        
        self.desktop_files.append(new_item)
        self.update_desktop_icons()
        
        self.logger.info(f"Added desktop item: {name}")
    
    def remove_desktop_item(self, path: str):
        """Masaüstünden öğe kaldır"""
        self.desktop_files = [item for item in self.desktop_files if item["path"] != path]
        self.update_desktop_icons()
        
        self.logger.info(f"Removed desktop item: {path}")
    
    def contextMenuEvent(self, event):
        """Masaüstü sağ tık menüsü"""
        self.logger.info(f"Context menu event triggered at position: {event.pos()}")
        
        try:
            # Context menu manager'ı kullan
            if self.kernel:
                context_menu_manager = self.kernel.get_module("contextmenu")
                if context_menu_manager:
                    self.logger.info("Using context menu manager")
                    from rain.contextmenu import MenuRequest, MenuType, MenuContext
                    
                    # Tıklanan pozisyonda dosya var mı kontrol et
                    clicked_widget = self.childAt(event.pos())
                    target_file = None
                    
                    if clicked_widget and isinstance(clicked_widget, DesktopIcon):
                        # Dosya/klasör üzerine tıklandı
                        target_file = clicked_widget.file_path
                        file_type = clicked_widget.name.split('.')[-1].lower() if '.' in clicked_widget.name else ''
                        
                        self.logger.info(f"Right-clicked on desktop icon: {clicked_widget.name}")
                        
                        if clicked_widget.name == "Belgelerim" or "folder" in clicked_widget.file_path.lower():
                            # Klasör menüsü
                            request = MenuRequest(
                                menu_type=MenuType.FOLDER,
                                context=MenuContext.DESKTOP_FOLDER,
                                target_path=target_file,
                                position=event.globalPos(),
                                widget=self,
                                extra_data={"icon_widget": clicked_widget}
                            )
                        else:
                            # Dosya menüsü
                            request = MenuRequest(
                                menu_type=MenuType.FILE,
                                context=MenuContext.DESKTOP_FILE,
                                target_path=target_file,
                                position=event.globalPos(),
                                widget=self,
                                extra_data={"icon_widget": clicked_widget, "file_type": file_type}
                            )
                    else:
                        # Boş alan menüsü
                        self.logger.info("Right-clicked on empty desktop area")
                        request = MenuRequest(
                            menu_type=MenuType.DESKTOP,
                            context=MenuContext.DESKTOP_EMPTY,
                            position=event.globalPos(),
                            widget=self,
                            extra_data={"click_pos": event.pos()}
                        )
                    
                    # Context menu'yu göster
                    success = context_menu_manager.show_context_menu(request)
                    self.logger.info(f"Context menu show result: {success}")
                    return
                else:
                    self.logger.warning("Context menu manager not found, using fallback")
            else:
                self.logger.warning("Kernel not available, using fallback")
            
            # Fallback: basit menü
            self.logger.info("Using fallback context menu")
            self._show_fallback_menu(event)
            
        except Exception as e:
            self.logger.error(f"Context menu error: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
            self._show_fallback_menu(event)
    
    def _show_fallback_menu(self, event):
        """Fallback basit menü"""
        try:
            from PyQt6.QtWidgets import QMenu
            from PyQt6.QtGui import QAction
            
            menu = QMenu(self)
            menu.setStyleSheet("""
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
                }
                
                QMenu::separator {
                    height: 1px;
                    background-color: rgba(100, 100, 100, 0.6);
                    margin: 6px 12px;
                }
            """)
            
            # Yeni menüsü
            new_menu = menu.addMenu("📄 Yeni")
            
            new_text_action = QAction("📝 Metin Belgesi", self)
            new_text_action.triggered.connect(lambda: self.create_new_file("text"))
            new_menu.addAction(new_text_action)
            
            new_python_action = QAction("🐍 Python Dosyası", self)
            new_python_action.triggered.connect(lambda: self.create_new_file("python"))
            new_menu.addAction(new_python_action)
            
            new_folder_action = QAction("📁 Klasör", self)
            new_folder_action.triggered.connect(self.create_new_folder)
            new_menu.addAction(new_folder_action)
            
            menu.addSeparator()
            
            # Yenile
            refresh_action = QAction("🔄 Yenile", self)
            refresh_action.triggered.connect(self.refresh_desktop)
            menu.addAction(refresh_action)
            
            menu.addSeparator()
            
            # Duvar kağıdı değiştir
            wallpaper_action = QAction("🖼️ Duvar Kağıdı Değiştir", self)
            wallpaper_action.triggered.connect(self.change_wallpaper)
            menu.addAction(wallpaper_action)
            
            # Özelleştir
            customize_action = QAction("🎨 Masaüstü Ayarları", self)
            customize_action.triggered.connect(self.open_desktop_settings)
            menu.addAction(customize_action)
            
            menu.exec(event.globalPos())
            
        except ImportError:
            pass
    
    def create_new_file(self, file_type: str):
        """Yeni dosya oluştur"""
        try:
            # Yeni yapıya uygun desktop path
            desktop_path = Path("pycloud_fs/home/Desktop")
            
            if file_type == "text":
                filename = "Yeni Metin Belgesi.txt"
                filepath = desktop_path / filename
                counter = 1
                while filepath.exists():
                    filename = f"Yeni Metin Belgesi ({counter}).txt"
                    filepath = desktop_path / filename
                    counter += 1
                
                # Basit içerikle dosya oluştur
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write("Bu yeni bir metin belgesidir.\n\nBuraya notlarınızı yazabilirsiniz.")
                
            elif file_type == "python":
                filename = "yeni_script.py"
                filepath = desktop_path / filename
                counter = 1
                while filepath.exists():
                    filename = f"yeni_script_{counter}.py"
                    filepath = desktop_path / filename
                    counter += 1
                
                # Python şablonu
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write('#!/usr/bin/env python3\n"""\nYeni Python Script\n"""\n\nprint("Merhaba PyCloud OS!")\n')
            
            elif file_type == "markdown":
                filename = "Not Defteri.md"
                filepath = desktop_path / filename
                counter = 1
                while filepath.exists():
                    filename = f"Not Defteri ({counter}).md"
                    filepath = desktop_path / filename
                    counter += 1
                
                # Markdown şablonu
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write("# Yeni Not\n\n## Başlık\n\nBuraya notlarınızı markdown formatında yazabilirsiniz.\n\n- Liste öğesi 1\n- Liste öğesi 2\n")
            
            # Desktop'u yenile
            self.load_desktop_items()
            self.logger.info(f"Created new file: {filepath}")
            
        except Exception as e:
            self.logger.error(f"Failed to create new file: {e}")
    
    def create_new_folder(self):
        """Yeni klasör oluştur"""
        try:
            # Yeni yapıya uygun desktop path
            desktop_path = Path("pycloud_fs/home/Desktop")
            
            folder_name = "Yeni Klasör"
            folder_path = desktop_path / folder_name
            counter = 1
            
            while folder_path.exists():
                folder_name = f"Yeni Klasör ({counter})"
                folder_path = desktop_path / folder_name
                counter += 1
            
            folder_path.mkdir()
            
            # Desktop'u yenile
            self.load_desktop_items()
            self.logger.info(f"Created new folder: {folder_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to create new folder: {e}")
    
    def open_desktop_settings(self):
        """Desktop ayarlarını aç"""
        self.logger.info("Opening desktop settings")
        try:
            # Settings uygulamasını başlat
            self.launch_app_for_file("cloud.settings", "desktop")
        except Exception as e:
            self.logger.error(f"Failed to open desktop settings: {e}")
    
    def change_wallpaper(self):
        """Duvar kağıdı değiştir"""
        try:
            if self.kernel:
                wallpaper_manager = self.kernel.get_module("wallpaper")
                if wallpaper_manager:
                    wallpaper_manager.show_wallpaper_dialog()
                else:
                    self.logger.warning("Wallpaper manager not available")
        except Exception as e:
            self.logger.error(f"Failed to change wallpaper: {e}")
    
    def get_default_app_for_file(self, file_path: str) -> str:
        """Dosya için varsayılan uygulamayı belirle"""
        file_ext = Path(file_path).suffix.lower()
        
        # Dosya uzantısına göre varsayılan uygulama
        default_apps = {
            ".txt": "cloud_notepad",
            ".md": "cloud_notepad", 
            ".py": "cloud_pyide",
            ".json": "cloud_notepad",
            ".log": "cloud_notepad",
            ".html": "cloud_browser",
            ".pdf": "cloud_browser",
        }
        
        return default_apps.get(file_ext, "cloud_notepad") 