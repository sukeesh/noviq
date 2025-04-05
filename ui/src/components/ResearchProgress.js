import React from 'react';
import styled, { keyframes, css } from 'styled-components';
import { FaCheck, FaSpinner, FaSearch, FaLink, FaArrowRight, FaBookmark } from 'react-icons/fa';

const fadeIn = keyframes`
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
`;

const pulse = keyframes`
  0% { transform: scale(1); }
  50% { transform: scale(1.05); }
  100% { transform: scale(1); }
`;

const spin = keyframes`
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
`;

const slideIn = keyframes`
  from { transform: translateX(-20px); opacity: 0; }
  to { transform: translateX(0); opacity: 1; }
`;

// Styled components for spinning icons
const SpinnerIcon = styled(FaSpinner)`
  animation: ${spin} 1s linear infinite;
`;

const SmallSpinnerIcon = styled(SpinnerIcon)`
  font-size: 10px;
  margin-right: 0.25rem;
`;

const ProgressContainer = styled.div`
  background-color: var(--secondary-bg);
  border-radius: 8px;
  padding: 1.2rem;
  margin-bottom: 1rem;
  animation: ${fadeIn} 0.4s ease-out;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
`;

const ProgressTitle = styled.h3`
  margin-top: 0;
  margin-bottom: 1.2rem;
  display: flex;
  align-items: center;
  color: var(--text-light);
  font-size: 1.2rem;
  
  svg {
    margin-right: 0.75rem;
    color: var(--primary-color);
  }
`;

const ProgressHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
`;

const ProgressSummary = styled.div`
  background-color: rgba(58, 134, 255, 0.1);
  padding: 0.5rem 0.75rem;
  border-radius: 4px;
  font-size: 0.9rem;
  color: var(--primary-color);
  display: flex;
  align-items: center;
  
  svg {
    margin-right: 0.5rem;
  }
`;

const StepsList = styled.ul`
  list-style: none;
  padding: 0;
  margin: 0;
  position: relative;
  
  &::before {
    content: '';
    position: absolute;
    top: 0;
    bottom: 0;
    left: 12px;
    width: 2px;
    background-color: var(--border-color);
    z-index: 0;
  }
`;

const Step = styled.li`
  padding: 0.75rem 1rem 0.75rem 2.5rem;
  margin-bottom: 0.5rem;
  border-radius: 4px;
  display: flex;
  align-items: flex-start;
  position: relative;
  background-color: ${props => props.active ? 'var(--highlight-bg)' : 'transparent'};
  border-left: 3px solid ${props => {
    if (props.completed) return 'var(--success-color)';
    if (props.active) return 'var(--primary-color)';
    return 'var(--border-color)';
  }};
  transition: all 0.3s ease;
  animation: ${props => props.active ? fadeIn : 'none'} 0.3s ease-out;
  
  &:hover {
    background-color: ${props => props.active ? 'var(--highlight-bg)' : 'rgba(255, 255, 255, 0.05)'};
  }
  
  &:last-child {
    margin-bottom: 0;
  }
`;

const StepIcon = styled.div`
  position: absolute;
  left: -12px;
  top: 0.9rem;
  width: 24px;
  height: 24px;
  background-color: var(--secondary-bg);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1;
  color: ${props => {
    if (props.completed) return 'var(--success-color)';
    if (props.active) return 'var(--primary-color)';
    return 'var(--text-secondary)';
  }};
  
  ${props => props.active && css`
    animation: ${pulse} 2s infinite ease-in-out;
  `}
`;

const StepContent = styled.div`
  flex: 1;
`;

const StepText = styled.div`
  margin-bottom: ${props => props.hasResults ? '0.5rem' : '0'};
  color: ${props => props.completed ? 'var(--text-secondary)' : 'var(--text-light)'};
  font-weight: ${props => props.active ? '500' : 'normal'};
  text-decoration: ${props => props.completed ? 'line-through' : 'none'};
`;

const StepProgress = styled.div`
  display: flex;
  align-items: center;
  font-size: 0.8rem;
  color: var(--primary-color);
  margin-top: 0.25rem;
`;

const SearchResultsContainer = styled.div`
  margin-top: 0.75rem;
  padding-left: 0.5rem;
  border-left: 1px dashed var(--border-color);
`;

const SearchResult = styled.div`
  font-size: 0.9rem;
  padding: 0.5rem;
  margin-bottom: 0.3rem;
  background-color: rgba(0, 0, 0, 0.2);
  border-radius: 4px;
  display: flex;
  align-items: center;
  transition: all 0.2s ease;
  animation: ${slideIn} 0.3s ease-out;
  animation-delay: ${props => `${props.index * 0.1}s`};
  
  &:hover {
    background-color: rgba(0, 0, 0, 0.3);
    transform: translateX(3px);
  }
  
  svg {
    margin-right: 0.5rem;
    min-width: 16px;
    color: var(--primary-color);
  }
  
  a {
    text-decoration: none;
    color: var(--text-light);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    
    &:hover {
      text-decoration: underline;
    }
  }
`;

const ProgressIndicator = styled.div`
  height: 4px;
  background-color: var(--border-color);
  border-radius: 2px;
  margin-top: 1rem;
  overflow: hidden;
  position: relative;
  
  &::after {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    height: 100%;
    width: ${props => `${props.progress}%`};
    background-color: var(--primary-color);
    border-radius: 2px;
    transition: width 0.5s ease;
  }
`;

const ResultsCount = styled.div`
  margin-top: 0.5rem;
  font-size: 0.8rem;
  color: var(--text-secondary);
  display: flex;
  align-items: center;
  
  svg {
    margin-right: 0.4rem;
    color: var(--primary-color);
  }
`;

function ResearchProgress({ plan, currentStep, searchResults }) {
  // Get a flat array of all search result URLs
  const allResultUrls = Object.values(searchResults).flatMap(results => 
    results.map(result => result.url)
  );
  
  // Calculate progress percentage
  const currentStepIndex = plan.indexOf(currentStep);
  const progressPercentage = plan.length > 0 
    ? Math.max(5, Math.min(100, Math.round((currentStepIndex / plan.length) * 100))) 
    : 5;
  
  // Count all results
  const totalResults = Object.values(searchResults).reduce((count, results) => count + results.length, 0);
  
  return (
    <ProgressContainer>
      <ProgressHeader>
        <ProgressTitle>
          <FaSearch /> Research Progress
        </ProgressTitle>
        
        <ProgressSummary>
          <FaBookmark />
          {currentStepIndex >= 0 ? `Step ${currentStepIndex + 1} of ${plan.length}` : 'Preparing research...'}
        </ProgressSummary>
      </ProgressHeader>
      
      <StepsList>
        {plan.map((step, index) => {
          const isActive = currentStep === step;
          const isCompleted = !isActive && allResultUrls.length > 0 && index < currentStepIndex;
          
          // Check if this step has any search results
          const stepHasResults = Object.keys(searchResults).some(query => 
            // Simplified check - in a real app, you'd track which queries belong to which steps
            query.toLowerCase().includes(step.toLowerCase().split(' ').slice(0, 3).join(' '))
          );
          
          // Get results that might be related to this step
          const relevantResults = Object.entries(searchResults)
            .filter(([query]) => query.toLowerCase().includes(step.toLowerCase().split(' ').slice(0, 3).join(' ')))
            .flatMap(([_, results]) => results);
          
          return (
            <Step 
              key={index} 
              active={isActive} 
              completed={isCompleted}
            >
              <StepIcon active={isActive} completed={isCompleted}>
                {isCompleted ? (
                  <FaCheck />
                ) : isActive ? (
                  <SmallSpinnerIcon />
                ) : (
                  <span>{index + 1}</span>
                )}
              </StepIcon>
              
              <StepContent>
                <StepText 
                  hasResults={relevantResults.length > 0} 
                  active={isActive}
                  completed={isCompleted}
                >
                  {step}
                </StepText>
                
                {isActive && (
                  <StepProgress>
                    <SmallSpinnerIcon /> Researching...
                  </StepProgress>
                )}
                
                {relevantResults.length > 0 && (
                  <>
                    <SearchResultsContainer>
                      {relevantResults.slice(0, 3).map((result, rIndex) => (
                        <SearchResult key={rIndex} index={rIndex}>
                          <FaLink />
                          <a href={result.url} target="_blank" rel="noopener noreferrer" title={result.title}>
                            {result.title}
                          </a>
                        </SearchResult>
                      ))}
                      
                      {relevantResults.length > 3 && (
                        <ResultsCount>
                          <FaArrowRight size={10} />
                          {relevantResults.length - 3} more results found
                        </ResultsCount>
                      )}
                    </SearchResultsContainer>
                  </>
                )}
              </StepContent>
            </Step>
          );
        })}
      </StepsList>
      
      <ProgressIndicator progress={progressPercentage} />
      
      {totalResults > 0 && (
        <ResultsCount>
          <FaBookmark />
          Found {totalResults} relevant sources so far
        </ResultsCount>
      )}
    </ProgressContainer>
  );
}

export default ResearchProgress; 