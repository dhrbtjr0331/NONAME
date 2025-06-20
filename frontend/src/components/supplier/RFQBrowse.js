import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { rfqService } from '../../services/rfq';
import Card from '../common/Card';
import Button from '../common/Button';
import LoadingSpinner from '../common/LoadingSpinner';
import { format, isAfter } from 'date-fns';

const RFQBrowse = () => {
  const [rfqs, setRfqs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [categoryFilter, setCategoryFilter] = useState('');
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    loadRFQs();
  }, [categoryFilter]);

  const loadRFQs = async () => {
    try {
      setLoading(true);
      const params = categoryFilter ? { product_category: categoryFilter } : {};
      const data = await rfqService.getPublicRFQs(params);
      setRfqs(data);
    } catch (error) {
      console.error('Error loading RFQs:', error);
      alert('Error loading RFQs. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const filteredRfqs = rfqs.filter(rfq => 
    rfq.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
    rfq.description.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const isDeadlineSoon = (deadline) => {
    const deadlineDate = new Date(deadline);
    const twoDaysFromNow = new Date();
    twoDaysFromNow.setDate(twoDaysFromNow.getDate() + 2);
    return isAfter(twoDaysFromNow, deadlineDate);
  };

  const getPriorityColor = (priority) => {
    const colors = {
      'LOW': '#6c757d',
      'MEDIUM': '#ffc107',
      'HIGH': '#fd7e14', 
      'URGENT': '#dc3545'
    };
    return colors[priority] || '#6c757d';
  };

  if (loading) {
    return <LoadingSpinner message="Loading available RFQs..." />;
  }

  return (
    <div className="container">
      <h1>Browse RFQs</h1>
      <p style={{ color: '#666', marginBottom: '20px' }}>
        Find opportunities to submit quotes and grow your business
      </p>

      {/* Search and Filter */}
      <Card>
        <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '15px', alignItems: 'end' }}>
          <div className="form-group" style={{ margin: 0 }}>
            <label className="form-label">Search RFQs</label>
            <input
              type="text"
              className="form-input"
              placeholder="Search by title or description..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
          
          <div className="form-group" style={{ margin: 0 }}>
            <label className="form-label">Category Filter</label>
            <select
              className="form-select"
              value={categoryFilter}
              onChange={(e) => setCategoryFilter(e.target.value)}
            >
              <option value="">All Categories</option>
              <option value="Electronics">Electronics</option>
              <option value="Automotive">Automotive</option>
              <option value="Textiles">Textiles</option>
              <option value="Packaging">Packaging</option>
              <option value="Machinery">Machinery</option>
              <option value="Raw Materials">Raw Materials</option>
              <option value="Other">Other</option>
            </select>
          </div>
        </div>
      </Card>

      {filteredRfqs.length === 0 ? (
        <Card>
          <div className="text-center">
            <h3>No RFQs Found</h3>
            <p>No RFQs match your current search criteria.</p>
            <p>Try adjusting your filters or check back later for new opportunities.</p>
          </div>
        </Card>
      ) : (
        <>
          <div style={{ marginBottom: '15px', color: '#666' }}>
            Showing {filteredRfqs.length} RFQ{filteredRfqs.length !== 1 ? 's' : ''}
          </div>
          
          <div className="grid grid-2">
           {filteredRfqs.map(rfq => (
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
                   <span 
                     className="status-badge"
                     style={{ 
                       backgroundColor: getPriorityColor(rfq.priority),
                       color: 'white'
                     }}
                   >
                     {rfq.priority}
                   </span>
                 </div>
                 
                 <p style={{ color: '#666', fontSize: '14px', margin: '5px 0' }}>
                   <strong>Category:</strong> {rfq.product_category}
                 </p>
                 
                 <p style={{ color: '#666', fontSize: '14px', margin: '5px 0' }}>
                   <strong>Quantity:</strong> {rfq.quantity.toLocaleString()} {rfq.unit}
                 </p>
                 
                 <div style={{ 
                   color: isDeadlineSoon(rfq.quote_deadline) ? '#dc3545' : '#666', 
                   fontSize: '14px', 
                   margin: '5px 0',
                   fontWeight: isDeadlineSoon(rfq.quote_deadline) ? 'bold' : 'normal'
                 }}>
                   <strong>Quote Deadline:</strong> {format(new Date(rfq.quote_deadline), 'MMM dd, yyyy HH:mm')}
                   {isDeadlineSoon(rfq.quote_deadline) && (
                     <span style={{ marginLeft: '5px' }}>⚠️ URGENT</span>
                   )}
                 </div>
                 
                 <p style={{ color: '#666', fontSize: '14px', margin: '5px 0' }}>
                   <strong>Posted:</strong> {format(new Date(rfq.created_at), 'MMM dd, yyyy')}
                 </p>
               </div>
               
               <div style={{ display: 'flex', gap: '10px' }}>
                 <Link to={`/rfqs/${rfq.id}`} style={{ flex: 1 }}>
                   <Button variant="outline" style={{ width: '100%' }}>
                     View Details
                   </Button>
                 </Link>
                 
                 <Link to={`/quotes/create?rfqId=${rfq.id}`} style={{ flex: 1 }}>
                   <Button style={{ width: '100%' }}>
                     Submit Quote
                   </Button>
                 </Link>
               </div>
             </Card>
           ))}
         </div>
       </>
     )}
   </div>
 );
};

export default RFQBrowse;
