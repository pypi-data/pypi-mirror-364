# Cloud Notepad - Modern Notepad Uygulaması

Modern ve gelişmiş bir notepad uygulaması. PyQt6 ile geliştirilmiş, Notepad++ benzeri özelliklere sahip cloud destekli metin editörü.

## 🚀 Özellikler

### Temel Özellikler
- ✅ **Çoklu Sekme Desteği** - Aynı anda birden fazla dosya düzenleme
- ✅ **Syntax Highlighting** - Python, JavaScript, HTML, CSS ve daha fazlası için kod renklendirme
- ✅ **Tema Desteği** - Açık ve koyu tema seçenekleri
- ✅ **Otomatik Kaydetme** - Belirli aralıklarla otomatik kaydetme
- ✅ **Bul ve Değiştir** - Gelişmiş arama ve değiştirme işlevleri
- ✅ **Zoom İşlevleri** - Metin boyutunu artırma/azaltma

### Gelişmiş Özellikler
- 🔄 **Cloud Senkronizasyon** - Dosyaları cloud servisleri ile senkronize etme
- 📁 **Dosya Gezgini** - Sol panelde dosya listesi
- 📊 **İstatistikler** - Satır, kelime ve karakter sayısı
- ⚙️ **Kapsamlı Ayarlar** - Detaylı yapılandırma seçenekleri
- 🎨 **Font Özelleştirme** - Font ailesi ve boyutu değiştirme
- 📝 **Düzenleme Geçmişi** - Dosya değişiklik geçmişi

### Cloud Özellikleri
- ☁️ **Google Drive Entegrasyonu** - Google Drive ile senkronizasyon
- 📦 **Dropbox Desteği** - Dropbox ile dosya paylaşımı
- 💾 **Yerel Senkronizasyon** - Yerel klasör ile senkronizasyon
- 🔐 **Güvenli Kimlik Doğrulama** - API key ile güvenli erişim

## 📋 Gereksinimler

- Python 3.8 veya üzeri
- PyQt6
- Pygments (syntax highlighting için)

## 🛠️ Kurulum

1. **Projeyi klonlayın:**
```bash
git clone https://github.com/yourusername/cloud-notepad.git
cd cloud-notepad
```

2. **Gerekli paketleri yükleyin:**
```bash
pip install -r requirements.txt
```

3. **Uygulamayı çalıştırın:**
```bash
python main.py
```

## 🎯 Kullanım

### Temel İşlemler
- **Yeni Dosya:** `Ctrl+N` veya Dosya → Yeni
- **Dosya Aç:** `Ctrl+O` veya Dosya → Aç
- **Kaydet:** `Ctrl+S` veya Dosya → Kaydet
- **Farklı Kaydet:** `Ctrl+Shift+S` veya Dosya → Farklı Kaydet

### Düzenleme İşlemleri
- **Geri Al:** `Ctrl+Z`
- **Yinele:** `Ctrl+Y`
- **Kes:** `Ctrl+X`
- **Kopyala:** `Ctrl+C`
- **Yapıştır:** `Ctrl+V`

### Arama İşlemleri
- **Bul:** `Ctrl+F`
- **Değiştir:** `Ctrl+H`
- **Sonraki:** `F3`
- **Önceki:** `Shift+F3`

### Görünüm Ayarları
- **Yakınlaştır:** `Ctrl++`
- **Uzaklaştır:** `Ctrl+-`
- **Yakınlaştırmayı Sıfırla:** `Ctrl+0`

## ⚙️ Ayarlar

### Genel Ayarlar
- **Tema Seçimi:** Açık, Koyu, Otomatik
- **Dil Seçimi:** Türkçe, English
- **Başlangıç Ayarları:** Yeni dosya açma, son dosyaları hatırlama

### Editör Ayarları
- **Font Seçimi:** Font ailesi ve boyutu
- **Satır Numaraları:** Göster/gizle
- **Kelime Kaydırma:** Etkinleştir/devre dışı bırak
- **Syntax Highlighting:** Etkinleştir/devre dışı bırak

### Cloud Ayarları
- **Cloud Servis:** Google Drive, Dropbox, OneDrive, Local Sync
- **API Key:** Cloud servis kimlik doğrulama
- **Senkronizasyon Klasörü:** Yerel senkronizasyon klasörü
- **Otomatik Senkronizasyon:** Aralık ayarları

## 🏗️ Proje Yapısı

```
cloud_note/
├── main.py                 # Ana uygulama dosyası
├── syntax_highlighter.py   # Syntax highlighting modülü
├── find_replace_dialog.py  # Bul ve değiştir dialog'u
├── settings_dialog.py      # Ayarlar dialog'u
├── cloud_sync.py          # Cloud senkronizasyon modülü
├── requirements.txt       # Gerekli paketler
└── README.md             # Bu dosya
```

## 🔧 Geliştirme

### Yeni Özellik Ekleme
1. İlgili modülü düzenleyin
2. Ana uygulamaya entegre edin
3. Test edin
4. Dokümantasyonu güncelleyin

### Syntax Highlighting Ekleme
1. `syntax_highlighter.py` dosyasında yeni dil kuralları tanımlayın
2. `detect_language` fonksiyonuna dosya uzantısını ekleyin
3. Renk formatlarını özelleştirin

### Cloud Servis Ekleme
1. `cloud_sync.py` dosyasında yeni servis sınıfı oluşturun
2. API entegrasyonunu implement edin
3. Ayarlar dialog'una servis seçeneğini ekleyin

## 🐛 Bilinen Sorunlar

- Büyük dosyalarda (100MB+) performans sorunları olabilir
- Bazı cloud servisleri için API key gerekli
- Windows'ta bazı fontlar görünmeyebilir

## 🤝 Katkıda Bulunma

1. Fork yapın
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Değişikliklerinizi commit edin (`git commit -m 'Add amazing feature'`)
4. Branch'inizi push edin (`git push origin feature/amazing-feature`)
5. Pull Request oluşturun

## 📄 Lisans

Bu proje MIT lisansı altında lisanslanmıştır. Detaylar için `LICENSE` dosyasına bakın.

## 🙏 Teşekkürler

- [PyQt6](https://www.riverbankcomputing.com/software/pyqt/) - GUI framework
- [Pygments](https://pygments.org/) - Syntax highlighting
- [Qt](https://www.qt.io/) - Cross-platform application framework

## 📞 İletişim

- **Geliştirici:** [Adınız]
- **Email:** [email@example.com]
- **GitHub:** [github.com/yourusername]

## 🔄 Güncellemeler

### v1.0.0 (2024-01-01)
- İlk sürüm
- Temel notepad özellikleri
- Syntax highlighting
- Cloud senkronizasyon altyapısı

---

⭐ Bu projeyi beğendiyseniz yıldız vermeyi unutmayın! 