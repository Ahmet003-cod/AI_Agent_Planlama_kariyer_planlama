# 🧭 PathFinder AI: Akıllı Kariyer & Yol Haritası Planlama Asistanı

PathFinder AI; yazılımdan tasarıma, yapay zekadan siber güvenliğe kadar dilediğiniz herhangi bir kariyer alanında hedeflerinizi belirlemenizi, bu hedeflere yönelik yapay zeka destekli ders programları çıkarmanızı, AI mentörlerle sohbet etmenizi ve 15 saniyelik fütüristik bir log terminalinde meslek simülasyonunu deneyimlemenizi sağlayan Flask tabanlı bir kariyer planlama uygulamasıdır.

---

## 🔒 Güvenlik Vurgusu (Code Security)

Bu proje güvenli kodlama standartları ve veri gizliliği esas alınarak geliştirilmiştir:
1. **API Anahtarı Güvenliği:** OpenAI API anahtarınız kesinlikle kod içerisinde barındırılmaz. `.gitignore` ve `.env` mekanizması kullanılarak kaynak koddan tamamen izole tutulur.
2. **Yerel Veri Depolama (Local Privacy):** Yol haritaları, tamamlanma durumları, haftalık ders planları ve chat geçmişleri hiçbir harici bulut sunucusuna gönderilmez; tamamen kullanıcının kendi yerel bilgisayarında (`data/user_profile.json` altında) izole şekilde saklanır.
3. **Doğrudan Güvenli Bağlantılar (Strict Links):** Kaynak önerilerinde open-redirect (açık yönlendirme) açığı oluşturabilecek arama motoru yönlendirme linkleri temizlenmiştir. Tüm video ve dokümanlar doğrudan `https` protokolüne sahip resmi adreslere gider.

---

## ⚙️ Projede Bulunan Özellikler (Mevcut Fonksiyonlar)

Uygulama içerisinde aktif olarak çalışan modüller şunlardır:

### 1. Yol Haritası Planlayıcı (Roadmap)
* Kullanıcının girdiği herhangi bir meslek hedefine göre OpenAI (`gpt-4o-mini`) ile 5 adımlı bir görsel yol haritası hazırlar.
* Her adımın altında tamamlanabilir görevlerden oluşan bir checklist yer alır.
* Her adıma özel **resmi dokümantasyon** bağlantıları ve yerel YouTube arama motoru modülümüzle çekilen **doğrudan video ders linkleri** enjekte edilir.

### 2. Haftalık Çalışma Takvimi (Scheduler & CRUD)
* Yol haritasındaki adımları gün bazlı saat planlamasına böler.
* **Tam CRUD Yeteneği:** Takvimdeki görevlerin isimlerini elle değiştirebilir, yeni görevler ekleyebilir veya silebilirsiniz.
* **Hafta Ekleme:** Mevcut çalışma bittiğinde yapay zeka ile sonraki haftayı planlayabilirsiniz.

### 3. Alarm ve Hatırlatıcı Bildirimleri
* Takvimdeki herhangi bir göreve özel tarih/saat seçerek hatırlatıcı kurabilirsiniz.
* Arka planda çalışan zaman kontrolcüsü sayesinde alarm vakti geldiğinde sesli/görsel slide-in toast uyarısı ve tarayıcı yerel bildirimi alırsınız.

### 4. Kariyer Chatbot Ajanları (AI Mentors)
* Farklı disiplinlere özel tanımlanmış 5 yapay zeka mentörüyle sohbet arayüzü:
  * **Yazılım Geliştirme Uzmanı**
  * **Yapay Zeka & Veri Uzmanı**
  * **Tasarım (UX/UI) Uzmanı**
  * **Dijital Pazarlama Uzmanı**
  * **Girişimcilik & Ürün Yönetimi Uzmanı**

### 5. Canlı Eğitim Önerileri (Deep Suggestions)
* Yol haritasında seçilen konu başlığına özel olarak Udemy kursları, YouTube videoları ve GitHub örnek depolarına giden doğrudan 6 adet eğitim linkini listeler.

### 6. Kariyer Simülasyon Kapsülü (Console HUD)
* Gelecekteki mesleğinizin bir gününü temsil eden operasyon loglarını daktilo efektiyle ekrana yazdıran, 15 saniyelik görsel dairesel geri sayım halkası içeren motivasyon podudur. 15 saniye sonunda başarı sertifikası ve rozeti ekrana gelir.

---

## 🛠️ Kurulum ve Çalıştırma

### 1. Otomatik Kurulum (Windows)
Windows işletim sistemlerinde klasördeki [run.bat](run.bat) dosyasına çift tıklayarak sistemi başlatabilirsiniz. Script sırasıyla:
1. Gerekli sanal ortamı (`venv`) hazırlar.
2. Bağımlılıkları (`requriments.txt`) yükler.
3. `.env` dosyası eksikse `.env_example` dosyasından otomatik kopyalar.
4. Sunucuyu `http://127.0.0.1:5000` adresinde başlatır.

### 2. Manuel Kurulum
1. Sanal ortam oluşturup aktif edin:
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```
2. Bağımlılıkları kurun:
   ```bash
   pip install -r requriments.txt
   ```
3. `.env` dosyasını oluşturup API anahtarınızı ekleyin:
   ```env
   OPENAI_API_KEY=sk-proj-your-key
   ```
4. Uygulamayı çalışrittin:
   ```bash
   python main.py
   ```
