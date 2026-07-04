import os
import requests
import json
from dotenv import load_dotenv

class CareerExpertAgent:
    def __init__(self, model_name="gpt-4o-mini"):
        load_dotenv()
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.model_name = model_name

    def ask_expert(self, domain, user_message, history):
        """
        Seçilen kariyer alanına (domain) göre kullanıcıyla sohbet eder (OpenAI API).
        history: [{'role': 'user', 'content': '...'}, {'role': 'assistant', 'content': '...'}]
        """
        # System message based on domain
        system_prompts = {
            "yazilim": (
                "Sen kıdemli bir Yazılım Geliştirme Kariyer Uzmanısın. "
                "Kullanıcıya yazılım dünyasındaki diller, teknolojiler, backend/frontend/mobil ayrımı, "
                "kariyer yolları, iş bulma süreçleri ve teknik gelişim hakkında profesyonel, yapıcı ve "
                "yol gösterici yanıtlar ver. Yanıtlarını çok uzun tutma, samimi ama profesyonel ol."
            ),
            "tasarim": (
                "Sen deneyimli bir Tasarım ve UX/UI Kariyer Uzmanısın. "
                "Kullanıcının portfolyo oluşturma, tasarım araçları (Figma, Adobe vb.), grafik tasarım, "
                "kullanıcı deneyimi araştırmaları ve arayüz tasarımı ile ilgili sorularını "
                "görsel estetiği ve kullanıcı odaklılığı vurgulayarak yanıtla. Yanıtların ilham verici ve pratik olsun."
            ),
            "pazarlama": (
                "Sen uzman bir Dijital Pazarlama ve Büyüme (Growth) Kariyer Uzmanısın. "
                "Kullanıcıya SEO, SEM, sosyal medya yönetimi, veri analitiği, içerik pazarlaması, "
                "reklam yönetimi ve marka stratejileri konularında sektörel trendlere uygun, "
                "aksiyon alınabilir tavsiyeler ver."
            ),
            "veri-yapayzeka": (
                "Sen kıdemli bir Veri Bilimi ve Yapay Zeka Kariyer Uzmanısın. "
                "Kullanıcıya veri analizi, makine öğrenmesi, derin öğrenme, büyük veri teknolojileri, "
                "LLM'ler ve RAG mimarileri ile ilgili kariyer yolları, matematiksel altyapı ve proje fikirleri "
                "sunarak rehberlik et. Teknik kavramları sadeleştirerek anlat."
            ),
            "girisimcilik-urun": (
                "Sen tecrübeli bir Girişimcilik ve Ürün Yönetimi (Product Management) Kariyer Uzmanısın. "
                "Kullanıcıya ürün geliştirme yaşam döngüsü, Scrum/Agile metodolojileri, MVP oluşturma, "
                "pazar araştırması, pitch deck hazırlama ve iş modeli geliştirme konularında mentorluk yap."
            )
        }
        
        system_prompt = system_prompts.get(domain.lower(), (
            "Sen profesyonel bir Kariyer Planlama Uzmanısın. Kullanıcının kariyer hedefleri, "
            "iş arama stratejileri, özgeçmiş hazırlama ve mülakat teknikleri hakkındaki sorularını yanıtla."
        ))

        if self.api_key:
            try:
                # Map history roles
                messages = [{"role": "system", "content": system_prompt}]
                for msg in history:
                    messages.append({
                        "role": msg.get("role", "user"),
                        "content": msg.get("content", "")
                    })
                
                # Append current user message
                messages.append({
                    "role": "user",
                    "content": user_message
                })

                url = "https://api.openai.com/v1/chat/completions"
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.api_key}"
                }
                payload = {
                    "model": self.model_name,
                    "messages": messages,
                    "temperature": 0.7
                }

                response = requests.post(url, headers=headers, json=payload, timeout=15)
                if response.status_code == 200:
                    resp_json = response.json()
                    text = resp_json['choices'][0]['message']['content']
                    return text.strip()
                else:
                    print(f"OpenAI API Error: {response.status_code} - {response.text}")
                    return self._generate_api_error_message(response.status_code, response.text, domain, user_message)
            except Exception as e:
                print(f"CareerExpertAgent Request Exception: {e}")
                return self._generate_mock_reply(domain, user_message)
        else:
            # If no API key is set, append a friendly reminder to the mock reply
            mock_reply = self._generate_mock_reply(domain, user_message)
            return (f"{mock_reply}\n\n"
                    f"💡 *Not: Gerçek zamanlı yapay zeka cevapları için lütfen projenin kök dizinindeki `.env` dosyasına "
                    f"`OPENAI_API_KEY=api_anahtariniz` şeklinde OpenAI API anahtarınızı ekleyin.*")

    def _generate_api_error_message(self, status_code, response_text, domain, user_message):
        try:
            error_data = json.loads(response_text)
            message = error_data.get("error", {}).get("message", response_text)
        except Exception:
            message = response_text
            
        return (f"⚠️ **OpenAI API Hatası ({status_code})**\n\n"
                f"Lütfen `.env` dosyasındaki API anahtarınızı kontrol edin. Alınan hata mesajı:\n"
                f"`{message}`\n\n"
                f"*Geçici olarak çevrimdışı (mock) modda verilen yanıt:*\n\n"
                f"{self._generate_mock_reply(domain, user_message)}")

    def _generate_mock_reply(self, domain, message):
        """
        API anahtarı bulunmadığında çalışacak akıllı chatbot mock sistemi.
        """
        msg_lower = message.lower()
        
        # Yazılım Uzmanı Mock Cevapları
        if domain == "yazilim":
            if "başla" in msg_lower or "nereden" in msg_lower or "yeni" in msg_lower:
                return ("Yazılım dünyasına adım atarken öncelikle temel algoritmaları ve problem çözme mantığını kavramanı öneririm. "
                        "Ardından bir alan seçmelisin. Web için HTML/CSS/JS ile frontend veya Python/Node.js ile backend; mobil için "
                        "Flutter veya Swift/Kotlin gibi teknolojilere yönelebilirsin. Hangisi ilgini çekiyor?")
            elif "dil" in msg_lower or "python" in msg_lower or "javascript" in msg_lower:
                return ("Python veri bilimi, yapay zeka ve backend için harika bir dildir ve öğrenmesi kolaydır. JavaScript ise webin dilidir; "
                        "tarayıcıda çalışan her şey Javascript ile yazılır. Eğer web arayüzleri seni heyecanlandırıyorsa JavaScript ile, "
                        "arka plan sistemleri veya veriyle uğraşmak istiyorsan Python ile başlamak en doğrusudur.")
            elif "iş" in msg_lower or "bul" in msg_lower or "mülakat" in msg_lower:
                return ("Yazılımda iş bulmanın anahtarı güçlü bir GitHub portföyüdür. Sadece teorik öğrenmekle kalma, mutlaka kendi yaptığın "
                        "özgün projeleri (örn. hava durumu uygulaması, to-do list, e-ticaret klonu) kodlayıp yayınla. Mülakatlarda ise algoritmalar "
                        "ve iletişim becerilerin sorgulanacaktır.")
            else:
                return ("Yazılım kariyerinde kendini geliştirmek için sürekli pratik yapmalısın. Sorduğun bu konu hakkında GitHub'da benzer "
                        "açık kaynaklı projeleri inceleyebilir veya küçük denemelerle kendi çözümünü üretebilirsin. Başka hangi alanları merak ediyorsun?")
        
        # Veri ve Yapay Zeka Mock Cevapları
        elif domain == "veri-yapayzeka":
            if "başla" in msg_lower or "öğren" in msg_lower:
                return ("Yapay zeka ve veri bilimi için temel yol haritan: 1) Python programlama, 2) İstatistik ve Lineer Cebir, 3) Veri analizi "
                        "(Pandas, NumPy), 4) Makine öğrenmesi (Scikit-Learn) ve 5) Derin öğrenme (PyTorch/TensorFlow) şeklindedir. Matematiksel temeli "
                        "ihmal etmemek çok önemli. İlk olarak Python temellerini aldın mı?")
            else:
                return ("Yapay zeka alanı (özellikle LLM ve RAG sistemleri) çok hızlı gelişiyor. Teorik bilgileri öğrendikten sonra Hugging Face "
                        "üzerindeki modelleri inceleyerek ve API'ler kullanarak kendi ufak chatbot veya veri analiz projelerini yapmanı öneririm.")
                
        # Tasarım Mock Cevapları
        elif domain == "tasarim":
            return ("UX/UI tasarımcısı olmak için öncelikle Figma aracında uzmanlaşmalısın. Ardından tasarım prensiplerini (renk teorisi, tipografi, "
                    "hizalama, kontrast) öğrenmelisin. Behance ve Dribbble gibi platformlarda başarılı çalışmaları taklit ederek el becerini geliştirebilirsin.")
            
        # Pazarlama Mock Cevapları
        elif domain == "pazarlama":
            return ("Dijital pazarlamada başarılı olmak için SEO (Arama Motoru Optimizasyonu), Google Ads ve sosyal medya reklamcılığı alanlarında "
                    "deneyim kazanmalısın. Kendi blog siteni açıp Google Analytics ile trafiği izlemek harika bir başlangıç projesi olabilir.")
            
        # Girişimcilik Mock Cevapları
        elif domain == "girisimcilik-urun":
            return ("Ürün yöneticisi (Product Manager) olmak için kullanıcı ihtiyaçlarını iyi analiz edebilmeli, yazılımcılar ve tasarımcılar arasında "
                    "köprü kurabilmelisiniz. Çevik (Agile/Scrum) çalışma metodolojilerini öğrenmek ve Jira/Trello gibi araçları deneyimlemek faydalı olacaktır.")

        # Genel Mock Cevap
        return f"Bu çok güzel bir soru! {domain} alanında başarılı olmak için en önemli şey istikrarlı çalışmaktır. Hedeflerini küçük parçalara bölerek ilerlemelisin. Sana bu konuda daha spesifik nasıl yardımcı olabilirim?"
