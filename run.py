print("Сервер запускается...")
from app import create_app
import os

app = create_app()
port = int(os.environ.get("PORT", 5000))

if __name__ == "__main__":
    print(f"Запуск на порту {port}")
    app.run(host="0.0.0.0", port=port)