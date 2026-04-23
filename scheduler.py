"""
scheduler.py — Agendador automático de geração de carrosseis.

Uso:
    python scheduler.py          # inicia o agendador
    python scheduler.py --now    # executa imediatamente (teste)
"""

import sys
import os
import subprocess
import logging
from datetime import datetime
from zoneinfo import ZoneInfo
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from src.config import SCHEDULE_DAYS, SCHEDULE_HOUR, SCHEDULE_MINUTE

logging.basicConfig(level=logging.WARNING)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PYTHON   = sys.executable
TZ = ZoneInfo("America/Sao_Paulo")


def generate_job():
    """Abre main.py numa janela CMD separada que permanece aberta."""
    print(f"\nAgendador: iniciando gerador de carrossel ({datetime.now(TZ).strftime('%H:%M:%S')})...")
    bat = os.path.join(BASE_DIR, "run_main.bat")
    subprocess.Popen(
        ["cmd", "/k", bat],
        cwd=BASE_DIR,
        creationflags=subprocess.CREATE_NEW_CONSOLE,
    )


def _should_run_now():
    """Retorna True se o horário de hoje já passou (computador ligou tarde)."""
    now = datetime.now(TZ)
    scheduled_today = now.replace(hour=SCHEDULE_HOUR, minute=SCHEDULE_MINUTE, second=0, microsecond=0)
    return now >= scheduled_today


def start_scheduler():
    # Verifica se já passou das 17:30 hoje e ainda não rodou
    if _should_run_now():
        print("Agendador: horário já passou hoje — rodando agora...")
        generate_job()

    scheduler = BlockingScheduler(timezone="America/Sao_Paulo")

    days_str = ",".join(str(d) for d in SCHEDULE_DAYS)
    trigger = CronTrigger(
        day_of_week=days_str,
        hour=SCHEDULE_HOUR,
        minute=SCHEDULE_MINUTE,
        timezone="America/Sao_Paulo",
    )

    scheduler.add_job(generate_job, trigger, id="carousel_generator")

    next_run = trigger.get_next_fire_time(None, datetime.now(TZ))
    print(f"\n Agendador iniciado!")
    print(f"  Horário: {SCHEDULE_HOUR:02d}:{SCHEDULE_MINUTE:02d}")
    print(f"  Próxima execução: {next_run.strftime('%d/%m/%Y %H:%M')}")
    print(f"\n  Pressione Ctrl+C para parar\n")

    try:
        scheduler.start()
    except KeyboardInterrupt:
        print("\nAgendador encerrado.")


if __name__ == "__main__":
    if "--now" in sys.argv:
        print("Executando geração imediata (teste)...")
        generate_job()
    else:
        start_scheduler()
