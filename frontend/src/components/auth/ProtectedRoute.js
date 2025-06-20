import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import LoadingSpinner from '../common/LoadingSpinner';

const ProtectedRoute = ({ children, requireManufacturer, requireSupplier }) => {
  const { isAuthenticated, isManufacturer, isSupplier, loading } = useAuth();
  const location = useLocation();

  if (loading) {
    return <LoadingSpinner message="Checking authentication..." />;
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  if (requireManufacturer && !isManufacturer) {
    return (
      <div className="container text-center mt-3">
        <h2>Access Denied</h2>
        <p>This page is only available to manufacturers.</p>
      </div>
    );
  }

  if (requireSupplier && !isSupplier) {
    return (
      <div className="container text-center mt-3">
        <h2>Access Denied</h2>
        <p>This page is only available to suppliers.</p>
      </div>
    );
  }

  return children;
};

export default ProtectedRoute;