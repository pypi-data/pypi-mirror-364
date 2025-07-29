#!/usr/bin/env python3
"""
Clapp Store Başlatma Scripti
Bu script, Clapp Store uygulamasını başlatmadan önce gerekli kontrolleri yapar.
"""

import sys
import subprocess
import os

def check_python_version():
    """Python sürümünü kontrol et"""
    if sys.version_info < (3, 7):
        print("❌ Python 3.7 veya daha yüksek bir sürüm gerekli!")
        print(f"   Mevcut sürüm: {sys.version}")
        return False
    print(f"✅ Python sürümü uygun: {sys.version.split()[0]}")
    return True

def check_dependencies():
    """Gerekli paketlerin yüklü olup olmadığını kontrol et"""
    required_packages = ['flet', 'requests']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Eksik paketler: {', '.join(missing_packages)}")
        print("   Lütfen aşağıdaki komutu çalıştırın:")
        print("   pip install -r requirements.txt")
        return False
    
    print("✅ Tüm bağımlılıklar yüklü")
    return True

def check_clapp():
    """Clapp paket yöneticisinin yüklü olup olmadığını kontrol et"""
    try:
        result = subprocess.run(["clapp", "version"], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print(f"✅ Clapp paket yöneticisi yüklü: {result.stdout.strip()}")
            return True
        else:
            print("❌ Clapp paket yöneticisi bulunamadı")
            return False
    except FileNotFoundError:
        print("❌ Clapp komutu bulunamadı")
        print("   Lütfen aşağıdaki komutu çalıştırın:")
        print("   pip install clapp-pm")
        return False
    except Exception as e:
        print(f"❌ Clapp kontrol hatası: {e}")
        return False

def main():
    """Ana başlatma fonksiyonu"""
    print("🚀 Clapp Store Başlatılıyor...")
    print("=" * 40)
    
    # Kontroller
    checks = [
        ("Python Sürümü", check_python_version),
        ("Bağımlılıklar", check_dependencies),
        ("Clapp Paket Yöneticisi", check_clapp),
    ]
    
    for check_name, check_func in checks:
        print(f"\n{check_name} kontrol ediliyor...")
        if not check_func():
            print(f"\n❌ {check_name} kontrolü başarısız!")
            print("Lütfen yukarıdaki hataları düzeltin ve tekrar deneyin.")
            return False
    
    print("\n" + "=" * 40)
    print("✅ Tüm kontroller başarılı!")
    print("🎉 Clapp Store başlatılıyor...")
    print()
    
    # Ana uygulamayı başlat
    try:
        from main import main as app_main
        import flet as ft
        ft.app(target=app_main)
    except ImportError as e:
        print(f"❌ Uygulama başlatılamadı: {e}")
        print("Lütfen main.py dosyasının mevcut olduğundan emin olun.")
        return False
    except Exception as e:
        print(f"❌ Uygulama hatası: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 