import os
from dotenv import load_dotenv

load_dotenv()

# API Keys
ANTHROPIC_API_KEY       = os.getenv("ANTHROPIC_API_KEY")
INSTAGRAM_ACCESS_TOKEN  = os.getenv("INSTAGRAM_ACCESS_TOKEN")
INSTAGRAM_USER_ID       = os.getenv("INSTAGRAM_USER_ID")

# Cloudinary (CDN confiável para Instagram API)
CLOUDINARY_CLOUD_NAME   = os.getenv("CLOUDINARY_CLOUD_NAME")
CLOUDINARY_API_KEY      = os.getenv("CLOUDINARY_API_KEY")
CLOUDINARY_API_SECRET   = os.getenv("CLOUDINARY_API_SECRET")

# Pexels (imagens para os slides — opcional)
PEXELS_API_KEY          = os.getenv("PEXELS_API_KEY", "")

# Telegram
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID   = os.getenv("TELEGRAM_CHAT_ID")

# Caminhos — OUTPUT_DIR pode ser sobrescrito via variável de ambiente para rodar localmente
BASE_DIR    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR  = os.getenv("OUTPUT_DIR", os.path.join(BASE_DIR, "output"))
PENDING_DIR = os.path.join(OUTPUT_DIR, "pending")
POSTED_DIR  = os.path.join(OUTPUT_DIR, "posted")

# Agendamento
SCHEDULE_DAYS   = [0, 1, 2, 3, 4, 5, 6]   # Todos os dias
SCHEDULE_HOUR   = 9
SCHEDULE_MINUTE = 0
