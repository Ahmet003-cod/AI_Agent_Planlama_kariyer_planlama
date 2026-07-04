import os
import json

class UserMemory:
    def __init__(self, file_path="data/user_profile.json"):
        self.file_path = file_path
        self._ensure_dir_exists()
        
    def _ensure_dir_exists(self):
        dir_name = os.path.dirname(self.file_path)
        if dir_name and not os.path.exists(dir_name):
            os.makedirs(dir_name)
        if not os.path.exists(self.file_path):
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump({
                    "career_goal": "",
                    "roadmaps": {},
                    "schedules": {},
                    "completed_steps": []
                }, f, ensure_ascii=False, indent=4)

    def load_profile(self):
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {
                "career_goal": "",
                "roadmaps": {},
                "schedules": {},
                "completed_steps": []
            }

    def save_profile(self, data):
        try:
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            return True
        except Exception as e:
            print(f"UserMemory kaydetme hatası: {e}")
            return False

    def update_profile(self, key, value):
        data = self.load_profile()
        data[key] = value
        return self.save_profile(data)
