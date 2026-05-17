import React from 'react';
import BrowserOnly from '@docusaurus/BrowserOnly';
import { Analytics } from '@vercel/analytics/react';

// Root component to wrap all pages with global components.
// AIChatWidget depends on shadcn/AI-Elements code that touches browser-only
// APIs at module load — wrap it in BrowserOnly so SSR doesn't try to render it.
export default function Root({ children }) {
    return (
        <>
            {children}
            <BrowserOnly>
                {() => {
                    const AIChatWidget = require('@site/src/components/AIChatWidget').default;
                    return <AIChatWidget />;
                }}
            </BrowserOnly>
            <Analytics />
        </>
    );
}
