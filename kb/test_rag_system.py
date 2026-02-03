"""Test RAG system with Doppler and GLM-4."""

import sys
from unittest.mock import MagicMock, patch

# Mock dependencies
sys.modules["spacy"] = MagicMock()
sys.modules["llama_index.core"] = MagicMock()
sys.modules["llama_index.embeddings.huggingface"] = MagicMock()

from fastapi.testclient import TestClient

def test_rag_with_glm():
    """Test RAG system with GLM-4 integration."""

    from kb.api.app import create_app

    app = create_app()
    client = TestClient(app)

    print("=== 1. Health Check ===")
    response = client.get('/health')
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    assert response.status_code == 200
    print("✅ Health check passed\n")

    print("=== 2. Test /ask Endpoint (with Mock Data) ===")

    # Mock retriever
    mock_retriever = MagicMock()
    mock_node = MagicMock()
    mock_node.node_id = "test-node-1"
    mock_node.metadata = {
        "title": "Introduction to RAG",
        "doc_id": "doc-1",
        "path": "/docs/rag.md",
        "heading_path": ["Introduction"],
        "anchor": "rag-intro"
    }
    mock_node.get_content.return_value = (
        "RAG (Retrieval-Augmented Generation) is a technique that combines "
        "retrieval systems with generative AI models to produce more accurate "
        "and contextual responses."
    )
    mock_retriever.retrieve.return_value = [(mock_node, 0.95)]

    # Mock GLM response
    mock_response = MagicMock()
    mock_choice_msg = MagicMock()
    mock_choice_msg.content = (
        "Based on the retrieved document [S1], RAG or Retrieval-Augmented "
        "Generation is a technique that enhances LLMs with external knowledge bases."
    )
    mock_choice = MagicMock()
    mock_choice.message = mock_choice_msg
    mock_response.choices = [mock_choice]

    # Create mock zhipuai client
    mock_zhipuai = MagicMock()
    mock_completions = MagicMock()
    mock_completions.create.return_value = mock_response
    mock_zhipuai.chat.completions = mock_completions

    # Mock config
    from kb.config import AppConfig
    config = AppConfig(
        index=MagicMock(content_roots=["docs"]),
        embedding=MagicMock(model="BAAI/bge-small-en-v1.5"),
        storage=MagicMock(persist_dir="kb_index/storage"),
        vector_store=MagicMock(table_name="kb_llama_nodes", embed_dim=384),
        chunking=MagicMock(),
        bm25=MagicMock(persist_dir="kb_index/bm25"),
        output=MagicMock(),
        llm=MagicMock(
            provider="zhipuai",
            model="glm-4",
            api_key="test-api-key-from-doppler"
        ),
        retrieval=MagicMock(top_k=10, rrf_k=60, use_bm25=True),
        api=MagicMock(host="0.0.0.0", port=8000, cors_origins=["*"])
    )

    # Test with mocks
    import zhipuai

    with patch('kb.api.dependencies.get_config', return_value=config):
        # Mock zhipuai at module level
        with patch('zhipuai.ZhipuAI', return_value=mock_zhipuai):
            with patch('kb.api.dependencies.create_retriever', return_value=mock_retriever):
                response = client.post(
                    '/api/v1/ask',
                    json={"query": "What is RAG?", "top_k": 5}
                )

                print(f"Status: {response.status_code}")
                assert response.status_code == 200, f"Failed: {response.text}"

                data = response.json()
                print(f"✅ Status: {response.status_code}")
                print(f"Answer preview: {data['answer'][:150]}...")
                print(f"Method: {data['method']}")
                print(f"Sources found: {len(data['sources'])}")
                print(f"Citation status: {data['status']}")

                assert data['method'] == "react_agent"
                assert "[S1]" in data['answer']
                assert len(data['sources']) > 0
                assert data['status'] == "verified"

    print("\n=== 3. Test /search Endpoint ===")
    response = client.post(
        '/api/v1/search',
        json={"query": "RAG", "top_k": 3}
    )

    print(f"Status: {response.status_code}")
    assert response.status_code == 200

    data = response.json()
    print(f"Results: {data['total']} found")
    assert data['total'] == 1
    assert len(data['results']) == 1
    print(f"Top result: {data['results'][0]['metadata']['title']}")
    print("✅ Search endpoint working\n")

    print("=== ✅ All Tests Passed ===")
    print("\nRAG System Components Verified:")
    print("  ✅ FastAPI server")
    print("  ✅ Health check endpoint")
    print("  ✅ /ask endpoint with GLM-4 integration")
    print("  ✅ /search endpoint")
    print("  ✅ Citation alignment system")
    print("  ✅ Mock GLM-4 responses")
    print("\nNext Steps:")
    print("  1. Set valid GLM_API_KEY in Doppler")
    print("  2. Test with real GLM-4 API:")
    print("     doppler run -- uvicorn kb.api.app:create_app --port 8000")
    print("     curl -X POST http://localhost:8000/api/v1/ask -H 'Content-Type: application/json' \\")
    print("       -d '{\"query\": \"What is RAG?\"}'")


if __name__ == "__main__":
    test_rag_with_glm()
