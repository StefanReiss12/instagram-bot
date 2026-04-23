"""
approve.py — Interface de aprovação de posts pendentes.

Uso:
    python approve.py
"""

import os
import subprocess
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich import box

console = Console()


def open_images(image_paths: list[str]):
    """Abre as imagens para visualização."""
    for path in image_paths[:3]:  # Abre os 3 primeiros slides
        if os.path.exists(path):
            try:
                os.startfile(path)  # Windows
            except Exception:
                subprocess.run(["xdg-open", path], check=False)


def show_post_details(post: dict):
    """Mostra detalhes de um post para aprovação."""
    console.print()
    console.print(Panel(
        f"[bold yellow]{post['topic']}[/bold yellow]",
        title=f"Post ID: {post['id']}",
        subtitle=f"Criado em: {post['created_at'][:16]}",
    ))

    # Slides
    table = Table(box=box.SIMPLE, show_header=True, header_style="bold yellow")
    table.add_column("Slide", style="dim", width=6)
    table.add_column("Tipo", width=10)
    table.add_column("Conteúdo")

    for slide in post.get("slides", []):
        slide_type = slide.get("type", "")
        if slide_type == "hook":
            content = f"[bold]{slide.get('title', '')}[/bold]\n[dim]{slide.get('subtitle', '')}[/dim]"
        elif slide_type == "cta":
            content = f"[bold]{slide.get('headline', '')}[/bold]\n[yellow]{slide.get('cta', '')}[/yellow]"
        else:
            content = f"[bold]{slide.get('headline', '')}[/bold]\n{slide.get('body', '')}"

        table.add_row(str(slide.get("slide_number", "")), slide_type, content)

    console.print(table)

    # Legenda
    console.print(Panel(
        post.get("caption", "")[:500] + ("..." if len(post.get("caption", "")) > 500 else ""),
        title="Legenda",
        style="dim",
    ))


def post_to_instagram(post: dict):
    """Faz upload das imagens e publica no Instagram."""
    from src.image_uploader import upload_all_images
    from src.instagram_api import post_carousel
    from src.post_manager import mark_as_posted

    image_paths = post.get("image_paths", [])

    console.print("\n[bold]Fazendo upload das imagens...[/bold]")
    image_urls = upload_all_images(image_paths)

    console.print("\n[bold]Publicando no Instagram...[/bold]")
    instagram_post_id = post_carousel(image_urls, post["caption"])

    mark_as_posted(post["id"], instagram_post_id)

    console.print(Panel(
        f"[bold green]✓ Publicado com sucesso![/bold green]\n"
        f"Instagram Post ID: [yellow]{instagram_post_id}[/yellow]",
        title="Publicado!",
    ))


def run():
    from src.post_manager import list_pending_posts, delete_pending_post

    console.print(Panel.fit("📋 [bold yellow]Aprovação de Posts[/bold yellow]"))

    posts = list_pending_posts()

    if not posts:
        console.print("\n[dim]Nenhum post pendente. Execute [yellow]python main.py[/yellow] para gerar.[/dim]\n")
        return

    console.print(f"\n[bold]{len(posts)} post(s) pendente(s)[/bold]\n")

    for i, post in enumerate(posts):
        console.print(f"[bold yellow][{i + 1}][/bold yellow] {post['topic'][:60]}  [dim]{post['id']}[/dim]")

    console.print()
    choice = Prompt.ask(
        "Selecione o número do post (ou [bold]q[/bold] para sair)",
        default="1",
    )

    if choice.lower() == "q":
        return

    try:
        idx = int(choice) - 1
        post = posts[idx]
    except (ValueError, IndexError):
        console.print("[red]Seleção inválida[/red]")
        return

    show_post_details(post)

    # Opção de ver imagens
    if Confirm.ask("\nAbrir imagens para visualizar?", default=True):
        open_images(post.get("image_paths", []))

    console.print()
    action = Prompt.ask(
        "O que deseja fazer?",
        choices=["publicar", "rejeitar", "voltar"],
        default="voltar",
    )

    if action == "publicar":
        if Confirm.ask("[bold red]Confirma publicação no Instagram?[/bold red]", default=False):
            post_to_instagram(post)

    elif action == "rejeitar":
        if Confirm.ask("[bold red]Confirma exclusão deste post?[/bold red]", default=False):
            delete_pending_post(post["id"])
            console.print("[dim]Post removido.[/dim]")


if __name__ == "__main__":
    run()
