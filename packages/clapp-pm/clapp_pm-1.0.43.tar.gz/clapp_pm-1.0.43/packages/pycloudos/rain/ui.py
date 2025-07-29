"""
Rain UI - Ana Arayüz Sistemi
PyCloud OS için macOS Aqua stilinde masaüstü ortamı
"""

import sys
import logging
from typing import Optional

try:
    from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                                QHBoxLayout, QLabel, QPushButton, QScrollArea,
                                QFrame, QTextEdit, QListWidget, QListWidgetItem, QSystemTrayIcon, QMenu)
    from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QRect
    from PyQt6.QtGui import QFont, QPixmap, QPainter, QBrush, QPen, QIcon, QPalette, QColor
    from rain.topbar import RainTopbar
    PYQT_AVAILABLE = True
except ImportError as e:
    print(f"PyQt6 veya bağımlılıkları yüklenemedi: {e}")
    PYQT_AVAILABLE = False
    # Mock classes for testing
    class QApplication: pass
    class QMainWindow: pass
    class QWidget: pass
    class RainTopbar: pass

class RainUI:
    """Rain UI ana sınıfı"""
    
    def __init__(self, kernel):
        self.logger = logging.getLogger("RainUI")
        self.kernel = kernel
        self.app: Optional[QApplication] = None
        self.main_window: Optional[QMainWindow] = None
        
        # PyQt6 durum kontrolü
        self.logger.info(f"PyQt6 available: {PYQT_AVAILABLE}")
        
        if not PYQT_AVAILABLE:
            self.logger.error("PyQt6 not available, UI will not start")
            return
        
        try:
            self.initialize()
            self.logger.info("RainUI constructor completed successfully")
        except Exception as e:
            self.logger.error(f"RainUI initialization failed: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
    
    def initialize(self):
        """UI sistemini başlat"""
        try:
            # QApplication kontrol et (eğer yoksa oluştur)
            self.app = QApplication.instance()
            if self.app is None:
                self.app = QApplication(sys.argv)
                self.app.setApplicationName("PyCloud OS")
                self.app.setApplicationVersion("0.9.0-dev")
            
            # Ana pencereyi oluştur
            self.main_window = RainMainWindow(self.kernel)
            
            # Tema uygula
            self.apply_theme()
            
            self.logger.info("Rain UI initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Rain UI: {e}")
            raise
    
    def apply_theme(self):
        """Tema uygula"""
        try:
            # Temel tema ayarları
            palette = QPalette()
            
            # Koyu tema (varsayılan)
            palette.setColor(QPalette.ColorRole.Window, QColor(45, 45, 45))
            palette.setColor(QPalette.ColorRole.WindowText, QColor(255, 255, 255))
            palette.setColor(QPalette.ColorRole.Base, QColor(35, 35, 35))
            palette.setColor(QPalette.ColorRole.AlternateBase, QColor(53, 53, 53))
            palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(0, 0, 0))
            palette.setColor(QPalette.ColorRole.ToolTipText, QColor(255, 255, 255))
            palette.setColor(QPalette.ColorRole.Text, QColor(255, 255, 255))
            palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
            palette.setColor(QPalette.ColorRole.ButtonText, QColor(255, 255, 255))
            palette.setColor(QPalette.ColorRole.BrightText, QColor(255, 0, 0))
            palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
            palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
            palette.setColor(QPalette.ColorRole.HighlightedText, QColor(0, 0, 0))
            
            self.app.setPalette(palette)
            
            # CSS stilleri
            style = """
            QMainWindow {
                background-color: #2d2d2d;
                color: #ffffff;
            }
            
            QWidget {
                background-color: #2d2d2d;
                color: #ffffff;
                font-family: 'Arial', 'Helvetica', sans-serif;
                font-size: 13px;
                border: none;
            }
            
            QPushButton {
                background-color: #404040;
                border: 1px solid #555555;
                border-radius: 6px;
                padding: 8px 16px;
                color: #ffffff;
            }
            
            QPushButton:hover {
                background-color: #4a4a4a;
                border-color: #666666;
            }
            
            QPushButton:pressed {
                background-color: #363636;
            }
            
            QLabel {
                color: #ffffff;
                background-color: transparent;
            }
            
            /* Monospace text areas */
            QTextEdit, QPlainTextEdit {
                font-family: 'Courier', 'Consolas', monospace;
            }
            """
            
            self.app.setStyleSheet(style)
            
        except Exception as e:
            self.logger.error(f"Failed to apply theme: {e}")
    
    def show(self):
        """Ana pencereyi göster"""
        if not PYQT_AVAILABLE or not self.main_window:
            self.logger.error("Cannot show UI: PyQt6 not available or not initialized")
            return
        
        try:
            self.main_window.show()
            self.logger.info("Rain UI shown")
        except Exception as e:
            self.logger.error(f"Failed to show UI: {e}")
    
    def run(self) -> int:
        """UI ana döngüsünü başlat"""
        if not PYQT_AVAILABLE or not self.app:
            self.logger.error("Cannot run UI: PyQt6 not available or not initialized")
            return 1
        
        try:
            # Ana pencereyi göster
            if self.main_window:
                self.main_window.show()
            
            # Event loop'u başlat
            return self.app.exec()
            
        except Exception as e:
            self.logger.error(f"UI run error: {e}")
            return 1
    
    def shutdown(self):
        """UI sistemini kapat"""
        if self.app:
            self.app.quit()
        self.logger.info("Rain UI shutdown")

class RainMainWindow(QMainWindow):
    """Ana pencere sınıfı"""
    
    def __init__(self, kernel):
        super().__init__()
        self.kernel = kernel
        self.logger = logging.getLogger("RainMainWindow")
        
        self.setup_ui()
        self.setup_connections()
    
    def setup_ui(self):
        """Arayüzü kur"""
        self.setWindowTitle("PyCloud OS")
        self.setGeometry(100, 100, 1200, 800)
        
        # Ana widget
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        # Wallpaper'ı ana widget'a uygula
        self.apply_wallpaper_to_main_widget(main_widget)
        
        # Ana layout
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Topbar oluştur ve ekle
        self.topbar = RainTopbar(self.kernel)
        main_layout.addWidget(self.topbar)
        
        # Desktop oluştur (window manager da burada başlatılır)
        self.create_desktop(main_layout)
        
        # Topbar ve window manager entegrasyonunu kur
        if hasattr(self, 'window_manager') and self.window_manager:
            self.window_manager.set_topbar(self.topbar)
            self.logger.info("Topbar-WindowManager integration established")
        
        # Dock oluştur
        self.create_dock(main_layout)
        
        # UI hazır olduktan sonra timer'ları başlat
        QTimer.singleShot(100, self.topbar.setup_timer)
        
        self.logger.info("Rain UI initialized")
    
    def apply_wallpaper_to_main_widget(self, main_widget):
        """Ana widget'a wallpaper uygula"""
        try:
            # Wallpaper manager'dan mevcut wallpaper'ı al
            default_background = "#2d2d2d"
            background_image = ""
            
            if self.kernel:
                wallpaper_manager = self.kernel.get_module("wallpaper")
                if wallpaper_manager and wallpaper_manager.config.current_path:
                    import os
                    if os.path.exists(wallpaper_manager.config.current_path):
                        background_image = f"background-image: url('{wallpaper_manager.config.current_path}');"
            
            # Ana widget'a wallpaper uygula - dock'un altına kadar iner
            main_widget.setStyleSheet(f"""
                QWidget {{
                    background-color: {default_background};
                    {background_image}
                    background-repeat: no-repeat;
                    background-position: center;
                }}
            """)
            
        except Exception as e:
            self.logger.error(f"Failed to apply wallpaper: {e}")
    
    def create_topbar(self, parent_layout):
        """Topbar oluştur"""
        try:
            from rain.topbar import RainTopbar
            self.topbar = RainTopbar(self.kernel)
            parent_layout.addWidget(self.topbar)
        except ImportError:
            # Basit topbar
            topbar = QWidget()
            topbar.setFixedHeight(30)
            topbar.setStyleSheet("background-color: #1e1e1e; border-bottom: 1px solid #404040;")
            parent_layout.addWidget(topbar)
            self.logger.warning("Using simple topbar (rain.topbar not available)")
    
    def create_desktop(self, parent_layout):
        """Desktop alanı oluştur"""
        try:
            # Window Manager'ı başlat
            from rain.windowmanager import init_window_manager
            self.window_manager = init_window_manager(self.kernel)
            self.kernel.register_module("windowmanager", self.window_manager)
            
            # Desktop widget'ını oluştur
            try:
                from rain.desktop import RainDesktop
                self.desktop = RainDesktop(self.kernel)
                
                # Ana desktop container - artık saydam
                desktop_container = QWidget()
                
                # Desktop container saydam olsun, wallpaper ana widget'ta
                desktop_container.setStyleSheet("""
                    QWidget {
                        background-color: transparent;
                    }
                """)
                
                # Stacked layout - desktop üstte, MDI area gizli
                from PyQt6.QtWidgets import QStackedLayout
                desktop_layout = QStackedLayout(desktop_container)
                desktop_layout.setContentsMargins(0, 0, 0, 0)
                
                # Desktop widget'ını ana sayfa olarak ekle
                desktop_layout.addWidget(self.desktop)
                
                # MDI area'yı ikinci sayfa olarak ekle (gizli)
                mdi_area = self.window_manager.get_mdi_area()
                if mdi_area:
                    mdi_area.setStyleSheet("""
                        QMdiArea {
                            background-color: transparent;
                            border: none;
                        }
                    """)
                    desktop_layout.addWidget(mdi_area)
                    
                    # Window manager'a desktop container referansını ver
                    self.window_manager.desktop_container = desktop_container
                    self.window_manager.desktop_layout = desktop_layout
                    self.window_manager.show_desktop = lambda: desktop_layout.setCurrentIndex(0)
                    self.window_manager.show_windows = lambda: desktop_layout.setCurrentIndex(1)
                
                # Desktop'u varsayılan olarak göster
                desktop_layout.setCurrentIndex(0)
                
                # Desktop container'ı parent layout'a ekle - dock'tan önce
                parent_layout.addWidget(desktop_container)
                
                # Kernel'a desktop referansını ver
                self.kernel.register_module("desktop", self.desktop)
                
                self.logger.info("Desktop created successfully")
                
            except ImportError:
                # Basit desktop
                simple_desktop = QWidget()
                simple_desktop.setStyleSheet("background-color: #2d2d2d;")
                parent_layout.addWidget(simple_desktop)
                self.logger.warning("Using simple desktop (rain.desktop not available)")
                
        except ImportError:
            # Window manager yok, basit desktop
            simple_desktop = QWidget()
            simple_desktop.setStyleSheet("background-color: #2d2d2d;")
            parent_layout.addWidget(simple_desktop)
            self.logger.warning("Using simple desktop (rain.windowmanager not available)")
    
    def create_dock(self, parent_layout):
        """Dock oluştur"""
        try:
            from rain.dock import ModernDock
            self.dock = ModernDock(self.kernel)
            parent_layout.addWidget(self.dock)
        except ImportError:
            # Basit dock
            dock = QWidget()
            dock.setFixedHeight(60)
            dock.setStyleSheet("background-color: #1e1e1e; border-top: 1px solid #404040;")
            parent_layout.addWidget(dock)
            self.logger.warning("Using simple dock (rain.dock not available)")
    
    def setup_connections(self):
        """Sinyal bağlantılarını kur"""
        # Kernel olaylarını dinle
        try:
            from core.events import subscribe, SystemEvents
            subscribe(SystemEvents.SYSTEM_SHUTDOWN, self.on_system_shutdown)
            subscribe(SystemEvents.THEME_CHANGE, self.on_theme_change)
        except ImportError:
            self.logger.warning("Event system not available")
    
    def on_system_shutdown(self, event):
        """Sistem kapatma olayı"""
        self.close()
    
    def on_theme_change(self, event):
        """Tema değişikliği olayı"""
        # Temayı yeniden uygula
        if hasattr(self.parent(), 'apply_theme'):
            self.parent().apply_theme()
    
    def closeEvent(self, event):
        """Pencere kapatma olayı"""
        # Kernel'e kapatma sinyali gönder
        if self.kernel:
            self.kernel.shutdown()
        event.accept() 