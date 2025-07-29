#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cloud Sync - Cloud senkronizasyon modülü
Dosyaları cloud servisleri ile senkronize etme
"""

import os
import json
import hashlib
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import threading
import time

from PyQt6.QtCore import QObject, pyqtSignal, QThread, QTimer
from PyQt6.QtWidgets import QMessageBox


class CloudSync(QObject):
    """Cloud senkronizasyon sınıfı"""
    
    sync_started = pyqtSignal()
    sync_finished = pyqtSignal(bool, str)  # success, message
    file_synced = pyqtSignal(str)  # file_path
    sync_progress = pyqtSignal(int)  # progress percentage
    
    def __init__(self):
        super().__init__()
        self.sync_folder = ""
        self.sync_enabled = False
        self.sync_interval = 30  # dakika
        self.sync_timer = QTimer()
        self.sync_timer.timeout.connect(self.auto_sync)
        self.sync_thread = None
        self.is_syncing = False
        
        # Dosya hash'leri
        self.file_hashes = {}
        self.hash_file = "file_hashes.json"
        
    def setup_sync(self, folder_path: str, interval: int = 30):
        """Senkronizasyon ayarla"""
        self.sync_folder = folder_path
        self.sync_interval = interval
        
        if folder_path and os.path.exists(folder_path):
            self.sync_enabled = True
            self.load_file_hashes()
            
            # Otomatik senkronizasyonu başlat
            if self.sync_interval > 0:
                self.sync_timer.start(self.sync_interval * 60 * 1000)  # dakika -> milisaniye
                
        return True
        
    def load_file_hashes(self):
        """Dosya hash'lerini yükle"""
        hash_path = os.path.join(self.sync_folder, self.hash_file)
        if os.path.exists(hash_path):
            try:
                with open(hash_path, 'r', encoding='utf-8') as f:
                    self.file_hashes = json.load(f)
            except Exception as e:
                print(f"Hash dosyası yüklenirken hata: {e}")
                self.file_hashes = {}
                
    def save_file_hashes(self):
        """Dosya hash'lerini kaydet"""
        if not self.sync_folder:
            return
            
        hash_path = os.path.join(self.sync_folder, self.hash_file)
        try:
            with open(hash_path, 'w', encoding='utf-8') as f:
                json.dump(self.file_hashes, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Hash dosyası kaydedilirken hata: {e}")
            
    def calculate_file_hash(self, file_path: str) -> str:
        """Dosya hash'ini hesapla"""
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
                return hashlib.md5(content).hexdigest()
        except Exception as e:
            print(f"Hash hesaplanırken hata: {e}")
            return ""
            
    def sync_file(self, file_path: str) -> bool:
        """Tek dosyayı senkronize et"""
        if not self.sync_folder or not os.path.exists(file_path):
            return False
            
        try:
            # Dosya adını al
            file_name = os.path.basename(file_path)
            sync_path = os.path.join(self.sync_folder, file_name)
            
            # Hash hesapla
            current_hash = self.calculate_file_hash(file_path)
            stored_hash = self.file_hashes.get(file_path, "")
            
            # Dosya değişmiş mi kontrol et
            if current_hash != stored_hash:
                # Dosyayı kopyala
                shutil.copy2(file_path, sync_path)
                
                # Hash'i güncelle
                self.file_hashes[file_path] = current_hash
                self.save_file_hashes()
                
                self.file_synced.emit(file_path)
                return True
                
        except Exception as e:
            print(f"Dosya senkronize edilirken hata: {e}")
            return False
            
        return False
        
    def sync_all_files(self, file_paths: List[str]) -> bool:
        """Tüm dosyaları senkronize et"""
        if self.is_syncing:
            return False
            
        self.is_syncing = True
        self.sync_started.emit()
        
        try:
            success_count = 0
            total_files = len(file_paths)
            
            for i, file_path in enumerate(file_paths):
                if self.sync_file(file_path):
                    success_count += 1
                    
                # İlerleme bildir
                progress = int((i + 1) / total_files * 100)
                self.sync_progress.emit(progress)
                
            success = success_count == total_files
            message = f"{success_count}/{total_files} dosya senkronize edildi"
            
            self.sync_finished.emit(success, message)
            return success
            
        except Exception as e:
            error_message = f"Senkronizasyon hatası: {e}"
            self.sync_finished.emit(False, error_message)
            return False
        finally:
            self.is_syncing = False
            
    def auto_sync(self):
        """Otomatik senkronizasyon"""
        if not self.sync_enabled or self.is_syncing:
            return
            
        # Burada mevcut dosyaları almak için parent'tan bilgi alınabilir
        # Şimdilik boş liste ile çağırıyoruz
        self.sync_all_files([])
        
    def start_sync_thread(self, file_paths: List[str]):
        """Senkronizasyon thread'ini başlat"""
        if self.sync_thread and self.sync_thread.isRunning():
            return
            
        self.sync_thread = SyncThread(self, file_paths)
        self.sync_thread.sync_started.connect(self.sync_started.emit)
        self.sync_thread.sync_finished.connect(self.sync_finished.emit)
        self.sync_thread.file_synced.connect(self.file_synced.emit)
        self.sync_thread.sync_progress.connect(self.sync_progress.emit)
        
        self.sync_thread.start()
        
    def stop_sync(self):
        """Senkronizasyonu durdur"""
        if self.sync_thread and self.sync_thread.isRunning():
            self.sync_thread.terminate()
            self.sync_thread.wait()
            
        self.sync_timer.stop()
        self.is_syncing = False
        
    def get_sync_status(self) -> Dict:
        """Senkronizasyon durumunu al"""
        return {
            'enabled': self.sync_enabled,
            'folder': self.sync_folder,
            'interval': self.sync_interval,
            'is_syncing': self.is_syncing,
            'file_count': len(self.file_hashes)
        }
        
    def cleanup_old_files(self, days: int = 30):
        """Eski dosyaları temizle"""
        if not self.sync_folder:
            return
            
        try:
            current_time = time.time()
            cutoff_time = current_time - (days * 24 * 60 * 60)  # gün -> saniye
            
            for file_name in os.listdir(self.sync_folder):
                file_path = os.path.join(self.sync_folder, file_name)
                
                if os.path.isfile(file_path) and file_name != self.hash_file:
                    file_time = os.path.getmtime(file_path)
                    
                    if file_time < cutoff_time:
                        os.remove(file_path)
                        print(f"Eski dosya silindi: {file_name}")
                        
        except Exception as e:
            print(f"Eski dosyalar temizlenirken hata: {e}")


class SyncThread(QThread):
    """Senkronizasyon thread'i"""
    
    sync_started = pyqtSignal()
    sync_finished = pyqtSignal(bool, str)
    file_synced = pyqtSignal(str)
    sync_progress = pyqtSignal(int)
    
    def __init__(self, cloud_sync: CloudSync, file_paths: List[str]):
        super().__init__()
        self.cloud_sync = cloud_sync
        self.file_paths = file_paths
        
    def run(self):
        """Thread çalıştır"""
        self.cloud_sync.sync_all_files(self.file_paths)


class GoogleDriveSync(CloudSync):
    """Google Drive senkronizasyon"""
    
    def __init__(self, api_key: str = ""):
        super().__init__()
        self.api_key = api_key
        self.service = None
        
    def authenticate(self):
        """Google Drive API kimlik doğrulaması"""
        try:
            # Google Drive API kimlik doğrulama kodu burada olacak
            # Şimdilik basit bir simülasyon
            return True
        except Exception as e:
            print(f"Google Drive kimlik doğrulama hatası: {e}")
            return False
            
    def upload_file(self, file_path: str) -> bool:
        """Dosyayı Google Drive'a yükle"""
        if not self.authenticate():
            return False
            
        try:
            # Google Drive API upload kodu burada olacak
            print(f"Dosya Google Drive'a yüklendi: {file_path}")
            return True
        except Exception as e:
            print(f"Google Drive upload hatası: {e}")
            return False
            
    def download_file(self, file_id: str, local_path: str) -> bool:
        """Dosyayı Google Drive'dan indir"""
        if not self.authenticate():
            return False
            
        try:
            # Google Drive API download kodu burada olacak
            print(f"Dosya Google Drive'dan indirildi: {local_path}")
            return True
        except Exception as e:
            print(f"Google Drive download hatası: {e}")
            return False


class DropboxSync(CloudSync):
    """Dropbox senkronizasyon"""
    
    def __init__(self, access_token: str = ""):
        super().__init__()
        self.access_token = access_token
        
    def authenticate(self):
        """Dropbox API kimlik doğrulaması"""
        try:
            # Dropbox API kimlik doğrulama kodu burada olacak
            return True
        except Exception as e:
            print(f"Dropbox kimlik doğrulama hatası: {e}")
            return False
            
    def upload_file(self, file_path: str) -> bool:
        """Dosyayı Dropbox'a yükle"""
        if not self.authenticate():
            return False
            
        try:
            # Dropbox API upload kodu burada olacak
            print(f"Dosya Dropbox'a yüklendi: {file_path}")
            return True
        except Exception as e:
            print(f"Dropbox upload hatası: {e}")
            return False


class LocalSync(CloudSync):
    """Yerel klasör senkronizasyonu"""
    
    def __init__(self, sync_folder: str = ""):
        super().__init__()
        self.sync_folder = sync_folder
        
    def setup_sync(self, folder_path: str, interval: int = 30):
        """Yerel senkronizasyon ayarla"""
        if not folder_path:
            return False
            
        # Klasörü oluştur
        try:
            os.makedirs(folder_path, exist_ok=True)
        except Exception as e:
            print(f"Klasör oluşturulurken hata: {e}")
            return False
            
        return super().setup_sync(folder_path, interval)
        
    def sync_file(self, file_path: str) -> bool:
        """Dosyayı yerel klasöre senkronize et"""
        if not self.sync_folder or not os.path.exists(file_path):
            return False
            
        try:
            # Dosya adını al
            file_name = os.path.basename(file_path)
            sync_path = os.path.join(self.sync_folder, file_name)
            
            # Hash hesapla
            current_hash = self.calculate_file_hash(file_path)
            stored_hash = self.file_hashes.get(file_path, "")
            
            # Dosya değişmiş mi kontrol et
            if current_hash != stored_hash:
                # Dosyayı kopyala
                shutil.copy2(file_path, sync_path)
                
                # Hash'i güncelle
                self.file_hashes[file_path] = current_hash
                self.save_file_hashes()
                
                self.file_synced.emit(file_path)
                return True
                
        except Exception as e:
            print(f"Yerel dosya senkronize edilirken hata: {e}")
            return False
            
        return False 