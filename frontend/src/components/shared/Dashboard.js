import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import { rfqService } from '../../services/rfq';
import { quoteService } from '../../services/quote';
import Card from '../common/Card';
import Button from '../common/Button';
import LoadingSpinner from '../common/LoadingSpinner';
import { format } from 'date-fns';

const Dashboard = () => {
  const { user, isManufacturer } = useAuth();

  if (isManufacturer) {
    return <ManufacturerDashboard />;
  } else {
    return <SupplierDashboard />;
  }
};

const ManufacturerDashboard = () => {
  const [recentRFQs, setRecentRFQs] = useState([]);
  const [stats, setStats] = useState({
    totalRFQs: 0,
    openRFQs: 0,
    totalQuotes: 0,
    acceptedQuotes: 0
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      
      // Load recent RFQs
      const rfqs = await rfqService.getMyRFQs({ limit: 5 });
      setRecentRFQs(rfqs);
      
      // Calculate basic stats
      const allRFQs = await rfqService.getMyRFQs();
      const openRFQs = allRFQs.filter(rfq => rfq.status === 'OPEN');
      
      setStats({
        totalRFQs: allRFQs.length,
        openRFQs: openRFQs.length,
        totalQuotes: 0, // Would need aggregated data from backend
        acceptedQuotes: 0
      });
    } catch (error) {
      console.error('Error loading dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <LoadingSpinner message="Loading dashboard..." />;
  }

  return (
    <div className="container">
      <h1>Manufacturer Dashboard</h1>
      <p style={{ color: '#666', marginBottom: '30px' }}>
        Welcome back! Here's an overview of your RFQs and quotes.
      </p>

      {/* Stats Cards */}
      <div className="grid grid-3" style={{ marginBottom: '30px' }}>
        <Card>
          <div style={{ textAlign: 'center' }}>
            <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#007bff' }}>
              {stats.totalRFQs}
            </div>
            <div style={{ color: '#666' }}>Total RFQs</div>
          </div>
        </Card>
        
        <Card>
          <div style={{ textAlign: 'center' }}>
            <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#28a745' }}>
              {stats.openRFQs}
            </div>
            <div style={{ color: '#666' }}>Open RFQs</div>
          </div>
        </Card>
        
        <Card>
          <div style={{ textAlign: 'center' }}>
            <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#ffc107' }}>
              {stats.totalQuotes}
            </div>
            <div style={{ color: '#666' }}>Total Quotes Received</div>
          </div>
        </Card>
      </div>

      {/* Quick Actions */}
      <Card title="Quick Actions">
        <div style={{ display: 'flex', gap: '15px', flexWrap: 'wrap' }}>
          <Link to="/rfqs/create">
            <Button>Create New RFQ</Button>
          </Link>
          <Link to="/rfqs">
            <Button variant="outline">View All RFQs</Button>
          </Link>
          <Link to="/profile">
            <Button variant="outline">Update Profile</Button>
          </Link>
        </div>
      </Card>

      {/* Recent RFQs */}
      <Card 
        title="Recent RFQs" 
        headerAction={
          <Link to="/rfqs">
            <Button variant="outline">View All</Button>
          </Link>
        }
      >
        {recentRFQs.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '40px' }}>
            <h3>No RFQs Yet</h3>
            <p>Create your first RFQ to start receiving quotes from suppliers.</p>
            <Link to="/rfqs/create">
              <Button>Create RFQ</Button>
            </Link>
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '15px' }}>
            {recentRFQs.map(rfq => (
              <div 
                key={rfq.id}
                style={{ 
                  padding: '15px', 
                  border: '1px solid #eee', 
                  borderRadius: '4px',
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center'
                }}
              >
                <div>
                  <h4 style={{ margin: '0 0 5px 0' }}>
                    <Link to={`/rfqs/${rfq.id}`} style={{ color: '#007bff', textDecoration: 'none' }}>
                      {rfq.title}
                    </Link>
                  </h4>
                  <div style={{ fontSize: '14px', color: '#666' }}>
                    {rfq.product_category} • {rfq.quantity} {rfq.unit} • 
                    Created {format(new Date(rfq.created_at), 'MMM dd')}
                  </div>
                </div>
                <span className={`status-badge status-${rfq.status.toLowerCase()}`}>
                  {rfq.status}
                </span>
              </div>
            ))}
          </div>
        )}
      </Card>
    </div>
  );
};

const SupplierDashboard = () => {
  const [recentRFQs, setRecentRFQs] = useState([]);
  const [myQuotes, setMyQuotes] = useState([]);
  const [stats, setStats] = useState({
    totalQuotes: 0,
    acceptedQuotes: 0,
    pendingQuotes: 0,
    newRFQs: 0
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      
      // Load recent public RFQs
      const rfqs = await rfqService.getPublicRFQs({ limit: 5 });
      setRecentRFQs(rfqs);
      
      // Load my quotes
      const quotes = await quoteService.getMyQuotes({ limit: 5 });
      setMyQuotes(quotes);
      
      // Calculate stats
      const allQuotes = await quoteService.getMyQuotes();
      const acceptedQuotes = allQuotes.filter(quote => quote.status === 'ACCEPTED');
      const pendingQuotes = allQuotes.filter(quote => quote.status === 'SUBMITTED');
      
      setStats({
        totalQuotes: allQuotes.length,
        acceptedQuotes: acceptedQuotes.length,
        pendingQuotes: pendingQuotes.length,
        newRFQs: rfqs.length
      });
    } catch (error) {
      console.error('Error loading dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <LoadingSpinner message="Loading dashboard..." />;
  }

  return (
    <div className="container">
      <h1>Supplier Dashboard</h1>
      <p style={{ color: '#666', marginBottom: '30px' }}>
        Welcome back! Here are the latest opportunities and your quote status.
      </p>

      {/* Stats Cards */}
      <div className="grid grid-3" style={{ marginBottom: '30px' }}>
        <Card>
          <div style={{ textAlign: 'center' }}>
            <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#007bff' }}>
              {stats.totalQuotes}
            </div>
            <div style={{ color: '#666' }}>Total Quotes</div>
          </div>
        </Card>
        
        <Card>
          <div style={{ textAlign: 'center' }}>
            <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#28a745' }}>
              {stats.acceptedQuotes}
            </div>
            <div style={{ color: '#666' }}>Accepted Quotes</div>
          </div>
        </Card>
        
        <Card>
          <div style={{ textAlign: 'center' }}>
            <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#ffc107' }}>
              {stats.pendingQuotes}
            </div>
            <div style={{ color: '#666' }}>Pending Quotes</div>
          </div>
        </Card>
      </div>

      {/* Quick Actions */}
      <Card title="Quick Actions">
        <div style={{ display: 'flex', gap: '15px', flexWrap: 'wrap' }}>
          <Link to="/browse-rfqs">
            <Button>Browse RFQs</Button>
          </Link>
          <Link to="/my-quotes">
            <Button variant="outline">My Quotes</Button>
          </Link>
          <Link to="/profile">
            <Button variant="outline">Update Profile</Button>
          </Link>
        </div>
      </Card>

      <div className="grid grid-2">
        {/* Latest RFQs */}
        <Card 
          title="Latest RFQs" 
          headerAction={
            <Link to="/browse-rfqs">
              <Button variant="outline">Browse All</Button>
            </Link>
          }
        >
          {recentRFQs.length === 0 ? (
            <div style={{ textAlign: 'center', padding: '20px' }}>
              <p>No new RFQs available.</p>
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '15px' }}>
              {recentRFQs.slice(0, 3).map(rfq => (
                <div 
                  key={rfq.id}
                  style={{ 
                    padding: '15px', 
                    border: '1px solid #eee', 
                    borderRadius: '4px'
                  }}
                >
                  <h4 style={{ margin: '0 0 5px 0' }}>
                    <Link to={`/rfqs/${rfq.id}`} style={{ color: '#007bff', textDecoration: 'none' }}>
                      {rfq.title}
                    </Link>
                  </h4>
                  <div style={{ fontSize: '14px', color: '#666', marginBottom: '10px' }}>
                   {rfq.product_category} • {rfq.quantity} {rfq.unit}
                 </div>
                 <div style={{ fontSize: '12px', color: '#999' }}>
                   Deadline: {format(new Date(rfq.quote_deadline), 'MMM dd, yyyy')}
                 </div>
               </div>
             ))}
           </div>
         )}
       </Card>

       {/* Recent Quotes */}
       <Card 
         title="My Recent Quotes" 
         headerAction={
           <Link to="/my-quotes">
             <Button variant="outline">View All</Button>
           </Link>
         }
       >
         {myQuotes.length === 0 ? (
           <div style={{ textAlign: 'center', padding: '20px' }}>
             <p>No quotes submitted yet.</p>
             <Link to="/browse-rfqs">
               <Button>Find RFQs to Quote</Button>
             </Link>
           </div>
         ) : (
           <div style={{ display: 'flex', flexDirection: 'column', gap: '15px' }}>
             {myQuotes.slice(0, 3).map(quote => (
               <div 
                 key={quote.id}
                 style={{ 
                   padding: '15px', 
                   border: '1px solid #eee', 
                   borderRadius: '4px',
                   display: 'flex',
                   justifyContent: 'space-between',
                   alignItems: 'center'
                 }}
               >
                 <div>
                   <h4 style={{ margin: '0 0 5px 0' }}>
                     <Link to={`/quotes/${quote.id}`} style={{ color: '#007bff', textDecoration: 'none' }}>
                       Quote #{quote.id}
                     </Link>
                   </h4>
                   <div style={{ fontSize: '14px', color: '#666' }}>
                     {quote.currency} {quote.total_price.toLocaleString()}
                   </div>
                 </div>
                 <span className={`status-badge status-${quote.status.toLowerCase()}`}>
                   {quote.status}
                 </span>
               </div>
             ))}
           </div>
         )}
       </Card>
     </div>
   </div>
 );
};

export default Dashboard;
