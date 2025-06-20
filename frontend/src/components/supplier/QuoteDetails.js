import React, { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { quoteService } from '../../services/quote';
import Card from '../common/Card';
import Button from '../common/Button';
import LoadingSpinner from '../common/LoadingSpinner';
import { format } from 'date-fns';

const QuoteDetails = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [quote, setQuote] = useState(null);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);

  useEffect(() => {
    loadQuote();
  }, [id]);

  const loadQuote = async () => {
    try {
      setLoading(true);
      const data = await quoteService.getQuoteById(id);
      setQuote(data);
    } catch (error) {
      console.error('Error loading quote:', error);
      alert('Error loading quote details.');
      navigate('/my-quotes');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmitQuote = async () => {
    if (!window.confirm('Are you sure you want to submit this quote? You won\'t be able to modify it after submission.')) {
      return;
    }

    try {
      setActionLoading(true);
      await quoteService.submitQuote(id);
      await loadQuote(); // Refresh data
      alert('Quote submitted successfully!');
    } catch (error) {
      console.error('Error submitting quote:', error);
      alert('Error submitting quote. Please try again.');
    } finally {
      setActionLoading(false);
    }
  };

  const handleWithdrawQuote = async () => {
    if (!window.confirm('Are you sure you want to withdraw this quote?')) {
      return;
    }

    try {
      setActionLoading(true);
      await quoteService.withdrawQuote(id);
      await loadQuote(); // Refresh data
      alert('Quote withdrawn successfully.');
    } catch (error) {
      console.error('Error withdrawing quote:', error);
      alert('Error withdrawing quote. Please try again.');
    } finally {
      setActionLoading(false);
    }
  };

  if (loading) {
    return <LoadingSpinner message="Loading quote details..." />;
  }

  if (!quote) {
    return (
      <div className="container text-center">
        <h2>Quote Not Found</h2>
        <Link to="/my-quotes">
          <Button>Back to My Quotes</Button>
        </Link>
      </div>
    );
  }

  const getStatusBadge = (status) => {
    const statusClasses = {
      'DRAFT': 'status-pending',
      'SUBMITTED': 'status-open',
      'UNDER_REVIEW': 'status-pending',
      'ACCEPTED': 'status-accepted',
      'REJECTED': 'status-closed',
      'WITHDRAWN': 'status-closed'
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
        <h1>Quote #{quote.id}</h1>
        <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
          {getStatusBadge(quote.status)}
          <Link to="/my-quotes">
            <Button variant="outline">Back to My Quotes</Button>
          </Link>
        </div>
      </div>

      {quote.status === 'ACCEPTED' && (
        <Card>
          <div style={{ 
            padding: '15px', 
            backgroundColor: '#d4edda', 
            color: '#155724',
            borderRadius: '4px',
            textAlign: 'center',
            fontWeight: 'bold',
            fontSize: '18px'
          }}>
            🎉 Congratulations! Your quote has been accepted!
          </div>
        </Card>
      )}

      <div className="grid grid-2">
        {/* Quote Summary */}
        <Card title="Quote Summary">
          <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#007bff', marginBottom: '15px' }}>
            {quote.currency} {quote.total_price.toLocaleString()}
          </div>
          
          <div style={{ marginBottom: '10px' }}>
            <strong>Unit Price:</strong> {quote.currency} {quote.unit_price}
          </div>
          
          <div style={{ marginBottom: '10px' }}>
            <strong>Lead Time:</strong> {quote.lead_time_days} days
          </div>
          
          <div style={{ marginBottom: '10px' }}>
            <strong>Minimum Order:</strong> {quote.minimum_order_quantity}
          </div>
          
          {quote.payment_terms && (
            <div style={{ marginBottom: '10px' }}>
              <strong>Payment Terms:</strong> {quote.payment_terms}
            </div>
          )}
          
          {quote.warranty_period && (
            <div style={{ marginBottom: '10px' }}>
              <strong>Warranty:</strong> {quote.warranty_period}
            </div>
          )}
          
          <div style={{ marginBottom: '10px' }}>
            <strong>Confidence Level:</strong> {quote.confidence_level}%
          </div>
        </Card>

        {/* Timeline */}
        <Card title="Timeline">
          <div style={{ marginBottom: '15px' }}>
            <strong>Created:</strong><br />
            {format(new Date(quote.created_at), 'MMMM dd, yyyy HH:mm')}
          </div>
          
          {quote.submitted_at && (
            <div style={{ marginBottom: '15px' }}>
              <strong>Submitted:</strong><br />
              {format(new Date(quote.submitted_at), 'MMMM dd, yyyy HH:mm')}
            </div>
          )}
          
          <div style={{ marginBottom: '15px' }}>
            <strong>Last Updated:</strong><br />
            {format(new Date(quote.updated_at || quote.created_at), 'MMMM dd, yyyy HH:mm')}
          </div>
          
          <div style={{ marginBottom: '15px' }}>
            <strong>Is Final:</strong> {quote.is_final ? 'Yes' : 'No'}
          </div>
        </Card>
      </div>

      {/* Technical Response */}
      {quote.technical_response && (
        <Card title="Technical Response">
          <p style={{ whiteSpace: 'pre-wrap', lineHeight: '1.6' }}>
            {quote.technical_response}
          </p>
        </Card>
      )}

      {/* Certifications */}
      {quote.certifications_provided && (
        <Card title="Certifications Provided">
          <p>{quote.certifications_provided}</p>
        </Card>
      )}

      {/* Notes */}
      {quote.notes && (
        <Card title="Additional Notes">
          <p style={{ whiteSpace: 'pre-wrap', lineHeight: '1.6' }}>
            {quote.notes}
          </p>
        </Card>
      )}

      {/* Actions */}
      <Card>
        <div style={{ display: 'flex', gap: '10px', justifyContent: 'flex-end' }}>
          {quote.status === 'DRAFT' && (
            <>
              <Link to={`/quotes/${quote.id}/edit`}>
                <Button variant="outline">Edit Quote</Button>
              </Link>
              <Button 
                onClick={handleSubmitQuote}
                loading={actionLoading}
              >
                Submit Quote
              </Button>
            </>
          )}
          
          {quote.status === 'SUBMITTED' && (
            <Button 
              variant="danger"
              onClick={handleWithdrawQuote}
              loading={actionLoading}
            >
              Withdraw Quote
            </Button>
          )}
          
          {quote.status === 'ACCEPTED' && (
            <div style={{ 
              padding: '10px 20px', 
              backgroundColor: '#d4edda', 
              color: '#155724',
              borderRadius: '4px',
              fontWeight: 'bold'
            }}>
              Quote Accepted - Contact manufacturer for next steps
            </div>
          )}
          
          <Link to={`/rfqs/${quote.rfq_id}`}>
            <Button variant="outline">View Original RFQ</Button>
          </Link>
        </div>
      </Card>
    </div>
  );
};

export default QuoteDetails;