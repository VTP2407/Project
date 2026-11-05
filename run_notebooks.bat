@echo off
echo ============================================================
echo   DIABETES AI SYSTEM - JUPYTER NOTEBOOKS (LOCALHOST)
echo ============================================================
echo Opening Jupyter Notebook on localhost...
cd ml-training\notebooks
start "" "http://127.0.0.1:8889/tree"
python -m jupyter notebook --ip=127.0.0.1 --port=8889 --no-browser --IdentityProvider.token="" --ServerApp.disable_check_xsrf=True
