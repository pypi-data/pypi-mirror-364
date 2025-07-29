"""
PyCloud OS Rain Wallpaper
Sistem temalı ve kullanıcıya özel duvar kağıdı yöneticisi
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from enum import Enum

try:
    from PyQt6.QtWidgets import (QWidget, QLabel, QVBoxLayout, QHBoxLayout,
                                QPushButton, QFileDialog, QMessageBox, QDialog,
                                QGridLayout, QScrollArea, QFrame, QSlider,
                                QComboBox, QCheckBox, QSpinBox)
    from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QSize, QRect
    from PyQt6.QtGui import QPixmap, QPainter, QBrush, QColor, QPalette
    PYQT_AVAILABLE = True
except ImportError:
    PYQT_AVAILABLE = False
    # Dummy classes for type hints
    class QSize:
        pass
    class QPixmap:
        pass

class WallpaperMode(Enum):
    """Duvar kağıdı modları"""
    STRETCH = "stretch"
    FIT = "fit"
    FILL = "fill"
    CENTER = "center"
    TILE = "tile"

class WallpaperType(Enum):
    """Duvar kağıdı türleri"""
    STATIC = "static"
    SLIDESHOW = "slideshow"
    SOLID_COLOR = "solid_color"

@dataclass
class WallpaperConfig:
    """Duvar kağıdı yapılandırması"""
    wallpaper_type: WallpaperType = WallpaperType.STATIC
    current_path: str = ""
    mode: WallpaperMode = WallpaperMode.FILL
    slideshow_paths: List[str] = None
    slideshow_interval: int = 300  # saniye
    solid_color: str = "#2d2d2d"
    blur_amount: int = 0
    brightness: float = 1.0
    contrast: float = 1.0
    
    def __post_init__(self):
        if self.slideshow_paths is None:
            self.slideshow_paths = []
    
    def to_dict(self) -> Dict:
        """Dict'e çevir"""
        data = asdict(self)
        data['wallpaper_type'] = self.wallpaper_type.value
        data['mode'] = self.mode.value
        return data
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'WallpaperConfig':
        """Dict'ten oluştur"""
        data['wallpaper_type'] = WallpaperType(data.get('wallpaper_type', 'static'))
        data['mode'] = WallpaperMode(data.get('mode', 'fill'))
        return cls(**data)

class WallpaperManager:
    """Duvar kağıdı yöneticisi"""
    
    def __init__(self, kernel=None):
        self.kernel = kernel
        self.logger = logging.getLogger("WallpaperManager")
        
        # Dizinler
        self.system_wallpapers_dir = Path("system/wallpapers")
        self.user_wallpapers_dir = Path("users/wallpapers")
        self.system_wallpapers_dir.mkdir(parents=True, exist_ok=True)
        self.user_wallpapers_dir.mkdir(parents=True, exist_ok=True)
        
        # Yapılandırma
        self.config_file = Path("users/wallpaper_config.json")
        self.config = WallpaperConfig()
        
        # Slideshow timer
        self.slideshow_timer = None
        self.slideshow_index = 0
        
        # Cache
        self.wallpaper_cache: Dict[str, QPixmap] = {}
        
        # Başlangıç
        self.create_default_wallpapers()
        self.load_config()
        self.setup_slideshow_timer()
    
    def create_default_wallpapers(self):
        """Varsayılan duvar kağıtları oluştur"""
        try:
            # PyQt6 kullanılamıyorsa atlayalım
            if not PYQT_AVAILABLE:
                self.logger.warning("PyQt6 not available, skipping default wallpaper creation")
                return
            
            # QApplication henüz başlatılmamışsa atlayalım
            from PyQt6.QtWidgets import QApplication
            if QApplication.instance() is None:
                self.logger.info("QApplication not available yet, will create wallpapers later")
                return
            
            # Sistem duvar kağıtları için placeholder'lar
            default_wallpapers = [
                ("default_dark.png", "#1e1e1e"),
                ("default_light.png", "#f5f5f5"),
                ("gradient_blue.png", "#2196F3"),
                ("gradient_purple.png", "#9C27B0"),
            ]
            
            for filename, color in default_wallpapers:
                wallpaper_path = self.system_wallpapers_dir / filename
                if not wallpaper_path.exists():
                    self.create_solid_color_wallpaper(color, wallpaper_path)
            
            self.logger.info("Default wallpapers created")
            
        except Exception as e:
            self.logger.error(f"Failed to create default wallpapers: {e}")
    
    def create_solid_color_wallpaper(self, color: str, output_path: Path, size: tuple = (1920, 1080)):
        """Düz renk duvar kağıdı oluştur"""
        try:
            if not PYQT_AVAILABLE:
                return
            
            pixmap = QPixmap(*size)
            pixmap.fill(QColor(color))
            
            # Gradient efekti ekle
            painter = QPainter(pixmap)
            gradient_color = QColor(color)
            gradient_color.setAlpha(50)
            
            # Köşelerden merkeze doğru gradient
            for i in range(min(size) // 4):
                painter.setPen(gradient_color)
                painter.drawRect(i, i, size[0] - 2*i, size[1] - 2*i)
            
            painter.end()
            
            pixmap.save(str(output_path))
            
        except Exception as e:
            self.logger.error(f"Failed to create solid color wallpaper: {e}")
    
    def load_config(self):
        """Yapılandırmayı yükle"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                
                self.config = WallpaperConfig.from_dict(config_data)
                
                # Mevcut duvar kağıdının var olup olmadığını kontrol et
                if self.config.current_path and not Path(self.config.current_path).exists():
                    self.logger.warning(f"Current wallpaper not found: {self.config.current_path}")
                    self.config.current_path = ""
            
            # Eğer duvar kağıdı ayarlanmamışsa varsayılanı kullan
            if not self.config.current_path:
                # Önce default.png'yi kontrol et
                default_wallpaper = self.system_wallpapers_dir / "default.png"
                if default_wallpaper.exists():
                    self.config.current_path = str(default_wallpaper)
                    self.logger.info(f"Using default.png wallpaper: {default_wallpaper}")
                else:
                    # Fallback: default_dark.png
                    fallback_wallpaper = self.system_wallpapers_dir / "default_dark.png"
                    if fallback_wallpaper.exists():
                        self.config.current_path = str(fallback_wallpaper)
                        self.logger.info(f"Using fallback wallpaper: {fallback_wallpaper}")
                
                self.save_config()
            
            self.logger.info(f"Wallpaper config loaded: {self.config.current_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to load wallpaper config: {e}")
            # Hata durumunda default.png'yi kullanmaya çalış
            default_wallpaper = self.system_wallpapers_dir / "default.png"
            if default_wallpaper.exists():
                self.config.current_path = str(default_wallpaper)
                self.save_config()
    
    def save_config(self):
        """Yapılandırmayı kaydet"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config.to_dict(), f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            self.logger.error(f"Failed to save wallpaper config: {e}")
    
    def setup_slideshow_timer(self):
        """Slideshow timer'ını ayarla"""
        if PYQT_AVAILABLE and self.config.wallpaper_type == WallpaperType.SLIDESHOW:
            if self.slideshow_timer:
                self.slideshow_timer.stop()
            
            self.slideshow_timer = QTimer()
            self.slideshow_timer.timeout.connect(self.next_slideshow_wallpaper)
            self.slideshow_timer.start(self.config.slideshow_interval * 1000)
    
    def get_available_wallpapers(self) -> List[Dict]:
        """Mevcut duvar kağıtlarını al"""
        wallpapers = []
        
        # Sistem duvar kağıtları - tüm desteklenen formatları kontrol et
        for wallpaper_path in self.system_wallpapers_dir.glob("*"):
            if wallpaper_path.suffix.lower() in ['.png', '.jpg', '.jpeg', '.bmp', '.webp']:
                wallpapers.append({
                    "name": wallpaper_path.stem,
                    "path": str(wallpaper_path),
                    "type": "system",
                    "size": self.get_image_size(wallpaper_path)
                })
        
        # Kullanıcı duvar kağıtları
        for wallpaper_path in self.user_wallpapers_dir.glob("*"):
            if wallpaper_path.suffix.lower() in ['.png', '.jpg', '.jpeg', '.bmp', '.webp']:
                wallpapers.append({
                    "name": wallpaper_path.stem,
                    "path": str(wallpaper_path),
                    "type": "user",
                    "size": self.get_image_size(wallpaper_path)
                })
        
        # Alfabetik olarak sırala
        wallpapers.sort(key=lambda x: x["name"].lower())
        
        return wallpapers
    
    def get_image_size(self, image_path: Path) -> tuple:
        """Resim boyutunu al"""
        try:
            if PYQT_AVAILABLE:
                pixmap = QPixmap(str(image_path))
                return (pixmap.width(), pixmap.height())
            return (0, 0)
        except:
            return (0, 0)
    
    def set_wallpaper(self, wallpaper_path: str, mode: WallpaperMode = None) -> bool:
        """Duvar kağıdını ayarla"""
        try:
            if not Path(wallpaper_path).exists():
                self.logger.error(f"Wallpaper not found: {wallpaper_path}")
                return False
            
            self.config.wallpaper_type = WallpaperType.STATIC
            self.config.current_path = wallpaper_path
            
            if mode:
                self.config.mode = mode
            
            self.save_config()
            self.apply_wallpaper()
            
            self.logger.info(f"Wallpaper set: {wallpaper_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to set wallpaper: {e}")
            return False
    
    def set_solid_color(self, color: str) -> bool:
        """Düz renk duvar kağıdı ayarla"""
        try:
            self.config.wallpaper_type = WallpaperType.SOLID_COLOR
            self.config.solid_color = color
            
            self.save_config()
            self.apply_wallpaper()
            
            self.logger.info(f"Solid color wallpaper set: {color}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to set solid color: {e}")
            return False
    
    def set_slideshow(self, wallpaper_paths: List[str], interval: int = 300) -> bool:
        """Slideshow ayarla"""
        try:
            # Geçerli dosyaları filtrele
            valid_paths = [path for path in wallpaper_paths if Path(path).exists()]
            
            if not valid_paths:
                self.logger.error("No valid wallpapers for slideshow")
                return False
            
            self.config.wallpaper_type = WallpaperType.SLIDESHOW
            self.config.slideshow_paths = valid_paths
            self.config.slideshow_interval = interval
            self.slideshow_index = 0
            
            self.save_config()
            self.setup_slideshow_timer()
            self.apply_wallpaper()
            
            self.logger.info(f"Slideshow set with {len(valid_paths)} wallpapers")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to set slideshow: {e}")
            return False
    
    def next_slideshow_wallpaper(self):
        """Slideshow'da sonraki duvar kağıdına geç"""
        try:
            if (self.config.wallpaper_type == WallpaperType.SLIDESHOW and 
                self.config.slideshow_paths):
                
                self.slideshow_index = (self.slideshow_index + 1) % len(self.config.slideshow_paths)
                self.config.current_path = self.config.slideshow_paths[self.slideshow_index]
                
                self.apply_wallpaper()
                
        except Exception as e:
            self.logger.error(f"Failed to switch slideshow wallpaper: {e}")
    
    def apply_wallpaper(self):
        """Duvar kağıdını uygula"""
        try:
            if not self.kernel:
                return
            
            # QApplication kontrolü
            if not PYQT_AVAILABLE:
                return
            
            from PyQt6.QtWidgets import QApplication
            if QApplication.instance() is None:
                self.logger.info("QApplication not ready, wallpaper will be applied later")
                return
            
            ui = self.kernel.get_module("ui")
            if not ui or not hasattr(ui, 'desktop'):
                return
            
            desktop = ui.desktop
            
            # Varsayılan duvar kağıtlarını kontrol et
            self.ensure_default_wallpapers()
            
            if self.config.wallpaper_type == WallpaperType.SOLID_COLOR:
                self.apply_solid_color(desktop)
            else:
                self.apply_image_wallpaper(desktop)
                
        except Exception as e:
            self.logger.error(f"Failed to apply wallpaper: {e}")
    
    def ensure_default_wallpapers(self):
        """Varsayılan duvar kağıtlarının varlığını garanti et"""
        try:
            # QApplication kontrolü
            if not PYQT_AVAILABLE:
                return
            
            from PyQt6.QtWidgets import QApplication
            if QApplication.instance() is None:
                return
            
            # Varsayılan duvar kağıtlarını oluştur
            default_wallpapers = [
                ("default_dark.png", "#1e1e1e"),
                ("default_light.png", "#f5f5f5"),
                ("gradient_blue.png", "#2196F3"),
                ("gradient_purple.png", "#9C27B0"),
            ]
            
            for filename, color in default_wallpapers:
                wallpaper_path = self.system_wallpapers_dir / filename
                if not wallpaper_path.exists():
                    self.create_solid_color_wallpaper(color, wallpaper_path)
            
        except Exception as e:
            self.logger.error(f"Failed to ensure default wallpapers: {e}")
    
    def apply_solid_color(self, desktop_widget):
        """Düz renk duvar kağıdı uygula"""
        try:
            if not PYQT_AVAILABLE:
                return
            
            color = self.config.solid_color
            desktop_widget.setStyleSheet(f"""
                QWidget {{
                    background-color: {color};
                }}
            """)
            
        except Exception as e:
            self.logger.error(f"Failed to apply solid color: {e}")
    
    def apply_image_wallpaper(self, desktop_widget):
        """Resim duvar kağıdı uygula"""
        try:
            if not PYQT_AVAILABLE or not self.config.current_path:
                return
            
            wallpaper_path = self.config.current_path
            
            # Cache'den al veya yükle
            if wallpaper_path in self.wallpaper_cache:
                pixmap = self.wallpaper_cache[wallpaper_path]
            else:
                pixmap = QPixmap(wallpaper_path)
                if pixmap.isNull():
                    self.logger.error(f"Failed to load wallpaper: {wallpaper_path}")
                    return
                
                # Efektleri uygula
                pixmap = self.apply_effects(pixmap)
                self.wallpaper_cache[wallpaper_path] = pixmap
            
            # Desktop boyutunu al
            desktop_size = desktop_widget.size()
            
            # Modu uygula
            scaled_pixmap = self.scale_wallpaper(pixmap, desktop_size, self.config.mode)
            
            # Stylesheet oluştur
            # PyQt6'da background-image için geçici dosya kullanmak gerekebilir
            temp_path = Path("temp/current_wallpaper.png")
            temp_path.parent.mkdir(exist_ok=True)
            scaled_pixmap.save(str(temp_path))
            
            desktop_widget.setStyleSheet(f"""
                QWidget {{
                    background-image: url({temp_path});
                    background-repeat: no-repeat;
                    background-position: center;
                }}
            """)
            
        except Exception as e:
            self.logger.error(f"Failed to apply image wallpaper: {e}")
    
    def apply_effects(self, pixmap: QPixmap) -> QPixmap:
        """Duvar kağıdına efektler uygula"""
        try:
            if not PYQT_AVAILABLE:
                return pixmap
            
            # Brightness ve contrast ayarları
            if self.config.brightness != 1.0 or self.config.contrast != 1.0:
                # Basit brightness/contrast implementasyonu
                # Gerçek uygulamada daha gelişmiş efektler kullanılabilir
                pass
            
            # Blur efekti
            if self.config.blur_amount > 0:
                # Blur implementasyonu
                pass
            
            return pixmap
            
        except Exception as e:
            self.logger.error(f"Failed to apply effects: {e}")
            return pixmap
    
    def scale_wallpaper(self, pixmap: QPixmap, target_size: QSize, mode: WallpaperMode) -> QPixmap:
        """Duvar kağıdını ölçekle"""
        try:
            if not PYQT_AVAILABLE:
                return pixmap
            
            if mode == WallpaperMode.STRETCH:
                return pixmap.scaled(target_size, Qt.AspectRatioMode.IgnoreAspectRatio, 
                                   Qt.TransformationMode.SmoothTransformation)
            
            elif mode == WallpaperMode.FIT:
                return pixmap.scaled(target_size, Qt.AspectRatioMode.KeepAspectRatio, 
                                   Qt.TransformationMode.SmoothTransformation)
            
            elif mode == WallpaperMode.FILL:
                return pixmap.scaled(target_size, Qt.AspectRatioMode.KeepAspectRatioByExpanding, 
                                   Qt.TransformationMode.SmoothTransformation)
            
            elif mode == WallpaperMode.CENTER:
                # Merkeze yerleştir, ölçekleme yok
                result = QPixmap(target_size)
                result.fill(Qt.GlobalColor.black)
                
                painter = QPainter(result)
                x = (target_size.width() - pixmap.width()) // 2
                y = (target_size.height() - pixmap.height()) // 2
                painter.drawPixmap(x, y, pixmap)
                painter.end()
                
                return result
            
            elif mode == WallpaperMode.TILE:
                # Döşeme modu
                result = QPixmap(target_size)
                painter = QPainter(result)
                
                for x in range(0, target_size.width(), pixmap.width()):
                    for y in range(0, target_size.height(), pixmap.height()):
                        painter.drawPixmap(x, y, pixmap)
                
                painter.end()
                return result
            
            return pixmap
            
        except Exception as e:
            self.logger.error(f"Failed to scale wallpaper: {e}")
            return pixmap
    
    def add_wallpaper(self, source_path: str) -> bool:
        """Yeni duvar kağıdı ekle"""
        try:
            source = Path(source_path)
            if not source.exists():
                return False
            
            # Hedef dosya adı
            target_name = source.name
            target_path = self.user_wallpapers_dir / target_name
            
            # Aynı isimde dosya varsa yeni isim oluştur
            counter = 1
            while target_path.exists():
                name_parts = source.stem, counter, source.suffix
                target_name = f"{name_parts[0]}_{name_parts[1]}{name_parts[2]}"
                target_path = self.user_wallpapers_dir / target_name
                counter += 1
            
            # Dosyayı kopyala
            import shutil
            shutil.copy2(source, target_path)
            
            self.logger.info(f"Wallpaper added: {target_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to add wallpaper: {e}")
            return False
    
    def remove_wallpaper(self, wallpaper_path: str) -> bool:
        """Duvar kağıdını kaldır"""
        try:
            path = Path(wallpaper_path)
            
            # Sistem duvar kağıtlarını silmeye izin verme
            if path.parent == self.system_wallpapers_dir:
                self.logger.warning("Cannot remove system wallpaper")
                return False
            
            if path.exists():
                path.unlink()
                
                # Cache'den kaldır
                if wallpaper_path in self.wallpaper_cache:
                    del self.wallpaper_cache[wallpaper_path]
                
                self.logger.info(f"Wallpaper removed: {wallpaper_path}")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to remove wallpaper: {e}")
            return False
    
    def show_wallpaper_dialog(self) -> bool:
        """Duvar kağıdı seçim dialogu göster"""
        try:
            if not PYQT_AVAILABLE:
                return False
            
            dialog = WallpaperDialog(self)
            return dialog.exec() == QDialog.DialogCode.Accepted
            
        except Exception as e:
            self.logger.error(f"Failed to show wallpaper dialog: {e}")
            return False
    
    def shutdown(self):
        """Wallpaper manager'ı kapat"""
        try:
            if self.slideshow_timer:
                self.slideshow_timer.stop()
            
            self.wallpaper_cache.clear()
            self.save_config()
            
            self.logger.info("Wallpaper manager shutdown completed")
            
        except Exception as e:
            self.logger.error(f"Wallpaper manager shutdown failed: {e}")

class WallpaperDialog(QDialog if PYQT_AVAILABLE else object):
    """Duvar kağıdı seçim dialogu"""
    
    def __init__(self, wallpaper_manager: WallpaperManager):
        super().__init__()
        self.wallpaper_manager = wallpaper_manager
        self.selected_wallpaper = None
        
        self.setup_ui()
        self.load_wallpapers()
    
    def setup_ui(self):
        """Arayüzü kur"""
        self.setWindowTitle("Duvar Kağıdı Seçici")
        self.setFixedSize(800, 600)
        
        layout = QVBoxLayout(self)
        
        # Üst kontroller
        controls_layout = QHBoxLayout()
        
        # Duvar kağıdı türü
        self.type_combo = QComboBox()
        self.type_combo.addItems(["Statik", "Slideshow", "Düz Renk"])
        self.type_combo.currentTextChanged.connect(self.on_type_changed)
        controls_layout.addWidget(QLabel("Tür:"))
        controls_layout.addWidget(self.type_combo)
        
        controls_layout.addStretch()
        
        # Duvar kağıdı ekle
        add_btn = QPushButton("📁 Duvar Kağıdı Ekle")
        add_btn.clicked.connect(self.add_wallpaper)
        controls_layout.addWidget(add_btn)
        
        layout.addLayout(controls_layout)
        
        # Duvar kağıdı listesi
        self.scroll_area = QScrollArea()
        self.wallpaper_widget = QWidget()
        self.wallpaper_layout = QGridLayout(self.wallpaper_widget)
        self.scroll_area.setWidget(self.wallpaper_widget)
        self.scroll_area.setWidgetResizable(True)
        layout.addWidget(self.scroll_area)
        
        # Alt kontroller
        bottom_layout = QHBoxLayout()
        
        # Mod seçimi
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["Doldur", "Sığdır", "Uzat", "Merkez", "Döşe"])
        bottom_layout.addWidget(QLabel("Mod:"))
        bottom_layout.addWidget(self.mode_combo)
        
        bottom_layout.addStretch()
        
        # Butonlar
        apply_btn = QPushButton("Uygula")
        apply_btn.clicked.connect(self.apply_wallpaper)
        bottom_layout.addWidget(apply_btn)
        
        cancel_btn = QPushButton("İptal")
        cancel_btn.clicked.connect(self.reject)
        bottom_layout.addWidget(cancel_btn)
        
        layout.addLayout(bottom_layout)
    
    def load_wallpapers(self):
        """Duvar kağıtlarını yükle"""
        try:
            # Mevcut widget'ları temizle
            for i in reversed(range(self.wallpaper_layout.count())):
                self.wallpaper_layout.itemAt(i).widget().setParent(None)
            
            wallpapers = self.wallpaper_manager.get_available_wallpapers()
            
            row, col = 0, 0
            max_cols = 4
            
            for wallpaper in wallpapers:
                preview = self.create_wallpaper_preview(wallpaper)
                self.wallpaper_layout.addWidget(preview, row, col)
                
                col += 1
                if col >= max_cols:
                    col = 0
                    row += 1
                    
        except Exception as e:
            self.wallpaper_manager.logger.error(f"Failed to load wallpapers: {e}")
    
    def create_wallpaper_preview(self, wallpaper: Dict) -> QWidget:
        """Duvar kağıdı önizlemesi oluştur"""
        try:
            preview = QFrame()
            preview.setFixedSize(150, 120)
            preview.setFrameStyle(QFrame.Shape.Box)
            preview.setStyleSheet("""
                QFrame {
                    border: 2px solid #404040;
                    border-radius: 8px;
                    background-color: #2d2d2d;
                }
                QFrame:hover {
                    border-color: #2196F3;
                }
            """)
            
            layout = QVBoxLayout(preview)
            
            # Önizleme resmi
            image_label = QLabel()
            image_label.setFixedSize(130, 80)
            image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            image_label.setStyleSheet("border: 1px solid #555; background-color: #1e1e1e;")
            
            # Resmi yükle
            pixmap = QPixmap(wallpaper["path"])
            if not pixmap.isNull():
                scaled_pixmap = pixmap.scaled(130, 80, Qt.AspectRatioMode.KeepAspectRatio, 
                                            Qt.TransformationMode.SmoothTransformation)
                image_label.setPixmap(scaled_pixmap)
            else:
                image_label.setText("📷")
            
            layout.addWidget(image_label)
            
            # İsim
            name_label = QLabel(wallpaper["name"])
            name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            name_label.setStyleSheet("color: white; font-size: 10px; border: none;")
            layout.addWidget(name_label)
            
            # Tıklama olayı
            preview.mousePressEvent = lambda event: self.select_wallpaper(wallpaper["path"])
            
            return preview
            
        except Exception as e:
            self.wallpaper_manager.logger.error(f"Failed to create preview: {e}")
            return QWidget()
    
    def select_wallpaper(self, wallpaper_path: str):
        """Duvar kağıdını seç"""
        self.selected_wallpaper = wallpaper_path
    
    def on_type_changed(self, type_text: str):
        """Tür değiştiğinde"""
        # TODO: Tür değişikliği implementasyonu
        pass
    
    def add_wallpaper(self):
        """Yeni duvar kağıdı ekle"""
        try:
            file_path, _ = QFileDialog.getOpenFileName(
                self, "Duvar Kağıdı Seç", "",
                "Resim Dosyaları (*.png *.jpg *.jpeg *.bmp *.webp)"
            )
            
            if file_path:
                if self.wallpaper_manager.add_wallpaper(file_path):
                    self.load_wallpapers()
                else:
                    QMessageBox.warning(self, "Hata", "Duvar kağıdı eklenemedi!")
                    
        except Exception as e:
            self.wallpaper_manager.logger.error(f"Failed to add wallpaper: {e}")
    
    def apply_wallpaper(self):
        """Duvar kağıdını uygula"""
        try:
            if not self.selected_wallpaper:
                QMessageBox.warning(self, "Uyarı", "Lütfen bir duvar kağıdı seçin!")
                return
            
            # Modu al
            mode_map = {
                "Doldur": WallpaperMode.FILL,
                "Sığdır": WallpaperMode.FIT,
                "Uzat": WallpaperMode.STRETCH,
                "Merkez": WallpaperMode.CENTER,
                "Döşe": WallpaperMode.TILE,
            }
            
            mode = mode_map.get(self.mode_combo.currentText(), WallpaperMode.FILL)
            
            if self.wallpaper_manager.set_wallpaper(self.selected_wallpaper, mode):
                self.accept()
            else:
                QMessageBox.warning(self, "Hata", "Duvar kağıdı ayarlanamadı!")
                
        except Exception as e:
            self.wallpaper_manager.logger.error(f"Failed to apply wallpaper: {e}")

# Kolaylık fonksiyonları
_wallpaper_manager = None

def init_wallpaper_manager(kernel=None) -> WallpaperManager:
    """Wallpaper manager'ı başlat"""
    global _wallpaper_manager
    _wallpaper_manager = WallpaperManager(kernel)
    return _wallpaper_manager

def get_wallpaper_manager() -> Optional[WallpaperManager]:
    """Wallpaper manager'ı al"""
    return _wallpaper_manager

def set_wallpaper(wallpaper_path: str, mode: WallpaperMode = WallpaperMode.FILL) -> bool:
    """Duvar kağıdı ayarla (kısayol)"""
    if _wallpaper_manager:
        return _wallpaper_manager.set_wallpaper(wallpaper_path, mode)
    return False

def show_wallpaper_dialog() -> bool:
    """Duvar kağıdı dialogu göster (kısayol)"""
    if _wallpaper_manager:
        return _wallpaper_manager.show_wallpaper_dialog()
    return False 