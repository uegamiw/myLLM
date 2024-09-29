from pathlib import Path

version = "0.4.0"
json_path = "config.json"
window_geometry = (50, 50, 1200, 950)
db_path = "llm_client.db"
log_path = Path("log/llm_app.log")
deliminator = ' -+-+-+-+- '
window_title = f"myLLM  v{version}"
n_history = 100
log_backup_count = 3
log_max_bytes = 1000000
search_delay = 150
n_prompt_buttons = 5
response_prefix = "[Model's response]:"
spacing = 3
history_table_height = 2
temp_deliminator = " t"
