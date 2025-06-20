import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { rfqService } from '../../services/rfq';
import { quoteService } from '../../services/quote';
import Card from '../common/Card';
import Input from '../common/Input';
import Button from '../common/Button';
import LoadingSpinner from '../common/LoadingSpinner';
import { format } from 'date-fns';

const CreateQuote = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const rfqId = searchParams.get('rfqId');
  
  const [rfq, setRfq] = useState(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSaving] = useState(false);
  
  const [formData, setFormData] = useState({
    unit_price: '',
    total_price: '',
    currency: 'USD',
    lead_time_days: '',
    minimum_order_quantity: '',
    payment_terms: '',
    warranty_period: '',
    notes: '',
    technical_response: '',
    certifications_provided: '',
    confidence_level: 100
  });

  useEffect(() => {
    if (rfqId) {
      loadRFQ();
    } else {
      navigate('/browse-rfqs');
    }
  }, [rfqId]);

  useEffect(() => {
    // Auto-calculate total price when unit price or quantity changes
    if (formData.unit_price && rfq?.quantity) {
      const total = parseFloat(formData.unit_price) * rfq.quantity;
      setFormData(prev => ({
        ...prev,
        total_price: total.toFixed(2)
      }));
    }
  }, [formData.unit_price, rfq?.quantity]);

  const loadRFQ = async () => {
    try {
      setLoading(true);
      const data = await rfqService.getRFQById(rfqId);
      setRfq(data);
      setFormData(prev => ({
        ...prev,
        currency: data.currency || 'USD',
        minimum_order_quantity: data.quantity
      }));
    } catch (error) {
      console.error('Error loading RFQ:', error);
      alert('Error loading RFQ details.');
      navigate('/browse-rfqs');
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    const { name, value, type } = e.target;
    setFormData({
      ...formData,
      [name]: type === 'number' ? (value ? parseFloat(value) : '') : value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);

    try {
      const quoteData = {
        rfq_id: parseInt(rfqId),
        unit_price: parseFloat(formData.unit_price),
        total_price: parseFloat(formData.total_price),
        currency: formData.currency,
        lead_time_days: parseInt(formData.lead_time_days),
        minimum_order_quantity: parseInt(formData.minimum_order_quantity),
        payment_terms: formData.payment_terms || null,
        warranty_period: formData.warranty_period || null,
        notes: formData.notes || null,
        technical_response: formData.technical_response || null,
        certifications_provided: formData.certifications_provided || null,
        confidence_level: parseInt(formData.confidence_level)
      };

      const response = await quoteService.createQuote(quoteData);
      alert('Quote created successfully!');
      navigate(`/quotes/${response.id}`);
    } catch (error) {
      console.error('Error creating quote:', error);
      alert(error.response?.data?.detail || 'Error creating quote. Please try again.');
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return <LoadingSpinner message="Loading RFQ details..." />;
  }

  if (!rfq) {
    return (
      <div className="container text-center">
        <h2>RFQ Not Found</h2>
        <Button onClick={() => navigate('/browse-rfqs')}>
          Back to Browse RFQs
        </Button>
      </div>
    );
  }

  return (
    <div className="container">
      <h1>Submit Quote</h1>
      
      {/* RFQ Summary */}
      <Card title="RFQ Summary">
        <div className="grid grid-2">
          <div>
            <h3>{rfq.title}</h3>
            <p><strong>Category:</strong> {rfq.product_category}</p>
            <p><strong>Quantity:</strong> {rfq.quantity.toLocaleString()} {rfq.unit}</p>
            {rfq.target_price_min && rfq.target_price_max && (
              <p><strong>Target Price Range:</strong> {rfq.currency} {rfq.target_price_min} - {rfq.target_price_max} per {rfq.unit}</p>
            )}
          </div>
          <div>
            <p><strong>Quote Deadline:</strong> {format(new Date(rfq.quote_deadline), 'MMM dd, yyyy HH:mm')}</p>
            {rfq.delivery_deadline && (
              <p><strong>Delivery Deadline:</strong> {format(new Date(rfq.delivery_deadline), 'MMM dd, yyyy')}</p>
            )}
            <p><strong>Delivery Location:</strong> {rfq.delivery_location || 'Not specified'}</p>
          </div>
        </div>
        
        <div style={{ marginTop: '15px' }}>
          <h4>Description</h4>
          <p style={{ whiteSpace: 'pre-wrap', lineHeight: '1.6' }}>
            {rfq.description}
          </p>
        </div>
      </Card>

      {/* Quote Form */}
      <Card title="Your Quote">
        <form onSubmit={handleSubmit}>
          <h4>Pricing</h4>
          <div className="grid grid-3">
            <Input
              label="Unit Price"
              name="unit_price"
              type="number"
              step="0.01"
              value={formData.unit_price}
              onChange={handleChange}
              required
              placeholder="Price per unit"
            />
            
            <Input
              label="Total Price"
              name="total_price"
              type="number"
              step="0.01"
              value={formData.total_price}
              onChange={handleChange}
              required
              placeholder="Total price for all units"
            />
            
            <div className="form-group">
              <label className="form-label">Currency</label>
              <select
                className="form-select"
                name="currency"
                value={formData.currency}
                onChange={handleChange}
                required
              >
                <option value="USD">USD</option>
                <option value="EUR">EUR</option>
                <option value="GBP">GBP</option>
                <option value="JPY">JPY</option>
              </select>
            </div>
          </div>

          <h4>Terms & Conditions</h4>
          <div className="grid grid-3">
            <Input
              label="Lead Time (Days)"
              name="lead_time_days"
              type="number"
              value={formData.lead_time_days}
              onChange={handleChange}
              required
              min="1"
              placeholder="Manufacturing/delivery time"
            />
            
            <Input
              label="Minimum Order Quantity"
              name="minimum_order_quantity"
              type="number"
              value={formData.minimum_order_quantity}
              onChange={handleChange}
              required
              min="1"
            />
            
            <Input
              label="Payment Terms"
              name="payment_terms"
              value={formData.payment_terms}
              onChange={handleChange}
              placeholder="e.g., Net 30, Advance payment"
            />
          </div>

          <Input
            label="Warranty Period"
            name="warranty_period"
            value={formData.warranty_period}
            onChange={handleChange}
            placeholder="e.g., 1 year, 6 months"
          />

          <h4>Technical & Compliance</h4>
          <div className="form-group">
            <label className="form-label">Technical Response</label>
            <textarea
              className="form-textarea"
              name="technical_response"
              value={formData.technical_response}
              onChange={handleChange}
              placeholder="Explain how your product/service meets the technical requirements..."
            />
          </div>

          <Input
            label="Certifications Provided"
            name="certifications_provided"
            value={formData.certifications_provided}
            onChange={handleChange}
            placeholder="e.g., ISO 9001, CE, FCC"
          />

          <div className="form-group">
            <label className="form-label">Additional Notes</label>
            <textarea
              className="form-textarea"
              name="notes"
              value={formData.notes}
              onChange={handleChange}
              placeholder="Any additional information, special offers, or terms..."
            />
          </div>

          <div className="form-group">
            <label className="form-label">Confidence Level: {formData.confidence_level}%</label>
            <input
              type="range"
              min="0"
              max="100"
              name="confidence_level"
              value={formData.confidence_level}
              onChange={handleChange}
              style={{ width: '100%' }}
            />
            <small style={{ color: '#666' }}>
              How confident are you in meeting all requirements and deadlines?
            </small>
          </div>

          <div style={{ display: 'flex', gap: '10px', justifyContent: 'flex-end' }}>
            <Button
              type="button"
              variant="secondary"
              onClick={() => navigate('/browse-rfqs')}
            >
              Cancel
            </Button>
            <Button type="submit" loading={submitting}>
              Submit Quote
            </Button>
          </div>
        </form>
      </Card>
    </div>
  );
};

export default CreateQuote;