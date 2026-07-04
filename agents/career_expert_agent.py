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
        Seçilen siber güvenlik alanına (domain) göre kullanıcıyla sohbet eder (OpenAI API).
        history: [{'role': 'user', 'content': '...'}, {'role': 'assistant', 'content': '...'}]
        """
        # System message based on domain
        system_prompts = {
            "offensive": (
                "Sen kıdemli bir Offensive Security (Sızma Testi ve Red Team) Kariyer Uzmanısın. "
                "Kullanıcıya sızma testleri, exploit yazma, zafiyet tarama, web/mobil uygulama güvenliği, "
                "ağ sızma testleri, OSCP/eWPT gibi sertifikalar ve teknik gelişim hakkında profesyonel, yapıcı ve "
                "yol gösterici yanıtlar ver. Yanıtlarını çok uzun tutma, samimi ama profesyonel ol."
            ),
            "defensive": (
                "Sen deneyimli bir Defensive Security (SOC ve Blue Team) Kariyer Uzmanısın. "
                "Kullanıcının SOC analistliği, SIEM entegrasyonu (Splunk, ELK vb.), tehdit avcılığı (Threat Hunting), "
                "log analizi, güvenlik duvarı kuralları, olay müdahale (Incident Response) ve mavi takım sertifikaları (Sec+, CYSA+) "
                "ile ilgili sorularını profesyonelce yanıtla. Yanıtların pratik ve sektörel uyumlu olsun."
            ),
            "malware-forensics": (
                "Sen uzman bir Zararlı Yazılım Analisti ve Adli Bilişim (Forensics) Kariyer Uzmanısın. "
                "Kullanıcıya tersine mühendislik (IDA Pro, Ghidra), statik ve dinamik malware analizi, "
                "disk/bellek imajı alma ve adli inceleme süreçleri, Volatility, FTK Imager gibi araçlar hakkında "
                "aksiyon alınabilir teknik tavsiyeler ver."
            ),
            "grc": (
                "Sen kıdemli bir GRC (Yönetişim, Risk ve Uyum) Kariyer Uzmanısın. "
                "Kullanıcıya bilgi güvenliği yönetim sistemleri (ISO 27001), KVKK/GDPR uyumluluğu, "
                "siber güvenlik politikaları hazırlama, risk analizi metodolojileri (OCTAVE, NIST) ve "
                "denetim süreçleri hakkında rehberlik et. Mevzuat ve kurumsal süreçlere uygun yanıtlar ver."
            ),
            "cloud-security": (
                "Sen tecrübeli bir Bulut Güvenliği (Cloud Security) Kariyer Uzmanısın. "
                "Kullanıcıya AWS/Azure/GCP üzerinde güvenli altyapı tasarımı, IAM (Kimlik Yönetimi) kuralları, "
                "konteyner ve Kubernetes güvenliği, DevSecOps süreçleri ve bulut sertifikaları (CCSP, CCSK) konularında mentorluk yap."
            )
        }
        
        system_prompt = system_prompts.get(domain.lower(), (
            "Sen profesyonel bir Siber Güvenlik Kariyer Planlama Uzmanısın. Kullanıcının siber güvenlik hedefleri, "
            "iş arama stratejileri, sertifikasyonlar ve mülakat teknikleri hakkındaki sorularını yanıtla."
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
        API anahtarı bulunmadığında çalışacak siber güvenlik chatbot mock sistemi.
        """
        msg_lower = message.lower()
        
        # Offensive Security Mock Cevapları
        if domain == "offensive":
            if "başla" in msg_lower or "nereden" in msg_lower or "yeni" in msg_lower:
                return ("Sızma testi (Pentest) dünyasına adım atarken öncelikle temel Ağ (Network) ve Linux yönetimi bilgilerini edinmelisiniz. "
                        "Ardından web zafiyetleri (OWASP Top 10) üzerine çalışarak PortSwigger Web Security Academy gibi laboratuvarlarda pratik yapabilirsiniz. "
                        "Temeliniz ne durumda, hiç Linux kullandınız mı?")
            elif "sertifika" in msg_lower or "oscp" in msg_lower:
                return ("Offensive Security alanında en değerli sertifika OSCP'dir (Offensive Security Certified Professional). Tamamen uygulamalı "
                        "24 saatlik bir sınavdır. OSCP öncesinde eJPT veya eWPT gibi başlangıç seviyesi sertifikalarla kendinizi test edebilirsiniz.")
            else:
                return ("Kırmızı Takım (Red Team) üyesi olmak, zafiyetleri istismar etmekten fazlasıdır. Ağ protokollerini, active directory mimarisini "
                        "ve savunma sistemlerini (AV/EDR) atlatma tekniklerini de öğrenmelisiniz. Pratik yapmak için TryHackMe ve HackTheBox platformlarını öneririm.")
        
        # Defensive Security Mock Cevapları
        elif domain == "defensive":
            if "başla" in msg_lower or "soc" in msg_lower:
                return ("Mavi Takım (SOC Analisti) olmak için sistem günlüklerini (log) okumayı ve tehdit tespit araçlarını (SIEM) öğrenmelisiniz. "
                        "Splunk veya ELK gibi SIEM araçlarının mantığını kavramak, Wireshark ile paket analizi yapmak harika bir başlangıçtır.")
            else:
                return ("Savunma tarafında kendinizi geliştirmek için siber saldırıların izlerini loglarda bulabilmelisiniz. Windows Event Log, Sysmon, "
                        "Snort kuralları ve firewall loglarını analiz etme becerileri SOC analisti olmanın temel taşlarıdır.")
                
        # Malware ve Forensics Mock Cevapları
        elif domain == "malware-forensics":
            return ("Zararlı yazılım analizi için x86 Assembly dili, işletim sistemi mimarileri ve C/C++ bilgisi önemlidir. Ghidra veya IDA Pro kullanarak "
                    "tersine mühendislik yapabilir, Volatility aracıyla bellek analizine giriş yapabilirsiniz. TryHackMe'deki adli bilişim odaları faydalı olacaktır.")
            
        # GRC Mock Cevapları
        elif domain == "grc":
            return ("Uyum ve risk yönetimi siber güvenliğin yönetimsel tarafıdır. ISO 27001 Bilgi Güvenliği Yönetim Sistemi, KVKK ve GDPR yasal mevzuatlarına "
                    "hâkim olmalı, NIST siber güvenlik çerçevesi gibi standartları öğrenmelisiniz.")
            
        # Bulut Güvenliği Mock Cevapları
        elif domain == "cloud-security":
            return ("Bulut güvenliği için öncelikle temel AWS veya Azure bulut mimarilerini öğrenmelisiniz. Güvenli IAM politikaları yazma, "
                    "Docker konteyner zafiyet taraması yapma ve Kubernetes güvenlik kurallarını (Network Policies) öğrenerek uzmanlaşabilirsiniz.")

        # Genel Mock Cevap
        return f"Siber güvenlikte {domain} alanında başarılı olmak için en önemli şey sürekli lab pratikleri yapmaktır. Bu alanda hangi konularda kendini geliştirmek istiyorsun?"

# main.py içerisindeki yazım hatası importuna (CreerGoalAgent) uyumluluk sağlamak için alias ekliyoruz
CreerGoalAgent = CareerExpertAgent
