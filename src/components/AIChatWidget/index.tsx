import React, { useState, useRef, useEffect, useCallback } from 'react';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import styles from './AIChatWidget.module.css';

interface Message {
    id: string;
    role: 'user' | 'assistant';
    content: string;
    isStreaming?: boolean;
    citations?: Citation[];
    agentType?: 'knowledge' | 'web_search' | 'hybrid' | 'hybrid_knowledge';
}

interface Citation {
    id: number;
    chunk_id: string;
    doc_id: string;
    title: string;
    path: string;
    heading_path: string[];
    score: number;
}

interface AskResponse {
    answer: string;
    citations: Citation[];
    has_sufficient_knowledge: boolean;
    model: string;
    tokens_used: number | null;
    retrieval_time_ms: number;
    generation_time_ms: number;
    agent_type?: 'knowledge' | 'web_search' | 'hybrid' | 'hybrid_knowledge';
}

export default function AIChatWidget(): JSX.Element {
    const { siteConfig } = useDocusaurusContext();
    // Use backend API for RAG Q&A
    const BACKEND_API_URL = (siteConfig.customFields?.backendUrl as string) || 'http://localhost:8000';

    const [isOpen, setIsOpen] = useState(false);
    const [messages, setMessages] = useState<Message[]>([]);
    const [inputValue, setInputValue] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const messagesEndRef = useRef<HTMLDivElement>(null);
    const inputRef = useRef<HTMLInputElement>(null);

    // Auto-scroll to bottom
    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    // Focus input when opened
    useEffect(() => {
        if (isOpen) {
            setTimeout(() => inputRef.current?.focus(), 100);
        }
    }, [isOpen]);

    const sendMessage = useCallback(async () => {
        if (!inputValue.trim() || isLoading) return;

        const userMessage: Message = {
            id: `user-${Date.now()}`,
            role: 'user',
            content: inputValue.trim(),
        };

        setMessages(prev => [...prev, userMessage]);
        setInputValue('');
        setIsLoading(true);

        // Create assistant message placeholder
        const assistantMessageId = `assistant-${Date.now()}`;
        setMessages(prev => [...prev, {
            id: assistantMessageId,
            role: 'assistant',
            content: '',
            isStreaming: true,
        }]);

        try {
            const response = await fetch(`${BACKEND_API_URL}/ask`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    question: userMessage.content,
                    top_k: 5,
                }),
            });

            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(`HTTP ${response.status}: ${errorText}`);
            }

            const data: AskResponse = await response.json();

            // Update assistant message with response
            setMessages(prev => prev.map(msg =>
                msg.id === assistantMessageId
                    ? {
                        ...msg,
                        content: data.answer,
                        isStreaming: false,
                        citations: data.citations,
                        agentType: data.agent_type,
                    }
                    : msg
            ));

        } catch (error) {
            console.error('Chat error:', error);
            setMessages(prev => prev.map(msg =>
                msg.id === assistantMessageId
                    ? {
                        ...msg,
                        content: `Sorry, I encountered an error: ${error instanceof Error ? error.message : 'Unknown error'}`,
                        isStreaming: false,
                    }
                    : msg
            ));
        } finally {
            setIsLoading(false);
        }
    }, [inputValue, isLoading, BACKEND_API_URL]);

    const handleKeyPress = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    };

    const clearChat = () => {
        setMessages([]);
    };

    return (
        <>
            {/* Floating Button */}
            <button
                className={styles.floatingButton}
                onClick={() => setIsOpen(!isOpen)}
                aria-label={isOpen ? 'Close chat' : 'Open AI chat'}
            >
                {isOpen ? (
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <path d="M18 6L6 18M6 6l12 12" />
                    </svg>
                ) : (
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z" />
                    </svg>
                )}
            </button>

            {/* Chat Window */}
            {isOpen && (
                <div className={styles.chatWindow}>
                    {/* Header */}
                    <div className={styles.header}>
                        <div className={styles.headerInfo}>
                            <span className={styles.headerIcon}>🤖</span>
                            <div>
                                <h3 className={styles.headerTitle}>AI Assistant</h3>
                                <span className={styles.headerSubtitle}>Powered by RAG Knowledge Base</span>
                            </div>
                        </div>
                        <button className={styles.clearButton} onClick={clearChat} title="Clear chat">
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                <path d="M3 6h18M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2" />
                            </svg>
                        </button>
                    </div>

                    {/* Messages */}
                    <div className={styles.messages}>
                        {messages.length === 0 && (
                            <div className={styles.welcomeMessage}>
                                <p>👋 Hi! I'm your AI documentation assistant.</p>
                                <p>I can help you find information from the knowledge base.</p>
                                <div className={styles.suggestions}>
                                    <button onClick={() => setInputValue('What is AgentOps and how does it work?')}>
                                        🤖 What is AgentOps?
                                    </button>
                                    <button onClick={() => setInputValue('Explain the agent loop architecture')}>
                                        🏗️ Agent loop architecture
                                    </button>
                                    <button onClick={() => setInputValue('What are the patterns of agent orchestration?')}>
                                        🔗 Agent orchestration patterns
                                    </button>
                                </div>
                            </div>
                        )}

                        {messages.map((message) => (
                            <div
                                key={message.id}
                                className={`${styles.message} ${styles[message.role]}`}
                            >
                                <div className={styles.messageContent}>
                                    {message.agentType && (
                                        <div className={styles.agentBadge}>
                                            {message.agentType === 'knowledge' && '📚 Knowledge Base'}
                                            {message.agentType === 'web_search' && '🌐 Web Search'}
                                            {message.agentType === 'hybrid' && '🔗 Hybrid (KB + Web)'}
                                            {message.agentType === 'hybrid_knowledge' && '📚 Knowledge Base'}
                                        </div>
                                    )}
                                    {message.content || (message.isStreaming && (
                                        <span className={styles.typingIndicator}>
                                            <span></span>
                                            <span></span>
                                            <span></span>
                                        </span>
                                    ))}
                                    {message.citations && message.citations.length > 0 && (
                                        <div className={styles.citations}>
                                            <p className={styles.citationsTitle}>📚 Sources:</p>
                                            <ul className={styles.citationsList}>
                                                {message.citations.map((citation) => (
                                                    <li key={citation.id}>
                                                        <a
                                                            href={citation.path}
                                                            target="_blank"
                                                            rel="noopener noreferrer"
                                                            className={styles.citationLink}
                                                        >
                                                            {citation.title}
                                                        </a>
                                                        <span className={styles.citationScore}>
                                                            ({(citation.score * 100).toFixed(0)}% match)
                                                        </span>
                                                    </li>
                                                ))}
                                            </ul>
                                        </div>
                                    )}
                                </div>
                            </div>
                        ))}
                        <div ref={messagesEndRef} />
                    </div>

                    {/* Input */}
                    <div className={styles.inputContainer}>
                        <input
                            ref={inputRef}
                            type="text"
                            value={inputValue}
                            onChange={(e) => setInputValue(e.target.value)}
                            onKeyPress={handleKeyPress}
                            placeholder="Ask about the docs..."
                            disabled={isLoading}
                            className={styles.input}
                        />
                        <button
                            onClick={sendMessage}
                            disabled={!inputValue.trim() || isLoading}
                            className={styles.sendButton}
                        >
                            {isLoading ? (
                                <span className={styles.loadingSpinner}></span>
                            ) : (
                                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                    <path d="M22 2L11 13M22 2l-7 20-4-9-9-4 20-7z" />
                                </svg>
                            )}
                        </button>
                    </div>
                </div>
            )}
        </>
    );
}
