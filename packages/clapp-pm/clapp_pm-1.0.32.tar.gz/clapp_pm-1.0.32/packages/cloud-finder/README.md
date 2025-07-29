# Cloud Finder

MacOS Finder'a benzeyen gelişmiş ve modern dosya gezgini uygulaması.

## 🚀 Yeni Özellikler

### **Gelişmiş Arayüz**
- 🎨 Liste ve Grid görünüm seçenekleri
- 🔍 Gerçek zamanlı dosya arama
- 👁️ Gizli dosyaları göster/gizle
- 📊 Gelişmiş sıralama seçenekleri (isim, boyut, tarih, tür)
- 🎯 Son kullanılan dosyalar geçmişi
- ⭐ Favori dosya/klasör sistemi

### **Gelişmiş Dosya Yönetimi**
- 📋 Çoklu dosya seçimi (Ctrl+Click)
- 🎯 Sağ tık bağlam menüsü
- 📋 Gelişmiş kopyala/kes/yapıştır işlemleri
- 🗑️ Güvenli silme işlemleri
- 📁 Yeni klasör/dosya oluşturma
- 📊 Detaylı dosya bilgileri

### **Kullanıcı Deneyimi**
- 🔔 Bildirim sistemi
- ⚡ Yükleme göstergeleri
- 🎨 Modern Material Design
- 📱 Responsive tasarım
- 🎯 Seçim sayacı
- 📋 Tooltip'ler ve yardım metinleri

## 📋 Özellikler

- 🎨 **Modern Arayüz**: MacOS Finder benzeri temiz tasarım
- 📁 **Tam Dosya Yönetimi**: Kopyala, kes, yapıştır, sil, yeniden adlandır
- 🔍 **Gelişmiş Arama**: Gerçek zamanlı dosya arama
- 🗂️ **Navigasyon**: Geri, ileri, üst klasör butonları
- 🎯 **Favori Klasörler**: Hızlı erişim için favori klasörler
- 📊 **Dosya Bilgileri**: Boyut, tarih, tür bilgileri
- 👁️ **Görünüm Seçenekleri**: Liste ve Grid görünümü
- 📈 **Sıralama**: İsim, boyut, tarih, tür sıralaması
- 🎯 **Geçmiş**: Son kullanılan dosyalar
- ⭐ **Favoriler**: Özel favori dosya/klasör sistemi

## 🛠️ Kurulum

1. **Python 3.8+** sürümünün yüklü olduğundan emin olun
2. **Gerekli paketleri yükleyin:**
   ```bash
   pip install -r requirements.txt
   ```

## 🚀 Çalıştırma

```bash
python main.py
```

## 📖 Kullanım Kılavuzu

### **Temel İşlemler**
- **Navigasyon**: Sidebar'daki favori klasörlere tıklayarak hızlı erişim
- **Dosya Seçimi**: 
  - Tek dosya: Normal tıklama
  - Çoklu seçim: Uzun basma
  - Tümünü seç: Ctrl+A (geliştirilecek)
- **Dosya Açma**: Dosyalara çift tıklayarak varsayılan uygulamada açın

### **Dosya İşlemleri**
- **Kopyala**: Seçili dosyaları kopyalamak için toolbar butonunu kullanın
- **Kes**: Seçili dosyaları kesmek için toolbar butonunu kullanın
- **Yapıştır**: Kopyalanan/kesilen dosyaları yapıştırmak için toolbar butonunu kullanın
- **Sil**: Seçili dosyaları silmek için toolbar butonunu kullanın
- **Yeni Klasör/Dosya**: Toolbar'daki ilgili butonları kullanın

### **Görünüm ve Arama**
- **Görünüm Değiştir**: Toolbar'daki görünüm butonunu kullanarak liste/grid arası geçiş
- **Arama**: Üst toolbar'daki arama kutusunu kullanarak dosya arayın
- **Gizli Dosyalar**: Gizli dosyaları göster/gizle butonunu kullanın
- **Sıralama**: Sıralama menüsünden istediğiniz sıralama türünü seçin

### **Gelişmiş Özellikler**
- **Sağ Tık Menüsü**: Dosyalara sağ tıklayarak hızlı işlemler
- **Favorilere Ekle**: Dosyaları favorilere ekleyerek hızlı erişim
- **Son Kullanılanlar**: Sidebar'da son kullanılan dosyaları görün

## 🎨 Arayüz Özellikleri

### **Toolbar**
- **Sol**: Navigasyon butonları (Geri, İleri, Üst Klasör)
- **Orta**: Mevcut yol ve arama kutusu
- **Sağ**: Görünüm, gizli dosyalar, sıralama seçenekleri

### **Sidebar**
- **Favoriler**: Hızlı erişim klasörleri
- **Son Kullanılanlar**: Son açılan dosyalar
- **Cihazlar**: Sistem klasörleri

### **Ana İçerik**
- **Liste Görünümü**: Detaylı dosya listesi
- **Grid Görünümü**: İkon tabanlı görünüm
- **Seçim Sayacı**: Seçili dosya sayısı

## 🔧 Teknolojiler

- **Flet 0.28+**: Modern Python UI framework
- **Python 3.8+**: Ana programlama dili
- **Pathlib**: Gelişmiş dosya yolu işlemleri
- **OS**: İşletim sistemi entegrasyonu
- **JSON**: Veri saklama (geçmiş, favoriler)

## ✅ Tamamlanan Özellikler

### **Gelişmiş Dosya Yönetimi**
- ✅ **Çoklu Dosya Seçimi**: Uzun basma ile çoklu seçim
- ✅ **Aralık Seçimi**: Shift + tıklama ile aralık seçimi
- ✅ **Tümünü Seç**: Ctrl+A ile tüm dosyaları seçme
- ✅ **Sağ Tık Menüsü**: Hızlı işlemler için bağlam menüsü
- ✅ **Favorilere Ekleme**: Dosyaları favorilere ekleme

### **Navigasyon Sistemi**
- ✅ **Geri/İleri Geçmişi**: Tam navigasyon geçmişi
- ✅ **Akıllı Geçmiş Yönetimi**: Otomatik geçmiş temizleme
- ✅ **Geçmiş Takibi**: Hangi yönlerde gidilebileceğini gösterme

### **Klavye Kısayolları**
- ✅ **Ctrl+C**: Kopyala
- ✅ **Ctrl+V**: Yapıştır
- ✅ **Ctrl+X**: Kes
- ✅ **Ctrl+A**: Tümünü seç
- ✅ **Delete**: Sil
- ✅ **Escape**: Seçimi temizle

### **Veri Yönetimi**
- ✅ **JSON Tabanlı Geçmiş**: Son kullanılan dosyalar
- ✅ **Favori Sistemi**: Özel favori dosya/klasör sistemi
- ✅ **Hata Yönetimi**: Güvenli dosya işlemleri
- ✅ **UTF-8 Desteği**: Türkçe karakter desteği

## 🚧 Gelecek Özellikler

- 🔄 **Sürükle-Bırak**: Dosya taşıma için sürükle-bırak
- 📱 **Gelişmiş Bildirimler**: UI tabanlı bildirim sistemi
- 🎨 **Tema Desteği**: Karanlık/Aydınlık tema
- 📊 **Dosya Önizleme**: Resim ve metin önizleme
- 🔒 **Dosya Şifreleme**: Güvenli dosya şifreleme
- ☁️ **Bulut Entegrasyonu**: Google Drive, Dropbox desteği
- 🎯 **Gelişmiş Arama**: Alt klasörlerde arama
- 📈 **İstatistikler**: Dosya kullanım istatistikleri

## 📄 Lisans

Bu proje MIT lisansı altında lisanslanmıştır.

## 🤝 Katkıda Bulunma

1. Bu repository'yi fork edin
2. Yeni bir branch oluşturun (`git checkout -b feature/yeni-ozellik`)
3. Değişikliklerinizi commit edin (`git commit -am 'Yeni özellik eklendi'`)
4. Branch'inizi push edin (`git push origin feature/yeni-ozellik`)
5. Pull Request oluşturun

## 📞 Destek

Herhangi bir sorun yaşarsanız veya öneriniz varsa, lütfen issue açın. 