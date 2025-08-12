# 📖 Documentação Completa da API - Sistema Vendas CEASA

## 🌐 Base URL

```
http://localhost:8000/api
```

## 📋 Índice

- [Autenticação](#-autenticação)
- [Clientes](#-clientes)
- [Produtos](#-produtos)
- [Vendas](#-vendas)
- [Estoque](#-estoque)
  - [Entradas de Estoque](#get-estoqueentradas)
  - [Inventário](#get-estoqueinventario)
  - [Fluxo de Caixa FIFO](#get-estoquefluxo-caixa)
  - [Relatório de Rentabilidade](#get-estoquerentabilidade)
- [Relatórios Financeiros](#-relatórios-financeiros)
  - [Pagamentos Pendentes](#get-relatoriospagamentos-pendentes)
  - [Histórico de Vendas por Cliente](#get-relatorioshistorico-vendascliente_id)
  - [Resumo Financeiro por Cliente](#get-relatoriosresumo-financeirocliente_id)
  - [Dashboard de Vendas](#get-relatoriosdashboard-vendas)
  - [Clientes Inadimplentes](#get-relatoriosclientes-inadimplentes)
- [Códigos de Resposta](#-códigos-de-resposta)
- [Headers](#-headers-obrigatórios)

---

## 🔐 Autenticação

### POST `/auth/login`

**Descrição**: Realizar login no sistema  
**Autenticação**: Não requerida

**Body (JSON)**:

```json
{
  "email": "admin@ceasa.com",
  "senha": "admin123"
}
```

**Resposta de Sucesso (200)**:

```json
{
  "data": {
    "user": {
      "id": 1,
      "nome": "Administrador",
      "email": "admin@ceasa.com",
      "tipo": "ADMINISTRADOR",
      "ativo": true
    },
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }
}
```

**Resposta de Erro (401)**:

```json
{
  "detail": "Email ou senha incorretos"
}
```

### POST `/auth/logout`

**Descrição**: Fazer logout do sistema  
**Autenticação**: Bearer Token requerido

**Body**: Nenhum

**Resposta de Sucesso (200)**:

```json
{
  "message": "Logout realizado com sucesso"
}
```

### GET `/auth/me`

**Descrição**: Obter dados do usuário atual  
**Autenticação**: Bearer Token requerido

**Parâmetros**: Nenhum

**Resposta de Sucesso (200)**:

```json
{
  "data": {
    "id": 1,
    "nome": "Administrador",
    "email": "admin@ceasa.com",
    "tipo": "ADMINISTRADOR",
    "ativo": true,
    "criado_em": "2025-08-07T13:27:57"
  }
}
```

---

## 👥 Clientes

### GET `/clientes/`

**Descrição**: Listar clientes com filtros e paginação  
**Autenticação**: Bearer Token requerido

**Query Parameters**:

- `skip` (int, opcional): Registros para pular (padrão: 0)
- `limit` (int, opcional): Registros por página (padrão: 20, máx: 100)
- `nome` (string, opcional): Filtrar por nome
- `cpf_ou_cnpj` (string, opcional): Filtrar por CPF/CNPJ
- `ativo` (boolean, opcional): Filtrar por status ativo

**Exemplo de URL**:

```
GET /clientes/?skip=0&limit=10&nome=João&ativo=true
```

**Resposta de Sucesso (200)**:

```json
{
  "data": {
    "clientes": [
      {
        "id": 1,
        "nome": "João Silva",
        "nome_fantasia": null,
        "cpf_ou_cnpj": "123.456.789-00",
        "endereco": "Rua das Flores, 123",
        "ponto_referencia": null,
        "email": "joao@email.com",
        "telefone1": "(11) 99999-1111",
        "telefone2": null,
        "ativo": true,
        "criado_em": "2025-08-07T13:27:57",
        "atualizado_em": null
      }
    ],
    "total": 3,
    "skip": 0,
    "limit": 20
  }
}
```

### GET `/clientes/{cliente_id}`

**Descrição**: Buscar cliente por ID  
**Autenticação**: Bearer Token requerido

**Path Parameters**:

- `cliente_id` (int, obrigatório): ID do cliente

**Resposta de Sucesso (200)**:

```json
{
  "data": {
    "id": 1,
    "nome": "João Silva",
    "nome_fantasia": null,
    "cpf_ou_cnpj": "123.456.789-00",
    "endereco": "Rua das Flores, 123",
    "ponto_referencia": null,
    "email": "joao@email.com",
    "telefone1": "(11) 99999-1111",
    "telefone2": null,
    "ativo": true,
    "criado_em": "2025-08-07T13:27:57",
    "atualizado_em": null
  }
}
```

**Resposta de Erro (404)**:

```json
{
  "detail": "Cliente não encontrado"
}
```

### POST `/clientes/`

**Descrição**: Criar novo cliente  
**Autenticação**: Bearer Token requerido

**Body (JSON)**:

```json
{
  "nome": "Maria Santos", // obrigatório
  "nome_fantasia": "Verduras Maria", // opcional
  "cpf_ou_cnpj": "987.654.321-00", // obrigatório
  "endereco": "Av. Principal, 456", // obrigatório
  "ponto_referencia": "Próximo ao banco", // opcional
  "email": "maria@email.com", // opcional
  "telefone1": "(11) 99999-2222", // obrigatório
  "telefone2": "(11) 3333-4444", // opcional
  "ativo": true // opcional (padrão: true)
}
```

**Resposta de Sucesso (201)**:

```json
{
  "data": {
    "id": 4,
    "nome": "Maria Santos",
    "nome_fantasia": "Verduras Maria",
    "cpf_ou_cnpj": "987.654.321-00",
    "endereco": "Av. Principal, 456",
    "ponto_referencia": "Próximo ao banco",
    "email": "maria@email.com",
    "telefone1": "(11) 99999-2222",
    "telefone2": "(11) 3333-4444",
    "ativo": true,
    "criado_em": "2025-08-07T16:30:00",
    "atualizado_em": null
  }
}
```

**Resposta de Erro (422)**:

```json
{
  "detail": [
    {
      "loc": ["body", "nome"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

### PUT `/clientes/{cliente_id}`

**Descrição**: Atualizar cliente  
**Autenticação**: Bearer Token requerido

**Path Parameters**:

- `cliente_id` (int, obrigatório): ID do cliente

**Body (JSON)** - Todos os campos são opcionais:

```json
{
  "nome": "Maria Santos Silva",
  "email": "maria.silva@email.com",
  "telefone1": "(11) 99999-5555",
  "ativo": false
}
```

**Resposta de Sucesso (200)**:

```json
{
  "data": {
    "id": 1,
    "nome": "Maria Santos Silva",
    "email": "maria.silva@email.com",
    "telefone1": "(11) 99999-5555",
    "ativo": false,
    "atualizado_em": "2025-08-07T16:35:00"
  }
}
```

### DELETE `/clientes/{cliente_id}`

**Descrição**: Excluir cliente  
**Autenticação**: Bearer Token requerido (Admin)

**Path Parameters**:

- `cliente_id` (int, obrigatório): ID do cliente

**Resposta de Sucesso (200)**:

```json
{
  "message": "Cliente excluído com sucesso"
}
```

**Resposta de Erro (403)**:

```json
{
  "detail": "Sem permissão para excluir clientes"
}
```

---

## 🛍️ Produtos

### GET `/produtos/`

**Descrição**: Listar produtos com filtros e paginação  
**Autenticação**: Bearer Token requerido

**Query Parameters**:

- `skip` (int, opcional): Registros para pular (padrão: 0)
- `limit` (int, opcional): Registros por página (padrão: 20, máx: 100)
- `nome` (string, opcional): Filtrar por nome
- `tipo_medida` (string, opcional): Filtrar por tipo de medida
  - Valores: `QUILOGRAMA`, `UNIDADE`, `GRAMA`, `LITRO`
- `ativo` (boolean, opcional): Filtrar por status ativo

**Exemplo de URL**:

```
GET /produtos/?skip=0&limit=10&tipo_medida=QUILOGRAMA&ativo=true
```

**Resposta de Sucesso (200)**:

```json
{
  "data": {
    "produtos": [
      {
        "id": 1,
        "nome": "Tomate",
        "descricao": "Tomate fresco de primeira qualidade",
        "preco_venda": 5.5,
        "tipo_medida": "QUILOGRAMA",
        "estoque_minimo": 10.0,
        "imagem": null,
        "ativo": true,
        "criado_em": "2025-08-07T13:27:57",
        "atualizado_em": null
      }
    ],
    "total": 5,
    "skip": 0,
    "limit": 20
  }
}
```

### GET `/produtos/{produto_id}`

**Descrição**: Buscar produto por ID  
**Autenticação**: Bearer Token requerido

**Path Parameters**:

- `produto_id` (int, obrigatório): ID do produto

**Resposta de Sucesso (200)**:

```json
{
  "data": {
    "id": 1,
    "nome": "Tomate",
    "descricao": "Tomate fresco de primeira qualidade",
    "preco_venda": 5.5,
    "tipo_medida": "QUILOGRAMA",
    "estoque_minimo": 10.0,
    "imagem": null,
    "ativo": true,
    "criado_em": "2025-08-07T13:27:57",
    "atualizado_em": null
  }
}
```

### POST `/produtos/`

**Descrição**: Criar novo produto  
**Autenticação**: Bearer Token requerido

**Body (JSON)**:

```json
{
  "nome": "Alface Crespa", // obrigatório
  "descricao": "Alface crespa orgânica", // opcional
  "preco_venda": 2.5, // obrigatório
  "tipo_medida": "UNIDADE", // obrigatório
  "estoque_minimo": 15.0, // obrigatório
  "ativo": true // opcional (padrão: true)
}
```

**Tipos de Medida Disponíveis**:

- `QUILOGRAMA` - Para produtos vendidos por peso
- `UNIDADE` - Para produtos vendidos por unidade
- `GRAMA` - Para produtos pequenos por peso
- `LITRO` - Para produtos líquidos

**Resposta de Sucesso (201)**:

```json
{
  "data": {
    "id": 6,
    "nome": "Alface Crespa",
    "descricao": "Alface crespa orgânica",
    "preco_venda": 2.5,
    "tipo_medida": "UNIDADE",
    "estoque_minimo": 15.0,
    "imagem": null,
    "ativo": true,
    "criado_em": "2025-08-07T16:40:00",
    "atualizado_em": null
  }
}
```

### PUT `/produtos/{produto_id}`

**Descrição**: Atualizar produto  
**Autenticação**: Bearer Token requerido

**Path Parameters**:

- `produto_id` (int, obrigatório): ID do produto

**Body (JSON)** - Todos os campos são opcionais:

```json
{
  "nome": "Alface Americana",
  "descricao": "Alface americana orgânica",
  "preco_venda": 6.0,
  "tipo_medida": "UNIDADE",
  "estoque_minimo": 12.0,
  "ativo": true
}
```

**Tipos de Medida Disponíveis**:

- `kg` - Quilogramas
- `un` - Unidades
- `cx` - Caixas
- `dz` - Dúzias

**Resposta de Sucesso (200)**:

```json
{
  "data": {
    "id": 1,
    "nome": "Alface Americana",
    "descricao": "Alface americana orgânica",
    "preco_venda": 6.0,
    "tipo_medida": "un",
    "estoque_minimo": 12.0,
    "ativo": true,
    "atualizado_em": "2025-08-08T09:45:00"
  },
  "message": "Produto atualizado com sucesso",
  "success": true
}
```

### PUT `/produtos/{produto_id}/imagem`

**Descrição**: Atualizar imagem do produto  
**Autenticação**: Bearer Token requerido

**Path Parameters**:

- `produto_id` (int, obrigatório): ID do produto

**Body (multipart/form-data)**:

- `imagem` (file, obrigatório): Arquivo de imagem

**Resposta de Sucesso (200)**:

```json
{
  "data": {
    "id": 1,
    "nome": "Tomate",
    "imagem": "https://drive.google.com/file/d/abc123/view",
    "atualizado_em": "2025-08-08T09:50:00"
  },
  "message": "Imagem do produto atualizada com sucesso",
  "success": true
}
```

**Resposta de Sucesso (200)**:

```json
{
  "data": {
    "id": 1,
    "preco_venda": 6.0,
    "descricao": "Tomate especial de primeira qualidade",
    "estoque_minimo": 12.0,
    "atualizado_em": "2025-08-07T16:45:00"
  }
}
```

### DELETE `/produtos/{produto_id}`

**Descrição**: Excluir produto  
**Autenticação**: Bearer Token requerido (Admin)

**Path Parameters**:

- `produto_id` (int, obrigatório): ID do produto

**Resposta de Sucesso (200)**:

```json
{
  "message": "Produto excluído com sucesso",
  "success": true
}
```

**Resposta de Erro (400) - Produto com dependências**:

```json
{
  "detail": "Não é possível excluir o produto pois ele possui: entradas de estoque (5), itens de venda (12), registros de inventário (1). Para excluir o produto, primeiro remova todos os registros relacionados ou desative o produto."
}
```

**Resposta de Erro (404)**:

```json
{
  "detail": "Produto não encontrado"
}
```

**Resposta de Erro (403)**:

```json
{
  "detail": "Sem permissão para excluir produtos"
}
```

**Observações Importantes**:

- ⚠️ **Verificação de Integridade**: O sistema verifica se o produto possui registros relacionados antes da exclusão
- 🔍 **Dependências Verificadas**:
  - Entradas de estoque
  - Itens de venda
  - Registros de inventário
  - Registros FIFO
  - Movimentações de caixa
  - Registros de lucro
- 💡 **Alternativa**: Se não for possível excluir, considere desativar o produto usando `PUT /produtos/{produto_id}` com `"ativo": false`

---

## 💰 Vendas

### GET `/vendas/`

**Descrição**: Listar vendas com filtros e paginação  
**Autenticação**: Bearer Token requerido

**Query Parameters**:

- `skip` (int, opcional): Registros para pular (padrão: 0)
- `limit` (int, opcional): Registros por página (padrão: 20, máx: 100)
- `cliente_id` (int, opcional): Filtrar por cliente
- `situacao_pedido` (string, opcional): Filtrar por situação
  - Valores: `PENDENTE`, `SEPARADO`, `PAGO`
- `data_inicio` (string, opcional): Data inicial no formato YYYY-MM-DD
- `data_fim` (string, opcional): Data final no formato YYYY-MM-DD

**Exemplo de URL**:

```
GET /vendas/?skip=0&limit=10&cliente_id=1&situacao_pedido=PENDENTE&data_inicio=2025-08-01&data_fim=2025-08-31
```

**Resposta de Sucesso (200)**:

```json
{
  "data": {
    "vendas": [
      {
        "id": 1,
        "cliente_id": 1,
        "cliente_nome": "João Silva",
        "data_pedido": "2025-08-07T13:30:00",
        "situacao_pedido": "PENDENTE",
        "total_venda": 27.5,
        "observacoes": "Entregar pela manhã",
        "criado_em": "2025-08-07T13:30:00",
        "atualizado_em": null,
        "itens": [
          {
            "id": 1,
            "produto_id": 1,
            "produto_nome": "Tomate",
            "quantidade_pedida": 5.0,
            "quantidade_real": null,
            "valor_unitario": 5.5,
            "valor_total_produto": 27.5
          }
        ]
      }
    ],
    "total": 1,
    "skip": 0,
    "limit": 20
  }
}
```

### GET `/vendas/{venda_id}`

**Descrição**: Buscar venda por ID  
**Autenticação**: Bearer Token requerido

**Path Parameters**:

- `venda_id` (int, obrigatório): ID da venda

**Resposta de Sucesso (200)**:

```json
{
  "data": {
    "id": 1,
    "cliente_id": 1,
    "cliente_nome": "João Silva",
    "data_pedido": "2025-08-07T13:30:00",
    "situacao_pedido": "PENDENTE",
    "total_venda": 27.5,
    "observacoes": "Entregar pela manhã",
    "criado_em": "2025-08-07T13:30:00",
    "atualizado_em": null,
    "itens": [
      {
        "id": 1,
        "produto_id": 1,
        "produto_nome": "Tomate",
        "quantidade_pedida": 5.0,
        "quantidade_real": null,
        "valor_unitario": 5.5,
        "valor_total_produto": 27.5
      }
    ]
  }
}
```

### POST `/vendas/`

**Descrição**: Criar nova venda  
**Autenticação**: Bearer Token requerido

**Body (JSON)**:

```json
{
  "cliente_id": 1, // obrigatório
  "observacoes": "Entregar pela manhã", // opcional
  "itens": [
    // obrigatório, mínimo 1 item
    {
      "produto_id": 1, // obrigatório
      "quantidade_pedida": 5.0 // obrigatório
    },
    {
      "produto_id": 2,
      "quantidade_pedida": 10.0
    }
  ]
}
```

**Resposta de Sucesso (201)**:

```json
{
  "data": {
    "id": 2,
    "cliente_id": 1,
    "data_pedido": "2025-08-07T16:45:00",
    "situacao_pedido": "PENDENTE",
    "total_venda": 57.5,
    "observacoes": "Entregar pela manhã",
    "criado_em": "2025-08-07T16:45:00",
    "itens": [
      {
        "id": 3,
        "produto_id": 1,
        "produto_nome": "Tomate",
        "quantidade_pedida": 5.0,
        "quantidade_real": null,
        "valor_unitario": 5.5,
        "valor_total_produto": 27.5
      },
      {
        "id": 4,
        "produto_id": 2,
        "produto_nome": "Alface",
        "quantidade_pedida": 10.0,
        "quantidade_real": null,
        "valor_unitario": 3.0,
        "valor_total_produto": 30.0
      }
    ]
  }
}
```

### PUT `/vendas/{venda_id}/separacao`

**Descrição**: Atualizar separação de produtos (informar quantidades reais) e calcular custos FIFO automaticamente  
**Autenticação**: Bearer Token requerido

**Path Parameters**:

- `venda_id` (int, obrigatório): ID da venda

**Body (JSON)**:

```json
{
  "produtos_separados": [
    // obrigatório
    {
      "produto_id": 1, // obrigatório
      "quantidade_real": 4.8 // obrigatório
    },
    {
      "produto_id": 2,
      "quantidade_real": 9.5
    }
  ]
}
```

**Resposta de Sucesso (200)**:

```json
{
  "data": {
    "id": 1,
    "situacao_pedido": "SEPARADO",
    "total_venda": 55.0,
    "atualizado_em": "2025-08-07T17:00:00",
    "custos_fifo": {
      "custo_total": 32.15,
      "lucro_bruto": 22.85,
      "margem_percentual": "41.55"
    },
    "itens": [
      {
        "produto_id": 1,
        "quantidade_pedida": 5.0,
        "quantidade_real": 4.8,
        "valor_unitario": 5.5,
        "valor_total_produto": 26.4,
        "custo_fifo": 16.8,
        "lucro_item": 9.6
      },
      {
        "produto_id": 2,
        "quantidade_pedida": 10.0,
        "quantidade_real": 9.5,
        "valor_unitario": 3.0,
        "valor_total_produto": 28.5,
        "custo_fifo": 15.35,
        "lucro_item": 13.15
      }
    ]
  },
  "message": "Separação realizada com sucesso. Custos FIFO calculados automaticamente.",
  "success": true
}
```

**Processamento Automático FIFO**:

- ✅ Calcula custos usando First In, First Out
- ✅ Registra movimentações de caixa automaticamente
- ✅ Atualiza estoque FIFO (finaliza lotes consumidos)
- ✅ Gera registros de lucro bruto por produto
- ✅ Calcula margem de lucro em tempo real

````

### PUT `/vendas/{venda_id}/pagamento`

**Descrição**: Marcar venda como paga
**Autenticação**: Bearer Token requerido

**Path Parameters**:

- `venda_id` (int, obrigatório): ID da venda

**Body (JSON)**:

```json
{
  "forma_pagamento": "DINHEIRO" // obrigatório
}
````

**Formas de Pagamento Disponíveis**:

- `DINHEIRO`
- `CARTAO_DEBITO`
- `CARTAO_CREDITO`
- `PIX`
- `TRANSFERENCIA`

**Resposta de Sucesso (200)**:

```json
{
  "data": {
    "id": 1,
    "situacao_pedido": "PAGO",
    "forma_pagamento": "DINHEIRO",
    "data_pagamento": "2025-08-07T17:05:00",
    "atualizado_em": "2025-08-07T17:05:00"
  }
}
```

---

## 📦 Estoque

### GET `/estoque/entradas`

**Descrição**: Listar entradas de estoque  
**Autenticação**: Bearer Token requerido

**Query Parameters**:

- `skip` (int, opcional): Registros para pular (padrão: 0)
- `limit` (int, opcional): Registros por página (padrão: 20)
- `produto_id` (int, opcional): Filtrar por produto
- `data_inicio` (string, opcional): Data inicial no formato YYYY-MM-DD
- `data_fim` (string, opcional): Data final no formato YYYY-MM-DD

**Exemplo de URL**:

```
GET /estoque/entradas?skip=0&limit=10&produto_id=1&data_inicio=2025-08-01&data_fim=2025-08-31
```

**Resposta de Sucesso (200)**:

```json
{
  "data": {
    "entradas": [
      {
        "id": 1,
        "produto_id": 1,
        "produto_nome": "Tomate",
        "quantidade": 50.0,
        "preco_custo": 3.5,
        "fornecedor": "Sitio Verde",
        "observacoes": "Lote premium",
        "data_entrada": "2025-08-07T10:00:00",
        "criado_em": "2025-08-07T10:00:00"
      }
    ],
    "total": 1,
    "skip": 0,
    "limit": 20
  }
}
```

### POST `/estoque/entradas`

**Descrição**: Registrar entrada de estoque com criação automática de registros FIFO  
**Autenticação**: Bearer Token requerido

**Body (JSON)**:

```json
{
  "produto_id": 1, // obrigatório
  "tipo_medida": "kg", // obrigatório: kg, unidade, caixa, saco
  "quantidade": 50.0, // obrigatório
  "preco_custo": 3.5, // obrigatório
  "fornecedor": "Sitio Verde", // opcional
  "observacoes": "Lote premium" // opcional
}
```

**Resposta de Sucesso (201)**:

```json
{
  "data": {
    "id": 2,
    "produto_id": 1,
    "produto_nome": "Tomate",
    "tipo_medida": "kg",
    "quantidade": 50.0,
    "preco_custo": 3.5,
    "valor_total": 175.0,
    "fornecedor": "Sitio Verde",
    "observacoes": "Lote premium",
    "data_entrada": "2025-08-07T17:10:00",
    "criado_em": "2025-08-07T17:10:00"
  },
  "message": "Entrada de estoque registrada com sucesso. Registro FIFO criado automaticamente.",
  "success": true
}
```

**Processamento Automático**:

- ✅ Cria registro na tabela `estoque_fifo` para controle FIFO
- ✅ Registra movimentação de entrada no fluxo de caixa
- ✅ Atualiza o inventário do produto automaticamente
- ✅ Calcula valor total (quantidade × preço de custo)

````

### GET `/estoque/inventario`

**Descrição**: Consultar inventário geral
**Autenticação**: Bearer Token requerido

**Query Parameters**:

- `skip` (int, opcional): Registros para pular (padrão: 0)
- `limit` (int, opcional): Registros por página (padrão: 20)

**Resposta de Sucesso (200)**:

```json
{
  "data": {
    "inventario": [
      {
        "produto_id": 1,
        "produto_nome": "Tomate",
        "quantidade_atual": 45.2,
        "tipo_medida": "QUILOGRAMA",
        "estoque_minimo": 10.0,
        "status": "OK",
        "ultima_atualizacao": "2025-08-07T14:30:00"
      },
      {
        "produto_id": 3,
        "produto_nome": "Banana",
        "quantidade_atual": 8.5,
        "tipo_medida": "QUILOGRAMA",
        "estoque_minimo": 15.0,
        "status": "BAIXO",
        "ultima_atualizacao": "2025-08-07T12:00:00"
      }
    ],
    "total": 5,
    "skip": 0,
    "limit": 20
  }
}
````

**Status do Estoque**:

- `OK` - Estoque acima do mínimo
- `BAIXO` - Estoque abaixo do mínimo
- `ZERADO` - Estoque zerado

### PUT `/estoque/inventario/{produto_id}`

**Descrição**: Atualizar inventário de produto  
**Autenticação**: Bearer Token requerido

**Path Parameters**:

- `produto_id` (int, obrigatório): ID do produto

**Body (JSON)**:

```json
{
  "quantidade_atual": 30.0, // obrigatório
  "observacoes": "Ajuste de inventário" // opcional
}
```

**Resposta de Sucesso (200)**:

```json
{
  "data": {
    "produto_id": 1,
    "produto_nome": "Tomate",
    "quantidade_atual": 30.0,
    "quantidade_anterior": 45.2,
    "diferenca": -15.2,
    "observacoes": "Ajuste de inventário",
    "atualizado_em": "2025-08-07T17:15:00"
  }
}
```

### GET `/estoque/consulta/{produto_id}`

**Descrição**: Consultar estoque específico com histórico  
**Autenticação**: Bearer Token requerido

**Path Parameters**:

- `produto_id` (int, obrigatório): ID do produto

**Resposta de Sucesso (200)**:

```json
{
  "data": {
    "produto_id": 1,
    "produto_nome": "Tomate",
    "quantidade_atual": 45.2,
    "tipo_medida": "QUILOGRAMA",
    "estoque_minimo": 10.0,
    "status": "OK",
    "historico_entradas": [
      {
        "id": 1,
        "data_entrada": "2025-08-07T10:00:00",
        "quantidade": 50.0,
        "preco_custo": 3.5,
        "fornecedor": "Sitio Verde"
      }
    ],
    "vendas_recentes": [
      {
        "venda_id": 1,
        "data_venda": "2025-08-07T13:30:00",
        "quantidade_vendida": 4.8,
        "cliente_nome": "João Silva"
      }
    ]
  }
}
```

### GET `/estoque/alertas`

**Descrição**: Obter alertas de estoque baixo  
**Autenticação**: Bearer Token requerido

**Resposta de Sucesso (200)**:

```json
{
  "data": {
    "alertas": [
      {
        "produto_id": 3,
        "produto_nome": "Banana",
        "quantidade_atual": 8.5,
        "estoque_minimo": 15.0,
        "diferenca": -6.5,
        "tipo_medida": "QUILOGRAMA",
        "status": "BAIXO"
      },
      {
        "produto_id": 5,
        "produto_nome": "Batata",
        "quantidade_atual": 0.0,
        "estoque_minimo": 25.0,
        "diferenca": -25.0,
        "tipo_medida": "QUILOGRAMA",
        "status": "ZERADO"
      }
    ],
    "total_alertas": 2,
    "resumo": {
      "produtos_baixo": 1,
      "produtos_zerados": 1,
      "total_produtos": 5
    }
  }
}
```

### GET `/estoque/fluxo-caixa`

**Descrição**: Obter relatório completo de fluxo de caixa com controle FIFO  
**Autenticação**: Bearer Token requerido

**Query Parameters**:

- `data_inicio` (string, opcional): Data inicial no formato YYYY-MM-DD
- `data_fim` (string, opcional): Data final no formato YYYY-MM-DD
- `produto_id` (int, opcional): Filtrar por produto específico
- `tipo_movimentacao` (string, opcional): ENTRADA, SAIDA ou AJUSTE

**Exemplo de URL**:

```
GET /estoque/fluxo-caixa?data_inicio=2025-08-01&data_fim=2025-08-31&produto_id=1
```

**Resposta de Sucesso (200)**:

```json
{
  "data": {
    "total_entradas": 1250.0,
    "total_saidas": 980.5,
    "saldo": 269.5,
    "lucro_bruto_total": 425.75,
    "margem_media": "43.42",
    "quantidade_vendas": 12,
    "movimentacoes": [
      {
        "id": 1,
        "tipo_movimentacao": "ENTRADA",
        "produto_nome": "Tomate",
        "quantidade": 50.0,
        "preco_unitario": 3.5,
        "valor_total": 175.0,
        "data_movimentacao": "2025-08-07T10:00:00",
        "observacoes": "Entrada de estoque - Sitio Verde"
      },
      {
        "id": 2,
        "tipo_movimentacao": "SAIDA",
        "produto_nome": "Tomate",
        "quantidade": 15.5,
        "preco_unitario": 3.5,
        "valor_total": 54.25,
        "data_movimentacao": "2025-08-07T14:30:00",
        "observacoes": "Venda #1 - Cálculo FIFO",
        "venda_id": 1
      }
    ]
  },
  "message": "Relatório de fluxo de caixa gerado com sucesso",
  "success": true
}
```

**Resposta sem dados (200)**:

```json
{
  "data": {
    "total_entradas": 0,
    "total_saidas": 0,
    "saldo": 0,
    "lucro_bruto_total": 0,
    "margem_media": "0",
    "quantidade_vendas": 0,
    "movimentacoes": []
  },
  "message": "Relatório de fluxo de caixa gerado com sucesso",
  "success": true
}
```

### GET `/estoque/rentabilidade`

**Descrição**: Obter relatório de rentabilidade por período com análise FIFO  
**Autenticação**: Bearer Token requerido

**Query Parameters** (obrigatórios):

- `data_inicio` (string, obrigatório): Data inicial no formato YYYY-MM-DD
- `data_fim` (string, obrigatório): Data final no formato YYYY-MM-DD

**Query Parameters** (opcionais):

- `produto_id` (int, opcional): Filtrar por produto específico

**Exemplo de URL**:

```
GET /estoque/rentabilidade?data_inicio=2025-08-01&data_fim=2025-08-31&produto_id=1
```

**Resposta de Sucesso (200)**:

```json
{
  "data": {
    "periodo": {
      "inicio": "2025-08-01",
      "fim": "2025-08-31"
    },
    "resumo": {
      "total_vendas": 2450.75,
      "total_custos": 1325.5,
      "lucro_bruto_total": 1125.25,
      "margem_bruta_geral": "45.92",
      "produtos_vendidos": 8
    },
    "produtos": [
      {
        "produto_id": 1,
        "produto_nome": "Tomate",
        "quantidade_total_vendida": 125.5,
        "receita_total": 1875.0,
        "custo_total_fifo": 875.25,
        "lucro_bruto": 999.75,
        "margem_percentual": "53.31",
        "vendas": [
          {
            "venda_id": 1,
            "data_venda": "2025-08-07T14:30:00",
            "quantidade_vendida": 15.5,
            "receita": 232.5,
            "custo_fifo": 54.25,
            "lucro": 178.25,
            "margem": "76.67",
            "cliente_nome": "João Silva"
          }
        ]
      }
    ]
  },
  "message": "Relatório de rentabilidade gerado com sucesso",
  "success": true
}
```

**Resposta de Erro (422) - Parâmetros obrigatórios**:

```json
{
  "detail": [
    {
      "type": "missing",
      "loc": ["query", "data_inicio"],
      "msg": "Field required",
      "input": null
    },
    {
      "type": "missing",
      "loc": ["query", "data_fim"],
      "msg": "Field required",
      "input": null
    }
  ]
}
```

### Explicação do Sistema FIFO

O sistema implementa o método **First In, First Out (FIFO)** para cálculo de custos:

1. **Entrada de Estoque**: Cada entrada cria registros FIFO com quantidade restante
2. **Saída (Venda)**: Consome automaticamente os lotes mais antigos primeiro
3. **Cálculo de Custo**: Usa o preço de custo do lote original FIFO
4. **Lucro Real**: Receita da venda menos custo FIFO calculado
5. **Margem Percentual**: (Lucro ÷ Receita) × 100

**Exemplo Prático**:

- Entrada 1: 50kg a R$ 3,00/kg = R$ 150,00
- Entrada 2: 30kg a R$ 4,00/kg = R$ 120,00
- Venda: 60kg a R$ 8,00/kg = R$ 480,00
- **Custo FIFO**: (50kg × R$ 3,00) + (10kg × R$ 4,00) = R$ 190,00
- **Lucro**: R$ 480,00 - R$ 190,00 = R$ 290,00
- **Margem**: 60,42%

---

## � Conceitos do Sistema de Controle Financeiro

### 🔄 Fluxo Automático FIFO

1. **Entrada de Mercadoria**:

   - ✅ Registra na tabela `entradas_estoque`
   - ✅ Cria registro FIFO em `estoque_fifo` com quantidade total
   - ✅ Adiciona movimentação de ENTRADA no `movimentacoes_caixa`
   - ✅ Atualiza inventário automaticamente

2. **Processo de Venda**:

   - ✅ Cria venda em status PENDENTE
   - ✅ No momento da separação:
     - Calcula custos usando FIFO (lotes mais antigos primeiro)
     - Atualiza quantidades restantes nos lotes FIFO
     - Finaliza lotes quando quantidade chega a zero
     - Registra movimentação de SAÍDA no fluxo de caixa
     - Calcula e salva lucro bruto automaticamente

3. **Relatórios Financeiros**:
   - ✅ **Fluxo de Caixa**: Visão geral de entradas, saídas e saldo
   - ✅ **Rentabilidade**: Análise detalhada de lucros por produto/período
   - ✅ **Margem de Lucro**: Cálculo automático em tempo real

### 📊 Tabelas do Sistema FIFO

| Tabela                | Função                                        |
| --------------------- | --------------------------------------------- |
| `estoque_fifo`        | Controla lotes FIFO com quantidades restantes |
| `movimentacoes_caixa` | Registra todas as movimentações financeiras   |
| `lucros_brutos`       | Armazena cálculos de lucro por venda/produto  |

### 🎯 Vantagens do Sistema

- **Precisão Financeira**: Custos exatos usando FIFO
- **Automação Total**: Sem necessidade de cálculos manuais
- **Relatórios Realistas**: Margens e lucros baseados em custos reais
- **Controle de Estoque**: Rastreamento completo de lotes
- **Análise Gerencial**: Dados para tomada de decisão

---

## �📋 Códigos de Resposta

| Código | Status                | Descrição                            |
| ------ | --------------------- | ------------------------------------ |
| 200    | OK                    | Requisição bem-sucedida              |
| 201    | Created               | Recurso criado com sucesso           |
| 400    | Bad Request           | Dados inválidos na requisição        |
| 401    | Unauthorized          | Token não fornecido ou inválido      |
| 403    | Forbidden             | Sem permissão para acessar o recurso |
| 404    | Not Found             | Recurso não encontrado               |
| 422    | Unprocessable Entity  | Erro de validação nos dados          |
| 500    | Internal Server Error | Erro interno do servidor             |

### Exemplos de Respostas de Erro

**400 Bad Request**:

```json
{
  "detail": "Dados inválidos fornecidos"
}
```

**401 Unauthorized**:

```json
{
  "detail": "Not authenticated"
}
```

**403 Forbidden**:

```json
{
  "detail": "Operação não permitida"
}
```

**404 Not Found**:

```json
{
  "detail": "Recurso não encontrado"
}
```

**422 Validation Error**:

```json
{
  "detail": [
    {
      "loc": ["body", "nome"],
      "msg": "field required",
      "type": "value_error.missing"
    },
    {
      "loc": ["body", "preco_venda"],
      "msg": "ensure this value is greater than 0",
      "type": "value_error.number.not_gt"
    }
  ]
}
```

---

## 🧪 Exemplos Práticos - Sistema FIFO

### 1. Registrar Entrada de Estoque

```bash
curl -X POST "http://localhost:8000/api/estoque/entradas" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "produto_id": 1,
    "tipo_medida": "kg",
    "quantidade": 50.0,
    "preco_custo": 3.50,
    "fornecedor": "Sitio Verde",
    "observacoes": "Lote premium"
  }'
```

### 2. Consultar Fluxo de Caixa

```bash
curl -X GET "http://localhost:8000/api/estoque/fluxo-caixa?data_inicio=2025-08-01&data_fim=2025-08-31" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 3. Relatório de Rentabilidade

```bash
curl -X GET "http://localhost:8000/api/estoque/rentabilidade?data_inicio=2025-08-01&data_fim=2025-08-31&produto_id=1" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 4. Separação com Cálculo FIFO Automático

```bash
curl -X PUT "http://localhost:8000/api/vendas/1/separacao" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "produtos_separados": [
      {
        "produto_id": 1,
        "quantidade_real": 15.5
      }
    ]
  }'
```

### 5. JavaScript - Fluxo Completo

```javascript
// 1. Login
const loginResponse = await fetch("http://localhost:8000/api/auth/login", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    email: "admin@ceasa.com",
    senha: "admin123",
  }),
});
const loginData = await loginResponse.json();
const token = loginData.data.token;

// 2. Registrar entrada
const entradaResponse = await fetch(
  "http://localhost:8000/api/estoque/entradas",
  {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      produto_id: 1,
      tipo_medida: "kg",
      quantidade: 50.0,
      preco_custo: 3.5,
      fornecedor: "Sitio Verde",
    }),
  }
);

// 3. Consultar fluxo de caixa
const fluxoResponse = await fetch(
  "http://localhost:8000/api/estoque/fluxo-caixa",
  {
    method: "GET",
    headers: { Authorization: `Bearer ${token}` },
  }
);
const fluxoData = await fluxoResponse.json();

console.log("Saldo atual:", fluxoData.data.saldo);
console.log("Lucro total:", fluxoData.data.lucro_bruto_total);
```

---

## 🔑 Headers Obrigatórios

### Para endpoints autenticados:

```http
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

### Para endpoints de upload (quando disponíveis):

```http
Authorization: Bearer <jwt_token>
Content-Type: multipart/form-data
```

### Exemplo de requisição com curl:

```bash
curl -X GET "http://localhost:8000/api/clientes/" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json"
```

### Exemplo de requisição com JavaScript:

```javascript
const response = await fetch("http://localhost:8000/api/clientes/", {
  method: "GET",
  headers: {
    Authorization: `Bearer ${token}`,
    "Content-Type": "application/json",
  },
});

const data = await response.json();
```

---

## 📝 Notas Importantes

1. **Autenticação**: Todos os endpoints (exceto `/auth/login`) requerem autenticação via Bearer Token
2. **Paginação**: Todas as listagens suportam paginação via `skip` e `limit`
3. **Filtros**: Múltiplos filtros podem ser combinados nas consultas
4. **Datas**: Formato padrão ISO 8601 (YYYY-MM-DDTHH:mm:ss)
5. **Decimais**: Valores monetários e quantidades usam precisão decimal
6. **Validação**: Todos os campos são validados conforme regras de negócio
7. **Soft Delete**: Alguns recursos usam exclusão lógica (campo `ativo`)
8. **Sistema FIFO**: Cálculos de custo automáticos usando First In First Out
9. **Integração Automática**: Entradas e vendas atualizam fluxo de caixa automaticamente
10. **Relatórios em Tempo Real**: Dados financeiros sempre atualizados

## 🚀 Testando a API

### Teste Rápido - Fluxo Básico:

1. **Fazer Login**:

```bash
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@ceasa.com","senha":"admin123"}'
```

2. **Testar Sistema FIFO**:

```bash
# Registrar entrada
curl -X POST "http://localhost:8000/api/estoque/entradas" \
  -H "Authorization: Bearer SEU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"produto_id":1,"tipo_medida":"kg","quantidade":50.0,"preco_custo":3.50}'

# Consultar fluxo de caixa
curl -X GET "http://localhost:8000/api/estoque/fluxo-caixa" \
  -H "Authorization: Bearer SEU_TOKEN"
```

---

## 📊 Relatórios Financeiros

Sistema completo de relatórios para análise financeira e controle de pagamentos.

### GET `/relatorios/pagamentos-pendentes`

**Descrição**: Lista pagamentos pendentes agrupados por cliente  
**Autenticação**: Token JWT obrigatório  
**Permissão**: Usuários autenticados

**Query Parameters**:

- `cliente_id` (opcional): Filtrar por cliente específico
- `ordenar_por` (opcional): `valor_desc`, `valor_asc`, `data_desc`, `data_asc`

**Response**:

```json
{
  "data": {
    "clientes": [
      {
        "cliente": {
          "id": 1,
          "nome": "João Silva",
          "nome_fantasia": "Silva & Cia",
          "email": "joao@silva.com",
          "telefone1": "11999999999"
        },
        "vendas_pendentes": [
          {
            "id": 1,
            "data_venda": "2025-08-01T10:00:00",
            "total_venda": 150.0,
            "situacao_pedido": "Separado",
            "observacoes": "Entrega urgente",
            "dias_pendente": 7
          }
        ],
        "total_pendente": 150.0,
        "quantidade_vendas": 1
      }
    ],
    "resumo": {
      "total_geral_pendente": 1250.5,
      "quantidade_clientes": 5,
      "quantidade_vendas_pendentes": 12
    }
  },
  "message": "Relatório de pagamentos pendentes gerado com sucesso",
  "success": true
}
```

### GET `/relatorios/historico-vendas/{cliente_id}`

**Descrição**: Histórico completo de vendas de um cliente  
**Autenticação**: Token JWT obrigatório  
**Permissão**: Usuários autenticados

**Path Parameters**:

- `cliente_id`: ID do cliente

**Query Parameters**:

- `data_inicio` (opcional): Data inicial (YYYY-MM-DD)
- `data_fim` (opcional): Data final (YYYY-MM-DD)
- `situacao_pagamento` (opcional): `PAGO` ou `PENDENTE`
- `skip` (opcional): Registros para pular (padrão: 0)
- `limit` (opcional): Registros por página (padrão: 50, máx: 100)

**Response**:

```json
{
  "data": {
    "cliente": {
      "id": 1,
      "nome": "João Silva",
      "nome_fantasia": "Silva & Cia",
      "email": "joao@silva.com",
      "telefone1": "11999999999"
    },
    "vendas": [
      {
        "id": 1,
        "data_venda": "2025-08-01T10:00:00",
        "data_separacao": "2025-08-01T14:30:00",
        "total_venda": 150.0,
        "situacao_pedido": "Separado",
        "situacao_pagamento": "PENDENTE",
        "observacoes": "Entrega urgente",
        "funcionario_separacao": {
          "id": 2,
          "nome": "Funcionário CEASA",
          "email": "funcionario@ceasa.com"
        },
        "quantidade_itens": 3
      }
    ],
    "estatisticas": {
      "total_vendido": 2500.0,
      "ticket_medio": 125.0,
      "quantidade_vendas": 20,
      "total_pendente": 500.0,
      "total_pago": 2000.0
    },
    "paginacao": {
      "pagina": 1,
      "itens_por_pagina": 50,
      "total_itens": 20,
      "total_paginas": 1
    }
  },
  "message": "Histórico de vendas do cliente João Silva obtido com sucesso",
  "success": true
}
```

### GET `/relatorios/resumo-financeiro/{cliente_id}`

**Descrição**: Dashboard financeiro completo de um cliente  
**Autenticação**: Token JWT obrigatório  
**Permissão**: Usuários autenticados

**Path Parameters**:

- `cliente_id`: ID do cliente

**Response**:

```json
{
  "data": {
    "cliente": {
      "id": 1,
      "nome": "João Silva",
      "nome_fantasia": "Silva & Cia",
      "email": "joao@silva.com",
      "telefone1": "11999999999",
      "ativo": true
    },
    "estatisticas_gerais": {
      "total_historico": 5000.0,
      "ticket_medio": 125.0,
      "total_vendas": 40,
      "total_pendente": 500.0,
      "total_pago": 4500.0,
      "primeira_compra": "2024-01-15T09:00:00",
      "ultima_compra": "2025-08-01T10:00:00",
      "percentual_inadimplencia": 10.0
    },
    "produtos_favoritos": [
      {
        "nome": "Batata",
        "quantidade_total": 120.5,
        "valor_total": 850.0,
        "vezes_comprado": 15
      }
    ],
    "evolucao_mensal": [
      {
        "mes": "2025-08",
        "total_vendido": 500.0,
        "quantidade_vendas": 4
      }
    ],
    "vendas_pendentes_recentes": [
      {
        "id": 1,
        "data_venda": "2025-08-01T10:00:00",
        "total_venda": 150.0,
        "dias_pendente": 7,
        "observacoes": "Entrega urgente"
      }
    ]
  },
  "message": "Resumo financeiro do cliente João Silva gerado com sucesso",
  "success": true
}
```

### GET `/relatorios/dashboard-vendas`

**Descrição**: Dashboard executivo com KPIs de vendas  
**Autenticação**: Token JWT obrigatório  
**Permissão**: Apenas administradores

**Query Parameters**:

- `data_inicio` (opcional): Data inicial (YYYY-MM-DD)
- `data_fim` (opcional): Data final (YYYY-MM-DD)

**Response**:

```json
{
  "data": {
    "periodo": {
      "data_inicio": "2025-08-01",
      "data_fim": "2025-08-31",
      "gerado_em": "2025-08-08T11:47:00"
    },
    "kpis": {
      "faturamento_total": 25000.0,
      "ticket_medio": 125.0,
      "total_vendas": 200,
      "total_pago": 20000.0,
      "total_pendente": 5000.0,
      "taxa_inadimplencia": 20.0,
      "vendas_separadas": 180,
      "vendas_a_separar": 20,
      "taxa_separacao": 90.0
    },
    "top_clientes": [
      {
        "nome": "João Silva",
        "nome_fantasia": "Silva & Cia",
        "total_comprado": 2500.0,
        "quantidade_compras": 20,
        "valor_pendente": 500.0
      }
    ],
    "top_produtos": [
      {
        "nome": "Batata",
        "quantidade_vendida": 500.0,
        "faturamento": 3500.0
      }
    ],
    "performance_funcionarios": [
      {
        "nome": "Funcionário CEASA",
        "email": "funcionario@ceasa.com",
        "vendas_separadas": 150,
        "valor_separado": 18750.0
      }
    ]
  },
  "message": "Dashboard de vendas gerado com sucesso",
  "success": true
}
```

### GET `/relatorios/clientes-inadimplentes`

**Descrição**: Lista clientes com pagamentos em atraso  
**Autenticação**: Token JWT obrigatório  
**Permissão**: Apenas administradores

**Query Parameters**:

- `dias_minimo` (opcional): Mínimo de dias em atraso (padrão: 30)
- `valor_minimo` (opcional): Valor mínimo em débito
- `ordenar_por` (opcional): `valor_desc`, `valor_asc`, `dias_desc`, `dias_asc`

**Response**:

```json
{
  "data": {
    "clientes_inadimplentes": [
      {
        "cliente": {
          "id": 1,
          "nome": "João Silva",
          "nome_fantasia": "Silva & Cia",
          "email": "joao@silva.com",
          "telefone1": "11999999999"
        },
        "divida": {
          "total_devido": 1500.0,
          "vendas_pendentes": 3,
          "venda_mais_antiga": "2025-06-15T10:00:00",
          "venda_mais_recente": "2025-07-20T15:30:00",
          "dias_atraso_maximo": 54
        }
      }
    ],
    "resumo": {
      "total_devido_geral": 8500.0,
      "quantidade_clientes": 8,
      "criterios": {
        "dias_minimo_atraso": 30,
        "valor_minimo": null,
        "ordenacao": "valor_desc"
      }
    }
  },
  "message": "Encontrados 8 clientes inadimplentes",
  "success": true
}
```

**Exemplos de uso dos relatórios**:

```bash
# Pagamentos pendentes geral
curl -X GET "http://localhost:8000/api/relatorios/pagamentos-pendentes" \
  -H "Authorization: Bearer SEU_TOKEN"

# Pagamentos pendentes de um cliente específico
curl -X GET "http://localhost:8000/api/relatorios/pagamentos-pendentes?cliente_id=1" \
  -H "Authorization: Bearer SEU_TOKEN"

# Histórico de vendas com filtro por período
curl -X GET "http://localhost:8000/api/relatorios/historico-vendas/1?data_inicio=2025-01-01&data_fim=2025-08-31" \
  -H "Authorization: Bearer SEU_TOKEN"

# Dashboard executivo
curl -X GET "http://localhost:8000/api/relatorios/dashboard-vendas?data_inicio=2025-08-01&data_fim=2025-08-31" \
  -H "Authorization: Bearer SEU_TOKEN"

# Clientes inadimplentes há mais de 60 dias
curl -X GET "http://localhost:8000/api/relatorios/clientes-inadimplentes?dias_minimo=60&valor_minimo=100" \
  -H "Authorization: Bearer SEU_TOKEN"
```

3. **Acessar documentação interativa**: http://localhost:8000/docs

### Links Úteis:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

---

_Documentação atualizada com Sistema FIFO - Versão 2.0.0 - Agosto 2025_
