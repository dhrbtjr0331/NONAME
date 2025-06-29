import React, { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { rfqService } from '../../services/rfq';
import Card from '../common/Card';
import Button from '../common/Button';
import LoadingSpinner from '../common/LoadingSpinner';
import { format } from 'date-fns';
import { useAuth } from '../../hooks/useAuth';

const RFQDetails = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [rfq, setRfq] = useState(null);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);

  useEffect(() => {
    loadRFQ();
  }, [id]);

  const loadRFQ = async () => {
    try {
      setLoading(true);
      const data = await rfqService.getRFQById(id);
      setRfq(data);
    } catch (error) {
      console.error('Error loading RFQ:', error);
      alert('Error loading RFQ details.');
      navigate('/rfqs');
    } finally {
      setLoading(false);
    }
  };

  const handleCloseRFQ = async () => {
    if (!window.confirm('Are you sure you want to close this RFQ? This action cannot be undone.')) {
      return;
    }

    try {
      setActionLoading(true);
      await rfqService.closeRFQ(id);
      await loadRFQ(); // Refresh data
      alert('RFQ closed successfully.');
    } catch (error) {
      console.error('Error closing RFQ:', error);
      alert('Error closing RFQ. Please try again.');
    } finally {
      setActionLoading(false);
    }
  };

  if (loading) {
    return <LoadingSpinner message="Loading RFQ details..." />;
  }

  if (!rfq) {
    return (
      <div className="container text-center">
        <h2>RFQ Not Found</h2>
        <Link to="/rfqs">
          <Button>Back to RFQs</Button>
        </Link>
      </div>
    );
  }

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

  return (
    <div className="container">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <h1>{rfq.title}</h1>
        <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
          {getStatusBadge(rfq.status)}
          <Link to="/rfqs">
            <Button variant="outline">Back to RFQs</Button>
          </Link>
        </div>
      </div>

      <div className="grid grid-2">
        {/* Basic Information */}
        <Card title="Basic Information">
          <div style={{ marginBottom: '15px' }}>
            <strong>Category:</strong> {rfq.product_category}
          </div>
          <div style={{ marginBottom: '15px' }}>
            <strong>Quantity:</strong> {rfq.quantity.toLocaleString()} {rfq.unit}
          </div>
          <div style={{ marginBottom: '15px' }}>
            <strong>Priority:</strong> 
            <span 
              className="status-badge"
              style={{ 
                marginLeft: '10px',
                backgroundColor: rfq.priority === 'URGENT' ? '#dc3545' : '#ffc107',
                color: 'white'
              }}
            >
              {rfq.priority}
            </span>
          </div>
          {rfq.target_price_min && rfq.target_price_max && (
            <div style={{ marginBottom: '15px' }}>
              <strong>Target Price Range:</strong> {rfq.currency} {rfq.target_price_min} - {rfq.target_price_max} per {rfq.unit}
            </div>
          )}
          <div style={{ marginBottom: '15px' }}>
            <strong>Max Suppliers:</strong> {rfq.max_suppliers}
          </div>
          <div style={{ marginBottom: '15px' }}>
            <strong>Created:</strong> {format(new Date(rfq.created_at), 'MMM dd, yyyy HH:mm')}
          </div>
        </Card>

        {/* Timeline */}
        <Card title="Timeline">
          <div style={{ marginBottom: '15px' }}>
            <strong>Quote Deadline:</strong><br />
            {format(new Date(rfq.quote_deadline), 'MMMM dd, yyyy HH:mm')}
          </div>
          {rfq.delivery_deadline && (
            <div style={{ marginBottom: '15px' }}>
              <strong>Delivery Deadline:</strong><br />
              {format(new Date(rfq.delivery_deadline), 'MMMM dd, yyyy HH:mm')}
            </div>
          )}
          {rfq.closed_at && (
            <div style={{ marginBottom: '15px' }}>
              <strong>Closed:</strong><br />
              {format(new Date(rfq.closed_at), 'MMMM dd, yyyy HH:mm')}
            </div>
          )}
        </Card>
      </div>

      {/* Description */}
      <Card title="Description">
        <p style={{ whiteSpace: 'pre-wrap', lineHeight: '1.6' }}>
          {rfq.description}
        </p>
      </Card>

      {/* Technical Details */}
      {(rfq.technical_specs || rfq.quality_requirements || rfq.certifications_required) && (
        <Card title="Technical Requirements">
          {rfq.technical_specs && (
            <div style={{ marginBottom: '20px' }}>
              <h4>Technical Specifications</h4>
              <p style={{ whiteSpace: 'pre-wrap', lineHeight: '1.6' }}>
                {rfq.technical_specs}
              </p>
            </div>
          )}
          
          {rfq.quality_requirements && (
            <div style={{ marginBottom: '20px' }}>
              <h4>Quality Requirements</h4>
              <p style={{ whiteSpace: 'pre-wrap', lineHeight: '1.6' }}>
                {rfq.quality_requirements}
              </p>
            </div>
          )}
          
          {rfq.certifications_required && (
            <div>
              <h4>Required Certifications</h4>
              <p>{rfq.certifications_required}</p>
            </div>
          )}
        </Card>
      )}

      {/* Logistics */}
      {(rfq.delivery_location || rfq.shipping_terms) && (
        <Card title="Logistics">
          {rfq.delivery_location && (
            <div style={{ marginBottom: '15px' }}>
              <strong>Delivery Location:</strong> {rfq.delivery_location}
            </div>
          )}
          {rfq.shipping_terms && (
            <div>
              <strong>Shipping Terms:</strong> {rfq.shipping_terms}
            </div>
          )}
        </Card>
      )}

      {/* Actions */}
      <Card>
        <div style={{ display: 'flex', gap: '10px', justifyContent: 'flex-end' }}>
          {rfq.status === 'OPEN' && (
            <>
              <Link to={`/rfqs/${rfq.id}/quotes`}>
                <Button>View Quotes</Button>
              </Link>
              <Link to={`/rfqs/${rfq.id}/edit`}>
                <Button variant="outline">Edit RFQ</Button>
              </Link>
              <Button 
                variant="danger" 
                onClick={handleCloseRFQ}
                loading={actionLoading}
              >
                Close RFQ
              </Button>
            </>
          )}
          
          {rfq.status === 'AWARDED' && (
            <Link to={`/rfqs/${rfq.id}/quotes`}>
              <Button>View Winning Quote</Button>
            </Link>
          )}
        </div>
      </Card>
    </div>
  );
};

export default RFQDetails;