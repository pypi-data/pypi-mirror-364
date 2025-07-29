#!/usr/bin/env python3
"""
progress_utils.py - Progress Bar ve İndirme Hızı Göstergesi

Bu modül indirme ve yükleme işlemleri için progress bar ve hız göstergesi sağlar.
"""

import sys
import time
import threading
from typing import Optional, Callable
from urllib.request import urlopen
from urllib.error import URLError
from tqdm import tqdm


class ProgressBar:
    """Progress bar sınıfı"""
    
    def __init__(self, total: int, description: str = "İndiriliyor", width: int = 50):
        self.total = total
        self.description = description
        self.width = width
        self.current = 0
        self.start_time = time.time()
        self.last_update = 0
        self.speed = 0
        self.lock = threading.Lock()
        self.last_line_length = 0  # Son satır uzunluğunu takip et
    
    def update(self, current: int, speed: Optional[float] = None):
        """Progress bar'ı günceller"""
        with self.lock:
            self.current = current
            if speed is not None:
                self.speed = speed
            
            # Hız hesaplama
            if self.current > 0:
                elapsed = time.time() - self.start_time
                if elapsed > 0:
                    self.speed = self.current / elapsed
    
    def display(self):
        if self.total <= 0:
            return

        percentage = (self.current / self.total) * 100
        filled_width = int(self.width * self.current // self.total)
        bar = '█' * filled_width + '░' * (self.width - filled_width)
        speed_str = self._format_speed(self.speed)
        current_str = self._format_size(self.current)
        total_str = self._format_size(self.total)
        progress_line = f"{self.description}: [{bar}] {percentage:5.1f}% | {current_str}/{total_str} | {speed_str}"

        # Satır başına dön, progress barı yaz, kalan karakterleri temizle
        pad = getattr(self, 'last_line_length', 0) - len(progress_line)
        sys.stdout.write('\r' + progress_line + (' ' * pad if pad > 0 else ''))
        sys.stdout.flush()
        self.last_line_length = len(progress_line)

    def finish(self, success: bool = True):
        # Satırı temizle
        sys.stdout.write('\r' + ' ' * getattr(self, 'last_line_length', 80) + '\r')
        if success:
            print(f"✅ {self.description} tamamlandı!")
        else:
            print(f"❌ {self.description} başarısız!")
        sys.stdout.flush()
    
    def _format_speed(self, speed: float) -> str:
        """Hızı formatlar (B/s, KB/s, MB/s)"""
        if speed < 1024:
            return f"{speed:.1f} B/s"
        elif speed < 1024 * 1024:
            return f"{speed/1024:.1f} KB/s"
        else:
            return f"{speed/(1024*1024):.1f} MB/s"
    
    def _format_size(self, size: int) -> str:
        """Boyutu formatlar (B, KB, MB, GB)"""
        if size < 1024:
            return f"{size} B"
        elif size < 1024 * 1024:
            return f"{size/1024:.1f} KB"
        elif size < 1024 * 1024 * 1024:
            return f"{size/(1024*1024):.1f} MB"
        else:
            return f"{size/(1024*1024*1024):.1f} GB"


def download_with_progress(url: str, filename: str, description: str = "İndiriliyor") -> bool:
    """
    tqdm ile dosya indirir
    """
    try:
        response = urlopen(url)
        total_size = int(response.headers.get('content-length', 0))
        response.close()
        with urlopen(url) as response, open(filename, 'wb') as file, tqdm(
            total=total_size, unit='B', unit_scale=True, desc=description, ncols=80
        ) as bar:
            downloaded = 0
            chunk_size = 8192
            while True:
                chunk = response.read(chunk_size)
                if not chunk:
                    break
                file.write(chunk)
                downloaded += len(chunk)
                bar.update(len(chunk))
        print(f"✅ {description} tamamlandı!")
        return True
    except Exception as e:
        print(f"❌ İndirme hatası: {e}")
        return False

def copy_with_progress(src: str, dst: str, description: str = "Kopyalanıyor") -> bool:
    import os
    try:
        total_size = os.path.getsize(src)
        with open(src, 'rb') as src_file, open(dst, 'wb') as dst_file, tqdm(
            total=total_size, unit='B', unit_scale=True, desc=description, ncols=80
        ) as bar:
            copied = 0
            chunk_size = 8192
            while True:
                chunk = src_file.read(chunk_size)
                if not chunk:
                    break
                dst_file.write(chunk)
                copied += len(chunk)
                bar.update(len(chunk))
        print(f"✅ {description} tamamlandı!")
        return True
    except Exception as e:
        print(f"❌ Kopyalama hatası: {e}")
        return False

def extract_with_progress(zip_path: str, extract_path: str, description: str = "Çıkarılıyor") -> bool:
    """
    tqdm ile ZIP dosyası çıkarır
    """
    import zipfile
    import os
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            file_list = zip_ref.filelist
            total_files = len(file_list)
            if total_files == 0:
                print(f"❌ ZIP dosyası boş: {zip_path}")
                return False
            with tqdm(total=total_files, desc=description, ncols=80, unit='dosya') as bar:
                for file_info in file_list:
                    zip_ref.extract(file_info, extract_path)
                    bar.update(1)
        print(f"✅ {description} tamamlandı!")
        return True
    except Exception as e:
        print(f"❌ Çıkarma hatası: {e}")
        return False

def show_success_message(message: str):
    print(f"✅ {message}")

def show_error_message(message: str):
    print(f"❌ {message}")

def show_info_message(message: str):
    print(f"ℹ️  {message}")

def show_warning_message(message: str):
    print(f"⚠️  {message}") 