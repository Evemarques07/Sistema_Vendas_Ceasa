#!/bin/bash

# Script de inicialização do projeto
# Este script facilita a configuração inicial em qualquer ambiente

echo "🚀 Inicializando Sistema de Vendas CEASA"
echo "======================================"

# Verificar se Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 não encontrado. Instale o Python 3.8+ primeiro."
    exit 1
fi

echo "✅ Python encontrado: $(python3 --version)"

# Verificar se está em um ambiente virtual
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "⚠️  Você não está em um ambiente virtual."
    echo "📋 Criando ambiente virtual..."
    
    python3 -m venv venv
    
    # Ativar ambiente virtual baseado no OS
    if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
        source venv/Scripts/activate
    else
        source venv/bin/activate
    fi
    
    echo "✅ Ambiente virtual criado e ativado"
else
    echo "✅ Ambiente virtual já ativo: $VIRTUAL_ENV"
fi

# Instalar dependências
echo "📦 Instalando dependências..."
pip install --upgrade pip
pip install -r requirements.txt

# Verificar se arquivo .env existe
if [ ! -f .env ]; then
    echo "📝 Criando arquivo .env..."
    cp .env.example .env
    echo "⚠️  IMPORTANTE: Edite o arquivo .env com suas configurações!"
    echo "   - Configure a DATABASE_URL"
    echo "   - Altere a SECRET_KEY para produção"
else
    echo "✅ Arquivo .env já existe"
fi

# Verificar conexão com banco (opcional)
echo "🔌 Para testar a conexão com o banco, execute:"
echo "   python -c \"from app.core.database import engine; print('✅ Conexão OK' if engine.connect() else '❌ Erro de conexão')\""

echo ""
echo "🎯 Próximos passos:"
echo "1. Configure o banco de dados (MySQL)"
echo "2. Edite o arquivo .env com suas configurações"
echo "3. Execute as migrações: alembic upgrade head"
echo "4. Inicialize os dados: python init_db.py"
echo "5. Inicie o servidor: uvicorn app.main:app --reload"
echo ""
echo "📚 Documentação: http://localhost:8000/docs"
echo "✅ Setup inicial concluído!"
