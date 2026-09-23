import React from 'react';

const TypingIndicator = () => (
    <div className="chat-row assistant">
        <div className="chat-avatar assistant" aria-hidden="true">AI</div>
        <div className="chat-bubble assistant typing" role="status" aria-live="polite">
            <span className="typing-dot" />
            <span className="typing-dot" />
            <span className="typing-dot" />
            <span className="typing-label">AgriBrain is thinking…</span>
        </div>
    </div>
);

export default TypingIndicator;
