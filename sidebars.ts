import type { SidebarsConfig } from "@docusaurus/plugin-content-docs";

const sidebars: SidebarsConfig = {
  // CS Core Sidebar
  csSidebar: [
    {
      type: "doc",
      id: "cs/index",
      label: "CS Core Overview",
    },
    {
      type: "category",
      label: "Algorithms & DS",
      collapsed: false,
      items: [
        {
          type: "doc",
          id: "cs/algorithms/index",
          label: "Overview",
        },
      ],
    },
    {
      type: "category",
      label: "System Design",
      collapsed: false,
      items: [
        {
          type: "doc",
          id: "cs/system-design/index",
          label: "Index",
        },
        {
          type: "doc",
          label: "1. Entry Layer",
          id: "cs/system-design/entry-layer",
        },
        {
          type: "doc",
          label: "2. Service Layer",
          id: "cs/system-design/service-layer",
        },
        {
          type: "doc",
          label: "3. Storage Layer",
          id: "cs/system-design/storage-layer",
        },
        {
          type: "doc",
          label: "4. Caching Layer",
          id: "cs/system-design/caching-layer",
        },
        {
          type: "doc",
          label: "5. Messaging & Analytics",
          id: "cs/system-design/messaging-analytics-layer",
        },
        {
          type: "doc",
          label: "6. Back-of-the-Envelope Estimation",
          id: "cs/system-design/back-of-envelope-estimation",
        },
        {
          type: "doc",
          label: "7. Consistent Hashing",
          id: "cs/system-design/consistent-hashing",
        },
        {
          type: "doc",
          label: "8. Notification System",
          id: "cs/system-design/notification-system",
        },
      ],
    },
    {
      type: "category",
      label: "Database Internals",
      collapsed: false,
      items: [
        {
          type: "doc",
          id: "cs/database/index",
          label: "Overview",
        },
      ],
    },
    {
      type: "category",
      label: "Network & OS",
      collapsed: false,
      items: [
        {
          type: "doc",
          id: "cs/network-os/index",
          label: "Overview",
        },
      ],
    },
  ],

  // AI & Agents Sidebar
  aiSidebar: [
    {
      type: "doc",
      id: "ai/index",
      label: "AI & Agents Overview",
    },
    {
      type: "category",
      label: "LLM Fundamentals",
      collapsed: false,
      items: [
        {
          type: "doc",
          id: "ai/llm-fundamentals/index",
          label: "Overview",
        },
        {
          type: "doc",
          id: "ai/llm-fundamentals/introduction",
          label: "1. Introduction",
        },
        {
          type: "doc",
          id: "ai/llm-fundamentals/tokenization",
          label: "2. Tokenization",
        },
        {
          type: "doc",
          id: "ai/llm-fundamentals/embeddings",
          label: "3. Embeddings",
        },
        {
          type: "doc",
          id: "ai/llm-fundamentals/transformer-architecture",
          label: "4. Transformer Architecture",
        },
        {
          type: "doc",
          id: "ai/llm-fundamentals/inference",
          label: "5. Inference",
        },
        {
          type: "doc",
          id: "ai/llm-fundamentals/limitations",
          label: "7. Limitations",
        },
        {
          type: "doc",
          id: "ai/llm-fundamentals/training-pipeline",
          label: "6. Training Pipeline",
        },
      ],
    },
    {
      type: "category",
      label: "Prompt Engineering",
      collapsed: false,
      items: [
        {
          type: "doc",
          id: "ai/prompt-engineering/index",
          label: "Overview",
        },
        {
          type: "doc",
          id: "ai/prompt-engineering/introduction",
          label: "1. Introduction",
        },
        {
          type: "doc",
          id: "ai/prompt-engineering/prompt-anatomy",
          label: "2.1 Prompt Anatomy",
        },
        {
          type: "doc",
          id: "ai/prompt-engineering/reasoning-patterns",
          label: "2.2 Core Reasoning Patterns",
        },
        {
          type: "doc",
          id: "ai/prompt-engineering/structured-output",
          label: "2.3 Structured Output",
        },
        {
          type: "doc",
          id: "ai/prompt-engineering/spring-ai",
          label: "2.4 Spring AI Implementation",
        },
        {
          type: "doc",
          id: "ai/prompt-engineering/evaluation-versioning",
          label: "2.5 Evaluation & Versioning",
        },
        {
          type: "doc",
          id: "ai/prompt-engineering/advanced-techniques",
          label: "2.6 Advanced Techniques",
        },
        {
          type: "doc",
          id: "ai/prompt-engineering/agent-orchestration",
          label: "2.7 Agent Orchestration",
        },
        {
          type: "doc",
          id: "ai/prompt-engineering/multimodal",
          label: "2.8 Multimodal",
        },
      ],
    },
    {
      type: "category",
      label: "RAG",
      collapsed: false,
      items: [
        {
          type: "doc",
          id: "ai/rag/index",
          label: "Overview",
        },
        {
          type: "doc",
          id: "ai/rag/introduction",
          label: "1. RAG Fundamentals",
        },
        {
          type: "doc",
          id: "ai/rag/data-processing",
          label: "2. Data Processing",
        },
        {
          type: "doc",
          id: "ai/rag/retrieval",
          label: "3. Retrieval",
        },
        {
          type: "doc",
          id: "ai/rag/generation",
          label: "5. Generation",
        },
        {
          type: "doc",
          id: "ai/rag/evaluation",
          label: "6. Evaluation",
        },
        {
          type: "doc",
          id: "ai/rag/advanced-rag",
          label: "7. Advanced RAG",
        },
        {
          type: "doc",
          id: "ai/rag/production",
          label: "8. Production",
        },
        {
          type: "doc",
          id: "ai/rag/best-practices",
          label: "9. Best Practices",
        },
      ],
    },
    {
      type: "category",
      label: "Agents",
      collapsed: false,
      items: [
        {
          type: "doc",
          id: "ai/agents/index",
          label: "Overview",
        },
        {
          type: "doc",
          id: "ai/agents/introduction",
          label: "1. Core Concepts & Definition",
        },
        {
          type: "doc",
          id: "ai/agents/architecture",
          label: "2. Architecture Components",
        },
        {
          type: "doc",
          id: "ai/agents/design-patterns",
          label: "3. Design Patterns",
        },
        {
          type: "doc",
          id: "ai/agents/frameworks",
          label: "4. Frameworks & Tech Stack",
        },
        {
          type: "doc",
          id: "ai/agents/engineering",
          label: "5. Engineering & Production",
        },
        {
          type: "doc",
          id: "ai/agents/frontier",
          label: "6. Frontier Trends",
        },
      ],
    },
    {
      type: "category",
      label: "MCP",
      collapsed: false,
      items: [
        {
          type: "doc",
          id: "ai/mcp/index",
          label: "Overview",
        },
        {
          type: "doc",
          id: "ai/mcp/interview-qa",
          label: "Interview Q&A",
        },
      ],
    },
    {
      type: "category",
      label: "Context Engineering",
      collapsed: false,
      items: [
        {
          type: "doc",
          id: "ai/context-engineering/index",
          label: "Overview",
        },
      ],
    },
    {
      type: "category",
      label: "AgentOps & Security",
      collapsed: false,
      items: [
        {
          type: "doc",
          id: "ai/agentops-security/index",
          label: "Overview",
        },
      ],
    },
    {
      type: "category",
      label: "Java & AI Internship",
      collapsed: false,
      items: [
        {
          type: "doc",
          id: "ai/internship/internship",
          label: "Java & AI Internship Guide",
        },
      ],
    },
  ],

  // Engineering Sidebar
  engineeringSidebar: [
    {
      type: "doc",
      id: "engineering/index",
      label: "Engineering Overview",
    },
    {
      type: "category",
      label: "Backend (Java)",
      collapsed: false,
      items: [
        {
          type: "doc",
          id: "engineering/backend/index",
          label: "Overview",
        },
        {
          type: "doc",
          id: "engineering/backend/concurrency",
          label: "Concurrency Programming",
        },
      ],
    },
    {
      type: "category",
      label: "Frontend",
      collapsed: false,
      items: [
        {
          type: "doc",
          id: "engineering/frontend/index",
          label: "Overview",
        },
      ],
    },
    {
      type: "category",
      label: "DevOps & Cloud",
      collapsed: false,
      items: [
        {
          type: "doc",
          id: "engineering/devops/index",
          label: "Overview",
        },
      ],
    },
    {
      type: "category",
      label: "Dev Tools",
      collapsed: false,
      items: [
        {
          type: "doc",
          id: "engineering/tools/index",
          label: "Overview",
        },
      ],
    },
  ],

  // Case Studies Sidebar
  projectsSidebar: [
    {
      type: "doc",
      id: "projects/index",
      label: "Case Studies Overview",
    },
    {
      type: "category",
      label: "RAG Knowledge Base",
      collapsed: false,
      items: [
        {
          type: "doc",
          id: "projects/rag-knowledge-base",
          label: "RAG Knowledge Base",
        },
      ],
    },
    {
      type: "category",
      label: "E-commerce Refactor",
      collapsed: false,
      items: [
        {
          type: "doc",
          id: "projects/ecommerce-refactor",
          label: "E-commerce Refactor",
        },
      ],
    },
  ],
};

export default sidebars;
