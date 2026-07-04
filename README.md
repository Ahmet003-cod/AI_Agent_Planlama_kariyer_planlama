# 🛡️ CyberShield AI: Siber Güvenlik Kariyer & Uzmanlık Planlama Platformu

CyberShield AI, siber güvenlik alanında hedeflerinizi belirlemenizi, adım adım özelleştirilmiş siber yol haritaları oluşturmanızı, haftalık çalışma programlarınızı yönetmenizi ve fütüristik bir terminal arayüzünde siber operasyonları simüle etmenizi sağlayan **OpenAI (`gpt-4o-mini`)** destekli bütünsel bir yapay zeka asistanı ekosistemidir.

---

## 🚀 Öne Çıkan Siber Özellikler

### 1. Siber Güvenlik Yol Haritası (Roadmap)
* Girdiğiniz uzmanlık rolüne (Örn: *Sızma Testi Uzmanı (Pentester)*, *SOC Analisti (Blue Team)*, *Zararlı Yazılım Analisti*) göre yapay zeka adım adım (en az 5 aşama) bir yol planı çıkarır.
* Her adımın altında detaylı teorik/pratik yapılacaklar listesi (checklist) sunulur.
* Her adıma özel **resmi dokümantasyon linkleri** ve YouTube üzerinden canlı taranıp bulunan **doğrudan video eğitim bağlantıları** enjekte edilir.

### 2. Siber Operasyon Simülatörü (SOC HUD Console)
* Seçtiğiniz uzmanlık rolünün günlük operasyonlarını deneyimleyebileceğiniz fütüristik bir terminal simülatörü.
* OpenAI tarafından üretilen siber operasyon adımları, **15 saniyelik dairesel geri sayım** eşliğinde daktilo efektiyle ekrana akar.
* Simülasyon bittiğinde parıltılı efektlerle süslenmiş bir **Siber Güvenlik Başarı Rozeti ve Sertifikası** takdim edilir.

### 3. Çalışma Takvimi & Hatırlatıcılar (CRUD)
* Yol haritasındaki adımları günlere bölen haftalık çalışma programları.
* **CRUD Desteği:** Görevleri düzenleyebilir, yeni özel görev ekleyebilir veya silebilirsiniz.
* **Alarm / Hatırlatıcı Kurma:** Görevlerinize tarih/saat belirleyerek alarm kurabilirsiniz. Zamanı geldiğinde sesli/görsel slide-in toast bildirimleri ve tarayıcı yerel bildirimleri alırsınız.

### 4. Siber Güvenlik Ajanları (AI Security Experts)
* 5 farklı uzmanlık alanına (Offensive Security, Defensive Security, Zararlı Yazılım & Adli Bilişim, GRC, Bulut Güvenliği) atanmış yapay zeka mentörleriyle canlı sohbet odaları.

### 5. Canlı Siber Kaynak Önerileri (Deep Links)
* Seçtiğiniz konuya yönelik Udemy, YouTube ve GitHub üzerindeki doğrudan ve çalışan en güncel eğitim kaynakları OpenAI tarafından canlı olarak derlenerek listelenir.

---

## 🛠️ Kurulum ve Çalıştırma

### 1. Gereksinimler
* Bilgisayarınızda Python 3.8 veya üzeri bir sürümün yüklü ve çevre değişkenlerine (PATH) ekli olduğundan emin olun.

### 2. Kolay Başlatıcı Scripti (Önerilen)
Windows kullanıyorsanız, proje klasöründeki [run.bat](run.bat) dosyasına çift tıklayarak sistemi otomatik başlatabilirsiniz. Script sırasıyla şunları yapacaktır:
1. Gerekli sanal ortamı (`venv`) oluşturur ve aktif eder.
2. Tüm Python kütüphanelerini (`requriments.txt`) otomatik yükler.
3. `.env` dosyası eksikse `.env_example` şablonunu kopyalar.
4. Sunucuyu ayağa kaldırarak tarayıcınızda açılmaya hazır hale getirir.

### 3. Manuel Kurulum
1. Sanal ortam oluşturun ve aktif edin:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows için: venv\Scripts\activate
   ```
2. Bağımlılıkları yükleyin:
   ```bash
   pip install -r requriments.txt
   ```
3. `.env_example` dosyasını `.env` olarak kopyalayıp içerisine kendi **OpenAI API Key** anahtarınızı ekleyin:
   ```env
   OPENAI_API_KEY=sk-proj-your-api-key-here
   ```
4. Flask uygulamasını çalıştırın:
   ```bash
   python main.py
   ```
5. Tarayıcınızdan açın: `http://127.0.0.1:5000`

---

## 📂 Proje Yapısı

```text
├── agents/                  # Yapay zeka ajanları (yol haritası, takvim planlama, kariyer uzmanı)
├── tools/                   # YouTube arama, kaynak öneri ve web arama araçları
├── memorys/                 # Kullanıcı profil ve ilerleme durum belleği
├── templates/               # HTML arayüz tasarımları
├── static/                  # CSS stilleri ve JS uygulama mantığı
├── main.py                  # Flask backend API sunucusu
├── .env_example             # Çevre değişkenleri şablonu
├── .gitignore               # Git dışı bırakma listesi
├── run.bat                  # Kolay çalıştırma scripti
└── README.md                # Proje tanıtım dosyası
```
