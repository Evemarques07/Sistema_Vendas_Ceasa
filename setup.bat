@echo off
REM Script de inicialização do projeto para Windows
REM Este script facilita a configuração inicial em qualquer ambiente

echo 🚀 Inicializando Sistema de Vendas CEASA
echo ======================================

REM Verificar se Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python não encontrado. Instale o Python 3.8+ primeiro.
    pause
    exit /b 1
)

echo ✅ Python encontrado
python --version

REM Verificar se está em um ambiente virtual
if "%VIRTUAL_ENV%"=="" (
    echo ⚠️  Você não está em um ambiente virtual.
    echo 📋 Criando ambiente virtual...
    
    python -m venv venv
    call venv\Scripts\activate.bat
    
    echo ✅ Ambiente virtual criado e ativado
) else (
    echo ✅ Ambiente virtual já ativo: %VIRTUAL_ENV%
)

REM Instalar dependências
echo 📦 Instalando dependências...
python -m pip install --upgrade pip
pip install -r requirements.txt

REM Verificar se arquivo .env existe
if not exist .env (
    echo 📝 Criando arquivo .env...
    copy .env.example .env
    echo ⚠️  IMPORTANTE: Edite o arquivo .env com suas configurações!
    echo    - Configure a DATABASE_URL
    echo    - Altere a SECRET_KEY para produção
) else (
    echo ✅ Arquivo .env já existe
)

echo.
echo 🎯 Próximos passos:
echo 1. Configure o banco de dados (MySQL)
echo 2. Edite o arquivo .env com suas configurações
echo 3. Execute as migrações: alembic upgrade head
echo 4. Inicialize os dados: python init_db.py
echo 5. Inicie o servidor: uvicorn app.main:app --reload
echo.
echo 📚 Documentação: http://localhost:8000/docs
echo ✅ Setup inicial concluído!
pause
