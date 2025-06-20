import React from 'react';

const Card = ({ title, children, className = '', headerAction }) => {
  return (
    <div className={`card ${className}`}>
      {title && (
        <div className="card-header">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <h3>{title}</h3>
            {headerAction}
          </div>
        </div>
      )}
      {children}
    </div>
  );
};

export default Card;