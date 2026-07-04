# 🧭 PathFinder AI: Akıllı Kariyer & Yol Haritası Planlama Platformu

PathFinder AI, kariyer hedeflerinizi belirlemenizi, adım adım dinamik yol haritaları oluşturmanızı, haftalık çalışma programlarınızı yönetmenizi ve fütüristik bir konsolda mesleğinizi simüle etmenizi sağlayan **OpenAI (`gpt-4o-mini`)** destekli bütünsel bir yapay zeka asistanı ekosistemidir.

---

## 🚀 Öne Çıkan Özellikler

### 1. Dinamik Yol Haritası (Roadmap)
* Girdiğiniz kariyer hedefine (Örn: *Siber Güvenlik Uzmanı*, *AI Engineer*) göre yapay zeka adım adım (en az 5 aşama) bir yol planı çıkarır.
* Her adımın altında detaylı teorik/pratik yapılacaklar listesi (checklist) sunulur.
* Her adıma özel **resmi dokümantasyon linkleri** ve YouTube üzerinden canlı taranıp bulunan **doğrudan video eğitim bağlantıları** enjekte edilir.

### 2. Kariyer Simülasyon Kapsülü (HUD Console)
* Mesleğinizin günlük yaşantısını deneyimleyebileceğiniz fütüristik bir terminal simülatörü.
* OpenAI tarafından üretilen mesleki operasyon adımları, **15 saniyelik dairesel geri sayım** eşliğinde daktilo efektiyle ekrana akar.
* Simülasyon bittiğinde parıltılı efektlerle süslenmiş bir **Kariyer Başarı Sertifikası ve Rozeti** takdim edilir.

### 3. Haftalık Çalışma Takvimi & Hatırlatıcılar
* Yol haritasındaki adımları günlere bölen haftalık çalışma programları.
* **CRUD Desteği:** Görevleri düzenleyebilir, yeni özel görev ekleyebilir veya silebilirsiniz.
* **Alarm / Hatırlatıcı Kurma:** Görevlerinize tarih/saat belirleyerek alarm kurabilirsiniz. Zamanı geldiğinde sesli/görsel slide-in toast bildirimleri ve tarayıcı yerel bildirimleri alırsınız.

### 4. Çoklu Kariyer Uzmanı Ajanları (AI Career Experts)
* 5 farklı uzmanlık alanına (Yazılım, AI & Veri, Tasarım, Pazarlama, Girişimcilik) atanmış yapay zeka mentörleriyle canlı sohbet odaları.

### 5. Canlı Kaynak Önerileri (Deep Links)
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
