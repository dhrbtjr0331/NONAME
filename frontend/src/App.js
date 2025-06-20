import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './hooks/useAuth';
import Header from './components/shared/Header';
import ProtectedRoute from './components/auth/ProtectedRoute';

// Auth Components
import Login from './components/auth/Login';
import Register from './components/auth/Register';

// Shared Components
import Profile from './components/shared/Profile';
import Dashboard from './components/shared/Dashboard';

// Manufacturer Components
import CreateRFQ from './components/manufacturer/CreateRFQ';
import RFQList from './components/manufacturer/RFQList';
import RFQDetails from './components/manufacturer/RFQDetails';
import QuoteComparison from './components/manufacturer/QuoteComparison';

// Supplier Components
import RFQBrowse from './components/supplier/RFQBrowse';
import CreateQuote from './components/supplier/CreateQuote';
import QuoteList from './components/supplier/QuoteList';
import QuoteDetails from './components/supplier/QuoteDetails';

// Styles
import './styles/globals.css';
import './App.css';

const App = () => {
  return (
    <AuthProvider>
      <Router>
        <div className="App">
          <Header />
          <main className="main-content">
            <Routes>
              {/* Public Routes */}
              <Route path="/" element={<HomePage />} />
              <Route path="/login" element={<Login />} />
              <Route path="/register" element={<Register />} />

              {/* Protected Routes - All Users */}
              <Route 
                path="/dashboard" 
                element={
                  <ProtectedRoute>
                    <Dashboard />
                  </ProtectedRoute>
                } 
              />
              <Route 
                path="/profile" 
                element={
                  <ProtectedRoute>
                    <Profile />
                  </ProtectedRoute>
                } 
              />

              {/* Manufacturer Routes */}
              <Route 
                path="/rfqs/create" 
                element={
                  <ProtectedRoute requireManufacturer>
                    <CreateRFQ />
                  </ProtectedRoute>
                } 
              />
              <Route 
                path="/rfqs" 
                element={
                  <ProtectedRoute requireManufacturer>
                    <RFQList />
                  </ProtectedRoute>
                } 
              />
              <Route 
                path="/rfqs/:id" 
                element={
                  <ProtectedRoute>
                    <RFQDetails />
                  </ProtectedRoute>
                } 
              />
              <Route 
                path="/rfqs/:rfqId/quotes" 
                element={
                  <ProtectedRoute requireManufacturer>
                    <QuoteComparison />
                  </ProtectedRoute>
                } 
              />

              {/* Supplier Routes */}
              <Route 
                path="/browse-rfqs" 
                element={
                  <ProtectedRoute requireSupplier>
                    <RFQBrowse />
                  </ProtectedRoute>
                } 
              />
              <Route 
                path="/quotes/create" 
                element={
                  <ProtectedRoute requireSupplier>
                    <CreateQuote />
                  </ProtectedRoute>
                } 
              />
              <Route 
                path="/my-quotes" 
                element={
                  <ProtectedRoute requireSupplier>
                    <QuoteList />
                  </ProtectedRoute>
                } 
              />
              <Route 
                path="/quotes/:id" 
                element={
                  <ProtectedRoute requireSupplier>
                    <QuoteDetails />
                  </ProtectedRoute>
                } 
              />

              {/* Catch all - redirect to dashboard if authenticated, login if not */}
              <Route path="*" element={<NotFound />} />
            </Routes>
          </main>
        </div>
      </Router>
    </AuthProvider>
  );
};

// Home Page Component
const HomePage = () => {
  return (
    <div className="container">
      <div style={{ textAlign: 'center', padding: '80px 20px' }}>
        <h1 style={{ fontSize: '3rem', marginBottom: '20px', color: '#007bff' }}>
          Marketplace Platform
        </h1>
        <p style={{ fontSize: '1.2rem', color: '#666', marginBottom: '40px', maxWidth: '600px', margin: '0 auto 40px' }}>
          Connect manufacturers with suppliers through our AI-powered bidding system. 
          Get competitive quotes and find the best partners for your business needs.
        </p>
        
        <div style={{ display: 'flex', gap: '20px', justifyContent: 'center', marginBottom: '60px' }}>
          <a href="/register" className="btn btn-primary" style={{ fontSize: '1.1rem', padding: '15px 30px' }}>
            Get Started
          </a>
          <a href="/login" className="btn btn-outline" style={{ fontSize: '1.1rem', padding: '15px 30px' }}>
            Login
          </a>
        </div>

        <div className="grid grid-2" style={{ maxWidth: '800px', margin: '0 auto', textAlign: 'left' }}>
          <div className="card">
            <h3 style={{ color: '#007bff', marginBottom: '15px' }}>For Manufacturers</h3>
            <ul style={{ lineHeight: '1.8' }}>
              <li>Post detailed RFQs with technical specifications</li>
              <li>Receive competitive quotes from verified suppliers</li>
              <li>Compare proposals and choose the best fit</li>
              <li>Streamline your procurement process</li>
            </ul>
          </div>
          
          <div className="card">
            <h3 style={{ color: '#28a745', marginBottom: '15px' }}>For Suppliers</h3>
            <ul style={{ lineHeight: '1.8' }}>
              <li>Browse available RFQs in your industry</li>
              <li>Submit detailed quotes with AI assistance</li>
              <li>Showcase your capabilities and certifications</li>
              <li>Grow your business with new opportunities</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

// Not Found Component
const NotFound = () => {
  return (
    <div className="container text-center" style={{ marginTop: '100px' }}>
      <h1>404 - Page Not Found</h1>
      <p>The page you're looking for doesn't exist.</p>
      <a href="/dashboard" className="btn btn-primary">
        Go to Dashboard
      </a>
    </div>
  );
};

export default App;