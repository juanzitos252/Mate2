import json
import os

class ConfigManager:
    def __init__(self, config_dir=None):
        if config_dir is None:
            self.config_dir = os.path.expanduser("~/.config/QuizApp")
        else:
            self.config_dir = config_dir

        os.makedirs(self.config_dir, exist_ok=True)

        self.files = {
            "settings": os.path.join(self.config_dir, "settings.json"),
            "user_data": os.path.join(self.config_dir, "user_data.json"),
        }

    def _load_json(self, file_key):
        filepath = self.files.get(file_key)
        if not filepath or not os.path.exists(filepath):
            return None
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except (IOError, json.JSONDecodeError) as e:
            print(f"Erro ao carregar {filepath}: {e}")
            return None

    def _save_json(self, file_key, data):
        filepath = self.files.get(file_key)
        if not filepath:
            raise ValueError(f"Chave de arquivo inválida: {file_key}")
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
        except IOError as e:
            print(f"Erro ao salvar em {filepath}: {e}")

    def load_settings(self):
        settings = self._load_json("settings")
        if settings is None:
            return {"theme": "colorido"}
        return settings

    def save_settings(self, settings_data):
        self._save_json("settings", settings_data)

    def load_user_data(self):
        user_data = self._load_json("user_data")
        if user_data is None:
            return {
                "multiplications_data": [],
                "custom_formulas_data": [],
                "table_weights": {str(i): 1.0 for i in range(1, 11)},
                "timed_mode_highscore": 0,
            }
        return user_data

    def save_user_data(self, user_data):
        self._save_json("user_data", user_data)
