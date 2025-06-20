import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { rfqService } from '../../services/rfq';
import Card from '../common/Card';
import Button from '../common/Button';
import LoadingSpinner from '../common/LoadingSpinner';
import { format } from 'date-fns';

const RFQList = () => {
  const [rfqs, setRfqs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');

  useEffect(() => {
    loadRFQs();
  }, [filter]);

  const loadRFQs = async () => {
    try {
      setLoading(true);
      const params = filter !== 'all' ? { status: filter } : {};
      const data = await rfqService.getMyRFQs(params);
      setRfqs(data);
    } catch (error) {
      console.error('Error loading RFQs:', error);
      alert('Error loading RFQs. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = (status) => {
    const statusClasses = {
      'OPEN': 'status-open',
      'CLOSED': 'status-closed', 
      'AWARDED': 'status-accepted',
      'CANCELLED': 'status-closed'
    };
    
    return (
      <span className={`status-badge ${statusClasses[status] || 'status-pending'}`}>
        {status}
      </span>
    );
  };

  const getPriorityBadge = (priority) => {
    const priorityColors = {
      'LOW': '#6c757d',
      'MEDIUM': '#ffc107', 
      'HIGH': '#fd7e14',
      'URGENT': '#dc3545'
    };
    
    return (
      <span 
        className="status-badge"
        style={{ 
          backgroundColor: priorityColors[priority],
          color: 'white'
        }}
      >
        {priority}
      </span>
    );
  };

  if (loading) {
    return <LoadingSpinner message="Loading your RFQs..." />;
  }

  return (
    <div className="container">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <h1>My RFQs</h1>
        <Link to="/rfqs/create">
          <Button>Create New RFQ</Button>
        </Link>
      </div>

      {/* Filter Tabs */}
      <div style={{ 
        borderBottom: '1px solid #ddd', 
        marginBottom: '20px',
        display: 'flex',
        gap: '20px'
      }}>
        {['all', 'OPEN', 'CLOSED', 'AWARDED'].map(status => (
          <button
            key={status}
            onClick={() => setFilter(status)}
            style={{
              padding: '10px 0',
              border: 'none',
              background: 'none',
              borderBottom: filter === status ? '2px solid #007bff' : 'none',
              color: filter === status ? '#007bff' : '#666',
              cursor: 'pointer',
              textTransform: 'capitalize'
            }}
          >
            {status === 'all' ? 'All RFQs' : status}
          </button>
        ))}
      </div>

      {rfqs.length === 0 ? (
        <Card>
          <div className="text-center">
            <h3>No RFQs found</h3>
            <p>You haven't created any RFQs yet.</p>
            <Link to="/rfqs/create">
              <Button>Create Your First RFQ</Button>
            </Link>
          </div>
        </Card>
      ) : (
        <div className="grid grid-2">
          {rfqs.map(rfq => (
            <Card key={rfq.id}>
              <div style={{ marginBottom: '15px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '10px' }}>
                  <h3 style={{ margin: 0, flex: 1 }}>
                    <Link 
                      to={`/rfqs/${rfq.id}`}
                      style={{ color: '#007bff', textDecoration: 'none' }}
                    >
                      {rfq.title}
                    </Link>
                  </h3>
                  <div style={{ display: 'flex', gap: '5px', flexDirection: 'column', alignItems: 'flex-end' }}>
                    {getStatusBadge(rfq.status)}
                    {getPriorityBadge(rfq.priority)}
                  </div>
                </div>
                
                <p style={{ color: '#666', fontSize: '14px', margin: '5px 0' }}>
                  <strong>Category:</strong> {rfq.product_category}
                </p>
                
                <p style={{ color: '#666', fontSize: '14px', margin: '5px 0' }}>
                  <strong>Quantity:</strong> {rfq.quantity.toLocaleString()} {rfq.unit}
                </p>
                
                <p style={{ color: '#666', fontSize: '14px', margin: '5px 0' }}>
                  <strong>Quote Deadline:</strong> {format(new Date(rfq.quote_deadline), 'MMM dd, yyyy HH:mm')}
                </p>
                
                <p style={{ color: '#666', fontSize: '14px', margin: '5px 0' }}>
                  <strong>Created:</strong> {format(new Date(rfq.created_at), 'MMM dd, yyyy')}
                </p>
              </div>
              
              <div style={{ display: 'flex', gap: '10px' }}>
                <Link to={`/rfqs/${rfq.id}`} style={{ flex: 1 }}>
                  <Button variant="outline" style={{ width: '100%' }}>
                    View Details
                  </Button>
                </Link>
                
                {rfq.status === 'OPEN' && (
                  <Link to={`/rfqs/${rfq.id}/quotes`} style={{ flex: 1 }}>
                    <Button style={{ width: '100%' }}>
                      View Quotes
                    </Button>
                  </Link>
                )}
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
};

export default RFQList;