#!/usr/bin/env python3
"""
Script para testar o endpoint de vendas com cálculo de lucro bruto
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def usar_token_existente():
    """Usa o token fornecido pelo usuário"""
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NTQ5MjMxNTAsInN1YiI6ImFkbWluQGNlYXNhLmNvbSJ9.VOgTdljzgQUbh4VM8NFr5jkO-27PbgYHC2P9BKhtLYo"
    print("✅ Usando token fornecido!")
    return token

def login():
    """Faz login e retorna o token"""
    login_data = {
        "email": "admin@ceasa.com",
        "senha": "admin123"
    }
    
    response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
    
    if response.status_code == 200:
        token = response.json()["access_token"]
        print("✅ Login realizado com sucesso!")
        return token
    else:
        print(f"❌ Erro no login: {response.status_code}")
        print(response.text)
        return None

def listar_vendas(token):
    """Lista todas as vendas"""
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(f"{BASE_URL}/api/vendas/", headers=headers)
    
    if response.status_code == 200:
        vendas = response.json()
        print(f"\n📋 {len(vendas)} vendas encontradas:")
        for venda in vendas:
            print(f"  - ID: {venda['id']}, Cliente: {venda['cliente']['nome']}, Total: R$ {venda['total_venda']:.2f}")
        return vendas
    else:
        print(f"❌ Erro ao listar vendas: {response.status_code}")
        return []

def testar_venda_detalhada(token, venda_id):
    """Testa o endpoint de venda com lucro bruto"""
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(f"{BASE_URL}/api/vendas/{venda_id}", headers=headers)
    
    if response.status_code == 200:
        venda = response.json()
        
        print(f"\n🔍 Detalhes da Venda ID {venda_id}:")
        print(f"Cliente: {venda['cliente']['nome']}")
        print(f"Data: {venda['data_venda']}")
        print(f"Total da Venda: R$ {venda['total_venda']:.2f}")
        
        # Verifica se tem dados de lucro bruto
        if 'lucro_bruto' in venda:
            lucro = venda['lucro_bruto']
            print(f"\n💰 Análise Financeira:")
            print(f"Receita Total: R$ {lucro['receita_total']:.2f}")
            print(f"Custo Total: R$ {lucro['custo_total']:.2f}")
            print(f"Lucro Bruto: R$ {lucro['lucro_bruto']:.2f}")
            print(f"Margem Bruta: {lucro['margem_bruta_percentual']:.2f}%")
            
            if 'detalhes_produtos' in lucro:
                print(f"\n📊 Detalhes por Produto:")
                for produto in lucro['detalhes_produtos']:
                    print(f"  - {produto['produto_nome']}: R$ {produto['receita']:.2f} (receita) - R$ {produto['custo']:.2f} (custo) = R$ {produto['lucro']:.2f} (margem: {produto['margem_percentual']:.2f}%)")
        else:
            print("⚠️ Dados de lucro bruto não encontrados")
        
        print(f"\n📄 JSON completo:")
        print(json.dumps(venda, indent=2, ensure_ascii=False))
        
    else:
        print(f"❌ Erro ao buscar venda {venda_id}: {response.status_code}")
        print(response.text)

def main():
    print("🚀 Testando endpoint de vendas com lucro bruto...")
    
    # Usar token fornecido
    token = usar_token_existente()
    if not token:
        # Fallback para login
        token = login()
        if not token:
            return
    
    # Listar vendas
    vendas = listar_vendas(token)
    
    if vendas:
        # Testar primeira venda
        primeira_venda = vendas[0]
        testar_venda_detalhada(token, primeira_venda['id'])
        
        # Testar venda específica (ID 4 se existir)
        venda_4_existe = any(v['id'] == 4 for v in vendas)
        if venda_4_existe:
            print(f"\n{'='*50}")
            testar_venda_detalhada(token, 4)
    else:
        print("❌ Nenhuma venda encontrada para testar")

if __name__ == "__main__":
    main()
