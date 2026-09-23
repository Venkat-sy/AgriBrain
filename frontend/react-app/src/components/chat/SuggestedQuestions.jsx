import React from 'react';

export const SUGGESTED_QUESTIONS = [
    'Why are my crops turning yellow?',
    'Should I irrigate today?',
    'How can I improve my soil health?',
    'What could cause low yield?',
    'How do I identify crop disease?',
    'Explain my farm analytics',
];

const SuggestedQuestions = ({ questions = SUGGESTED_QUESTIONS, onSelect, disabled = false }) => (
    <div className="suggested-questions">
        {questions.map((question) => (
            <button
                key={question}
                type="button"
                className="suggested-chip"
                onClick={() => onSelect(question)}
                disabled={disabled}
            >
                {question}
            </button>
        ))}
    </div>
);

export default SuggestedQuestions;
