@echo off
cd /d %~dp0

echo ================================
echo LOTOFACIL PRO - MODO PROFISSIONAL
echo ================================

echo.
echo [1/5] Ativando ambiente virtual...
if exist venv\Scripts\activate (
    call venv\Scripts\activate
) else (
    echo ERRO: Ambiente virtual nao encontrado!
    pause
    exit
)

echo.
echo [2/5] Buscando atualizacoes remotas...
git fetch

echo.
echo [3/5] Indo para branch v3-core...
git checkout v3-core 2>nul || git checkout -b v3-core origin/v3-core

echo.
echo [4/5] Atualizando repositorio...
git pull

echo.
echo [5/5] Status atual:
git status

echo.
echo =================================
echo Ambiente pronto para trabalhar.
echo =================================
echo.

cmd