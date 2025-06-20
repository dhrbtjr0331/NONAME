import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import Button from '../common/Button';
import Input from '../common/Input';
import Card from '../common/Card';

const Register = () => {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    confirmPassword: '',
    accountType: 'supplier'
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const { register } = useAuth();
  const navigate = useNavigate();

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match');
      setLoading(false);
      return;
    }

    const isManufacturer = formData.accountType === 'manufacturer';
    const result = await register(formData.email, formData.password, isManufacturer);
    
    if (result.success) {
      navigate('/login', { 
        state: { message: 'Registration successful! Please login.' }
      });
    } else {
      setError(result.error);
    }
    
    setLoading(false);
  };

  return (
    <div className="container" style={{ maxWidth: '400px', marginTop: '80px' }}>
      <Card title="Create Account">
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="form-label">Account Type *</label>
            <div style={{ display: 'flex', gap: '20px', marginBottom: '10px' }}>
              <label style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
                <input
                  type="radio"
                  name="accountType"
                  value="supplier"
                  checked={formData.accountType === 'supplier'}
                  onChange={handleChange}
                />
                Supplier
              </label>
              <label style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
                <input
                  type="radio"
                  name="accountType"
                  value="manufacturer"
                  checked={formData.accountType === 'manufacturer'}
                  onChange={handleChange}
                />
                Manufacturer
              </label>
            </div>
            <small style={{ color: '#666' }}>
              {formData.accountType === 'supplier' ? 
                'I provide products/services to manufacturers' : 
                'I need to source products/services from suppliers'
              }
            </small>
          </div>

          <Input
            label="Email"
            type="email"
            name="email"
            value={formData.email}
            onChange={handleChange}
            required
            placeholder="Enter your email"
          />
          
          <Input
            label="Password"
            type="password"
            name="password"
            value={formData.password}
            onChange={handleChange}
            required
            placeholder="Enter your password"
          />

          <Input
            label="Confirm Password"
            type="password"
            name="confirmPassword"
            value={formData.confirmPassword}
            onChange={handleChange}
            required
            placeholder="Confirm your password"
          />

          {error && (
            <div className="form-error mb-2">{error}</div>
          )}

          <Button
            type="submit"
            loading={loading}
            style={{ width: '100%' }}
          >
            Create Account
          </Button>
        </form>

        <div className="text-center mt-3">
          <p>
            Already have an account?{' '}
            <Link to="/login" style={{ color: '#007bff' }}>
              Login here
            </Link>
          </p>
        </div>
      </Card>
    </div>
  );
};

export default Register;