import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import Button from '../common/Button';

const Header = () => {
  const { isAuthenticated, user, logout, isManufacturer } = useAuth();

  const handleLogout = () => {
    logout();
  };

  return (
    <header style={{
      backgroundColor: 'white',
      borderBottom: '1px solid #eee',
      padding: '15px 0',
      position: 'sticky',
      top: 0,
      zIndex: 100
    }}>
      <div className="container">
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center'
        }}>
          <Link 
            to={isAuthenticated ? '/dashboard' : '/'} 
            style={{ 
              fontSize: '24px', 
              fontWeight: 'bold', 
              color: '#007bff',
              textDecoration: 'none'
            }}
          >
            Marketplace
          </Link>

          <nav style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
            {isAuthenticated ? (
              <>
                <Link to="/dashboard" style={{ textDecoration: 'none', color: '#333' }}>
                  Dashboard
                </Link>
                
                {isManufacturer ? (
                  <>
                    <Link to="/rfqs" style={{ textDecoration: 'none', color: '#333' }}>
                      My RFQs
                    </Link>
                    <Link to="/rfqs/create" style={{ textDecoration: 'none', color: '#333' }}>
                      Create RFQ
                    </Link>
                  </>
                ) : (
                  <>
                    <Link to="/browse-rfqs" style={{ textDecoration: 'none', color: '#333' }}>
                      Browse RFQs
                    </Link>
                    <Link to="/my-quotes" style={{ textDecoration: 'none', color: '#333' }}>
                      My Quotes
                    </Link>
                  </>
                )}
                
                <Link to="/profile" style={{ textDecoration: 'none', color: '#333' }}>
                  Profile
                </Link>
                
                <span style={{ color: '#666' }}>
                  {user?.email} ({isManufacturer ? 'Manufacturer' : 'Supplier'})
                </span>
                
                <Button variant="outline" onClick={handleLogout}>
                  Logout
                </Button>
              </>
            ) : (
              <>
                <Link to="/login">
                  <Button variant="outline">Login</Button>
                </Link>
                <Link to="/register">
                  <Button>Register</Button>
                </Link>
              </>
            )}
          </nav>
        </div>
      </div>
    </header>
  );
};

export default Header;