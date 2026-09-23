import React, { useRef } from 'react';
import { Send } from 'lucide-react';

const ChatInput = ({
    value,
    onChange,
    onSend,
    disabled = false,
    placeholder = 'Ask about crops, soil, weather, disease, irrigation…',
}) => {
    const textareaRef = useRef(null);

    const handleKeyDown = (event) => {
        if (event.key === 'Enter' && !event.shiftKey) {
            event.preventDefault();
            if (!disabled && value.trim()) onSend();
        }
    };

    const handleInput = (event) => {
        onChange(event.target.value);
        const el = textareaRef.current;
        if (!el) return;
        el.style.height = 'auto';
        el.style.height = `${Math.min(el.scrollHeight, 140)}px`;
    };

    return (
        <form
            className="chat-input-bar"
            onSubmit={(event) => {
                event.preventDefault();
                if (!disabled && value.trim()) onSend();
            }}
        >
            <textarea
                ref={textareaRef}
                className="chat-input"
                rows={1}
                value={value}
                onChange={handleInput}
                onKeyDown={handleKeyDown}
                placeholder={placeholder}
                disabled={disabled}
                aria-label="Message AgriBrain AI Assistant"
            />
            <button
                type="submit"
                className="chat-send-btn"
                disabled={disabled || !value.trim()}
                aria-label="Send message"
            >
                <Send size={18} strokeWidth={2.2} />
            </button>
        </form>
    );
};

export default ChatInput;
