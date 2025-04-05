import React from 'react';
import styled from 'styled-components';
import { BrowserRouter as Router, Route, Routes, Navigate } from 'react-router-dom';
import ResearchInterface from './components/ResearchInterface';
import Header from './components/Header';

const AppContainer = styled.div`
  display: flex;
  flex-direction: column;
  height: 100vh;
  overflow: hidden;
  background-color: var(--bg-dark);
`;

const ContentContainer = styled.div`
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
`;

function App() {
  return (
    <Router>
      <AppContainer>
        <Header />
        <ContentContainer>
          <Routes>
            <Route path="/research" element={<ResearchInterface />} />
            <Route path="*" element={<Navigate to="/research" replace />} />
          </Routes>
        </ContentContainer>
      </AppContainer>
    </Router>
  );
}

export default App; 