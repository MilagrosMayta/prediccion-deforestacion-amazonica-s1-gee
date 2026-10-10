@echo off
setlocal
if "%~1"=="" (
  echo Uso: busqueda_ejemplo_windows.bat PROJECT_ID
  exit /b 1
)
call .venv\Scripts\activate
deforest-gee buscar --proyecto "%~1" --config config\busqueda.ejemplo.json
