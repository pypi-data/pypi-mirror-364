import os
import zipfile
import urllib.request
import tempfile
import shutil
import json
from manifest_validator import validate_manifest_verbose
from package_registry import app_exists
from progress_utils import download_with_progress, extract_with_progress, copy_with_progress, show_success_message, show_error_message

def find_app_folder(extract_path, app_name):
    """
    Zip çıkarıldıktan sonra, extract_path altında **/packages/{app_name} klasörünü bulur.
    """
    for root, dirs, files in os.walk(extract_path):
        if os.path.basename(root) == app_name and os.path.basename(os.path.dirname(root)) == "packages":
            return root
    return None


def install_package(source, force=False):
    """
    Bir .clapp paketini zip dosyasından veya URL'den yükler.
    """
    temp_dir = None
    try:
        temp_dir = tempfile.mkdtemp()
        if source.startswith(('http://', 'https://')):
            zip_path = download_package(source, temp_dir)
            if not zip_path:
                return False, "Paket indirilemedi"
        else:
            if not os.path.exists(source):
                return False, f"Dosya bulunamadı: {source}"
            zip_path = source
        extract_path = os.path.join(temp_dir, "extracted")
        success, message = extract_package(zip_path, extract_path)
        if not success:
            return False, message

        # --- YENİ: Doğru app klasörünü bul ---
        # Önce manifesti bulmak için tüm app klasörlerini tara
        app_folder = None
        manifest = None
        manifest_path = None
        # Tüm packages altındaki app klasörlerini bul
        for root, dirs, files in os.walk(extract_path):
            if "manifest.json" in files:
                with open(os.path.join(root, "manifest.json"), 'r', encoding='utf-8') as f:
                    try:
                        m = json.load(f)
                        if 'name' in m:
                            app_folder = root
                            manifest = m
                            manifest_path = os.path.join(root, "manifest.json")
                            break
                    except Exception:
                        continue
        if not app_folder or not manifest:
            return False, "Uygulama klasörü bulunamadı: manifest.json"
        app_name = manifest['name']

        # --- YENİ: Sadece packages/{app_name} klasörünü bul ve kopyala ---
        app_real_folder = find_app_folder(extract_path, app_name)
        if not app_real_folder:
            return False, f"Uygulama klasörü bulunamadı: packages/{app_name}"

        # Manifesti doğrula
        is_valid, errors = validate_manifest_file(os.path.join(app_real_folder, "manifest.json"))
        if not is_valid:
            error_msg = "Manifest doğrulama hatası:\n" + "\n".join(errors)
            return False, error_msg

        # Giriş dosyasının varlığını kontrol et
        entry_file = manifest['entry']
        entry_path = os.path.join(app_real_folder, entry_file)
        if not os.path.exists(entry_path):
            return False, f"Giriş dosyası bulunamadı: {entry_file}"

        # Hedef dizini oluştur
        target_dir = os.path.join("apps", app_name)
        if os.path.exists(target_dir):
            shutil.rmtree(target_dir)
        shutil.copytree(app_real_folder, target_dir)
        
        show_success_message(f"'{app_name}' başarıyla yüklendi!")
        return True, f"✅ '{app_name}' başarıyla yüklendi!"
    except Exception as e:
        return False, f"Yükleme hatası: {e}"
    finally:
        if temp_dir and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)

def download_package(url, temp_dir):
    """
    Paketi URL'den indirir.
    
    Args:
        url (str): İndirilecek URL
        temp_dir (str): Geçici dizin
        
    Returns:
        str or None: İndirilen dosyanın yolu veya None
    """
    try:
        # Dosya adını URL'den çıkar
        filename = os.path.basename(url)
        if not filename.endswith('.zip'):
            filename += '.zip'
        
        zip_path = os.path.join(temp_dir, filename)
        
        # Progress bar ile indir
        success = download_with_progress(url, zip_path, f"📦 {filename} indiriliyor")
        
        if success:
            return zip_path
        else:
            return None
        
    except Exception as e:
        show_error_message(f"İndirme hatası: {e}")
        return None

def extract_package(zip_path, extract_path):
    """
    Zip dosyasını çıkarır.
    
    Args:
        zip_path (str): Zip dosyasının yolu
        extract_path (str): Çıkarılacak dizin
        
    Returns:
        tuple: (success: bool, message: str)
    """
    try:
        # Çıkarma dizinini oluştur
        os.makedirs(extract_path, exist_ok=True)
        
        # Progress bar ile çıkar
        filename = os.path.basename(zip_path)
        success = extract_with_progress(zip_path, extract_path, f"📦 {filename} çıkarılıyor")
        
        if success:
            return True, "Paket başarıyla çıkarıldı"
        else:
            return False, "Çıkarma hatası"
        
    except zipfile.BadZipFile:
        return False, "Geçersiz zip dosyası"
    except Exception as e:
        return False, f"Çıkarma hatası: {e}"

def validate_manifest_file(manifest_path):
    """
    Manifest dosyasını doğrular.
    
    Args:
        manifest_path (str): Manifest dosyasının yolu
        
    Returns:
        tuple: (is_valid: bool, errors: list)
    """
    if not os.path.exists(manifest_path):
        return False, ["Manifest dosyası bulunamadı"]
    
    try:
        with open(manifest_path, 'r', encoding='utf-8') as f:
            manifest = json.load(f)
        
        return validate_manifest_verbose(manifest)
        
    except json.JSONDecodeError as e:
        return False, [f"JSON formatı hatalı: {e}"]
    except Exception as e:
        return False, [f"Dosya okuma hatası: {e}"]

def create_package_from_directory(source_dir, output_path=None):
    """
    Dizinden .clapp paketi oluşturur.
    
    Args:
        source_dir (str): Kaynak dizin
        output_path (str): Çıktı dosyası yolu (opsiyonel)
        
    Returns:
        tuple: (success: bool, message: str, output_file: str)
    """
    try:
        # Manifest dosyasını kontrol et
        manifest_path = os.path.join(source_dir, "manifest.json")
        is_valid, errors = validate_manifest_file(manifest_path)
        
        if not is_valid:
            error_msg = "Manifest doğrulama hatası:\n" + "\n".join(errors)
            return False, error_msg, None
        
        # Manifest'i yükle
        with open(manifest_path, 'r', encoding='utf-8') as f:
            manifest = json.load(f)
        
        app_name = manifest['name']
        
        # Çıktı dosyası yolunu belirle
        if not output_path:
            output_path = f"{app_name}.clapp.zip"
        
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
            rel_path = os.path.relpath(path, source_dir)
            
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
        
        # Zip dosyasını oluştur
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zip_ref:
            for root, dirs, files in os.walk(source_dir):
                # Dizinleri filtrele
                dirs[:] = [d for d in dirs if not should_exclude(os.path.join(root, d))]
                
                for file in files:
                    file_path = os.path.join(root, file)
                    
                    # Dosyayı hariç tut
                    if should_exclude(file_path):
                        continue
                    
                    arc_path = os.path.relpath(file_path, source_dir)
                    zip_ref.write(file_path, arc_path)
        
        return True, f"✅ Paket oluşturuldu: {output_path}", output_path
        
    except Exception as e:
        return False, f"Paket oluşturma hatası: {e}", None

def install_from_directory(source_dir, force=False):
    """
    Dizinden doğrudan uygulama yükler.
    
    Args:
        source_dir (str): Kaynak dizin
        force (bool): Mevcut uygulamanın üzerine yazılmasına izin ver
        
    Returns:
        tuple: (success: bool, message: str)
    """
    try:
        # Manifest dosyasını kontrol et
        manifest_path = os.path.join(source_dir, "manifest.json")
        is_valid, errors = validate_manifest_file(manifest_path)
        
        if not is_valid:
            error_msg = "Manifest doğrulama hatası:\n" + "\n".join(errors)
            return False, error_msg
        
        # Manifest'i yükle
        with open(manifest_path, 'r', encoding='utf-8') as f:
            manifest = json.load(f)
        
        app_name = manifest['name']
        
        # Uygulama zaten var mı kontrol et
        if app_exists(app_name) and not force:
            return False, f"Uygulama '{app_name}' zaten yüklü. --force kullanarak üzerine yazabilirsiniz."
        
        # Giriş dosyasının varlığını kontrol et
        entry_file = manifest['entry']
        entry_path = os.path.join(source_dir, entry_file)
        if not os.path.exists(entry_path):
            return False, f"Giriş dosyası bulunamadı: {entry_file}"
        
        # Hedef dizini oluştur
        target_dir = os.path.join("apps", app_name)
        
        # Mevcut dizini sil (eğer varsa)
        if os.path.exists(target_dir):
            shutil.rmtree(target_dir)
        
        # Dosyaları kopyala
        shutil.copytree(source_dir, target_dir)
        
        show_success_message(f"'{app_name}' başarıyla yüklendi!")
        return True, f"✅ '{app_name}' başarıyla yüklendi!"
        
    except Exception as e:
        return False, f"Yükleme hatası: {e}"

def uninstall_package(app_name):
    """
    Uygulamayı kaldırır.
    
    Args:
        app_name (str): Kaldırılacak uygulama adı
        
    Returns:
        tuple: (success: bool, message: str)
    """
    try:
        if not app_exists(app_name):
            return False, f"Uygulama '{app_name}' bulunamadı"
        
        # Uygulama dizinini sil
        app_dir = os.path.join("apps", app_name)
        shutil.rmtree(app_dir)
        
        return True, f"✅ '{app_name}' başarıyla kaldırıldı!"
        
    except Exception as e:
        return False, f"Kaldırma hatası: {e}"

def list_installable_files(directory="."):
    """
    Dizindeki yüklenebilir .clapp dosyalarını listeler.
    
    Args:
        directory (str): Aranacak dizin
        
    Returns:
        list: .clapp dosyalarının listesi
    """
    clapp_files = []
    
    for file in os.listdir(directory):
        if file.endswith('.clapp.zip') or file.endswith('.zip'):
            file_path = os.path.join(directory, file)
            clapp_files.append(file_path)
    
    return clapp_files

if __name__ == "__main__":
    # Test için örnek kullanım
    print("clapp Installer Test")
    print("=" * 30)
    
    # Mevcut dizindeki .clapp dosyalarını listele
    installable = list_installable_files()
    if installable:
        print("Yüklenebilir dosyalar:")
        for file in installable:
            print(f"  - {file}")
    else:
        print("Yüklenebilir dosya bulunamadı")
    
    print("\nTest tamamlandı.") 