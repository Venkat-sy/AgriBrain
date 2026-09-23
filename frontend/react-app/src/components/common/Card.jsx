import React from 'react';
import './Card.css';

const Card = ({ children, className = '', onClick, hover = false, padding = true }) => {
    return (
        <div 
            className={`card ${hover ? 'card-hover' : ''} ${!padding ? 'no-padding' : ''} ${className}`}
            onClick={onClick}
            style={{ cursor: onClick ? 'pointer' : 'default' }}
        >
            {children}
        </div>
    );
};

export default Card;
