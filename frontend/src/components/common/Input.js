import React from 'react';

const Input = ({ 
  label, 
  error, 
  type = 'text', 
  placeholder,
  value,
  onChange,
  required = false,
  className = '',
  ...props 
}) => {
  return (
    <div className="form-group">
      {label && (
        <label className="form-label">
          {label}
          {required && <span style={{ color: 'red' }}> *</span>}
        </label>
      )}
      <input
        type={type}
        className={`form-input ${className}`}
        placeholder={placeholder}
        value={value}
        onChange={onChange}
        required={required}
        {...props}
      />
      {error && <div className="form-error">{error}</div>}
    </div>
  );
};

export default Input;