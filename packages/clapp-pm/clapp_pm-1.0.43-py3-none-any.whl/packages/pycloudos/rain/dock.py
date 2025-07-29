"""
Rain Dock - Modern Dock Sistemi
Kullanıcıya sabit uygulamalara hızlı erişim sağlayan modern dock yapısı
macOS Big Sur/Monterey tarzında glassmorphism efektleri ile
"""

import logging
import math
from typing import List, Dict, Optional
from pathlib import Path

try:
    from PyQt6.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QLabel, 
                                QPushButton, QFrame, QScrollArea, QMenu,
                                QGraphicsDropShadowEffect, QSizePolicy, QGraphicsBlurEffect)
    from PyQt6.QtCore import (Qt, QSize, QPropertyAnimation, QEasingCurve, pyqtSignal, 
                             QTimer, QRect, QPoint, QParallelAnimationGroup, QSequentialAnimationGroup)
    from PyQt6.QtGui import (QFont, QPixmap, QAction, QPainter, QColor, QBrush, QIcon,
                            QPainterPath, QLinearGradient, QRadialGradient, QPen)
    PYQT_AVAILABLE = True
except ImportError:
    PYQT_AVAILABLE = False

class ModernDockIcon(QPushButton):
    """Modern Dock simgesi widget'ı - glassmorphism efektleri ile"""
    
    # Sinyaller
    app_launch_requested = pyqtSignal(str)  # app_id
    context_menu_requested = pyqtSignal(str, object)  # app_id, position
    
    def __init__(self, app_id: str, app_name: str, icon_path: str = None, icon_text: str = "📱", is_running: bool = False):
        super().__init__()
        
        self.app_id = app_id
        self.app_name = app_name
        self.icon_path = icon_path
        self.icon_text = icon_text
        self.is_running = is_running
        self.is_hovered = False
        
        # Animasyon değişkenleri
        self.base_size = 64
        self.hover_size = 80
        self.current_scale = 1.0
        
        self.setup_ui()
        self.setup_animations()
        self.setup_effects()
    
    def setup_ui(self):
        """UI kurulumu"""
        self.setFixedSize(self.base_size, self.base_size)
        self.setObjectName("ModernDockIcon")
        
        # İkon yükleme - daha yüksek kalite
        if self.icon_path and Path(self.icon_path).exists():
            # PNG ikon kullan
            pixmap = QPixmap(self.icon_path)
            if not pixmap.isNull():
                # İkonu ultra yüksek kalitede boyutlandır
                icon_size = int(self.base_size * 0.75)  # %75 boyut
                scaled_pixmap = pixmap.scaled(
                    icon_size, icon_size, 
                    Qt.AspectRatioMode.KeepAspectRatio, 
                    Qt.TransformationMode.SmoothTransformation
                )
                
                # Şeffaf arka plan ile temiz ikon oluştur
                clean_pixmap = QPixmap(icon_size, icon_size)
                clean_pixmap.fill(Qt.GlobalColor.transparent)
                
                painter = QPainter(clean_pixmap)
                painter.setRenderHint(QPainter.RenderHint.Antialiasing)
                painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
                
                # İkonu ortala
                x = (icon_size - scaled_pixmap.width()) // 2
                y = (icon_size - scaled_pixmap.height()) // 2
                painter.drawPixmap(x, y, scaled_pixmap)
                painter.end()
                
                self.setIcon(QIcon(clean_pixmap))
                self.setIconSize(QSize(icon_size, icon_size))
                
                # Metin temizle (sadece ikon göster)
                self.setText("")
            else:
                # Fallback: emoji
                self.setText(self.icon_text)
                self.setStyleSheet("font-size: 32px;")
        else:
            # Fallback: emoji veya metin
            self.setText(self.icon_text)
            self.setStyleSheet("font-size: 32px;")
        
        # Modern stil
        self.setStyleSheet(self._get_modern_style())
        
        # Tooltip
        self.setToolTip(self.app_name)
    
    def _get_modern_style(self) -> str:
        """Modern glassmorphism stil"""
        return f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(255, 255, 255, 0.3),
                    stop:0.5 rgba(255, 255, 255, 0.2),
                    stop:1 rgba(255, 255, 255, 0.1));
                border: 1px solid rgba(255, 255, 255, 0.3);
                border-radius: {self.base_size // 4}px;
                margin: 2px;
                padding: 0px;
            }}
            
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(255, 255, 255, 0.4),
                    stop:0.5 rgba(255, 255, 255, 0.25),
                    stop:1 rgba(255, 255, 255, 0.15));
                border: 1px solid rgba(255, 255, 255, 0.5);
            }}
            
            QPushButton:pressed {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(255, 255, 255, 0.2),
                    stop:0.5 rgba(255, 255, 255, 0.1),
                    stop:1 rgba(255, 255, 255, 0.05));
                border: 1px solid rgba(255, 255, 255, 0.4);
            }}
        """
    
    def setup_animations(self):
        """Modern animasyonları kur"""
        # Hover scale animasyonu
        self.scale_animation = QPropertyAnimation(self, b"geometry")
        self.scale_animation.setDuration(200)
        self.scale_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        # Bounce animasyonu
        self.bounce_animation = QSequentialAnimationGroup()
        
        # Yukarı bounce
        bounce_up = QPropertyAnimation(self, b"geometry")
        bounce_up.setDuration(150)
        bounce_up.setEasingCurve(QEasingCurve.Type.OutQuad)
        
        # Aşağı bounce
        bounce_down = QPropertyAnimation(self, b"geometry")
        bounce_down.setDuration(150)
        bounce_down.setEasingCurve(QEasingCurve.Type.InQuad)
        
        self.bounce_animation.addAnimation(bounce_up)
        self.bounce_animation.addAnimation(bounce_down)
    
    def setup_effects(self):
        """Görsel efektleri kur"""
        # Gölge efekti
        self.shadow_effect = QGraphicsDropShadowEffect()
        self.shadow_effect.setBlurRadius(15)
        self.shadow_effect.setColor(QColor(0, 0, 0, 80))
        self.shadow_effect.setOffset(0, 4)
        self.setGraphicsEffect(self.shadow_effect)
    
    def enterEvent(self, event):
        """Mouse hover başlangıcı - devre dışı"""
        super().enterEvent(event)
        # Hover efekti kaldırıldı
        pass
    
    def leaveEvent(self, event):
        """Mouse hover bitişi - devre dışı"""
        super().leaveEvent(event)
        # Hover efekti kaldırıldı
        pass
    
    def animate_hover(self, hover: bool):
        """Hover animasyonu - devre dışı bırakıldı"""
        # Hover efekti tamamen kaldırıldı
        # Sadece tıklama animasyonu aktif
        pass
    
    def animate_click(self):
        """Tıklama animasyonu - yukarı zıplama efekti"""
        if self.bounce_animation.state() == QSequentialAnimationGroup.State.Running:
            return
        
        current_rect = self.geometry()
        
        # Daha belirgin yukarı zıplama (20px yukarı)
        bounce_height = 20
        bounce_up_rect = QRect(
            current_rect.x(),
            current_rect.y() - bounce_height,
            current_rect.width(),
            current_rect.height()
        )
        
        # Aşağı bounce (orijinal pozisyon)
        bounce_down_rect = current_rect
        
        # Animasyonları ayarla
        bounce_up = self.bounce_animation.animationAt(0)
        bounce_down = self.bounce_animation.animationAt(1)
        
        # Yukarı zıplama - hızlı ve etkili
        bounce_up.setDuration(120)  # Daha hızlı
        bounce_up.setEasingCurve(QEasingCurve.Type.OutQuart)  # Daha etkili easing
        bounce_up.setStartValue(current_rect)
        bounce_up.setEndValue(bounce_up_rect)
        
        # Aşağı zıplama - yumuşak iniş
        bounce_down.setDuration(180)  # Biraz daha yavaş iniş
        bounce_down.setEasingCurve(QEasingCurve.Type.InQuart)  # Yumuşak iniş
        bounce_down.setStartValue(bounce_up_rect)
        bounce_down.setEndValue(bounce_down_rect)
        
        self.bounce_animation.start()
    
    def set_running_state(self, is_running: bool):
        """Çalışma durumunu ayarla"""
        if self.is_running != is_running:
            self.is_running = is_running
            self.update_running_indicator()
    
    def update_running_indicator(self):
        """Çalışma göstergesini güncelle"""
        # Bu özellik paintEvent'te implement edilecek
        self.update()
    
    def paintEvent(self, event):
        """Özel çizim - çalışma göstergesi için"""
        super().paintEvent(event)
        
        if self.is_running:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            
            # Çalışma göstergesi (alt kısımda küçük nokta)
            indicator_size = 6
            indicator_x = (self.width() - indicator_size) // 2
            indicator_y = self.height() - 8
            
            # Gradient nokta
            gradient = QRadialGradient(
                indicator_x + indicator_size // 2,
                indicator_y + indicator_size // 2,
                indicator_size // 2
            )
            gradient.setColorAt(0, QColor(255, 255, 255, 255))
            gradient.setColorAt(1, QColor(200, 200, 200, 200))
            
            painter.setBrush(QBrush(gradient))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(indicator_x, indicator_y, indicator_size, indicator_size)
            
            painter.end()
    
    def mousePressEvent(self, event):
        """Fare tıklama olayı"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.animate_click()
            self.app_launch_requested.emit(self.app_id)
        elif event.button() == Qt.MouseButton.RightButton:
            # PyQt6'da globalPosition() kullan
            try:
                global_pos = event.globalPosition().toPoint()
            except AttributeError:
                # Fallback
                global_pos = self.mapToGlobal(event.pos())
            
            self.context_menu_requested.emit(self.app_id, global_pos)
        
        super().mousePressEvent(event)

class ModernRainDock(QWidget):
    """Modern Rain UI Dock bileşeni - glassmorphism efektleri ile"""
    
    def __init__(self, kernel):
        super().__init__()
        self.kernel = kernel
        self.logger = logging.getLogger("ModernRainDock")
        
        if not PYQT_AVAILABLE:
            return
        
        self.dock_icons: List[ModernDockIcon] = []
        self.pinned_apps: List[Dict] = []
        self.running_apps: List[str] = []
        
        # Dock pozisyon ve boyut ayarları
        self.dock_height = 80
        self.dock_margin = 20
        self.icon_spacing = 12
        
        self.setup_ui()
        self.load_pinned_apps()
        self.setup_connections()
        self.setup_update_timer()
    
    def setup_ui(self):
        """Modern arayüzü kur"""
        self.setFixedHeight(self.dock_height + self.dock_margin)
        self.setStyleSheet("""
            QWidget {
                background-color: transparent;
                border: none;
            }
        """)
        
        # Ana layout
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, self.dock_margin)
        main_layout.setSpacing(0)
        
        # Sol spacer
        main_layout.addStretch()
        
        # Modern dock container
        self.dock_container = QWidget()
        self.dock_layout = QHBoxLayout(self.dock_container)
        self.dock_layout.setSpacing(self.icon_spacing)
        self.dock_layout.setContentsMargins(20, 10, 20, 10)
        
        # Modern glassmorphism dock container stili
        self.dock_container.setStyleSheet(f"""
            QWidget {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(255, 255, 255, 0.2),
                    stop:0.5 rgba(255, 255, 255, 0.15),
                    stop:1 rgba(255, 255, 255, 0.1));
                border: 1px solid rgba(255, 255, 255, 0.3);
                border-radius: {self.dock_height // 3}px;
            }}
        """)
        
        # Modern gölge efekti
        shadow_effect = QGraphicsDropShadowEffect()
        shadow_effect.setBlurRadius(25)
        shadow_effect.setColor(QColor(0, 0, 0, 60))
        shadow_effect.setOffset(0, 8)
        self.dock_container.setGraphicsEffect(shadow_effect)
        
        main_layout.addWidget(self.dock_container)
        
        # Sağ spacer
        main_layout.addStretch()
    
    def load_pinned_apps(self):
        """Sabitlenmiş uygulamaları yükle"""
        try:
            # Varsayılan sabitlenmiş uygulamalar
            default_apps = [
                {"id": "cloud_files", "name": "Dosyalar", "icon": "📁"},
                {"id": "cloud_terminal", "name": "Terminal", "icon": "💻"},
                {"id": "cloud_notepad", "name": "Notepad", "icon": "📝"},
                {"id": "cloud_browser", "name": "Tarayıcı", "icon": "🌐"},
                {"id": "cloud_pyide", "name": "Python IDE", "icon": "🐍"},
            ]
            
            # AppExplorer'dan gerçek uygulama bilgilerini al
            if self.kernel:
                app_explorer = self.kernel.get_module("appexplorer")
                if app_explorer:
                    for app_config in default_apps:
                        app_info = app_explorer.get_app_by_id(app_config["id"])
                        if app_info:
                            # PNG ikon yolunu al
                            icon_path = None
                            if app_info.app_path:
                                potential_icon = Path(app_info.app_path) / "icon.png"
                                if potential_icon.exists():
                                    icon_path = str(potential_icon)
                            
                            self.pinned_apps.append({
                                "id": app_config["id"],
                                "name": app_info.name,
                                "icon": app_config["icon"],
                                "icon_path": icon_path
                            })
                        else:
                            # Fallback
                            self.pinned_apps.append(app_config)
                else:
                    self.pinned_apps = default_apps
            else:
                self.pinned_apps = default_apps
            
            self.update_dock_icons()
            
        except Exception as e:
            self.logger.error(f"Failed to load pinned apps: {e}")
    
    def update_dock_icons(self):
        """Dock simgelerini güncelle"""
        # Mevcut simgeleri temizle
        for icon in self.dock_icons:
            icon.setParent(None)
            icon.deleteLater()
        
        self.dock_icons.clear()
        
        # Yeni simgeleri oluştur
        for app_info in self.pinned_apps:
            is_running = app_info["id"] in self.running_apps
            
            icon = ModernDockIcon(
                app_id=app_info["id"],
                app_name=app_info["name"],
                icon_path=app_info.get("icon_path"),
                icon_text=app_info["icon"],
                is_running=is_running
            )
            
            # Sinyal bağlantıları
            icon.app_launch_requested.connect(self.launch_app)
            icon.context_menu_requested.connect(self.show_app_context_menu)
            
            self.dock_layout.addWidget(icon)
            self.dock_icons.append(icon)
        
        self.logger.info(f"Updated dock with {len(self.dock_icons)} icons")
    
    def setup_connections(self):
        """Sinyal bağlantıları"""
        if self.kernel:
            # Event sistemi ile bağlantı kur
            events = self.kernel.get_module("events")
            if events:
                events.subscribe("app_launched", self.on_app_launched)
                events.subscribe("app_closed", self.on_app_closed)
    
    def setup_update_timer(self):
        """Güncelleme zamanlayıcısı"""
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_running_apps)
        self.update_timer.start(2000)  # Her 2 saniyede güncelle
    
    def update_running_apps(self):
        """Çalışan uygulamaları güncelle"""
        try:
            if self.kernel:
                launcher = self.kernel.get_module("launcher")
                if launcher:
                    running_apps = list(launcher.get_all_running_apps().keys())
                    
                    if running_apps != self.running_apps:
                        self.running_apps = running_apps
                        self.update_dock_running_states()
                        
        except Exception as e:
            self.logger.error(f"Failed to update running apps: {e}")
    
    def update_dock_running_states(self):
        """Dock simgelerinin çalışma durumlarını güncelle"""
        for icon in self.dock_icons:
            is_running = icon.app_id in self.running_apps
            icon.set_running_state(is_running)
    
    def launch_app(self, app_id: str):
        """Uygulama başlat"""
        try:
            self.logger.info(f"Launching app: {app_id}")
            
            if self.kernel:
                launcher = self.kernel.get_module("launcher")
                if launcher:
                    success = launcher.launch_app(app_id)
                    if success:
                        self.logger.info(f"App {app_id} launch requested successfully")
                    else:
                        self.logger.warning(f"Failed to launch app {app_id}")
                        self._fallback_launch(app_id)
                else:
                    self.logger.warning("Launcher module not available")
                    self._fallback_launch(app_id)
            else:
                self.logger.warning("Kernel not available")
                self._fallback_launch(app_id)
                
        except Exception as e:
            self.logger.error(f"Failed to launch app {app_id}: {e}")
            self._fallback_launch(app_id)
    
    def _fallback_launch(self, app_id: str):
        """Fallback uygulama başlatma"""
        try:
            import subprocess
            import os
            
            # Uygulama dizinini bul
            app_path = Path("apps") / app_id
            if app_path.exists():
                main_py = app_path / "main.py"
                if main_py.exists():
                    # Python ile başlat
                    subprocess.Popen([
                        "python3", str(main_py)
                    ], cwd=str(app_path))
                    
                    self.logger.info(f"Fallback launch successful for {app_id}")
                else:
                    self.logger.error(f"main.py not found for {app_id}")
            else:
                self.logger.error(f"App directory not found: {app_path}")
                
        except Exception as e:
            self.logger.error(f"Fallback launch failed for {app_id}: {e}")
    
    def show_app_context_menu(self, app_id: str, position):
        """Uygulama bağlam menüsünü göster"""
        try:
            self.logger.info(f"Showing context menu for app: {app_id}")
            
            menu = QMenu(self)
            menu.setStyleSheet("""
                QMenu {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 rgba(45, 45, 45, 0.95),
                        stop:1 rgba(35, 35, 35, 0.95));
                    border: 1px solid rgba(80, 80, 80, 0.8);
                    border-radius: 12px;
                    padding: 8px;
                    color: #ffffff;
                }
                
                QMenu::item {
                    background-color: transparent;
                    padding: 12px 20px;
                    border-radius: 8px;
                    margin: 2px;
                    color: #ffffff;
                    font-size: 14px;
                }
                
                QMenu::item:selected {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 rgba(70, 70, 70, 0.8),
                        stop:1 rgba(60, 60, 60, 0.8));
                    color: #ffffff;
                }
                
                QMenu::separator {
                    height: 1px;
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 transparent,
                        stop:0.5 rgba(100, 100, 100, 0.6),
                        stop:1 transparent);
                    margin: 6px 16px;
                }
            """)
            
            # Menü öğeleri
            if app_id in self.running_apps:
                # Çalışan uygulama menüsü
                show_action = QAction("🔍 Göster", self)
                show_action.triggered.connect(lambda: self.show_app(app_id))
                menu.addAction(show_action)
                
                close_action = QAction("❌ Kapat", self)
                close_action.triggered.connect(lambda: self.close_app(app_id))
                menu.addAction(close_action)
                
                menu.addSeparator()
                
                restart_action = QAction("🔄 Yeniden Başlat", self)
                restart_action.triggered.connect(lambda: self.restart_app(app_id))
                menu.addAction(restart_action)
            else:
                # Çalışmayan uygulama menüsü
                launch_action = QAction("🚀 Başlat", self)
                launch_action.triggered.connect(lambda: self.launch_app(app_id))
                menu.addAction(launch_action)
            
            menu.addSeparator()
            
            # Dock işlemleri
            unpin_action = QAction("📌 Dock'tan Kaldır", self)
            unpin_action.triggered.connect(lambda: self.unpin_app(app_id))
            menu.addAction(unpin_action)
            
            info_action = QAction("ℹ️ Uygulama Bilgileri", self)
            info_action.triggered.connect(lambda: self.show_app_info(app_id))
            menu.addAction(info_action)
            
            menu.exec(position)
            
        except Exception as e:
            self.logger.error(f"Failed to show context menu: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
    
    def show_app(self, app_id: str):
        """Uygulamayı göster/öne getir"""
        try:
            if self.kernel:
                window_manager = self.kernel.get_module("windowmanager")
                if window_manager:
                    windows = window_manager.get_windows_by_app(app_id)
                    if windows:
                        window_manager.focus_window(windows[0].window_id)
        except Exception as e:
            self.logger.error(f"Failed to show app {app_id}: {e}")
    
    def close_app(self, app_id: str):
        """Uygulamayı kapat"""
        try:
            if self.kernel:
                launcher = self.kernel.get_module("launcher")
                if launcher:
                    launcher.stop_app(app_id)
        except Exception as e:
            self.logger.error(f"Failed to close app {app_id}: {e}")
    
    def restart_app(self, app_id: str):
        """Uygulamayı yeniden başlat"""
        try:
            if self.kernel:
                launcher = self.kernel.get_module("launcher")
                if launcher:
                    launcher.restart_app(app_id)
        except Exception as e:
            self.logger.error(f"Failed to restart app {app_id}: {e}")
    
    def unpin_app(self, app_id: str):
        """Uygulamayı dock'tan kaldır"""
        try:
            self.pinned_apps = [app for app in self.pinned_apps if app["id"] != app_id]
            self.update_dock_icons()
            self.logger.info(f"Unpinned app: {app_id}")
        except Exception as e:
            self.logger.error(f"Failed to unpin app {app_id}: {e}")
    
    def pin_app(self, app_id: str, app_name: str, icon: str):
        """Uygulamayı dock'a sabitle"""
        try:
            # Zaten sabitlenmiş mi kontrol et
            if any(app["id"] == app_id for app in self.pinned_apps):
                return
            
            # PNG ikon yolunu bul
            icon_path = None
            if self.kernel:
                app_explorer = self.kernel.get_module("appexplorer")
                if app_explorer:
                    app_info = app_explorer.get_app_by_id(app_id)
                    if app_info and app_info.app_path:
                        potential_icon = Path(app_info.app_path) / "icon.png"
                        if potential_icon.exists():
                            icon_path = str(potential_icon)
            
            self.pinned_apps.append({
                "id": app_id,
                "name": app_name,
                "icon": icon,
                "icon_path": icon_path
            })
            
            self.update_dock_icons()
            self.logger.info(f"Pinned app: {app_id}")
            
        except Exception as e:
            self.logger.error(f"Failed to pin app {app_id}: {e}")
    
    def show_app_info(self, app_id: str):
        """Uygulama bilgilerini göster"""
        self.logger.info(f"Show app info for: {app_id}")
        # TODO: Uygulama bilgi dialogu implementasyonu
    
    def on_app_launched(self, event):
        """Uygulama başlatıldı olayı"""
        try:
            app_id = event.get("app_id")
            if app_id and app_id not in self.running_apps:
                self.running_apps.append(app_id)
                self.update_dock_running_states()
        except Exception as e:
            self.logger.error(f"Failed to handle app launched event: {e}")
    
    def on_app_closed(self, event):
        """Uygulama kapatıldı olayı"""
        try:
            app_id = event.get("app_id")
            if app_id and app_id in self.running_apps:
                self.running_apps.remove(app_id)
                self.update_dock_running_states()
        except Exception as e:
            self.logger.error(f"Failed to handle app closed event: {e}")
    
    def get_dock_config(self) -> Dict:
        """Dock konfigürasyonunu al"""
        return {
            "pinned_apps": self.pinned_apps,
            "dock_height": self.dock_height,
            "dock_margin": self.dock_margin,
            "icon_spacing": self.icon_spacing
        }
    
    def apply_dock_config(self, config: Dict):
        """Dock konfigürasyonunu uygula"""
        try:
            if "pinned_apps" in config:
                self.pinned_apps = config["pinned_apps"]
                self.update_dock_icons()
            
            if "dock_height" in config:
                self.dock_height = config["dock_height"]
                self.setFixedHeight(self.dock_height + self.dock_margin)
            
            if "dock_margin" in config:
                self.dock_margin = config["dock_margin"]
            
            if "icon_spacing" in config:
                self.icon_spacing = config["icon_spacing"]
                self.dock_layout.setSpacing(self.icon_spacing)
                
        except Exception as e:
            self.logger.error(f"Failed to apply dock config: {e}")

# Geriye uyumluluk için alias
ModernDock = ModernRainDock
RainDock = ModernRainDock  # Eski isim için de alias 