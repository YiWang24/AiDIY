import Layout from "@theme/Layout";
import Heading from "@theme/Heading";
import Link from "@docusaurus/Link";
import { Analytics } from "@vercel/analytics/next"
import { JSX } from "react";

export default function Home(): JSX.Element {
  return (
    <Layout title="AI Engineering Knowledge Base" description="Building AI Agents in Public • Computer Science & Engineering Documentation">
      <Analytics />
      <main>
        {/* Hero Section - Builder Card */}
        <section className="builderCard">
          <div className="container">
            <div className="builderCard__wrapper">
              {/* Avatar Section */}
              <div className="builderCard__avatar">
                <div className="avatar__container">
                  <img
                    src="https://cdn-icons-png.freepik.com/512/763/763775.png"
                    alt="Yi Wang"
                    className="avatar__image"
                  />
                  <span className="avatar__status" title="Open to Work">🟢</span>
                </div>
              </div>

              {/* Content Section */}
              <div className="builderCard__content">
                <div className="builderCard__header">
                  <Heading as="h1" className="builderCard__name">
                    Yi Wang
                  </Heading>
                  <div className="builderCard__tags">
                    <span className="tag">🎓 CS Student @ York University</span>
                    <span className="tag">🇨🇦 Toronto</span>
                    <span className="tag">🤖 AI Agent Builder</span>
                  </div>
                </div>

                <div className="builderCard__bio">
                  <p>
                    👋 Hi, I'm Yi. I'm building this digital garden to document my engineering journey from CS fundamentals to production-grade AI Agents.
                    Passionate about self-hosting, local LLM deployment, and making AI engineering accessible.
                  </p>
                  <p className="builderCard__status">
                    <span className="status__indicator">🟢</span>
                    <span className="status__text">Building in Public • Open to Opportunities</span>
                  </p>
                </div>

                {/* Social Links */}
                <div className="builderCard__links">
                  <a
                    href="https://github.com/YiWang24"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="social__link social__link--github"
                  >
                    <svg width="20" height="20" viewBox="0 0 16 16" fill="currentColor">
                      <path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z" />
                    </svg>
                    GitHub
                  </a>
                  <a
                    href="mailto:yiwang2457@gmail.com"
                    className="social__link social__link--email"
                  >
                    <svg width="20" height="20" viewBox="0 0 16 16" fill="currentColor">
                      <path d="M.05 3.555A2 2 0 0 1 2 2h12a2 2 0 0 1 1.95 1.555L8 8.414.05 3.555zM0 4.697v7.104l5.803-3.558L0 4.697zM6.761 8.83l-6.57 4.027A2 2 0 0 0 2 14h12a2 2 0 0 0 1.808-1.144l-6.57-4.027L8 9.586l-1.239-.757zm3.436-.586L16 11.801V4.697l-5.803 3.546z" />
                    </svg>
                    Email
                  </a>
                  <a
                    href="https://www.linkedin.com/in/yiwang2025/"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="social__link social__link--linkedin"
                  >
                    <svg width="20" height="20" viewBox="0 0 16 16" fill="currentColor">
                      <path d="M0 1.146C0 .513.526 0 1.175 0h13.65C15.474 0 16 .513 16 1.146v13.708c0 .633-.526 1.146-1.175 1.146H1.175C.526 16 0 15.487 0 14.854V1.146zm4.943 12.248V6.169H2.542v7.225h2.401zm-1.2-8.212c.837 0 1.358-.554 1.358-1.248-.015-.709-.52-1.248-1.342-1.248-.822 0-1.359.54-1.359 1.248 0 .694.521 1.248 1.327 1.248h.016zm4.908 8.212V9.359c0-.216.016-.432.08-.586.173-.431.568-.878 1.232-.878.869 0 1.216.662 1.216 1.634v3.865h2.401V9.25c0-2.22-1.184-3.252-2.764-3.252-1.274 0-1.845.7-2.165 1.193v.025h-.016a5.54 5.54 0 0 1 .016-.025V6.169h-2.4c.03.678 0 7.225 0 7.225h2.4z" />
                    </svg>
                    LinkedIn
                  </a>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Knowledge Grid - Core Topics */}
        <section className="knowledgeGrid">
          <div className="container">
            <div className="section__header">
              <Heading as="h2" className="section__title">Knowledge Base</Heading>
              <p className="section__subtitle">Curated engineering notes from fundamentals to production</p>
            </div>

            <div className="knowledge__grid">
              <Link
                to="/category/cs-fundamentals"
                className="knowledge__card knowledge__card--primary"
                style={{ backgroundImage: 'url(https://images.unsplash.com/photo-1635070041078-e363dbe005cb?w=800&q=80)' }}
              >
                <div className="card__overlay"></div>
                <div className="card__content">
                  <h3 className="card__title">CS Fundamentals</h3>
                  <p className="card__description">Data structures, algorithms, complexity analysis, and core computer science concepts</p>
                  <div className="card__meta">
                    <span className="meta__badge">Algorithms</span>
                    <span className="meta__badge">DSA</span>
                  </div>
                </div>
              </Link>

              <Link
                to="/category/frontend-frameworks"
                className="knowledge__card knowledge__card--secondary"
                style={{ backgroundImage: 'url(https://images.unsplash.com/photo-1633356122544-f134324a6cee?w=800&q=80)' }}
              >
                <div className="card__overlay"></div>
                <div className="card__content">
                  <h3 className="card__title">Frontend Frameworks</h3>
                  <p className="card__description">React, Next.js, Vue, Angular - modern UI libraries and component architecture</p>
                  <div className="card__meta">
                    <span className="meta__badge">React</span>
                    <span className="meta__badge">UI/UX</span>
                  </div>
                </div>
              </Link>

              <Link
                to="/category/backend-frameworks"
                className="knowledge__card knowledge__card--accent"
                style={{ backgroundImage: 'url(https://images.unsplash.com/photo-1544197150-b99a580bb7a8?w=800&q=80)' }}
              >
                <div className="card__overlay"></div>
                <div className="card__content">
                  <h3 className="card__title">Backend Frameworks</h3>
                  <p className="card__description">Spring Boot, Node.js, Django, FastAPI - server-side development and APIs</p>
                  <div className="card__meta">
                    <span className="meta__badge">Spring</span>
                    <span className="meta__badge">APIs</span>
                  </div>
                </div>
              </Link>

              <Link
                to="/category/ai-engineering"
                className="knowledge__card knowledge__card--quaternary"
                style={{ backgroundImage: 'url(https://images.unsplash.com/photo-1677442136019-21780ecad995?w=800&q=80)' }}
              >
                <div className="card__overlay"></div>
                <div className="card__content">
                  <h3 className="card__title">AI Engineering</h3>
                  <p className="card__description">LLM integration, RAG systems, vector databases, AI agent development</p>
                  <div className="card__meta">
                    <span className="meta__badge">LLM</span>
                    <span className="meta__badge">RAG</span>
                  </div>
                </div>
              </Link>

              <Link
                to="/category/system-design"
                className="knowledge__card knowledge__card--quinary"
                style={{ backgroundImage: 'url(https://images.unsplash.com/photo-1558494949-ef010cbdcc31?w=800&q=80)' }}
              >
                <div className="card__overlay"></div>
                <div className="card__content">
                  <h3 className="card__title">System Design</h3>
                  <p className="card__description">Architecture patterns, scalability, distributed systems, and design trade-offs</p>
                  <div className="card__meta">
                    <span className="meta__badge">Architecture</span>
                    <span className="meta__badge">Scalability</span>
                  </div>
                </div>
              </Link>

              <Link
                to="/category/devops-cloud"
                className="knowledge__card knowledge__card--senary"
                style={{ backgroundImage: 'url(https://images.unsplash.com/photo-1667372393119-3d4c48d07fc9?w=800&q=80)' }}
              >
                <div className="card__overlay"></div>
                <div className="card__content">
                  <h3 className="card__title">DevOps & Cloud</h3>
                  <p className="card__description">CI/CD, containerization, Kubernetes, infrastructure as code, cloud platforms</p>
                  <div className="card__meta">
                    <span className="meta__badge">Docker</span>
                    <span className="meta__badge">K8s</span>
                  </div>
                </div>
              </Link>
            </div>
          </div>
        </section>

        {/* Tech Stack */}
        <section className="techStack">
          <div className="container">
            <Heading as="h2" className="section__title">Tech Stack</Heading>
            <p className="section__subtitle">Technologies powering this knowledge base and my projects</p>

            <div className="techStack__categories">
              {/* AI & Backend */}
              <div className="techStack__category">
                <h3 className="category__title">AI & Backend</h3>
                <div className="tech__list">
                  <span className="tech__item">Spring AI</span>
                  <span className="tech__item">LangChain</span>
                  <span className="tech__item">OpenAI</span>
                  <span className="tech__item">Vector DBs</span>
                  <span className="tech__item">FastAPI</span>
                  <span className="tech__item">PostgreSQL</span>
                </div>
              </div>

              {/* Frontend */}
              <div className="techStack__category">
                <h3 className="category__title">Frontend</h3>
                <div className="tech__list">
                  <span className="tech__item">React</span>
                  <span className="tech__item">Next.js</span>
                  <span className="tech__item">TypeScript</span>
                  <span className="tech__item">Tailwind CSS</span>
                  <span className="tech__item">Docusaurus</span>
                </div>
              </div>

              {/* DevOps & Tools */}
              <div className="techStack__category">
                <h3 className="category__title">DevOps & Tools</h3>
                <div className="tech__list">
                  <span className="tech__item">Docker</span>
                  <span className="tech__item">Kubernetes</span>
                  <span className="tech__item">GitHub Actions</span>
                  <span className="tech__item">Vercel</span>
                  <span className="tech__item">AWS</span>
                  <span className="tech__item">Terraform</span>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Quick Features Highlight */}
        <section className="features">
          <div className="container">
            <Heading as="h2" className="section__title">Interactive Features</Heading>
            <div className="features__grid">
              <div className="feature__card">
                <div className="feature__icon">⚡</div>
                <h3>Live Code Editor</h3>
                <p>Edit React code in-browser with instant preview</p>
              </div>
              <div className="feature__card">
                <div className="feature__icon">📊</div>
                <h3>Mermaid Diagrams</h3>
                <p>Interactive flowcharts and architecture diagrams</p>
              </div>
              <div className="feature__card">
                <div className="feature__icon">🤖</div>
                <h3>AI Chat Assistant</h3>
                <p>Ask questions about the documentation</p>
              </div>
              <div className="feature__card">
                <div className="feature__icon">🌙</div>
                <h3>Dark Mode</h3>
                <p>Eye-care optimized for long reading sessions</p>
              </div>
            </div>
          </div>
        </section>
      </main>
    </Layout>
  );
}
