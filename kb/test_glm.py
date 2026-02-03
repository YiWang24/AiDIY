"""Test script for GLM-4 configuration."""

import os
import sys

def test_glm_config():
    """Test GLM-4 configuration and API connection."""

    # Check environment variable
    api_key = os.getenv("GLM_API_KEY")
    if not api_key:
        print("❌ GLM_API_KEY not found in environment")
        print("\nTo set it up with Doppler:")
        print("  1. Create a Doppler project")
        print("  2. Add GLM_API_KEY secret")
        print("  3. Run: doppler run -- python test_glm.py")
        return False

    print(f"✓ GLM_API_KEY found (length: {len(api_key)})")

    # Test zhipuai import
    try:
        from zhipuai import ZhipuAI
        print("✓ zhipuai package imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import zhipuai: {e}")
        return False

    # Test configuration loading
    try:
        from kb.config import load_config, load_env_database_url

        config_path = os.getenv("KB_CONFIG", "config.example.yaml")
        config = load_config(config_path)
        config = load_env_database_url(config)

        print(f"✓ Config loaded from {config_path}")
        print(f"  Provider: {config.llm.provider}")
        print(f"  Model: {config.llm.model}")
        print(f"  Temperature: {config.llm.temperature}")
        print(f"  API Key: {'✓ Set' if config.llm.api_key else '✗ Not set'}")

        # Validate provider is zhipuai
        if config.llm.provider != "zhipuai":
            print(f"\n⚠️  Warning: Provider is '{config.llm.provider}', expected 'zhipuai'")
            print("   Update config.example.yaml llm.provider to 'zhipuai'")

    except Exception as e:
        print(f"❌ Config loading failed: {e}")
        return False

    # Test LLM initialization (without actual API call)
    try:
        from zhipuai import ZhipuAI

        client = ZhipuAI(
            api_key=config.llm.api_key,
        )
        print("✓ ZhipuAI client initialized successfully")
    except Exception as e:
        print(f"❌ ZhipuAI client initialization failed: {e}")
        return False

    # Optional: Test actual API call (only if --test-api flag is provided)
    if "--test-api" in sys.argv:
        print("\n🔄 Testing API call...")
        try:
            response = client.chat.completions.create(
                model=config.llm.model,
                messages=[{"role": "user", "content": "Hello, please respond with 'OK' if you can understand this."}],
                temperature=config.llm.temperature,
            )
            print(f"✓ API call successful")
            if hasattr(response, 'choices'):
                print(f"  Response: {response.choices[0].message.content[:100]}...")
            elif hasattr(response, 'content'):
                print(f"  Response: {response.content[:100]}...")
        except Exception as e:
            print(f"❌ API call failed: {e}")
            print("\nPossible issues:")
            print("  1. Invalid API key")
            print("  2. Network connectivity")
            print("  3. Rate limiting")
            print("  4. Model name incorrect")
            return False
    else:
        print("\n💡 Tip: Use '--test-api' flag to test actual API call")

    return True


if __name__ == "__main__":
    print("=" * 60)
    print("GLM-4 Configuration Test")
    print("=" * 60)
    print()

    success = test_glm_config()

    print()
    print("=" * 60)
    if success:
        print("✅ All checks passed!")
        print("\nTo run the API server:")
        print("  doppler run -- uvicorn kb.api.app:create_app --host 0.0.0.0 --port 8000")
    else:
        print("❌ Some checks failed")
        sys.exit(1)
