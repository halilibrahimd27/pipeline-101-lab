# Pipeline Security 101 — LAB

Bu repoda küçük bir Node.js uygulaması ve onu test eden bir **pipeline** var.
Pipeline çalışıyor, testler geçiyor, her şey yolunda görünüyor.

Görünüyor. Çünkü içine **bilerek 5 tane güvenlik hatası** koyduk.

Senin işin onları bulup düzeltmek. Hiçbir şey kurman gerekmiyor —
her şeyi tarayıcıdan, GitHub'ın kendi editöründen yapacaksın.

---

## Başlamadan önce (3 dakika)

**1. Kendi kopyanı oluştur**

Bu sayfanın üstündeki yeşil **`Use this template`** düğmesine bas →
**`Create a new repository`** seç → bir isim ver (örneğin `pipeline-lab`) →
**`Create repository`**.

> Dikkat: `Fork` değil, `Use this template`. Fork edilen repolarda
> otomatik kontrol çalışmaz.

**2. Actions'ı aç**

Yeni repondaki **`Actions`** sekmesine gir. Bir uyarı çıkarsa
**`I understand my workflows, go ahead and enable them`** de.

**3. Karneyi bul**

`Actions` sekmesinde soldaki listeden **`kontrol`** iş akışını seç,
en üstteki çalışmaya tıkla ve **`Summary`** ekranına bak.

Şöyle bir tablo göreceksin:

```
░░░░░  0 / 5
```

**Hedefin bu tabloyu 5/5 yapmak.** Her düzeltmeden sonra karne
kendiliğinden yenilenir.

---

## Dosya nasıl düzenlenir

Bunu 5 kez yapacaksın, bir kere öğrenmen yeterli:

1. Dosyaya tıkla
2. Sağ üstteki **kalem** ikonuna bas
3. Değişikliği yap
4. Sağ üstteki **`Commit changes...`** → **`Commit changes`**

Dosya silmek için kalem yerine **çöp kutusu** ikonunu kullan.

---

# GÖREVLER

## Görev 1 — Secret temizliği

**Sorun:** Repoda `.env` diye bir dosya var. İçinde bir API anahtarı ve bir
veritabanı parolası duruyor. Ayrıca `src/config.js` dosyasında da aynı anahtar
"yedek değer" olarak yazılı.

Bu dosyaları herkes görebilir. GitHub'ı tarayan botlar bu tür anahtarları
saniyeler içinde buluyor.

**Yapacakların:**

- `.env` dosyasını **sil**
- `.gitignore` dosyasını aç, en alta `.env` satırını **ekle**
  (böylece bir daha yanlışlıkla eklenmez)
- `src/config.js` içindeki gömülü anahtarı **kaldır**:

```js
// önce
apiKey: process.env.API_KEY || "sk_live_...",

// sonra
apiKey: process.env.API_KEY,
```

> Not: gerçek hayatta bu yetmez. Anahtar geçmişte kaldığı için **iptal edilip
> yenisi üretilmelidir**. Bu lab'da geçmişi temizlemene gerek yok.

---

## Görev 2 — İzni kıs

**Sorun:** `.github/workflows/ci.yml` dosyasında hiç izin tanımı yok. Bu durumda
pipeline'a gereğinden fazla yetki verilebiliyor. Oysa bu pipeline sadece test
çalıştırıyor — repoya yazmasına gerek yok.

**Yapacakların:** `ci.yml` dosyasını aç, `on:` bloğunun altına, `jobs:`
satırından **önce** şunu ekle:

```yaml
permissions:
  contents: read
```

---

## Görev 3 — Kurulumu düzelt

**Sorun:** `ci.yml` içinde `npm install` kullanılıyor. Bu komut, kilit dosyasını
(`package-lock.json`) görmezden gelip farklı sürümler kurabilir. Yani senin test
ettiğin kod ile pipeline'ın kurduğu kod aynı olmayabilir.

**Yapacakların:** `Paketleri kur` adımındaki satırı değiştir:

```yaml
# önce
run: npm install

# sonra
run: npm ci
```

---

## Görev 4 — Action'ları sabitle

**Sorun:** `ci.yml` içinde iki tane hazır adım var:

```yaml
- uses: actions/checkout@v4
- uses: actions/setup-node@v4
```

`@v4` bir sürüm değil, bir **etiket**. Etiketin gösterdiği kod sonradan
değiştirilebilir — ve o kod senin pipeline'ında çalışır.

**Yapacakların:** Etiket yerine değişmeyen **commit numarasını** (SHA) yaz.

Numarayı şöyle bulacaksın:

1. Yeni bir sekmede `github.com/actions/checkout` adresini aç
2. Sağ taraftaki **`Releases`** bölümünden en güncel `v4` sürümüne tıkla
3. Sürüm başlığının altındaki **commit numarasına** tıkla
4. Açılan sayfada sağ üstteki **`Copy full SHA`** düğmesine bas

Sonra `ci.yml` dosyasında şu hale getir:

```yaml
- uses: actions/checkout@<yapistirdigin-40-karakter>   # v4.x.x
- uses: actions/setup-node@<yapistirdigin-40-karakter> # v4.x.x
```

Aynı işlemi `actions/setup-node` için de tekrarla.

> Yanına sürüm numarasını yorum olarak bırak — altı ay sonra o numaranın
> hangi sürüm olduğunu hatırlamak istersin.
>
> Numarayı yanlış yazarsan `ci` iş akışı kırmızı olur. Sorun değil, karneyi
> basan `kontrol` iş akışı yine çalışır.

---

## Görev 5 — Girdiyi ayır

**Sorun:** `ci.yml` dosyasının en altındaki adım şöyle:

```yaml
- name: Son commit mesajini logla
  run: echo "Son commit -> ${{ github.event.head_commit.message }}"
```

`${{ ... }}` ifadesi, komut çalışmadan **önce** metin olarak yerine yazılır.
Commit mesajını sen yazıyorsun — ama bir başkası da yazabilir. İçine tırnak ve
noktalı virgül koyan biri, oraya kendi komutunu yazdırabilir.

**Yapacakların:** Değeri önce bir değişkene al, sonra o değişkeni kullan:

```yaml
- name: Son commit mesajini logla
  env:
    MESAJ: ${{ github.event.head_commit.message }}
  run: echo "Son commit -> $MESAJ"
```

Fark şurada: değişkenin **içeriği** komut olarak yorumlanmaz.

> Adımı silmek çözüm değil — karne bunu kabul etmez.

---

## Bonus — Tarama ekle

Karne için şart değil, ama bir yıldız kazandırır.

`ci.yml` dosyasına, testlerden sonra bir tarama adımı ekle:

```yaml
- name: Bagimlilik taramasi
  run: |
    curl -sSfL -o osv-scanner \
      https://github.com/google/osv-scanner/releases/latest/download/osv-scanner_linux_amd64
    chmod +x osv-scanner
    ./osv-scanner scan source -r . || true
```

Sonundaki `|| true` şu anlama geliyor: "bulgu varsa göster ama pipeline'ı
kırma". Yeni bir taramayı ekibe tanıtırken ilk hafta böyle başlanır.

Çalıştırınca bu projedeki `lodash` paketinin eski bir sürümü olduğunu ve
bilinen açıkları bulunduğunu göreceksin. O da bilerek konuldu.

---

## Takıldıysan

- Karne güncellenmiyorsa: `Actions` → `kontrol` → en üstteki çalışma → `Summary`
- Karnedeki her satır, neyin eksik olduğunu yazıyor. Önce onu oku.
- YAML boşluklara duyarlıdır. Girintiyi bozmadığından emin ol.
- `ci` kırmızı ama `kontrol` yeşilse sorun yok — görevler tamamlanmış demektir.
