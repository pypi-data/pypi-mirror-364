# Cloud Web Browser

Python ve Flet kullanılarak geliştirilmiş modern bir web tarayıcı uygulaması. WebView teknolojisi ile gerçek web sayfalarını uygulama içinde görüntüler.

## 🌟 Özellikler

### 🚀 Temel Özellikler
- **WebView Desteği**: Gerçek web sayfalarını uygulama içinde görüntüleme
- **Modern Arayüz**: Flet framework'ü ile oluşturulmuş güzel ve kullanıcı dostu arayüz
- **URL Navigasyonu**: URL girişi ve otomatik tamamlama
- **Geri/İleri**: Sayfa geçmişi ile navigasyon
- **Yenileme**: Sayfa yenileme özelliği
- **Ana Sayfa**: Hızlı ana sayfa erişimi

### 🔍 Gelişmiş Özellikler
- **Hızlı Erişim**: Popüler sitelere hızlı erişim butonları
- **Yer İmleri**: Sayfa yer imi ekleme/çıkarma
- **JavaScript Desteği**: Modern web sitelerinin tam desteği
- **Arama**: Google arama entegrasyonu
- **Geçmiş**: Ziyaret edilen sayfaların geçmişi
- **Varsayılan Tarayıcı**: İsteğe bağlı varsayılan tarayıcıda açma

### 🎨 Kullanıcı Deneyimi
- **Responsive Tasarım**: Farklı ekran boyutlarına uyumlu
- **Tema Desteği**: Açık tema
- **Yükleme Göstergeleri**: Kullanıcı dostu yükleme animasyonları
- **Hata Yönetimi**: Kapsamlı hata mesajları

## 🛠️ Kurulum

### Gereksinimler
- Python 3.8 veya üzeri
- Flet framework
- Diğer gerekli paketler

### Adımlar

1. **Projeyi klonlayın:**
```bash
git clone <repository-url>
cd fletbrowser
```

2. **Gerekli paketleri yükleyin:**
```bash
pip install -r requirements.txt
```

3. **Uygulamayı çalıştırın:**
```bash
python cloud_browser.py
```

## 🎯 Kullanım

### Temel Kullanım
1. URL alanına istediğiniz web sitesinin adresini yazın
2. Enter tuşuna basın veya "Git" butonuna tıklayın
3. Navigasyon butonlarını kullanarak sayfalar arası geçiş yapın

### Hızlı Erişim
- Google, YouTube, GitHub, Wikipedia, Stack Overflow, Twitter gibi popüler sitelere hızlı erişim butonlarını kullanın
- Ana sayfa butonuna tıklayarak Google'a dönün

### Yer İmleri
- Sayfa açıkken yer imi butonuna tıklayarak sayfayı kaydedin
- Yer imi eklenmiş sayfalar için buton rengi değişir

### Varsayılan Tarayıcı
- "Varsayılan Tarayıcıda Aç" butonuna tıklayarak sayfayı sistem tarayıcısında açın

## 📁 Dosya Yapısı

```
fletbrowser/
├── cloud_browser.py    # Ana web tarayıcı uygulaması
├── requirements.txt    # Gerekli paketler
└── README.md          # Bu dosya
```

## 🔧 Teknik Detaylar

### Kullanılan Teknolojiler
- **Flet**: Modern Python UI framework
- **WebView**: Gerçek web sayfası görüntüleme
- **Threading**: Asenkron işlemler

### Mimari
- **MVC Benzeri Yapı**: Model-View-Controller benzeri organizasyon
- **Event-Driven**: Olay tabanlı programlama
- **WebView Integration**: Gerçek web engine entegrasyonu

## 🌐 WebView Avantajları

### ✅ Gerçek Web Deneyimi
- JavaScript çalışır
- CSS stilleri doğru görüntülenir
- Modern web siteleri tam desteklenir
- Video ve ses oynatma
- Form doldurma
- AJAX istekleri

### ✅ Performans
- Hızlı sayfa yükleme
- Düşük bellek kullanımı
- Smooth navigasyon

### ✅ Güvenlik
- Sandboxed ortam
- Güvenli web görüntüleme

## 🎨 Özelleştirme

### Tema Değişiklikleri
`cloud_browser.py` dosyasında:
```python
page.theme_mode = ft.ThemeMode.LIGHT  # Açık tema
page.theme_mode = ft.ThemeMode.DARK   # Koyu tema
```

### Yeni Hızlı Erişim Butonları
Hızlı erişim bölümüne yeni butonlar ekleyebilirsiniz:
```python
ft.ElevatedButton(
    "Site Adı",
    icon="icon_name",
    on_click=lambda _: self.navigate_to("https://site.com")
)
```

## 🚀 Özellikler Listesi

- ✅ WebView ile gerçek web sayfası görüntüleme
- ✅ JavaScript desteği
- ✅ Modern web standartları
- ✅ Hızlı erişim butonları
- ✅ Yer imi sistemi
- ✅ Sayfa geçmişi
- ✅ URL navigasyonu
- ✅ Sayfa yenileme
- ✅ Varsayılan tarayıcıda açma
- ✅ Modern arayüz
- ✅ Responsive tasarım
- ✅ Hata yönetimi

## 📝 Lisans

Bu proje MIT lisansı altında lisanslanmıştır.

## 🤝 Katkıda Bulunma

1. Projeyi fork edin
2. Yeni bir branch oluşturun (`git checkout -b feature/yeni-ozellik`)
3. Değişikliklerinizi commit edin (`git commit -am 'Yeni özellik eklendi'`)
4. Branch'inizi push edin (`git push origin feature/yeni-ozellik`)
5. Pull Request oluşturun

---

**Cloud Web Browser** - Modern ve hızlı web tarama deneyimi! 🚀✨ 