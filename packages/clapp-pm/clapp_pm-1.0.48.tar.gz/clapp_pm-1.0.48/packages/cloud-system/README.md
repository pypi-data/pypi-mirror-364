# Cloud System - Sistem Yöneticisi

Modern ve profesyonel arayüze sahip, Python ve Flet ile geliştirilmiş kapsamlı bir sistem yöneticisi/görev yöneticisi uygulaması.

## 🚀 Özellikler

### 📋 Görev Yöneticisi
- Görev oluşturma, düzenleme ve silme
- Öncelik seviyeleri (Düşük, Orta, Yüksek, Kritik)
- Görev durumu takibi (Beklemede, Tamamlandı)
- Modern kart tabanlı arayüz

### 📊 Sistem İzleme
- Gerçek zamanlı CPU kullanımı
- RAM kullanımı ve bellek bilgileri
- Disk kullanımı ve depolama bilgileri
- Görsel progress bar'lar ile anlık izleme

### 🔄 Süreç Yönetimi
- Çalışan süreçlerin listesi
- CPU ve RAM kullanım oranları
- Süreç durumu bilgileri
- Süreç sonlandırma özelliği

### 📁 Dosya Yöneticisi
- Klasör ve dosya gezintisi
- Dosya boyutu görüntüleme
- Yeni klasör oluşturma
- Dosya silme ve yeniden adlandırma
- Geri/ileri navigasyon

### 🌐 Ağ İzleme
- Aktif ağ bağlantıları
- Gönderilen/alınan veri miktarları
- Paket istatistikleri
- Ağ performans bilgileri

### ℹ️ Sistem Bilgileri
- İşletim sistemi bilgileri
- Donanım bilgileri
- Python sürümü
- Kullanıcı ve çalışma dizini bilgileri

## 🛠️ Kurulum

### Gereksinimler
- Python 3.8 veya üzeri
- Flet framework
- psutil kütüphanesi

### Kurulum Adımları

1. **Projeyi klonlayın:**
```bash
git clone <repository-url>
cd cloud_system
```

2. **Gerekli paketleri yükleyin:**
```bash
pip install -r requirements.txt
```

3. **Uygulamayı çalıştırın:**
```bash
python main.py
```

## 📦 Gerekli Paketler

- `flet>=0.21.0` - Modern UI framework
- `psutil>=5.9.0` - Sistem ve süreç izleme
- `requests>=2.31.0` - HTTP istekleri
- `ping3>=4.0.4` - Ağ ping işlemleri
- `speedtest-cli>=2.1.3` - İnternet hız testi

## 🎨 Arayüz Özellikleri

- **Modern Tasarım**: Material Design 3 prensipleri
- **Karanlık Tema**: Göz yorgunluğunu azaltan koyu tema
- **Responsive Layout**: Farklı ekran boyutlarına uyum
- **Animasyonlar**: Yumuşak geçişler ve animasyonlar
- **İkonlar**: Material Design ikonları
- **Kartlar**: Modern kart tabanlı arayüz

## 🔧 Kullanım

### Görev Yöneticisi
1. "Görev Yöneticisi" sekmesine tıklayın
2. Yeni görev açıklaması girin
3. Öncelik seviyesini seçin
4. "Görev Ekle" butonuna tıklayın
5. Görevleri tamamlamak için ✓ butonuna tıklayın
6. Görevleri silmek için 🗑️ butonuna tıklayın

### Sistem İzleme
- Sistem İzleme sekmesi otomatik olarak güncellenir
- CPU, RAM ve Disk kullanımını gerçek zamanlı izleyin
- Progress bar'lar ile görsel geri bildirim alın

### Süreç Yönetimi
- Çalışan süreçleri CPU kullanımına göre sıralı görün
- Süreç detaylarını inceleyin
- Gereksiz süreçleri sonlandırın

### Dosya Yöneticisi
- Klasörlere çift tıklayarak gezinin
- Geri/ileri butonları ile navigasyon yapın
- "Yeni Klasör" butonu ile klasör oluşturun
- Dosya/klasör silme işlemleri yapın

## 🖥️ Sistem Gereksinimleri

- **İşletim Sistemi**: Windows, macOS, Linux
- **Python**: 3.8 veya üzeri
- **RAM**: Minimum 4GB (önerilen 8GB)
- **Disk**: 100MB boş alan

## 🔒 Güvenlik

- Uygulama yerel sistem kaynaklarına erişim gerektirir
- Süreç sonlandırma işlemleri dikkatli kullanılmalıdır
- Dosya silme işlemleri geri alınamaz

## 🐛 Bilinen Sorunlar

- Bazı sistemlerde süreç izleme kısıtlamaları olabilir
- Dosya yöneticisi büyük klasörlerde yavaşlayabilir
- Ağ izleme özellikleri firewall tarafından engellenebilir

## 🤝 Katkıda Bulunma

1. Projeyi fork edin
2. Feature branch oluşturun (`git checkout -b feature/AmazingFeature`)
3. Değişikliklerinizi commit edin (`git commit -m 'Add some AmazingFeature'`)
4. Branch'inizi push edin (`git push origin feature/AmazingFeature`)
5. Pull Request oluşturun

## 📄 Lisans

Bu proje MIT lisansı altında lisanslanmıştır.

## 👨‍💻 Geliştirici

Cloud System - Modern Sistem Yöneticisi uygulaması Python ve Flet ile geliştirilmiştir.

---

**Not**: Bu uygulama eğitim amaçlı geliştirilmiştir. Üretim ortamında kullanmadan önce gerekli testleri yapınız. 