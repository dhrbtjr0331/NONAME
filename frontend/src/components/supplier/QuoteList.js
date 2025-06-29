import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { quoteService } from '../../services/quote';
import Card from '../common/Card';
import Button from '../common/Button';
import LoadingSpinner from '../common/LoadingSpinner';
import { format } from 'date-fns';

const QuoteList = () => {
  const [quotes, setQuotes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');

  useEffect(() => {
    loadQuotes();
  }, [filter]);

  const loadQuotes = async () => {
    try {
      setLoading(true);
      const params = filter !== 'all' ? { status: filter } : {};
      const data = await quoteService.getMyQuotes(params);
      setQuotes(data);
    } catch (error) {
      console.error('Error loading quotes:', error);
      alert('Error loading quotes. Please try again.');
    } finally {
      setLoading(false);
    }
  };

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

  if (loading) {
    return <LoadingSpinner message="Loading your quotes..." />;
  }

  return (
    <div className="container">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <h1>My Quotes</h1>
        <Link to="/browse-rfqs">
          <Button>Browse RFQs</Button>
        </Link>
      </div>

      {/* Filter Tabs */}
      <div style={{ 
        borderBottom: '1px solid #ddd', 
        marginBottom: '20px',
        display: 'flex',
        gap: '20px'
      }}>
        {['all', 'DRAFT', 'SUBMITTED', 'ACCEPTED', 'REJECTED'].map(status => (
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
            {status === 'all' ? 'All Quotes' : status}
          </button>
        ))}
      </div>

      {quotes.length === 0 ? (
        <Card>
          <div className="text-center">
            <h3>No Quotes Found</h3>
            <p>You haven't submitted any quotes yet.</p>
            <Link to="/browse-rfqs">
              <Button>Browse Available RFQs</Button>
            </Link>
          </div>
        </Card>
      ) : (
        <div className="grid grid-2">
          {quotes.map(quote => (
            <Card key={quote.id}>
              <div style={{ marginBottom: '15px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '10px' }}>
                  <h3 style={{ margin: 0, flex: 1 }}>
                    Quote #{quote.id}
                  </h3>
                  {getStatusBadge(quote.status)}
                </div>
                
                <div style={{ fontSize: '20px', fontWeight: 'bold', color: '#007bff', marginBottom: '10px' }}>
                  {quote.currency} {quote.total_price.toLocaleString()}
                </div>
                
                <p style={{ color: '#666', fontSize: '14px', margin: '5px 0' }}>
                  <strong>Unit Price:</strong> {quote.currency} {quote.unit_price}
                </p>
                
                <p style={{ color: '#666', fontSize: '14px', margin: '5px 0' }}>
                  <strong>Lead Time:</strong> {quote.lead_time_days} days
                </p>
                
                <p style={{ color: '#666', fontSize: '14px', margin: '5px 0' }}>
                  <strong>RFQ ID:</strong> #{quote.rfq_id}
                </p>
                
                <p style={{ color: '#666', fontSize: '14px', margin: '5px 0' }}>
                  <strong>Created:</strong> {format(new Date(quote.created_at), 'MMM dd, yyyy')}
                </p>

                {quote.submitted_at && (
                  <p style={{ color: '#666', fontSize: '14px', margin: '5px 0' }}>
                    <strong>Submitted:</strong> {format(new Date(quote.submitted_at), 'MMM dd, yyyy HH:mm')}
                  </p>
                )}
              </div>
              
              <div style={{ display: 'flex', gap: '10px' }}>
                <Link to={`/quotes/${quote.id}`} style={{ flex: 1 }}>
                  <Button variant="outline" style={{ width: '100%' }}>
                    View Details
                  </Button>
                </Link>
                
                {quote.status === 'DRAFT' && (
                  <Link to={`/quotes/${quote.id}/edit`} style={{ flex: 1 }}>
                    <Button style={{ width: '100%' }}>
                      Edit & Submit
                    </Button>
                  </Link>
                )}

                {quote.status === 'ACCEPTED' && (
                  <div style={{ 
                    flex: 1,
                    padding: '10px',
                    backgroundColor: '#d4edda', 
                    color: '#155724',
                    borderRadius: '4px',
                    textAlign: 'center',
                    fontWeight: 'bold',
                    border: 'none',
                    cursor: 'default'  // Changed from pointer to default
                  }}>
                    ✓ Accepted
                  </div>
                )}

                {/* Keep other status buttons as they were */}
                {quote.status === 'SUBMITTED' && (
                  <Button variant="outline" style={{ flex: 1 }} disabled>
                    Under Review
                  </Button>
                )}

                {quote.status === 'REJECTED' && (
                  <Button variant="secondary" style={{ flex: 1 }} disabled>
                    Rejected
                  </Button>
                )}
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
};

export default QuoteList;