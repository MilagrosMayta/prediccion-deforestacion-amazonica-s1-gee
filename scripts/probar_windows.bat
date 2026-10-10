@echo off
setlocal
call .venv\Scripts\activate
python -m compileall -q src
pytest
