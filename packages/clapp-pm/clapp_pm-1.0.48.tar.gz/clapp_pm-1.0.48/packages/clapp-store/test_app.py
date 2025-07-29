#!/usr/bin/env python3
"""
Clapp Store Test Uygulaması
Bu dosya, Clapp Store uygulamasının temel işlevlerini test etmek için kullanılır.
"""

import requests
import subprocess
import sys
import os

def test_internet_connection():
    """İnternet bağlantısını test et"""
    print("🌐 İnternet bağlantısı test ediliyor...")
    try:
        response = requests.get("https://raw.githubusercontent.com/mburakmmm/clapp-packages/main/index.json", timeout=5)
        if response.status_code == 200:
            print("✅ İnternet bağlantısı başarılı")
            return True
        else:
            print(f"❌ GitHub'a erişim sorunu: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ İnternet bağlantısı hatası: {e}")
        return False

def test_clapp_installation():
    """Clapp paket yöneticisinin yüklü olup olmadığını test et"""
    print("📦 Clapp paket yöneticisi test ediliyor...")
    try:
        result = subprocess.run(["clapp", "version"], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print("✅ Clapp paket yöneticisi yüklü")
            print(f"   Versiyon: {result.stdout.strip()}")
            return True
        else:
            print("❌ Clapp paket yöneticisi bulunamadı")
            return False
    except FileNotFoundError:
        print("❌ Clapp komutu bulunamadı. Lütfen 'pip install clapp-pm' komutunu çalıştırın.")
        return False
    except Exception as e:
        print(f"❌ Clapp test hatası: {e}")
        return False

def test_packages_fetch():
    """Paket listesini çekmeyi test et"""
    print("📋 Paket listesi test ediliyor...")
    try:
        response = requests.get("https://raw.githubusercontent.com/mburakmmm/clapp-packages/main/index.json", timeout=10)
        if response.status_code == 200:
            packages = response.json()
            print(f"✅ {len(packages)} paket bulundu")
            if packages:
                print("   Örnek paketler:")
                for i, package in enumerate(packages[:3]):
                    print(f"   - {package.get('name', 'Bilinmeyen')} v{package.get('version', '1.0.0')}")
            return True
        else:
            print(f"❌ Paket listesi alınamadı: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Paket listesi hatası: {e}")
        return False

def test_installed_packages():
    """Yüklü paketleri listele"""
    print("📥 Yüklü paketler kontrol ediliyor...")
    try:
        result = subprocess.run(["clapp", "list"], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            installed = result.stdout.strip().split('\n')
            installed = [pkg.strip() for pkg in installed if pkg.strip()]
            print(f"✅ {len(installed)} yüklü paket bulundu")
            if installed:
                print("   Yüklü paketler:")
                for pkg in installed:
                    print(f"   - {pkg}")
            else:
                print("   Henüz yüklü paket yok")
            return True
        else:
            print("❌ Yüklü paketler listelenemedi")
            return False
    except Exception as e:
        print(f"❌ Yüklü paketler hatası: {e}")
        return False

def test_dependencies():
    """Gerekli Python paketlerini kontrol et"""
    print("🔧 Python bağımlılıkları kontrol ediliyor...")
    required_packages = ['flet', 'requests']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} yüklü")
        except ImportError:
            print(f"❌ {package} eksik")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️  Eksik paketler: {', '.join(missing_packages)}")
        print("   Lütfen 'pip install -r requirements.txt' komutunu çalıştırın.")
        return False
    else:
        print("✅ Tüm bağımlılıklar yüklü")
        return True

def main():
    """Ana test fonksiyonu"""
    print("🚀 Clapp Store Test Uygulaması")
    print("=" * 50)
    
    tests = [
        ("Python Bağımlılıkları", test_dependencies),
        ("İnternet Bağlantısı", test_internet_connection),
        ("Clapp Paket Yöneticisi", test_clapp_installation),
        ("Paket Listesi", test_packages_fetch),
        ("Yüklü Paketler", test_installed_packages),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        print("-" * 30)
        if test_func():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"📊 Test Sonuçları: {passed}/{total} başarılı")
    
    if passed == total:
        print("🎉 Tüm testler başarılı! Clapp Store uygulamasını çalıştırabilirsiniz.")
        print("   Komut: python main.py")
    else:
        print("⚠️  Bazı testler başarısız. Lütfen yukarıdaki hataları düzeltin.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 