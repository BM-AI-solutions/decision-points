import React from 'react';
import Hero from './Hero';
import Features from './Features';
import HowItWorks from './HowItWorks';
import DashboardPreview from './DashboardPreview';
import Pricing from './Pricing';
import AppSection from './AppSection';
import Footer from './Footer';
import Header from './Header'; // Assuming a Header component exists or will be created

function LandingPage() {
  return (
    <>
      <Header />
      <Hero />
      <Features />
      <HowItWorks />
      <DashboardPreview />
      <Pricing />
      <AppSection />
      <Footer />
    </>
  );
}

export default LandingPage;
