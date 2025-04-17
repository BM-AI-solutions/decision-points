import React from 'react';
import Header from './Header';
import Footer from './Footer';

const MarketingLayout = ({ children }) => (
  <>
    <Header />
    {children}
    <Footer />
  </>
);

export default MarketingLayout;