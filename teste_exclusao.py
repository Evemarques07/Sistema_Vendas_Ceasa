#!/usr/bin/env python3
"""
Teste da funcionalidade de exclusão de entradas de estoque
"""

import requests
import json

BASE_URL = "http://localhost:8000"
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NTQ5MjMxNTAsInN1YiI6ImFkbWluQGNlYXNhLmNvbSJ9.VOgTdljzgQUbh4VM8NFr5jkO-27PbgYHC2P9BKhtLYo"

headers = {"Authorization": f"Bearer {TOKEN}"}

def testar_endpoints_exclusao():
    print("🧪 Testando endpoints de exclusão de entradas de estoque")
    
    # 1. Listar entradas deletáveis
    try:
        print("\n1️⃣ Testando listagem de entradas deletáveis...")
        response = requests.get(f"{BASE_URL}/api/estoque/entradas/deletaveis", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            total = data["data"]["total"]
            print(f"✅ Sucesso! {total} entradas podem ser deletadas")
            
            if total > 0:
                primeira_entrada = data["data"]["entradas_deletaveis"][0]
                entrada_id = primeira_entrada["id"]
                produto_nome = primeira_entrada["produto"]["nome"]
                print(f"   - Primeira entrada: ID {entrada_id} ({produto_nome})")
                return entrada_id
        else:
            print(f"❌ Erro: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
    
    return None

def testar_status_exclusao(entrada_id):
    print(f"\n2️⃣ Testando status de exclusão da entrada {entrada_id}...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/estoque/entradas/{entrada_id}/status-exclusao", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            pode_deletar = data["data"]["pode_deletar"]
            motivos = data["data"]["motivos_bloqueio"]
            
            if pode_deletar:
                print("✅ Entrada pode ser deletada!")
                print(f"   - Quantidade: {data['data']['entrada']['quantidade']}")
                print(f"   - Valor: R$ {data['data']['entrada']['valor_total']}")
                return True
            else:
                print("⚠️ Entrada NÃO pode ser deletada")
                for motivo in motivos:
                    print(f"   - {motivo}")
                return False
        else:
            print(f"❌ Erro: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
    
    return False

def testar_exclusao(entrada_id):
    print(f"\n3️⃣ Testando exclusão da entrada {entrada_id}...")
    
    try:
        response = requests.delete(f"{BASE_URL}/api/estoque/entradas/{entrada_id}", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            print("🎉 Entrada deletada com sucesso!")
            print(f"   - Produto ID: {data['data']['entrada_deletada']['produto_id']}")
            print(f"   - Quantidade removida: {data['data']['inventario_atualizado']['quantidade_removida']}")
            print(f"   - Nova quantidade inventário: {data['data']['inventario_atualizado']['quantidade_atual']}")
            return True
        else:
            print(f"❌ Erro na exclusão: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
    
    return False

def main():
    print("🚀 Iniciando testes de exclusão de entradas de estoque...")
    
    # Testar listagem
    entrada_id = testar_endpoints_exclusao()
    
    if entrada_id:
        # Testar status
        pode_deletar = testar_status_exclusao(entrada_id)
        
        if pode_deletar:
            # Confirmar exclusão
            print("\n❓ Deseja realmente deletar esta entrada? (s/N)")
            confirmacao = input().lower()
            
            if confirmacao == 's':
                sucesso = testar_exclusao(entrada_id)
                if sucesso:
                    print("\n✅ Teste completo realizado com sucesso!")
            else:
                print("\n⏭️ Exclusão cancelada pelo usuário")
        else:
            print("\n⚠️ Entrada não pode ser deletada - teste de validação passou!")
    else:
        print("\n📋 Nenhuma entrada deletável encontrada")
    
    print("\n🏁 Testes finalizados!")

if __name__ == "__main__":
    main()
