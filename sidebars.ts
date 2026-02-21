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
        {
          type: "category",
          label: "Data Structures",
          collapsed: false,
          items: [
            { type: "doc", id: "cs/algorithms/arrays-strings", label: "1. Arrays & Strings" },
            { type: "doc", id: "cs/algorithms/linked-lists", label: "2. Linked Lists" },
            { type: "doc", id: "cs/algorithms/stacks-queues", label: "3. Stacks & Queues" },
            { type: "doc", id: "cs/algorithms/hash-maps", label: "4. HashMaps & HashSets" },
            { type: "doc", id: "cs/algorithms/trees", label: "5. Trees" },
            { type: "doc", id: "cs/algorithms/heaps", label: "6. Heaps" },
            { type: "doc", id: "cs/algorithms/graphs", label: "7. Graphs" },
            { type: "doc", id: "cs/algorithms/tries", label: "8. Tries" },
            { type: "doc", id: "cs/algorithms/sorting", label: "9. Sorting" },
          ],
        },
        {
          type: "category",
          label: "Algorithm Patterns",
          collapsed: false,
          items: [
            { type: "doc", id: "cs/algorithms/two-pointers", label: "10. Two Pointers" },
            { type: "doc", id: "cs/algorithms/sliding-window", label: "11. Sliding Window" },
            { type: "doc", id: "cs/algorithms/binary-search", label: "12. Binary Search" },
            { type: "doc", id: "cs/algorithms/greedy", label: "13. Greedy" },
            { type: "doc", id: "cs/algorithms/backtracking", label: "14. Backtracking" },
            { type: "doc", id: "cs/algorithms/dynamic-programming", label: "15. Dynamic Programming" },
            { type: "doc", id: "cs/algorithms/searching", label: "16. Search Strategies" },
          ],
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
      label: "Database",
      collapsed: false,
      items: [
        {
          type: "doc",
          id: "cs/database/index",
          label: "Overview",
        },
        {
          type: "category",
          label: "MySQL",
          collapsed: false,
          items: [
            {
              type: "doc",
              id: "cs/database/mysql/index",
              label: "Overview",
            },
            {
              type: "doc",
              id: "cs/database/mysql/architecture",
              label: "Architecture & Storage Engines",
            },
            {
              type: "doc",
              id: "cs/database/mysql/indexes",
              label: "Indexes",
            },
            {
              type: "doc",
              id: "cs/database/mysql/transactions",
              label: "Transactions",
            },
            {
              type: "doc",
              id: "cs/database/mysql/locking",
              label: "Locking",
            },
            {
              type: "doc",
              id: "cs/database/mysql/logging-replication",
              label: "Logging & Replication",
            },
            {
              type: "doc",
              id: "cs/database/mysql/optimization",
              label: "SQL Optimization",
            },
          ],
        },
        {
          type: "category",
          label: "Redis",
          collapsed: false,
          items: [
            {
              type: "doc",
              id: "cs/database/redis/index",
              label: "Overview",
            },
            {
              type: "doc",
              id: "cs/database/redis/data-structures",
              label: "Data Structures",
            },
            {
              type: "doc",
              id: "cs/database/redis/persistence",
              label: "Persistence (RDB & AOF)",
            },
            {
              type: "doc",
              id: "cs/database/redis/cluster",
              label: "Cluster & Sentinel",
            },
            {
              type: "doc",
              id: "cs/database/redis/caching-patterns",
              label: "Caching Patterns",
            },
          ],
        },
        {
          type: "category",
          label: "Advanced Topics",
          collapsed: true,
          items: [
            {
              type: "doc",
              id: "cs/database/advanced/deadlocks",
              label: "Deadlock Prevention",
            },
            {
              type: "doc",
              id: "cs/database/advanced/connection-pooling",
              label: "Connection Pooling",
            },
            {
              type: "doc",
              id: "cs/database/advanced/nosql-comparison",
              label: "NoSQL Comparison",
            },
          ],
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
        {
          type: "category",
          label: "TCP/IP Five-Layer Model",
          collapsed: false,
          items: [
            {
              type: "doc",
              id: "cs/network-os/physical-layer",
              label: "1. Physical Layer",
            },
            {
              type: "doc",
              id: "cs/network-os/data-link-layer",
              label: "2. Data Link Layer",
            },
            {
              type: "doc",
              id: "cs/network-os/network-layer",
              label: "3. Network Layer",
            },
            {
              type: "doc",
              id: "cs/network-os/transport-layer",
              label: "4. Transport Layer",
            },
            {
              type: "doc",
              id: "cs/network-os/application-layer",
              label: "5. Application Layer",
            },
          ],
        },
        {
          type: "category",
          label: "Troubleshooting",
          collapsed: true,
          items: [
            {
              type: "doc",
              id: "cs/network-os/troubleshooting/index",
              label: "Overview",
            },
          ],
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
