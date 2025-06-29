import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { rfqService } from '../../services/rfq';
import Card from '../common/Card';
import Input from '../common/Input';
import Button from '../common/Button';

const CreateRFQ = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    product_category: '',
    quantity: '',
    unit: 'pieces',
    target_price_min: '',
    target_price_max: '',
    currency: 'USD',
    quote_deadline: '',
    delivery_deadline: '',
    delivery_location: '',
    shipping_terms: '',
    technical_specs: '',
    quality_requirements: '',
    certifications_required: '',
    priority: 'MEDIUM',
    max_suppliers: 10
  });

  const handleChange = (e) => {
    const { name, value, type } = e.target;
    setFormData({
      ...formData,
      [name]: type === 'number' ? parseInt(value) || '' : value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
  
    try {
      const rfqData = {
        ...formData,
        quantity: parseInt(formData.quantity),
        target_price_min: formData.target_price_min ? parseFloat(formData.target_price_min) : null,
        target_price_max: formData.target_price_max ? parseFloat(formData.target_price_max) : null,
        max_suppliers: parseInt(formData.max_suppliers),
        // Ensure proper datetime format
        quote_deadline: new Date(formData.quote_deadline).toISOString(),
        delivery_deadline: formData.delivery_deadline ? new Date(formData.delivery_deadline).toISOString() : null,
        // Ensure uppercase priority
        priority: formData.priority.toUpperCase()
      };
  
      console.log('Sending RFQ data:', rfqData); // Debug log
  
      const response = await rfqService.createRFQ(rfqData);
      alert('RFQ created successfully!');
      navigate(`/rfqs/${response.id}`);
    } catch (error) {
      console.error('Error creating RFQ:', error);
      console.error('Error response:', error.response?.data); // Debug log
      alert(`Error creating RFQ: ${error.response?.data?.detail || 'Please try again.'}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container">
      <h1>Create New RFQ</h1>
      
      <Card title="RFQ Details">
        <form onSubmit={handleSubmit}>
          <Input
            label="Title"
            name="title"
            value={formData.title}
            onChange={handleChange}
            required
            placeholder="e.g., Electronic Components for Smart TV Manufacturing"
          />

          <div className="form-group">
            <label className="form-label">Description *</label>
            <textarea
              className="form-textarea"
              name="description"
              value={formData.description}
              onChange={handleChange}
              required
              placeholder="Detailed description of what you need..."
            />
          </div>

          <div className="grid grid-2">
            <div className="form-group">
              <label className="form-label">Product Category *</label>
              <select
                className="form-select"
                name="product_category"
                value={formData.product_category}
                onChange={handleChange}
                required
              >
                <option value="">Select Category</option>
                <option value="Electronics">Electronics</option>
                <option value="Automotive">Automotive Parts</option>
                <option value="Textiles">Textiles</option>
                <option value="Packaging">Packaging</option>
                <option value="Machinery">Machinery</option>
                <option value="Raw Materials">Raw Materials</option>
                <option value="Other">Other</option>
              </select>
            </div>

            <div className="form-group">
              <label className="form-label">Priority</label>
              <select
                className="form-select"
                name="priority"
                value={formData.priority}
                onChange={handleChange}
              >
                <option value="LOW">Low</option>
                <option value="MEDIUM">Medium</option>
                <option value="HIGH">High</option>
                <option value="URGENT">Urgent</option>
              </select>
            </div>
          </div>

          <div className="grid grid-3">
            <Input
              label="Quantity"
              name="quantity"
              type="number"
              value={formData.quantity}
              onChange={handleChange}
              required
              min="1"
            />
            
            <div className="form-group">
              <label className="form-label">Unit</label>
              <select
                className="form-select"
                name="unit"
                value={formData.unit}
                onChange={handleChange}
              >
                <option value="pieces">Pieces</option>
                <option value="kg">Kilograms</option>
                <option value="meters">Meters</option>
                <option value="liters">Liters</option>
                <option value="sets">Sets</option>
              </select>
            </div>

            <Input
              label="Max Suppliers"
              name="max_suppliers"
              type="number"
              value={formData.max_suppliers}
              onChange={handleChange}
              min="1"
              max="50"
            />
          </div>

          <h4>Budget Range (Optional)</h4>
          <div className="grid grid-3">
            <Input
              label="Min Price per Unit"
              name="target_price_min"
              type="number"
              step="0.01"
              value={formData.target_price_min}
              onChange={handleChange}
            />
            
            <Input
              label="Max Price per Unit"
              name="target_price_max"
              type="number"
              step="0.01"
              value={formData.target_price_max}
              onChange={handleChange}
            />
            
            <div className="form-group">
              <label className="form-label">Currency</label>
              <select
                className="form-select"
                name="currency"
                value={formData.currency}
                onChange={handleChange}
              >
                <option value="USD">USD</option>
                <option value="EUR">EUR</option>
                <option value="GBP">GBP</option>
                <option value="JPY">JPY</option>
              </select>
            </div>
          </div>

          <h4>Timeline</h4>
          <div className="grid grid-2">
            <Input
              label="Quote Deadline"
              name="quote_deadline"
              type="datetime-local"
              value={formData.quote_deadline}
              onChange={handleChange}
              required
            />
            
            <Input
              label="Delivery Deadline (Optional)"
              name="delivery_deadline"
              type="datetime-local"
              value={formData.delivery_deadline}
              onChange={handleChange}
            />
          </div>

          <h4>Additional Details</h4>
          <div className="grid grid-2">
            <Input
              label="Delivery Location"
              name="delivery_location"
              value={formData.delivery_location}
              onChange={handleChange}
              placeholder="City, State, Country"
            />
            
            <Input
              label="Shipping Terms"
              name="shipping_terms"
              value={formData.shipping_terms}
              onChange={handleChange}
              placeholder="FOB, CIF, etc."
            />
          </div>

          <div className="form-group">
            <label className="form-label">Technical Specifications</label>
            <textarea
              className="form-textarea"
              name="technical_specs"
              value={formData.technical_specs}
              onChange={handleChange}
              placeholder="Detailed technical requirements, dimensions, materials, etc."
            />
          </div>

          <div className="form-group">
            <label className="form-label">Quality Requirements</label>
            <textarea
              className="form-textarea"
              name="quality_requirements"
              value={formData.quality_requirements}
              onChange={handleChange}
              placeholder="Quality standards, testing requirements, etc."
            />
          </div>

          <Input
            label="Required Certifications"
            name="certifications_required"
            value={formData.certifications_required}
            onChange={handleChange}
            placeholder="ISO 9001, CE, FCC, etc."
          />

          <div style={{ display: 'flex', gap: '10px', justifyContent: 'flex-end' }}>
            <Button
              type="button"
              variant="secondary"
              onClick={() => navigate('/rfqs')}
            >
              Cancel
            </Button>
            <Button type="submit" loading={loading}>
              Create RFQ
            </Button>
          </div>
        </form>
      </Card>
    </div>
  );
};

export default CreateRFQ;