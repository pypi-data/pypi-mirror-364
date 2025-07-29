# 🌩️ PyCloud OS

Modern, Python tabanlı, macOS benzeri işletim sistemi. Modüler mimarisi, güçlü GUI sistemi ve kapsamlı uygulama ekosistemine sahiptir.

## ✨ Özellikler

### 🖥️ Rain UI System
- **Dock**: Uygulamalara hızlı erişim, live preview, sürükle-bırak desteği
- **Topbar**: Sistem kontrolleri, bildirimler, kullanıcı menüsü
- **Desktop**: Özelleştirilebilir masaüstü, wallpaper yönetimi
- **Context Menu**: Dosya ve uygulama işlemleri için sağ tık menüleri

### 📱 Core Applications
- **Cloud Files**: Dosya yöneticisi (Finder benzeri)
- **Cloud Terminal**: Modern terminal uygulaması
- **Cloud Browser**: WebEngine tabanlı web tarayıcısı
- **Cloud PyIDE**: Python geliştirme ortamı
- **Cloud Settings**: Sistem ayarları ve konfigürasyon
- **Cloud Task Manager**: Sistem izleme ve görev yöneticisi

### 📦 Clapp Package System
- **Clapp Store**: Uygulama mağazası ve paket yöneticisi
- **App Explorer**: Kurulu uygulamaları keşfetme ve yönetme
- **.app Format**: Standart uygulama paket formatı

### 🛠️ Developer Features
- **Modüler Mimari**: Bağımsız core modüller
- **Event System**: Modüller arası iletişim
- **Plugin Support**: Genişletilebilir uygulama sistemi
- **Theme System**: Özelleştirilebilir görünüm

## 🚀 Kurulum

### Gereksinimler

- **Python 3.8+**
- **PyQt6** (GUI için)
- **psutil** (sistem izleme için)

### Otomatik Kurulum

```bash
# Repository'yi klonlayın
git clone https://github.com/your-username/pycloud-os.git
cd pycloud-os

# Bağımlılıkları otomatik kontrol et ve yükle
python setup_deps.py

# PyCloud OS'i başlat
python main.py
```

### Manuel Kurulum

```bash
# Temel bağımlılıkları yükle
pip install -r requirements.txt

# Geliştirme bağımlılıkları (opsiyonel)
pip install -r requirements-dev.txt
```

### Bağımlılık Listesi

#### Gerekli Paketler
- `PyQt6>=6.4.0` - GUI framework
- `PyQt6-WebEngine>=6.4.0` - Web browser desteği
- `psutil>=5.9.0` - Sistem izleme
- `requests>=2.28.0` - HTTP istekleri
- `Pillow>=9.0.0` - Resim işleme
- `pyserial>=3.5` - Seri port desteği
- `Flask>=2.2.0` - PyIDE şablonları için

#### Standart Python Kütüphaneleri
- `json`, `os`, `sys`, `pathlib`, `typing`
- `datetime`, `logging`, `threading`, `time`
- `subprocess`, `shutil`, `zipfile`, `urllib`
- `hashlib`, `uuid`, `enum`, `dataclasses`

## 🎯 Kullanım

### İlk Başlatma

1. **Sistem Başlatma**:
   ```bash
   python main.py
   ```

2. **Kullanıcı Girişi**: Demo kullanıcısı ile giriş yapın

3. **Uygulamaları Keşfetme**: Topbar'daki "Uygulamalar" menüsünden

### Uygulama Yönetimi

#### Clapp Komut Satırı
```bash
# Mevcut uygulamaları listele
python -m clapp.core list

# Yeni uygulama yükle
python -m clapp.core install <app_package>

# Uygulama kaldır
python -m clapp.core remove <app_id>

# Sistem durumu kontrol et
python -m clapp.core doctor
```

#### App Store UI
- Topbar → "☁️ PyCloud" → "App Store"
- Kategori bazlı uygulama gezinme
- Tek tıkla kurulum ve kaldırma

### Geliştirme

#### Yeni Uygulama Oluşturma

1. **Uygulama Klasörü Oluşturun**:
   ```
   apps/my_app/
   ├── app.json
   ├── main.py
   ├── icon.png
   └── README.md
   ```

2. **app.json Yapılandırması**:
   ```json
   {
     "id": "my_app",
     "name": "My Application",
     "version": "1.0.0",
     "description": "My awesome app for PyCloud OS",
     "entry": "main.py",
     "exec": "python3 main.py",
     "requires": ["python3", "pyqt6"],
     "category": "Utilities"
   }
   ```

3. **main.py Launcher**:
   ```python
   import sys
   from pathlib import Path
   sys.path.insert(0, str(Path(__file__).parent.parent.parent))
   
   from my_app_module import run_app
   
   if __name__ == "__main__":
       sys.exit(run_app())
   ```

#### Core Modül Geliştirme

```python
# core/my_module.py
class MyModule:
    def __init__(self, kernel):
        self.kernel = kernel
        self.logger = logging.getLogger("MyModule")
    
    def initialize(self):
        # Modül başlatma
        pass
    
    def shutdown(self):
        # Temizlik işlemleri
        pass

def init_my_module(kernel):
    return MyModule(kernel)
```

## 🗂️ Proje Yapısı

```
pycloud-os/
├── core/               # Çekirdek modüller
│   ├── kernel.py      # Ana çekirdek
│   ├── fs/            # Dosya sistemi
│   ├── users.py       # Kullanıcı yönetimi
│   ├── process.py     # Süreç yönetimi
│   └── ...
├── rain/              # UI sistem bileşenleri
│   ├── ui.py          # Ana UI yöneticisi
│   ├── desktop.py     # Masaüstü
│   ├── dock.py        # Dock
│   ├── topbar.py      # Üst çubuk
│   └── ...
├── cloud/             # Core uygulamalar
│   ├── files.py       # Dosya yöneticisi
│   ├── terminal.py    # Terminal
│   ├── browser.py     # Web tarayıcısı
│   └── ...
├── clapp/             # Paket yönetim sistemi
│   ├── core.py        # Paket yöneticisi
│   ├── repo.py        # Repository yönetimi
│   └── ui.py          # App Store UI
├── apps/              # .app uygulamaları
│   ├── cloud_files/
│   ├── cloud_terminal/
│   └── ...
├── system/            # Sistem dosyaları
│   ├── config/        # Yapılandırma
│   ├── wallpapers/    # Duvar kağıtları
│   └── themes/        # Temalar
├── requirements.txt   # Production bağımlılıkları
├── requirements-dev.txt # Development bağımlılıkları
├── setup_deps.py      # Bağımlılık kurulum scripti
└── main.py           # Ana başlatıcı
```

## 🧪 Testing

```bash
# Unit testleri çalıştır
python -m pytest

# Coverage raporu
python -m pytest --cov=core --cov=rain --cov=cloud

# Linting
python -m flake8 core/ rain/ cloud/
python -m black --check .
```

## 📚 Dokümantasyon

```bash
# Sphinx dokümantasyonu oluştur
cd docs/
make html

# Dokümantasyonu görüntüle
open _build/html/index.html
```

## 🤝 Katkıda Bulunma

1. Repository'yi fork edin
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Değişikliklerinizi commit edin (`git commit -m 'Add amazing feature'`)
4. Branch'inizi push edin (`git push origin feature/amazing-feature`)
5. Pull Request oluşturun

### Development Setup

```bash
# Development bağımlılıklarını yükle
pip install -r requirements-dev.txt

# Pre-commit hooks kur
pre-commit install

# Code formatting
black .
isort .
```

## 📄 Lisans

Bu proje MIT lisansı altında lisanslanmıştır - detaylar için [LICENSE](LICENSE) dosyasına bakın.

## 🙏 Teşekkürler

- **PyQt6**: Güçlü GUI framework
- **Python Community**: Harika ecosystem
- **macOS**: Design inspiration

## 📞 İletişim

- **GitHub Issues**: Bug raporları ve feature istekleri
- **Discussions**: Genel sorular ve tartışmalar

---

**PyCloud OS** - Python ile modern işletim sistemi deneyimi 🌩️ 