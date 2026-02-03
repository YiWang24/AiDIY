# GLM-4 Setup with Doppler

This guide shows how to configure the KB Agent to use GLM-4 through Doppler for secret management.

## Prerequisites

1. Install Doppler CLI:
```bash
brew install dopplerhq/cli/doppler
# or
npm install -g dopplerhq/cli
```

2. Install Python dependencies:
```bash
pip install zhipuai langchain-community
```

## Doppler Setup

### 1. Create a Doppler Project

```bash
# Navigate to the kb directory
cd kb

# Initialize Doppler project
doppler setup

# Select or create a project (e.g., "kb-agent")
```

### 2. Configure Secrets

Add the following secrets to your Doppler project:

```bash
# Set GLM API Key
doppler secrets set GLM_API_KEY "your-zhipuai-api-key"

# Optional: Set Database URL (if using PostgreSQL)
doppler secrets set DATABASE_URL "postgresql://user:password@localhost:5432/kb"

# Optional: Set custom config path
doppler secrets set KB_CONFIG "config.example.yaml"
```

### 3. Verify Configuration

```bash
# Run the test script with Doppler
doppler run -- python test_glm.py

# Test with actual API call
doppler run -- python test_glm.py --test-api
```

## Configuration File

Update `config.example.yaml`:

```yaml
llm:
  provider: zhipuai
  model: glm-4  # or glm-4-plus, glm-4-0520, glm-4-air, etc.
  api_key: ${GLM_API_KEY:-}
  temperature: 0.0
```

## Running the Application

### Development Server

```bash
# Using Doppler to inject secrets
doppler run -- uvicorn kb.api.app:create_app --host 0.0.0.0 --port 8000 --reload
```

### Production Server

```bash
# Using Doppler with production config
doppler run --production -- uvicorn kb.api.app:create_app --host 0.0.0.0 --port 8000 --workers 4
```

### CLI Commands

```bash
# Build index with Doppler
doppler run -- kb-index-build --config config.example.yaml --verify

# Validate config
doppler run -- kb-index-build validate --config config.example.yaml
```

## GLM-4 Model Options

Available models in ZhipuAI GLM series:

- `glm-4` - Standard GLM-4 model
- `glm-4-plus` - Enhanced GLM-4
- `glm-4-0520` - GLM-4 with 128k context
- `glm-4-air` - Lightweight version
- `glm-4-flash` - Fast inference version
- `glm-4-long` - Long context version

Update the `model` field in config to use different variants.

## Testing the Setup

### 1. Test Configuration

```bash
doppler run -- python test_glm.py
```

Expected output:
```
✓ GLM_API_KEY found (length: 32)
✓ zhipuai package imported successfully
✓ Config loaded from config.example.yaml
  Provider: zhipuai
  Model: glm-4
  Temperature: 0.0
  API Key: ✓ Set
✓ ZhipuAI client initialized successfully
```

### 2. Test API Call

```bash
doppler run -- python test_glm.py --test-api
```

### 3. Test API Endpoints

Start the server:
```bash
doppler run -- uvicorn kb.api.app:create_app --host 0.0.0.0 --port 8000
```

Test `/ask` endpoint:
```bash
curl -X POST http://localhost:8000/api/v1/ask \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is RAG?",
    "top_k": 5
  }'
```

## Troubleshooting

### Issue: "GLM_API_KEY not found"

**Solution**: Make sure the secret is set in Doppler:
```bash
doppler secrets list
# If GLM_API_KEY is missing:
doppler secrets set GLM_API_KEY "your-api-key"
```

### Issue: "ImportError: No module named 'zhipuai'"

**Solution**: Install the package:
```bash
pip install zhipuai
# or add to pyproject.toml:
# "zhipuai>=2.1"
```

### Issue: "Authentication failed"

**Solution**: Verify your API key:
```bash
# Check if key is set
doppler secrets get GLM_API_KEY

# Test with zhipuai CLI
doppler run -- python -c "from zhipuai import ZhipuAI; client = ZhipuAI(api_key='YOUR_KEY'); print('OK')"
```

### Issue: "Model not found"

**Solution**: Check available model names:
- Use `glm-4` instead of `glm-4.7`
- See ZhipuAI documentation for current model names

### Issue: "Doppler: No project configured"

**Solution**: Setup Doppler project:
```bash
doppler setup
# Follow the prompts to select/create project
```

## Doppler Commands Reference

```bash
# List all secrets
doppler secrets list

# Get a specific secret
doppler secrets get GLM_API_KEY

# Set a secret
doppler secrets set GLM_API_KEY "value"

# Open Doppler dashboard
doppler open

# Run command with secrets injected
doppler run -- <command>

# Run with specific environment
doppler run --production -- <command>

# Run with specific config file
doppler run --config config.prod.yaml -- <command>
```

## Security Best Practices

1. **Never commit API keys** - Use Doppler for all secrets
2. **Use different keys for dev/prod** - Create separate Doppler environments
3. **Rotate keys regularly** - Update secrets with `doppler secrets set`
4. **Limit key permissions** - Only grant necessary scopes
5. **Monitor usage** - Check ZhipuAI dashboard for API usage

## Next Steps

1. ✅ Install Doppler CLI
2. ✅ Create Doppler project
3. ✅ Set GLM_API_KEY secret
4. ✅ Run `doppler run -- python test_glm.py`
5. ✅ Start server with `doppler run -- uvicorn ...`
6. ✅ Test `/ask` endpoint

For more information:
- [Doppler Documentation](https://docs.doppler.com)
- [ZhipuAI GLM-4 API](https://open.bigmodel.cn/dev/api)
- [LangChain Documentation](https://python.langchain.com)
