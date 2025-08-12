"""
Script para inicializar dados básicos do sistema
Cria um usuário administrador padrão e alguns dados de exemplo
"""

import asyncio
from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine, Base
from app.core.security import get_password_hash
from app.models.usuario import Usuario
from app.core.enums import TipoUsuario
from app.models.cliente import Cliente
from app.models.produto import Produto
from app.core.enums import TipoMedida
from decimal import Decimal

def init_db():
    """Inicializar banco de dados com dados básicos"""
    print("🔧 Inicializando banco de dados...")
    
    # Criar todas as tabelas
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        # Verificar se já existem usuários
        existing_users = db.query(Usuario).count()
        
        if existing_users == 0:
            print("👤 Criando usuários padrão...")
            
            # Criar usuário administrador
            admin_user = Usuario(
                nome="Administrador",
                email="admin@ceasa.com",
                senha_hash=get_password_hash("admin123"),
                tipo=TipoUsuario.ADMINISTRADOR,
                ativo=True
            )
            db.add(admin_user)
            print("✅ Usuário ADMIN criado - Email: admin@ceasa.com, Senha: admin123")
            
            # Criar usuário funcionário/operador
            funcionario_user = Usuario(
                nome="Funcionário Operador",
                email="funcionario@ceasa.com",
                senha_hash=get_password_hash("func123"),
                tipo=TipoUsuario.FUNCIONARIO,
                ativo=True
            )
            db.add(funcionario_user)
            print("✅ Usuário FUNCIONÁRIO criado - Email: funcionario@ceasa.com, Senha: func123")
        else:
            print("ℹ️ Usuários já existem no sistema")
        
        # Salvar todas as mudanças
        db.commit()
        print("💾 Dados salvos com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro ao inicializar dados: {e}")
        db.rollback()
    finally:
        db.close()

def main():
    """Função principal"""
    print("🚀 Inicializando Sistema de Vendas CEASA")
    print("=" * 40)
    
    try:
        init_db()
        print("\n✅ Inicialização concluída com sucesso!")
        print("\n📋 Dados criados:")
        print("   👤 Usuário ADMIN: admin@ceasa.com (senha: admin123)")
        print("   👷 Usuário FUNCIONÁRIO: funcionario@ceasa.com (senha: func123)")
        print("\n🔐 Perfis de acesso:")
        print("   👨‍💼 ADMIN: Cria vendas, gerencia sistema, relatórios")
        print("   👷 FUNCIONÁRIO: Separa pedidos, atualiza quantidades reais")
        print("\n🌐 Para iniciar o servidor, execute:")
        print("   uvicorn app.main:app --reload")
        print("\n📚 Documentação da API disponível em:")
        print("   http://localhost:8000/docs")
        
    except Exception as e:
        print(f"\n❌ Erro durante a inicialização: {e}")
        print("\n🔧 Verifique se:")
        print("   - O banco de dados está rodando")
        print("   - As variáveis de ambiente estão configuradas")
        print("   - As dependências estão instaladas")

if __name__ == "__main__":
    main()
