"""
scheduler.py — Agendador automático de geração de carrosseis.

Uso:
    python scheduler.py            # inicia o agendador (9h e 14h)
    python scheduler.py --now      # executa o carrossel das 9h imediatamente
    python scheduler.py --now-14h  # executa o carrossel das 14h imediatamente
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
TZ       = ZoneInfo("America/Sao_Paulo")

SCHEDULE_14H_HOUR   = 14
SCHEDULE_14H_MINUTE = 0


def _open_cmd(bat_file: str):
    subprocess.Popen(
        ["cmd", "/k", bat_file],
        cwd=BASE_DIR,
        creationflags=subprocess.CREATE_NEW_CONSOLE,
    )


def generate_job_9h():
    print(f"\nAgendador: iniciando carrossel 9h ({datetime.now(TZ).strftime('%H:%M:%S')})...")
    bat = os.path.join(BASE_DIR, "run_main.bat")
    _open_cmd(bat)


def generate_job_14h():
    print(f"\nAgendador: iniciando carrossel 14h ({datetime.now(TZ).strftime('%H:%M:%S')})...")
    bat = os.path.join(BASE_DIR, "run_main_14h.bat")
    _open_cmd(bat)


def start_scheduler():
    now = datetime.now(TZ)

    # Catch-up: se 9h já passou hoje, roda agora
    scheduled_9h = now.replace(hour=SCHEDULE_HOUR, minute=SCHEDULE_MINUTE, second=0, microsecond=0)
    if now >= scheduled_9h:
        print("Agendador: horário das 9h já passou — rodando agora...")
        generate_job_9h()

    scheduler = BlockingScheduler(timezone="America/Sao_Paulo")

    days_str = ",".join(str(d) for d in SCHEDULE_DAYS)

    trigger_9h = CronTrigger(
        day_of_week=days_str,
        hour=SCHEDULE_HOUR,
        minute=SCHEDULE_MINUTE,
        timezone="America/Sao_Paulo",
    )
    trigger_14h = CronTrigger(
        day_of_week=days_str,
        hour=SCHEDULE_14H_HOUR,
        minute=SCHEDULE_14H_MINUTE,
        timezone="America/Sao_Paulo",
    )

    scheduler.add_job(generate_job_9h,  trigger_9h,  id="carousel_9h")
    scheduler.add_job(generate_job_14h, trigger_14h, id="carousel_14h")

    next_9h  = trigger_9h.get_next_fire_time(None, now)
    next_14h = trigger_14h.get_next_fire_time(None, now)

    print(f"\n Agendador iniciado!")
    print(f"  9h  — próxima: {next_9h.strftime('%d/%m/%Y %H:%M')}")
    print(f"  14h — próxima: {next_14h.strftime('%d/%m/%Y %H:%M')}")
    print(f"\n  Pressione Ctrl+C para parar\n")

    try:
        scheduler.start()
    except KeyboardInterrupt:
        print("\nAgendador encerrado.")


if __name__ == "__main__":
    if "--now-14h" in sys.argv:
        print("Executando carrossel 14h imediatamente...")
        generate_job_14h()
    elif "--now" in sys.argv:
        print("Executando carrossel 9h imediatamente...")
        generate_job_9h()
    else:
        start_scheduler()
