# CI/CD Architecture for KB API

## Overview

正确的 Doppler 配置架构：

```
┌─────────────────────────────────────────────┐
│         GitHub Actions Workflow              │
│                                             │
│  从 Doppler STG 读取:                        │
│  - ACR credentials (推送到 Azure)            │
│  - SSH keys (连接到 VPS)                     │
│  - DOPPLER_TOKEN (注入 PRD secrets)         │
└──────────────────┬──────────────────────────┘
                   │
                   ▼
         ┌─────────────────┐
         │  Build Docker    │
         │  Push to ACR     │
         └────────┬─────────┘
                  │
                  ▼
         ┌─────────────────┐
         │  SSH to VPS     │
         └────────┬─────────┘
                  │
                  ▼
┌─────────────────────────────────────────────┐
│         VPS (Jump Server)                    │
│                                             │
│  使用 DOPPLER_TOKEN 读取 PRD 配置:            │
│  - DATABASE_URL                             │
│  - GEMINI_API_KEY                           │
│  - TAVILY_API_KEY                           │
│  - SENTRY_DSN                               │
│  - Feature flags                            │
│                                             │
│  通过 `doppler run` 注入到 Docker 容器        │
└─────────────────────────────────────────────┘
```

## Doppler Configuration

### STG Config (GitHub Actions 凭证)

GitHub Actions 运行时需要的凭证，**不是**应用运行时的环境变量：

```yaml
# Azure Container Registry
ACR_LOGIN_SERVER: your-acr.azurecr.io
ACR_REPOSITORY: kb-api
ACR_USERNAME: your-acr-username
ACR_PASSWORD: your-acr-password

# SSH Deployment
DEPLOY_SSH_HOST: your-vps.example.com
DEPLOY_SSH_USER: deploy
DEPLOY_SSH_KEY: |
  -----BEGIN OPENSSH PRIVATE KEY-----
  ...
  -----END OPENSSH PRIVATE KEY-----
DEPLOY_SSH_PORT: 22
DEPLOY_WORKDIR: /opt/kb-api

# Doppler Configuration
DOPPLER_TOKEN: dp.x.xxxxxx  # Service token for reading PRD config
DOPPLER_PROJECT: portfolio-api
DOPPLER_TARGET_CONFIG: prd  # GitHub Actions 将部署到 PRD 环境

# Health Check
HEALTHCHECK_URL: https://your-api.example.com/health

# Sentry Release Tracking
SENTRY_AUTH_TOKEN: your-sentry-auth-token
SENTRY_ORG: your-org
SENTRY_PROJECT: kb-api
```

### PRD Config (应用运行时环境变量)

应用运行时需要的环境变量，通过 Doppler 注入到容器：

```yaml
# Database
DATABASE_URL: postgresql://postgres:PgPass!123@10.0.0.4:15432/smart_sred
PGVECTOR: true

# LLM
GEMINI_API_KEY: your-gemini-api-key

# Web Search
TAVILY_API_KEY: tvly-xxxxx
BRAVE_API_KEY: your-brave-api-key

# Observability
SENTRY_DSN: https://your-sentry-dsn@sentry.io/project-id
SENTRY_ENVIRONMENT: production

# Feature Flags
USE_HYBRID_SEARCH: true
USE_RERANKING: true
WEB_FALLBACK_ENABLED: true

# Performance
TOP_K_DEFAULT: 10
MAX_CONTEXT_LENGTH: 4000
PORT: 8000
LOG_LEVEL: INFO
```

## GitHub Actions Workflow

### CI Workflow (`.github/workflows/ci.yml`)

**触发条件**: PR 或 push 到 main

**任务**:
1. **Code Quality** - Ruff (lint, format), Bandit (security), Pytest
2. **Docker Build** - 验证 Dockerfile 可以成功构建

**不需要 Doppler secrets** - 使用测试值

### Release Workflow (`.github/workflows/release.yml`)

**触发条件**: Push 到 main 或 tag

**任务**:
1. **Pre-release Checks** - Lint + Tests (70% coverage required)
2. **Build & Push to ACR** - 构建并推送 Docker 镜像到 Azure
3. **Deploy to VPS** - 部署到生产环境

**Secrets 来源**:
- 从 GitHub Secrets 读取（从 Doppler STG 同步）
- 用于 GitHub Actions 流程本身

## Deployment Flow

### 步骤 1: GitHub Actions 读取 STG 配置

```yaml
env:
  # 从 Doppler STG 读取的 GitHub Actions 凭证
  DEPLOY_SSH_HOST: ${{ secrets.DEPLOY_SSH_HOST }}
  DEPLOY_SSH_KEY: ${{ secrets.DEPLOY_SSH_KEY }}
  ACR_LOGIN_SERVER: ${{ secrets.ACR_LOGIN_SERVER }}
  ACR_PASSWORD: ${{ secrets.ACR_PASSWORD }}
  DOPPLER_TOKEN: ${{ secrets.DOPPLER_TOKEN }}  # Service token
```

### 步骤 2: 构建并推送 Docker 镜像

```bash
docker build -t kb-api:sha-abc123 .
docker push your-acr.azurecr.io/kb-api:sha-abc123
```

### 步骤 3: SSH 到 VPS

```bash
ssh deploy@vps "cd /opt/kb-api &&部署脚本"
```

### 步骤 4: VPS 使用 DOPPLER_TOKEN 读取 PRD 配置

```bash
# 在 VPS 上执行
DOPPLER_TOKEN="dp.x.xxxxxx" \
DOPPLER_PROJECT="portfolio-api" \
DOPPLER_CONFIG="prd" \
doppler run -- \
docker compose up -d
```

Doppler 会：
1. 使用 `DOPPLER_TOKEN` 认证
2. 读取 `portfolio-api` 项目的 `prd` 配置
3. 注入所有 PRD 环境变量到 Docker 容器
4. 启动容器

## Setup Instructions

### 1. 配置 Doppler STG (GitHub Actions 凭证)

```bash
# 安装 Doppler CLI
brew install dopplerhq/cli/doppler

# 登录
doppler login

# 配置 STG
doppler secrets set ACR_LOGIN_SERVER "your-acr.azurecr.io" --project portfolio-api --config stg
doppler secrets set ACR_USERNAME "your-username" --project portfolio-api --config stg
doppler secrets set ACR_PASSWORD "your-password" --project portfolio-api --config stg

# ... 其他 GitHub Actions 凭证
```

### 2. 配置 Doppler PRD (应用环境变量)

```bash
# 配置 PRD
doppler secrets set DATABASE_URL "postgresql://..." --project portfolio-api --config prd
doppler secrets set GEMINI_API_KEY "your-key" --project portfolio-api --config prd
doppler secrets set TAVILY_API_KEY "tvly-..." --project portfolio-api --config prd

# ... 其他应用环境变量
```

### 3. 创建 Doppler Service Token

GitHub Actions 需要 service token 来读取 PRD 配置：

```bash
# 在 Doppler Dashboard 创建 Service Token
# 或者用 CLI (需要权限)
doppler tokens create --project portfolio-api --config prd
```

保存输出的 token 到 `DOPPLER_TOKEN` (STG 配置)

### 4. 同步到 GitHub Secrets

从 Doppler STG 复制所有 secrets 到 GitHub：

```bash
# 方法 1: 使用 Doppler CLI
doppler secrets download --project portfolio-api --config stg --format env > .env.stg

# 手动复制每个 secret 到 GitHub:
# Settings → Secrets and variables → Actions → New repository secret
```

### 5. 验证配置

```bash
# 验证 STG 配置 (GitHub Actions 凭证)
doppler secrets --project portfolio-api --config stg --only-names

# 验证 PRD 配置 (应用环境变量)
doppler secrets --project portfolio-api --config prd --only-names

# 测试 Doppler 注入
doppler run --project portfolio-api --config prd -- env | grep DATABASE_URL
```

## Secret 分类

### GitHub Actions Secrets (来自 Doppler STG)

| Secret Name | 用途 | 谁使用 |
|------------|------|--------|
| ACR_LOGIN_SERVER | Azure Container Registry | GitHub Actions |
| ACR_USERNAME | ACR 用户名 | GitHub Actions |
| ACR_PASSWORD | ACR 密码 | GitHub Actions |
| DEPLOY_SSH_HOST | VPS 主机名 | GitHub Actions |
| DEPLOY_SSH_USER | SSH 用户名 | GitHub Actions |
| DEPLOY_SSH_KEY | SSH 私钥 | GitHub Actions |
| DEPLOY_SSH_PORT | SSH 端口 | GitHub Actions |
| DEPLOY_WORKDIR | 部署目录 | GitHub Actions |
| DOPPLER_TOKEN | Service Token | VPS |
| DOPPLER_PROJECT | 项目名 | GitHub Actions + VPS |
| DOPPLER_TARGET_CONFIG | 目标配置 (prd) | VPS |
| HEALTHCHECK_URL | 健康检查 URL | GitHub Actions |
| SENTRY_AUTH_TOKEN | Sentry 认证 | GitHub Actions |
| SENTRY_ORG | Sentry 组织 | GitHub Actions |
| SENTRY_PROJECT | Sentry 项目 | GitHub Actions |

### Application Secrets (来自 Doppler PRD)

| Secret Name | 用途 | 谁使用 |
|------------|------|--------|
| DATABASE_URL | 数据库连接 | 应用容器 |
| GEMINI_API_KEY | LLM API | 应用容器 |
| TAVILY_API_KEY | 搜索 API | 应用容器 |
| SENTRY_DSN | Sentry DSN | 应用容器 |
| USE_HYBRID_SEARCH | 特性开关 | 应用容器 |
| ... | 其他应用配置 | 应用容器 |

## Security Best Practices

1. **分离关注点**:
   - STG 配置只包含 CI/CD 凭证
   - PRD 配置只包含应用环境变量

2. **最小权限原则**:
   - DOPPLER_TOKEN 是 service token，只能读取 PRD 配置
   - SSH key 只能用于部署，不能用于其他用途

3. **定期轮换**:
   - 定期更新 ACR 密码
   - 定期轮换 SSH keys
   - 定期轮换 DOPPLER_TOKEN

4. **审计日志**:
   - Doppler 提供完整的 secret 访问日志
   - GitHub Actions 提供工作流运行日志

## Troubleshooting

### GitHub Actions 无法连接到 Doppler

```bash
# 检查 DOPPLER_TOKEN 是否有效
doppler me

# 检查 service token 权限
# 在 Doppler Dashboard 查看 token 权限
```

### VPS 部署时无法注入环境变量

```bash
# 在 VPS 上测试 Doppler
ssh deploy@vps
doppler run --project portfolio-api --config prd -- env | grep DATABASE_URL

# 检查 DOPPLER_TOKEN 权限
# 确保可以读取 PRD 配置
```

### 容器启动失败

```bash
# 检查容器日志
docker logs kb-api

# 检查环境变量是否注入
docker exec kb-api env | grep -E "DATABASE_URL|GEMINI_API_KEY"

# 手动测试 Doppler 注入
doppler run --project portfolio-api --config prd -- docker compose up
```

## References

- [Doppler Documentation](https://docs.doppler.com/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Azure Container Registry](https://docs.microsoft.com/en-us/azure/container-registry/)
