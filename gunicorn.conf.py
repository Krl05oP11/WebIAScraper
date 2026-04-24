import os

workers = 1        # Un solo worker evita schedulers duplicados
timeout = 120
bind = f"0.0.0.0:{os.getenv('PORT', '8000')}"
preload_app = False
loglevel = "info"
accesslog = "-"    # stdout
errorlog = "-"     # stdout

def post_fork(server, worker):
    """Inicializa el scheduler una vez que el worker está listo."""
    try:
        from src.app import init_scheduler, scrape_and_save_news
        init_scheduler()
    except Exception as e:
        print(f"[gunicorn] Error iniciando scheduler: {e}")
