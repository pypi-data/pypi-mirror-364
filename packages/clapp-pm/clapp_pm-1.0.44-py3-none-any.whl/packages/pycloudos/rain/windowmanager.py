"""
Rain Window Manager - Uygulama Pencere Yöneticisi
PyCloud OS için window management sistemi
"""

import logging
import time
from enum import Enum
from typing import Dict, List, Optional, Tuple, Callable
from dataclasses import dataclass, field
import json
from pathlib import Path
from functools import wraps

try:
    from PyQt6.QtWidgets import (QApplication, QWidget, QMainWindow, QMdiArea, 
                                QMdiSubWindow, QVBoxLayout, QHBoxLayout, 
                                QPushButton, QLabel, QFrame)
    from PyQt6.QtCore import Qt, QRect, QPoint, QSize, QTimer, pyqtSignal, QObject, QMetaObject, Q_ARG, QThread
    from PyQt6.QtGui import QPixmap, QIcon, QFont
    PYQT_AVAILABLE = True
except ImportError:
    PYQT_AVAILABLE = False
    # Dummy classes for fallback
    class QObject:
        def __init__(self): pass
    class pyqtSignal:
        def __init__(self, *args): pass
        def emit(self, *args): pass

def ensure_main_thread(func):
    """UI işlemlerini main thread'de çalıştırmak için dekoratör"""
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if not PYQT_AVAILABLE:
            return func(self, *args, **kwargs)
        
        # Ana thread kontrolü
        app = QApplication.instance()
        if app:
            current_thread = QThread.currentThread()
            main_thread = app.thread()
            
            if current_thread != main_thread:
                # Farklı thread'deyiz, main thread'e yönlendir
                # QTimer kullanarak main thread'de çalıştır
                def delayed_call():
                    try:
                        return func(self, *args, **kwargs)
                    except Exception as e:
                        self.logger.error(f"Main thread call failed: {e}")
                
                QTimer.singleShot(0, delayed_call)
                return None
            else:
                # Ana thread'deyiz, doğrudan çalıştır
                return func(self, *args, **kwargs)
        else:
            # QApplication yok, doğrudan çalıştır
            return func(self, *args, **kwargs)
    
    return wrapper

class WindowState(Enum):
    """Pencere durumları"""
    NORMAL = "normal"
    MINIMIZED = "minimized"
    MAXIMIZED = "maximized"
    FULLSCREEN = "fullscreen"
    HIDDEN = "hidden"

class WindowType(Enum):
    """Pencere türleri"""
    APPLICATION = "application"
    SYSTEM = "system"
    DIALOG = "dialog"
    POPUP = "popup"
    WIDGET = "widget"

@dataclass
class WindowInfo:
    """Pencere bilgi yapısı"""
    window_id: str
    app_id: str
    title: str
    window_type: WindowType
    state: WindowState
    geometry: QRect = field(default_factory=lambda: QRect(100, 100, 800, 600))
    z_order: int = 0
    is_active: bool = False
    is_visible: bool = True
    created_time: float = field(default_factory=time.time)
    last_focus_time: float = field(default_factory=time.time)
    icon_path: Optional[str] = None
    metadata: Dict = field(default_factory=dict)

@dataclass
class WindowConfig:
    """Pencere yöneticisi yapılandırması"""
    enable_animations: bool = True
    enable_transparency: bool = True
    enable_shadows: bool = True
    default_window_size: Tuple[int, int] = (800, 600)
    minimum_window_size: Tuple[int, int] = (300, 200)
    taskbar_height: int = 40
    titlebar_height: int = 30
    snap_threshold: int = 10
    animation_duration: int = 200

class WindowManager(QObject):
    """Ana pencere yöneticisi sınıfı"""
    
    # Sinyaller
    window_created = pyqtSignal(str)  # window_id
    window_destroyed = pyqtSignal(str)  # window_id
    window_state_changed = pyqtSignal(str, str)  # window_id, new_state
    window_focus_changed = pyqtSignal(str)  # window_id
    
    def __init__(self, kernel=None):
        super().__init__()
        self.kernel = kernel
        self.logger = logging.getLogger("WindowManager")
        
        # Pencere kayıtları
        self.windows: Dict[str, WindowInfo] = {}
        self.window_widgets: Dict[str, QWidget] = {}
        self.active_window_id: Optional[str] = None
        self.window_counter = 0
        
        # Topbar entegrasyonu
        self.topbar = None
        
        # Yapılandırma
        self.config = WindowConfig()
        self.config_file = Path("system/config/window_manager.json")
        
        # UI bileşenleri
        self.mdi_area: Optional[QMdiArea] = None
        self.taskbar: Optional[QWidget] = None
        
        # Timer'lar
        self.focus_timer = QTimer()
        self.focus_timer.timeout.connect(self._check_window_focus)
        self.focus_timer.start(100)  # 100ms
        
        # İstatistikler
        self.stats = {
            "total_windows_created": 0,
            "active_windows": 0,
            "window_switches": 0,
            "last_activity": time.time()
        }
        
        self._load_config()
        self._setup_ui()
        
        self.logger.info("Window Manager initialized")
    
    def _load_config(self):
        """Yapılandırmayı yükle"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                    
                # Config güncelle
                for key, value in config_data.items():
                    if hasattr(self.config, key):
                        setattr(self.config, key, value)
                        
                self.logger.info("Window manager config loaded")
        except Exception as e:
            self.logger.error(f"Failed to load window manager config: {e}")
    
    def _save_config(self):
        """Yapılandırmayı kaydet"""
        try:
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            
            config_data = {
                "enable_animations": self.config.enable_animations,
                "enable_transparency": self.config.enable_transparency,
                "enable_shadows": self.config.enable_shadows,
                "default_window_size": self.config.default_window_size,
                "minimum_window_size": self.config.minimum_window_size,
                "taskbar_height": self.config.taskbar_height,
                "titlebar_height": self.config.titlebar_height,
                "snap_threshold": self.config.snap_threshold,
                "animation_duration": self.config.animation_duration
            }
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
                
            self.logger.info("Window manager config saved")
        except Exception as e:
            self.logger.error(f"Failed to save window manager config: {e}")
    
    def _setup_ui(self):
        """UI bileşenlerini kur"""
        if not PYQT_AVAILABLE:
            return
            
        try:
            # MDI Area oluştur (ana pencere alanı)
            self.mdi_area = QMdiArea()
            self.mdi_area.setViewMode(QMdiArea.ViewMode.TabbedView)
            self.mdi_area.setTabsClosable(True)
            self.mdi_area.setTabsMovable(True)
            self.mdi_area.setDocumentMode(True)
            
            # Stil ayarları
            self.mdi_area.setStyleSheet("""
                QMdiArea {
                    background-color: #2d2d2d;
                    border: none;
                }
                QMdiSubWindow {
                    background-color: #3d3d3d;
                    border: 1px solid #555;
                    border-radius: 8px;
                }
                QMdiSubWindow::title {
                    background-color: #404040;
                    color: #ffffff;
                    padding: 4px 8px;
                    font-size: 13px;
                }
            """)
            
            self.logger.info("Window manager UI setup completed")
            
        except Exception as e:
            self.logger.error(f"Failed to setup window manager UI: {e}")
    
    @ensure_main_thread
    def create_window(self, app_id: str, title: str, 
                     window_type: WindowType = WindowType.APPLICATION,
                     geometry: Optional[QRect] = None,
                     icon_path: Optional[str] = None,
                     metadata: Optional[Dict] = None) -> str:
        """Yeni pencere oluştur"""
        
        # Benzersiz window ID oluştur
        self.window_counter += 1
        window_id = f"{app_id}_{self.window_counter}_{int(time.time())}"
        
        # Geometry ayarla
        if geometry is None:
            geometry = QRect(
                100 + (len(self.windows) * 30),
                100 + (len(self.windows) * 30),
                self.config.default_window_size[0],
                self.config.default_window_size[1]
            )
        
        # WindowInfo oluştur
        window_info = WindowInfo(
            window_id=window_id,
            app_id=app_id,
            title=title,
            window_type=window_type,
            state=WindowState.NORMAL,
            geometry=geometry,
            z_order=len(self.windows),
            is_active=True,
            is_visible=True,
            icon_path=icon_path,
            metadata=metadata or {}
        )
        
        # Kaydet
        self.windows[window_id] = window_info
        
        # İstatistikleri güncelle
        self.stats["total_windows_created"] += 1
        self.stats["active_windows"] = len(self.windows)
        self.stats["last_activity"] = time.time()
        
        # Aktif pencereyi ayarla
        self._set_active_window(window_id)
        
        # UI widget oluştur
        self._create_window_widget(window_id)
        
        # Desktop'tan window view'a geç (eğer varsa)
        if hasattr(self, 'show_windows'):
            self.show_windows()
        
        # Sinyal gönder
        self.window_created.emit(window_id)
        
        self.logger.info(f"Window created: {window_id} ({title})")
        return window_id
    
    @ensure_main_thread
    def _create_window_widget(self, window_id: str):
        """Pencere için UI widget oluştur"""
        if not PYQT_AVAILABLE or not self.mdi_area:
            return
            
        try:
            window_info = self.windows.get(window_id)
            if not window_info:
                return
            
            # Main thread kontrol et
            app = QApplication.instance()
            if not app or app.thread() != QObject().thread():
                # Ana thread'de değiliz, işlemi ertele
                QTimer.singleShot(100, lambda: self._create_window_widget(window_id))
                return
            
            # Sub window oluştur
            sub_window = QMdiSubWindow(self.mdi_area)
            sub_window.setWindowTitle(window_info.title)
            sub_window.resize(window_info.geometry.size())
            
            # İçerik widget'ı oluştur
            content_widget = QWidget()
            content_widget.setStyleSheet("""
                QWidget {
                    background-color: #2d2d2d;
                    color: #ffffff;
                }
            """)
            
            # Basit layout
            layout = QVBoxLayout(content_widget)
            
            # Başlık
            title_label = QLabel(window_info.title)
            title_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
            title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(title_label)
            
            # App ID bilgisi
            app_label = QLabel(f"App: {window_info.app_id}")
            app_label.setFont(QFont("Arial", 10))
            app_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            app_label.setStyleSheet("color: #888;")
            layout.addWidget(app_label)
            
            # Window ID bilgisi
            id_label = QLabel(f"Window ID: {window_id}")
            id_label.setFont(QFont("Arial", 9))
            id_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            id_label.setStyleSheet("color: #666;")
            layout.addWidget(id_label)
            
            # Pencere kontrolleri
            controls_layout = QHBoxLayout()
            
            minimize_btn = QPushButton("−")
            minimize_btn.setFixedSize(30, 30)
            minimize_btn.clicked.connect(lambda: self.minimize_window(window_id))
            controls_layout.addWidget(minimize_btn)
            
            maximize_btn = QPushButton("□")
            maximize_btn.setFixedSize(30, 30)
            maximize_btn.clicked.connect(lambda: self.toggle_maximize_window(window_id))
            controls_layout.addWidget(maximize_btn)
            
            close_btn = QPushButton("×")
            close_btn.setFixedSize(30, 30)
            close_btn.clicked.connect(lambda: self.close_window(window_id))
            controls_layout.addWidget(close_btn)
            
            layout.addLayout(controls_layout)
            layout.addStretch()
            
            # Sub window'a içeriği ayarla
            sub_window.setWidget(content_widget)
            
            # MDI area'ya ekle
            self.mdi_area.addSubWindow(sub_window)
            sub_window.show()
            
            # Widget'ı kaydet
            self.window_widgets[window_id] = sub_window
            
            self.logger.info(f"Window widget created for: {window_id}")
            
        except Exception as e:
            self.logger.error(f"Failed to create window widget for {window_id}: {e}")
            # Hata durumunda retry dene
            QTimer.singleShot(1000, lambda: self._create_window_widget(window_id))
    
    @ensure_main_thread
    def close_window(self, window_id: str) -> bool:
        """Pencereyi kapat"""
        try:
            window_info = self.windows.get(window_id)
            if not window_info:
                return False
            
            # UI widget'ı kaldır
            if window_id in self.window_widgets:
                widget = self.window_widgets[window_id]
                if widget and self.mdi_area:
                    self.mdi_area.removeSubWindow(widget)
                    widget.close()
                del self.window_widgets[window_id]
            
            # Pencere kaydını sil
            del self.windows[window_id]
            
            # Aktif pencere kontrolü
            if self.active_window_id == window_id:
                self.active_window_id = None
                # Bir sonraki pencereyi aktif yap
                if self.windows:
                    next_window_id = list(self.windows.keys())[-1]
                    self._set_active_window(next_window_id)
                else:
                    # Hiç pencere kalmadıysa topbar'ı temizle
                    if self.topbar and hasattr(self.topbar, 'on_app_focus_changed'):
                        self.topbar.on_app_focus_changed(None)
            
            # İstatistikleri güncelle
            self.stats["active_windows"] = len(self.windows)
            self.stats["last_activity"] = time.time()
            
            # Eğer hiç pencere kalmadıysa desktop'a dön
            if len(self.windows) == 0 and hasattr(self, 'show_desktop'):
                self.show_desktop()
            
            # Sinyal gönder
            self.window_destroyed.emit(window_id)
            
            self.logger.info(f"Window closed: {window_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to close window {window_id}: {e}")
            return False
    
    def minimize_window(self, window_id: str) -> bool:
        """Pencereyi küçült"""
        return self._change_window_state(window_id, WindowState.MINIMIZED)
    
    def maximize_window(self, window_id: str) -> bool:
        """Pencereyi büyüt"""
        return self._change_window_state(window_id, WindowState.MAXIMIZED)
    
    def toggle_maximize_window(self, window_id: str) -> bool:
        """Pencere büyütme/normal arası geçiş"""
        window_info = self.windows.get(window_id)
        if not window_info:
            return False
            
        new_state = (WindowState.NORMAL if window_info.state == WindowState.MAXIMIZED 
                    else WindowState.MAXIMIZED)
        return self._change_window_state(window_id, new_state)
    
    def _change_window_state(self, window_id: str, new_state: WindowState) -> bool:
        """Pencere durumunu değiştir"""
        try:
            window_info = self.windows.get(window_id)
            if not window_info:
                return False
            
            old_state = window_info.state
            window_info.state = new_state
            window_info.last_focus_time = time.time()
            
            # UI widget'ı güncelle
            if window_id in self.window_widgets:
                widget = self.window_widgets[window_id]
                if widget:
                    if new_state == WindowState.MINIMIZED:
                        widget.showMinimized()
                    elif new_state == WindowState.MAXIMIZED:
                        widget.showMaximized()
                    elif new_state == WindowState.NORMAL:
                        widget.showNormal()
                    elif new_state == WindowState.HIDDEN:
                        widget.hide()
            
            # Sinyal gönder
            self.window_state_changed.emit(window_id, new_state.value)
            
            self.logger.info(f"Window {window_id} state changed: {old_state.value} -> {new_state.value}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to change window state for {window_id}: {e}")
            return False
    
    def _set_active_window(self, window_id: str):
        """Aktif pencereyi ayarla"""
        try:
            if window_id not in self.windows:
                return
            
            # Önceki aktif pencereyi güncelle
            if self.active_window_id and self.active_window_id in self.windows:
                self.windows[self.active_window_id].is_active = False
            
            # Yeni aktif pencereyi ayarla
            self.active_window_id = window_id
            self.windows[window_id].is_active = True
            self.windows[window_id].last_focus_time = time.time()
            
            # Z-order güncelle
            max_z = max(w.z_order for w in self.windows.values()) if self.windows else 0
            self.windows[window_id].z_order = max_z + 1
            
            # Topbar'ı bilgilendir
            if self.topbar and hasattr(self.topbar, 'on_app_focus_changed'):
                app_id = self.windows[window_id].app_id
                self.topbar.on_app_focus_changed(app_id)
            
            # İstatistikler
            self.stats["window_switches"] += 1
            self.stats["last_activity"] = time.time()
            
            # Sinyal gönder
            self.window_focus_changed.emit(window_id)
            
            self.logger.debug(f"Active window set to: {window_id}")
            
        except Exception as e:
            self.logger.error(f"Failed to set active window {window_id}: {e}")
    
    def _check_window_focus(self):
        """Pencere focus durumunu kontrol et"""
        if not PYQT_AVAILABLE or not self.mdi_area:
            return
            
        try:
            active_sub_window = self.mdi_area.activeSubWindow()
            if active_sub_window:
                # Aktif sub window'u bul
                for window_id, widget in self.window_widgets.items():
                    if widget == active_sub_window and window_id != self.active_window_id:
                        self._set_active_window(window_id)
                        break
        except Exception as e:
            self.logger.debug(f"Focus check error: {e}")
    
    def get_window_info(self, window_id: str) -> Optional[WindowInfo]:
        """Pencere bilgisini al"""
        return self.windows.get(window_id)
    
    def get_all_windows(self) -> Dict[str, WindowInfo]:
        """Tüm pencereleri al"""
        return self.windows.copy()
    
    def get_windows_by_app(self, app_id: str) -> List[WindowInfo]:
        """Uygulamaya ait pencereleri al"""
        return [w for w in self.windows.values() if w.app_id == app_id]
    
    def get_active_window(self) -> Optional[WindowInfo]:
        """Aktif pencereyi al"""
        if self.active_window_id:
            return self.windows.get(self.active_window_id)
        return None
    
    def get_mdi_area(self) -> Optional[QMdiArea]:
        """MDI Area widget'ını al"""
        return self.mdi_area
    
    def get_stats(self) -> Dict:
        """İstatistikleri al"""
        return self.stats.copy()
    
    def shutdown(self):
        """Modül kapatma"""
        try:
            # Tüm pencereleri kapat
            window_ids = list(self.windows.keys())
            for window_id in window_ids:
                self.close_window(window_id)
            
            # Timer'ları durdur
            if hasattr(self, 'focus_timer'):
                self.focus_timer.stop()
            
            # Config kaydet
            self._save_config()
            
            self.logger.info("Window manager shutdown completed")
            
        except Exception as e:
            self.logger.error(f"Error during window manager shutdown: {e}")
    
    def set_topbar(self, topbar):
        """Topbar referansını ayarla"""
        self.topbar = topbar
        self.logger.info("Topbar reference set in window manager")

# Global window manager instance
_window_manager = None

def init_window_manager(kernel=None) -> WindowManager:
    """Window manager'ı başlat"""
    global _window_manager
    if _window_manager is None:
        _window_manager = WindowManager(kernel)
    return _window_manager

def get_window_manager() -> Optional[WindowManager]:
    """Window manager'ı al"""
    return _window_manager 