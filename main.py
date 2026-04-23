"""
main.py — Gera carrossel, envia para aprovação e aguarda resposta via Telegram.

Uso:
    py main.py                      # tópico automático
    py main.py "Meu tópico aqui"    # tópico personalizado
    py main.py --bot                # apenas inicia o bot (modo contínuo)
"""
import sys, os, json, threading
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()


def run(topic: str = None):
    from src.content_generator import generate_carousel_content
    from src.image_creator import create_carousel_images
    from src.telegram_approval import send_for_approval
    from src.config import PENDING_DIR

    console.print(Panel.fit("[bold yellow]Instagram Bot - IA Generativa[/bold yellow]"))

    # 1. Gerar conteúdo
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as p:
        task = p.add_task("Gerando conteúdo viral com Claude...", total=None)
        carousel_data = generate_carousel_content(topic)
        p.remove_task(task)

    console.print(f"\n[bold yellow]Tópico:[/bold yellow] {carousel_data['topic']}\n")

    # 2. Criar pasta com ID único
    post_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    post_dir = os.path.join(PENDING_DIR, post_id)
    os.makedirs(post_dir, exist_ok=True)

    # 3. Criar imagens
    console.print("[bold]Criando slides profissionais...[/bold]")
    image_paths = create_carousel_images(carousel_data, post_dir)

    # 4. Salvar meta.json
    from src.image_creator import THEMES
    from src.config import OUTPUT_DIR
    import json as _json
    _counter_path = os.path.join(OUTPUT_DIR, "design_counter.json")
    try:
        with open(_counter_path, encoding="utf-8") as _f:
            _last_theme = _json.load(_f).get("last_used", "classic")
    except Exception:
        _last_theme = "classic"
    meta = {
        "id": post_id,
        "created_at": datetime.now().isoformat(),
        "status": "pending",
        "topic": carousel_data.get("topic", ""),
        "caption": carousel_data.get("caption", ""),
        "slides": carousel_data.get("slides", []),
        "image_paths": image_paths,
        "design_theme": _last_theme,
    }
    with open(os.path.join(post_dir, "meta.json"), "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

    # 5. Enviar para Telegram
    console.print("\n[bold]Enviando para aprovação no Telegram...[/bold]")
    send_for_approval(post_id, carousel_data, image_paths)

    console.print(
        Panel(
            f"[bold green]Carrossel enviado![/bold green]\n\n"
            f"Aguardando sua decisão no Telegram...\n\n"
            f"ID: [dim]{post_id}[/dim]",
            title="Aguardando aprovação",
        )
    )

    # 6. Iniciar bot polling para receber os cliques dos botões
    console.print("[dim]Bot ativo — aguardando clique em Publicar ou Rejeitar...[/dim]")
    _start_bot()


def _start_bot(timeout_seconds: int = 1800):
    """Inicia o polling do Telegram. Para após timeout_seconds (padrão 30 min)."""
    import bot as bot_module
    console.print(f"[dim]Bot ativo por até {timeout_seconds // 60} min. Pressione Ctrl+C para encerrar[/dim]\n")
    timer = threading.Timer(timeout_seconds, bot_module.bot.stop_polling)
    timer.start()
    try:
        bot_module.bot.infinity_polling(timeout=30, long_polling_timeout=20)
    finally:
        timer.cancel()


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--bot":
        # Modo contínuo — apenas o bot, sem gerar conteúdo
        console.print(Panel.fit("[bold yellow]Bot de aprovacao iniciado (modo continuo)[/bold yellow]"))
        console.print("[dim]Pressione Ctrl+C para parar[/dim]\n")
        _start_bot()
    else:
        topic = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else None
        run(topic)
