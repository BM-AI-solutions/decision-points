import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Hero from './components/Hero';
import Features from './components/Features';
import HowItWorks from './components/HowItWorks';
import DashboardPreview from './components/DashboardPreview';
import Dashboard from './components/Dashboard';
import Pricing from './components/Pricing';
import AppSection from './components/AppSection';
import Testimonials from './components/Testimonials';
import ArchonDashboard from './components/ArchonDashboard';
import AnalyticsPage from './components/AnalyticsPage';
import AutomationPage from './components/AutomationPage';
import InsightsPage from './components/InsightsPage';
import CustomersPage from './components/CustomersPage';
import RevenuePage from './components/RevenuePage';
import MarketingLayout from './components/MarketingLayout';
import DashboardLayout from './components/DashboardLayout';

function LandingPage() {
  return (
    <>
      <Hero />
      <Features />
      <HowItWorks />
      <DashboardPreview />
      <Pricing />
      <AppSection />
      <Testimonials />
    </>
  );
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route
          path="/"
          element={
            <MarketingLayout>
              <LandingPage />
            </MarketingLayout>
          }
        />
        {/* Dashboard Routes with Layout */}
        <Route path="/dashboard" element={<DashboardLayout />}>
          {/* Index route for the main dashboard content */}
          <Route index element={<Dashboard />} />
          {/* Nested routes for dashboard sections */}
          <Route path="analytics" element={<AnalyticsPage />} />
          <Route path="automation" element={<AutomationPage />} />
          <Route path="insights" element={<InsightsPage />} />
          <Route path="customers" element={<CustomersPage />} />
          <Route path="revenue" element={<RevenuePage />} />
        </Route>
      </Routes>
      {/* Modals */}
      <div id="login-modal" className="modal">
        <div className="modal-content">
          <div className="modal-header">
            <h3>Log In to Decision Points AI</h3>
            <span className="close-modal">&times;</span>
          </div>
          <div className="modal-body">
            <form className="auth-form">
              <div className="input-group">
                <label htmlFor="email">Email</label>
                <input type="email" id="email" className="form-input" placeholder="your@email.com" />
              </div>
              <div className="input-group">
                <label htmlFor="password">Password</label>
                <input type="password" id="password" className="form-input" placeholder="••••••••••" />
              </div>
              <button type="submit" className="btn btn-primary btn-full">Log In</button>
              <div className="auth-divider">
                <span>or continue with</span>
              </div>
              <div id="google-signin-button-container" className="google-btn-container"></div>
            </form>
          </div>
        </div>
      </div>
      <div id="app-modal" className="modal">
        <div className="modal-content">
          <div className="modal-header">
            <h3>Decision Points AI</h3>
            <span className="close-modal">&times;</span>
          </div>
          <div className="modal-body">
            {/* Dynamic content will be added here */}
            Dynamic content will be added here
          </div>
        </div>
      </div>
    </BrowserRouter>
  );
}

export default App;