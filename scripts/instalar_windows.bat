@echo off
setlocal
python -m venv .venv
call .venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -e ".[local,ml,dev]"
echo.
echo Instalacion completada.
echo Active el entorno con: .venv\Scripts\activate
