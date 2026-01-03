# YouTube Downloader

Modern ve kullanıcı dostu bir YouTube video ve ses indirme uygulaması.

## Genel Bakış

YouTube Downloader, YouTube videolarını çeşitli kalite seçenekleriyle indirmenize veya MP3 formatında ses dosyalarına dönüştürmenize olanak tanıyan bir masaüstü uygulamasıdır. Minimalist ve zarif arayüzü ile kullanımı son derece kolaydır.

## Özellikler

### Temel Özellikler

- **Çoklu İndirme Yöntemi**: Doğrudan YouTube bağlantısı veya video adı ile arama yaparak indirme
- **Gelişmiş Kalite Seçenekleri**: 4K'dan standart çözünürlüğe kadar geniş kalite yelpazesi
- **Ses Çıkarma**: Videoları yüksek kaliteli MP3 formatında indirme (320kbps)
- **Akıllı Arama**: Video adı ile arama yapıldığında sonuçları önizleme ve onaylama
- **Gerçek Zamanlı İlerleme**: İndirme sürecini detaylı olarak takip etme
- **Bildirim Sistemi**: İndirme tamamlandığında sistem bildirimi

### Kalite Seçenekleri

- **Otomatik (1080p)**: Optimal kalite ve dosya boyutu dengesi
- **2160p 4K**: Ultra yüksek çözünürlük
- **1440p 2K**: Yüksek çözünürlük
- **1080p FHD**: Full HD kalite
- **720p HD**: HD kalite
- **480p SD**: Standart kalite
- **MP3 Sadece Ses**: Yalnızca ses dosyası (320kbps)

### Kullanıcı Arayüzü

- Modern ve minimalist tasarım
- Koyu tema ile göz dostu görünüm
- Sezgisel kontroller
- Gerçek zamanlı durum güncellemeleri
- İlerleme çubuğu ve hız göstergesi

## Sistem Gereksinimleri

### Minimum Gereksinimler

- **İşletim Sistemi**: Windows 10 veya üzeri
- **RAM**: 4 GB
- **Disk Alanı**: 100 MB (uygulama için) + indirilen dosyalar için ek alan
- **İnternet Bağlantısı**: Aktif internet bağlantısı gereklidir

### Gerekli Yazılımlar

- **FFmpeg**: Video ve ses işleme için gereklidir
  - FFmpeg'in `C:/ffmpeg/bin` konumunda kurulu olması gerekmektedir
  - Alternatif olarak, sistem PATH değişkenine eklenmiş olmalıdır

## Kurulum

### Kaynak Koddan Kurulum

1. Depoyu klonlayın:
```bash
git clone <repository-url>
cd "Youtube MP3"
```

2. Gerekli Python paketlerini yükleyin:
```bash
pip install -r requirements.txt
```

3. FFmpeg'i kurun:
   - [FFmpeg resmi sitesinden](https://ffmpeg.org/download.html) indirin
   - `C:/ffmpeg/bin` konumuna çıkarın veya sistem PATH'ine ekleyin

4. Uygulamayı çalıştırın:
```bash
python main.py
```

### Bağımlılıklar

Uygulama aşağıdaki Python kütüphanelerini kullanır:

- **yt-dlp**: YouTube video indirme motoru
- **customtkinter**: Modern GUI framework
- **ffmpeg-python**: Video/ses işleme
- **plyer**: Sistem bildirimleri

## Kullanım

### Temel Kullanım

1. **Uygulamayı Başlatın**: `main.py` dosyasını çalıştırın veya derlenmiş uygulamayı açın

2. **Video Seçimi**:
   - **Yöntem 1**: YouTube video bağlantısını kopyalayıp giriş alanına yapıştırın
   - **Yöntem 2**: Video adını yazarak arama yapın

3. **Kalite Seçimi**: Açılır menüden istediğiniz kalite veya format seçeneğini belirleyin

4. **İndirme**: "İndirmeyi Başlat" butonuna tıklayın

5. **Onaylama** (arama ile indirme yapıldığında):
   - Bulunan video bilgileri gösterilecektir
   - Video başlığı, kanal adı ve süre bilgilerini kontrol edin
   - Onaylamak için "Evet" butonuna tıklayın

6. **İlerleme Takibi**: İndirme sürecini ilerleme çubuğu ve durum mesajları ile takip edin

### İndirilen Dosyalar

Tüm indirilen dosyalar varsayılan olarak kullanıcının **İndirilenler** klasörüne kaydedilir:
- Windows: `C:\Users\<KullanıcıAdı>\Downloads`

Dosya adı, videonun orijinal başlığı ile otomatik olarak belirlenir.

## Arayüz Özellikleri

### Ana Bileşenler

- **Başlık Alanı**: Uygulama adı ve logo
- **Giriş Alanı**: URL veya arama terimi girişi
- **Kalite Seçici**: Video/ses kalitesi seçimi
- **İndirme Butonu**: İndirme işlemini başlatma
- **Durum Göstergesi**: Mevcut işlem durumu
- **İlerleme Çubuğu**: İndirme ilerlemesi ve hız bilgisi

### Durum Mesajları

- **Hazır**: "İndirme yapmak için hazırım"
- **Analiz**: "Analiz ediliyor..." / "Bağlantı analiz ediliyor..."
- **Arama**: "YouTube'da aranıyor..."
- **İndirme**: "%XX.X • XX MB/s"
- **Dönüştürme**: "Dönüştürme işlemi yapılıyor..."
- **Tamamlandı**: "İndirme Tamamlandı!"
- **Hata**: "Hata Oluştu"

## Teknik Detaylar

### Mimari

Uygulama, aşağıdaki temel bileşenlerden oluşur:

- **GUI Katmanı**: CustomTkinter tabanlı modern arayüz
- **İndirme Motoru**: yt-dlp kütüphanesi
- **Medya İşleme**: FFmpeg entegrasyonu
- **Thread Yönetimi**: Asenkron indirme işlemleri
- **Bildirim Sistemi**: Plyer ve Windows API entegrasyonu

### Format Seçimi

Uygulama, seçilen kaliteye göre en uygun video ve ses formatlarını otomatik olarak belirler:

- **Video İndirme**: MP4 konteyner formatında video + ses birleştirmesi
- **Ses İndirme**: MP3 formatında 320kbps kalitede ses çıkarma

### Arama Özelliği

Video adı ile arama yapıldığında:

1. YouTube'da arama sorgusu çalıştırılır
2. En alakalı sonuç bulunur
3. Video bilgileri (başlık, kanal, süre) kullanıcıya gösterilir
4. Kullanıcı onayı alındıktan sonra indirme başlatılır

## Sorun Giderme

### Sık Karşılaşılan Sorunlar

**FFmpeg Bulunamadı Hatası**
- FFmpeg'in doğru konumda kurulu olduğundan emin olun
- `C:/ffmpeg/bin` yolunu kontrol edin
- Alternatif olarak FFmpeg'i sistem PATH'ine ekleyin

**İndirme Başlamıyor**
- İnternet bağlantınızı kontrol edin
- YouTube bağlantısının geçerli olduğundan emin olun
- Firewall veya antivirüs yazılımınızın uygulamayı engellemediğini kontrol edin

**Kalite Seçeneği Bulunamadı**
- Seçilen kalite videoda mevcut olmayabilir
- "Otomatik" seçeneğini deneyin
- Daha düşük bir kalite seçeneği seçin

**Bildirim Çalışmıyor**
- Windows bildirim ayarlarınızı kontrol edin
- Uygulama izinlerini kontrol edin

### Hata Raporlama

Bir hata ile karşılaşırsanız:

1. Hata mesajını not edin
2. Hatayı yeniden oluşturmak için adımları kaydedin
3. Sistem bilgilerinizi (Windows sürümü, Python sürümü) toplayın
4. Proje deposunda bir issue açın

## Geliştirme

### Proje Yapısı

```
Youtube MP3/
├── main.py                 # Ana uygulama dosyası
├── requirements.txt        # Python bağımlılıkları
├── icon.ico               # Uygulama ikonu
├── YoutubeDownloader.spec # PyInstaller yapılandırması
├── .gitignore            # Git ignore kuralları
├── assets/               # Görsel varlıklar
├── build/                # Derleme dosyaları
├── dist/                 # Dağıtım dosyaları
└── downloads/            # Geçici indirme klasörü
```

### Kod Yapısı

**YoutubeDownloaderApp Sınıfı**:
- `__init__()`: GUI başlatma ve yapılandırma
- `is_youtube_url()`: URL doğrulama
- `search_and_confirm()`: Video arama ve onaylama
- `start_download_thread()`: İndirme thread'i başlatma
- `download_core()`: Ana indirme mantığı
- `progress_hook()`: İlerleme güncellemeleri
- `download_done()`: İndirme tamamlanma işlemleri

### Tema Yapılandırması

Uygulama renk teması `THEME` sözlüğünde tanımlanmıştır:

- **bg**: Ana arka plan rengi (#0B0E14)
- **accent**: Vurgu rengi (#0095FF)
- **accent_sub**: İkincil vurgu rengi (#0077CC)
- **text_main**: Ana metin rengi (#E1E7EF)
- **text_dim**: Soluk metin rengi (#718096)
- **success**: Başarı rengi (#22C55E)
- **error**: Hata rengi (#EF4444)
- **input_bg**: Giriş alanı arka planı (#151921)
- **button_dark**: Koyu buton rengi (#1E232E)

## Lisans

Bu proje açık kaynak kodludur ve ilgili lisans koşulları altında dağıtılmaktadır.

## Katkıda Bulunma

Projeye katkıda bulunmak isterseniz:

1. Projeyi fork edin
2. Yeni bir branch oluşturun (`git checkout -b feature/yeniOzellik`)
3. Değişikliklerinizi commit edin (`git commit -m 'Yeni özellik eklendi'`)
4. Branch'inizi push edin (`git push origin feature/yeniOzellik`)
5. Pull Request oluşturun

## İletişim

Sorularınız veya önerileriniz için proje deposunda bir issue açabilirsiniz.

## Teşekkürler

Bu proje aşağıdaki açık kaynak projeleri kullanmaktadır:

- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - YouTube indirme motoru
- [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) - Modern GUI framework
- [FFmpeg](https://ffmpeg.org/) - Multimedya işleme
- [Plyer](https://github.com/kivy/plyer) - Platform bağımsız bildirimler

---

**Not**: Bu uygulama yalnızca eğitim amaçlıdır. İndirdiğiniz içeriklerin telif hakkı yasalarına uygun olduğundan emin olun.
