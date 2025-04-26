import React, { lazy, Suspense } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';

const LandingPage = lazy(() => import('./components/LandingPage'));
const ArchonDashboard = lazy(() => import('./components/ArchonDashboard'));
const AgentTestPage = lazy(() => import('./pages/AgentTestPage'));

function App() {
  return (
    <BrowserRouter>
      <Suspense fallback={<div>Loading...</div>}>
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/dashboard" element={<ArchonDashboard />} />
          <Route path="/agent-test" element={<AgentTestPage />} />
          {/* Add other routes as needed */}
        </Routes>
      </Suspense>
    </BrowserRouter>
  );
}

export default App;
