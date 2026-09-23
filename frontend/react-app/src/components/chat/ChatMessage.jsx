import React from 'react';
import { Sparkles, User, Copy, Check } from 'lucide-react';
import { formatDateTime } from '../../utils/helpers';

// Helper to format basic markdown-style text into React elements cleanly
const renderFormattedText = (text) => {
    if (!text) return null;

    const lines = text.split('\n');
    const elements = [];
    let inList = false;
    let listItems = [];

    const flushList = (keyPrefix) => {
        if (inList && listItems.length > 0) {
            elements.push(
                <ul key={`${keyPrefix}-ul`} className="chat-msg-list">
                    {listItems.map((item, idx) => (
                        <li key={idx}>{parseInlineFormatting(item)}</li>
                    ))}
                </ul>
            );
            listItems = [];
            inList = false;
        }
    };

    lines.forEach((line, index) => {
        const trimmed = line.trim();

        // Header detection (#, ##, ###)
        if (trimmed.startsWith('### ')) {
            flushList(index);
            elements.push(
                <h4 key={index} className="chat-msg-heading h4">
                    {parseInlineFormatting(trimmed.substring(4))}
                </h4>
            );
        } else if (trimmed.startsWith('## ')) {
            flushList(index);
            elements.push(
                <h3 key={index} className="chat-msg-heading h3">
                    {parseInlineFormatting(trimmed.substring(3))}
                </h3>
            );
        } else if (trimmed.startsWith('# ')) {
            flushList(index);
            elements.push(
                <h2 key={index} className="chat-msg-heading h2">
                    {parseInlineFormatting(trimmed.substring(2))}
                </h2>
            );
        }
        // Bullet list item (*, -, •, 1.)
        else if (/^[-*•]\s+/.test(trimmed) || /^\d+\.\s+/.test(trimmed)) {
            inList = true;
            const content = trimmed.replace(/^([-*•]|\d+\.)\s+/, '');
            listItems.push(content);
        }
        // Blank line
        else if (trimmed === '') {
            flushList(index);
        }
        // Standard paragraph
        else {
            flushList(index);
            elements.push(
                <p key={index} className="chat-msg-p">
                    {parseInlineFormatting(trimmed)}
                </p>
            );
        }
    });

    flushList('final');

    return elements;
};

// Parse bold **text**, code `text`, and highlight key words
const parseInlineFormatting = (text) => {
    const parts = text.split(/(\*\*.*?\*\*|`.*?`)/g);
    return parts.map((part, index) => {
        if (part.startsWith('**') && part.endsWith('**')) {
            return <strong key={index}>{part.slice(2, -2)}</strong>;
        }
        if (part.startsWith('`') && part.endsWith('`')) {
            return <code key={index} className="chat-msg-code">{part.slice(1, -1)}</code>;
        }
        return part;
    });
};

const ChatMessage = ({ message }) => {
    const [copied, setCopied] = React.useState(false);
    const isAssistant = message.role === 'assistant';

    const handleCopy = () => {
        navigator.clipboard.writeText(message.content);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
    };

    return (
        <div className={`chat-row ${isAssistant ? 'assistant' : 'user'}`}>
            <div className={`chat-avatar ${isAssistant ? 'assistant' : 'user'}`}>
                {isAssistant ? <Sparkles size={16} /> : <User size={16} />}
            </div>

            <div className={`chat-bubble ${isAssistant ? 'assistant' : 'user'}`}>
                <div className="chat-bubble-header">
                    <span className="chat-author-name">
                        {isAssistant ? 'AgriBrain AI' : 'You'}
                    </span>
                    {isAssistant && (
                        <span className="chat-ai-badge" title="Powered by AgriBrain Decision Engine">
                            <Sparkles size={11} /> AI Generated
                        </span>
                    )}
                    {message.timestamp && (
                        <span className="chat-timestamp">{formatDateTime(message.timestamp)}</span>
                    )}
                </div>

                <div className="chat-bubble-body">
                    {isAssistant ? (
                        renderFormattedText(message.content)
                    ) : (
                        <p className="chat-msg-p">{message.content}</p>
                    )}
                </div>

                {isAssistant && (
                    <div className="chat-bubble-footer">
                        <button
                            type="button"
                            className="chat-action-btn"
                            onClick={handleCopy}
                            title="Copy response"
                        >
                            {copied ? (
                                <>
                                    <Check size={13} style={{ color: 'var(--forest-500)' }} /> Copied
                                </>
                            ) : (
                                <>
                                    <Copy size={13} /> Copy
                                </>
                            )}
                        </button>
                    </div>
                )}
            </div>
        </div>
    );
};

export default ChatMessage;
