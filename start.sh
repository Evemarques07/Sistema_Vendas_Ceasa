#!/bin/bash

echo "🚀 Backend de Vendas CEASA"
echo "=========================="
echo ""

# Create database if it doesn't exist
echo "📦 Criando estrutura de banco de dados..."

# Create initial migration
echo "🔄 Criando migração inicial..."
alembic revision --autogenerate -m "Initial migration"

# Apply migrations
echo "⬆️ Aplicando migrações..."
alembic upgrade head

echo ""
echo "✅ Configuração do banco concluída!"
echo ""

# Start server
echo "🌟 Iniciando servidor FastAPI..."
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
