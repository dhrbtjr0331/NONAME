import React, { useState, useEffect } from 'react';
import { userService } from '../../services/user';
import { useAuth } from '../../hooks/useAuth';
import Card from '../common/Card';
import Input from '../common/Input';
import Button from '../common/Button';
import LoadingSpinner from '../common/LoadingSpinner';

const Profile = () => {
  const { user } = useAuth();
  const [profile, setProfile] = useState(null);
  const [company, setCompany] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [activeTab, setActiveTab] = useState('profile');

  const [profileForm, setProfileForm] = useState({
    first_name: '',
    last_name: '',
    phone: '',
    job_title: '',
    bio: ''
  });

  const [companyForm, setCompanyForm] = useState({
    company_name: '',
    industry: '',
    company_size: '',
    website: '',
    description: '',
    address_line1: '',
    city: '',
    state: '',
    country: '',
    postal_code: ''
  });

  useEffect(() => {
    loadProfile();
  }, []);

  const loadProfile = async () => {
    try {
      setLoading(true);
      
      // Try to get existing profile
      try {
        const profileResponse = await userService.getMyProfile();
        setProfile(profileResponse);
        setProfileForm(profileResponse);
      } catch (error) {
        if (error.response?.status !== 404) {
          console.error('Error loading profile:', error);
        }
      }

      // Try to get existing company
      try {
        const companyResponse = await userService.getMyCompany();
        setCompany(companyResponse);
        setCompanyForm(companyResponse);
      } catch (error) {
        if (error.response?.status !== 404) {
          console.error('Error loading company:', error);
        }
      }
    } catch (error) {
      console.error('Error loading data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleProfileSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);

    try {
      if (profile) {
        // Update existing profile
        const response = await userService.updateProfile(profileForm);
        setProfile(response);
      } else {
        // Create new profile
        const response = await userService.createProfile({
          ...profileForm,
          user_id: user.id
        });
        setProfile(response);
      }
      alert('Profile saved successfully!');
    } catch (error) {
      console.error('Error saving profile:', error);
      alert('Error saving profile. Please try again.');
    } finally {
      setSaving(false);
    }
  };

  const handleCompanySubmit = async (e) => {
    e.preventDefault();
    setSaving(true);

    try {
      if (company) {
        // Update existing company
        const response = await userService.updateCompany(companyForm);
        setCompany(response);
      } else {
        // Create new company
        const response = await userService.createCompany(companyForm);
        setCompany(response);
      }
      alert('Company information saved successfully!');
    } catch (error) {
      console.error('Error saving company:', error);
      alert('Error saving company information. Please try again.');
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return <LoadingSpinner message="Loading profile..." />;
  }

  return (
    <div className="container">
      <h1>Profile Settings</h1>
      
      {/* Tab Navigation */}
      <div style={{ 
        borderBottom: '1px solid #ddd', 
        marginBottom: '20px',
        display: 'flex',
        gap: '20px'
      }}>
        <button
          onClick={() => setActiveTab('profile')}
          style={{
            padding: '10px 0',
            border: 'none',
            background: 'none',
            borderBottom: activeTab === 'profile' ? '2px solid #007bff' : 'none',
            color: activeTab === 'profile' ? '#007bff' : '#666',
            cursor: 'pointer'
          }}
        >
          Personal Profile
        </button>
        <button
          onClick={() => setActiveTab('company')}
          style={{
            padding: '10px 0',
            border: 'none',
            background: 'none',
            borderBottom: activeTab === 'company' ? '2px solid #007bff' : 'none',
            color: activeTab === 'company' ? '#007bff' : '#666',
            cursor: 'pointer'
          }}
        >
          Company Information
        </button>
      </div>

      {/* Profile Tab */}
      {activeTab === 'profile' && (
        <Card title="Personal Information">
          <form onSubmit={handleProfileSubmit}>
            <div className="grid grid-2">
              <Input
                label="First Name"
                value={profileForm.first_name}
                onChange={(e) => setProfileForm({...profileForm, first_name: e.target.value})}
                required
              />
              <Input
                label="Last Name"
                value={profileForm.last_name}
                onChange={(e) => setProfileForm({...profileForm, last_name: e.target.value})}
                required
              />
            </div>

            <div className="grid grid-2">
              <Input
                label="Phone"
                value={profileForm.phone}
                onChange={(e) => setProfileForm({...profileForm, phone: e.target.value})}
                required
              />
              <Input
                label="Job Title"
                value={profileForm.job_title}
                onChange={(e) => setProfileForm({...profileForm, job_title: e.target.value})}
                required
              />
            </div>

            <div className="form-group">
              <label className="form-label">Bio</label>
              <textarea
                className="form-textarea"
                value={profileForm.bio}
                onChange={(e) => setProfileForm({...profileForm, bio: e.target.value})}
                placeholder="Tell us about yourself and your experience..."
              />
            </div>

            <Button type="submit" loading={saving}>
              {profile ? 'Update Profile' : 'Create Profile'}
            </Button>
          </form>
        </Card>
      )}

      {/* Company Tab */}
      {activeTab === 'company' && (
        <Card title="Company Information">
          <form onSubmit={handleCompanySubmit}>
            <Input
              label="Company Name"
              value={companyForm.company_name}
              onChange={(e) => setCompanyForm({...companyForm, company_name: e.target.value})}
              required
            />

            <div className="grid grid-2">
              <div className="form-group">
                <label className="form-label">Industry</label>
                <select
                  className="form-select"
                  value={companyForm.industry}
                  onChange={(e) => setCompanyForm({...companyForm, industry: e.target.value})}
                >
                  <option value="">Select Industry</option>
                  <option value="Electronics">Electronics</option>
                  <option value="Automotive">Automotive</option>
                  <option value="Textiles">Textiles</option>
                  <option value="Packaging">Packaging</option>
                  <option value="Machinery">Machinery</option>
                  <option value="Other">Other</option>
                </select>
              </div>

              <div className="form-group">
                <label className="form-label">Company Size</label>
                <select
                  className="form-select"
                  value={companyForm.company_size}
                  onChange={(e) => setCompanyForm({...companyForm, company_size: e.target.value})}
                >
                  <option value="">Select Size</option>
                  <option value="1-10">1-10 employees</option>
                  <option value="11-50">11-50 employees</option>
                  <option value="51-200">51-200 employees</option>
                  <option value="200+">200+ employees</option>
                </select>
              </div>
            </div>

            <Input
              label="Website"
              value={companyForm.website}
              onChange={(e) => setCompanyForm({...companyForm, website: e.target.value})}
              placeholder="https://www.yourcompany.com"
            />

            <div className="form-group">
              <label className="form-label">Description</label>
              <textarea
                className="form-textarea"
                value={companyForm.description}
                onChange={(e) => setCompanyForm({...companyForm, description: e.target.value})}
                placeholder="Describe your company and what you do..."
              />
            </div>

            <h4>Address</h4>
            <Input
              label="Address Line 1"
              value={companyForm.address_line1}
              onChange={(e) => setCompanyForm({...companyForm, address_line1: e.target.value})}
            />

            <div className="grid grid-3">
              <Input
                label="City"
                value={companyForm.city}
                onChange={(e) => setCompanyForm({...companyForm, city: e.target.value})}
              />
              <Input
                label="State"
                value={companyForm.state}
                onChange={(e) => setCompanyForm({...companyForm, state: e.target.value})}
              />
              <Input
                label="Postal Code"
                value={companyForm.postal_code}
                onChange={(e) => setCompanyForm({...companyForm, postal_code: e.target.value})}
              />
            </div>

            <Input
              label="Country"
              value={companyForm.country}
              onChange={(e) => setCompanyForm({...companyForm, country: e.target.value})}
            />

            <Button type="submit" loading={saving}>
              {company ? 'Update Company' : 'Create Company'}
            </Button>
          </form>
        </Card>
      )}
    </div>
  );
};

export default Profile;