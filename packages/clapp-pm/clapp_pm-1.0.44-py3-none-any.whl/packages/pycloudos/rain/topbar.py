"""
Rain Topbar - Modern Üst Çubuk Bileşeni
Sistem kontrol butonları, saat, bildirimler, denetim merkezi
macOS Big Sur/Monterey tarzında modern tasarım
HTML widget'ları ile hibrit yaklaşım
"""

import logging
from datetime import datetime
from typing import Optional
from pathlib import Path

try:
    from PyQt6.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, 
                                QMenu, QSystemTrayIcon, QSpacerItem, QSizePolicy, QApplication,
                                QFrame, QSlider, QCheckBox, QGraphicsDropShadowEffect, QScrollArea)
    from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QPropertyAnimation, QEasingCurve, QRect, QSize
    from PyQt6.QtGui import QFont, QIcon, QPixmap, QAction, QPainter, QColor
    PYQT_AVAILABLE = True
except ImportError:
    PYQT_AVAILABLE = False

# HTML widget'larını import et
try:
    from rain.flet_html_widgets import (
        HTMLNotificationWidget, HTMLClockWidget, 
        HTMLControlCenterWidget, HTMLCloudSearchWidget
    )
    HTML_WIDGETS_AVAILABLE = True
except ImportError:
    HTML_WIDGETS_AVAILABLE = False

class RainTopbar(QWidget):
    """Rain UI Topbar bileşeni - HTML widget'ları ile hibrit"""
    
    # Sinyaller
    cloud_menu_requested = pyqtSignal()
    settings_requested = pyqtSignal()
    shutdown_requested = pyqtSignal()
    
    def __init__(self, kernel):
        super().__init__()
        self.kernel = kernel
        self.logger = logging.getLogger("RainTopbar")
        
        if not PYQT_AVAILABLE:
            return
        
        self.setup_ui()
        self.setup_timer()
        self.setup_connections()
        
    def setup_ui(self):
        """macOS tarzında tek parça topbar arayüzü"""
        self.setFixedHeight(28)  # macOS topbar yüksekliği
        
        # macOS tarzında tek parça topbar stili - renk gradyanı tüm topbar'da
        self.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(240, 240, 240, 0.98),
                    stop:1 rgba(220, 220, 220, 0.98));
                border-bottom: 1px solid rgba(180, 180, 180, 0.8);
                color: #333333;
            }
            
            QPushButton {
                background: transparent;
                border: none;
                padding: 4px 12px;
                color: #333333;
                font-size: 13px;
                font-weight: 500;
                border-radius: 4px;
            }
            
            QPushButton:hover {
                background: rgba(0, 0, 0, 0.1);
            }
            
            QPushButton:pressed {
                background: rgba(0, 0, 0, 0.2);
            }
            
            QLabel {
                color: #333333;
                font-size: 13px;
                background-color: transparent;
                font-weight: 500;
            }
        """)
        
        # Ana layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 0, 8, 0)
        layout.setSpacing(0)
        
        # Sol taraf - Sabit sistem butonları
        left_widget = QWidget()
        left_widget.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(240, 240, 240, 0.98),
                    stop:1 rgba(220, 220, 220, 0.98));
            }
        """)
        left_layout = QHBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(0)
        
        # PyCloud butonu (Apple logosu gibi)
        self.cloud_button = QPushButton("☁️")
        self.cloud_button.setFixedWidth(40)
        self.cloud_button.setStyleSheet("""
            QPushButton {
                font-size: 16px;
                padding: 4px 8px;
                text-align: center;
                background: transparent;
            }
        """)
        self.cloud_button.clicked.connect(self.show_cloud_menu)
        left_layout.addWidget(self.cloud_button)
        
        # Uygulamalar butonu
        self.apps_button = QPushButton("Uygulamalar")
        self.apps_button.setStyleSheet("""
            QPushButton {
                background: transparent;
            }
        """)
        self.apps_button.clicked.connect(self.show_applications)
        left_layout.addWidget(self.apps_button)
        
        layout.addWidget(left_widget)
        
        # Orta kısım - Dinamik uygulama menüleri
        self.app_menu_widget = QWidget()
        self.app_menu_widget.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(240, 240, 240, 0.98),
                    stop:1 rgba(220, 220, 220, 0.98));
            }
        """)
        self.app_menu_layout = QHBoxLayout(self.app_menu_widget)
        self.app_menu_layout.setContentsMargins(20, 0, 20, 0)
        self.app_menu_layout.setSpacing(0)
        
        # Varsayılan boş durum
        self.clear_app_menus()
        
        layout.addWidget(self.app_menu_widget)
        
        # Esnek alan - orta kısmı genişletmek için
        layout.addStretch()
        
        # Sağ taraf - Sabit sistem kontrolleri - daha geniş alan
        right_widget = QWidget()
        right_widget.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(240, 240, 240, 0.98),
                    stop:1 rgba(220, 220, 220, 0.98));
            }
        """)
        right_layout = QHBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(12)  # Widget'lar arası boşluk artırıldı
        
        # Sistem durumu
        self.system_status = QLabel("●")
        self.system_status.setStyleSheet("""
            QLabel {
                color: #00aa00;
                font-size: 12px;
                background: transparent;
            }
        """)
        self.system_status.setToolTip("Sistem Durumu: Çalışıyor")
        right_layout.addWidget(self.system_status)
        
        # CloudSearch butonu - yeni eklenen
        self.cloudsearch_button = QPushButton("🔍")
        self.cloudsearch_button.setMinimumWidth(35)
        self.cloudsearch_button.setStyleSheet("""
            QPushButton {
                background: transparent;
                min-width: 35px;
                text-align: center;
                font-size: 14px;
            }
        """)
        self.cloudsearch_button.clicked.connect(self.show_flet_cloudsearch_widget)
        self.cloudsearch_button.setToolTip("CloudSearch - Dosya ve İçerik Arama")
        # Özel ikon yükleme
        self.load_cloudsearch_icon()
        right_layout.addWidget(self.cloudsearch_button)
        
        # Saat butonu - daha geniş alan
        self.clock_button = QPushButton()
        self.clock_button.setMinimumWidth(120)  # Yatay düzen için daha geniş
        self.clock_button.setStyleSheet("""
            QPushButton {
                font-weight: 600;
                padding: 4px 12px;
                background: transparent;
                min-width: 120px;
                text-align: center;
                font-size: 12px;
            }
        """)
        self.clock_button.clicked.connect(self.show_flet_clock_widget)
        self.update_clock()
        right_layout.addWidget(self.clock_button)
        
        # Bildirimler butonu - daha geniş alan
        self.notifications_button = QPushButton("🔔")
        self.notifications_button.setMinimumWidth(35)  # Genişlik artırıldı
        self.notifications_button.setStyleSheet("""
            QPushButton {
                background: transparent;
                min-width: 35px;
                text-align: center;
            }
        """)
        self.notifications_button.clicked.connect(self.show_flet_notification_widget)
        # Özel ikon yükleme
        self.load_notification_icon()
        right_layout.addWidget(self.notifications_button)
        
        # Denetim merkezi butonu - daha geniş alan
        self.control_center_button = QPushButton("⚙️")
        self.control_center_button.setMinimumWidth(35)  # Genişlik artırıldı
        self.control_center_button.setStyleSheet("""
            QPushButton {
                background: transparent;
                min-width: 35px;
                text-align: center;
            }
        """)
        self.control_center_button.clicked.connect(self.show_flet_control_center_widget)
        # Özel ikon yükleme
        self.load_control_center_icon()
        right_layout.addWidget(self.control_center_button)
        
        layout.addWidget(right_widget)
        
        # Widget'ları başlat
        self.current_app_id = None
    
    def setup_timer(self):
        """Zamanlayıcıları kur"""
        from PyQt6.QtWidgets import QApplication
        
        # QApplication kontrolü
        if QApplication.instance() is None:
            self.logger.warning("QApplication not ready for timers")
            return
        
        try:
            # Saat güncelleyici
            self.clock_timer = QTimer(self)
            self.clock_timer.timeout.connect(self.update_clock)
            self.clock_timer.start(1000)  # Her saniye
            
            # Sistem durumu güncelleyici
            self.status_timer = QTimer(self)
            self.status_timer.timeout.connect(self.update_system_status)
            self.status_timer.start(5000)  # Her 5 saniye
            
            self.logger.info("Topbar timers started successfully")
            
        except Exception as e:
            self.logger.error(f"Timer setup failed: {e}")
    
    def cleanup(self):
        """Temizlik işlemleri"""
        try:
            # Tüm HTML widget'ları gizle
            self.hide_all_html_widgets()
            
            # Timer'ları durdur
            if hasattr(self, 'clock_timer') and self.clock_timer:
                self.clock_timer.stop()
                self.clock_timer.deleteLater()
                self.clock_timer = None
            
            if hasattr(self, 'status_timer') and self.status_timer:
                self.status_timer.stop()
                self.status_timer.deleteLater()
                self.status_timer = None
                
        except Exception as e:
            self.logger.error(f"Cleanup failed: {e}")
            pass
    
    def setup_connections(self):
        """Sinyal bağlantılarını kur"""
        try:
            from core.events import subscribe, SystemEvents
            subscribe(SystemEvents.USER_LOGIN, self.on_user_login)
            subscribe(SystemEvents.USER_LOGOUT, self.on_user_logout)
            subscribe(SystemEvents.NOTIFICATION_SHOW, self.on_notification)
        except ImportError:
            self.logger.warning("Event system not available")
    
    def update_clock(self):
        """Saati güncelle"""
        try:
            # Widget'ın hala geçerli olup olmadığını kontrol et
            if not hasattr(self, 'clock_button') or not self.clock_button:
                return
            
            # Widget'ın silinip silinmediğini kontrol et
            try:
                # Widget'a erişmeye çalış
                self.clock_button.isVisible()
            except (RuntimeError, AttributeError):
                # Widget silinmiş, timer'ı durdur
                if hasattr(self, 'clock_timer') and self.clock_timer:
                    self.clock_timer.stop()
                return
            
            now = datetime.now()
            time_str = now.strftime("%H:%M")
            date_str = now.strftime("%d %b")
            
            # QLabel'ın hala geçerli olduğunu kontrol et
            try:
                # Yatay düzen - saat ve tarih yan yana
                self.clock_button.setText(f"{time_str}  {date_str}")
            except (RuntimeError, AttributeError):
                # Widget silinmiş, timer'ı durdur
                if hasattr(self, 'clock_timer') and self.clock_timer:
                    self.clock_timer.stop()
                return
            
        except Exception as e:
            self.logger.error(f"Failed to update clock: {e}")
    
    def update_system_status(self):
        """Sistem durumunu güncelle"""
        if self.kernel and self.kernel.running:
            uptime = self.kernel.get_uptime()
            hours = int(uptime // 3600)
            minutes = int((uptime % 3600) // 60)
            
            self.system_status.setStyleSheet("color: #00ff00; font-size: 16px;")
            self.system_status.setToolTip(f"Sistem Durumu: Çalışıyor\nÇalışma Süresi: {hours:02d}:{minutes:02d}")
        else:
            self.system_status.setStyleSheet("color: #ff0000; font-size: 16px;")
            self.system_status.setToolTip("Sistem Durumu: Hata")
    
    def show_cloud_menu(self):
        """Bulut menüsünü göster"""
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: rgba(45, 45, 45, 0.95);
                border: 1px solid rgba(80, 80, 80, 0.8);
                border-radius: 8px;
                padding: 6px;
                min-width: 250px;
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
        
        # Uygulamalar
        apps_action = QAction("📱 Uygulamalar", self)
        apps_action.triggered.connect(self.show_applications)
        menu.addAction(apps_action)
        
        # App Store
        appstore_action = QAction("🏪 App Store", self)
        appstore_action.triggered.connect(self.show_appstore)
        menu.addAction(appstore_action)
        
        menu.addSeparator()
        
        # Dosyalar
        files_action = QAction("📁 Dosyalar", self)
        files_action.triggered.connect(self.show_files)
        menu.addAction(files_action)
        
        # Terminal
        terminal_action = QAction("💻 Terminal", self)
        terminal_action.triggered.connect(self.show_terminal)
        menu.addAction(terminal_action)
        
        menu.addSeparator()
        
        # Sistem Ayarları
        settings_action = QAction("⚙️ Sistem Ayarları", self)
        settings_action.triggered.connect(self.show_settings)
        menu.addAction(settings_action)
        
        # Görev Yöneticisi
        taskmanager_action = QAction("📊 Görev Yöneticisi", self)
        taskmanager_action.triggered.connect(self.show_task_manager)
        menu.addAction(taskmanager_action)
        
        menu.addSeparator()
        
        # Yeniden Başlat
        restart_action = QAction("🔄 Yeniden Başlat", self)
        restart_action.triggered.connect(self.restart_system)
        menu.addAction(restart_action)
        
        # Kapat
        shutdown_action = QAction("⏻ Kapat", self)
        shutdown_action.triggered.connect(self.shutdown_system)
        menu.addAction(shutdown_action)
        
        # Menüyü göster
        button_rect = self.cloud_button.geometry()
        menu.exec(self.mapToGlobal(button_rect.bottomLeft()))
    
    def show_user_menu(self):
        """Kullanıcı menüsünü göster"""
        menu = QMenu(self)
        menu.setStyleSheet(self.cloud_button.parent().styleSheet())
        
        # Mevcut kullanıcı bilgisi
        current_user = None
        if self.kernel:
            user_manager = self.kernel.get_module("users")
            if user_manager:
                current_user = user_manager.get_current_user()
        
        if current_user:
            user_info = QAction(f"👤 {current_user.display_name}", self)
            user_info.setEnabled(False)
            menu.addAction(user_info)
            
            menu.addSeparator()
        
        # Profil Ayarları
        profile_action = QAction("👤 Profil Ayarları", self)
        profile_action.triggered.connect(self.show_profile_settings)
        menu.addAction(profile_action)
        
        # Kullanıcı Değiştir
        switch_action = QAction("🔄 Kullanıcı Değiştir", self)
        switch_action.triggered.connect(self.switch_user)
        menu.addAction(switch_action)
        
        # Çıkış Yap
        logout_action = QAction("🚪 Çıkış Yap", self)
        logout_action.triggered.connect(self.logout_user)
        menu.addAction(logout_action)
        
        # Menüyü göster
        button_rect = self.control_center_button.geometry()
        menu.exec(self.mapToGlobal(button_rect.bottomLeft()))
    
    def show_notifications(self):
        """Bildirimleri göster"""
        self.logger.info("Notifications requested")
        
        # Test bildirimleri göster
        try:
            notify_manager = self.kernel.get_module("notify")
            if notify_manager:
                from core.notify import NotificationType, NotificationPriority
                
                # Bilgi bildirimi
                notify_manager.show_notification(
                    "Sistem Bildirimi",
                    "PyCloud OS bildirim sistemi test ediliyor!",
                    NotificationType.INFO,
                    NotificationPriority.NORMAL,
                    source="Topbar"
                )
                
                # Başarı bildirimi
                notify_manager.show_notification(
                    "İşlem Başarılı",
                    "Bildirim sistemi başarıyla çalışıyor.",
                    NotificationType.SUCCESS,
                    NotificationPriority.HIGH,
                    source="Topbar"
                )
                
                # Uyarı bildirimi
                notify_manager.show_notification(
                    "Dikkat",
                    "Bu bir test uyarı bildirimidir.",
                    NotificationType.WARNING,
                    NotificationPriority.NORMAL,
                    source="Topbar"
                )
        
        except Exception as e:
            self.logger.error(f"Failed to show test notifications: {e}")
        
        # TODO: Bildirim geçmişi paneli
    
    def show_applications(self):
        """Uygulamaları göster"""
        self.logger.info("Applications requested")
        # Uygulama listesi menüsü göster - App Explorer kullan
        try:
            if self.kernel:
                app_explorer = self.kernel.get_module("appexplorer")
                if app_explorer:
                    self.show_app_explorer_menu()
                else:
                    # Fallback: App Store aç
                    self._launch_app("app_store")
            else:
                self._launch_app("app_store")
        except Exception as e:
            self.logger.error(f"Failed to show applications: {e}")
            self._launch_app("app_store")
    
    def show_app_explorer_menu(self):
        """App Explorer menüsünü göster"""
        try:
            app_explorer = self.kernel.get_module("appexplorer")
            if not app_explorer:
                return
            
            menu = QMenu(self)
            menu.setStyleSheet("""
                QMenu {
                    background-color: rgba(45, 45, 45, 0.95);
                    border: 1px solid rgba(80, 80, 80, 0.8);
                    border-radius: 8px;
                    padding: 6px;
                    min-width: 250px;
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
            
            # Kategori bazlı uygulamalar
            all_apps = app_explorer.get_all_apps()
            categories = {}
            
            # Uygulamaları kategorilere ayır
            for app in all_apps:
                if app.status.value == "indexed":  # Sadece geçerli uygulamalar
                    category = app.category or "Diğer"
                    if category not in categories:
                        categories[category] = []
                    categories[category].append(app)
            
            # Her kategori için alt menü oluştur
            for category, apps in sorted(categories.items()):
                if apps:  # Boş kategorileri atla
                    category_menu = menu.addMenu(f"📁 {category}")
                    category_menu.setStyleSheet(menu.styleSheet())
                    
                    # Kategorideki uygulamaları listele (en fazla 10 tane)
                    for app in sorted(apps, key=lambda x: x.name)[:10]:
                        # İkon yükle
                        icon = QIcon()
                        if app.icon_path and Path(app.icon_path).exists():
                            pixmap = QPixmap(app.icon_path)
                            if not pixmap.isNull():
                                # İkonu yüksek kalitede 16x16 boyutuna getir
                                scaled_pixmap = pixmap.scaled(
                                    16, 16, 
                                    Qt.AspectRatioMode.KeepAspectRatio, 
                                    Qt.TransformationMode.SmoothTransformation
                                )
                                
                                # Şeffaf arka plan ile temiz ikon oluştur
                                clean_pixmap = QPixmap(16, 16)
                                clean_pixmap.fill(Qt.GlobalColor.transparent)
                                
                                from PyQt6.QtGui import QPainter
                                painter = QPainter(clean_pixmap)
                                painter.setRenderHint(QPainter.RenderHint.Antialiasing)
                                painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
                                
                                # İkonu ortala
                                x = (16 - scaled_pixmap.width()) // 2
                                y = (16 - scaled_pixmap.height()) // 2
                                painter.drawPixmap(x, y, scaled_pixmap)
                                painter.end()
                                
                                icon = QIcon(clean_pixmap)
                        
                        # Action oluştur
                        app_action = QAction(app.name, self)
                        if not icon.isNull():
                            app_action.setIcon(icon)
                        app_action.triggered.connect(lambda checked, app_id=app.app_id: self._launch_app(app_id))
                        category_menu.addAction(app_action)
                    
                    # Çok fazla uygulama varsa "Daha fazla..." ekle
                    if len(apps) > 10:
                        more_action = QAction(f"... ve {len(apps) - 10} daha", self)
                        more_action.triggered.connect(lambda: self._launch_app("app_store"))
                        category_menu.addAction(more_action)
            
            # Hiç uygulama yoksa
            if not categories:
                no_apps_action = QAction("Hiç uygulama bulunamadı", self)
                no_apps_action.setEnabled(False)
                menu.addAction(no_apps_action)
            
            menu.addSeparator()
            
            # App Store'u aç
            appstore_action = QAction("🏪 App Store'u Aç", self)
            appstore_action.triggered.connect(lambda: self._launch_app("app_store"))
            menu.addAction(appstore_action)
            
            # Uygulamaları yenile
            refresh_action = QAction("🔄 Uygulamaları Yenile", self)
            refresh_action.triggered.connect(self.refresh_app_explorer)
            menu.addAction(refresh_action)
            
            # Menüyü göster
            button_pos = self.cloud_button.mapToGlobal(self.cloud_button.rect().bottomLeft())
            menu.exec(button_pos)
            
        except Exception as e:
            self.logger.error(f"Failed to show app explorer menu: {e}")
    
    def refresh_app_explorer(self):
        """App Explorer'ı yenile"""
        try:
            app_explorer = self.kernel.get_module("appexplorer")
            if app_explorer:
                app_explorer.force_discovery()
                self.logger.info("App explorer refreshed")
        except Exception as e:
            self.logger.error(f"Failed to refresh app explorer: {e}")
    
    def show_appstore(self):
        """App Store'u göster"""
        self.logger.info("App Store requested")
        self._launch_app("app_store")
    
    def show_files(self):
        """Dosya yöneticisini göster"""
        self.logger.info("File manager requested")
        self._launch_app("cloud_files")
    
    def show_terminal(self):
        """Terminal'i göster"""
        self.logger.info("Terminal requested")
        self._launch_app("cloud_terminal")
    
    def show_task_manager(self):
        """Görev yöneticisini göster"""
        self.logger.info("Task manager requested")
        self._launch_app("cloud_taskmanager")
    
    def show_profile_settings(self):
        """Profil ayarlarını göster"""
        self.logger.info("Profile settings requested")
        # TODO: Profil ayarları implementasyonu
    
    def switch_user(self):
        """Kullanıcı değiştir"""
        self.logger.info("User switch requested")
        # TODO: Kullanıcı değiştirme implementasyonu
    
    def logout_user(self):
        """Kullanıcı çıkışı"""
        self.logger.info("User logout requested")
        if self.kernel:
            user_manager = self.kernel.get_module("users")
            if user_manager:
                user_manager.logout()
    
    def restart_system(self):
        """Sistemi yeniden başlat"""
        self.logger.info("System restart requested")
        if self.kernel:
            self.kernel.restart()
    
    def shutdown_system(self):
        """Sistemi kapat"""
        self.logger.info("System shutdown requested")
        self.shutdown_requested.emit()
        if self.kernel:
            self.kernel.shutdown()
    
    def on_user_login(self, event):
        """Kullanıcı giriş olayı"""
        username = event.data.get("username", "")
        self.control_center_button.setText(f"👤 {username}")
        self.logger.info(f"User logged in: {username}")
    
    def on_user_logout(self, event):
        """Kullanıcı çıkış olayı"""
        self.control_center_button.setText("👤 Giriş Yap")
        self.logger.info("User logged out")
    
    def on_notification(self, event):
        """Bildirim olayı"""
        # Bildirim sayısını güncelle
        # TODO: Bildirim sayacı implementasyonu
        pass 
    
    def _launch_app(self, app_id: str):
        """Uygulama başlat"""
        try:
            if self.kernel:
                launcher = self.kernel.get_module("launcher")
                if launcher:
                    launcher.launch_app(app_id)
                    self.logger.info(f"Launched app: {app_id}")
                else:
                    self.logger.error("Launcher module not available")
            else:
                self.logger.error("Kernel not available")
        except Exception as e:
            self.logger.error(f"Failed to launch app {app_id}: {e}")
    
    def show_settings(self):
        """Ayarları göster"""
        self.logger.info("Settings requested")
        self._launch_app("cloud_settings")

    def clear_app_menus(self):
        """Uygulama menülerini temizle"""
        # Mevcut widget'ları temizle
        for i in reversed(range(self.app_menu_layout.count())):
            child = self.app_menu_layout.itemAt(i).widget()
            if child:
                child.setParent(None)
        
        # Varsayılan boş durum mesajı
        empty_label = QLabel("PyCloud OS")
        empty_label.setStyleSheet("""
            QLabel {
                color: #666666;
                font-weight: 600;
                padding: 4px 12px;
            }
        """)
        self.app_menu_layout.addWidget(empty_label)
    
    def set_app_menus(self, app_id: str, menus: list):
        """Belirli bir uygulama için menüleri ayarla"""
        if self.current_app_id == app_id:
            return  # Zaten aynı uygulama
        
        self.current_app_id = app_id
        
        # Mevcut menüleri temizle
        for i in reversed(range(self.app_menu_layout.count())):
            child = self.app_menu_layout.itemAt(i).widget()
            if child:
                child.setParent(None)
        
        # Uygulama adını ekle
        app_name_label = QLabel(self.get_app_display_name(app_id))
        app_name_label.setStyleSheet("""
            QLabel {
                color: #333333;
                font-weight: bold;
                padding: 4px 12px;
            }
        """)
        self.app_menu_layout.addWidget(app_name_label)
        
        # Menü butonlarını ekle
        for menu_item in menus:
            menu_button = QPushButton(menu_item['title'])
            if 'action' in menu_item:
                menu_button.clicked.connect(menu_item['action'])
            self.app_menu_layout.addWidget(menu_button)
    
    def get_app_display_name(self, app_id: str) -> str:
        """Uygulama ID'sinden görünen adı al"""
        app_names = {
            'cloud_files': 'Dosyalar',
            'cloud_browser': 'Tarayıcı',
            'cloud_terminal': 'Terminal',
            'cloud_notepad': 'Not Defteri',
            'cloud_pyide': 'Python IDE',
            'cloud_settings': 'Ayarlar',
            'cloud_taskmanager': 'Görev Yöneticisi'
        }
        return app_names.get(app_id, app_id)
    
    def on_app_focus_changed(self, app_id: str):
        """Uygulama odağı değiştiğinde çağrılır"""
        if not app_id:
            self.clear_app_menus()
            return
        
        # Uygulamaya özel menüleri ayarla
        if app_id == 'cloud_files':
            self.set_files_menus()
        elif app_id == 'cloud_browser':
            self.set_browser_menus()
        elif app_id == 'cloud_terminal':
            self.set_terminal_menus()
        elif app_id == 'cloud_notepad':
            self.set_notepad_menus()
        elif app_id == 'cloud_pyide':
            self.set_pyide_menus()
        elif app_id == 'cloud_settings':
            self.set_settings_menus()
        else:
            # Genel uygulama menüleri
            self.set_generic_app_menus(app_id)
    
    def set_files_menus(self):
        """Dosyalar uygulaması için menüler"""
        menus = [
            {'title': 'Dosya', 'action': self.show_file_menu},
            {'title': 'Düzenle', 'action': self.show_edit_menu},
            {'title': 'Görünüm', 'action': self.show_view_menu},
            {'title': 'Git', 'action': self.show_go_menu},
            {'title': 'Pencere', 'action': self.show_window_menu}
        ]
        self.set_app_menus('cloud_files', menus)
    
    def set_browser_menus(self):
        """Tarayıcı uygulaması için menüler"""
        menus = [
            {'title': 'Dosya', 'action': self.show_browser_file_menu},
            {'title': 'Düzenle', 'action': self.show_browser_edit_menu},
            {'title': 'Görünüm', 'action': self.show_browser_view_menu},
            {'title': 'Geçmiş', 'action': self.show_browser_history_menu},
            {'title': 'Yer İmleri', 'action': self.show_browser_bookmarks_menu},
            {'title': 'Pencere', 'action': self.show_window_menu}
        ]
        self.set_app_menus('cloud_browser', menus)
    
    def set_terminal_menus(self):
        """Terminal uygulaması için menüler"""
        menus = [
            {'title': 'Terminal', 'action': self.show_terminal_menu},
            {'title': 'Düzenle', 'action': self.show_edit_menu},
            {'title': 'Görünüm', 'action': self.show_view_menu},
            {'title': 'Pencere', 'action': self.show_window_menu}
        ]
        self.set_app_menus('cloud_terminal', menus)
    
    def set_notepad_menus(self):
        """Not Defteri uygulaması için menüler"""
        menus = [
            {'title': 'Dosya', 'action': self.show_notepad_file_menu},
            {'title': 'Düzenle', 'action': self.show_notepad_edit_menu},
            {'title': 'Format', 'action': self.show_notepad_format_menu},
            {'title': 'Görünüm', 'action': self.show_view_menu}
        ]
        self.set_app_menus('cloud_notepad', menus)
    
    def set_pyide_menus(self):
        """Python IDE uygulaması için menüler"""
        menus = [
            {'title': 'Dosya', 'action': self.show_pyide_file_menu},
            {'title': 'Düzenle', 'action': self.show_pyide_edit_menu},
            {'title': 'Görünüm', 'action': self.show_view_menu},
            {'title': 'Çalıştır', 'action': self.show_pyide_run_menu},
            {'title': 'Araçlar', 'action': self.show_pyide_tools_menu}
        ]
        self.set_app_menus('cloud_pyide', menus)
    
    def set_settings_menus(self):
        """Ayarlar uygulaması için menüler"""
        menus = [
            {'title': 'Ayarlar', 'action': self.show_settings_menu},
            {'title': 'Görünüm', 'action': self.show_view_menu}
        ]
        self.set_app_menus('cloud_settings', menus)
    
    def set_generic_app_menus(self, app_id: str):
        """Genel uygulama menüleri"""
        menus = [
            {'title': 'Dosya', 'action': self.show_file_menu},
            {'title': 'Düzenle', 'action': self.show_edit_menu},
            {'title': 'Görünüm', 'action': self.show_view_menu}
        ]
        self.set_app_menus(app_id, menus)
    
    # Menü action metodları
    def show_file_menu(self):
        """Dosya menüsünü göster"""
        self.logger.info("File menu requested")
        # TODO: Dosya menüsü implementasyonu
    
    def show_edit_menu(self):
        """Düzenle menüsünü göster"""
        self.logger.info("Edit menu requested")
        # TODO: Düzenle menüsü implementasyonu
    
    def show_view_menu(self):
        """Görünüm menüsünü göster"""
        self.logger.info("View menu requested")
        # TODO: Görünüm menüsü implementasyonu
    
    def show_go_menu(self):
        """Git menüsünü göster"""
        self.logger.info("Go menu requested")
        # TODO: Git menüsü implementasyonu
    
    def show_window_menu(self):
        """Pencere menüsünü göster"""
        self.logger.info("Window menu requested")
        # TODO: Pencere menüsü implementasyonu
    
    def show_browser_file_menu(self):
        """Tarayıcı dosya menüsünü göster"""
        self.logger.info("Browser file menu requested")
        # TODO: Tarayıcı dosya menüsü implementasyonu
    
    def show_browser_edit_menu(self):
        """Tarayıcı düzenle menüsünü göster"""
        self.logger.info("Browser edit menu requested")
        # TODO: Tarayıcı düzenle menüsü implementasyonu
    
    def show_browser_view_menu(self):
        """Tarayıcı görünüm menüsünü göster"""
        self.logger.info("Browser view menu requested")
        # TODO: Tarayıcı görünüm menüsü implementasyonu
    
    def show_browser_history_menu(self):
        """Tarayıcı geçmiş menüsünü göster"""
        self.logger.info("Browser history menu requested")
        # TODO: Tarayıcı geçmiş menüsü implementasyonu
    
    def show_browser_bookmarks_menu(self):
        """Tarayıcı yer imleri menüsünü göster"""
        self.logger.info("Browser bookmarks menu requested")
        # TODO: Tarayıcı yer imleri menüsü implementasyonu
    
    def show_terminal_menu(self):
        """Terminal menüsünü göster"""
        self.logger.info("Terminal menu requested")
        # TODO: Terminal menüsü implementasyonu
    
    def show_notepad_file_menu(self):
        """Not defteri dosya menüsünü göster"""
        self.logger.info("Notepad file menu requested")
        # TODO: Not defteri dosya menüsü implementasyonu
    
    def show_notepad_edit_menu(self):
        """Not defteri düzenle menüsünü göster"""
        self.logger.info("Notepad edit menu requested")
        # TODO: Not defteri düzenle menüsü implementasyonu
    
    def show_notepad_format_menu(self):
        """Not defteri format menüsünü göster"""
        self.logger.info("Notepad format menu requested")
        # TODO: Not defteri format menüsü implementasyonu
    
    def show_pyide_file_menu(self):
        """Python IDE dosya menüsünü göster"""
        self.logger.info("PyIDE file menu requested")
        # TODO: Python IDE dosya menüsü implementasyonu
    
    def show_pyide_edit_menu(self):
        """Python IDE düzenle menüsünü göster"""
        self.logger.info("PyIDE edit menu requested")
        # TODO: Python IDE düzenle menüsü implementasyonu
    
    def show_pyide_run_menu(self):
        """Python IDE çalıştır menüsünü göster"""
        self.logger.info("PyIDE run menu requested")
        # TODO: Python IDE çalıştır menüsü implementasyonu
    
    def show_pyide_tools_menu(self):
        """Python IDE araçlar menüsünü göster"""
        self.logger.info("PyIDE tools menu requested")
        # TODO: Python IDE araçlar menüsü implementasyonu
    
    def show_settings_menu(self):
        """Ayarlar menüsünü göster"""
        self.logger.info("Settings menu requested")
        # TODO: Ayarlar menüsü implementasyonu

    def load_notification_icon(self):
        """Bildirim butonu için özel ikon yükle"""
        try:
            # Özel ikon yolları
            icon_paths = [
                "assets/icons/notification.png",
                "assets/icons/bell.png", 
                "rain/assets/notification.png",
                "icons/notification.png"
            ]
            
            for icon_path in icon_paths:
                if Path(icon_path).exists():
                    icon = QIcon(icon_path)
                    if not icon.isNull():
                        self.notifications_button.setIcon(icon)
                        self.notifications_button.setText("")  # Metni kaldır
                        self.notifications_button.setIconSize(QSize(20, 20))
                        self.logger.info(f"Notification icon loaded from: {icon_path}")
                        return
            
            # Varsayılan emoji ikon
            self.notifications_button.setText("🔔")
            self.logger.info("Using default notification emoji icon")
            
        except Exception as e:
            self.logger.error(f"Failed to load notification icon: {e}")
            self.notifications_button.setText("🔔")

    def load_control_center_icon(self):
        """Denetim merkezi butonu için özel ikon yükle"""
        try:
            # Özel ikon yolları
            icon_paths = [
                "assets/icons/settings.png",
                "assets/icons/control.png",
                "rain/assets/settings.png", 
                "icons/settings.png"
            ]
            
            for icon_path in icon_paths:
                if Path(icon_path).exists():
                    icon = QIcon(icon_path)
                    if not icon.isNull():
                        self.control_center_button.setIcon(icon)
                        self.control_center_button.setText("")  # Metni kaldır
                        self.control_center_button.setIconSize(QSize(20, 20))
                        self.logger.info(f"Control center icon loaded from: {icon_path}")
                        return
            
            # Varsayılan emoji ikon
            self.control_center_button.setText("⚙️")
            self.logger.info("Using default control center emoji icon")
            
        except Exception as e:
            self.logger.error(f"Failed to load control center icon: {e}")
            self.control_center_button.setText("⚙️")

    def set_notification_icon(self, icon_path: str):
        """Bildirim ikonu manuel olarak ayarla"""
        try:
            if Path(icon_path).exists():
                icon = QIcon(icon_path)
                if not icon.isNull():
                    self.notifications_button.setIcon(icon)
                    self.notifications_button.setText("")
                    self.notifications_button.setIconSize(QSize(20, 20))
                    self.logger.info(f"Notification icon set to: {icon_path}")
                    return True
            return False
        except Exception as e:
            self.logger.error(f"Failed to set notification icon: {e}")
            return False

    def set_control_center_icon(self, icon_path: str):
        """Denetim merkezi ikonu manuel olarak ayarla"""
        try:
            if Path(icon_path).exists():
                icon = QIcon(icon_path)
                if not icon.isNull():
                    self.control_center_button.setIcon(icon)
                    self.control_center_button.setText("")
                    self.control_center_button.setIconSize(QSize(20, 20))
                    self.logger.info(f"Control center icon set to: {icon_path}")
                    return True
            return False
        except Exception as e:
            self.logger.error(f"Failed to set control center icon: {e}")
            return False

    def set_cloudsearch_icon(self, icon_path: str):
        """CloudSearch ikonu manuel olarak ayarla"""
        try:
            if Path(icon_path).exists():
                icon = QIcon(icon_path)
                if not icon.isNull():
                    self.cloudsearch_button.setIcon(icon)
                    self.cloudsearch_button.setText("")
                    self.cloudsearch_button.setIconSize(QSize(20, 20))
                    self.logger.info(f"CloudSearch icon set to: {icon_path}")
                    return True
            return False
        except Exception as e:
            self.logger.error(f"Failed to set CloudSearch icon: {e}")
            return False

    def show_flet_notification_widget(self):
        """Modern HTML bildirim widget'ını göster"""
        if not HTML_WIDGETS_AVAILABLE:
            self.logger.warning("HTML widgets not available")
            return
            
        try:
            # Eğer widget zaten açıksa kapat
            if hasattr(self, 'html_notification_widget') and self.html_notification_widget:
                self.html_notification_widget.hide()
                self.html_notification_widget.deleteLater()
                self.html_notification_widget = None
                self.logger.info("HTML notification widget closed")
                return
            
            # Yeni widget oluştur
            self.html_notification_widget = HTMLNotificationWidget()
            
            # Widget kapanma sinyalini bağla
            self.html_notification_widget.widget_closed.connect(self.on_notification_widget_closed)
            
            # Widget'ı topbar'ın altında konumlandır - ekran içinde kalacak şekilde
            topbar_pos = self.mapToGlobal(self.pos())
            button_pos = self.notifications_button.mapToGlobal(self.notifications_button.pos())
            
            # Widget boyutları (380x450)
            widget_width = 380
            widget_height = 450
            
            # Ekran boyutlarını al
            screen = self.screen()
            screen_geometry = screen.availableGeometry()
            
            # X konumu - butonun sağından başlayıp widget genişliği kadar sola kaydır
            widget_x = button_pos.x() - widget_width + self.notifications_button.width()
            
            # Ekran sınırlarını kontrol et
            if widget_x < 0:
                widget_x = 10  # Sol kenara minimum 10px boşluk
            elif widget_x + widget_width > screen_geometry.width():
                widget_x = screen_geometry.width() - widget_width - 10  # Sağ kenara minimum 10px boşluk
            
            # Y konumu - topbar'ın altında
            widget_y = topbar_pos.y() + self.height() + 10
            
            # Ekran alt sınırını kontrol et
            if widget_y + widget_height > screen_geometry.height():
                widget_y = screen_geometry.height() - widget_height - 10  # Alt kenara minimum 10px boşluk
            
            self.html_notification_widget.move(widget_x, widget_y)
            self.html_notification_widget.show_widget()
            
            self.logger.info(f"HTML notification widget opened at ({widget_x}, {widget_y})")
            
        except Exception as e:
            self.logger.error(f"Failed to show HTML notification widget: {e}")

    def show_flet_clock_widget(self):
        """Modern HTML saat widget'ını göster"""
        if not HTML_WIDGETS_AVAILABLE:
            self.logger.warning("HTML widgets not available")
            return
            
        try:
            # Eğer widget zaten açıksa kapat
            if hasattr(self, 'html_clock_widget') and self.html_clock_widget:
                self.html_clock_widget.hide()
                self.html_clock_widget.deleteLater()
                self.html_clock_widget = None
                self.logger.info("HTML clock widget closed")
                return
            
            # Yeni widget oluştur
            self.html_clock_widget = HTMLClockWidget()
            
            # Widget kapanma sinyalini bağla
            self.html_clock_widget.widget_closed.connect(self.on_clock_widget_closed)
            
            # Widget'ı topbar'ın altında konumlandır - ekran içinde kalacak şekilde
            topbar_pos = self.mapToGlobal(self.pos())
            button_pos = self.clock_button.mapToGlobal(self.clock_button.pos())
            
            # Widget boyutları (330x400)
            widget_width = 330
            widget_height = 400
            
            # Ekran boyutlarını al
            screen = self.screen()
            screen_geometry = screen.availableGeometry()
            
            # X konumu - butonun ortasından widget'ı ortalamaya çalış
            widget_x = button_pos.x() + (self.clock_button.width() // 2) - (widget_width // 2)
            
            # Ekran sınırlarını kontrol et
            if widget_x < 0:
                widget_x = 10  # Sol kenara minimum 10px boşluk
            elif widget_x + widget_width > screen_geometry.width():
                widget_x = screen_geometry.width() - widget_width - 10  # Sağ kenara minimum 10px boşluk
            
            # Y konumu - topbar'ın altında
            widget_y = topbar_pos.y() + self.height() + 10
            
            # Ekran alt sınırını kontrol et
            if widget_y + widget_height > screen_geometry.height():
                widget_y = screen_geometry.height() - widget_height - 10  # Alt kenara minimum 10px boşluk
            
            self.html_clock_widget.move(widget_x, widget_y)
            self.html_clock_widget.show_widget()
            
            self.logger.info(f"HTML clock widget opened at ({widget_x}, {widget_y})")
            
        except Exception as e:
            self.logger.error(f"Failed to show HTML clock widget: {e}")

    def show_flet_control_center_widget(self):
        """Modern HTML denetim merkezi widget'ını göster"""
        if not HTML_WIDGETS_AVAILABLE:
            self.logger.warning("HTML widgets not available")
            return
            
        try:
            # Eğer widget zaten açıksa kapat
            if hasattr(self, 'html_control_widget') and self.html_control_widget:
                self.html_control_widget.hide()
                self.html_control_widget.deleteLater()
                self.html_control_widget = None
                self.logger.info("HTML control center widget closed")
                return
            
            # Yeni widget oluştur
            self.html_control_widget = HTMLControlCenterWidget()
            
            # Widget kapanma sinyalini bağla
            self.html_control_widget.widget_closed.connect(self.on_control_widget_closed)
            
            # Widget'ı topbar'ın altında konumlandır - ekran içinde kalacak şekilde
            topbar_pos = self.mapToGlobal(self.pos())
            button_pos = self.control_center_button.mapToGlobal(self.control_center_button.pos())
            
            # Widget boyutları (360x520)
            widget_width = 360
            widget_height = 520
            
            # Ekran boyutlarını al
            screen = self.screen()
            screen_geometry = screen.availableGeometry()
            
            # X konumu - butonun sağından başlayıp widget genişliği kadar sola kaydır
            widget_x = button_pos.x() - widget_width + self.control_center_button.width()
            
            # Ekran sınırlarını kontrol et
            if widget_x < 0:
                widget_x = 10  # Sol kenara minimum 10px boşluk
            elif widget_x + widget_width > screen_geometry.width():
                widget_x = screen_geometry.width() - widget_width - 10  # Sağ kenara minimum 10px boşluk
            
            # Y konumu - topbar'ın altında
            widget_y = topbar_pos.y() + self.height() + 10
            
            # Ekran alt sınırını kontrol et
            if widget_y + widget_height > screen_geometry.height():
                widget_y = screen_geometry.height() - widget_height - 10  # Alt kenara minimum 10px boşluk
            
            self.html_control_widget.move(widget_x, widget_y)
            self.html_control_widget.show_widget()
            
            self.logger.info(f"HTML control center widget opened at ({widget_x}, {widget_y})")
            
        except Exception as e:
            self.logger.error(f"Failed to show HTML control center widget: {e}")

    def show_flet_cloudsearch_widget(self):
        """Modern HTML CloudSearch widget'ını göster"""
        if not HTML_WIDGETS_AVAILABLE:
            self.logger.warning("HTML widgets not available")
            return
            
        try:
            # Eğer widget zaten açıksa kapat
            if hasattr(self, 'html_search_widget') and self.html_search_widget:
                self.html_search_widget.hide()
                self.html_search_widget.deleteLater()
                self.html_search_widget = None
                self.logger.info("HTML CloudSearch widget closed")
                return
            
            # Yeni widget oluştur
            self.html_search_widget = HTMLCloudSearchWidget()
            
            # Widget kapanma sinyalini bağla
            self.html_search_widget.widget_closed.connect(self.on_search_widget_closed)
            
            # Widget'ı topbar'ın altında konumlandır - ekran içinde kalacak şekilde
            topbar_pos = self.mapToGlobal(self.pos())
            button_pos = self.cloudsearch_button.mapToGlobal(self.cloudsearch_button.pos())
            
            # Widget boyutları (400x500)
            widget_width = 400
            widget_height = 500
            
            # Ekran boyutlarını al
            screen = self.screen()
            screen_geometry = screen.availableGeometry()
            
            # X konumu - butonun sağından başlayıp widget genişliği kadar sola kaydır
            widget_x = button_pos.x() - widget_width + self.cloudsearch_button.width()
            
            # Ekran sınırlarını kontrol et
            if widget_x < 0:
                widget_x = 10  # Sol kenara minimum 10px boşluk
            elif widget_x + widget_width > screen_geometry.width():
                widget_x = screen_geometry.width() - widget_width - 10  # Sağ kenara minimum 10px boşluk
            
            # Y konumu - topbar'ın altında
            widget_y = topbar_pos.y() + self.height() + 10
            
            # Ekran alt sınırını kontrol et
            if widget_y + widget_height > screen_geometry.height():
                widget_y = screen_geometry.height() - widget_height - 10  # Alt kenara minimum 10px boşluk
            
            self.html_search_widget.move(widget_x, widget_y)
            self.html_search_widget.show_widget()
            
            self.logger.info(f"HTML CloudSearch widget opened at ({widget_x}, {widget_y})")
            
        except Exception as e:
            self.logger.error(f"Failed to show HTML CloudSearch widget: {e}")

    def on_notification_widget_closed(self):
        """Bildirim widget'ı kapandığında çağrılır"""
        if hasattr(self, 'html_notification_widget'):
            self.html_notification_widget = None
        self.logger.info("Notification widget closed by outside click")

    def on_clock_widget_closed(self):
        """Saat widget'ı kapandığında çağrılır"""
        if hasattr(self, 'html_clock_widget'):
            self.html_clock_widget = None
        self.logger.info("Clock widget closed by outside click")

    def on_control_widget_closed(self):
        """Denetim merkezi widget'ı kapandığında çağrılır"""
        if hasattr(self, 'html_control_widget'):
            self.html_control_widget = None
        self.logger.info("Control center widget closed by outside click")

    def on_search_widget_closed(self):
        """CloudSearch widget'ı kapandığında çağrılır"""
        if hasattr(self, 'html_search_widget'):
            self.html_search_widget = None
        self.logger.info("CloudSearch widget closed by outside click")

    def hide_all_html_widgets(self):
        """Tüm HTML widget'larını gizle"""
        try:
            # HTML widget'larını gizle
            if hasattr(self, 'html_notification_widget') and self.html_notification_widget:
                self.html_notification_widget.hide()
                self.html_notification_widget.deleteLater()
                self.html_notification_widget = None
                
            if hasattr(self, 'html_clock_widget') and self.html_clock_widget:
                self.html_clock_widget.hide()
                self.html_clock_widget.deleteLater()
                self.html_clock_widget = None
                
            if hasattr(self, 'html_control_widget') and self.html_control_widget:
                self.html_control_widget.hide()
                self.html_control_widget.deleteLater()
                self.html_control_widget = None
                
            if hasattr(self, 'html_search_widget') and self.html_search_widget:
                self.html_search_widget.hide()
                self.html_search_widget.deleteLater()
                self.html_search_widget = None
                
        except Exception as e:
            self.logger.error(f"Failed to hide HTML widgets: {e}")

    def load_cloudsearch_icon(self):
        """CloudSearch butonu için özel ikon yükle"""
        try:
            # Özel ikon yolları
            icon_paths = [
                "assets/icons/search.png",
                "rain/assets/search.png",
                "icons/search.png"
            ]
            
            for icon_path in icon_paths:
                if Path(icon_path).exists():
                    icon = QIcon(icon_path)
                    if not icon.isNull():
                        self.cloudsearch_button.setIcon(icon)
                        self.cloudsearch_button.setText("")  # Metni kaldır
                        self.cloudsearch_button.setIconSize(QSize(20, 20))
                        self.logger.info(f"CloudSearch icon loaded from: {icon_path}")
                        return
            
            # Varsayılan ikon
            self.cloudsearch_button.setText("🔍")
            self.logger.info("Using default CloudSearch icon")
            
        except Exception as e:
            self.logger.error(f"Failed to load CloudSearch icon: {e}")
            self.cloudsearch_button.setText("🔍")