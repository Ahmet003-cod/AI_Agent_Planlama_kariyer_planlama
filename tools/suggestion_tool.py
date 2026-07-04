import os
import json
import requests
from dotenv import load_dotenv
from urllib.parse import quote

class SuggestionTool:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv("OPENAI_API_KEY")

    def get_suggestions(self, topic):
        """
        Seçilen konuya özel doğrudan hedef eğitim sitelerine (Udemy, GitHub, YouTube, resmi kılavuz) 
        ait 6 adet yüksek kaliteli çalışan linki OpenAI kullanarak üretir.
        """
        system_prompt = (
            "Sen bir Eğitim Kaynakları Asistanısın. Kullanıcı sana bir konu söyleyecek. "
            "Bu konu hakkında öğrenim amaçlı kullanılabilecek en popüler, güncel ve doğrudan 6 adet eğitim kaynağı öner. "
            "Öneriler Kurs, Video ve Proje Önerisi kategorilerinde olmalıdır.\n"
            "KRİTİK KURAL: Linkler kesinlikle 'https://www.youtube.com', 'https://www.udemy.com' veya 'https://github.com' gibi "
            "ana sayfa adresleri veya genel alan adları olmamalıdır! Mutlaka o konuya özgü doğrudan alt sayfa veya video bağlantısı olmalıdır "
            "(Örn: 'https://www.youtube.com/watch?v=...' veya 'https://www.udemy.com/course/...'). Eğer doğrudan bağlantıyı kesin olarak "
            "bilmiyorsanız, o kategoriyi eklemeyin veya resmi dokümantasyon ana rehber sayfasını yazın. Arama sorgusu sayfaları (results?search_query) eklemeyin.\n"
            "Çıktıyı sadece aşağıdaki geçerli JSON formatında üret, başka metin ekleme:\n"
            "{\n"
            "  \"suggestions\": [\n"
            "    {\n"
            "      \"type\": \"Kurs\" veya \"Video\" veya \"Proje Önerisi\",\n"
            "      \"title\": \"Kaynak Başlığı\",\n"
            "      \"url\": \"https://... (doğrudan link)\",\n"
            "      \"description\": \"Kaynak açıklaması\"\n"
            "    }\n"
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
                    "model": "gpt-4o-mini",
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": f"Konu: {topic}"}
                    ],
                    "response_format": {"type": "json_object"},
                    "temperature": 0.5
                }
                response = requests.post(url, headers=headers, json=payload, timeout=15)
                if response.status_code == 200:
                    resp_json = response.json()
                    content = resp_json['choices'][0]['message']['content'].strip()
                    data = json.loads(content)
                    if "suggestions" in data:
                        return data["suggestions"]
                    elif isinstance(data, list):
                        return data
            except Exception as e:
                print(f"OpenAI suggestion generation failed: {e}")

        # Fallback if API key is not set or request failed
        return self._generate_mock_suggestions(topic)

    def _generate_mock_suggestions(self, topic):
        """
        API hata durumlarında çalışan akıllı arama yönlendirmeli mock öneriler.
        """
        return [
            {
                "type": "Kurs",
                "title": f"Udemy: {topic} Kursları",
                "url": f"https://www.udemy.com/courses/search/?q={quote(topic)}",
                "description": f"'{topic}' konusunda uzmanlaşmak için popüler online video kurs portalındaki ilgili eğitimler."
            },
            {
                "type": "Video",
                "title": f"YouTube: {topic} Eğitim Videoları",
                "url": f"https://www.youtube.com/results?search_query={quote(topic)}",
                "description": f"YouTube üzerinde '{topic}' konusundaki pratik video anlatımları ve dersler."
            },
            {
                "type": "Proje Önerisi",
                "title": f"GitHub: {topic} Örnek Depoları",
                "url": f"https://github.com/search?q={quote(topic)}",
                "description": f"GitHub üzerinde '{topic}' ile ilgili paylaşılmış en popüler açık kaynak kod depoları."
            }
        ]
