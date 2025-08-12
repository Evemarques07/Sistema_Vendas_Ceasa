Write-Host "🚀 Backend de Vendas CEASA" -ForegroundColor Green
Write-Host "==========================" -ForegroundColor Green
Write-Host ""

# Check if Docker is running
Write-Host "🐳 Verificando Docker..." -ForegroundColor Yellow
try {
    docker --version | Out-Null
    Write-Host "✅ Docker disponível" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker não está disponível" -ForegroundColor Red
    Write-Host "   Para usar com MySQL, instale o Docker Desktop" -ForegroundColor Yellow
    Write-Host "   Por enquanto, você pode usar SQLite para desenvolvimento" -ForegroundColor Yellow
}

Write-Host ""

# Install dependencies
Write-Host "📦 Instalando dependências..." -ForegroundColor Yellow
pip install -r requirements.txt

Write-Host ""

# Check database connection
Write-Host "🔗 Verificando conexão com banco..." -ForegroundColor Yellow
try {
    python -c "from app.core.database import engine; engine.connect(); print('✅ Conexão com banco estabelecida')"
} catch {
    Write-Host "❌ Erro ao conectar com banco de dados" -ForegroundColor Red
    Write-Host "   Verifique se o MySQL está rodando ou configure SQLite" -ForegroundColor Yellow
    Write-Host "   Para iniciar MySQL com Docker: docker-compose up -d mysql" -ForegroundColor Yellow
}

Write-Host ""

# Start server
Write-Host "🌟 Iniciando servidor FastAPI..." -ForegroundColor Green
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
