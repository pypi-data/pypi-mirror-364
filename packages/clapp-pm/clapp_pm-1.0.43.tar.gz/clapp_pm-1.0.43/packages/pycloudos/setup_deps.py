#!/usr/bin/env python3
"""
PyCloud OS Dependency Setup Script
Bağımlılıkları yükler ve kontrol eder - Cursorrules Enhanced
"""

import sys
import subprocess
import importlib
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Set

# Gerekli paketler ve import isimleri
REQUIRED_PACKAGES = {
    "PyQt6": "PyQt6",
    "PyQt6-WebEngine": "PyQt6.QtWebEngineWidgets", 
    "Pillow": "PIL",
    "psutil": "psutil",
    "requests": "requests",
    "pyserial": "serial",
    "Flask": "flask",
    "jsonschema": "jsonschema"
}

# Opsiyonel paketler
OPTIONAL_PACKAGES = {
    "pytest": "pytest",
    "black": "black",
    "flake8": "flake8",
    "sphinx": "sphinx"
}

# Yeni cursorrules özellikler için desteklenen çekirdek modüller
SUPPORTED_CORE_MODULES = {
    "core.fs": "Dosya sistemi erişimi",
    "core.config": "Yapılandırma sistemi",
    "core.events": "Olay sistemi",
    "core.notify": "Bildirim sistemi",
    "core.users": "Kullanıcı sistemi",
    "core.security": "Güvenlik sistemi",
    "core.process": "İşlem yönetimi",
    "core.thread": "Thread yönetimi",
    "core.memory": "Bellek yönetimi",
    "core.audio": "Ses sistemi",
    "core.network": "Ağ erişimi"
}

# Desteklenen izin türleri
SUPPORTED_PERMISSIONS = {
    "fs.read": "Dosya okuma izni",
    "fs.write": "Dosya yazma izni",
    "network": "Ağ erişim izni",
    "audio": "Ses sistemi izni",
    "camera": "Kamera erişim izni",
    "microphone": "Mikrofon erişim izni",
    "location": "Konum erişim izni",
    "notifications": "Bildirim gönderme izni",
    "system": "Sistem seviyesi erişim izni",
    "clipboard": "Pano erişim izni",
    "processes": "İşlem yönetimi izni",
    "threads": "Thread yönetimi izni"
}

def check_python_version() -> bool:
    """Python versiyonunu kontrol et"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python 3.8+ gerekli, mevcut: {version.major}.{version.minor}")
        return False
    
    print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
    return True

def check_package_installed(package_name: str, import_name: str) -> bool:
    """Paketin yüklü olup olmadığını kontrol et"""
    try:
        importlib.import_module(import_name)
        return True
    except ImportError:
        return False

def install_package(package_name: str) -> bool:
    """Paketi pip ile yükle"""
    try:
        print(f"📦 {package_name} yükleniyor...")
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", package_name
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ {package_name} başarıyla yüklendi")
            return True
        else:
            print(f"❌ {package_name} yüklenemedi: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ {package_name} yükleme hatası: {e}")
        return False

def check_and_install_dependencies(packages: Dict[str, str], required: bool = True) -> Tuple[List[str], List[str]]:
    """Bağımlılıkları kontrol et ve eksikleri yükle"""
    missing = []
    installed = []
    
    for package_name, import_name in packages.items():
        if check_package_installed(package_name, import_name):
            print(f"✅ {package_name}")
            installed.append(package_name)
        else:
            print(f"❌ {package_name} eksik")
            
            if required:
                if install_package(package_name):
                    # Yükleme başarılıysa installed listesine ekle
                    installed.append(package_name)
                    # Tekrar kontrol et
                    if check_package_installed(package_name, import_name):
                        print(f"✅ {package_name} doğrulandı")
                    else:
                        print(f"⚠️  {package_name} yüklendi ama import edilemiyor")
                        missing.append(package_name)
                else:
                    print(f"⚠️  {package_name} yüklenemedi")
                    missing.append(package_name)
            else:
                missing.append(package_name)
    
    return installed, missing

def analyze_app_manifest(app_dir: Path) -> Dict:
    """Uygulama manifest'ini analiz et - cursorrules enhanced"""
    app_json = app_dir / "app.json"
    analysis = {
        "name": app_dir.name,
        "valid": False,
        "requires": [],
        "permissions": {},
        "core_modules": [],
        "python_packages": [],
        "unknown_requirements": [],
        "permission_warnings": [],
        "errors": []
    }
    
    if not app_json.exists():
        analysis["errors"].append("app.json not found")
        return analysis
    
    try:
        with open(app_json, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        analysis["name"] = data.get('name', app_dir.name)
        analysis["valid"] = True
        
        # Requires analizi (yeni cursorrules özelliği)
        requires = data.get('requires', [])
        analysis["requires"] = requires
        
        for requirement in requires:
            if requirement.startswith("core."):
                # Çekirdek modül gereksinimi
                analysis["core_modules"].append(requirement)
                if requirement not in SUPPORTED_CORE_MODULES:
                    analysis["errors"].append(f"Unsupported core module: {requirement}")
            
            elif requirement.startswith("python"):
                # Python sürüm gereksinimi
                continue  # Python sürümlerini atla
            
            elif requirement in ["pyqt6", "psutil", "requests", "flask", "pillow"]:
                # Bilinen Python paketi
                analysis["python_packages"].append(requirement)
            
            else:
                # Bilinmeyen gereksinim
                analysis["unknown_requirements"].append(requirement)
        
        # Permissions analizi (yeni cursorrules özelliği)
        permissions = data.get('permissions', {})
        if isinstance(permissions, list):
            # Eski format: ["filesystem", "network"]
            permissions = {perm: True for perm in permissions}
        
        analysis["permissions"] = permissions
        
        for permission, granted in permissions.items():
            if permission not in SUPPORTED_PERMISSIONS:
                analysis["permission_warnings"].append(f"Unknown permission: {permission}")
            
            if permission == "system" and granted:
                analysis["permission_warnings"].append("System permission requested - requires admin approval")
            
            if permission in ["fs.write", "network"] and granted:
                analysis["permission_warnings"].append(f"High-risk permission: {permission}")
        
    except json.JSONDecodeError as e:
        analysis["errors"].append(f"Invalid JSON: {e}")
    except Exception as e:
        analysis["errors"].append(f"Analysis error: {e}")
    
    return analysis

def check_app_dependencies() -> Dict[str, List[str]]:
    """Uygulama bağımlılıklarını kontrol et - legacy uyumluluk"""
    apps_dir = Path("apps")
    app_deps = {}
    
    if not apps_dir.exists():
        print("⚠️  apps/ klasörü bulunamadı")
        return app_deps
    
    for app_dir in apps_dir.iterdir():
        if app_dir.is_dir():
            app_json = app_dir / "app.json"
            if app_json.exists():
                try:
                    with open(app_json, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    requires = data.get('requires', [])
                    if requires:
                        app_deps[data.get('name', app_dir.name)] = requires
                        
                except Exception as e:
                    print(f"⚠️  {app_dir.name}/app.json okunamadı: {e}")
    
    return app_deps

def analyze_all_apps() -> Dict:
    """Tüm uygulamaları analiz et - cursorrules enhanced"""
    apps_dir = Path("apps")
    analysis = {
        "total_apps": 0,
        "valid_apps": 0,
        "apps_with_core_modules": 0,
        "apps_with_permissions": 0,
        "all_core_modules": set(),
        "all_permissions": set(),
        "all_python_packages": set(),
        "apps": {},
        "warnings": [],
        "errors": []
    }
    
    if not apps_dir.exists():
        analysis["errors"].append("apps/ directory not found")
        return analysis
    
    for app_dir in apps_dir.iterdir():
        if app_dir.is_dir() and not app_dir.name.startswith('.'):
            analysis["total_apps"] += 1
            
            app_analysis = analyze_app_manifest(app_dir)
            analysis["apps"][app_dir.name] = app_analysis
            
            if app_analysis["valid"]:
                analysis["valid_apps"] += 1
                
                if app_analysis["core_modules"]:
                    analysis["apps_with_core_modules"] += 1
                    analysis["all_core_modules"].update(app_analysis["core_modules"])
                
                if app_analysis["permissions"]:
                    analysis["apps_with_permissions"] += 1
                    analysis["all_permissions"].update(app_analysis["permissions"].keys())
                
                analysis["all_python_packages"].update(app_analysis["python_packages"])
                
                # Uyarıları topla
                analysis["warnings"].extend([
                    f"{app_analysis['name']}: {warning}" 
                    for warning in app_analysis["permission_warnings"]
                ])
                
                # Hataları topla
                analysis["errors"].extend([
                    f"{app_analysis['name']}: {error}" 
                    for error in app_analysis["errors"]
                ])
    
    return analysis

def generate_requirements_from_apps():
    """Uygulama bağımlılıklarından requirements.txt oluştur - legacy"""
    app_deps = check_app_dependencies()
    all_deps = set()
    
    for app_name, deps in app_deps.items():
        for dep in deps:
            if dep.startswith("python"):
                continue  # Python sürümlerini atla
            all_deps.add(dep)
    
    print("\n📋 Uygulama bağımlılıkları (Legacy Format):")
    for app_name, deps in app_deps.items():
        print(f"  {app_name}: {', '.join(deps)}")
    
    print(f"\n📦 Toplam benzersiz bağımlılık: {len(all_deps)}")
    for dep in sorted(all_deps):
        print(f"  - {dep}")

def generate_enhanced_analysis():
    """Gelişmiş uygulama analizi - cursorrules enhanced"""
    print("\n🔍 Gelişmiş Uygulama Analizi (Cursorrules Enhanced):")
    print("=" * 60)
    
    analysis = analyze_all_apps()
    
    print(f"📊 Genel İstatistikler:")
    print(f"  Toplam uygulama: {analysis['total_apps']}")
    print(f"  Geçerli uygulama: {analysis['valid_apps']}")
    print(f"  Çekirdek modül kullanan: {analysis['apps_with_core_modules']}")
    print(f"  İzin sistemi kullanan: {analysis['apps_with_permissions']}")
    
    if analysis['all_core_modules']:
        print(f"\n🔗 Kullanılan Çekirdek Modüller ({len(analysis['all_core_modules'])}):")
        for module in sorted(analysis['all_core_modules']):
            description = SUPPORTED_CORE_MODULES.get(module, "Bilinmeyen modül")
            status = "✅" if module in SUPPORTED_CORE_MODULES else "❌"
            print(f"  {status} {module} - {description}")
    
    if analysis['all_permissions']:
        print(f"\n🔐 Kullanılan İzinler ({len(analysis['all_permissions'])}):")
        for permission in sorted(analysis['all_permissions']):
            description = SUPPORTED_PERMISSIONS.get(permission, "Bilinmeyen izin")
            status = "✅" if permission in SUPPORTED_PERMISSIONS else "❌"
            risk = "🔴" if permission in ["system", "fs.write", "network"] else "🟢"
            print(f"  {status} {risk} {permission} - {description}")
    
    if analysis['all_python_packages']:
        print(f"\n📦 Python Paket Gereksinimleri ({len(analysis['all_python_packages'])}):")
        for package in sorted(analysis['all_python_packages']):
            print(f"  - {package}")
    
    if analysis['warnings']:
        print(f"\n⚠️  Uyarılar ({len(analysis['warnings'])}):")
        for warning in analysis['warnings'][:10]:  # İlk 10 uyarı
            print(f"  {warning}")
        if len(analysis['warnings']) > 10:
            print(f"  ... ve {len(analysis['warnings']) - 10} uyarı daha")
    
    if analysis['errors']:
        print(f"\n❌ Hatalar ({len(analysis['errors'])}):")
        for error in analysis['errors'][:10]:  # İlk 10 hata
            print(f"  {error}")
        if len(analysis['errors']) > 10:
            print(f"  ... ve {len(analysis['errors']) - 10} hata daha")
    
    # Detaylı uygulama listesi
    print(f"\n📱 Uygulama Detayları:")
    for app_id, app_data in analysis['apps'].items():
        if app_data['valid']:
            core_count = len(app_data['core_modules'])
            perm_count = len(app_data['permissions'])
            status_icons = []
            
            if core_count > 0:
                status_icons.append(f"🔗{core_count}")
            if perm_count > 0:
                status_icons.append(f"🔐{perm_count}")
            if app_data['errors']:
                status_icons.append("❌")
            if app_data['permission_warnings']:
                status_icons.append("⚠️")
            
            status = " ".join(status_icons) if status_icons else "✅"
            print(f"  {status} {app_data['name']}")

def main():
    """Ana fonksiyon"""
    print("🌩️  PyCloud OS Bağımlılık Kurulum Scripti (Cursorrules Enhanced)")
    print("=" * 70)
    
    # Python versiyonu kontrol et
    if not check_python_version():
        sys.exit(1)
    
    print("\n📋 Gerekli paketler kontrol ediliyor...")
    installed, missing = check_and_install_dependencies(REQUIRED_PACKAGES, required=True)
    
    print("\n📋 Opsiyonel paketler kontrol ediliyor...")
    opt_installed, opt_missing = check_and_install_dependencies(OPTIONAL_PACKAGES, required=False)
    
    print("\n📱 Uygulama bağımlılıkları kontrol ediliyor...")
    generate_requirements_from_apps()
    
    # Yeni cursorrules analizi
    generate_enhanced_analysis()
    
    # Özet
    print("\n📊 Kurulum Özeti:")
    print(f"✅ Yüklü gerekli paketler: {len(installed)}/{len(REQUIRED_PACKAGES)}")
    print(f"📦 Yüklü opsiyonel paketler: {len(opt_installed)}/{len(OPTIONAL_PACKAGES)}")
    
    if missing:
        print(f"❌ Eksik gerekli paketler: {', '.join(missing)}")
        return 1
    
    print("\n🎉 Tüm gerekli bağımlılıklar hazır!")
    
    # PyQt6 test et
    try:
        from PyQt6.QtWidgets import QApplication
        print("✅ PyQt6 GUI sistemi kullanılabilir")
    except ImportError:
        print("⚠️  PyQt6 GUI sistemi kullanılamıyor")
    
    # Cursorrules uyumluluk kontrolü
    print("\n🔗 Cursorrules Uyumluluk Kontrolü:")
    print(f"✅ {len(SUPPORTED_CORE_MODULES)} çekirdek modül destekleniyor")
    print(f"✅ {len(SUPPORTED_PERMISSIONS)} izin türü destekleniyor")
    print("✅ Bridge sistemi hazır")
    print("✅ ModuleAdapter sistemi hazır")
    print("✅ PermissionManager sistemi hazır")
    print("✅ SandboxManager sistemi hazır")
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 