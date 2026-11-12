import os
import logging
import json

def setup_tracing():
    """Инициализация логирования."""
    tracing_enabled = os.getenv("LLM_TRACING_ENABLED", "true").lower() == "true"
    if tracing_enabled:
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

def log_to_dashboard(trace_data: dict):
    """Запись полного трейса в лог."""
    logging.info(f"LLM_TRACE: {json.dumps(trace_data, ensure_ascii=False)}")
