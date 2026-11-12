import os
import logging

def setup_tracing():
    """
    Настройка трассировки LLM-вызовов.
    В baseline мы логируем в консоль, но здесь задаем конфигурацию для SDK.
    """
    tracing_enabled = os.getenv("LLM_TRACING_ENABLED", "true").lower() == "true"
    
    if tracing_enabled:
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        logging.info("LLM Tracing initialized")
    else:
        logging.info("LLM Tracing disabled")

# Пример интеграции с Langfuse или LangSmith (заглушка для лабы)
def log_to_dashboard(trace_data: dict):
    """
    Здесь в будущем будет отправка в Langfuse/LangSmith.
    Пока просто пишет в лог.
    """
    logging.info(f"Trace: {trace_data}")
