from pathlib import Path

version = "0.2.0"
json_path = "config.json"
db_path = "llm_client.db"
log_path = Path("log/llm_app.log")
deliminator = ' ----- '
window_title = f"myLLM v{version}"
n_history = 100
log_backup_count = 3
log_max_bytes = 1000000