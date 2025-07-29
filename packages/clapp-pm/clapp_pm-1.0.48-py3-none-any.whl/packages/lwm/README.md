# LWM - Lua Window Manager

Modern ve profesyonel görünümlü Lua tabanlı pencere yöneticisi.

## 🚀 Özellikler

### 🎨 Modern Tasarım
- Koyu tema (Dark Theme)
- Yuvarlatılmış köşeler
- Gradient efektleri
- Gölge efektleri
- Blur efektleri

### 📱 Gelişmiş Widget'lar
- **CPU Kullanımı**: Gerçek zamanlı CPU monitörü
- **RAM Kullanımı**: Bellek kullanım takibi
- **Sıcaklık**: Sistem sıcaklığı monitörü
- **Ağ**: İndirme/yükleme hızı
- **Ses**: Ses seviyesi kontrolü
- **Pil**: Pil durumu ve şarj seviyesi
- **Hava Durumu**: Gerçek zamanlı hava durumu
- **Takvim**: Takvim widget'ı
- **Müzik**: Müzik çalar kontrolü
- **E-posta**: E-posta bildirim sayacı
- **Sistem Bilgisi**: Çalışma süresi
- **Çalışma Alanı**: Aktif çalışma alanı göstergesi
- **Hızlı Başlat**: Popüler uygulamalar
- **Bildirim Merkezi**: Bildirim sayacı

### ⌨️ Klavye Kısayolları

#### Genel Kısayollar
- `Super + S`: Yardım menüsü
- `Super + Left/Right`: Önceki/sonraki tag
- `Super + Escape`: Tag geçmişini geri yükle
- `Super + J/K`: Sonraki/önceki pencere
- `Super + W`: Ana menü
- `Super + Tab`: Önceki pencere

#### Pencere Yönetimi
- `Super + Shift + J/K`: Pencereyi aşağı/yukarı taşı
- `Super + Ctrl + J/K`: Sonraki/önceki ekran
- `Super + U`: Acil pencereye git
- `Super + F`: Tam ekran
- `Super + Shift + C`: Pencereyi kapat
- `Super + Ctrl + Space`: Yüzen pencere yap
- `Super + Ctrl + Enter`: Master pencere yap
- `Super + O`: Pencereyi başka ekrana taşı
- `Super + T`: Her zaman üstte
- `Super + N`: Minimize et
- `Super + M`: Maksimize et

#### Layout Yönetimi
- `Super + L/H`: Pencere boyutunu artır/azalt
- `Super + Shift + H/L`: Master alanını artır/azalt
- `Super + Ctrl + H/L`: Sütun sayısını artır/azalt
- `Super + Space`: Sonraki layout
- `Super + Shift + Space`: Önceki layout

#### Sistem
- `Super + Enter`: Terminal aç
- `Super + Ctrl + R`: Awesome yeniden başlat
- `Super + Shift + Q`: Awesome kapat
- `Super + R`: Komut çalıştır
- `Super + X`: Lua kodu çalıştır
- `Super + P`: Menü çubuğunu göster

#### Tag Yönetimi
- `Super + 1-9`: Tag'e geç
- `Super + Ctrl + 1-9`: Tag'i göster/gizle
- `Super + Shift + 1-9`: Pencereyi tag'e taşı
- `Super + Ctrl + Shift + 1-9`: Pencereyi tag'e ekle/çıkar

### 🎯 Layout'lar
- **Floating**: Yüzen pencereler
- **Tile**: Döşeme düzeni
- **Tile Left**: Sol döşeme
- **Tile Bottom**: Alt döşeme
- **Tile Top**: Üst döşeme
- **Fair**: Adil düzen
- **Fair Horizontal**: Yatay adil düzen
- **Spiral**: Spiral düzen
- **Dwindle**: Küçülen spiral
- **Max**: Maksimize
- **Fullscreen**: Tam ekran
- **Magnifier**: Büyüteç
- **Corner NW**: Köşe düzeni

## 📦 Kurulum

### Gereksinimler
- AwesomeWM 4.3+
- Lua 5.4+
- X11
- Vicious (widget'lar için)
- Playerctl (müzik kontrolü için)
- Alacritty (terminal)
- JetBrains Mono font

### Ubuntu/Debian Kurulumu
```bash
# AwesomeWM kurulumu
sudo apt update
sudo apt install awesome awesome-extra

# Gerekli paketler
sudo apt install lua5.4 lua5.4-dev
sudo apt install vicious
sudo apt install playerctl
sudo apt install alacritty
sudo apt install fonts-jetbrains-mono

# Font kurulumu
sudo apt install fonts-jetbrains-mono
```

### Arch Linux Kurulumu
```bash
# AwesomeWM kurulumu
sudo pacman -S awesome vicious playerctl alacritty ttf-jetbrains-mono
```

### Fedora Kurulumu
```bash
# AwesomeWM kurulumu
sudo dnf install awesome vicious playerctl alacritty jetbrains-mono-fonts
```

### LWM Kurulumu
```bash
# LWM'yi klonla
git clone https://github.com/kullanici/lwm.git
cd lwm

# Konfigürasyon dosyalarını kopyala
cp -r * ~/.config/awesome/

# AwesomeWM'yi yeniden başlat
awesome --replace
```

## ⚙️ Konfigürasyon

### Ana Konfigürasyon
Ana konfigürasyon dosyası `main.lua`'dır. Bu dosyada:
- Klavye kısayolları
- Mouse butonları
- Pencere kuralları
- Layout ayarları

### Tema Konfigürasyonu
Tema ayarları `theme.lua` dosyasında bulunur:
- Renk paleti
- Font ayarları
- Widget renkleri
- Efekt ayarları

### Widget Konfigürasyonu
Widget'lar `widgets.lua` dosyasında tanımlanmıştır:
- Sistem monitörleri
- Medya kontrolleri
- Hava durumu
- Takvim

## 🎨 Tema Özelleştirme

### Renk Paleti Değiştirme
`theme.lua` dosyasında renkleri değiştirebilirsiniz:

```lua
-- Ana renkler
theme.bg_normal = "#1a1a1a"  -- Arka plan
theme.fg_normal = "#ffffff"  -- Ön plan
theme.border_focus = "#00ff88"  -- Odaklanmış kenarlık
```

### Font Değiştirme
```lua
theme.font = "JetBrains Mono 10"  -- Ana font
theme.font_bold = "JetBrains Mono Bold 10"  -- Kalın font
```

### Widget Renkleri
```lua
theme.widget_cpu_bg = "#00ff88"  -- CPU widget arka planı
theme.widget_cpu_fg = "#000000"  -- CPU widget ön planı
```

## 🔧 Gelişmiş Özellikler

### Özel Widget Ekleme
Yeni widget eklemek için `widgets.lua` dosyasına fonksiyon ekleyin:

```lua
function widgets.create_custom_widget()
    local custom_widget = wibox.widget.textbox()
    -- Widget mantığı
    return custom_widget
end
```

### Özel Kısayol Ekleme
`main.lua` dosyasında `globalkeys` tablosuna ekleyin:

```lua
awful.key({ modkey }, "key", function()
    -- Fonksiyon
end, {description = "açıklama", group = "grup"})
```

### Özel Layout Ekleme
```lua
-- Layout'u layouts listesine ekle
awful.layout.layouts = {
    awful.layout.suit.floating,
    -- Yeni layout
}
```

## 🐛 Sorun Giderme

### Widget'lar Çalışmıyor
- Vicious paketinin kurulu olduğundan emin olun
- Lua sürümünü kontrol edin
- Hata mesajlarını kontrol edin

### Font Sorunları
```bash
# Font cache'ini yenile
fc-cache -fv

# Font listesini kontrol et
fc-list | grep JetBrains
```

### Performans Sorunları
- Widget güncelleme sıklığını azaltın
- Gereksiz widget'ları devre dışı bırakın
- Compositor ayarlarını kontrol edin

## 📝 Katkıda Bulunma

1. Fork yapın
2. Feature branch oluşturun (`git checkout -b feature/yeni-ozellik`)
3. Commit yapın (`git commit -am 'Yeni özellik eklendi'`)
4. Branch'i push edin (`git push origin feature/yeni-ozellik`)
5. Pull Request oluşturun

## 📄 Lisans

Bu proje MIT lisansı altında lisanslanmıştır. Detaylar için `LICENSE` dosyasına bakın.

## 🙏 Teşekkürler

- [AwesomeWM](https://awesomewm.org/) - Temel pencere yöneticisi
- [Vicious](https://github.com/vicious-widgets/vicious) - Widget kütüphanesi
- [JetBrains](https://www.jetbrains.com/) - Font desteği

## 📞 İletişim

- GitHub: [@kullanici](https://github.com/kullanici)
- E-posta: kullanici@example.com
- Twitter: [@kullanici](https://twitter.com/kullanici)

---

**LWM** - Modern ve profesyonel Lua pencere yöneticisi 🚀 