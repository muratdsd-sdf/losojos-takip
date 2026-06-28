# Los Ojos · Trendyol Satış Takip

Trendyol'daki **Los Ojos** markasının tüm ürünlerini izleyen, satış adetlerini
(Trendyol'un "son 3 günde X+ sattı" rakamı), favori/sepet/yorum sayılarını toplayan
ve bunları paylaşılabilir bir **web sitesinde** gösteren ücretsiz bir araç.

- **Maliyet:** 0 ₺ (GitHub ücretsiz hesabıyla çalışır)
- **Otomatik:** her gün kendi kendine veri toplar, bilgisayarının açık olması gerekmez
- **Paylaşılabilir:** herkesin açabileceği bir internet linki (arkadaşına da gönderebilirsin)

---

## Dosyalar
| Dosya | Ne işe yarar |
|---|---|
| `index.html` | Web sitesi (panel, tablolar, grafikler) |
| `collector.py` | Veriyi Trendyol'dan toplayan program |
| `data/latest.json` | En güncel veri |
| `data/history.json` | Gün gün biriken arşiv (trend için) |
| `.github/workflows/collect.yml` | Her gün otomatik çalıştıran ayar |

---

## Kurulum (web üzerinden, kod yazmadan)

### 1) GitHub'da depo oluştur
1. https://github.com adresine gir, giriş yap.
2. Sağ üstte **+** → **New repository**.
3. İsim: `losojos-takip` · **Public** seç · **Create repository**.

### 2) Dosyaları yükle
1. Yeni depoda **"uploading an existing file"** linkine tıkla.
2. Bu klasördeki **tüm dosyaları** sürükle bırak (`index.html`, `collector.py`,
   `data` klasörü ve `.github` klasörü dahil).
3. **Commit changes**.

> Not: `.github` klasörü gizli görünebilir; yine de yüklendiğinden emin ol.

### 3) Siteyi yayına al (GitHub Pages)
1. Depoda **Settings** → sol menüde **Pages**.
2. **Source: Deploy from a branch**, **Branch: main / (root)** → **Save**.
3. 1-2 dakika sonra sitenin linki çıkar:
   `https://KULLANICIADIN.github.io/losojos-takip/`
   Bu linki arkadaşınla paylaşabilirsin.

### 4) Otomatik günlük toplamayı aç
1. Depoda **Actions** sekmesine gir, çıkan uyarıda **"I understand… enable"**.
2. Soldan **"Los Ojos veri topla"** → sağda **Run workflow** ile ilk veriyi hemen çekebilirsin.
3. Bundan sonra her gün otomatik çalışır.

---

## Satış rakamları ne kadar doğru?
- **3 günlük satış** = Trendyol'un kendi gösterdiği yaklaşık rakam ("500+", "2B+" gibi).
  Kesin değil, **alt sınırdır** ("+" = en az). Sadece yeterince satan ürünlerde görünür.
- **Haftalık/aylık tahmin**, ürünlerin **yorum sayısı artışından** hesaplanır.
  Bu yüzden program her gün veri biriktirir; birkaç gün sonra tahminler isabetli olur.
- Sitedeki **"yorum→satış oranı"** çubuğuyla tahmini kendine göre ayarlayabilirsin.

## Kendi bilgisayarında çalıştırmak (isteğe bağlı / yedek)
GitHub bulutu Trendyol tarafından engellenirse, programı kendi bilgisayarında çalıştırıp
veriyi GitHub'a yükleyebilirsin:
1. Python kur: https://www.python.org/downloads/ (kurulumda "Add to PATH" işaretle).
2. Bu klasörde komut satırında: `python collector.py`
3. `data` klasöründeki güncellenen dosyaları GitHub'a yükle.

---
*Bu araç yalnızca herkese açık Trendyol verisini okur; giriş/şifre gerektirmez.*
