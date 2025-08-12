# 🍎 Sistema de Vendas CEASA - Backend API

Sistema completo de controle de pedidos para frutas, legumes e verduras com funcionalidades avançadas de gestão de estoque, vendas e relatórios financeiros.

## 🚀 Funcionalidades Principais

### 👥 **Gestão de Clientes**

- Cadastro completo de clientes
- Controle de CPF/CNPJ único
- Endereçamento e contatos
- Status ativo/inativo

### 🥕 **Catálogo de Produtos**

- Produtos com tipos de medida (kg, unidade, litro, caixa, saco, dúzia)
- Controle de preços de venda
- Estoque mínimo configurável
- Upload de imagens de produtos
- Sistema de ativação/desativação

### 💰 **Sistema de Vendas**

- Criação de pedidos com múltiplos itens
- Fluxo: Pedido → Separação → Pagamento
- Cálculo automático de totais
- Observações por pedido
- Rastreamento de funcionário responsável pela separação

### 📦 **Controle de Estoque FIFO**

- Sistema First In, First Out (FIFO) para cálculo de custos
- Entradas de estoque com preço de custo
- Baixa automática no estoque durante vendas
- Inventário em tempo real
- Alertas de estoque baixo
- Histórico completo de movimentações

### 💹 **Relatórios Financeiros**

- **Fluxo de Caixa**: Entradas, saídas e saldo
- **Rentabilidade**: Lucro bruto e margem por produto/período
- **Pagamentos Pendentes**: Controle de inadimplência
- **Dashboard Executivo**: KPIs e métricas de vendas
- **Histórico por Cliente**: Análise individual de vendas

### 🔐 **Sistema de Autenticação**

- Login JWT com roles (Administrador/Funcionário)
- Controle de permissões por funcionalidade
- Segurança em todos os endpoints

## 🛠️ Tecnologias Utilizadas

- **Backend**: FastAPI (Python 3.11+)
- **Banco de Dados**: MySQL 8.0
- **ORM**: SQLAlchemy
- **Autenticação**: JWT (JSON Web Tokens)
- **Validação**: Pydantic
- **Migrações**: Alembic
- **Containerização**: Docker & Docker Compose
- **Upload**: Google Drive integration (rclone)

## 📋 Pré-requisitos

- Python 3.11+
- Docker & Docker Compose
- MySQL 8.0 (via Docker)

## ⚡ Instalação e Execução

### 1. **Clone o repositório**

```bash
git clone <url-do-repositorio>
cd backend-vendas-ceasa
```

### 2. **Configure as variáveis de ambiente**

```bash
cp .env.example .env
# Edite o .env conforme necessário
```

### 3. **Subir com Docker (Recomendado)**

#### **Opção A: Ambiente Completo (Produção)**

```bash
# Subir MySQL + FastAPI em containers
docker compose up -d

# Verificar se estão rodando
docker compose ps

# Ver logs
docker compose logs -f
```

#### **Opção B: Desenvolvimento Híbrido**

```bash
# Apenas MySQL em container
docker compose up mysql -d

# FastAPI local (com hot reload)
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### 4. **Inicializar banco de dados**

```bash
python init_db.py
```

### 5. **Acessar a aplicação**

- **API**: http://localhost:8000
- **Documentação**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **PHPMyAdmin**: http://localhost:8080 (apenas com profile dev)

## 🐳 Comandos Docker Úteis

### **Gerenciamento de Serviços**

```bash
# Subir todos os serviços
docker compose up -d

# Subir apenas MySQL
docker compose up mysql -d

# Subir apenas API
docker compose up api -d

# Parar todos os serviços
docker compose down

# Parar e remover volumes (limpar dados)
docker compose down -v

# Ver status dos serviços
docker compose ps

# Ver logs em tempo real
docker compose logs -f

# Ver logs de um serviço específico
docker compose logs api
docker compose logs mysql

# Rebuild e restart
docker compose up --build -d

# Reiniciar apenas um serviço
docker compose restart api
```

### **PHPMyAdmin para Desenvolvimento**

```bash
# Subir com PHPMyAdmin
docker compose --profile dev up -d

# Acessar: http://localhost:8080
# Host: mysql
# Usuário: vendas_user
# Senha: vendas_pass
```

## 👤 Usuários Padrão

Após executar `python init_db.py`, os seguintes usuários são criados:

### **Administrador**

- **Email**: `admin@ceasa.com`
- **Senha**: `admin123`
- **Permissões**: Acesso total ao sistema

### **Funcionário**

- **Email**: `funcionario@ceasa.com`
- **Senha**: `func123`
- **Permissões**: Separação de pedidos, consultas

## 📦 Guia Completo dos Endpoints de Separação

### 🎯 Visão Geral

O sistema de separação permite que **funcionários** pesem/contem os produtos reais e atualizem as quantidades dos pedidos, diminuindo automaticamente do estoque usando o sistema FIFO.

### **PUT** `/api/vendas/{venda_id}/separacao`

**Descrição**: Separa produtos de uma venda, registra quantidades reais e diminui do estoque automaticamente.

**Permissão**: Usuários autenticados (funcionários e admins)

**Path Parameters**:

- `venda_id` (int, obrigatório): ID da venda a ser separada

**Headers**:

```
Authorization: Bearer {seu_token_jwt}
Content-Type: application/json
```

**Body (JSON)**:

```json
{
  "produtos_separados": [
    {
      "produto_id": 1,
      "quantidade_real": 2.5
    },
    {
      "produto_id": 2,
      "quantidade_real": 3.0
    }
  ]
}
```

**Exemplo Completo com cURL**:

```bash
curl -X PUT "http://localhost:8000/api/vendas/1/separacao" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "produtos_separados": [
      {
        "produto_id": 1,
        "quantidade_real": 2.3
      },
      {
        "produto_id": 5,
        "quantidade_real": 8.5
      }
    ]
  }'
```

**Response de Sucesso (200)**:

```json
{
  "data": {
    "id": 1,
    "cliente_id": 1,
    "cliente": {
      "id": 1,
      "nome": "João Silva",
      "email": "joao@silva.com"
    },
    "total_venda": 87.5,
    "situacao_pedido": "Separado",
    "situacao_pagamento": "Pendente",
    "data_venda": "2025-08-08T10:00:00",
    "data_separacao": "2025-08-08T14:30:15",
    "funcionario_separacao_id": 2,
    "funcionario_separacao": {
      "id": 2,
      "nome": "Funcionário CEASA",
      "email": "funcionario@ceasa.com"
    },
    "observacoes": "Pedido urgente",
    "itens": [
      {
        "id": 1,
        "produto_id": 1,
        "produto": {
          "id": 1,
          "nome": "Tomate",
          "tipo_medida": "kg"
        },
        "quantidade": 2.5,
        "quantidade_real": 2.3,
        "tipo_medida": "kg",
        "valor_unitario": 8.0,
        "valor_total_produto": 18.4
      }
    ]
  },
  "message": "Separação atualizada com sucesso. Estoque diminuído automaticamente.",
  "success": true
}
```

### **PUT** `/api/vendas/{venda_id}/cancelar-separacao`

**Descrição**: Cancela uma separação já feita, retornando os produtos ao estoque.

**Permissão**: Usuários autenticados (funcionários e admins)

**Exemplo com cURL**:

```bash
curl -X PUT "http://localhost:8000/api/vendas/1/cancelar-separacao" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Response de Sucesso (200)**:

```json
{
  "data": {
    "id": 1,
    "situacao_pedido": "A separar",
    "funcionario_separacao_id": null,
    "data_separacao": null,
    "total_venda": 92.5,
    "itens": [
      {
        "quantidade": 2.5,
        "quantidade_real": null,
        "valor_total_produto": 20.0
      }
    ]
  },
  "message": "Separação cancelada com sucesso. Produtos retornados ao estoque.",
  "success": true
}
```

## 📦 Guia Completo dos Endpoints de Estoque

### 🎯 Visão Geral

O sistema de estoque gerencia entradas de produtos, controle de inventário, alertas de estoque baixo e relatórios financeiros com sistema FIFO (First In, First Out).

### **GET** `/api/estoque/entradas`

**Descrição**: Lista todas as entradas de estoque com filtros e paginação.

**Permissão**: Usuários autenticados

**Query Parameters**:

- `skip` (int, opcional): Registros para pular (padrão: 0)
- `limit` (int, opcional): Registros por página (padrão: 20, máx: 100)
- `produto_id` (int, opcional): Filtrar por produto específico
- `data_inicio` (date, opcional): Data inicial (YYYY-MM-DD)
- `data_fim` (date, opcional): Data final (YYYY-MM-DD)

**Exemplo com cURL**:

```bash
curl -X GET "http://localhost:8000/api/estoque/entradas?limit=10&produto_id=1&data_inicio=2025-08-01" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### **POST** `/api/estoque/entradas`

**Descrição**: Cria nova entrada de estoque e atualiza inventário automaticamente.

**Permissão**: Apenas administradores

**Body (JSON)**:

```json
{
  "produto_id": 1,
  "quantidade": 25.5,
  "tipo_medida": "kg",
  "preco_custo": 4.2,
  "fornecedor": "Fazenda Verde Ltda",
  "observacoes": "Entrega da manhã - produtos frescos"
}
```

**Exemplo com cURL**:

```bash
curl -X POST "http://localhost:8000/api/estoque/entradas" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "produto_id": 1,
    "quantidade": 25.5,
    "tipo_medida": "kg",
    "preco_custo": 4.20,
    "fornecedor": "Fazenda Verde Ltda",
    "observacoes": "Entrega da manhã"
  }'
```

### **GET** `/api/estoque/inventario`

**Descrição**: Lista o inventário atual de todos os produtos.

**Query Parameters**:

- `estoque_baixo` (bool, opcional): Mostrar apenas estoque baixo (padrão: false)

**Exemplo com cURL**:

```bash
curl -X GET "http://localhost:8000/api/estoque/inventario?estoque_baixo=true" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### **GET** `/api/estoque/alertas`

**Descrição**: Lista produtos com estoque baixo ou zerado.

**Exemplo com cURL**:

```bash
curl -X GET "http://localhost:8000/api/estoque/alertas" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### **GET** `/api/estoque/fluxo-caixa`

**Descrição**: Relatório de fluxo de caixa com controle FIFO.

**Query Parameters**:

- `produto_id` (int, opcional): Filtrar por produto
- `data_inicio` (date, opcional): Data inicial (YYYY-MM-DD)
- `data_fim` (date, opcional): Data final (YYYY-MM-DD)

**Exemplo com cURL**:

```bash
curl -X GET "http://localhost:8000/api/estoque/fluxo-caixa?data_inicio=2025-08-01&data_fim=2025-08-31" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### **GET** `/api/estoque/rentabilidade`

**Descrição**: Relatório de rentabilidade por período com análise de lucro.

**Query Parameters**:

- `data_inicio` (date, obrigatório): Data inicial (YYYY-MM-DD)
- `data_fim` (date, obrigatório): Data final (YYYY-MM-DD)

**Exemplo com cURL**:

```bash
curl -X GET "http://localhost:8000/api/estoque/rentabilidade?data_inicio=2025-08-01&data_fim=2025-08-31" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

## 🔄 Fluxo Completo de Gestão

### **1. Login do Administrador**

```bash
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@ceasa.com&password=admin123"
```

### **2. Criar Entrada de Estoque**

```bash
curl -X POST "http://localhost:8000/api/estoque/entradas" \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "produto_id": 1,
    "quantidade": 50.0,
    "tipo_medida": "kg",
    "preco_custo": 3.50,
    "fornecedor": "Fazenda São João"
  }'
```

### **3. Separar uma Venda Específica**

```bash
curl -X PUT "http://localhost:8000/api/vendas/1/separacao" \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "produtos_separados": [
      {"produto_id": 1, "quantidade_real": 2.3},
      {"produto_id": 2, "quantidade_real": 1.8}
    ]
  }'
```

### **4. Gerar Relatório de Rentabilidade**

```bash
curl -X GET "http://localhost:8000/api/estoque/rentabilidade?data_inicio=2025-08-01&data_fim=2025-08-31" \
  -H "Authorization: Bearer {token}"
```

## 📊 Estrutura da Base de Dados

### **Tabelas Principais**

- `usuarios` - Controle de acesso
- `clientes` - Cadastro de clientes
- `produtos` - Catálogo de produtos
- `vendas` - Pedidos e vendas
- `itens_venda` - Itens dos pedidos

### **Sistema FIFO**

- `entradas_estoque` - Registro de entradas
- `estoque_fifo` - Controle FIFO de lotes
- `inventarios` - Estoque atual
- `movimentacoes_caixa` - Fluxo financeiro
- `lucros_brutos` - Cálculos de rentabilidade

## 🔑 Autenticação

### **Login**

```bash
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@ceasa.com","senha":"admin123"}'
```

### **Usar Token**

```bash
curl -X GET "http://localhost:8000/api/clientes/" \
  -H "Authorization: Bearer SEU_TOKEN_JWT"
```

## 📈 Exemplos de Uso

### **1. Criar Cliente**

```bash
curl -X POST "http://localhost:8000/api/clientes/" \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "nome": "João Silva",
    "cpf_ou_cnpj": "123.456.789-00",
    "endereco": "Rua das Flores, 123",
    "telefone1": "(11) 99999-1111",
    "email": "joao@email.com"
  }'
```

### **2. Registrar Entrada de Estoque**

```bash
curl -X POST "http://localhost:8000/api/estoque/entradas" \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "produto_id": 1,
    "quantidade": 50.0,
    "tipo_medida": "kg",
    "preco_custo": 3.50,
    "fornecedor": "Fazenda Verde"
  }'
```

### **3. Criar Venda**

```bash
curl -X POST "http://localhost:8000/api/vendas/" \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "cliente_id": 1,
    "observacoes": "Entrega pela manhã",
    "itens": [
      {
        "produto_id": 1,
        "quantidade": 5.0,
        "tipo_medida": "kg",
        "valor_unitario": 8.00
      }
    ]
  }'
```

### **4. Separar Pedido (com cálculo FIFO automático)**

```bash
curl -X PUT "http://localhost:8000/api/vendas/1/separacao" \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "produtos_separados": [
      {
        "produto_id": 1,
        "quantidade_real": 4.8
      }
    ]
  }'
```

### **5. Relatório de Rentabilidade**

```bash
curl -X GET "http://localhost:8000/api/estoque/rentabilidade?data_inicio=2025-08-01&data_fim=2025-08-31" \
  -H "Authorization: Bearer TOKEN"
```

## ✅ Funcionalidades Automáticas

### **O sistema faz automaticamente**:

- ✅ **Sistema FIFO**: Primeiro a entrar, primeiro a sair
- ✅ **Atualização de inventário**: Ao criar entradas
- ✅ **Cálculo de custos**: Baseado no FIFO para vendas
- ✅ **Alertas de estoque baixo**: Comparação com estoque mínimo
- ✅ **Relatórios financeiros**: Lucro, margem, fluxo de caixa
- ✅ **Rastreabilidade**: Histórico completo de movimentações

### **Validações Automáticas**:

- ✅ Produtos existem antes de criar entradas
- ✅ Quantidades são positivas
- ✅ Preços de custo são válidos
- ✅ Permissões de usuário respeitadas
- ✅ Dados consistentes entre modelos

## 🎯 Casos de Uso Práticos

### **Cenário 1: Separação Normal**

- Cliente pediu 3kg de tomate
- Funcionário pesou e deu 2.8kg
- Sistema aceita e cobra pelo peso real

### **Cenário 2: Estoque Insuficiente**

- Cliente pediu 5kg de batata
- Estoque só tem 3kg disponível
- Sistema bloqueia e mostra erro detalhado

### **Cenário 3: Controle de Estoque Baixo**

1. Sistema monitora estoques continuamente
2. Quando quantidade < estoque_mínimo → gera alerta
3. Endpoint `/alertas` mostra produtos críticos
4. Admin pode tomar ação preventiva

### **Cenário 4: Análise de Rentabilidade**

1. Admin consulta rentabilidade mensal
2. Sistema calcula lucro usando custos FIFO
3. Identifica produtos mais/menos rentáveis
4. Suporte para decisões estratégicas

## 🔍 Monitoramento e Logs

### **Logs da Aplicação**

```bash
# Logs em tempo real
docker compose logs -f api

# Logs específicos
docker compose logs api --tail=100
```

### **Logs do Banco**

```bash
# Ver logs do MySQL
docker compose logs mysql
```

### **Health Check**

```bash
# Verificar se API está respondendo
curl http://localhost:8000/

# Verificar documentação
curl http://localhost:8000/docs
```

## 🛡️ Segurança

- **JWT**: Autenticação segura com expiração configurável
- **CORS**: Configurado para desenvolvimento e produção
- **Validação**: Todos os inputs são validados via Pydantic
- **SQL Injection**: Proteção via SQLAlchemy ORM
- **Logs**: Registro de ações críticas do sistema

## 📊 Performance e Escalabilidade

- **Paginação**: Implementada em todas as listagens
- **Índices**: Otimizações no banco de dados
- **FIFO Otimizado**: Cálculos eficientes de custo
- **Cache**: Estratégias de cache para consultas frequentes
- **Conexões**: Pool de conexões configurado

## 🧪 Testes

### **Teste Manual via Swagger**

1. Acesse http://localhost:8000/docs
2. Clique em "Authorize"
3. Faça login via `/auth/login`
4. Cole o token retornado
5. Teste os endpoints interativamente

### **Teste via cURL**

```bash
# Script de teste completo
chmod +x test_api.sh
./test_api.sh
```

## 🐛 Troubleshooting

### **Problemas Comuns**

#### **1. Erro de conexão com MySQL**

```bash
# Verificar se MySQL está rodando
docker compose ps mysql

# Restart do MySQL
docker compose restart mysql

# Ver logs do MySQL
docker compose logs mysql
```

#### **2. Erro de build do Docker**

```bash
# Limpar cache e rebuild
docker system prune -f
docker compose build --no-cache
docker compose up -d
```

#### **3. Problemas de permissão**

```bash
# No Windows PowerShell
# Verificar se usuário tem permissões Docker
whoami
```

#### **4. Porta já em uso**

```bash
# Verificar o que está usando a porta 8000
netstat -an | findstr :8000

# Parar processo se necessário
docker compose down
```

### **Reset Completo**

```bash
# Parar tudo e limpar dados
docker compose down -v

# Limpar sistema Docker
docker system prune -f

# Subir novamente
docker compose up -d

# Reinicializar banco
python init_db.py
```

## 📞 Suporte

Para dúvidas ou problemas:

1. **Documentação**: http://localhost:8000/docs
2. **Logs**: `docker compose logs -f`
3. **Issues**: Abra um issue no repositório
4. **Email**: Contato do desenvolvedor

## 🔄 Atualizações

Para atualizar o sistema:

```bash
# 1. Parar serviços
docker compose down

# 2. Atualizar código
git pull origin main

# 3. Rebuild se necessário
docker compose build

# 4. Subir novamente
docker compose up -d

# 5. Rodar migrações se houver
alembic upgrade head
```

## 📋 Roadmap

### **Próximas Funcionalidades**

- [ ] Relatórios em PDF
- [ ] Integração com WhatsApp
- [ ] Dashboard web frontend
- [ ] Backup automático
- [ ] API webhooks
- [ ] Notificações push

### **Melhorias Técnicas**

- [ ] Testes automatizados
- [ ] CI/CD pipeline
- [ ] Monitoramento APM
- [ ] Cache Redis
- [ ] Rate limiting
- [ ] OpenAPI 3.1

## 📚 Documentação Completa da API

Para documentação detalhada de todos os endpoints, consulte o arquivo [`API_DOCUMENTATION.md`](API_DOCUMENTATION.md) que contém:

- 🔐 Todos os endpoints de autenticação
- 👥 CRUD completo de clientes
- 🥕 Gestão de produtos com upload de imagens
- 💰 Sistema completo de vendas
- 📦 Controle de estoque e inventário
- 💹 Relatórios financeiros avançados
- 🔄 Sistema FIFO detalhado
- 📊 Exemplos práticos de uso

## 📄 Licença

Este projeto está licenciado sob a [MIT License](LICENSE).

---

**Desenvolvido com ❤️ para otimizar a gestão de vendas no CEASA**
