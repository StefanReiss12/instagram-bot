"""
Envia o carrossel para aprovação via Telegram.
O bot.py é quem processa os botões de resposta.
"""
import os
import json
import telebot
from src.config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID


def send_for_approval(post_id: str, carousel_data: dict, image_paths: list[str]):
    """Envia imagens + botões de aprovação para o Telegram."""
    bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)
    chat_id = TELEGRAM_CHAT_ID

    # Envia imagens como álbum
    media = []
    for i, path in enumerate(image_paths):
        with open(path, "rb") as f:
            data = f.read()
        if i == 0:
            media.append(telebot.types.InputMediaPhoto(data, caption=f"🎠 *Novo carrossel para aprovação*\n\nTópico: {carousel_data.get('topic', '')}", parse_mode="Markdown"))
        else:
            media.append(telebot.types.InputMediaPhoto(data))

    bot.send_media_group(chat_id, media)

    # Legenda completa — Telegram suporta até 4096 chars por mensagem
    caption = carousel_data.get("caption", "")
    # Divide em partes se ultrapassar o limite do Telegram
    max_len = 4000
    parts   = [caption[i:i+max_len] for i in range(0, len(caption), max_len)]
    for idx, part in enumerate(parts):
        prefix = "📝 *Legenda completa:*\n\n" if idx == 0 else ""
        bot.send_message(chat_id, f"{prefix}{part}")

    # Botões de aprovação
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(
        telebot.types.InlineKeyboardButton("✅ Publicar agora", callback_data=f"approve:{post_id}"),
        telebot.types.InlineKeyboardButton("❌ Rejeitar",       callback_data=f"reject:{post_id}"),
    )

    bot.send_message(
        chat_id,
        f"🔔 *O que deseja fazer com este carrossel?*\n\n`ID: {post_id}`",
        reply_markup=markup,
        parse_mode="Markdown",
    )

    print(f"  ok Enviado para aprovacao no Telegram (ID: {post_id})")
