# Clapp Store

Clapp paket yöneticisinin grafiksel kullanıcı arayüzü (GUI) uygulaması. Python ve Lua uygulamalarını kolayca keşfedebilir, yükleyebilir ve yönetebilirsiniz.

## 🚀 Özellikler

- **Modern Arayüz**: Flet ile geliştirilmiş güzel ve kullanıcı dostu arayüz
- **Paket Keşfi**: GitHub'daki clapp-packages deposundan tüm paketleri görüntüleme
- **Kolay Yükleme**: Tek tıkla paket yükleme ve çalıştırma
- **Yüklü Paket Yönetimi**: Yüklü paketleri listeleme, çalıştırma ve kaldırma
- **Arama ve Filtreleme**: Paketleri isim ve açıklamaya göre arama
- **Gerçek Zamanlı Güncelleme**: Paket durumlarını otomatik güncelleme

## 📋 Gereksinimler

- Python 3.7+
- clapp paket yöneticisi (yüklü olmalı)
- İnternet bağlantısı

## 🛠️ Kurulum

1. **Bağımlılıkları yükleyin:**
```bash
pip install -r requirements.txt
```

2. **Clapp paket yöneticisini yükleyin (eğer yüklü değilse):**
```bash
pip install clapp-pm
```

3. **Uygulamayı çalıştırın:**
```bash
python main.py
```

## 🎯 Kullanım

### Ana Ekran
- **Tüm Uygulamalar**: Mevcut tüm paketleri grid görünümünde listeler
- **Yüklü Uygulamalar**: Sisteminizde yüklü olan paketleri gösterir
- **Hakkında**: Clapp ve Clapp Store hakkında bilgiler

### Paket İşlemleri
- **Yükleme**: Paket kartındaki "Yükle" butonuna tıklayın
- **Çalıştırma**: Yüklü paketler için "Çalıştır" butonuna tıklayın
- **Kaldırma**: "Kaldır" ikonuna tıklayarak paketi sistemden kaldırın
- **Detaylar**: Paket hakkında detaylı bilgi için "Detaylar" ikonuna tıklayın

### Arama
- Üst kısımdaki arama çubuğunu kullanarak paketleri filtreleyebilirsiniz
- Arama, paket adı ve açıklamasında çalışır

## 🔧 Teknik Detaylar

### Mimari
- **Frontend**: Flet (Python GUI framework)
- **Backend**: Python subprocess ile clapp CLI entegrasyonu
- **Veri Kaynağı**: GitHub clapp-packages deposu (index.json)

### Dosya Yapısı
```
clapp_store/
├── main.py              # Ana uygulama dosyası
├── requirements.txt     # Python bağımlılıkları
└── README.md           # Bu dosya
```

### Entegrasyon
- clapp CLI komutları ile tam entegrasyon
- GitHub API ile paket listesi çekme
- Gerçek zamanlı paket durumu kontrolü

## 🌐 Bağlantılar

- **Clapp Paket Yöneticisi**: [GitHub](https://github.com/mburakmmm/clapp)
- **Clapp Paket Deposu**: [GitHub](https://github.com/mburakmmm/clapp-packages)
- **Flet Framework**: [Dokümantasyon](https://flet.dev/)

## 🐛 Sorun Giderme

### Yaygın Sorunlar

1. **"clapp komutu bulunamadı" hatası**
   - clapp paket yöneticisinin yüklü olduğundan emin olun
   - `pip install clapp-pm` komutunu çalıştırın

2. **Paketler yüklenmiyor**
   - İnternet bağlantınızı kontrol edin
   - GitHub'a erişiminizin olduğundan emin olun

3. **Uygulama açılmıyor**
   - Python sürümünüzün 3.7+ olduğundan emin olun
   - Tüm bağımlılıkların yüklü olduğunu kontrol edin

### Hata Bildirimi
Sorun yaşarsanız, lütfen GitHub Issues üzerinden bildirin.

## 🤝 Katkıda Bulunma

1. Bu depoyu fork edin
2. Yeni bir branch oluşturun (`git checkout -b feature/yeni-ozellik`)
3. Değişikliklerinizi commit edin (`git commit -am 'Yeni özellik eklendi'`)
4. Branch'inizi push edin (`git push origin feature/yeni-ozellik`)
5. Pull Request oluşturun

## 📄 Lisans

Bu proje MIT lisansı altında lisanslanmıştır.

## 🙏 Teşekkürler

- [Clapp](https://github.com/mburakmmm/clapp) projesi için
- [Flet](https://flet.dev/) framework'ü için
- Tüm katkıda bulunanlara

---

**Not**: Bu uygulama, clapp paket yöneticisinin resmi GUI arayüzüdür ve clapp CLI ile tam uyumlu çalışır. 