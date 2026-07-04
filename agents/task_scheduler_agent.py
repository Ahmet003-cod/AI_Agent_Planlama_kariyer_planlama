import os
import json
import requests
from dotenv import load_dotenv

class TaskSchedulerAgent:
    def __init__(self, model_name="gpt-4o-mini"):
        load_dotenv()
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.model_name = model_name

    def generate_schedule(self, step_name, user_goal="", week_number=1):
        """
        Seçilen bir adım için 5 günlük detaylı haftalık çalışma programı oluşturur (OpenAI).
        """
        system_prompt = (
            "Sen detaylı bir Görev Planlama Asistanısın. Kullanıcı senden bir kariyer adımını planlamanı isteyecek. "
            f"Bu adım için {week_number}. Hafta ders/çalışma planı üret (Hafta {week_number}). "
            "Plan 5 günlük (Pazartesi-Cuma) detaylı ve gerçekçi görevlerden oluşmalıdır. "
            f"Eğer week_number > 1 ise, görevler bu konunun daha ileri seviye detaylarını kapsamalı ve bir önceki haftaların devamı niteliğinde olmalıdır. "
            "Yanıtın kesinlikle SADECE geçerli bir JSON olmalıdır ve başka hiçbir metin veya açıklama içermemelidir. "
            "Format şu şekilde olmalıdır:\n"
            "{\n"
            "  \"HaftalikPlan\": [\n"
            "    {\n"
            "      \"Gun\": \"Pazartesi\",\n"
            "      \"Gorevler\": [\"Giriş konularını oku\", \"Basit örnek kod yaz\"],\n"
            "      \"Sure\": \"2 Saat\"\n"
            "    },\n"
            "    ...\n"
            "  ]\n"
            "}"
        )

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
                        {"role": "user", "content": f"Hedef Kariyer: {user_goal}\nPlanlanacak Adım: {step_name}\nSeçilen Hafta: {week_number}"}
                    ],
                    "response_format": {"type": "json_object"},
                    "temperature": 0.4
                }

                response = requests.post(url, headers=headers, json=payload, timeout=20)
                if response.status_code == 200:
                    resp_json = response.json()
                    content = resp_json['choices'][0]['message']['content'].strip()
                    return json.loads(content)
                else:
                    print(f"OpenAI API Error: {response.status_code} - {response.text}")
                    return self._generate_mock_schedule(step_name, week_number)
            except Exception as e:
                print(f"TaskSchedulerAgent request failed: {e}")
                return self._generate_mock_schedule(step_name, week_number)
        else:
            return self._generate_mock_schedule(step_name, week_number)

    def _generate_mock_schedule(self, step_name, week_number=1):
        """
        API anahtarı bulunmadığında çalışan mock plan üreticisi.
        """
        days = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma"]
        
        # Vary tasks based on week number
        if week_number == 1:
            tasks_pool = [
                [f"{step_name} konusunun temel kavramlarını araştır ve not al.", "İlk eğitim dokümanını oku."],
                [f"{step_name} için gerekli araçları kurun.", "Basit pratik denemeler yap."],
                [f"{step_name} ile ilgili 1. seviye video dersleri izle.", "Örnek kod yapılarını incele."],
                [f"{step_name} kullanarak küçük bir kod parçası veya proje taslağı yaz.", "Çıkan hataları debug et."],
                [f"1. hafta öğrenilenleri tekrar et.", "Gelişmeleri GitHub reposuna kaydet."]
            ]
        else:
            tasks_pool = [
                [f"{step_name} konusundaki ileri düzey kavramlara geçiş yap.", f"{week_number}. hafta hedeflerini belirle."],
                [f"{step_name} ile ilgili orta-ileri seviye pratik egzersizler yap.", "Algoritmaları optimize et."],
                [f"{step_name} için detaylı kütüphane ve modül yapılarını araştır.", "Dokümantasyonu derinlemesine oku."],
                [f"{step_name} kullanarak daha kapsamlı ve fonksiyonel bir modül geliştir.", "Hata yönetimini (Exception handling) güçlendir."],
                [f"{week_number}. hafta öğrenilenleri pekiştir.", "Uygulamayı çalıştırıp testleri gerçekleştir."]
            ]
            
        plan = []
        for i, day in enumerate(days):
            plan.append({
                "Gun": day,
                "Gorevler": tasks_pool[i],
                "Sure": "2 Saat"
            })
            
        return {"HaftalikPlan": plan}
