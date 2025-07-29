#!/usr/bin/env python3
"""
PyCloud OS - Ana Başlatıcı
Modern, modüler, Python tabanlı işletim sistemi
"""

import sys
import os
import logging
import argparse
from pathlib import Path
import time

# PyQt6 import ve gerekli ayarlar
try:
    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtCore import Qt, QCoreApplication
    from PyQt6.QtGui import QIcon
    PYQT_AVAILABLE = True
except ImportError as e:
    print(f"❌ PyQt6 import hatası: {e}")
    print("💡 Çözüm: pip install PyQt6")
    PYQT_AVAILABLE = False

# Proje kök dizinini Python path'ine ekle
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def setup_logging():
    """Logging sistemini kur"""
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        handlers=[
            logging.FileHandler('logs/pycloud.log', encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Log dizinini oluştur
    Path('logs').mkdir(exist_ok=True)

def parse_arguments():
    """Komut satırı argümanlarını parse et"""
    parser = argparse.ArgumentParser(description='PyCloud OS')
    parser.add_argument('--no-splash', action='store_true', 
                       help='Splash screen\'i atla')
    parser.add_argument('--debug', action='store_true',
                       help='Debug modunda başlat')
    parser.add_argument('--safe-mode', action='store_true',
                       help='Güvenli modda başlat')
    parser.add_argument('--version', action='version', version='PyCloud OS v0.9.0-dev')
    
    return parser.parse_args()

def check_dependencies():
    """Gerekli bağımlılıkları kontrol et"""
    required_packages = ['PyQt6', 'PIL', 'psutil']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Eksik paketler: {', '.join(missing_packages)}")
        print("Lütfen şu komutu çalıştırın: pip install -r requirements.txt")
        return False
    
    return True

def main():
    """Ana fonksiyon"""
    # Argümanları parse et
    args = parse_arguments()
    
    # Logging kurulumu
    setup_logging()
    logger = logging.getLogger("PyCloudOS")
    
    logger.info("🌩️ PyCloud OS başlatılıyor...")
    
    if not PYQT_AVAILABLE:
        logger.error("PyQt6 bulunamadı. GUI başlatılamıyor.")
        return 1
    
    # WebEngine için gerekli ayar
    QCoreApplication.setAttribute(Qt.ApplicationAttribute.AA_ShareOpenGLContexts)
    
    # QApplication oluştur
    app = QApplication(sys.argv)
    app.setApplicationName("PyCloud OS")
    app.setApplicationVersion("0.9.0-dev")
    app.setOrganizationName("PyCloud")
    
    # Uygulama ikonu
    icon_path = Path("system/logo/cloud.png")
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))
    
    splash = None
    kernel = None
    
    try:
        # Splash screen göster (eğer devre dışı değilse)
        if not args.no_splash:
            try:
                from boot.splash import show_splash
                splash = show_splash()
                if splash:
                    logger.info("✨ Splash screen gösteriliyor")
                    app.processEvents()  # Splash'in görünmesini sağla
            except Exception as e:
                logger.warning(f"Splash screen başlatılamadı: {e}")
        
        # Kernel başlat
        logger.info("🔧 Çekirdek başlatılıyor...")
        from core.kernel import PyCloudKernel
        
        kernel = PyCloudKernel(debug_mode=args.debug, safe_mode=args.safe_mode)
        
        # Splash'e kernel referansı ver
        if splash:
            splash.kernel = kernel
        
        # Kernel başlatma
        if not kernel.start():
            logger.error("❌ Çekirdek başlatılamadı")
            return 1
        
        logger.info("✅ Çekirdek başarıyla başlatıldı")
        
        # Rain UI başlat
        logger.info("🎨 Arayüz başlatılıyor...")
        from rain.ui import RainUI
        
        ui = RainUI(kernel)
        
        # Splash'in minimum süresini bekle ve yumuşak geçiş yap
        if splash:
            # Splash'in tamamlanmasını bekle
            time.sleep(2.0)  # Ek 2 saniye bekleme (1 saniyeden artırdık)
            app.processEvents()
            splash._finish_splash()
            
            # Splash kapanana kadar bekle
            time.sleep(2.5)  # Fade out animasyonunun tamamlanması için (1.5 saniyeden artırdık)
        
        # Ana arayüzü göster
        ui.show()
        logger.info("🚀 PyCloud OS hazır!")
        
        # Event loop başlat
        exit_code = app.exec()
        
        # Temizlik
        logger.info("🔄 Sistem kapatılıyor...")
        if kernel:
            kernel.shutdown()
        
        logger.info("👋 PyCloud OS kapatıldı")
        return exit_code
        
    except KeyboardInterrupt:
        logger.info("⚠️ Kullanıcı tarafından durduruldu")
        return 0
        
    except Exception as e:
        logger.error(f"💥 Kritik hata: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return 1
        
    finally:
        # Splash'i temizle
        if splash:
            try:
                splash.close()
            except:
                pass
        
        # Kernel'i temizle
        if kernel:
            try:
                kernel.shutdown()
            except:
                pass

if __name__ == "__main__":
    sys.exit(main()) 