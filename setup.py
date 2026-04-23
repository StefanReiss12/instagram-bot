"""
setup.py — Verifica e configura o ambiente inicial.

Uso:
    python setup.py
"""

import os
import sys
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
from rich import box

console = Console()

ENV_FILE = ".env"
ENV_EXAMPLE = ".env.example"


def check_env():
    """Verifica se o .env existe e está configurado."""
    if not os.path.exists(ENV_FILE):
        console.print(f"[yellow]Arquivo .env não encontrado. Criando a partir do exemplo...[/yellow]")
        with open(ENV_EXAMPLE) as f:
            content = f.read()
        with open(ENV_FILE, "w") as f:
            f.write(content)

    from dotenv import load_dotenv
    load_dotenv()

    checks = {
        "ANTHROPIC_API_KEY": os.getenv("ANTHROPIC_API_KEY"),
        "INSTAGRAM_ACCESS_TOKEN": os.getenv("INSTAGRAM_ACCESS_TOKEN"),
        "INSTAGRAM_USER_ID": os.getenv("INSTAGRAM_USER_ID"),
        "IMGBB_API_KEY": os.getenv("IMGBB_API_KEY"),
    }

    table = Table(box=box.SIMPLE, show_header=True, header_style="bold yellow")
    table.add_column("Variável", width=30)
    table.add_column("Status", width=15)
    table.add_column("Valor (parcial)", width=30)

    all_ok = True
    for key, value in checks.items():
        if value and value != f"sua_chave_aqui" and value != "seu_token_aqui" and value != "seu_user_id_aqui":
            status = "[green]✓ OK[/green]"
            display = value[:8] + "..." if len(value) > 8 else value
        else:
            status = "[red]✗ FALTA[/red]"
            display = "[dim]não configurado[/dim]"
            all_ok = False

        table.add_row(key, status, display)

    console.print(table)
    return all_ok


def install_deps():
    """Instala as dependências."""
    console.print("\n[bold]Instalando dependências...[/bold]")
    os.system(f"{sys.executable} -m pip install -r requirements.txt -q")
    console.print("[green]✓ Dependências instaladas![/green]")


def run():
    console.print(Panel.fit("⚙️  [bold yellow]Setup — Instagram Bot IA Generativa[/bold yellow]"))

    # 1. Instalar deps
    install_deps()

    # 2. Verificar .env
    console.print("\n[bold]Verificando credenciais...[/bold]\n")
    all_ok = check_env()

    if not all_ok:
        console.print(Panel(
            "[bold yellow]Configure as variáveis no arquivo [white].env[/white][/bold yellow]\n\n"
            "Consulte o GUIA.md para obter cada credencial:\n\n"
            "[bold]1.[/bold] ANTHROPIC_API_KEY  → console.anthropic.com\n"
            "[bold]2.[/bold] INSTAGRAM_ACCESS_TOKEN + USER_ID → Meta for Developers\n"
            "[bold]3.[/bold] IMGBB_API_KEY → imgbb.com/api\n\n"
            "Depois execute [yellow]python setup.py[/yellow] novamente para verificar.",
            title="Ação necessária",
            border_style="yellow",
        ))
    else:
        console.print(Panel(
            "[bold green]✓ Tudo configurado![/bold green]\n\n"
            "Comandos disponíveis:\n\n"
            "  [yellow]python main.py[/yellow]         → Gera um carrossel agora\n"
            "  [yellow]python approve.py[/yellow]      → Revisa e publica posts\n"
            "  [yellow]python scheduler.py[/yellow]    → Inicia o agendador automático\n"
            "  [yellow]python scheduler.py --now[/yellow] → Testa a geração imediatamente",
            title="Pronto para usar!",
            border_style="green",
        ))


if __name__ == "__main__":
    run()
