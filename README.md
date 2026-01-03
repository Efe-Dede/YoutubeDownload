# YouTube Downloader

Modern, kullanıcı dostu ve özelliklerle dolu bir YouTube video ve ses indirme uygulaması.

## Genel Bakış

YouTube Downloader, YouTube videolarını yüksek kalitede indirmenizi, ses dosyalarına dönüştürmenizi ve indirme geçmişinizi takip etmenizi sağlayan gelişmiş bir masaüstü uygulamasıdır. Yenilenen sekmeli arayüzü ve entegre önizleme sistemi ile kesintisiz bir deneyim sunar.

## Özellikler

### 🌟 Temel Özellikler

- **Çoklu İndirme Yöntemi**: Doğrudan bağlantı ile veya video ismiyle arama yaparak indirme
- **Gelişmiş Kalite Seçenekleri**: 4K'dan standart çözünürlüğe kadar geniş kalite yelpazesi
- **Ses Çıkarma**: Videoları yüksek kaliteli MP3 formatında indirme (320kbps)
- **Kişiselleştirilebilir Konum**: İndirme klasörünü seçme ve hatırlama özelliği

### 🚀 Yeni Özellikler

- **Sekmeli Arayüz**: "İndirici" ve "Geçmiş" sekmeleriyle düzenli görünüm
- **İndirme Geçmişi**: 
  - İndirilen videoları otomatik kaydetme
  - Geçmişten dosya konumuna veya videoya hızlı erişim
  - Geçmişi yönetme ve temizleme
- **Akıllı Önizleme Kartları**: 
  - Pop-up pencereler yerine uygulama içi şık kartlar
  - Video thumbnail, başlık, kanal ve süre bilgisi gösterimi
  - İndirme öncesi/sonrası aksiyon butonları

### 🎨 Kullanıcı Arayüzü

- Modern ve minimalist karanlık tema (Dark Mode)
- Büyük ve okunaklı fontlar
- Salt okunur kalite seçim menüsü (Hatalı girişleri önler)
- Gerçek zamanlı ilerleme çubuğu ve hız göstergesi
- Başarılı işlem sonrası sesli ve görsel bildirimler

## Sistem Gereksinimleri

### Minimum Gereksinimler

- **İşletim Sistemi**: Windows 10 veya üzeri
- **RAM**: 4 GB
- **Disk Alanı**: 100 MB + İndirilen dosyalar için alan
- **İnternet**: Aktif internet bağlantısı

### Gerekli Yazılımlar

- **FFmpeg**: Video ve ses işleme için gereklidir
  - `C:/ffmpeg/bin` konumunda kurulu olmalı veya sistem PATH'ine eklenmelidir.

## Kurulum ve Çalıştırma

### Hazır EXE Kullanımı (Önerilen)

1. `dist` klasöründeki `Youtube Downloader.exe` dosyasını çalıştırın.
2. FFmpeg'in kurulu olduğundan emin olun.

### Kaynak Koddan Çalıştırma

1. Depoyu klonlayın:
```bash
git clone <repository-url>
cd "Youtube MP3"
```

2. Gerekli kütüphaneleri yükleyin:
```bash
pip install -r requirements.txt
```

3. Uygulamayı başlatın:
```bash
python main.py
```

## Kullanım Kılavuzu

### 1. Video İndirme (İndirici Sekmesi)

1. **Konum Seçimi**: İlk kullanımda "Gözat" butonu ile indirme klasörünü seçin (Otomatik kaydedilir).
2. **Video Seçimi**: 
   - YouTube linkini yapıştırın VEYA
   - Video ismini yazarak arama yapın.
3. **Kalite**: Listeden istediğiniz kaliteyi seçin (4K, 1080p, MP3 vb.).
4. **Başlat**: "İndirmeyi Başlat" butonuna tıklayın.
5. **Önizleme ve Onay**: 
   - Alt kısımda beliren karttan videoyu kontrol edin.
   - "✓ İndir" butonuna basarak işlemi başlatın.
6. **Tamamlanma**: İşlem bitince "Dosyayı Göster" diyerek klasöre gidebilirsiniz.

### 2. Geçmiş Yönetimi (Geçmiş Sekmesi)

- **Listeleme**: "Geçmiş" sekmesine geçerek önceki indirmelerinizi görebilirsiniz.
- **Hızlı Erişim**:
  - 📂 simgesi: Dosyanın bilgisayardaki konumunu açar.
  - 🔗 simgesi: Videoyu tarayıcıda açar.
- **Silme**: ✕ simgesi ile kaydı listeden silebilirsiniz (Dosya silinmez).
- **Temizleme**: "Geçmişi Temizle" butonu ile tüm listeyi sıfırlayabilirsiniz.

## Teknik Detaylar

### Mimari
Uygulama Python ile geliştirilmiş olup aşağıdaki teknolojileri kullanır:
- **GUI**: CustomTkinter (Modern Tkinter wrapper)
- **Motor**: yt-dlp (İndirme işlemleri)
- **Medya**: FFmpeg (Dönüştürme ve birleştirme)
- **Veri**: JSON (Ayarlar ve geçmiş veritabanı)

### Dosya Yapısı
- `.youtube_downloader_settings.json`: Kullanıcı ayarları (Kayıt konumu)
- `.youtube_downloader_history.json`: İndirme geçmişi veritabanı

## Sorun Giderme

**Video İnmiyor / Hata Veriyor**
- İnternet bağlantınızı kontrol edin.
- FFmpeg'in `C:/ffmpeg/bin` konumunda olduğundan emin olun.
- Virüs programının uygulamayı engellemediğini kontrol edin.

**Görüntü Bozuk / Yazılar Siliniyor**
- Uygulama son güncelleme ile "readonly" moduna geçmiştir, sorun çözülmüştür.
- Sorun devam ederse ekran ölçeklendirme ayarlarınızı kontrol edin.

## Lisans
Bu proje açık kaynak kodludur. Eğitim amaçlı geliştirilmiştir.

---
**Geliştirici Notu**: Bu uygulama "Uygulama İçi Akış" (In-App Flow) prensibiyle tasarlanmıştır. Kullanıcıyı rahatsız eden pop-up pencereler yerine modern kart yapıları tercih edilmiştir.
