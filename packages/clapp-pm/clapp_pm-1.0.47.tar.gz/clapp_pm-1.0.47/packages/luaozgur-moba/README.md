# Lua Özgür MOBA

League of Legends benzeri bir MOBA oyunu, Lua dili ve LÖVE2D framework'ü ile geliştirilmiştir.

## 🎮 Oyun Özellikleri

- **20 Farklı Karakter**: 5 kategoriye ayrılmış karakterler
  - 🧙‍♂️ **Büyücüler**: Yüksek hasar, düşük can
  - ⚔️ **Savaşçılar**: Dengeli hasar ve can
  - 🏹 **Nişancılar**: Uzun mesafe, yüksek hasar
  - 🛡️ **Destekler**: Düşük hasar, yardımcı yetenekler
  - 🛡️ **Tanklar**: Düşük hasar, yüksek can ve savunma

- **3 Şeritli Harita**: Üst, Orta, Alt şeritler
- **Kule Sistemi**: Her şeritte 6 kule (3'er tane her takım için)
- **Minion Sistemi**: Otomatik spawn eden minionlar
- **Savaş Sistemi**: Otomatik saldırı ve hasar hesaplama
- **Görsel Efektler**: Hasar göstergeleri ve animasyonlar

## 🚀 Kurulum

### Gereksinimler
- [LÖVE2D](https://love2d.org/) (0.11.0 veya üzeri)

### Kurulum Adımları

1. **LÖVE2D'yi indirin ve kurun**
   ```bash
   # macOS için (Homebrew ile)
   brew install love
   
   # Windows için
   # https://love2d.org/ adresinden indirin
   
   # Linux için
   sudo apt-get install love
   ```

2. **Projeyi çalıştırın**
   ```bash
   # Proje dizininde
   love .
   
   # Veya
   love /path/to/luaozgur
   ```

## 🎯 Oynanış

### Kontroller
- **Sol Tık**: Karakter seç / Hareket et
- **ESC**: Menüye dön
- **ENTER**: Oyunu başlat

### Oyun Kuralları
1. **Amaç**: Düşman kulelerini yıkarak üslerine ulaşmak
2. **Şeritler**: 3 farklı şerit (Üst, Orta, Alt)
3. **Minionlar**: Her 30 saniyede otomatik spawn olur
4. **Savaş**: Karakterler otomatik olarak düşmanlara saldırır
5. **Kazanma**: Tüm düşman kulelerini yıkan takım kazanır

### Karakter Seçimi
- Ana menüden "Karakter Seç" butonuna tıklayın
- 20 farklı karakterden birini seçin
- Takımınızı belirleyin (Mavi/Kırmızı)
- "Oyunu Başlat" ile oyuna başlayın

## 🏗️ Proje Yapısı

```
luaozgur/
├── main.lua          # Ana oyun dosyası
├── game.lua          # Oyun mantığı
├── menu.lua          # Menü sistemi
├── characters.lua    # Karakter tanımları
├── map.lua           # Harita ve kule sistemi
└── README.md         # Bu dosya
```

## 🎨 Karakter Kategorileri

### Büyücüler (4 karakter)
- **Ateş Büyücüsü**: Yüksek hasar, ateş temalı yetenekler
- **Buz Büyücüsü**: Kontrol odaklı, donma efektleri
- **Şimşek Büyücüsü**: Hızlı saldırılar, elektrik hasarı
- **Karanlık Büyücü**: Gölge saldırıları, karanlık büyüler

### Savaşçılar (4 karakter)
- **Kılıç Ustası**: Dengeli savaşçı, keskin vuruşlar
- **Çift Kılıçlı**: Hızlı saldırılar, çifte vuruş
- **Balta Savaşçısı**: Güçlü vuruşlar, ağır hasar
- **Mızrak Savaşçısı**: Uzun mesafe, savunma odaklı

### Nişancılar (4 karakter)
- **Okçu**: Temel nişancı, hızlı ok atışları
- **Keskin Nişancı**: Uzun mesafe, kritik vuruşlar
- **Çapraz Yay**: Mobil nişancı, çapraz atışlar
- **Tüfekçi**: Hızlı ateş, mermi yağmuru

### Destekler (4 karakter)
- **Şifa Büyücüsü**: İyileştirme, koruyucu kalkanlar
- **Koruyucu**: Savunma odaklı, güçlendirme
- **Kontrol Büyücüsü**: Yavaşlatma, köleleştirme
- **Taktik Uzmanı**: Grup koordinasyonu, strateji

### Tanklar (4 karakter)
- **Demir Dev**: Yüksek savunma, demir yumruk
- **Kaya Savaşçısı**: Taş temalı, sertleşme
- **Zırh Savaşçısı**: Ağır zırh, savunma modu
- **Golem**: En yüksek can, yıkıcı saldırılar

## 🔧 Geliştirme

### Yeni Karakter Ekleme
`characters.lua` dosyasında `Characters.DATA` tablosuna yeni karakter ekleyin:

```lua
{
    name = "Yeni Karakter",
    category = Characters.CATEGORIES.MAGE, -- veya diğer kategoriler
    health = 500,
    mana = 800,
    attack = 60,
    defense = 30,
    speed = 1.2,
    range = 150,
    abilities = {"Yetenek 1", "Yetenek 2", "Yetenek 3"},
    color = {1, 0.3, 0.3} -- RGB renk değerleri
}
```

### Yeni Harita Ekleme
`map.lua` dosyasında `GameMap:setupTowers()` fonksiyonunu düzenleyin.

## 🐛 Bilinen Sorunlar

- Karakterler bazen birbirine takılabilir
- Minion AI basit seviyededir
- Görsel efektler sınırlıdır

## 📝 Lisans

Bu proje eğitim amaçlı geliştirilmiştir. LÖVE2D framework'ü MIT lisansı altındadır.

## 🤝 Katkıda Bulunma

1. Fork yapın
2. Feature branch oluşturun (`git checkout -b feature/yeni-ozellik`)
3. Commit yapın (`git commit -am 'Yeni özellik eklendi'`)
4. Push yapın (`git push origin feature/yeni-ozellik`)
5. Pull Request oluşturun

## 📞 İletişim

Sorularınız için issue açabilir veya iletişime geçebilirsiniz.

---

**Lua Özgür MOBA** - League of Legends benzeri MOBA oyunu 🎮 