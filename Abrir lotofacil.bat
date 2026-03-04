@echo off
cd /d %~dp0

echo ================================
echo LOTOFACIL PRO - INICIALIZANDO
echo ================================

echo.
echo Ativando ambiente virtual...
call venv\Scripts\activate

echo.
echo Atualizando repositorio...
git pull

echo.
echo Ambiente pronto.
echo.

cmd