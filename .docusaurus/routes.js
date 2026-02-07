import React from 'react';
import ComponentCreator from '@docusaurus/ComponentCreator';

export default [
  {
    path: '/__docusaurus/debug/',
    component: ComponentCreator('/__docusaurus/debug/', '546'),
    exact: true
  },
  {
    path: '/__docusaurus/debug/config/',
    component: ComponentCreator('/__docusaurus/debug/config/', '8a8'),
    exact: true
  },
  {
    path: '/__docusaurus/debug/content/',
    component: ComponentCreator('/__docusaurus/debug/content/', '2da'),
    exact: true
  },
  {
    path: '/__docusaurus/debug/globalData/',
    component: ComponentCreator('/__docusaurus/debug/globalData/', '178'),
    exact: true
  },
  {
    path: '/__docusaurus/debug/metadata/',
    component: ComponentCreator('/__docusaurus/debug/metadata/', 'd6c'),
    exact: true
  },
  {
    path: '/__docusaurus/debug/registry/',
    component: ComponentCreator('/__docusaurus/debug/registry/', '6e3'),
    exact: true
  },
  {
    path: '/__docusaurus/debug/routes/',
    component: ComponentCreator('/__docusaurus/debug/routes/', 'cab'),
    exact: true
  },
  {
    path: '/blog/',
    component: ComponentCreator('/blog/', 'fe9'),
    exact: true
  },
  {
    path: '/blog/archive/',
    component: ComponentCreator('/blog/archive/', '1d9'),
    exact: true
  },
  {
    path: '/blog/authors/',
    component: ComponentCreator('/blog/authors/', '347'),
    exact: true
  },
  {
    path: '/blog/first-blog-post/',
    component: ComponentCreator('/blog/first-blog-post/', 'acf'),
    exact: true
  },
  {
    path: '/blog/tags/',
    component: ComponentCreator('/blog/tags/', 'e17'),
    exact: true
  },
  {
    path: '/blog/tags/docusaurus/',
    component: ComponentCreator('/blog/tags/docusaurus/', '8ce'),
    exact: true
  },
  {
    path: '/blog/tags/hello/',
    component: ComponentCreator('/blog/tags/hello/', '2a4'),
    exact: true
  },
  {
    path: '/docs/',
    component: ComponentCreator('/docs/', '39b'),
    routes: [
      {
        path: '/docs/',
        component: ComponentCreator('/docs/', '119'),
        routes: [
          {
            path: '/docs/tags/',
            component: ComponentCreator('/docs/tags/', 'dc9'),
            exact: true
          },
          {
            path: '/docs/tags/advanced/',
            component: ComponentCreator('/docs/tags/advanced/', 'de2'),
            exact: true
          },
          {
            path: '/docs/tags/agents/',
            component: ComponentCreator('/docs/tags/agents/', 'eea'),
            exact: true
          },
          {
            path: '/docs/tags/ai/',
            component: ComponentCreator('/docs/tags/ai/', 'df6'),
            exact: true
          },
          {
            path: '/docs/tags/chat-client/',
            component: ComponentCreator('/docs/tags/chat-client/', 'efa'),
            exact: true
          },
          {
            path: '/docs/tags/cot/',
            component: ComponentCreator('/docs/tags/cot/', '60b'),
            exact: true
          },
          {
            path: '/docs/tags/document-understanding/',
            component: ComponentCreator('/docs/tags/document-understanding/', '51d'),
            exact: true
          },
          {
            path: '/docs/tags/evaluation/',
            component: ComponentCreator('/docs/tags/evaluation/', '546'),
            exact: true
          },
          {
            path: '/docs/tags/introduction/',
            component: ComponentCreator('/docs/tags/introduction/', '74a'),
            exact: true
          },
          {
            path: '/docs/tags/java/',
            component: ComponentCreator('/docs/tags/java/', 'a6b'),
            exact: true
          },
          {
            path: '/docs/tags/json/',
            component: ComponentCreator('/docs/tags/json/', 'aac'),
            exact: true
          },
          {
            path: '/docs/tags/llm/',
            component: ComponentCreator('/docs/tags/llm/', '4f6'),
            exact: true
          },
          {
            path: '/docs/tags/mcp/',
            component: ComponentCreator('/docs/tags/mcp/', '83a'),
            exact: true
          },
          {
            path: '/docs/tags/meta-prompting/',
            component: ComponentCreator('/docs/tags/meta-prompting/', '2b8'),
            exact: true
          },
          {
            path: '/docs/tags/metrics/',
            component: ComponentCreator('/docs/tags/metrics/', '5a1'),
            exact: true
          },
          {
            path: '/docs/tags/mlops/',
            component: ComponentCreator('/docs/tags/mlops/', '4f4'),
            exact: true
          },
          {
            path: '/docs/tags/multi-agent/',
            component: ComponentCreator('/docs/tags/multi-agent/', '65c'),
            exact: true
          },
          {
            path: '/docs/tags/multimodal/',
            component: ComponentCreator('/docs/tags/multimodal/', 'b07'),
            exact: true
          },
          {
            path: '/docs/tags/orchestration/',
            component: ComponentCreator('/docs/tags/orchestration/', 'fba'),
            exact: true
          },
          {
            path: '/docs/tags/prompt-engineering/',
            component: ComponentCreator('/docs/tags/prompt-engineering/', '8cc'),
            exact: true
          },
          {
            path: '/docs/tags/prompt-structure/',
            component: ComponentCreator('/docs/tags/prompt-structure/', '80d'),
            exact: true
          },
          {
            path: '/docs/tags/prompt-template/',
            component: ComponentCreator('/docs/tags/prompt-template/', 'ac4'),
            exact: true
          },
          {
            path: '/docs/tags/react/',
            component: ComponentCreator('/docs/tags/react/', '28c'),
            exact: true
          },
          {
            path: '/docs/tags/reasoning/',
            component: ComponentCreator('/docs/tags/reasoning/', 'd0e'),
            exact: true
          },
          {
            path: '/docs/tags/reflexion/',
            component: ComponentCreator('/docs/tags/reflexion/', '7bd'),
            exact: true
          },
          {
            path: '/docs/tags/schema/',
            component: ComponentCreator('/docs/tags/schema/', '8dc'),
            exact: true
          },
          {
            path: '/docs/tags/spring-ai/',
            component: ComponentCreator('/docs/tags/spring-ai/', '6f7'),
            exact: true
          },
          {
            path: '/docs/tags/structured-output/',
            component: ComponentCreator('/docs/tags/structured-output/', 'ccd'),
            exact: true
          },
          {
            path: '/docs/tags/testing/',
            component: ComponentCreator('/docs/tags/testing/', '092'),
            exact: true
          },
          {
            path: '/docs/tags/vision/',
            component: ComponentCreator('/docs/tags/vision/', 'd53'),
            exact: true
          },
          {
            path: '/docs/',
            component: ComponentCreator('/docs/', '290'),
            routes: [
              {
                path: '/docs/ai/',
                component: ComponentCreator('/docs/ai/', 'ad7'),
                exact: true,
                sidebar: "aiSidebar"
              },
              {
                path: '/docs/ai/agentops-security/',
                component: ComponentCreator('/docs/ai/agentops-security/', '10d'),
                exact: true,
                sidebar: "aiSidebar"
              },
              {
                path: '/docs/ai/agents/',
                component: ComponentCreator('/docs/ai/agents/', '37c'),
                exact: true,
                sidebar: "aiSidebar"
              },
              {
                path: '/docs/ai/agents/architecture/',
                component: ComponentCreator('/docs/ai/agents/architecture/', '9eb'),
                exact: true,
                sidebar: "aiSidebar"
              },
              {
                path: '/docs/ai/agents/design-patterns/',
                component: ComponentCreator('/docs/ai/agents/design-patterns/', 'd30'),
                exact: true,
                sidebar: "aiSidebar"
              },
              {
                path: '/docs/ai/agents/engineering/',
                component: ComponentCreator('/docs/ai/agents/engineering/', '75d'),
                exact: true,
                sidebar: "aiSidebar"
              },
              {
                path: '/docs/ai/agents/frameworks/',
                component: ComponentCreator('/docs/ai/agents/frameworks/', 'd1b'),
                exact: true,
                sidebar: "aiSidebar"
              },
              {
                path: '/docs/ai/agents/frontier/',
                component: ComponentCreator('/docs/ai/agents/frontier/', 'd3b'),
                exact: true,
                sidebar: "aiSidebar"
              },
              {
                path: '/docs/ai/agents/introduction/',
                component: ComponentCreator('/docs/ai/agents/introduction/', 'cff'),
                exact: true,
                sidebar: "aiSidebar"
              },
              {
                path: '/docs/ai/context-engineering/',
                component: ComponentCreator('/docs/ai/context-engineering/', '2a4'),
                exact: true,
                sidebar: "aiSidebar"
              },
              {
                path: '/docs/ai/internship/',
                component: ComponentCreator('/docs/ai/internship/', '7ea'),
                exact: true,
                sidebar: "aiSidebar"
              },
              {
                path: '/docs/ai/llm-fundamentals/',
                component: ComponentCreator('/docs/ai/llm-fundamentals/', 'c2a'),
                exact: true,
                sidebar: "aiSidebar"
              },
              {
                path: '/docs/ai/llm-fundamentals/embeddings/',
                component: ComponentCreator('/docs/ai/llm-fundamentals/embeddings/', '6e2'),
                exact: true,
                sidebar: "aiSidebar"
              },
              {
                path: '/docs/ai/llm-fundamentals/inference/',
                component: ComponentCreator('/docs/ai/llm-fundamentals/inference/', '879'),
                exact: true,
                sidebar: "aiSidebar"
              },
              {
                path: '/docs/ai/llm-fundamentals/introduction/',
                component: ComponentCreator('/docs/ai/llm-fundamentals/introduction/', '992'),
                exact: true,
                sidebar: "aiSidebar"
              },
              {
                path: '/docs/ai/llm-fundamentals/limitations/',
                component: ComponentCreator('/docs/ai/llm-fundamentals/limitations/', '458'),
                exact: true,
                sidebar: "aiSidebar"
              },
              {
                path: '/docs/ai/llm-fundamentals/tokenization/',
                component: ComponentCreator('/docs/ai/llm-fundamentals/tokenization/', '6d5'),
                exact: true,
                sidebar: "aiSidebar"
              },
              {
                path: '/docs/ai/llm-fundamentals/training-pipeline/',
                component: ComponentCreator('/docs/ai/llm-fundamentals/training-pipeline/', '109'),
                exact: true,
                sidebar: "aiSidebar"
              },
              {
                path: '/docs/ai/llm-fundamentals/transformer-architecture/',
                component: ComponentCreator('/docs/ai/llm-fundamentals/transformer-architecture/', 'a6b'),
                exact: true,
                sidebar: "aiSidebar"
              },
              {
                path: '/docs/ai/mcp/',
                component: ComponentCreator('/docs/ai/mcp/', '9d2'),
                exact: true,
                sidebar: "aiSidebar"
              },
              {
                path: '/docs/ai/mcp/interview-qa/',
                component: ComponentCreator('/docs/ai/mcp/interview-qa/', 'd0a'),
                exact: true,
                sidebar: "aiSidebar"
              },
              {
                path: '/docs/ai/prompt-engineering/',
                component: ComponentCreator('/docs/ai/prompt-engineering/', 'c64'),
                exact: true,
                sidebar: "aiSidebar"
              },
              {
                path: '/docs/ai/prompt-engineering/advanced-techniques/',
                component: ComponentCreator('/docs/ai/prompt-engineering/advanced-techniques/', 'f73'),
                exact: true,
                sidebar: "aiSidebar"
              },
              {
                path: '/docs/ai/prompt-engineering/agent-orchestration/',
                component: ComponentCreator('/docs/ai/prompt-engineering/agent-orchestration/', '8fe'),
                exact: true,
                sidebar: "aiSidebar"
              },
              {
                path: '/docs/ai/prompt-engineering/evaluation-versioning/',
                component: ComponentCreator('/docs/ai/prompt-engineering/evaluation-versioning/', 'e44'),
                exact: true,
                sidebar: "aiSidebar"
              },
              {
                path: '/docs/ai/prompt-engineering/introduction/',
                component: ComponentCreator('/docs/ai/prompt-engineering/introduction/', '65f'),
                exact: true,
                sidebar: "aiSidebar"
              },
              {
                path: '/docs/ai/prompt-engineering/multimodal/',
                component: ComponentCreator('/docs/ai/prompt-engineering/multimodal/', '5d3'),
                exact: true,
                sidebar: "aiSidebar"
              },
              {
                path: '/docs/ai/prompt-engineering/prompt-anatomy/',
                component: ComponentCreator('/docs/ai/prompt-engineering/prompt-anatomy/', '28a'),
                exact: true,
                sidebar: "aiSidebar"
              },
              {
                path: '/docs/ai/prompt-engineering/reasoning-patterns/',
                component: ComponentCreator('/docs/ai/prompt-engineering/reasoning-patterns/', '249'),
                exact: true,
                sidebar: "aiSidebar"
              },
              {
                path: '/docs/ai/prompt-engineering/spring-ai/',
                component: ComponentCreator('/docs/ai/prompt-engineering/spring-ai/', '33d'),
                exact: true,
                sidebar: "aiSidebar"
              },
              {
                path: '/docs/ai/prompt-engineering/structured-output/',
                component: ComponentCreator('/docs/ai/prompt-engineering/structured-output/', '13e'),
                exact: true,
                sidebar: "aiSidebar"
              },
              {
                path: '/docs/ai/rag/',
                component: ComponentCreator('/docs/ai/rag/', 'fe6'),
                exact: true,
                sidebar: "aiSidebar"
              },
              {
                path: '/docs/ai/rag/advanced-rag/',
                component: ComponentCreator('/docs/ai/rag/advanced-rag/', '015'),
                exact: true,
                sidebar: "aiSidebar"
              },
              {
                path: '/docs/ai/rag/best-practices/',
                component: ComponentCreator('/docs/ai/rag/best-practices/', '4a2'),
                exact: true,
                sidebar: "aiSidebar"
              },
              {
                path: '/docs/ai/rag/data-processing/',
                component: ComponentCreator('/docs/ai/rag/data-processing/', '2ab'),
                exact: true,
                sidebar: "aiSidebar"
              },
              {
                path: '/docs/ai/rag/evaluation/',
                component: ComponentCreator('/docs/ai/rag/evaluation/', 'cb8'),
                exact: true,
                sidebar: "aiSidebar"
              },
              {
                path: '/docs/ai/rag/generation/',
                component: ComponentCreator('/docs/ai/rag/generation/', '907'),
                exact: true,
                sidebar: "aiSidebar"
              },
              {
                path: '/docs/ai/rag/introduction/',
                component: ComponentCreator('/docs/ai/rag/introduction/', '7e7'),
                exact: true,
                sidebar: "aiSidebar"
              },
              {
                path: '/docs/ai/rag/production/',
                component: ComponentCreator('/docs/ai/rag/production/', '9e9'),
                exact: true,
                sidebar: "aiSidebar"
              },
              {
                path: '/docs/ai/rag/retrieval/',
                component: ComponentCreator('/docs/ai/rag/retrieval/', '580'),
                exact: true,
                sidebar: "aiSidebar"
              },
              {
                path: '/docs/ai/rag/vector-indexing/',
                component: ComponentCreator('/docs/ai/rag/vector-indexing/', '701'),
                exact: true,
                sidebar: "aiSidebar"
              },
              {
                path: '/docs/ai/spring-ai/',
                component: ComponentCreator('/docs/ai/spring-ai/', '220'),
                exact: true
              },
              {
                path: '/docs/cs/',
                component: ComponentCreator('/docs/cs/', '528'),
                exact: true,
                sidebar: "csSidebar"
              },
              {
                path: '/docs/cs/algorithms/',
                component: ComponentCreator('/docs/cs/algorithms/', '4ee'),
                exact: true,
                sidebar: "csSidebar"
              },
              {
                path: '/docs/cs/database/',
                component: ComponentCreator('/docs/cs/database/', 'd3b'),
                exact: true,
                sidebar: "csSidebar"
              },
              {
                path: '/docs/cs/network-os/',
                component: ComponentCreator('/docs/cs/network-os/', '836'),
                exact: true,
                sidebar: "csSidebar"
              },
              {
                path: '/docs/cs/system-design/',
                component: ComponentCreator('/docs/cs/system-design/', '08b'),
                exact: true,
                sidebar: "csSidebar"
              },
              {
                path: '/docs/engineering/',
                component: ComponentCreator('/docs/engineering/', 'ebc'),
                exact: true,
                sidebar: "engineeringSidebar"
              },
              {
                path: '/docs/engineering/backend/',
                component: ComponentCreator('/docs/engineering/backend/', '7e1'),
                exact: true,
                sidebar: "engineeringSidebar"
              },
              {
                path: '/docs/engineering/backend/concurrency/',
                component: ComponentCreator('/docs/engineering/backend/concurrency/', 'e31'),
                exact: true,
                sidebar: "engineeringSidebar"
              },
              {
                path: '/docs/engineering/devops/',
                component: ComponentCreator('/docs/engineering/devops/', 'ddd'),
                exact: true,
                sidebar: "engineeringSidebar"
              },
              {
                path: '/docs/engineering/frontend/',
                component: ComponentCreator('/docs/engineering/frontend/', '6a0'),
                exact: true,
                sidebar: "engineeringSidebar"
              },
              {
                path: '/docs/engineering/tools/',
                component: ComponentCreator('/docs/engineering/tools/', '6bd'),
                exact: true,
                sidebar: "engineeringSidebar"
              },
              {
                path: '/docs/projects/',
                component: ComponentCreator('/docs/projects/', '7a1'),
                exact: true,
                sidebar: "projectsSidebar"
              },
              {
                path: '/docs/projects/ecommerce-refactor/',
                component: ComponentCreator('/docs/projects/ecommerce-refactor/', '6b3'),
                exact: true,
                sidebar: "projectsSidebar"
              },
              {
                path: '/docs/projects/kb-rag-system/',
                component: ComponentCreator('/docs/projects/kb-rag-system/', '043'),
                exact: true,
                sidebar: "projectsSidebar"
              },
              {
                path: '/docs/projects/rag-knowledge-base/',
                component: ComponentCreator('/docs/projects/rag-knowledge-base/', 'dc1'),
                exact: true,
                sidebar: "projectsSidebar"
              }
            ]
          }
        ]
      }
    ]
  },
  {
    path: '/',
    component: ComponentCreator('/', 'e5f'),
    exact: true
  },
  {
    path: '*',
    component: ComponentCreator('*'),
  },
];
