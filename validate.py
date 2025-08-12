#!/usr/bin/env python3
"""
Script de validação do projeto
Verifica se todas as dependências e configurações estão corretas
"""

import sys
import os
import subprocess
from pathlib import Path

def check_python_version():
    """Verificar versão do Python"""
    print("🐍 Verificando versão do Python...")
    version = sys.version_info
    
    if version.major == 3 and version.minor >= 8:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} - OK")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} - Requer Python 3.8+")
        return False

def check_virtual_env():
    """Verificar se está em ambiente virtual"""
    print("🔧 Verificando ambiente virtual...")
    
    if os.environ.get('VIRTUAL_ENV'):
        print(f"✅ Ambiente virtual ativo: {os.environ.get('VIRTUAL_ENV')}")
        return True
    else:
        print("⚠️  Não está em um ambiente virtual (recomendado usar venv)")
        return False

def check_dependencies():
    """Verificar dependências instaladas"""
    print("📦 Verificando dependências...")
    
    required_packages = [
        'fastapi',
        'sqlalchemy', 
        'alembic',
        'pymysql',
        'uvicorn',
        'pydantic',
        'python-jose',
        'passlib'
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - FALTANDO")
            missing.append(package)
    
    return len(missing) == 0, missing

def check_env_file():
    """Verificar arquivo .env"""
    print("📝 Verificando arquivo .env...")
    
    env_path = Path('.env')
    env_example_path = Path('.env.example')
    
    if not env_path.exists():
        if env_example_path.exists():
            print("⚠️  Arquivo .env não encontrado, mas .env.example existe")
            print("💡 Execute: cp .env.example .env")
            return False
        else:
            print("❌ Nem .env nem .env.example encontrados")
            return False
    
    # Verificar variáveis essenciais
    with open(env_path) as f:
        content = f.read()
        
    required_vars = [
        'DATABASE_URL',
        'SECRET_KEY'
    ]
    
    missing_vars = []
    for var in required_vars:
        if var not in content:
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Variáveis faltando no .env: {', '.join(missing_vars)}")
        return False
    
    print("✅ Arquivo .env configurado")
    return True

def check_database_connection():
    """Verificar conexão com banco de dados"""
    print("🔌 Verificando conexão com banco...")
    
    try:
        from app.core.database import engine
        with engine.connect() as conn:
            print("✅ Conexão com banco de dados - OK")
            return True
    except Exception as e:
        print(f"❌ Erro na conexão: {str(e)}")
        print("💡 Verifique se o MySQL está rodando e as configurações estão corretas")
        return False

def check_migrations():
    """Verificar se migrações foram aplicadas"""
    print("🗄️ Verificando migrações...")
    
    try:
        result = subprocess.run(['alembic', 'current'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            current = result.stdout.strip()
            if current and 'head' in current:
                print("✅ Migrações aplicadas")
                return True
            else:
                print("⚠️  Migrações não aplicadas")
                print("💡 Execute: alembic upgrade head")
                return False
        else:
            print("❌ Erro ao verificar migrações")
            return False
    except FileNotFoundError:
        print("❌ Alembic não encontrado")
        return False

def check_project_structure():
    """Verificar estrutura do projeto"""
    print("📁 Verificando estrutura do projeto...")
    
    required_files = [
        'app/main.py',
        'app/core/database.py',
        'app/core/config.py',
        'requirements.txt',
        'alembic.ini',
        'init_db.py'
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ Arquivos faltando: {', '.join(missing_files)}")
        return False
    
    print("✅ Estrutura do projeto - OK")
    return True

def main():
    """Função principal"""
    print("🔍 Sistema de Validação - Vendas CEASA")
    print("=" * 50)
    
    checks = [
        ("Versão Python", check_python_version),
        ("Ambiente Virtual", check_virtual_env), 
        ("Estrutura do Projeto", check_project_structure),
        ("Dependências", lambda: check_dependencies()[0]),
        ("Arquivo .env", check_env_file),
        ("Conexão com Banco", check_database_connection),
        ("Migrações", check_migrations)
    ]
    
    results = []
    warnings = 0
    
    for name, check_func in checks:
        print(f"\n--- {name} ---")
        try:
            result = check_func()
            results.append((name, result))
            if not result and name == "Ambiente Virtual":
                warnings += 1
        except Exception as e:
            print(f"❌ Erro durante verificação: {e}")
            results.append((name, False))
    
    print("\n" + "=" * 50)
    print("📊 RESUMO DA VALIDAÇÃO")
    print("=" * 50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"{name:<20} {status}")
    
    print(f"\nResultado: {passed}/{total} verificações passaram")
    
    if warnings > 0:
        print(f"⚠️  {warnings} avisos (não críticos)")
    
    if passed == total:
        print("\n🎉 PROJETO PRONTO PARA EXECUÇÃO!")
        print("💡 Execute: uvicorn app.main:app --reload")
    elif passed >= total - warnings:
        print("\n✅ PROJETO QUASE PRONTO!")
        print("💡 Corrija os problemas acima e tente novamente")
    else:
        print("\n❌ PROJETO NÃO ESTÁ PRONTO")
        print("💡 Corrija os problemas listados acima")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
