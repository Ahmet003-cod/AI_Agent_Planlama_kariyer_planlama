import os
import json
import requests
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import quote
from tools.youtube_search import search_youtube_video

class CareerGoalAgent:
    def __init__(self, model_name="gpt-4o-mini"):
        load_dotenv()
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.model_name = model_name

    def ask_career_goal(self, user_input):
        """
        Kullanıcıdan gelen hedef meslek bilgisine göre kariyer yol haritası oluşturur (OpenAI).
        """
        system_prompt = (
            "Sen Kariyer Planlama Asistanısın. Kullanıcı bir meslek söylediğinde "
            "bu meslekte uzmanlaşmak için adım adım (en az 5 adım) detaylı bir yol haritası üret. "
            "Her adım için başlık, kısa açıklama, yapılması gereken pratik görevler (en az 3 adet) "
            "ve öğrenmek için önerilen resmi dokümantasyon/kılavuz kaynaklarının listesini dahil et.\n"
            "KRİTİK KURAL: Dokümantasyon linkleri mutlaka resmi ve doğrudan hedef web sitesine ait çalışan bağlantılar olmalıdır "
            "(Örn: W3Schools, MDN, PortSwigger, OWASP, Docker Docs, React.dev, vb.). "
            "Kesinlikle 'https://www.youtube.com', 'https://www.udemy.com' veya 'https://github.com' gibi genel ana sayfa adresleri veya "
            "genel alan adları eklemeyin! Eğer doğrudan bağlantıyı kesin olarak bilmiyorsanız, o kaynağı eklemeyin veya "
            "resmi rehber alt sayfalarını yazın. Arama motoru sorgu linkleri eklemeyin.\n"
            "Çıktı sadece aşağıdaki geçerli JSON formatında olmalı, başka metin veya açıklama içermemelidir:\n"
            "{\n"
            "  \"Adimlar\": [\n"
            "    {\n"
            "      \"AdimNo\": 1,\n"
            "      \"Baslik\": \"Adım Başlığı\",\n"
            "      \"Aciklama\": \"Kısa Açıklama...\",\n"
            "      \"Gorevler\": [\"Görev 1\", \"Görev 2\", \"Görev 3\"],\n"
            "      \"Kaynaklar\": [\n"
            "        {\n"
            "          \"Tur\": \"Dokümantasyon\",\n"
            "          \"Baslik\": \"Kaynak Başlığı\",\n"
            "          \"Link\": \"https://... (Resmi dokümantasyon doğrudan linki)\",\n"
            "          \"Aciklama\": \"Kaynak açıklaması\"\n"
            "        }\n"
            "      ]\n"
            "    }\n"
            "  ]\n"
            "}"
        )

        roadmap = None
        if self.api_key:
            try:
                url = "https://api.openai.com/v1/chat/completions"
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.api_key}"
                }
                payload = {
                    "model": self.model_name,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": f"Hedef Mesleğim={user_input}"}
                    ],
                    "response_format": {"type": "json_object"},
                    "temperature": 0.5
                }

                response = requests.post(url, headers=headers, json=payload, timeout=20)
                if response.status_code == 200:
                    resp_json = response.json()
                    content = resp_json['choices'][0]['message']['content'].strip()
                    roadmap = self.parse_response(content)
                else:
                    print(f"OpenAI API Error: {response.status_code} - {response.text}")
                    roadmap = self._generate_mock_roadmap(user_input)
            except Exception as e:
                print(f"CareerGoalAgent request failed: {e}")
                roadmap = self._generate_mock_roadmap(user_input)
        else:
            roadmap = self._generate_mock_roadmap(user_input)

        # Enrich roadmap steps with real-time web search links in the background
        if roadmap and "Adimlar" in roadmap:
            try:
                # Concurrently fetch web resources for all steps combining career goal with step title
                with ThreadPoolExecutor(max_workers=5) as executor:
                    enriched_steps = list(executor.map(
                        lambda step: self._enrich_step_with_search(step, user_input),
                        roadmap["Adimlar"]
                    ))
                roadmap["Adimlar"] = enriched_steps
            except Exception as e:
                print(f"Roadmap enrichment failed: {e}")
                
        return roadmap

    def parse_response(self, response_text):
        try:
            return json.loads(response_text)
        except json.JSONDecodeError:
            return {"hata": "Modelden Gelen yanıtlar json formatında değil.", "raw": response_text}

    def _enrich_step_with_search(self, step, career_goal):
        """
        YouTube üzerinden adım başlığı ve meslek hedefini birleştirerek doğrudan video ders bağlantısını arar
        ve resmi dokümantasyon kaynaklarına ekler.
        """
        title = step.get("Baslik", "")
        search_topic = f"{career_goal} {title}"
        
        # 1. YouTube'dan gerçek video linkini ve başlığını ara
        video_res = search_youtube_video(search_topic)
        
        # 2. Mevcut dokümantasyon kaynaklarını oku (OpenAI tarafından üretilen)
        existing_resources = step.get("Kaynaklar", [])
        if not isinstance(existing_resources, list):
            existing_resources = []
            
        new_resources = []
        
        # Add crawled video resource first
        new_resources.append({
            "Tur": "Video",
            "Baslik": video_res["title"],
            "Link": video_res["url"],
            "Aciklama": f"'{title}' konusu için internette bulunan popüler video ders kaynağı."
        })
        
        # Keep documentation resources (ensure links are clean and not search results)
        for res in existing_resources:
            if isinstance(res, dict):
                # If OpenAI generated a valid doc link, keep it
                tur = res.get("Tur", "Dokümantasyon")
                if tur.lower() == "video":
                    continue # Skip mock video links from OpenAI, we use our crawled one
                new_resources.append(res)
                
        # If no documentation was generated by OpenAI, add a fallback official one
        has_doc = any(r.get("Tur", "").lower() == "dokümantasyon" for r in new_resources)
        if not has_doc:
            new_resources.append({
                "Tur": "Dokümantasyon",
                "Baslik": f"Google: {title} Belgeleri",
                "Link": f"https://www.google.com/search?q={quote(search_topic + ' belgelendirmesi rehber')}",
                "Aciklama": f"'{title}' konusu için Google üzerinden erişilebilen resmi dokümantasyon kaynakları."
            })
            
        step["Kaynaklar"] = new_resources
        return step

    def _generate_mock_roadmap(self, user_input):
        """
        API anahtarı bulunmadığında çalışan mock yol haritaları.
        """
        ui_lower = user_input.lower()
        
        if "web" in ui_lower or "front" in ui_lower or "html" in ui_lower or "arayüz" in ui_lower:
            steps = [
                {
                    "AdimNo": 1,
                    "Baslik": "HTML5 ve CSS3 Temelleri",
                    "Aciklama": "Semantik web, modern sayfa düzenleme ve responsive tasarımlar yapın.",
                    "Gorevler": [
                        "HTML5 semantik etiketlerini öğrenin ve kullanın.",
                        "CSS Grid ve Flexbox kullanarak 2 farklı sayfa şablonu oluşturun.",
                        "Responsive tasarım için mobil uyumlu bir profil sayfası geliştirin."
                    ],
                    "Kaynaklar": [
                        {"Tur": "Dokümantasyon", "Baslik": "MDN Web Docs HTML/CSS", "Link": "https://developer.mozilla.org/tr/docs/Web/HTML", "Aciklama": "Web geliştirmenin resmi ansiklopedisi."}
                    ]
                },
                {
                    "AdimNo": 2,
                    "Baslik": "Modern JavaScript (ES6+)",
                    "Aciklama": "Dinamik web sayfaları geliştirin, DOM manipülasyonu ve API isteklerini kavrayın.",
                    "Gorevler": [
                        "Değişkenler, döngüler, arrow fonksiyonları ve ES6+ özelliklerini kavrayın.",
                        "Bir butona tıklandığında veri çeken Fetch/Axios API entegrasyonu yapın.",
                        "Tarayıcı yerel hafızasını (LocalStorage) kullanan bir yapılacaklar listesi yazın."
                    ],
                    "Kaynaklar": [
                        {"Tur": "Dokümantasyon", "Baslik": "Javascript.info Modern JS Kılavuzu", "Link": "https://javascript.info/", "Aciklama": "Temelden ileri seviyeye kod örnekleriyle JS kılavuzu."}
                    ]
                },
                {
                    "AdimNo": 3,
                    "Baslik": "CSS Çatıları ve Araçlar (Tailwind CSS)",
                    "Aciklama": "CSS preprocessor'lar ve Tailwind CSS ile arayüz tasarımlarını hızlandırın.",
                    "Gorevler": [
                        "Tailwind CSS'i projenize NPM ile entegre edin.",
                        "Utility-first sınıflar kullanarak modern bir Dashboard arayüzü kodlayın.",
                        "Karanlık mod (dark mode) desteğini projelerinize ekleyin."
                    ],
                    "Kaynaklar": [
                        {"Tur": "Dokümantasyon", "Baslik": "Tailwind CSS Dokümantasyonu", "Link": "https://tailwindcss.com/docs", "Aciklama": "Resmi Tailwind CSS resmi dökümanı."}
                    ]
                },
                {
                    "AdimNo": 4,
                    "Baslik": "React.js Kütüphanesi",
                    "Aciklama": "Bileşen tabanlı state yönetimi ve modern React hooks (useState, useEffect) öğrenin.",
                    "Gorevler": [
                        "React projesi oluşturup özel component yapıları tanımlayın.",
                        "Bir formdan veri alıp state güncelleyen dinamik bir uygulama tasarlayın.",
                        "useEffect hook'u kullanarak harici API'den veri çeken bir galeri yapın."
                    ],
                    "Kaynaklar": [
                        {"Tur": "Dokümantasyon", "Baslik": "Yeni React.dev Dokümanları", "Link": "https://react.dev/", "Aciklama": "Yeni nesil modern React resmi belgeleri."}
                    ]
                },
                {
                    "AdimNo": 5,
                    "Baslik": "Sürüm Kontrolü ve Derleme Araçları",
                    "Aciklama": "Git/GitHub, NPM paket yöneticisi ve Vite derleme aracında uzmanlaşın.",
                    "Gorevler": [
                        "Git ile proje versiyonlama yapın, commit ve push adımlarını öğrenin.",
                        "GitHub'da bir repository oluşturup projenizi deploy edin.",
                        "Vite paketleyicisi kullanarak projenin üretim çıktılarını optimize edin."
                    ],
                    "Kaynaklar": [
                        {"Tur": "Dokümantasyon", "Baslik": "Vite.js Resmi Kılavuz", "Link": "https://vitejs.dev/", "Aciklama": "Hızlı frontend geliştirme ve build aracı."}
                    ]
                }
            ]
        elif "python" in ui_lower or "backend" in ui_lower or "sunucu" in ui_lower:
            steps = [
                {
                    "AdimNo": 1,
                    "Baslik": "Python Temelleri ve OOP",
                    "Aciklama": "Python programlama dilinin veri tiplerini, kontrol yapılarını ve Nesne Yönelimli Programlamayı öğrenin.",
                    "Gorevler": [
                        "Değişkenler, döngüler ve fonksiyon yazma egzersizleri yapın.",
                        "OOP mantığıyla Sınıf (Class) ve Kalıtım (Inheritance) örnekleri kodlayın.",
                        "Dosya okuma/yazma ve hata yönetimi (try-except) yapılarını uygulayın."
                    ],
                    "Kaynaklar": [
                        {"Tur": "Dokümantasyon", "Baslik": "Python.org Resmi Dokümanları", "Link": "https://docs.python.org/3/", "Aciklama": "Resmi Python kılavuzları."}
                    ]
                },
                {
                    "AdimNo": 2,
                    "Baslik": "Veritabanı ve SQL Modelleme",
                    "Aciklama": "İlişkisel veritabanlarını, SQL sorgularını ve PostgreSQL/SQLite entegrasyonunu kavrayın.",
                    "Gorevler": [
                        "Temel SQL komutlarını (SELECT, INSERT, UPDATE, DELETE) öğrenin.",
                        "Tablolar arası ilişkiler (One-to-Many, Many-to-Many) kurun.",
                        "Python ile veritabanına bağlanıp veri ekleyen ve çeken kodlar yazın."
                    ],
                    "Kaynaklar": [
                        {"Tur": "Dokümantasyon", "Baslik": "PostgreSQL Resmi Kılavuzu", "Link": "https://www.postgresql.org/docs/", "Aciklama": "Güçlü, açık kaynaklı ilişkisel veritabanı belgeleri."}
                    ]
                },
                {
                    "AdimNo": 3,
                    "Baslik": "Flask veya FastAPI ile REST API Geliştirme",
                    "Aciklama": "Modern API sunucuları oluşturun, HTTP istek tiplerini ve yönlendirmeleri yönetin.",
                    "Gorevler": [
                        "Seçtiğiniz framework ile ilk HTTP API sunucunuzu ayağa kaldırın.",
                        "JSON verisi dönen GET ve POST API uç noktaları tasarlayın.",
                        "API'leri test etmek için Postman veya arama araçlarını kullanın."
                    ],
                    "Kaynaklar": [
                        {"Tur": "Dokümantasyon", "Baslik": "FastAPI Kullanım Kılavuzu", "Link": "https://fastapi.tiangolo.com/", "Aciklama": "Hızlı ve modern API framework resmi dökümanı."}
                    ]
                },
                {
                    "AdimNo": 4,
                    "Baslik": "Güvenlik ve Kimlik Doğrulama",
                    "Aciklama": "Kullanıcı kayıt, giriş işlemleri, şifre şifreleme ve JWT tabanlı yetkilendirme.",
                    "Gorevler": [
                        "Kullanıcı şifrelerini bcrypt kullanarak veritabanına hash'leyerek kaydedin.",
                        "Giriş yapan kullanıcılara özel JWT üreten login API yazın.",
                        "Giriş yetkisi gerektiren korumalı API yolları geliştirin."
                    ],
                    "Kaynaklar": [
                        {"Tur": "Dokümantasyon", "Baslik": "JWT.io Token Kılavuzu", "Link": "https://jwt.io/introduction", "Aciklama": "Kimlik doğrulama standartları ve detayları."}
                    ]
                },
                {
                    "AdimNo": 5,
                    "Baslik": "Docker ile Paketleme ve Dağıtım",
                    "Aciklama": "Uygulamanızı Docker container ile izele edin ve bulut ortamında deploy edin.",
                    "Gorevler": [
                        "Projeniz için bir Dockerfile yazın ve imaj oluşturun.",
                        "Bulut servislerine (Render, AWS) veritabanı ile birlikte deploy edin.",
                        "GitHub Actions kullanarak basit bir CI/CD otomatik yayına alma süreci kurgulayın."
                    ],
                    "Kaynaklar": [
                        {"Tur": "Dokümantasyon", "Baslik": "Docker Official Docs", "Link": "https://docs.docker.com/", "Aciklama": "Docker kurulumu ve komutları resmi kılavuzu."}
                    ]
                }
            ]
        else:
            steps = [
                {
                    "AdimNo": 1,
                    "Baslik": "Temel Kavramlar ve Teori",
                    "Aciklama": f"{user_input} alanındaki temel kavramları, terminolojiyi ve teorik altyapıyı öğrenin.",
                    "Gorevler": [
                        f"{user_input} alanındaki temel terimleri araştırın.",
                        "Sektördeki öncüler tarafından yazılmış makaleleri okuyun.",
                        "Bu alandaki temel gereksinimleri listeleyin."
                    ],
                    "Kaynaklar": [
                        {"Tur": "Dokümantasyon", "Baslik": f"{user_input} Giriş Kılavuzu", "Link": f"https://tr.wikipedia.org/wiki/Special:Search?search={quote(user_input)}", "Aciklama": "Vikipedi üzerinden temel alan araştırması."}
                    ]
                },
                {
                    "AdimNo": 2,
                    "Baslik": "Temel Araçların Keşfi",
                    "Aciklama": "Sektörde kullanılan temel araçları ve teknolojileri keşfederek pratik yapmaya başlayın.",
                    "Gorevler": [
                        "Kullanılan popüler yazılım veya araçları bilgisayarınıza kurun.",
                        "İlk deneme çalışmanızı veya projenizi hazırlayın.",
                        "Karşılaştığınız sorunları çözmek için topluluk forumlarını inceleyin."
                    ],
                    "Kaynaklar": [
                        {"Tur": "Dokümantasyon", "Baslik": f"{user_input} Resmi Araçları", "Link": f"https://github.com/search?q={quote(user_input)}", "Aciklama": "Popüler araçların kurulum rehberleri."}
                    ]
                },
                {
                    "AdimNo": 3,
                    "Baslik": "Orta Seviye Uygulamalar",
                    "Aciklama": "Orta seviye konulara geçiş yapın, ilk küçük ölçekli projelerinizi hazırlayın.",
                    "Gorevler": [
                        "Kendi başınıza bağımsız bir portföy çalışması yapın.",
                        "Çalışmanızı gözden geçirmesi için alanında uzman birinden geri bildirim alın.",
                        "Optimizasyon kurallarını projenize uygulayın."
                    ],
                    "Kaynaklar": [
                        {"Tur": "Dokümantasyon", "Baslik": f"{user_input} Rehber Kaynakları", "Link": f"https://www.google.com/search?q={quote(user_input + ' dersleri ve kilavuzlari')}", "Aciklama": "Genel eğitim portalı kılavuzları."}
                    ]
                },
                {
                    "AdimNo": 4,
                    "Baslik": "Portföy ve İleri Seviye",
                    "Aciklama": f"{user_input} alanında deneyimli kişilerin projelerini inceleyin ve portföyünüzü oluşturmaya başlayın.",
                    "Gorevler": [
                        "Tüm projelerinizi sergileyebileceğiniz kişisel bir web sitesi veya Behance/GitHub hesabı açın.",
                        "En az 3 adet tamamlanmış çalışmayı portföyünüze ekleyin.",
                        "Gelişmiş teknikleri veya iş modellerini öğrenin."
                    ],
                    "Kaynaklar": [
                        {"Tur": "Dokümantasyon", "Baslik": "GitHub Proje Keşifleri", "Link": f"https://github.com/search?q={quote(user_input + ' templates')}", "Aciklama": "Örnek kod şablonları."}
                    ]
                },
                {
                    "AdimNo": 5,
                    "Baslik": "Sektörel Ağ Kurma ve İş Başvuruları",
                    "Aciklama": "Sektörel topluluklara katılın, açık kaynak projelere katkıda bulunun ve iş başvuruları için hazırlanın.",
                    "Gorevler": [
                        "LinkedIn profilinizi güncelleyip bu alandaki profesyonelleri takip edin.",
                        "CV'nizi ve portföyünüzü mülakatlara uygun şekilde düzenleyin.",
                        "Aktif iş ilanlarına başvurmaya başlayın."
                    ],
                    "Kaynaklar": [
                        {"Tur": "Dokümantasyon", "Baslik": "LinkedIn Ağ Oluşturma", "Link": f"https://www.google.com/search?q={quote(user_input + ' linkedin networking guide')}", "Aciklama": "LinkedIn ağ oluşturma rehberi."}
                    ]
                }
            ]
            
        return {"Adimlar": steps}

# main.py içerisindeki yazım hatası importuna (CreerGoalAgent) uyumluluk sağlamak için alias ekliyoruz
CreerGoalAgent = CareerGoalAgent
