#!/usr/bin/env python3
"""
publish_command.py - clapp Publish Command

Bu modül 'clapp publish <folder>' komutunu uygular.
Bir uygulama klasörünü validate edip packages/ klasörüne kopyalar
ve index.json'u günceller. Opsiyonel olarak clapp-packages reposuna push eder.
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Tuple, Optional

from manifest_validator import validate_manifest_verbose
from manifest_schema import load_manifest

def validate_app_folder(folder_path: str) -> Tuple[bool, str, Optional[dict]]:
    """
    Uygulama klasörünü doğrular
    
    Returns:
        (success, message, manifest_data)
    """
    if not os.path.exists(folder_path):
        return False, f"Klasör bulunamadı: {folder_path}", None
    
    if not os.path.isdir(folder_path):
        return False, f"Geçerli bir klasör değil: {folder_path}", None
    
    # manifest.json kontrolü
    manifest_path = os.path.join(folder_path, "manifest.json")
    if not os.path.exists(manifest_path):
        return False, "manifest.json dosyası bulunamadı", None
    
    try:
        manifest = load_manifest(manifest_path)
    except Exception as e:
        return False, f"manifest.json okunamadı: {e}", None
    
    # Manifest doğrulama
    is_valid, errors = validate_manifest_verbose(manifest)
    if not is_valid:
        error_msg = "Manifest doğrulama hatası:\n" + "\n".join(f"  - {error}" for error in errors)
        return False, error_msg, None
    
    # Entry file kontrolü
    entry_file = manifest.get('entry')
    if entry_file:
        entry_path = os.path.join(folder_path, entry_file)
        if not os.path.exists(entry_path):
            return False, f"Entry dosyası bulunamadı: {entry_file}", None
    
    return True, "Doğrulama başarılı", manifest

def copy_app_to_packages(source_folder: str, app_name: str) -> Tuple[bool, str]:
    """
    Uygulama klasörünü ana clapp dizinindeki packages/ altına kopyalar
    
    Returns:
        (success, message)
    """
    try:
        # Ana clapp dizinini bul
        clapp_root, _ = find_clapp_root_with_build_index()
        if not clapp_root:
            return False, "Ana clapp dizini bulunamadı"
        
        packages_dir = os.path.join(clapp_root, "packages")
        target_path = os.path.join(packages_dir, app_name)
        
        # packages klasörünü oluştur
        os.makedirs(packages_dir, exist_ok=True)
        
        # Eğer hedef klasör varsa, sil
        if os.path.exists(target_path):
            shutil.rmtree(target_path)
            print(f"⚠️  Mevcut {app_name} klasörü silindi")
        
        # Hariç tutulacak dosya ve klasörler
        exclude_patterns = [
            '.venv', '__pycache__', '.git', '.gitignore', '.DS_Store',
            '*.pyc', '*.pyo', '*.pyd', '*.so', '*.dll', '*.dylib',
            'node_modules', '.npm', '.yarn', 'yarn.lock', 'package-lock.json',
            '*.log', '*.tmp', '*.temp', '.vscode', '.idea', '*.swp', '*.swo',
            'Thumbs.db', 'desktop.ini', '.Trashes', '.Spotlight-V100',
            'packages'  # packages klasörünü de hariç tut
        ]
        
        def should_exclude(path):
            """Dosya/klasörün hariç tutulup tutulmayacağını kontrol eder"""
            basename = os.path.basename(path)
            rel_path = os.path.relpath(path, source_folder)
            
            for pattern in exclude_patterns:
                if pattern.startswith('*'):
                    # *.ext formatındaki pattern'ler
                    if basename.endswith(pattern[1:]):
                        return True
                else:
                    # Tam eşleşme
                    if basename == pattern or rel_path == pattern:
                        return True
            return False
        
        # Önce hedef klasörü oluştur
        os.makedirs(target_path, exist_ok=True)
        
        # Dosyaları tek tek kopyala (hariç tutma ile)
        for root, dirs, files in os.walk(source_folder):
            # Dizinleri filtrele
            dirs[:] = [d for d in dirs if not should_exclude(os.path.join(root, d))]
            
            # Hedef dizini oluştur
            rel_root = os.path.relpath(root, source_folder)
            target_root = os.path.join(target_path, rel_root)
            os.makedirs(target_root, exist_ok=True)
            
            # Dosyaları kopyala
            for file in files:
                source_file = os.path.join(root, file)
                
                # Dosyayı hariç tut
                if should_exclude(source_file):
                    continue
                
                target_file = os.path.join(target_root, file)
                shutil.copy2(source_file, target_file)
        
        print(f"✅ {app_name} -> packages/{app_name} kopyalandı")
        
        return True, f"Uygulama başarıyla kopyalandı: packages/{app_name}"
        
    except Exception as e:
        return False, f"Kopyalama hatası: {e}"

def find_clapp_root_with_build_index():
    """
    Ana clapp dizinini ve build_index.py'yi bulur.
    1. which clapp konumundan arama
    2. pyenv which clapp konumundan arama
    3. Kesin konum kontrolü
    4. Fallback olarak mevcut çalışma dizininden arama
    Returns: (clapp_root, build_index_path) veya (None, None)
    """
    import os
    import subprocess
    
    # Debug bilgisi
    print(f"🔍 Mevcut çalışma dizini: {os.getcwd()}")
    print(f"🔍 publish_command.py konumu: {os.path.dirname(os.path.abspath(__file__))}")
    
    # 1. which clapp konumundan arama
    try:
        result = subprocess.run(['which', 'clapp'], capture_output=True, text=True)
        if result.returncode == 0:
            clapp_path = result.stdout.strip()
            print(f"🔍 1. which clapp sonucu: {clapp_path}")
            
            # clapp komutunun bulunduğu dizinden başlayarak yukarı çık
            clapp_dir = os.path.dirname(clapp_path)
            search_dir = clapp_dir
            
            print(f"🔍 1. Arama: {clapp_dir} dizininden başlıyor...")
            while search_dir != os.path.dirname(search_dir):  # Root'a ulaşana kadar
                build_index_path = os.path.join(search_dir, "build_index.py")
                print(f"   Kontrol ediliyor: {build_index_path}")
                if os.path.exists(build_index_path):
                    print(f"✅ build_index.py which clapp yanında bulundu: {build_index_path}")
                    return search_dir, build_index_path
                search_dir = os.path.dirname(search_dir)
    except Exception as e:
        print(f"⚠️  which clapp hatası: {e}")
    
    # 2. pyenv which clapp konumundan arama
    try:
        result = subprocess.run(['pyenv', 'which', 'clapp'], capture_output=True, text=True)
        if result.returncode == 0:
            clapp_path = result.stdout.strip()
            print(f"🔍 2. pyenv which clapp sonucu: {clapp_path}")
            
            # clapp komutunun bulunduğu dizinden başlayarak yukarı çık
            clapp_dir = os.path.dirname(clapp_path)
            search_dir = clapp_dir
            
            print(f"🔍 2. Arama: {clapp_dir} dizininden başlıyor...")
            while search_dir != os.path.dirname(search_dir):  # Root'a ulaşana kadar
                build_index_path = os.path.join(search_dir, "build_index.py")
                print(f"   Kontrol ediliyor: {build_index_path}")
                if os.path.exists(build_index_path):
                    print(f"✅ build_index.py pyenv which clapp yanında bulundu: {build_index_path}")
                    return search_dir, build_index_path
                search_dir = os.path.dirname(search_dir)
    except Exception as e:
        print(f"⚠️  pyenv which clapp hatası: {e}")
    
    # 3. Kesin konum kontrolü
    clapp_home = "/Users/melihburakmemis/Desktop/clapp"
    build_index_path = os.path.join(clapp_home, "build_index.py")
    print(f"🔍 3. Kesin konum kontrolü: {build_index_path}")
    if os.path.exists(build_index_path):
        print(f"✅ build_index.py kesin konumda bulundu: {build_index_path}")
        return clapp_home, build_index_path
    
    # 4. Fallback: Mevcut çalışma dizininden başlayarak yukarı çık
    search_dir = os.getcwd()
    print(f"🔍 4. Fallback arama: {search_dir} dizininden başlıyor...")
    while search_dir != os.path.dirname(search_dir):  # Root'a ulaşana kadar
        build_index_path = os.path.join(search_dir, "build_index.py")
        print(f"   Kontrol ediliyor: {build_index_path}")
        if os.path.exists(build_index_path):
            print(f"✅ build_index.py bulundu: {build_index_path}")
            return search_dir, build_index_path
        search_dir = os.path.dirname(search_dir)
    
    print("❌ build_index.py hiçbir yerde bulunamadı!")
    return None, None


def update_index() -> Tuple[bool, str]:
    """
    build_index.py script'ini çalıştırarak index.json'u günceller
    Returns: (success, message)
    """
    try:
        clapp_root, build_index_path = find_clapp_root_with_build_index()
        if not clapp_root or not build_index_path:
            return False, "Ana clapp dizini veya build_index.py bulunamadı. Lütfen komutu ana dizinden veya bir alt klasörden çalıştırın."
        
        # build_index.py'yi ana dizinde çalıştır
        result = subprocess.run([
            sys.executable, build_index_path
        ], cwd=clapp_root)
        if result.returncode == 0:
            return True, "Index başarıyla güncellendi"
        else:
            return False, f"Index güncelleme hatası: Çalıştırılan dizin: {clapp_root}"
    except Exception as e:
        return False, f"Index script çalıştırılamadı: {e}"

def push_to_clapp_packages_repo(app_name: str, app_version: str) -> Tuple[bool, str]:
    """
    Değişiklikleri clapp-packages reposuna push eder
    
    Returns:
        (success, message)
    """
    try:
        print("4️⃣ clapp-packages reposuna push ediliyor...")
        
        # clapp-packages reposunu kontrol et
        packages_repo_path = "./clapp-packages-repo"
        
        # Eğer clapp-packages repo klonlanmamışsa, klonla
        if not os.path.exists(packages_repo_path):
            print("📥 clapp-packages reposu klonlanıyor...")
            subprocess.run([
                'git', 'clone', 'https://github.com/mburakmmm/clapp-packages.git', 
                packages_repo_path
            ], check=True, cwd=".")
        
        # Ana clapp dizinindeki packages klasöründen uygulamayı kopyala
        clapp_root, _ = find_clapp_root_with_build_index()
        if not clapp_root:
            return False, "Ana clapp dizini bulunamadı"
        
        source_app = os.path.join(clapp_root, "packages", app_name)
        target_app = os.path.join(packages_repo_path, "packages", app_name)
        
        # Hedef packages klasörünü oluştur (yoksa)
        target_packages = os.path.join(packages_repo_path, "packages")
        os.makedirs(target_packages, exist_ok=True)
        
        # Eğer hedef uygulama klasörü varsa, sil
        if os.path.exists(target_app):
            shutil.rmtree(target_app)
        
        # Uygulamayı kopyala
        shutil.copytree(source_app, target_app)
        print(f"✅ {app_name} uygulaması clapp-packages reposuna kopyalandı")
        
        # Ana clapp dizinindeki index.json'u kopyala
        clapp_root, _ = find_clapp_root_with_build_index()
        if clapp_root:
            source_index = os.path.join(clapp_root, "index.json")
            if os.path.exists(source_index):
                shutil.copy(source_index, os.path.join(packages_repo_path, "index.json"))
                print("✅ index.json clapp-packages reposuna kopyalandı")
            else:
                print("⚠️  Ana clapp dizininde index.json bulunamadı")
        else:
            print("⚠️  Ana clapp dizini bulunamadı, index.json kopyalanamadı")
        
        # clapp-packages reposuna git işlemleri
        os.chdir(packages_repo_path)
        
        # Git durumunu kontrol et
        result = subprocess.run(['git', 'status', '--porcelain'], 
                              capture_output=True, text=True)
        
        # Working tree'de değişiklik var mı kontrol et
        if result.stdout.strip():
            # Değişiklik var, add ve commit yap
            print("📦 Değişiklikler commit ediliyor...")
            subprocess.run(['git', 'add', '.'], check=True)
            
            # Commit oluştur
            commit_message = f"📦 Publish {app_name} v{app_version}\n\n- {app_name} uygulaması packages/ klasörüne eklendi\n- index.json güncellendi\n- Otomatik publish işlemi"
            subprocess.run(['git', 'commit', '-m', commit_message], check=True)
        else:
            # Working tree temiz, sadece push yapılıyor...
            print("📦 Working tree temiz, sadece push yapılıyor...")
        
        # Push et
        try:
            # Önce pull yap
            print("📥 Remote değişiklikleri çekiliyor...")
            subprocess.run(['git', 'pull', 'origin', 'main'], check=True)
        except subprocess.CalledProcessError:
            print("⚠️  Pull başarısız, force push yapılıyor...")
            subprocess.run(['git', 'push', 'origin', 'main', '--force'], check=True)
        else:
            # Normal push
            subprocess.run(['git', 'push', 'origin', 'main'], check=True)
        
        # Ana dizine geri dön
        os.chdir("..")
        
        return True, "clapp-packages reposuna başarıyla push edildi"
        
    except subprocess.CalledProcessError as e:
        # Ana dizine geri dön
        if os.getcwd() != os.path.abspath("."):
            os.chdir("..")
        return False, f"Git işlemi hatası: {e}"
    except Exception as e:
        # Ana dizine geri dön
        if os.getcwd() != os.path.abspath("."):
            os.chdir("..")
        return False, f"Push hatası: {e}"

def publish_app(folder_path: str, force: bool = False, push_to_github: bool = False) -> Tuple[bool, str]:
    """
    Ana publish fonksiyonu
    
    Args:
        folder_path: Publish edilecek uygulama klasörü
        force: Zorla üzerine yaz
        push_to_github: clapp-packages reposuna push et
        
    Returns:
        (success, message)
    """
    print(f"🚀 Publish başlatılıyor: {folder_path}")
    print("=" * 50)
    
    # 1. Klasörü doğrula
    print("1️⃣ Uygulama doğrulanıyor...")
    is_valid, message, manifest = validate_app_folder(folder_path)
    
    if not is_valid:
        return False, f"Doğrulama hatası: {message}"
    
    app_name = manifest['name']
    app_version = manifest['version']
    print(f"✅ {app_name} v{app_version} doğrulandı")
    
    # 2. Uygulamayı packages klasörüne kopyala
    print("2️⃣ Uygulama kopyalanıyor...")
    success, message = copy_app_to_packages(folder_path, app_name)
    if not success:
        return False, message
    
    # 3. Index güncelle
    print("3️⃣ Index güncelleniyor...")
    success, message = update_index()
    if not success:
        return False, message
    
    # 4. Eğer push isteniyorsa, clapp-packages reposuna push et
    if push_to_github:
        success, message = push_to_clapp_packages_repo(app_name, app_version)
        if not success:
            return False, message
    
    return True, f"🎉 '{app_name}' başarıyla publish edildi! Index güncellendi."

def main():
    """CLI entry point"""
    if len(sys.argv) < 2:
        print("Kullanım: python publish_command.py <folder_path> [--push]")
        print("Örnek: python publish_command.py ./my-app")
        print("Örnek: python publish_command.py ./my-app --push")
        sys.exit(1)
    
    folder_path = sys.argv[1]
    force = "--force" in sys.argv
    push_to_github = "--push" in sys.argv
    
    success, message = publish_app(folder_path, force, push_to_github)
    
    print("\n" + "=" * 50)
    if success:
        print(f"✅ {message}")
        sys.exit(0)
    else:
        print(f"❌ {message}")
        sys.exit(1)

if __name__ == "__main__":
    main() 