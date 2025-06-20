import React, { useState, useEffect, useCallback } from 'react';
import { useParams, Link } from 'react-router-dom';
import { rfqService } from '../../services/rfq';
import { quoteService } from '../../services/quote'; // Fixed import
import Card from '../common/Card';
import Button from '../common/Button';
import LoadingSpinner from '../common/LoadingSpinner';
import { format } from 'date-fns';

const QuoteComparison = () => {
  const { rfqId } = useParams();
  const [rfq, setRfq] = useState(null);
  const [quotes, setQuotes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(null);
  const [sortBy, setSortBy] = useState('price');

  const loadData = useCallback(async () => {
    try {
      setLoading(true);
      const [rfqData, quotesData] = await Promise.all([
        rfqService.getRFQById(rfqId),
        rfqService.getQuotesForRFQ(rfqId)
      ]);
      setRfq(rfqData);
      setQuotes(quotesData);
    } catch (error) {
      console.error('Error loading data:', error);
      alert('Error loading quotes. Please try again.');
    } finally {
      setLoading(false);
    }
  }, [rfqId]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const handleAcceptQuote = async (quoteId) => {
    if (!window.confirm('Are you sure you want to accept this quote? This will close the RFQ and reject all other quotes.')) {
      return;
    }

    try {
      setActionLoading(quoteId);
      await quoteService.acceptQuote(quoteId);
      await loadData(); // Refresh data
      alert('Quote accepted successfully!');
    } catch (error) {
      console.error('Error accepting quote:', error);
      alert('Error accepting quote. Please try again.');
    } finally {
      setActionLoading(null);
    }
  };

  const getSortedQuotes = () => {
    return [...quotes].sort((a, b) => {
      switch (sortBy) {
        case 'price':
          return a.total_price - b.total_price;
        case 'leadTime':
          return a.lead_time_days - b.lead_time_days;
        case 'date':
          return new Date(b.created_at) - new Date(a.created_at);
        default:
          return 0;
      }
    });
  };

  const getStatusBadge = (status) => {
    const statusClasses = {
      'SUBMITTED': 'status-pending',
      'UNDER_REVIEW': 'status-pending',
      'ACCEPTED': 'status-accepted',
      'REJECTED': 'status-closed'
    };
    
    return (
      <span className={`status-badge ${statusClasses[status] || 'status-pending'}`}>
        {status}
      </span>
    );
  };

  if (loading) {
    return <LoadingSpinner message="Loading quotes..." />;
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

  const sortedQuotes = getSortedQuotes();

  return (
    <div className="container">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <div>
          <h1>Quotes for: {rfq.title}</h1>
          <p style={{ color: '#666', margin: 0 }}>
            {quotes.length} quote{quotes.length !== 1 ? 's' : ''} received
          </p>
        </div>
        <Link to={`/rfqs/${rfqId}`}>
          <Button variant="outline">Back to RFQ</Button>
        </Link>
      </div>

      {quotes.length === 0 ? (
        <Card>
          <div className="text-center">
            <h3>No Quotes Yet</h3>
            <p>No suppliers have submitted quotes for this RFQ yet.</p>
            <p>Check back later or share your RFQ with potential suppliers.</p>
          </div>
        </Card>
      ) : (
        <>
          {/* Sort Controls */}
          <Card>
            <div style={{ display: 'flex', alignItems: 'center', gap: '15px' }}>
              <span><strong>Sort by:</strong></span>
              <button
                onClick={() => setSortBy('price')}
                style={{
                  padding: '5px 10px',
                  border: 'none',
                  background: sortBy === 'price' ? '#007bff' : '#f8f9fa',
                  color: sortBy === 'price' ? 'white' : '#333',
                  borderRadius: '4px',
                  cursor: 'pointer'
                }}
              >
                Price (Low to High)
              </button>
              <button
                onClick={() => setSortBy('leadTime')}
                style={{
                  padding: '5px 10px',
                  border: 'none',
                  background: sortBy === 'leadTime' ? '#007bff' : '#f8f9fa',
                  color: sortBy === 'leadTime' ? 'white' : '#333',
                  borderRadius: '4px',
                  cursor: 'pointer'
                }}
              >
                Lead Time
              </button>
              <button
                onClick={() => setSortBy('date')}
                style={{
                  padding: '5px 10px',
                  border: 'none',
                  background: sortBy === 'date' ? '#007bff' : '#f8f9fa',
                  color: sortBy === 'date' ? 'white' : '#333',
                  borderRadius: '4px',
                  cursor: 'pointer'
                }}
              >
                Date Submitted
              </button>
            </div>
          </Card>

          {/* Quotes List */}
          <div className="grid grid-2">
            {sortedQuotes.map((quote, index) => (
              <Card key={quote.id}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '15px' }}>
                  <h3 style={{ margin: 0 }}>
                    Quote #{quote.id}
                    {index === 0 && sortBy === 'price' && (
                      <span style={{ color: '#28a745', fontSize: '14px', marginLeft: '10px' }}>
                        LOWEST PRICE
                      </span>
                    )}
                  </h3>
                  {getStatusBadge(quote.status)}
                </div>

                <div style={{ marginBottom: '15px' }}>
                  <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#007bff', marginBottom: '5px' }}>
                    {quote.currency} {quote.total_price.toLocaleString()}
                  </div>
                  <div style={{ fontSize: '14px', color: '#666' }}>
                    Unit Price: {quote.currency} {quote.unit_price} per {rfq.unit}
                  </div>
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px', marginBottom: '15px', fontSize: '14px' }}>
                  <div>
                    <strong>Lead Time:</strong><br />
                    {quote.lead_time_days} days
                  </div>
                  <div>
                    <strong>Min Order:</strong><br />
                    {quote.minimum_order_quantity} {rfq.unit}
                  </div>
                  {quote.payment_terms && (
                    <div>
                      <strong>Payment:</strong><br />
                      {quote.payment_terms}
                    </div>
                  )}
                  {quote.warranty_period && (
                    <div>
                      <strong>Warranty:</strong><br />
                      {quote.warranty_period}
                    </div>
                  )}
                </div>

                {quote.certifications_provided && (
                  <div style={{ marginBottom: '15px', fontSize: '14px' }}>
                    <strong>Certifications:</strong><br />
                    {quote.certifications_provided}
                  </div>
                )}

                {quote.notes && (
                  <div style={{ marginBottom: '15px', fontSize: '14px' }}>
                    <strong>Supplier Notes:</strong><br />
                    <p style={{ 
                      backgroundColor: '#f8f9fa', 
                      padding: '10px', 
                      borderRadius: '4px',
                      margin: '5px 0',
                      whiteSpace: 'pre-wrap'
                    }}>
                      {quote.notes}
                    </p>
                  </div>
                )}

                {quote.technical_response && (
                  <div style={{ marginBottom: '15px', fontSize: '14px' }}>
                    <strong>Technical Response:</strong><br />
                    <p style={{ 
                      backgroundColor: '#f8f9fa', 
                      padding: '10px', 
                      borderRadius: '4px',
                      margin: '5px 0',
                      whiteSpace: 'pre-wrap'
                    }}>
                      {quote.technical_response}
                    </p>
                  </div>
                )}

                <div style={{ fontSize: '12px', color: '#666', marginBottom: '15px' }}>
                  <div>Confidence Level: {quote.confidence_level}%</div>
                  <div>Submitted: {format(new Date(quote.submitted_at || quote.created_at), 'MMM dd, yyyy HH:mm')}</div>
                </div>

                {rfq.status === 'OPEN' && quote.status === 'SUBMITTED' && (
                  <div style={{ display: 'flex', gap: '10px' }}>
                    <Button
                      variant="success"
                      onClick={() => handleAcceptQuote(quote.id)}
                      loading={actionLoading === quote.id}
                      style={{ flex: 1 }}
                    >
                      Accept Quote
                    </Button>
                    <Button variant="outline" style={{ flex: 1 }}>
                      Contact Supplier
                    </Button>
                  </div>
                )}

                {quote.status === 'ACCEPTED' && (
                  <div style={{ 
                    padding: '10px', 
                    backgroundColor: '#d4edda', 
                    color: '#155724',
                    borderRadius: '4px',
                    textAlign: 'center',
                    fontWeight: 'bold'
                  }}>
                    ✓ ACCEPTED QUOTE
                  </div>
                )}
              </Card>
            ))}
          </div>
        </>
      )}
    </div>
  );
};

export default QuoteComparison;