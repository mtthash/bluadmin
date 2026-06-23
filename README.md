# BluAdmin

Sistema corporativo de gerenciamento de colaboradores integrado ao Microsoft Entra ID (Azure AD).

Permite que equipes de RH e TI realizem **onboarding** e **offboarding** de colaboradores através de uma interface web, com criação automática de contas no Azure AD, atribuição de grupos/setores e auditoria completa.

## Stack Tecnológico

| Camada | Tecnologia |
|--------|-----------|
| Frontend | React 18 + TypeScript + Material UI 6 |
| Backend | FastAPI + Python 3.12 + SQLAlchemy 2 (async) |
| Banco de Dados | PostgreSQL 16 |
| Autenticação | Azure Entra ID (OAuth2/OIDC via MSAL) |
| Integração | Microsoft Graph API |
| Containerização | Docker + Docker Compose |

## Funcionalidades

- **Onboarding**: Cadastro de colaborador com criação automática no Entra ID, senha temporária com troca obrigatória, atribuição a grupo/setor
- **Offboarding**: Bloqueio de login, revogação de sessões, remoção de grupos e licenças (sem exclusão da conta)
- **Consulta de Setores**: Carregados dinamicamente dos grupos do Azure AD via Graph API
- **Listagem de Colaboradores**: Nome, e-mail, UPN, status, setor, data de criação
- **Auditoria**: Registro completo de quem fez o quê, quando, para quem, com resultado
- **RBAC**: Perfis RH, TI e Administrador com permissões granulares

## Pré-requisitos

- Docker e Docker Compose
- Tenant do Azure AD com permissões de administrador
- Duas App Registrations no Azure Portal (ver seção de configuração)

## Configuração do Azure AD

### App Registration 1: "BluAdmin Frontend" (SPA)

1. Acesse o [Azure Portal](https://portal.azure.com) > Azure Active Directory > App Registrations
2. Crie uma nova registration com nome "BluAdmin Frontend"
3. Plataforma: **Single-page application (SPA)**
4. Redirect URI: `http://localhost:3000`
5. Anote o **Application (client) ID** e o **Directory (tenant) ID**

### App Registration 2: "BluAdmin Backend" (Web API)

1. Crie outra registration com nome "BluAdmin Backend"
2. Plataforma: **Web**
3. Gere um **Client Secret** (anote o valor)
4. Em "Expose an API":
   - Defina o Application ID URI: `api://{client-id}`
   - Adicione o scope: `access_as_user`
5. Em "API Permissions" (tipo **Application**, não Delegated):
   - `User.ReadWrite.All`
   - `Group.ReadWrite.All`
   - `Directory.ReadWrite.All`
6. Conceda **Admin Consent** para as permissões acima
7. Em "Token Configuration": adicione o claim opcional `groups` nos tokens Access e ID

### Grupos do Azure AD

Crie (ou identifique) os grupos para os perfis de acesso:
- Grupo para **RH** (ex: "BluAdmin-HR")
- Grupo para **TI** (ex: "BluAdmin-IT")
- Grupo para **Administradores** (ex: "BluAdmin-Admin")

Anote os **Object IDs** de cada grupo.

## Instalação

### 1. Clone o repositório

```bash
git clone <url-do-repositorio>
cd bluadmin
```

### 2. Configure as variáveis de ambiente

```bash
cp .env.example .env
```

Edite o arquivo `.env` com os valores do seu tenant Azure:

```env
AZURE_TENANT_ID=seu-tenant-id
AZURE_CLIENT_ID=client-id-do-backend
AZURE_CLIENT_SECRET=secret-do-backend
AZURE_FRONTEND_CLIENT_ID=client-id-do-frontend

AZURE_GROUP_ID_HR=object-id-do-grupo-hr
AZURE_GROUP_ID_IT=object-id-do-grupo-it
AZURE_GROUP_ID_ADMIN=object-id-do-grupo-admin

POSTGRES_PASSWORD=uma-senha-forte-aqui
```

### 3. Suba os containers

```bash
docker compose up --build
```

### 4. Acesse a aplicação

- **Frontend**: http://localhost:3000
- **Backend (Swagger)**: http://localhost:8000/api/docs
- **Backend (Health)**: http://localhost:8000/api/v1/health

## Estrutura do Projeto

```
bluadmin/
├── backend/            # API FastAPI
│   ├── app/
│   │   ├── api/        # Rotas da API v1
│   │   ├── auth/       # Validação JWT + RBAC
│   │   ├── core/       # Logging, exceptions
│   │   ├── db/         # SQLAlchemy base + session
│   │   ├── integrations/graph/  # Microsoft Graph API
│   │   ├── middleware/  # Security headers, logging, error handler
│   │   ├── models/     # SQLAlchemy models
│   │   ├── schemas/    # Pydantic schemas + validators
│   │   └── services/   # Lógica de negócio
│   └── alembic/        # Migrations do banco
├── frontend/           # React SPA
│   └── src/
│       ├── auth/       # MSAL provider + protected routes
│       ├── components/ # Componentes reutilizáveis
│       ├── hooks/      # React Query hooks
│       ├── pages/      # Páginas da aplicação
│       ├── services/   # Chamadas à API
│       └── types/      # TypeScript types
└── docker-compose.yml
```

## Segurança

O projeto implementa proteções contra todas as vulnerabilidades do OWASP Top 10:

- **SQL Injection**: SQLAlchemy ORM exclusivo, zero SQL raw
- **XSS**: React auto-escape + CSP headers rigorosos + validação Pydantic com regex
- **CSRF**: Bearer token via header (sem cookies de sessão)
- **Broken Auth**: JWT RS256 validado em toda request, JWKS rotation automática
- **Data Exposure**: Senhas nunca em logs/DB local, HSTS em produção
- **Broken Access Control**: RBAC granular em todas as rotas + rate limiting
- **Security Headers**: CSP, X-Frame-Options DENY, nosniff, HSTS, Permissions-Policy
- **Logging**: Auditoria completa sem PII nos logs, dados sensíveis filtrados

## Permissões RBAC

| Ação | RH | TI | Admin |
|------|:--:|:--:|:-----:|
| Criar colaborador | X | X | X |
| Consultar colaborador | X | X | X |
| Listar colaboradores | X | X | X |
| Desabilitar colaborador | | X | X |
| Consultar setores | X | X | X |
| Visualizar auditoria | | | X |
| Gerenciar usuários | | | X |

## Deploy em Produção (Linux)

### 1. Servidor

- Ubuntu 22.04+ ou similar
- Docker e Docker Compose instalados
- Domínio configurado com certificado SSL (Let's Encrypt / Certbot)

### 2. Variáveis de ambiente

```bash
# Ajuste para produção
ENVIRONMENT=production
CORS_ORIGINS=["https://seu-dominio.com"]
POSTGRES_PASSWORD=senha-muito-forte-gerada-aleatoriamente
VITE_API_BASE_URL=https://seu-dominio.com/api/v1
VITE_REDIRECT_URI=https://seu-dominio.com
```

### 3. Build de produção

```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml up --build -d
```

### 4. Nginx reverso (host)

Configure um Nginx no host para terminar SSL e fazer proxy para os containers:

```nginx
server {
    listen 443 ssl http2;
    server_name seu-dominio.com;

    ssl_certificate /etc/letsencrypt/live/seu-dominio.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/seu-dominio.com/privkey.pem;

    location / {
        proxy_pass http://localhost:3000;
    }

    location /api/ {
        proxy_pass http://localhost:8000;
    }
}
```

### 5. Atualize as App Registrations

- Redirect URI do frontend: `https://seu-dominio.com`
- CORS origins: `https://seu-dominio.com`

## Melhorias Futuras

- **Notificações por e-mail**: Enviar credenciais ao gestor via Microsoft Graph Send Mail
- **Importação em lote**: Upload de CSV para onboarding de múltiplos colaboradores
- **Dashboard avançado**: Gráficos com histórico de onboarding/offboarding
- **Integração com Teams**: Notificar canais sobre novos colaboradores
- **Backup de conta**: Exportar dados do usuário antes do offboarding (OneDrive, Mailbox)
- **Workflow de aprovação**: Fluxo de aprovação multi-nível para onboarding
- **MFA enforcement**: Forçar MFA para novos usuários via Conditional Access Policy
- **Relatórios**: Exportação de relatórios de auditoria em PDF/Excel
- **Testes automatizados**: Suite completa de testes unitários e de integração
- **CI/CD**: Pipeline GitHub Actions para build, test e deploy automático
