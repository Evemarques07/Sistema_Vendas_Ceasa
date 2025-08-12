# Backend - Sistema de Vendas CEASA

Backend FastAPI para o sistema de controle de pedidos de frutas, legumes e verduras.

## 🚀 Tecnologias

- **FastAPI** - Framework web moderno e rápido
- **SQLAlchemy** - ORM para Python
- **MySQL** - Banco de dados relacional
- **Alembic** - Migrações de banco de dados
- **JWT** - Autenticação com tokens
- **Docker** - Containerização
- **rclone** - Upload de imagens para Google Drive

## 📋 Funcionalidades

### ✅ Implementado

- Autenticação JWT com login/logout
- CRUD completo de usuários, clientes e produtos
- Sistema de vendas com separação de produtos
- Controle de estoque (entradas e inventário)
- Upload de imagens para Google Drive
- API RESTful com documentação automática

### 🔄 Endpoints Disponíveis

#### Autenticação

- `POST /api/v1/auth/login` - Fazer login
- `POST /api/v1/auth/logout` - Fazer logout
- `GET /api/v1/auth/me` - Obter dados do usuário atual

#### Usuários

- `GET /api/v1/usuarios/` - Listar usuários
- `POST /api/v1/usuarios/` - Criar usuário
- `GET /api/v1/usuarios/{id}` - Obter usuário por ID
- `PUT /api/v1/usuarios/{id}` - Atualizar usuário
- `DELETE /api/v1/usuarios/{id}` - Deletar usuário

#### Clientes

- `GET /api/v1/clientes/` - Listar clientes (com filtros e paginação)
- `POST /api/v1/clientes/` - Criar cliente
- `GET /api/v1/clientes/{id}` - Obter cliente por ID
- `PUT /api/v1/clientes/{id}` - Atualizar cliente
- `DELETE /api/v1/clientes/{id}` - Deletar cliente

#### Produtos

- `GET /api/v1/produtos/` - Listar produtos (com filtros e paginação)
- `POST /api/v1/produtos/` - Criar produto
- `GET /api/v1/produtos/{id}` - Obter produto por ID
- `PUT /api/v1/produtos/{id}` - Atualizar produto
- `DELETE /api/v1/produtos/{id}` - Deletar produto
- `POST /api/v1/produtos/{id}/imagem` - Upload de imagem

#### Vendas

- `GET /api/v1/vendas/` - Listar vendas (com filtros e paginação)
- `POST /api/v1/vendas/` - Criar venda
- `GET /api/v1/vendas/{id}` - Obter venda por ID
- `PUT /api/v1/vendas/{id}/separacao` - Atualizar separação
- `PUT /api/v1/vendas/{id}/pagamento` - Marcar como pago

#### Estoque

- `GET /api/v1/estoque/entradas` - Listar entradas de estoque
- `POST /api/v1/estoque/entradas` - Criar entrada de estoque
- `GET /api/v1/estoque/inventario` - Listar inventário
- `PUT /api/v1/estoque/inventario/{produto_id}` - Atualizar inventário
- `GET /api/v1/estoque/consulta/{produto_id}` - Consultar estoque de produto
- `GET /api/v1/estoque/alertas` - Obter alertas de estoque baixo

## 🛠️ Instalação

### 1. Pré-requisitos

- Python 3.11+
- Docker Desktop (opcional, mas recomendado)
- Git

### 2. Clonar o repositório

```bash
git clone <url-do-repositorio>
cd backend-vendas-ceasa
```

### 3. Criar ambiente virtual

```bash
python -m venv venv

# Windows
venv\\Scripts\\activate

# Linux/Mac
source venv/bin/activate
```

### 4. Instalar dependências

```bash
pip install -r requirements.txt
```

### 5. Configurar variáveis de ambiente

Crie um arquivo `.env` na raiz do projeto:

```env
# Database
DATABASE_URL=mysql+pymysql://user:password@localhost:3306/vendas_ceasa

# Security
SECRET_KEY=sua_chave_secreta_muito_segura_aqui
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Google Drive (opcional)
GDRIVE_FOLDER_ID=seu_folder_id_do_google_drive

# MySQL (para Docker)
MYSQL_ROOT_PASSWORD=rootpassword
MYSQL_DATABASE=vendas_ceasa
MYSQL_USER=user
MYSQL_PASSWORD=password
```

### 6. Iniciar banco de dados

#### Opção A: Com Docker (Recomendado)

```bash
docker-compose up -d mysql
```

#### Opção B: MySQL local

- Instale o MySQL 8.0
- Crie um banco de dados chamado `vendas_ceasa`
- Configure as credenciais no `.env`

### 7. Executar migrações

```bash
alembic upgrade head
```

### 8. Iniciar servidor

```bash
# Windows
powershell -ExecutionPolicy Bypass -File start.ps1

# Linux/Mac
chmod +x start.sh
./start.sh

# Ou manualmente:
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## 📚 Documentação da API

Após iniciar o servidor, acesse:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 📖 Documentação Detalhada dos Endpoints

### 🔐 Autenticação

#### POST `/api/auth/login`

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

#### POST `/api/auth/logout`

**Descrição**: Fazer logout do sistema  
**Autenticação**: Bearer Token requerido

**Body**: Nenhum

**Resposta de Sucesso (200)**:

```json
{
  "message": "Logout realizado com sucesso"
}
```

#### GET `/api/auth/me`

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

### 👥 Clientes

#### GET `/api/clientes/`

**Descrição**: Listar clientes com filtros e paginação  
**Autenticação**: Bearer Token requerido

**Query Parameters**:

- `skip` (int): Registros para pular (padrão: 0)
- `limit` (int): Registros por página (padrão: 20, máx: 100)
- `nome` (string): Filtrar por nome
- `cpf_ou_cnpj` (string): Filtrar por CPF/CNPJ
- `ativo` (boolean): Filtrar por status ativo

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
        "criado_em": "2025-08-07T13:27:57"
      }
    ],
    "total": 3,
    "skip": 0,
    "limit": 20
  }
}
```

#### GET `/api/clientes/{cliente_id}`

**Descrição**: Buscar cliente por ID  
**Autenticação**: Bearer Token requerido

**Path Parameters**:

- `cliente_id` (int): ID do cliente

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
    "criado_em": "2025-08-07T13:27:57"
  }
}
```

#### POST `/api/clientes/`

**Descrição**: Criar novo cliente  
**Autenticação**: Bearer Token requerido

**Body (JSON)**:

```json
{
  "nome": "Maria Santos",
  "nome_fantasia": "Verduras Maria",
  "cpf_ou_cnpj": "987.654.321-00",
  "endereco": "Av. Principal, 456",
  "ponto_referencia": "Próximo ao banco",
  "email": "maria@email.com",
  "telefone1": "(11) 99999-2222",
  "telefone2": "(11) 3333-4444",
  "ativo": true
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
    "criado_em": "2025-08-07T16:30:00"
  }
}
```

#### PUT `/api/clientes/{cliente_id}`

**Descrição**: Atualizar cliente  
**Autenticação**: Bearer Token requerido

**Path Parameters**:

- `cliente_id` (int): ID do cliente

**Body (JSON)** - Todos os campos são opcionais:

```json
{
  "nome": "Maria Santos Silva",
  "email": "maria.silva@email.com",
  "telefone1": "(11) 99999-5555"
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
    "atualizado_em": "2025-08-07T16:35:00"
  }
}
```

#### DELETE `/api/clientes/{cliente_id}`

**Descrição**: Excluir cliente  
**Autenticação**: Bearer Token requerido (Admin)

**Path Parameters**:

- `cliente_id` (int): ID do cliente

**Resposta de Sucesso (200)**:

```json
{
  "message": "Cliente excluído com sucesso"
}
```

---

### 🛍️ Produtos

#### GET `/api/produtos/`

**Descrição**: Listar produtos com filtros e paginação  
**Autenticação**: Bearer Token requerido

**Query Parameters**:

- `skip` (int): Registros para pular (padrão: 0)
- `limit` (int): Registros por página (padrão: 20, máx: 100)
- `nome` (string): Filtrar por nome
- `tipo_medida` (string): Filtrar por tipo de medida (QUILOGRAMA, UNIDADE, GRAMA, LITRO)
- `ativo` (boolean): Filtrar por status ativo

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
        "criado_em": "2025-08-07T13:27:57"
      }
    ],
    "total": 5,
    "skip": 0,
    "limit": 20
  }
}
```

#### GET `/api/produtos/{produto_id}`

**Descrição**: Buscar produto por ID  
**Autenticação**: Bearer Token requerido

**Path Parameters**:

- `produto_id` (int): ID do produto

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
    "criado_em": "2025-08-07T13:27:57"
  }
}
```

#### POST `/api/produtos/`

**Descrição**: Criar novo produto  
**Autenticação**: Bearer Token requerido

**Body (JSON)**:

```json
{
  "nome": "Alface Crespa",
  "descricao": "Alface crespa orgânica",
  "preco_venda": 2.5,
  "tipo_medida": "UNIDADE",
  "estoque_minimo": 15.0,
  "ativo": true
}
```

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
    "criado_em": "2025-08-07T16:40:00"
  }
}
```

#### PUT `/api/produtos/{produto_id}`

**Descrição**: Atualizar produto  
**Autenticação**: Bearer Token requerido

**Path Parameters**:

- `produto_id` (int): ID do produto

**Body (JSON)** - Todos os campos são opcionais:

```json
{
  "preco_venda": 6.0,
  "descricao": "Tomate especial de primeira qualidade"
}
```

#### DELETE `/api/produtos/{produto_id}`

**Descrição**: Excluir produto  
**Autenticação**: Bearer Token requerido (Admin)

---

### 💰 Vendas

#### GET `/api/vendas/`

**Descrição**: Listar vendas com filtros e paginação  
**Autenticação**: Bearer Token requerido

**Query Parameters**:

- `skip` (int): Registros para pular (padrão: 0)
- `limit` (int): Registros por página (padrão: 20, máx: 100)
- `cliente_id` (int): Filtrar por cliente
- `situacao_pedido` (string): Filtrar por situação (PENDENTE, SEPARADO, PAGO)
- `data_inicio` (string): Data inicial (YYYY-MM-DD)
- `data_fim` (string): Data final (YYYY-MM-DD)

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

#### GET `/api/vendas/{venda_id}`

**Descrição**: Buscar venda por ID  
**Autenticação**: Bearer Token requerido

**Path Parameters**:

- `venda_id` (int): ID da venda

#### POST `/api/vendas/`

**Descrição**: Criar nova venda  
**Autenticação**: Bearer Token requerido

**Body (JSON)**:

```json
{
  "cliente_id": 1,
  "observacoes": "Entregar pela manhã",
  "itens": [
    {
      "produto_id": 1,
      "quantidade_pedida": 5.0
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
    "itens": [
      {
        "produto_id": 1,
        "quantidade_pedida": 5.0,
        "valor_unitario": 5.5,
        "valor_total_produto": 27.5
      },
      {
        "produto_id": 2,
        "quantidade_pedida": 10.0,
        "valor_unitario": 3.0,
        "valor_total_produto": 30.0
      }
    ]
  }
}
```

#### PUT `/api/vendas/{venda_id}/separacao`

**Descrição**: Atualizar separação de produtos  
**Autenticação**: Bearer Token requerido

**Path Parameters**:

- `venda_id` (int): ID da venda

**Body (JSON)**:

```json
{
  "produtos_separados": [
    {
      "produto_id": 1,
      "quantidade_real": 4.8
    },
    {
      "produto_id": 2,
      "quantidade_real": 9.5
    }
  ]
}
```

#### PUT `/api/vendas/{venda_id}/pagamento`

**Descrição**: Marcar venda como paga  
**Autenticação**: Bearer Token requerido

**Path Parameters**:

- `venda_id` (int): ID da venda

**Body (JSON)**:

```json
{
  "forma_pagamento": "DINHEIRO"
}
```

---

### 📦 Estoque

#### GET `/api/estoque/entradas`

**Descrição**: Listar entradas de estoque  
**Autenticação**: Bearer Token requerido

**Query Parameters**:

- `skip` (int): Registros para pular (padrão: 0)
- `limit` (int): Registros por página (padrão: 20)
- `produto_id` (int): Filtrar por produto
- `data_inicio` (string): Data inicial (YYYY-MM-DD)
- `data_fim` (string): Data final (YYYY-MM-DD)

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
        "data_entrada": "2025-08-07T10:00:00"
      }
    ],
    "total": 1,
    "skip": 0,
    "limit": 20
  }
}
```

#### POST `/api/estoque/entradas`

**Descrição**: Registrar entrada de estoque  
**Autenticação**: Bearer Token requerido

**Body (JSON)**:

```json
{
  "produto_id": 1,
  "quantidade": 50.0,
  "preco_custo": 3.5,
  "fornecedor": "Sitio Verde",
  "observacoes": "Lote premium"
}
```

#### GET `/api/estoque/inventario`

**Descrição**: Consultar inventário geral  
**Autenticação**: Bearer Token requerido

**Query Parameters**:

- `skip` (int): Registros para pular (padrão: 0)
- `limit` (int): Registros por página (padrão: 20)

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
      }
    ],
    "total": 5,
    "skip": 0,
    "limit": 20
  }
}
```

#### PUT `/api/estoque/inventario/{produto_id}`

**Descrição**: Atualizar inventário de produto  
**Autenticação**: Bearer Token requerido

**Path Parameters**:

- `produto_id` (int): ID do produto

**Body (JSON)**:

```json
{
  "quantidade_atual": 30.0,
  "observacoes": "Ajuste de inventário"
}
```

#### GET `/api/estoque/consulta/{produto_id}`

**Descrição**: Consultar estoque específico  
**Autenticação**: Bearer Token requerido

**Path Parameters**:

- `produto_id` (int): ID do produto

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
        "data_entrada": "2025-08-07T10:00:00",
        "quantidade": 50.0,
        "fornecedor": "Sitio Verde"
      }
    ]
  }
}
```

#### GET `/api/estoque/alertas`

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
        "tipo_medida": "QUILOGRAMA"
      }
    ],
    "total_alertas": 1
  }
}
```

---

### 📋 Códigos de Resposta

- **200 OK**: Requisição bem-sucedida
- **201 Created**: Recurso criado com sucesso
- **400 Bad Request**: Dados inválidos
- **401 Unauthorized**: Token não fornecido ou inválido
- **403 Forbidden**: Sem permissão para acessar o recurso
- **404 Not Found**: Recurso não encontrado
- **422 Unprocessable Entity**: Erro de validação
- **500 Internal Server Error**: Erro interno do servidor

### 🔑 Headers Obrigatórios

Para endpoints autenticados:

```
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

## 🐳 Docker

### Executar com Docker Compose

```bash
docker-compose up -d
```

### Executar apenas o MySQL

```bash
docker-compose up -d mysql
```

### Ver logs

```bash
docker-compose logs -f
```

### Parar containers

```bash
docker-compose down
```

## 🗃️ Estrutura do Banco

### Tabelas Principais

- `usuarios` - Usuários do sistema (admin/operador)
- `clientes` - Clientes que fazem pedidos
- `produtos` - Produtos disponíveis para venda
- `vendas` - Pedidos/vendas realizadas
- `itens_venda` - Itens de cada venda
- `entradas_estoque` - Registros de entrada de mercadorias
- `inventario` - Estoque atual de cada produto

### Relacionamentos

- Uma venda tem muitos itens
- Um cliente pode ter muitas vendas
- Um produto pode estar em muitas vendas
- Um produto tem um registro de inventário

## 🔐 Autenticação

O sistema usa JWT (JSON Web Tokens) para autenticação:

1. Faça login em `/api/v1/auth/login` com email e senha
2. Receba o token de acesso
3. Use o token no header: `Authorization: Bearer <token>`
4. Token expira em 30 minutos (configurável)

### Tipos de Usuário

- **ADMINISTRADOR**: Acesso total ao sistema
- **OPERADOR**: Acesso limitado (sem deletar, apenas consultas e operações)

## 🚀 Deploy

### Variáveis de Ambiente para Produção

```env
DEBUG=False
DATABASE_URL=mysql+pymysql://user:password@mysql:3306/vendas_ceasa
SECRET_KEY=chave_super_secreta_para_producao
CORS_ORIGINS=["https://seudominio.com"]
```

### Docker em Produção

```bash
docker-compose -f docker-compose.prod.yml up -d
```

## 🧪 Testes

```bash
# Executar testes
pytest

# Com cobertura
pytest --cov=app

# Apenas testes específicos
pytest tests/test_auth.py
```

## 📝 Desenvolvimento

### Adicionar nova migração

```bash
alembic revision --autogenerate -m "Descrição da mudança"
alembic upgrade head
```

### Estrutura de pastas

```
app/
├── api/
│   └── api_v1/
│       └── endpoints/    # Endpoints da API
├── core/                # Configurações centrais
├── models/              # Modelos do SQLAlchemy
├── schemas/             # Schemas do Pydantic
└── utils/               # Utilitários
```

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 📞 Suporte

Se você encontrar problemas ou tiver dúvidas:

1. Verifique se todas as dependências estão instaladas
2. Confirme se o banco de dados está rodando
3. Verifique os logs do servidor
4. Consulte a documentação da API em `/docs`

Para mais ajuda, abra uma issue no repositório do projeto.
