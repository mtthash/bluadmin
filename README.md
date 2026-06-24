# BluAdmin

Sistema corporativo de gerenciamento de colaboradores integrado ao Active Directory on-premises via LDAP/LDAPS.

Desenvolvido para a **Blumenau Iluminacao**, permite que administradores realizem **onboarding** e **offboarding** de colaboradores atraves de uma interface web com tema dark, com criacao automatica de contas no AD, atribuicao de departamentos e auditoria completa.

## Stack Tecnologico

| Camada | Tecnologia |
|--------|-----------|
| Frontend | React 18 + TypeScript + Material UI 6 |
| Backend | FastAPI + Python 3.12 + SQLAlchemy 2 (async) |
| Banco de Dados | PostgreSQL 16 |
| Autenticacao | JWT local (bcrypt + python-jose) |
| Integracao | Active Directory via LDAP/LDAPS (ldap3) |
| Containerizacao | Docker + Docker Compose |

## Funcionalidades

- **Onboarding**: Cadastro de colaborador com criacao automatica no AD, senha temporaria, atribuicao a departamento/grupo
- **Offboarding**: Bloqueio de login no AD, remocao de grupos, agendamento de exclusao definitiva com prazo customizavel
- **Exclusao agendada**: Countdown visual com remocao automatica do AD e banco apos o prazo (scheduler em background)
- **Departamentos**: Gerenciamento de departamentos como grupos do AD, criaveis pela interface
- **Colaboradores**: Listagem com filtros por status, detalhes, desativacao e exclusao definitiva
- **Permissoes**: CRUD de usuarios da plataforma (admin/visualizador) com protecao do admin principal
- **Atividades**: Log completo de acoes com filtro por periodo rapido e modo tempo real (polling 5s)
- **Tema dark**: Interface com cores da Blumenau Iluminacao, cursor glow, loading com lampada pulsante

## Pre-requisitos

- Docker e Docker Compose
- Servidor Active Directory acessivel via rede (LDAP porta 389 ou LDAPS porta 636)
- Para definicao de senhas no onboarding: LDAPS habilitado no AD (ver secao abaixo)

## Instalacao

### 1. Clone o repositorio

```bash
git clone <url-do-repositorio>
cd bluadmin
```

### 2. Configure as variaveis de ambiente

```bash
cp .env.example .env
```

Edite o arquivo `.env`:

```env
# Active Directory
LDAP_SERVER=192.168.1.250
LDAP_PORT=636
LDAP_USE_SSL=true
LDAP_BIND_DN=CN=admin,CN=Users,DC=seudominio,DC=local
LDAP_BIND_PASSWORD=sua-senha
LDAP_BASE_DN=CN=Users,DC=seudominio,DC=local
LDAP_DOMAIN=seudominio.local

# JWT (troque em producao)
JWT_SECRET_KEY=chave-secreta-com-pelo-menos-32-caracteres

# Banco
POSTGRES_PASSWORD=uma-senha-forte
```

### 3. Habilitar LDAPS no AD (obrigatorio para definicao de senhas)

Copie o script `scripts/enable-ldaps.ps1` para o Windows Server e execute como Administrador:

```powershell
powershell -ExecutionPolicy Bypass -File .\enable-ldaps.ps1
```

### 4. Suba os containers

```bash
docker compose up --build
```

Na primeira execucao, o sistema automaticamente:
- Roda as migrations do banco
- Cria os grupos BluAdmin-HR, BluAdmin-IT e BluAdmin-Admin no AD
- Cria o usuario `admin` com senha `admin` na plataforma

### 5. Acesse a aplicacao

- **Frontend**: http://localhost:3000
- **API Docs (Swagger)**: http://localhost:8000/docs
- **Login padrao**: `admin` / `admin`

## Arquitetura

### Autenticacao

O BluAdmin possui **dois sistemas separados**:

1. **Usuarios da plataforma** (tabela `platform_users`): Quem faz login no BluAdmin. Autenticacao local com bcrypt + JWT HS256.
2. **Colaboradores** (tabela `users` + Active Directory): Pessoas gerenciadas via onboarding/offboarding. Criados/desativados no AD via LDAP.

### Permissoes

| Funcionalidade | Administrador | Visualizador |
|----------------|:---:|:---:|
| Dashboard | X | X |
| Listar colaboradores | X | X |
| Ver detalhes do colaborador | X | X |
| Onboarding (criar colaborador) | X | |
| Offboarding (desativar colaborador) | X | |
| Excluir colaborador definitivamente | X | |
| Gerenciar departamentos | X | |
| Gerenciar usuarios da plataforma | X | |
| Visualizar log de atividades | X | |

O usuario `admin` possui protecao contra rebaixamento, desativacao ou remocao.

## Estrutura do Projeto

```
bluadmin/
├── backend/
│   ├── app/
│   │   ├── api/v1/          # Endpoints (auth, employees, departments, platform-users, audit)
│   │   ├── auth/            # JWT local + permissoes
│   │   ├── core/            # Logging, exceptions, security (bcrypt)
│   │   ├── db/              # SQLAlchemy base + session
│   │   ├── integrations/ldap/  # Conexao, usuarios e grupos do AD
│   │   ├── middleware/      # Security headers, logging, error handler
│   │   ├── models/          # User, PlatformUser, AuditLog, Role, Permission
│   │   ├── schemas/         # Pydantic schemas + validators
│   │   └── services/        # Employee, PlatformUser, Department, Audit, DeletionScheduler
│   └── alembic/             # Migrations do banco
├── frontend/
│   └── src/
│       ├── auth/            # AuthProvider (JWT), ProtectedRoute, roleGuard
│       ├── assets/          # Logo Blumenau Iluminacao
│       ├── components/      # Layout, employees, audit, effects (GlowCursor)
│       ├── hooks/           # React Query hooks
│       ├── pages/           # Dashboard, Employees, Onboarding, Departments, Permissions, Audit
│       ├── services/        # Chamadas a API (axios)
│       └── config/          # Theme dark, API config
├── scripts/
│   └── enable-ldaps.ps1     # Script para habilitar LDAPS no Windows Server
└── docker-compose.yml
```

## Seguranca

- **Senhas**: Bcrypt hash para usuarios da plataforma, LDAPS para senhas do AD
- **JWT**: HS256 com expiracao de 8 horas, validacao em toda request
- **RBAC**: Permissoes granulares verificadas no backend e frontend
- **SQL Injection**: SQLAlchemy ORM exclusivo
- **XSS**: React auto-escape + CSP headers + validacao Pydantic com regex
- **CSRF**: Bearer token via header (sem cookies de sessao)
- **Security Headers**: CSP, X-Frame-Options DENY, nosniff, HSTS
- **Protecao admin**: Impossivel rebaixar/desativar/remover o administrador principal
- **Auditoria**: Registro completo de todas as acoes incluindo tentativas bloqueadas

## Melhorias Futuras

- Notificacoes por e-mail ao gestor com credenciais do novo colaborador
- Importacao em lote via CSV para onboarding multiplo
- Dashboard com graficos de historico
- Exportacao de relatorios de auditoria em PDF/Excel
- Testes automatizados (unitarios e integracao)
- CI/CD pipeline
