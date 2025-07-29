"""
Rain Flet HTML Widgets - Flet Widget'larını HTML olarak PyQt6'da göster
Flet widget'larını HTML'e çevirip QWebEngineView'de gösterir
"""

import logging
import tempfile
import os
import json
from pathlib import Path
from typing import Optional
from datetime import datetime

try:
    from PyQt6.QtWidgets import QWidget, QVBoxLayout, QApplication
    from PyQt6.QtCore import Qt, QUrl, QTimer, pyqtSignal
    from PyQt6.QtWebEngineWidgets import QWebEngineView
    from PyQt6.QtWebEngineCore import QWebEngineSettings
    from PyQt6.QtGui import QMouseEvent
    PYQT_AVAILABLE = True
except ImportError:
    PYQT_AVAILABLE = False

class FletHTMLWidget(QWidget):
    """Flet widget'ını HTML olarak gösteren base sınıf"""
    
    # Widget kapanma sinyali
    widget_closed = pyqtSignal()
    
    def __init__(self, widget_name: str, width: int = 400, height: int = 500):
        super().__init__()
        self.widget_name = widget_name
        self.logger = logging.getLogger(f"FletHTML_{widget_name}")
        
        if not PYQT_AVAILABLE:
            self.logger.error("PyQt6 not available")
            return
            
        self.setFixedSize(width, height)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Global mouse event filter'ı kur
        self.installEventFilter(self)
        
        self.setup_ui()
        
    def setup_ui(self):
        """UI kurulumu"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Web view oluştur
        self.web_view = QWebEngineView()
        self.web_view.setStyleSheet("""
            QWebEngineView {
                background: transparent;
                border: none;
            }
        """)
        
        # Web engine ayarları
        settings = self.web_view.settings()
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessFileUrls, True)
        
        layout.addWidget(self.web_view)
        
    def load_html_content(self, html_content: str):
        """HTML içeriğini yükle"""
        try:
            # Geçici HTML dosyası oluştur
            temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8')
            temp_file.write(html_content)
            temp_file.close()
            
            # HTML dosyasını yükle
            file_url = QUrl.fromLocalFile(temp_file.name)
            self.web_view.load(file_url)
            
            self.logger.info(f"Loaded HTML content for {self.widget_name}")
            
        except Exception as e:
            self.logger.error(f"Failed to load HTML content: {e}")
    
    def showEvent(self, event):
        """Widget gösterildiğinde global mouse event'leri dinlemeye başla"""
        super().showEvent(event)
        if QApplication.instance():
            QApplication.instance().installEventFilter(self)
    
    def hideEvent(self, event):
        """Widget gizlendiğinde global mouse event'leri dinlemeyi bırak"""
        super().hideEvent(event)
        if QApplication.instance():
            QApplication.instance().removeEventFilter(self)
    
    def eventFilter(self, obj, event):
        """Global event filter - dış tıklamaları yakala"""
        if event.type() == event.Type.MouseButtonPress:
            # Eğer tıklama bu widget'ın dışındaysa kapat
            if not self.geometry().contains(event.globalPosition().toPoint()):
                self.close_widget()
                return True
        return super().eventFilter(obj, event)
    
    def close_widget(self):
        """Widget'ı kapat"""
        self.widget_closed.emit()
        self.hide()
        self.logger.info(f"{self.widget_name} widget closed by outside click")

class HTMLNotificationWidget(FletHTMLWidget):
    """HTML bildirim widget'ı"""
    
    def __init__(self):
        super().__init__("Notification", 380, 450)
        self.notifications_data = self.get_notifications_data()
        
    def get_notifications_data(self):
        """Bildirim verilerini al"""
        return [
            {
                "title": "Sistem Bildirimi",
                "message": "PyCloud OS başarıyla başlatıldı ve tüm servisler çalışıyor",
                "time": "2 dakika önce",
                "icon": "📢"
            },
            {
                "title": "Uygulama Güncellemesi", 
                "message": "Cloud Files v2.1.0 güncellendi",
                "time": "1 saat önce",
                "icon": "🔄"
            },
            {
                "title": "Güvenlik Uyarısı",
                "message": "Yeni giriş denemesi tespit edildi",
                "time": "3 saat önce",
                "icon": "⚠️"
            },
            {
                "title": "Yedekleme Tamamlandı",
                "message": "Haftalık sistem yedeklemesi başarıyla tamamlandı",
                "time": "1 gün önce",
                "icon": "✅"
            }
        ]
        
    def show_widget(self):
        """Widget'ı göster"""
        html_content = self.generate_notification_html()
        self.load_html_content(html_content)
        self.show()
        
    def generate_notification_html(self):
        """Bildirim HTML'ini oluştur"""
        notifications_html = ""
        
        for notif in self.notifications_data:
            notifications_html += f"""
            <div class="notification-item">
                <div class="notification-icon">{notif['icon']}</div>
                <div class="notification-content">
                    <div class="notification-title">{notif['title']}</div>
                    <div class="notification-message">{notif['message']}</div>
                </div>
                <div class="notification-time">{notif['time']}</div>
            </div>
            """
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Bildirimler</title>
            <style>
                body {{
                    margin: 0;
                    padding: 20px;
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    background: rgba(30, 30, 30, 0.98);
                    color: white;
                    border-radius: 18px;
                    border: 2px solid rgba(80, 80, 80, 0.9);
                    box-shadow: 0 15px 40px rgba(0, 0, 0, 0.3);
                    width: 340px;
                    height: 410px;
                    overflow: hidden;
                }}
                
                .header {{
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin-bottom: 16px;
                }}
                
                .title {{
                    font-size: 20px;
                    font-weight: bold;
                    color: white;
                }}
                
                .count {{
                    background: rgba(0, 120, 255, 0.8);
                    color: white;
                    padding: 4px 8px;
                    border-radius: 10px;
                    font-size: 12px;
                    font-weight: bold;
                }}
                
                .notifications-list {{
                    max-height: 280px;
                    overflow-y: auto;
                    margin-bottom: 16px;
                }}
                
                .notification-item {{
                    background: rgba(45, 45, 45, 0.9);
                    border: 1px solid rgba(100, 100, 100, 0.5);
                    border-radius: 12px;
                    padding: 12px;
                    margin-bottom: 8px;
                    display: flex;
                    align-items: flex-start;
                    gap: 12px;
                    transition: background 0.2s;
                }}
                
                .notification-item:hover {{
                    background: rgba(55, 55, 55, 0.9);
                }}
                
                .notification-icon {{
                    background: rgba(0, 120, 255, 0.3);
                    border-radius: 20px;
                    width: 40px;
                    height: 40px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-size: 20px;
                    flex-shrink: 0;
                }}
                
                .notification-content {{
                    flex: 1;
                    min-width: 0;
                }}
                
                .notification-title {{
                    font-size: 14px;
                    font-weight: bold;
                    color: white;
                    margin-bottom: 4px;
                    white-space: nowrap;
                    overflow: hidden;
                    text-overflow: ellipsis;
                }}
                
                .notification-message {{
                    font-size: 12px;
                    color: #cccccc;
                    line-height: 1.4;
                    display: -webkit-box;
                    -webkit-line-clamp: 2;
                    -webkit-box-orient: vertical;
                    overflow: hidden;
                }}
                
                .notification-time {{
                    font-size: 10px;
                    color: #888888;
                    flex-shrink: 0;
                    text-align: right;
                }}
                
                .buttons {{
                    display: flex;
                    gap: 12px;
                }}
                
                .button {{
                    background: rgba(60, 60, 60, 0.8);
                    border: 1px solid rgba(120, 120, 120, 0.6);
                    border-radius: 10px;
                    padding: 10px 16px;
                    color: white;
                    font-weight: 600;
                    font-size: 13px;
                    cursor: pointer;
                    transition: background 0.2s;
                    text-decoration: none;
                    display: inline-block;
                }}
                
                .button:hover {{
                    background: rgba(80, 80, 80, 0.9);
                }}
                
                .button.clear {{
                    background: rgba(200, 60, 60, 0.8);
                }}
                
                .button.clear:hover {{
                    background: rgba(220, 80, 80, 0.9);
                }}
                
                .button.settings {{
                    background: rgba(0, 120, 255, 0.8);
                }}
                
                .button.settings:hover {{
                    background: rgba(0, 140, 255, 0.9);
                }}
                
                /* Scrollbar styling */
                .notifications-list::-webkit-scrollbar {{
                    width: 8px;
                }}
                
                .notifications-list::-webkit-scrollbar-track {{
                    background: rgba(60, 60, 60, 0.5);
                    border-radius: 4px;
                }}
                
                .notifications-list::-webkit-scrollbar-thumb {{
                    background: rgba(120, 120, 120, 0.8);
                    border-radius: 4px;
                }}
                
                .notifications-list::-webkit-scrollbar-thumb:hover {{
                    background: rgba(140, 140, 140, 0.9);
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <div class="title">🔔 Bildirimler</div>
                <div class="count">{len(self.notifications_data)}</div>
            </div>
            
            <div class="notifications-list">
                {notifications_html}
            </div>
            
            <div class="buttons">
                <div class="button clear" onclick="clearNotifications()">🗑️ Temizle</div>
                <div class="button settings" onclick="openSettings()">⚙️ Ayarlar</div>
            </div>
            
            <script>
                function clearNotifications() {{
                    alert('🗑️ Bildirimler temizlendi');
                }}
                
                function openSettings() {{
                    alert('⚙️ Bildirim ayarları açılıyor...');
                }}
            </script>
        </body>
        </html>
        """

class HTMLClockWidget(FletHTMLWidget):
    """HTML saat widget'ı"""
    
    def __init__(self):
        super().__init__("Clock", 330, 400)
        
    def show_widget(self):
        """Widget'ı göster"""
        html_content = self.generate_clock_html()
        self.load_html_content(html_content)
        self.show()
        
        # Saati her saniye güncelle
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_clock)
        self.timer.start(1000)
        
    def update_clock(self):
        """Saati güncelle"""
        try:
            # JavaScript ile saati güncelle
            now = datetime.now()
            time_str = now.strftime("%H:%M:%S")
            js_code = f"document.getElementById('current-time').textContent = '{time_str}';"
            self.web_view.page().runJavaScript(js_code)
        except Exception as e:
            self.logger.error(f"Failed to update clock: {e}")
        
    def generate_clock_html(self):
        """Saat HTML'ini oluştur"""
        now = datetime.now()
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Saat & Takvim</title>
            <style>
                body {{
                    margin: 0;
                    padding: 20px;
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    background: rgba(30, 30, 30, 0.98);
                    color: white;
                    border-radius: 18px;
                    border: 2px solid rgba(80, 80, 80, 0.9);
                    box-shadow: 0 15px 40px rgba(0, 0, 0, 0.3);
                    width: 290px;
                    height: 360px;
                    overflow: hidden;
                }}
                
                .title {{
                    font-size: 20px;
                    font-weight: bold;
                    color: white;
                    text-align: center;
                    margin-bottom: 16px;
                }}
                
                .card {{
                    background: rgba(45, 45, 45, 0.9);
                    border: 1px solid rgba(100, 100, 100, 0.5);
                    border-radius: 16px;
                    padding: 16px;
                    margin-bottom: 16px;
                }}
                
                .time-card {{
                    text-align: center;
                }}
                
                .big-time {{
                    font-size: 36px;
                    font-weight: bold;
                    color: white;
                    margin-bottom: 8px;
                }}
                
                .date {{
                    font-size: 16px;
                    color: #cccccc;
                }}
                
                .calendar-title {{
                    font-size: 16px;
                    font-weight: bold;
                    color: white;
                    margin-bottom: 12px;
                }}
                
                .month-year {{
                    font-size: 15px;
                    font-weight: bold;
                    text-align: center;
                    color: white;
                    margin-bottom: 12px;
                }}
                
                .days-header {{
                    display: flex;
                    justify-content: space-around;
                    background: rgba(60, 60, 60, 0.6);
                    border-radius: 8px;
                    padding: 8px;
                    margin-bottom: 12px;
                }}
                
                .day-name {{
                    font-size: 11px;
                    color: #bbbbbb;
                    text-align: center;
                    flex: 1;
                }}
                
                .today-highlight {{
                    background: rgba(0, 200, 100, 0.3);
                    border: 2px solid rgba(0, 200, 100, 0.6);
                    border-radius: 10px;
                    padding: 12px;
                    display: flex;
                    align-items: center;
                    gap: 12px;
                }}
                
                .today-icon {{
                    font-size: 24px;
                    color: #00ff88;
                }}
                
                .today-text {{
                    font-size: 14px;
                    color: white;
                    font-weight: bold;
                }}
                
                .timezone-card {{
                    display: flex;
                    align-items: center;
                    gap: 12px;
                }}
                
                .timezone-icon {{
                    font-size: 20px;
                    color: white;
                }}
                
                .timezone-text {{
                    font-size: 14px;
                    color: #cccccc;
                }}
            </style>
        </head>
        <body>
            <div class="title">🕐 Saat & Takvim</div>
            
            <div class="card time-card">
                <div class="big-time" id="current-time">{now.strftime("%H:%M:%S")}</div>
                <div class="date">{now.strftime("%A, %d %B %Y")}</div>
            </div>
            
            <div class="card">
                <div class="calendar-title">📅 Bu Ay</div>
                <div class="month-year">{now.strftime("%B %Y")}</div>
                
                <div class="days-header">
                    <div class="day-name">Pzt</div>
                    <div class="day-name">Sal</div>
                    <div class="day-name">Çar</div>
                    <div class="day-name">Per</div>
                    <div class="day-name">Cum</div>
                    <div class="day-name">Cmt</div>
                    <div class="day-name">Paz</div>
                </div>
                
                <div class="today-highlight">
                    <div class="today-icon">📅</div>
                    <div class="today-text">Bugün: {now.day} {now.strftime('%B')}</div>
                </div>
            </div>
            
            <div class="card">
                <div class="timezone-card">
                    <div class="timezone-icon">🌍</div>
                    <div class="timezone-text">Türkiye Saati (UTC+3)</div>
                </div>
            </div>
        </body>
        </html>
        """

class HTMLControlCenterWidget(FletHTMLWidget):
    """HTML denetim merkezi widget'ı"""
    
    def __init__(self):
        super().__init__("ControlCenter", 360, 520)
        
    def show_widget(self):
        """Widget'ı göster"""
        html_content = self.generate_control_center_html()
        self.load_html_content(html_content)
        self.show()
        
    def generate_control_center_html(self):
        """Denetim merkezi HTML'ini oluştur - ListView yapısı"""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Denetim Merkezi</title>
            <style>
                body {
                    margin: 0;
                    padding: 20px;
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    background: rgba(30, 30, 30, 0.98);
                    color: white;
                    border-radius: 18px;
                    border: 2px solid rgba(80, 80, 80, 0.9);
                    box-shadow: 0 15px 40px rgba(0, 0, 0, 0.3);
                    width: 320px;
                    height: 480px;
                    overflow: hidden;
                    display: flex;
                    flex-direction: column;
                }
                
                .title {
                    font-size: 20px;
                    font-weight: bold;
                    color: white;
                    text-align: center;
                    margin-bottom: 16px;
                    flex-shrink: 0;
                }
                
                .content {
                    flex: 1;
                    overflow-y: auto;
                    padding-right: 5px;
                }
                
                .content::-webkit-scrollbar {
                    width: 6px;
                }
                
                .content::-webkit-scrollbar-track {
                    background: rgba(60, 60, 60, 0.3);
                    border-radius: 3px;
                }
                
                .content::-webkit-scrollbar-thumb {
                    background: rgba(120, 120, 120, 0.6);
                    border-radius: 3px;
                }
                
                .content::-webkit-scrollbar-thumb:hover {
                    background: rgba(140, 140, 140, 0.8);
                }
                
                .section-title {
                    font-size: 16px;
                    font-weight: bold;
                    color: rgba(255, 255, 255, 0.8);
                    margin: 16px 0 12px 0;
                    padding-left: 8px;
                    border-left: 3px solid rgba(0, 120, 255, 0.8);
                }
                
                .list-item {
                    background: rgba(45, 45, 45, 0.9);
                    border: 1px solid rgba(100, 100, 100, 0.5);
                    border-radius: 12px;
                    padding: 12px 16px;
                    margin-bottom: 8px;
                    display: flex;
                    align-items: center;
                    justify-content: space-between;
                    cursor: pointer;
                    transition: all 0.2s;
                }
                
                .list-item:hover {
                    background: rgba(55, 55, 55, 0.9);
                    transform: translateX(2px);
                }
                
                .item-left {
                    display: flex;
                    align-items: center;
                    gap: 12px;
                }
                
                .item-icon {
                    font-size: 20px;
                    width: 24px;
                    text-align: center;
                }
                
                .item-info {
                    display: flex;
                    flex-direction: column;
                }
                
                .item-title {
                    font-size: 14px;
                    font-weight: bold;
                    color: white;
                    margin-bottom: 2px;
                }
                
                .item-subtitle {
                    font-size: 12px;
                    color: rgba(255, 255, 255, 0.7);
                }
                
                .item-right {
                    display: flex;
                    align-items: center;
                    gap: 8px;
                }
                
                .toggle-switch {
                    width: 44px;
                    height: 24px;
                    background: rgba(80, 80, 80, 0.8);
                    border-radius: 12px;
                    position: relative;
                    cursor: pointer;
                    transition: background 0.2s;
                }
                
                .toggle-switch.on {
                    background: rgba(0, 200, 100, 0.8);
                }
                
                .toggle-switch::after {
                    content: '';
                    position: absolute;
                    width: 20px;
                    height: 20px;
                    background: white;
                    border-radius: 10px;
                    top: 2px;
                    left: 2px;
                    transition: transform 0.2s;
                }
                
                .toggle-switch.on::after {
                    transform: translateX(20px);
                }
                
                .slider-item {
                    background: rgba(45, 45, 45, 0.9);
                    border: 1px solid rgba(100, 100, 100, 0.5);
                    border-radius: 12px;
                    padding: 16px;
                    margin-bottom: 8px;
                }
                
                .slider-header {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin-bottom: 12px;
                }
                
                .slider-title {
                    font-size: 14px;
                    font-weight: bold;
                    color: white;
                    display: flex;
                    align-items: center;
                    gap: 8px;
                }
                
                .slider-value {
                    font-size: 14px;
                    color: white;
                    font-weight: bold;
                    min-width: 40px;
                    text-align: right;
                }
                
                .slider {
                    width: 100%;
                    height: 8px;
                    border-radius: 4px;
                    background: rgba(80, 80, 80, 0.8);
                    outline: none;
                    cursor: pointer;
                    appearance: none;
                }
                
                .slider::-webkit-slider-thumb {
                    appearance: none;
                    width: 20px;
                    height: 20px;
                    border-radius: 10px;
                    background: white;
                    border: 2px solid rgba(0, 120, 255, 0.8);
                    cursor: pointer;
                }
                
                .system-item {
                    background: rgba(60, 60, 60, 0.8);
                    border: 1px solid rgba(120, 120, 120, 0.6);
                }
                
                .system-item.danger {
                    background: rgba(200, 60, 60, 0.8);
                    border: 1px solid rgba(200, 60, 60, 0.9);
                }
                
                .system-item:hover {
                    background: rgba(80, 80, 80, 0.9);
                }
                
                .system-item.danger:hover {
                    background: rgba(220, 80, 80, 0.9);
                }
                
                .status-badge {
                    background: rgba(0, 200, 100, 0.8);
                    color: white;
                    padding: 2px 8px;
                    border-radius: 10px;
                    font-size: 11px;
                    font-weight: bold;
                }
                
                .status-badge.off {
                    background: rgba(120, 120, 120, 0.8);
                }
            </style>
        </head>
        <body>
            <div class="title">⚙️ Denetim Merkezi</div>
            
            <div class="content">
                <div class="section-title">🔧 Hızlı Ayarlar</div>
                
                <div class="list-item" onclick="toggleWifi()">
                    <div class="item-left">
                        <div class="item-icon">📶</div>
                        <div class="item-info">
                            <div class="item-title">WiFi</div>
                            <div class="item-subtitle">Bağlı: PyCloud-Network</div>
                        </div>
                    </div>
                    <div class="item-right">
                        <div class="toggle-switch on" id="wifi-toggle"></div>
                    </div>
                </div>
                
                <div class="list-item" onclick="toggleBluetooth()">
                    <div class="item-left">
                        <div class="item-icon">🔵</div>
                        <div class="item-info">
                            <div class="item-title">Bluetooth</div>
                            <div class="item-subtitle">Kapalı</div>
                        </div>
                    </div>
                    <div class="item-right">
                        <div class="toggle-switch" id="bluetooth-toggle"></div>
                    </div>
                </div>
                
                <div class="list-item" onclick="toggleDarkMode()">
                    <div class="item-left">
                        <div class="item-icon">🌙</div>
                        <div class="item-info">
                            <div class="item-title">Gece Modu</div>
                            <div class="item-subtitle">Koyu tema aktif</div>
                        </div>
                    </div>
                    <div class="item-right">
                        <div class="toggle-switch on" id="darkmode-toggle"></div>
                    </div>
                </div>
                
                <div class="list-item" onclick="toggleSilent()">
                    <div class="item-left">
                        <div class="item-icon">🔕</div>
                        <div class="item-info">
                            <div class="item-title">Sessiz Mod</div>
                            <div class="item-subtitle">Bildirimler kapalı</div>
                        </div>
                    </div>
                    <div class="item-right">
                        <div class="toggle-switch" id="silent-toggle"></div>
                    </div>
                </div>
                
                <div class="section-title">🎚️ Ses & Görüntü</div>
                
                <div class="slider-item">
                    <div class="slider-header">
                        <div class="slider-title">
                            <span>🔊</span>
                            <span>Ses Seviyesi</span>
                        </div>
                        <div class="slider-value" id="volume-value">70%</div>
                    </div>
                    <input type="range" min="0" max="100" value="70" class="slider" id="volume-slider" oninput="updateVolume(this.value)">
                </div>
                
                <div class="slider-item">
                    <div class="slider-header">
                        <div class="slider-title">
                            <span>☀️</span>
                            <span>Parlaklık</span>
                        </div>
                        <div class="slider-value" id="brightness-value">80%</div>
                    </div>
                    <input type="range" min="0" max="100" value="80" class="slider" id="brightness-slider" oninput="updateBrightness(this.value)">
                </div>
                
                <div class="section-title">⚙️ Sistem</div>
                
                <div class="list-item system-item" onclick="openSettings()">
                    <div class="item-left">
                        <div class="item-icon">⚙️</div>
                        <div class="item-info">
                            <div class="item-title">Sistem Ayarları</div>
                            <div class="item-subtitle">Tüm ayarları yönet</div>
                        </div>
                    </div>
                    <div class="item-right">
                        <div style="color: rgba(255, 255, 255, 0.5);">›</div>
                    </div>
                </div>
                
                <div class="list-item system-item" onclick="openTaskManager()">
                    <div class="item-left">
                        <div class="item-icon">📊</div>
                        <div class="item-info">
                            <div class="item-title">Görev Yöneticisi</div>
                            <div class="item-subtitle">CPU: 23% | RAM: 45%</div>
                        </div>
                    </div>
                    <div class="item-right">
                        <div style="color: rgba(255, 255, 255, 0.5);">›</div>
                    </div>
                </div>
                
                <div class="list-item system-item" onclick="restartSystem()">
                    <div class="item-left">
                        <div class="item-icon">🔄</div>
                        <div class="item-info">
                            <div class="item-title">Yeniden Başlat</div>
                            <div class="item-subtitle">Sistemi yeniden başlat</div>
                        </div>
                    </div>
                    <div class="item-right">
                        <div style="color: rgba(255, 255, 255, 0.5);">›</div>
                    </div>
                </div>
                
                <div class="list-item system-item danger" onclick="shutdownSystem()">
                    <div class="item-left">
                        <div class="item-icon">⏻</div>
                        <div class="item-info">
                            <div class="item-title">Sistemi Kapat</div>
                            <div class="item-subtitle">Güvenli kapatma</div>
                        </div>
                    </div>
                    <div class="item-right">
                        <div style="color: rgba(255, 255, 255, 0.8);">›</div>
                    </div>
                </div>
            </div>
            
            <script>
                function toggleWifi() {
                    const toggle = document.getElementById('wifi-toggle');
                    toggle.classList.toggle('on');
                    const subtitle = toggle.closest('.list-item').querySelector('.item-subtitle');
                    if (toggle.classList.contains('on')) {
                        subtitle.textContent = 'Bağlı: PyCloud-Network';
                        console.log('📶 WiFi açıldı');
                    } else {
                        subtitle.textContent = 'Kapalı';
                        console.log('📶 WiFi kapatıldı');
                    }
                }
                
                function toggleBluetooth() {
                    const toggle = document.getElementById('bluetooth-toggle');
                    toggle.classList.toggle('on');
                    const subtitle = toggle.closest('.list-item').querySelector('.item-subtitle');
                    if (toggle.classList.contains('on')) {
                        subtitle.textContent = 'Açık - Cihaz aranıyor';
                        console.log('🔵 Bluetooth açıldı');
                    } else {
                        subtitle.textContent = 'Kapalı';
                        console.log('🔵 Bluetooth kapatıldı');
                    }
                }
                
                function toggleDarkMode() {
                    const toggle = document.getElementById('darkmode-toggle');
                    toggle.classList.toggle('on');
                    const subtitle = toggle.closest('.list-item').querySelector('.item-subtitle');
                    if (toggle.classList.contains('on')) {
                        subtitle.textContent = 'Koyu tema aktif';
                        console.log('🌙 Gece modu açıldı');
                    } else {
                        subtitle.textContent = 'Açık tema aktif';
                        console.log('🌙 Gece modu kapatıldı');
                    }
                }
                
                function toggleSilent() {
                    const toggle = document.getElementById('silent-toggle');
                    toggle.classList.toggle('on');
                    const subtitle = toggle.closest('.list-item').querySelector('.item-subtitle');
                    if (toggle.classList.contains('on')) {
                        subtitle.textContent = 'Bildirimler kapalı';
                        console.log('🔕 Sessiz mod açıldı');
                    } else {
                        subtitle.textContent = 'Bildirimler açık';
                        console.log('🔕 Sessiz mod kapatıldı');
                    }
                }
                
                function updateVolume(value) {
                    document.getElementById('volume-value').textContent = value + '%';
                    console.log('🔊 Ses seviyesi: ' + value + '%');
                }
                
                function updateBrightness(value) {
                    document.getElementById('brightness-value').textContent = value + '%';
                    console.log('☀️ Parlaklık: ' + value + '%');
                }
                
                function openSettings() {
                    console.log('⚙️ Sistem ayarları açılıyor...');
                }
                
                function openTaskManager() {
                    console.log('📊 Görev yöneticisi açılıyor...');
                }
                
                function restartSystem() {
                    if (confirm('Sistemi yeniden başlatmak istediğinizden emin misiniz?')) {
                        console.log('🔄 Sistem yeniden başlatılıyor...');
                    }
                }
                
                function shutdownSystem() {
                    if (confirm('Sistemi kapatmak istediğinizden emin misiniz?')) {
                        console.log('⏻ Sistem kapatılıyor...');
                    }
                }
            </script>
        </body>
        </html>
        """

class HTMLCloudSearchWidget(FletHTMLWidget):
    """HTML CloudSearch widget'ı"""
    
    def __init__(self):
        super().__init__("CloudSearch", 420, 480)
        
    def show_widget(self):
        """Widget'ı göster"""
        html_content = self.generate_cloudsearch_html()
        self.load_html_content(html_content)
        self.show()
        
    def generate_cloudsearch_html(self):
        """CloudSearch HTML'ini oluştur"""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>CloudSearch</title>
            <style>
                body {
                    margin: 0;
                    padding: 20px;
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    background: rgba(30, 30, 30, 0.98);
                    color: white;
                    border-radius: 18px;
                    border: 2px solid rgba(80, 80, 80, 0.9);
                    box-shadow: 0 15px 40px rgba(0, 0, 0, 0.3);
                    width: 380px;
                    height: 440px;
                    overflow: hidden;
                }
                
                .header {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin-bottom: 16px;
                }
                
                .title {
                    font-size: 20px;
                    font-weight: bold;
                    color: white;
                }
                
                .open-app-btn {
                    background: rgba(156, 39, 176, 0.8);
                    border: none;
                    border-radius: 8px;
                    padding: 8px 12px;
                    color: white;
                    font-size: 12px;
                    cursor: pointer;
                    transition: background 0.2s;
                }
                
                .open-app-btn:hover {
                    background: rgba(176, 59, 196, 0.9);
                }
                
                .search-container {
                    margin-bottom: 16px;
                }
                
                .search-input {
                    width: 100%;
                    padding: 12px 16px;
                    background: rgba(45, 45, 45, 0.9);
                    border: 1px solid rgba(100, 100, 100, 0.5);
                    border-radius: 12px;
                    color: white;
                    font-size: 16px;
                    outline: none;
                    box-sizing: border-box;
                }
                
                .search-input::placeholder {
                    color: rgba(255, 255, 255, 0.54);
                }
                
                .search-input:focus {
                    border-color: rgba(0, 120, 255, 0.8);
                }
                
                .filters {
                    display: flex;
                    gap: 8px;
                    margin-bottom: 16px;
                    overflow-x: auto;
                }
                
                .filter-btn {
                    background: rgba(60, 60, 60, 0.8);
                    border: 1px solid rgba(120, 120, 120, 0.6);
                    border-radius: 15px;
                    padding: 6px 12px;
                    color: white;
                    font-size: 11px;
                    cursor: pointer;
                    transition: background 0.2s;
                    white-space: nowrap;
                }
                
                .filter-btn:hover {
                    background: rgba(80, 80, 80, 0.9);
                }
                
                .filter-btn.active {
                    background: rgba(0, 120, 255, 0.8);
                }
                
                .results-title {
                    font-size: 14px;
                    font-weight: bold;
                    color: rgba(255, 255, 255, 0.7);
                    margin-bottom: 8px;
                }
                
                .results-list {
                    max-height: 240px;
                    overflow-y: auto;
                    margin-bottom: 16px;
                }
                
                .result-item {
                    background: rgba(45, 45, 45, 0.9);
                    border: 1px solid rgba(100, 100, 100, 0.5);
                    border-radius: 10px;
                    padding: 10px;
                    margin-bottom: 8px;
                    display: flex;
                    align-items: center;
                    gap: 12px;
                    cursor: pointer;
                    transition: background 0.2s;
                }
                
                .result-item:hover {
                    background: rgba(55, 55, 55, 0.9);
                }
                
                .result-icon {
                    background: rgba(0, 120, 255, 0.8);
                    border-radius: 8px;
                    width: 32px;
                    height: 32px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-size: 16px;
                    flex-shrink: 0;
                }
                
                .result-content {
                    flex: 1;
                    min-width: 0;
                }
                
                .result-name {
                    font-size: 13px;
                    font-weight: bold;
                    color: white;
                    margin-bottom: 2px;
                    white-space: nowrap;
                    overflow: hidden;
                    text-overflow: ellipsis;
                }
                
                .result-path {
                    font-size: 10px;
                    color: rgba(255, 255, 255, 0.6);
                    white-space: nowrap;
                    overflow: hidden;
                    text-overflow: ellipsis;
                }
                
                .result-meta {
                    font-size: 9px;
                    color: rgba(255, 255, 255, 0.54);
                    display: flex;
                    gap: 4px;
                }
                
                .open-btn {
                    background: rgba(0, 120, 255, 0.8);
                    border: none;
                    border-radius: 6px;
                    padding: 6px 10px;
                    color: white;
                    font-size: 10px;
                    cursor: pointer;
                    transition: background 0.2s;
                }
                
                .open-btn:hover {
                    background: rgba(0, 140, 255, 0.9);
                }
                
                .bottom-buttons {
                    display: flex;
                    gap: 12px;
                }
                
                .bottom-btn {
                    background: rgba(60, 60, 60, 0.8);
                    border: 1px solid rgba(120, 120, 120, 0.6);
                    border-radius: 10px;
                    padding: 10px 16px;
                    color: white;
                    font-weight: 600;
                    font-size: 13px;
                    cursor: pointer;
                    transition: background 0.2s;
                    flex: 1;
                    text-align: center;
                }
                
                .bottom-btn:hover {
                    background: rgba(80, 80, 80, 0.9);
                }
                
                .empty-state {
                    text-align: center;
                    padding: 40px 20px;
                    color: rgba(255, 255, 255, 0.54);
                }
                
                .empty-icon {
                    font-size: 48px;
                    margin-bottom: 16px;
                    color: rgba(255, 255, 255, 0.3);
                }
                
                /* Scrollbar styling */
                .results-list::-webkit-scrollbar {
                    width: 8px;
                }
                
                .results-list::-webkit-scrollbar-track {
                    background: rgba(60, 60, 60, 0.5);
                    border-radius: 4px;
                }
                
                .results-list::-webkit-scrollbar-thumb {
                    background: rgba(120, 120, 120, 0.8);
                    border-radius: 4px;
                }
                
                .results-list::-webkit-scrollbar-thumb:hover {
                    background: rgba(140, 140, 140, 0.9);
                }
            </style>
        </head>
        <body>
            <div class="header">
                <div class="title">🔍 CloudSearch</div>
                <button class="open-app-btn" onclick="openCloudSearchApp()">Tam Uygulama</button>
            </div>
            
            <div class="search-container">
                <input type="text" class="search-input" placeholder="Dosya, klasör veya içerik ara..." oninput="performSearch(this.value)">
            </div>
            
            <div class="filters">
                <div class="filter-btn active" onclick="setFilter('all')">📄 Tümü</div>
                <div class="filter-btn" onclick="setFilter('documents')">📝 Belgeler</div>
                <div class="filter-btn" onclick="setFilter('images')">🖼️ Resimler</div>
                <div class="filter-btn" onclick="setFilter('code')">💻 Kod</div>
            </div>
            
            <div class="results-title" id="results-title">Arama sonuçları burada görünecek</div>
            
            <div class="results-list" id="results-list">
                <div class="empty-state">
                    <div class="empty-icon">🔍</div>
                    <div>Arama yapmak için yukarıdaki kutuya yazın</div>
                </div>
            </div>
            
            <div class="bottom-buttons">
                <div class="bottom-btn" onclick="openCloudSearchApp()">🔍 Gelişmiş Arama</div>
                <div class="bottom-btn" onclick="openFileManager()">📁 Dosya Yöneticisi</div>
            </div>
            
            <script>
                let currentFilter = 'all';
                let searchResults = [];
                
                const mockResults = [
                    {
                        name: 'document.txt',
                        path: '/users/documents/document.txt',
                        type: 'text',
                        size: '2.4 KB',
                        modified: '2 saat önce',
                        icon: '📄'
                    },
                    {
                        name: 'project.py',
                        path: '/users/projects/project.py',
                        type: 'python',
                        size: '15.7 KB',
                        modified: '1 gün önce',
                        icon: '🐍'
                    },
                    {
                        name: 'image.png',
                        path: '/users/pictures/image.png',
                        type: 'image',
                        size: '1.2 MB',
                        modified: '3 gün önce',
                        icon: '🖼️'
                    }
                ];
                
                function performSearch(query) {
                    if (query.length < 2) {
                        showEmptyState();
                        return;
                    }
                    
                    // Simüle edilmiş arama
                    searchResults = mockResults.filter(item => 
                        item.name.toLowerCase().includes(query.toLowerCase())
                    );
                    
                    displayResults();
                }
                
                function setFilter(filter) {
                    currentFilter = filter;
                    
                    // Filter butonlarını güncelle
                    document.querySelectorAll('.filter-btn').forEach(btn => {
                        btn.classList.remove('active');
                    });
                    event.target.classList.add('active');
                    
                    displayResults();
                }
                
                function displayResults() {
                    const resultsList = document.getElementById('results-list');
                    const resultsTitle = document.getElementById('results-title');
                    
                    if (searchResults.length === 0) {
                        showEmptyState();
                        return;
                    }
                    
                    resultsTitle.textContent = `Sonuçlar (${searchResults.length})`;
                    
                    let html = '';
                    searchResults.forEach(result => {
                        html += `
                            <div class="result-item" onclick="openFile('${result.path}')">
                                <div class="result-icon">${result.icon}</div>
                                <div class="result-content">
                                    <div class="result-name">${result.name}</div>
                                    <div class="result-path">${result.path}</div>
                                    <div class="result-meta">
                                        <span>${result.size}</span>
                                        <span>•</span>
                                        <span>${result.modified}</span>
                                    </div>
                                </div>
                                <button class="open-btn" onclick="event.stopPropagation(); openFile('${result.path}')">Aç</button>
                            </div>
                        `;
                    });
                    
                    resultsList.innerHTML = html;
                }
                
                function showEmptyState() {
                    const resultsList = document.getElementById('results-list');
                    const resultsTitle = document.getElementById('results-title');
                    
                    resultsTitle.textContent = 'Arama sonuçları burada görünecek';
                    resultsList.innerHTML = `
                        <div class="empty-state">
                            <div class="empty-icon">🔍</div>
                            <div>Arama yapmak için yukarıdaki kutuya yazın</div>
                        </div>
                    `;
                }
                
                function openFile(path) {
                    alert('📂 ' + path + ' açılıyor...');
                }
                
                function openCloudSearchApp() {
                    alert('🔍 CloudSearch uygulaması açılıyor...');
                }
                
                function openFileManager() {
                    alert('📁 Dosya yöneticisi açılıyor...');
                }
            </script>
        </body>
        </html>
        """

# Widget factory fonksiyonu
def create_html_widget(widget_type: str) -> Optional[FletHTMLWidget]:
    """HTML widget oluştur"""
    widgets = {
        "notification": HTMLNotificationWidget,
        "clock": HTMLClockWidget,
        "control_center": HTMLControlCenterWidget,
        "cloudsearch": HTMLCloudSearchWidget
    }
    
    widget_class = widgets.get(widget_type)
    if widget_class:
        return widget_class()
    return None 