#!/usr/bin/env python3
"""
update_command.py - clapp Update Command

Bu modül kullanıcıların yüklü uygulamalarını güncellemelerini sağlar.
"""

import os
import json
import shutil
import tempfile
import urllib.request
import zipfile
from typing import Tuple, Optional, Dict, Any
from progress_utils import download_with_progress, extract_with_progress, show_success_message, show_error_message, show_info_message, show_warning_message

def load_index() -> Tuple[bool, Dict[str, Any], str]:
    """
    GitHub'dan index.json'u yükler
    
    Returns:
        (success, index_data, error_message)
    """
    try:
        index_url = "https://raw.githubusercontent.com/mburakmmm/clapp-packages/main/index.json"
        show_info_message("🔄 GitHub'dan index.json indiriliyor...")
        
        with urllib.request.urlopen(index_url) as response:
            index_data = json.loads(response.read().decode('utf-8'))
        
        return True, index_data, ""
    except Exception as e:
        return False, {}, f"Index yükleme hatası: {e}"

def get_installed_apps() -> Dict[str, Dict[str, Any]]:
    """
    Yerel olarak yüklü uygulamaları listeler
    
    Returns:
        Dict[app_name, app_info]
    """
    installed_apps = {}
    apps_dir = os.path.expanduser("~/.clapp/apps")
    
    if not os.path.exists(apps_dir):
        return installed_apps
    
    for app_name in os.listdir(apps_dir):
        app_path = os.path.join(apps_dir, app_name)
        if os.path.isdir(app_path):
            manifest_path = os.path.join(app_path, "manifest.json")
            if os.path.exists(manifest_path):
                try:
                    with open(manifest_path, 'r', encoding='utf-8') as f:
                        manifest = json.load(f)
                    installed_apps[app_name] = {
                        'version': manifest.get('version', 'unknown'),
                        'path': app_path,
                        'manifest': manifest
                    }
                except:
                    continue
    
    return installed_apps

def check_for_updates(app_name: str, current_version: str, index_data: Dict[str, Any]) -> Optional[str]:
    """
    Uygulama için güncelleme kontrol eder
    
    Args:
        app_name: Uygulama adı
        current_version: Mevcut sürüm
        index_data: Index verisi
        
    Returns:
        En son sürüm (güncelleme varsa) veya None
    """
    if app_name not in index_data:
        return None
    
    app_versions = index_data[app_name]
    
    # En son sürümü bul
    latest_version = None
    for version in app_versions.keys():
        if latest_version is None or version > latest_version:
            latest_version = version
    
    if latest_version and latest_version > current_version:
        return latest_version
    
    return None

def download_and_install_update(app_name: str, version: str, index_data: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Uygulama güncellemesini indirir ve yükler
    
    Args:
        app_name: Uygulama adı
        version: Yüklenecek sürüm
        index_data: Index verisi
        
    Returns:
        (success, message)
    """
    try:
        app_info = index_data[app_name][version]
        repo_url = app_info['repo_url']
        subdir = app_info['subdir']
        
        # GitHub'dan zip dosyasını indir
        zip_url = f"{repo_url}/archive/refs/heads/main.zip"
        show_info_message(f"📦 {app_name} v{version} indiriliyor...")
        
        with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as temp_file:
            temp_zip_path = temp_file.name
        
        # İndirme işlemi
        download_with_progress(zip_url, temp_zip_path, f"📦 {app_name} indiriliyor")
        
        # Geçici dizin oluştur
        with tempfile.TemporaryDirectory() as temp_dir:
            # Zip dosyasını çıkar
            extract_with_progress(temp_zip_path, temp_dir, f"📦 {app_name} çıkarılıyor")
            
            # Uygulama dizinini bul
            extracted_dir = os.path.join(temp_dir, "clapp-packages-main", subdir)
            if not os.path.exists(extracted_dir):
                return False, f"Uygulama dizini bulunamadı: {subdir}"
            
            # Yüklü uygulamayı yedekle
            apps_dir = os.path.expanduser("~/.clapp/apps")
            app_path = os.path.join(apps_dir, app_name)
            backup_path = os.path.join(apps_dir, f"{app_name}_backup")
            
            if os.path.exists(app_path):
                if os.path.exists(backup_path):
                    shutil.rmtree(backup_path)
                shutil.move(app_path, backup_path)
            
            # Yeni sürümü yükle
            shutil.copytree(extracted_dir, app_path)
            
            # Eski yedekleri temizle
            if os.path.exists(backup_path):
                shutil.rmtree(backup_path)
        
        # Geçici zip dosyasını sil
        os.unlink(temp_zip_path)
        
        return True, f"{app_name} v{version} başarıyla güncellendi!"
        
    except Exception as e:
        return False, f"Güncelleme hatası: {e}"

def update_app(app_name: str) -> Tuple[bool, str]:
    """
    Belirtilen uygulamayı günceller
    
    Args:
        app_name: Güncellenecek uygulama adı
        
    Returns:
        (success, message)
    """
    # Yüklü uygulamaları kontrol et
    installed_apps = get_installed_apps()
    if app_name not in installed_apps:
        return False, f"'{app_name}' yüklü değil"
    
    current_version = installed_apps[app_name]['version']
    show_info_message(f"🔍 {app_name} (v{current_version}) güncellemeleri kontrol ediliyor...")
    
    # Index'i yükle
    success, index_data, error = load_index()
    if not success:
        return False, error
    
    # Güncelleme kontrol et
    latest_version = check_for_updates(app_name, current_version, index_data)
    if not latest_version:
        return True, f"{app_name} zaten en son sürümde (v{current_version})"
    
    show_info_message(f"🔄 {app_name} v{current_version} → v{latest_version} güncelleniyor...")
    
    # Güncellemeyi indir ve yükle
    success, message = download_and_install_update(app_name, latest_version, index_data)
    if success:
        show_success_message(message)
    else:
        show_error_message(message)
    
    return success, message

def update_all_apps() -> Tuple[bool, str]:
    """
    Tüm yüklü uygulamaları günceller
    
    Returns:
        (success, message)
    """
    installed_apps = get_installed_apps()
    if not installed_apps:
        return True, "Yüklü uygulama bulunamadı"
    
    show_info_message(f"🔍 {len(installed_apps)} uygulama için güncellemeler kontrol ediliyor...")
    
    # Index'i yükle
    success, index_data, error = load_index()
    if not success:
        return False, error
    
    updated_count = 0
    errors = []
    
    for app_name in installed_apps.keys():
        current_version = installed_apps[app_name]['version']
        latest_version = check_for_updates(app_name, current_version, index_data)
        
        if latest_version:
            show_info_message(f"🔄 {app_name} v{current_version} → v{latest_version} güncelleniyor...")
            success, message = download_and_install_update(app_name, latest_version, index_data)
            if success:
                updated_count += 1
                show_success_message(f"✅ {app_name} güncellendi")
            else:
                errors.append(f"{app_name}: {message}")
        else:
            show_info_message(f"✅ {app_name} zaten güncel (v{current_version})")
    
    # Sonuç raporu
    if updated_count > 0:
        message = f"✅ {updated_count} uygulama güncellendi"
        if errors:
            message += f"\n❌ Hatalar: {', '.join(errors)}"
        return True, message
    else:
        return True, "Tüm uygulamalar zaten güncel"

def handle_update_command(args):
    """
    Update komutunu işler
    
    Args:
        args: Argparse arguments
    """
    if args.app:
        # Belirli uygulamayı güncelle
        success, message = update_app(args.app)
        if not success:
            show_error_message(message)
            return False
    else:
        # Tüm uygulamaları güncelle
        success, message = update_all_apps()
        if not success:
            show_error_message(message)
            return False
    
    return True 