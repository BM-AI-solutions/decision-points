import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import ArchonDashboard from './components/ArchonDashboard';
import LandingPage from './components/LandingPage';
import AgentTestPage from './pages/AgentTestPage';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/dashboard" element={<ArchonDashboard />} />
        <Route path="/agent-test" element={<AgentTestPage />} />
        {/* Add other routes as needed */}
      </Routes>
    </BrowserRouter>
  );
}

export default App;