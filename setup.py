import sys
from cx_Freeze import setup, Executable

build_exe_options = {
    "packages": ["os", "sys", "PySide6", "openai", "anthropic"],
    "include_files": [], 
}

base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(
    name="myLLM",
    version="0.2",
    description="GPT app",
    options={"build_exe": build_exe_options},
    executables=[Executable("myLLM.py", base=base)],
)
