@echo off
echo ============================================================
echo   DIABETES MULTI-AGENT AI SUPPORT SYSTEM
echo ============================================================
echo Starting Backend, Frontend, and Jupyter Notebooks...
start cmd /k "run_backend.bat"
start cmd /k "run_frontend.bat"
start cmd /k "run_notebooks.bat"
echo Services launched!
echo - Web App UI:        http://localhost:5173
echo - FastAPI Backend:   http://localhost:8000/docs
echo - Jupyter Notebooks: http://127.0.0.1:8889/tree
