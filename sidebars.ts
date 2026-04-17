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
          key: "cs-algorithms-overview",
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
          key: "cs-database-overview",
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
              key: "cs-mysql-overview",
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
              key: "cs-redis-overview",
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
      label: "Operating System",
      collapsed: false,
      items: [
        {
          type: "doc",
          id: "cs/os/index",
          label: "Overview",
          key: "cs-os-overview",
        },
        { type: "doc", id: "cs/os/introduction", label: "1. Introduction to OS" },
        { type: "doc", id: "cs/os/process-management", label: "2. Process Management" },
        { type: "doc", id: "cs/os/threads-concurrency", label: "3. Threads & Concurrency" },
        { type: "doc", id: "cs/os/memory-management", label: "4. Memory Management" },
        { type: "doc", id: "cs/os/file-system", label: "5. File System" },
        { type: "doc", id: "cs/os/io-system", label: "6. I/O System" },
        { type: "doc", id: "cs/os/storage-system", label: "7. Storage System" },
        { type: "doc", id: "cs/os/security-protection", label: "8. Security & Protection" },
        { type: "doc", id: "cs/os/virtualization", label: "9. Virtualization" },
        { type: "doc", id: "cs/os/linux-essentials", label: "10. Linux Essentials" },
      ],
    },
    {
      type: "category",
      label: "Computer Network",
      collapsed: false,
      items: [
        {
          type: "doc",
          id: "cs/network-os/index",
          label: "Overview",
          key: "cs-network-os-overview",
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
              key: "cs-network-os-troubleshooting-overview",
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
          key: "ai-llm-overview",
        },
        {
          type: "doc",
          id: "ai/llm-fundamentals/introduction",
          label: "1. Introduction",
          key: "ai-llm-intro",
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
          key: "ai-prompt-overview",
        },
        {
          type: "doc",
          id: "ai/prompt-engineering/introduction",
          label: "1. Introduction",
          key: "ai-prompt-intro",
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
          key: "ai-rag-overview",
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
        { type: "doc", id: "ai/agents/index", label: "Overview" },
        { type: "doc", id: "ai/agents/01-introduction", label: "1. Core Concepts", key: "ai-agents-core-concepts" },
        { type: "doc", id: "ai/agents/02-architecture", label: "2. Architecture" },
        { type: "doc", id: "ai/agents/03-design-patterns", label: "3. Design Patterns" },
        { type: "doc", id: "ai/agents/04-frameworks", label: "4. Frameworks & SDK" },
        { type: "doc", id: "ai/agents/05-coding-agents", label: "5. Coding Agents" },
        { type: "doc", id: "ai/agents/06-computer-use", label: "6. Computer Use & GUI Agents" },
        { type: "doc", id: "ai/agents/07-multi-agent", label: "7. Multi-Agent & A2A" },
        { type: "doc", id: "ai/agents/08-evaluation", label: "8. Evaluation & Benchmarks" },
        { type: "doc", id: "ai/agents/09-engineering", label: "9. Engineering & Production" },
        { type: "doc", id: "ai/agents/10-frontier", label: "10. Frontier Trends" },
      ],
    },
    {
      type: "category",
      label: "Harness Engineering",
      collapsed: false,
      items: [
        {
          type: "doc",
          id: "ai/harness-engineering/index",
          label: "Overview",
          key: "ai-harness-overview",
        },
        {
          type: "doc",
          id: "ai/harness-engineering/core-concepts",
          label: "1. Core Concepts",
        },
        {
          type: "doc",
          id: "ai/harness-engineering/orchestration",
          label: "2. Tool Orchestration",
        },
        {
          type: "doc",
          id: "ai/harness-engineering/state-management",
          label: "3. State Management",
        },
        {
          type: "doc",
          id: "ai/harness-engineering/error-handling",
          label: "4. Error Handling & Recovery",
        },
        {
          type: "doc",
          id: "ai/harness-engineering/observability",
          label: "5. Observability",
        },
        {
          type: "doc",
          id: "ai/harness-engineering/safety-guards",
          label: "6. Safety & Guardrails",
        },
        {
          type: "doc",
          id: "ai/harness-engineering/patterns",
          label: "7. Production Patterns",
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
          key: "ai-mcp-overview",
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
          key: "ai-context-eng-overview",
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
          key: "ai-agentops-overview",
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
          key: "eng-backend-overview",
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
          key: "eng-frontend-overview",
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
          key: "eng-devops-overview",
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
          key: "eng-tools-overview",
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
    {
      type: "category",
      label: "Open SWE",
      collapsed: false,
      items: [
        {
          type: "doc",
          id: "projects/open-swe",
          label: "Open SWE Agent",
        },
      ],
    },
  ],
};

export default sidebars;
