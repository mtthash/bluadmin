# BluAdmin

Sistema corporativo de gerenciamento de colaboradores integrado ao Active Directory on-premises via LDAP/LDAPS.

Desenvolvido para **ESTUDOS**, permite que administradores realizem **onboarding** e **offboarding** de colaboradores atraves de uma interface web com tema dark, com criacao automatica de contas no AD, gerenciamento de departamentos com persistencia local, servidor de arquivos com pastas por departamento e auditoria completa.

## Stack Tecnologico

| Camada | Tecnologia |
|--------|-----------|
| Frontend | React 18 + TypeScript + Material UI 6 |
| Backend | FastAPI + Python 3.12 + SQLAlchemy 2 (async) |
| Banco de Dados | PostgreSQL 16 |
| Autenticacao | JWT local (bcrypt + python-jose) |
| Integracao AD | Active Directory via LDAP/LDAPS (ldap3) |
| File Server | Compartilhamento SMB + WinRM (pywinrm) |
| Containerizacao | Docker + Docker Compose |

## Funcionalidades

- **Onboarding**: Cadastro de colaborador com criacao automatica no AD, atribuicao a departamento/grupo e mapeamento de pasta
- **Offboarding**: Bloqueio de login no AD, remocao de grupos, agendamento de exclusao definitiva com prazo customizavel
- **Exclusao agendada**: Countdown visual com remocao automatica do AD e banco apos o prazo (scheduler em background)
- **Departamentos**: Gerenciamento persistido no PostgreSQL com sync opcional ao AD. Criacao automatica de pasta no file server
- **File Server**: Servidor de arquivos integrado com pastas por departamento, permissoes NTFS por grupo AD e criacao automatica via WinRM
- **Mapeamento de pastas**: Controle de mapeamento de drives por colaborador (qual pasta/drive), com API CRUD e interface no frontend
- **Colaboradores**: Listagem com filtros por status, detalhes, menu de acoes (pastas mapeadas, desativar, excluir)
- **Permissoes**: CRUD de usuarios da plataforma (admin/visualizador) com protecao do admin principal
- **Atividades**: Log completo de acoes com filtro por periodo rapido e modo tempo real (polling 5s)
- **Dashboard**: Painel com graficos de colaboradores por departamento, status (pizza), movimentacoes mensais (linha) e atividade recente
- **Tema dark**: Interface com cores da Blumenau Iluminacao

## Pre-requisitos

- Docker e Docker Compose
- Servidor Active Directory acessivel via rede (LDAP porta 389 ou LDAPS porta 636)
- WinRM habilitado no servidor AD (para criacao automatica de pastas de departamento)
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

# File Server
FILE_SHARE_SERVER=192.168.1.250
FILE_SHARE_NAME=Departamentos
FILE_SHARE_DEFAULT_DRIVE=X:
FOLDER_MAPPING_API_KEY=chave-secreta-para-api-do-agent

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

### 4. Habilitar WinRM no AD (necessario para criacao automatica de pastas)

No servidor AD, execute como Administrador:

```powershell
Enable-PSRemoting -Force
Set-Service -Name WinRM -StartupType Automatic
```

### 5. Configurar compartilhamento de arquivos

No servidor AD, crie o compartilhamento:

```powershell
# Criar compartilhamento (ajuste o path conforme seu disco)
New-SmbShare -Name "Departamentos" -Path "X:\" -FullAccess "DOMINIO\Domain Admins" -ReadAccess "DOMINIO\Domain Users"
```

As pastas de departamentos serao criadas automaticamente pela API ao cadastrar novos departamentos.

### 6. Suba os containers

```bash
docker compose up --build
```

Na primeira execucao, o sistema automaticamente:
- Roda as migrations do banco (5 migrations: schema inicial, platform users, exclusao agendada, departamentos, folder mappings)
- Cria o usuario `admin` com senha `admin` na plataforma
- Os departamentos (e seus grupos no AD) sao criados pelo menu Departamentos na interface

### 7. Acesse a aplicacao

- **Frontend**: http://localhost:3000
- **API Docs (Swagger)**: http://localhost:8000/docs (login: admin/admin)
- **Login padrao**: `admin` / `admin`

## Arquitetura

### Autenticacao

O BluAdmin possui **dois sistemas separados**:

1. **Usuarios da plataforma** (tabela `platform_users`): Quem faz login no BluAdmin. Autenticacao local com bcrypt + JWT HS256.
2. **Colaboradores** (tabela `users` + Active Directory): Pessoas gerenciadas via onboarding/offboarding. Criados/desativados no AD via LDAP.

### Banco de Dados

| Tabela | Descricao |
|--------|-----------|
| `users` | Colaboradores (espelho do AD) |
| `departments` | Departamentos persistidos localmente |
| `folder_mappings` | Mapeamentos de pasta por usuario |
| `platform_users` | Usuarios que acessam o BluAdmin |
| `roles` / `permissions` | RBAC |
| `audit_logs` | Log de todas as acoes |

### Integracoes

- **LDAP/AD**: Criacao, desativacao e exclusao de usuarios; gerenciamento de grupos
- **File Server (WinRM)**: Criacao automatica de pastas de departamento com permissoes NTFS por grupo AD
- **PostgreSQL**: Armazenamento primario de departamentos, mapeamentos e dados da plataforma

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
| Gerenciar mapeamento de pastas | X | |
| Gerenciar usuarios da plataforma | X | |
| Visualizar log de atividades | X | |

O usuario `admin` possui protecao contra rebaixamento, desativacao ou remocao.

## Estrutura do Projeto

```
bluadmin/
├── backend/
│   ├── app/
│   │   ├── api/v1/             # Endpoints (auth, employees, departments, folder_mappings, audit, platform-users)
│   │   ├── auth/               # JWT local + permissoes
│   │   ├── core/               # Logging, exceptions, security (bcrypt)
│   │   ├── db/                 # SQLAlchemy base + session (async)
│   │   ├── integrations/
│   │   │   ├── ldap/           # Conexao, usuarios e grupos do AD
│   │   │   └── fileshare/      # Criacao de pastas via WinRM
│   │   ├── middleware/         # Security headers (CSP), logging, error handler
│   │   ├── models/             # User, Department, FolderMapping, PlatformUser, AuditLog, Role, Permission
│   │   ├── schemas/            # Pydantic schemas + validators
│   │   └── services/           # Employee, Department, FolderMapping, PlatformUser, Audit, DeletionScheduler
│   └── alembic/                # Migrations (001-005)
├── frontend/
│   └── src/
│       ├── auth/               # AuthProvider (JWT), ProtectedRoute, roleGuard
│       ├── components/         # Layout, employees (tabela, card, onboarding), departments, audit
│       ├── hooks/              # React Query hooks
│       ├── pages/              # Dashboard, Employees, Onboarding, Departments, Permissions, Audit
│       ├── services/           # Chamadas a API (axios) — employee, department, folderMapping
│       ├── types/              # TypeScript interfaces (employee, department, folderMapping)
│       └── config/             # Theme dark, API config
├── scripts/
│   └── enable-ldaps.ps1        # Script para habilitar LDAPS no Windows Server
└── docker-compose.yml
```

## Seguranca

- **Senhas**: Bcrypt hash para usuarios da plataforma, LDAPS para senhas do AD
- **JWT**: HS256 com expiracao de 8 horas, validacao em toda request
- **RBAC**: Permissoes granulares verificadas no backend e frontend
- **SQL Injection**: SQLAlchemy ORM exclusivo
- **XSS**: React auto-escape + CSP headers + validacao Pydantic com regex
- **CSRF**: Bearer token via header (sem cookies de sessao)
- **Security Headers**: CSP, X-Frame-Options DENY, nosniff, HSTS (producao)
- **API Docs**: Protegido por Basic Auth (apenas em ambiente dev)
- **Protecao admin**: Impossivel rebaixar/desativar/remover o administrador principal
- **LDAP resiliente**: Falhas de conexao ao AD nao bloqueiam operacoes do banco local
- **Auditoria**: Registro completo de todas as acoes incluindo tentativas bloqueadas

## Melhorias Futuras

- Mapeamento automatico de drives nas maquinas do dominio (agent Windows)
- Notificacoes por e-mail ao gestor com credenciais do novo colaborador
- Importacao em lote via CSV para onboarding multiplo
- Exportacao de relatorios de auditoria em PDF/Excel
- Testes automatizados (unitarios e integracao)
- CI/CD pipeline
