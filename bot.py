"""
bot.py — Bot do Telegram para aprovação de carrosseis.
"""
import json, os, shutil, threading
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from rich.console import Console
from rich.panel import Panel
from src.config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, PENDING_DIR, POSTED_DIR

console = Console()
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)


def load_post(post_id: str) -> dict | None:
    path = os.path.join(PENDING_DIR, post_id, "meta.json")
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def publish_post(post_id: str, meta: dict) -> str:
    from src.image_uploader import upload_all_images
    from src.instagram_api import post_carousel
    from src.post_manager import mark_as_posted

    image_paths = meta["image_paths"]
    caption     = meta["caption"]

    console.print(f"\n[bold yellow]Publicando {post_id}...[/bold yellow]")
    console.print("  Fazendo upload das imagens...")
    urls = upload_all_images(image_paths)

    console.print("  Postando no Instagram...")
    ig_id = post_carousel(urls, caption)

    mark_as_posted(post_id, ig_id)
    console.print(f"  [bold green]✓ Publicado! Post ID: {ig_id}[/bold green]")
    return ig_id


def delete_post(post_id: str):
    from src.post_manager import delete_pending_post
    delete_pending_post(post_id)


def regenerate_in_background(chat_id: int, avoided_topic: str):
    """Gera novo carrossel em thread separada."""
    try:
        from datetime import datetime
        from src.content_generator import generate_carousel_content
        from src.image_creator import create_carousel_images
        from src.telegram_approval import send_for_approval
        from src.config import PENDING_DIR

        bot.send_message(chat_id, "🔄 Gerando novo carrossel com tema diferente...")

        carousel_data = generate_carousel_content(avoid_topics=[avoided_topic])

        post_id  = datetime.now().strftime("%Y%m%d_%H%M%S")
        post_dir = os.path.join(PENDING_DIR, post_id)
        os.makedirs(post_dir, exist_ok=True)

        image_paths = create_carousel_images(carousel_data, post_dir)

        meta = {
            "id":          post_id,
            "created_at":  datetime.now().isoformat(),
            "status":      "pending",
            "topic":       carousel_data.get("topic", ""),
            "caption":     carousel_data.get("caption", ""),
            "slides":      carousel_data.get("slides", []),
            "image_paths": image_paths,
        }
        with open(os.path.join(post_dir, "meta.json"), "w", encoding="utf-8") as f:
            json.dump(meta, f, ensure_ascii=False, indent=2)

        send_for_approval(post_id, carousel_data, image_paths)

    except Exception as e:
        bot.send_message(
            chat_id,
            f"❌ Erro ao regenerar:\n`{str(e)}`",
            parse_mode="Markdown",
        )


def _novo_btn(post_id: str, topic: str) -> InlineKeyboardMarkup:
    """Teclado com botão para gerar novo carrossel após falha."""
    # callback_data tem limite de 64 bytes no Telegram
    safe_topic = topic[:20].replace(":", "-")
    data = f"regen:{post_id[:15]}:{safe_topic}"
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("🔄 Gerar Novo Carrossel", callback_data=data))
    return kb


@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    try:
        bot.answer_callback_query(call.id)
    except Exception:
        pass

    parts  = call.data.split(":", 2)
    action = parts[0]

    # ── Gerar novo carrossel (botão pós-erro) ──────────────────
    if action == "regen":
        avoided = parts[2] if len(parts) > 2 else ""
        post_id = parts[1] if len(parts) > 1 else ""
        try:
            bot.edit_message_text(
                "🔄 Gerando novo carrossel...",
                call.message.chat.id, call.message.message_id,
            )
        except Exception:
            pass
        threading.Thread(
            target=regenerate_in_background,
            args=(call.message.chat.id, avoided),
            daemon=True,
        ).start()
        return

    # ── Aprovar / Rejeitar ─────────────────────────────────────
    post_id = parts[1] if len(parts) > 1 else ""
    meta    = load_post(post_id)

    if not meta:
        try:
            bot.edit_message_text(
                "⚠️ Post não encontrado — pode já ter sido processado.",
                call.message.chat.id, call.message.message_id,
            )
        except Exception:
            pass
        return

    if action == "approve":
        try:
            bot.edit_message_text(
                "⏳ Publicando no Instagram...",
                call.message.chat.id, call.message.message_id,
            )
        except Exception:
            pass
        try:
            ig_id = publish_post(post_id, meta)
            bot.send_message(
                call.message.chat.id,
                f"Publicado com sucesso!\n\nPost ID: {ig_id}",
            )
        except Exception as e:
            topic = meta.get("topic", "")
            err   = str(e)[:300]   # truncar para evitar mensagem gigante
            try:
                bot.send_message(
                    call.message.chat.id,
                    f"Erro ao publicar:\n{err}\n\nDeseja gerar um novo carrossel?",
                    reply_markup=_novo_btn(post_id, topic),
                )
            except Exception:
                # fallback sem markup se a mensagem falhar
                bot.send_message(
                    call.message.chat.id,
                    "Erro ao publicar. Use /novo para gerar um novo carrossel.",
                )

    elif action == "reject":
        avoided_topic = meta.get("topic", "")
        delete_post(post_id)
        try:
            bot.edit_message_text(
                "🗑️ Rejeitado. Gerando novo carrossel...",
                call.message.chat.id, call.message.message_id,
            )
        except Exception:
            pass
        threading.Thread(
            target=regenerate_in_background,
            args=(call.message.chat.id, avoided_topic),
            daemon=True,
        ).start()


@bot.message_handler(commands=["novo"])
def cmd_novo(message):
    bot.reply_to(message, "🔄 Gerando novo carrossel...")
    threading.Thread(
        target=regenerate_in_background,
        args=(message.chat.id, ""),
        daemon=True,
    ).start()


@bot.message_handler(commands=["status"])
def status(message):
    from src.post_manager import list_pending_posts
    posts = list_pending_posts()
    if not posts:
        bot.reply_to(message, "✅ Nenhum post pendente.")
    else:
        lines = [f"📋 *{len(posts)} post(s) pendente(s):*\n"]
        for p in posts:
            lines.append(f"• `{p['id']}` — {p['topic'][:50]}")
        bot.reply_to(message, "\n".join(lines), parse_mode="Markdown")


@bot.message_handler(commands=["start", "help"])
def start(message):
    bot.reply_to(
        message,
        "🤖 *Instagram Bot — IA Generativa*\n\n"
        "Quando um carrossel for gerado, você receberá as imagens aqui "
        "com botões para *Publicar* ou *Rejeitar*.\n\n"
        "Comandos:\n"
        "/status — posts pendentes\n"
        "/novo — gerar novo carrossel agora",
        parse_mode="Markdown",
    )


if __name__ == "__main__":
    console.print(Panel.fit("[bold yellow]Bot de aprovacao iniciado![/bold yellow]"))
    console.print("Aguardando aprovações no Telegram...\n")
    console.print("[dim]Pressione Ctrl+C para parar[/dim]")
    bot.infinity_polling()
