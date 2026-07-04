import os
import json
import requests
from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv

# Import agents, tools, memorys
from agents.career_goal_agent import CareerGoalAgent
from agents.task_scheduler_agent import TaskSchedulerAgent
from agents.career_expert_agent import CareerExpertAgent
from tools.suggestion_tool import SuggestionTool
from memorys.user_memry import UserMemory

# Load environments
load_dotenv()

app = Flask(__name__, template_folder='templates', static_folder='static')
CORS(app)

# Initialize modules
career_agent = CareerGoalAgent()
scheduler_agent = TaskSchedulerAgent()
expert_agent = CareerExpertAgent()
suggestion_tool = SuggestionTool()
user_memory = UserMemory()

@app.route('/')
def index():
    """
    Ana arayüzü sunar.
    """
    return render_template('index.html')

@app.route('/api/career-goal', methods=['POST'])
def get_career_goal():
    """
    Kullanıcının hedef mesleğine göre yol haritası üretir.
    """
    data = request.get_json()
    if not data or 'career_goal' not in data:
        return jsonify({"hata": "Eksik parametre: career_goal"}), 400
    
    career_goal = data['career_goal']
    # Yol haritasını ajandan talep et
    roadmap = career_agent.ask_career_goal(career_goal)
    return jsonify(roadmap)

@app.route('/api/schedule-tasks', methods=['POST'])
def schedule_tasks():
    """
    Seçilen bir adım için haftalık ders/çalışma planı üretir.
    """
    data = request.get_json()
    if not data or 'step_name' not in data:
        return jsonify({"hata": "Eksik parametre: step_name"}), 400
    
    step_name = data['step_name']
    career_goal = data.get('career_goal', '')
    week_number = int(data.get('week_number', 1))
    
    # Çalışma programını planlayıcı ajandan talep et
    schedule = scheduler_agent.generate_schedule(step_name, career_goal, week_number)
    return jsonify(schedule)

@app.route('/api/suggestions', methods=['GET'])
def get_suggestions():
    """
    Seçilen adıma yönelik eğitim kaynakları ve öneriler döner.
    """
    topic = request.args.get('topic', '')
    career_goal = request.args.get('career_goal', '')
    if not topic:
        return jsonify({"hata": "Eksik parametre: topic"}), 400
    
    # Combine career goal with step topic for precise search crawling
    full_topic = f"{career_goal} {topic}" if career_goal else topic
    suggestions = suggestion_tool.get_suggestions(full_topic)
    return jsonify(suggestions)

@app.route('/api/chat', methods=['POST'])
def chat_with_expert():
    """
    Kullanıcının seçtiği kariyer uzmanı alanı ile sohbet etmesini sağlar.
    """
    data = request.get_json()
    if not data or 'message' not in data or 'domain' not in data:
        return jsonify({"hata": "Eksik parametreler: message ve domain gereklidir."}), 400
    
    message = data['message']
    domain = data['domain']
    history = data.get('history', [])
    
    response_text = expert_agent.ask_expert(domain, message, history)
    return jsonify({"response": response_text})

@app.route('/api/simulation-logs', methods=['POST'])
def get_simulation_logs():
    """
    Kullanıcının hedef mesleğine uygun 15 saniyelik motivasyon logları üretir (OpenAI).
    """
    data = request.get_json()
    if not data or 'career_goal' not in data:
        return jsonify({"hata": "Eksik parametre: career_goal"}), 400
    
    career_goal = data['career_goal']
    api_key = os.getenv("OPENAI_API_KEY")
    
    system_prompt = (
        "Sen bir Kariyer Simülasyon Asistanısın. Kullanıcı bir meslek söylediğinde "
        "o mesleğin günlük hayatında yaptığı 5 kritik operasyon adımını kronolojik olarak yaz. "
        "Operasyonlar heyecan verici, motive edici ve gerçekçi olmalıdır. "
        "Her adım bir saat bilgisi ve kısa bir açıklama içermelidir (Örn: '09:00 - Güvenlik logları tarandı'). "
        "Yanıtın kesinlikle SADECE geçerli bir JSON olmalıdır ve başka hiçbir metin veya açıklama içermemelidir. "
        "Format şu şekilde olmalıdır:\n"
        "{\n"
        "  \"Logs\": [\n"
        "    \"09:00 - Birinci operasyon açıklaması...\",\n"
        "    \"11:30 - İkinci operasyon açıklaması...\",\n"
        "    \"14:00 - Üçüncü operasyon açıklaması...\",\n"
        "    \"16:15 - Dördüncü operasyon açıklaması...\",\n"
        "    \"18:00 - Beşinci operasyon açıklaması...\"\n"
        "  ]\n"
        "}"
    )

    if api_key:
        try:
            url = "https://api.openai.com/v1/chat/completions"
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            }
            payload = {
                "model": "gpt-4o-mini",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Hedef Mesleğim={career_goal}"}
                ],
                "response_format": {"type": "json_object"},
                "temperature": 0.6
            }
            response = requests.post(url, headers=headers, json=payload, timeout=15)
            if response.status_code == 200:
                resp_json = response.json()
                content = resp_json['choices'][0]['message']['content'].strip()
                return jsonify(json.loads(content))
            else:
                return jsonify(_generate_mock_simulation_logs(career_goal))
        except Exception as e:
            print(f"Simulation logs request failed: {e}")
            return jsonify(_generate_mock_simulation_logs(career_goal))
    else:
        return jsonify(_generate_mock_simulation_logs(career_goal))

def _generate_mock_simulation_logs(career_goal):
    ui_lower = career_goal.lower()
    if "siber" in ui_lower or "güvenlik" in ui_lower:
        return {
            "Logs": [
                "08:30 - Ağ güvenlik duvarı (firewall) logları tarandı ve olası tehditler analiz edildi.",
                "10:15 - Şüpheli bir IP adresinden gelen port tarama girişimi tespit edildi ve engellendi.",
                "12:00 - Sunucu altyapısına yönelik planlı sızma testi (penetrasyon) çalışması başlatıldı.",
                "14:45 - Kritik bir sistem kütüphanesinde güvenlik açığı yamanarak ağ koruma altına alındı.",
                "17:30 - Günlük siber güvenlik durum raporu başarıyla tamamlandı ve onaylandı."
            ]
        }
    elif "yazılım" in ui_lower or "developer" in ui_lower or "kod" in ui_lower:
        return {
            "Logs": [
                "09:00 - Sabah toplantısı (Daily Scrum) yapıldı ve günlük yazılım hedefleri belirlendi.",
                "11:00 - Yeni kullanıcı paneli arayüzü kodlandı ve yerel sunucuda başarıyla test edildi.",
                "13:30 - Veritabanı sorgu performansları optimize edildi ve gecikme süreleri yarı yarıya düşürüldü.",
                "15:15 - Github üzerinden gelen kod inceleme (Code Review) talepleri gözden geçirilip onaylandı.",
                "17:00 - Geliştirilen son sürüm CI/CD hattı üzerinden canlı sunucuya başarıyla dağıtıldı (deployed)."
            ]
        }
    else:
        return {
            "Logs": [
                f"09:00 - {career_goal} görevi için günlük hazırlıklar ve planlamalar yapıldı.",
                f"11:30 - Kullanılan temel sektörel araçlar kontrol edilerek ilk iş adımı başarıyla atıldı.",
                f"14:00 - Karşılaşılan teknik problemler başarıyla çözülerek iş süreci optimize edildi.",
                f"16:00 - Diğer ekip üyeleri ile toplantı yapılarak ilerleme detayları paylaşıldı.",
                f"18:00 - {career_goal} rolü için günlük hedeflere ulaşıldı ve başarıyla tamamlandı."
            ]
        }

@app.route('/api/profile', methods=['GET', 'POST'])
def manage_profile():
    """
    Kullanıcı profilini kaydeder ve yükler.
    """
    if request.method == 'POST':
        data = request.get_json()
        if not data:
            return jsonify({"hata": "Geçersiz veri"}), 400
        
        success = user_memory.save_profile(data)
        if success:
            return jsonify({"durum": "başarılı"})
        else:
            return jsonify({"hata": "Kaydedilemedi"}), 500
    else:
        profile = user_memory.load_profile()
        return jsonify(profile)

if __name__ == '__main__':
    print("Uygulama başlatılıyor...")
    print("Port: 5000 | Adres: http://127.0.0.1:5000")
    app.run(debug=True, port=5000)
