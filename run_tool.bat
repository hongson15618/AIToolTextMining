@echo off
chcp 65001 > nul
title CONG CU LAM SACH VA LOC DU LIEU EXCEL (NLP TIENG VIET)
echo ====================================================================
echo        CONG CU LAM SACH VA LOC DU LIEU EXCEL (NLP TIENG VIET)
echo                     (Chuan quy trinh 4 buoc UEH)
echo ====================================================================
echo.
echo [1/2] Dang kiem tra va don dep cong ket noi 8501...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8501') do (
    taskkill /f /pid %%a >nul 2>&1
)
echo [2/2] Dang khoi dong ung dung Web tren trinh duyet...
echo.
cd /d "C:\Users\ADMIN\ai_mkt_tool"
python -m streamlit run app.py --server.port 8501 --server.headless false --browser.gatherUsageStats false
pause

