import React, { useState, useEffect, useRef } from 'react';
import styled, { keyframes, css } from 'styled-components';
import axios from 'axios';
import { FaSearch, FaPaperPlane, FaSpinner, FaExternalLinkAlt, FaBrain, FaCheck, FaRobot } from 'react-icons/fa';
import ModelSelector from './ModelSelector';
import ResearchProgress from './ResearchProgress';

// Animations
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

const shimmer = keyframes`
  0% { background-position: -200% 0; }
  100% { background-position: 200% 0; }
`;

// Reusable animation styles
const spinAnimation = css`
  animation: ${spin} 1s linear infinite;
`;

// Styled components for spinning icons
const SpinnerIcon = styled(FaSpinner)`
  animation: ${spin} 1s linear infinite;
`;

const ButtonSpinner = styled(SpinnerIcon)`
  margin-right: 0.5rem;
`;

const Container = styled.div`
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;
`;

const ChatContainer = styled.div`
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 1rem;
  overflow-y: auto;
  scroll-behavior: smooth;
`;

const Message = styled.div`
  margin-bottom: 1.5rem;
  max-width: 90%;
  animation: ${fadeIn} 0.3s ease-out;
  
  ${props => props.isUser ? css`
    align-self: flex-end;
    text-align: right;
  ` : css`
    align-self: flex-start;
  `}
`;

const MessageContent = styled.div`
  background-color: ${props => props.isUser ? 'var(--primary-color)' : 'var(--secondary-bg)'};
  color: var(--text-light);
  padding: 0.8rem 1.2rem;
  border-radius: 1rem;
  display: inline-block;
  text-align: left;
  margin-top: 0.5rem;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
  transition: all 0.2s ease;
  
  &:hover {
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
  }
`;

const InputContainer = styled.div`
  display: flex;
  padding: 1rem;
  border-top: 1px solid var(--border-color);
  background-color: var(--bg-dark);
`;

const InputWrapper = styled.div`
  flex: 1;
  display: flex;
  background-color: var(--secondary-bg);
  border-radius: 1.5rem;
  overflow: hidden;
  padding: 0.5rem 1rem;
  align-items: center;
  transition: box-shadow 0.3s ease;
  
  &:focus-within {
    box-shadow: 0 0 0 2px var(--primary-color);
  }
`;

const Input = styled.input`
  flex: 1;
  background: none;
  border: none;
  color: var(--text-light);
  font-size: 1rem;
  padding: 0.5rem;
  
  &:focus {
    outline: none;
  }
`;

const SendButton = styled.button`
  background: none;
  border: none;
  color: var(--primary-color);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0.5rem;
  border-radius: 50%;
  margin-left: 0.5rem;
  transition: all 0.2s ease;
  
  &:disabled {
    color: var(--text-secondary);
    cursor: not-allowed;
  }
  
  &:hover:not(:disabled) {
    background-color: rgba(58, 134, 255, 0.1);
    transform: scale(1.1);
  }
  
  .spinning {
    animation: ${spin} 1s linear infinite;
  }
`;

const LoadingContainer = styled.div`
  display: flex;
  padding: 3rem;
  justify-content: center;
  align-items: center;
  flex-direction: column;
  height: 60vh;
`;

const LoadingSpinner = styled(FaSpinner)`
  animation: ${spin} 1s linear infinite;
  font-size: 2.5rem;
  margin-bottom: 1.5rem;
  color: var(--primary-color);
`;

const LoadingText = styled.p`
  font-size: 1.2rem;
  color: var(--text-light);
  margin-top: 1rem;
  animation: ${pulse} 1.5s infinite ease-in-out;
  text-align: center;
`;

const LoadingProgress = styled.div`
  width: 60%;
  max-width: 400px;
  height: 6px;
  background-color: var(--secondary-bg);
  border-radius: 3px;
  margin-top: 1.5rem;
  overflow: hidden;
  position: relative;
  
  &::after {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    height: 100%;
    width: 30%;
    background: linear-gradient(90deg, var(--secondary-bg), var(--primary-color), var(--secondary-bg));
    background-size: 200% 100%;
    animation: ${shimmer} 2s infinite;
  }
`;

const StepIndicator = styled.div`
  margin-top: 1rem;
  font-size: 0.9rem;
  color: var(--text-secondary);
  display: flex;
  align-items: center;
  justify-content: center;
  
  svg {
    margin-right: 0.5rem;
  }
`;

const ActionButton = styled.button`
  display: flex;
  align-items: center;
  background: var(--secondary-bg);
  border: 1px solid var(--border-color);
  color: var(--text-light);
  padding: 0.5rem 1rem;
  border-radius: 4px;
  margin-right: 0.5rem;
  cursor: pointer;
  transition: all 0.2s ease;
  
  &:hover {
    background: var(--highlight-bg);
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  }
  
  svg {
    margin-right: 0.5rem;
  }
`;

const ActionBar = styled.div`
  display: flex;
  margin-top: 0.5rem;
`;

const InitialView = styled.div`
  text-align: center;
  margin-top: 4rem;
  padding: 2rem;
  animation: ${fadeIn} 0.5s ease-out;
  
  h1 {
    margin-bottom: 0.5rem;
    color: var(--text-light);
    font-size: 2.5rem;
  }
  
  h2 {
    margin-bottom: 1rem;
    color: var(--text-light);
  }
  
  p {
    margin-bottom: 2rem;
    color: var(--text-secondary);
  }
`;

const LogoIcon = styled(FaRobot)`
  font-size: 3rem;
  margin-bottom: 1.5rem;
  color: var(--primary-color);
`;

const ProgressStatus = styled.div`
  padding: 0.75rem 1rem;
  background-color: var(--highlight-bg);
  border-radius: 8px;
  margin-bottom: 1rem;
  display: flex;
  align-items: center;
  animation: ${fadeIn} 0.3s ease-out;
  
  svg {
    margin-right: 0.75rem;
    color: var(--primary-color);
  }
`;

const QuestionForm = styled.div`
  animation: ${fadeIn} 0.3s ease-out;
`;

function ResearchInterface() {
  const [isInitializing, setIsInitializing] = useState(true);
  const [models, setModels] = useState([]);
  const [selectedModel, setSelectedModel] = useState('');
  const [userIntent, setUserIntent] = useState('');
  const [messages, setMessages] = useState([]);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const [currentStage, setCurrentStage] = useState('init'); // init, questions, answering, researching, complete
  const [questions, setQuestions] = useState([]);
  const [answers, setAnswers] = useState({});
  const [searchResults, setSearchResults] = useState({});
  const [researching, setResearching] = useState(false);
  const [researchPlan, setResearchPlan] = useState([]);
  const [currentStep, setCurrentStep] = useState(null);
  const [reportUrl, setReportUrl] = useState(null);
  const [wsConnection, setWsConnection] = useState(null);
  const [statusMessage, setStatusMessage] = useState('');
  const [loadingPhase, setLoadingPhase] = useState('connecting');
  
  const messagesEndRef = useRef(null);
  const chatContainerRef = useRef(null);

  useEffect(() => {
    // Load available models on component mount
    const loadModels = async () => {
      setLoadingPhase('connecting');
      try {
        const response = await axios.get('/models');
        setModels(response.data.models);
        if (response.data.models.length > 0) {
          setSelectedModel(response.data.models[0]);
        }
        setIsInitializing(false);
      } catch (error) {
        console.error('Failed to load models:', error);
        setMessages([
          ...messages,
          { content: 'Failed to connect to the server. Please check if the backend is running.', isUser: false }
        ]);
        setIsInitializing(false);
      }
    };
    
    loadModels();
  }, []);

  useEffect(() => {
    // Scroll to bottom when messages change
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages]);

  const handleModelSelect = (model) => {
    setSelectedModel(model);
  };
  
  const handleInputChange = (e) => {
    setUserIntent(e.target.value);
  };
  
  const handleSubmit = async () => {
    if (!userIntent.trim() || isSubmitting) return;
    
    setIsSubmitting(true);
    setStatusMessage('Initializing research session...');
    
    // Add user message
    setMessages([...messages, { content: userIntent, isUser: true }]);
    
    try {
      // Create a new session
      const response = await axios.post('/sessions', {
        intent: userIntent,
        model_name: selectedModel
      });
      
      const newSessionId = response.data.session_id;
      setSessionId(newSessionId);
      
      // Connect to WebSocket for real-time updates
      connectWebSocket(newSessionId);
      
      setStatusMessage('Generating clarifying questions...');
      
      // Get clarifying questions
      const questionsResponse = await axios.get(`/sessions/${newSessionId}/questions`);
      
      const clarifyingQuestions = questionsResponse.data.questions;
      setQuestions(clarifyingQuestions);
      
      // Initialize answers object
      const initialAnswers = {};
      clarifyingQuestions.forEach(q => initialAnswers[q] = '');
      setAnswers(initialAnswers);
      
      // Add questions as a message
      setMessages([
        ...messages,
        { content: userIntent, isUser: true },
        { 
          content: 'To help with your research, I have a few questions:',
          questions: clarifyingQuestions,
          isUser: false
        }
      ]);
      
      setCurrentStage('questions');
      setStatusMessage('');
    } catch (error) {
      console.error('Error starting research:', error);
      setMessages([
        ...messages,
        { content: userIntent, isUser: true },
        { content: 'Sorry, there was an error starting the research. Please try again.', isUser: false }
      ]);
      setStatusMessage('');
    } finally {
      setUserIntent('');
      setIsSubmitting(false);
    }
  };
  
  const handleAnswerChange = (question, answer) => {
    setAnswers({
      ...answers,
      [question]: answer
    });
  };
  
  const handleAnswersSubmit = async () => {
    if (Object.values(answers).some(a => !a.trim()) || isSubmitting) return;
    
    setIsSubmitting(true);
    setStatusMessage('Processing your answers...');
    
    try {
      // Format answers for the API
      const qaArray = Object.entries(answers).map(([question, answer]) => ({
        question,
        answer
      }));
      
      // Submit answers
      await axios.post(`/sessions/${sessionId}/answers`, {
        qa_pairs: qaArray,
        session_id: sessionId
      });
      
      setStatusMessage('Generating research plan...');
      
      // Get research plan
      const planResponse = await axios.get(`/sessions/${sessionId}/plan`);
      const plan = planResponse.data.plan;
      setResearchPlan(plan);
      
      // Add plan as a message
      setMessages([
        ...messages,
        { 
          content: 'Thanks for your answers. Here\'s my research plan:',
          plan,
          isUser: false
        }
      ]);
      
      setCurrentStage('researching');
      setResearching(true);
      setStatusMessage('Beginning research...');
      
    } catch (error) {
      console.error('Error submitting answers:', error);
      setMessages([
        ...messages,
        { content: 'Sorry, there was an error processing your answers. Please try again.', isUser: false }
      ]);
      setStatusMessage('');
    } finally {
      setIsSubmitting(false);
    }
  };
  
  const connectWebSocket = (sid) => {
    // Close existing connection if any
    if (wsConnection) {
      wsConnection.close();
    }
    
    // Create new WebSocket connection
    const ws = new WebSocket(`ws://${window.location.hostname}:8001/ws/${sid}`);
    
    ws.onopen = () => {
      console.log('WebSocket connected');
      setStatusMessage('Research session connected');
    };
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      handleWebSocketMessage(data);
    };
    
    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      setStatusMessage('Connection error. Research may be delayed.');
    };
    
    ws.onclose = () => {
      console.log('WebSocket disconnected');
    };
    
    setWsConnection(ws);
  };
  
  const handleWebSocketMessage = (data) => {
    console.log('WS message:', data);
    
    switch (data.type) {
      case 'status_update':
        handleStatusUpdate(data);
        break;
      case 'plan_generated':
        setResearchPlan(data.plan);
        setStatusMessage('Research plan generated. Beginning execution...');
        break;
      case 'step_started':
        setCurrentStep(data.step);
        setStatusMessage(`Working on: ${data.step}`);
        break;
      case 'executing_search':
        setStatusMessage(`Searching for: "${data.query}"`);
        break;
      case 'processing_url':
        setStatusMessage(`Analyzing: ${data.title}`);
        break;
      case 'queries_generated':
        setStatusMessage(`Created search queries for current step`);
        break;
      case 'search_results':
        // Update search results for the query
        setSearchResults(prev => ({
          ...prev,
          [data.query]: data.results
        }));
        setStatusMessage(`Found ${data.results.length} results for "${data.query}"`);
        break;
      case 'step_completed':
        setStatusMessage(`Completed research step ${data.step_index + 1}`);
        break;
      case 'generating_report':
        setStatusMessage('Generating final research report...');
        break;
      case 'report_generated':
        setReportUrl(`/${data.filename}`);
        setCurrentStage('complete');
        setResearching(false);
        setStatusMessage('Research completed successfully!');
        
        // Add completion message
        setMessages(prev => [
          ...prev,
          { 
            content: 'I\'ve completed the research and generated a report.',
            reportUrl: `/${data.filename}`,
            isUser: false
          }
        ]);
        break;
      case 'error':
        // Only display errors to the user if we're actively researching
        // This prevents transient errors during setup from showing to the user
        if (currentStage === 'researching') {
          setResearching(false);
          setStatusMessage('Error during research');
          
          // Don't display certain error messages that are part of normal flow
          const normalErrorMessages = [
            "User intent and QA pairs must be set before generating a research plan",
            "Please answer the clarifying questions"
          ];
          
          // Only display the error if it's not a normal flow message
          if (!normalErrorMessages.some(msg => data.message.includes(msg))) {
            setMessages(prev => [
              ...prev,
              { content: `Error during research: ${data.message}`, isUser: false }
            ]);
          }
        } else {
          console.log('Ignoring error during setup:', data.message);
        }
        break;
      default:
        // Handle other message types
        break;
    }
  };
  
  const handleStatusUpdate = (data) => {
    if (data.status === 'completed') {
      setCurrentStage('complete');
      setResearching(false);
      setStatusMessage('Research completed!');
    } else if (data.status === 'generating_report') {
      setStatusMessage('Generating final research report...');
    } else if (data.status.includes('generating_queries')) {
      setStatusMessage('Generating search queries...');
    } else if (data.status === 'generating_plan') {
      setStatusMessage('Creating research plan...');
    }
  };
  
  const openReport = () => {
    if (reportUrl) {
      window.open(reportUrl, '_blank');
    }
  };
  
  if (isInitializing) {
    return (
      <LoadingContainer>
        <LoadingSpinner />
        <LoadingText>Connecting to Noviq Research Engine</LoadingText>
        <LoadingProgress />
        <StepIndicator>
          <FaBrain /> Initializing AI Research Assistant
        </StepIndicator>
      </LoadingContainer>
    );
  }

  return (
    <Container>
      {models.length === 0 ? (
        <div style={{ padding: '2rem', textAlign: 'center' }}>
          <p>No models found. Please make sure Ollama is running with at least one model installed.</p>
        </div>
      ) : (
        <>
          <ChatContainer ref={chatContainerRef}>
            {messages.length === 0 ? (
              <InitialView>
                <LogoIcon />
                <h1>Noviq</h1>
                <h2>AI-Powered Research Assistant</h2>
                <p>Start by selecting a model and entering your research topic.</p>
                <ModelSelector 
                  models={models} 
                  selectedModel={selectedModel} 
                  onSelect={handleModelSelect} 
                />
              </InitialView>
            ) : (
              <>
                {messages.map((message, index) => (
                  <Message key={index} isUser={message.isUser}>
                    <MessageContent isUser={message.isUser}>
                      {message.content}
                      
                      {message.questions && (
                        <QuestionForm style={{ marginTop: '1rem' }}>
                          {message.questions.map((question, qIndex) => (
                            <div key={qIndex} style={{ marginBottom: '1rem' }}>
                              <div>{question}</div>
                              <input 
                                type="text" 
                                value={answers[question] || ''} 
                                onChange={(e) => handleAnswerChange(question, e.target.value)}
                                style={{
                                  width: '100%',
                                  padding: '0.5rem',
                                  marginTop: '0.5rem',
                                  backgroundColor: 'var(--highlight-bg)',
                                  border: '1px solid var(--border-color)',
                                  borderRadius: '4px',
                                  color: 'var(--text-light)'
                                }}
                                placeholder="Your answer..."
                              />
                            </div>
                          ))}
                          <button 
                            onClick={handleAnswersSubmit}
                            style={{
                              padding: '0.5rem 1rem',
                              backgroundColor: 'var(--primary-color)',
                              color: 'white',
                              border: 'none',
                              borderRadius: '4px',
                              cursor: 'pointer',
                              marginTop: '0.5rem',
                              transition: 'all 0.2s ease'
                            }}
                            onMouseOver={(e) => {
                              e.currentTarget.style.transform = 'translateY(-2px)';
                              e.currentTarget.style.boxShadow = '0 4px 8px rgba(0, 0, 0, 0.2)';
                            }}
                            onMouseOut={(e) => {
                              e.currentTarget.style.transform = 'translateY(0)';
                              e.currentTarget.style.boxShadow = 'none';
                            }}
                            disabled={isSubmitting || Object.values(answers).some(a => !a.trim())}
                          >
                            {isSubmitting ? (
                              <>
                                <ButtonSpinner />
                                Processing...
                              </>
                            ) : 'Submit Answers'}
                          </button>
                        </QuestionForm>
                      )}
                      
                      {message.plan && (
                        <div style={{ marginTop: '1rem' }}>
                          <ol>
                            {message.plan.map((step, stepIndex) => (
                              <li key={stepIndex} style={{ 
                                marginBottom: '0.5rem', 
                                padding: '0.5rem',
                                borderRadius: '4px',
                                transition: 'background-color 0.3s ease',
                                backgroundColor: currentStep === step ? 'rgba(58, 134, 255, 0.1)' : 'transparent'
                              }}>{step}</li>
                            ))}
                          </ol>
                        </div>
                      )}
                      
                      {message.reportUrl && (
                        <ActionBar>
                          <ActionButton onClick={openReport}>
                            <FaExternalLinkAlt /> Open Report
                          </ActionButton>
                          <ActionButton onClick={() => window.location.reload()}>
                            <FaSearch /> New Research
                          </ActionButton>
                        </ActionBar>
                      )}
                    </MessageContent>
                  </Message>
                ))}
                
                {statusMessage && (
                  <ProgressStatus>
                    <ButtonSpinner />
                    <div>{statusMessage}</div>
                  </ProgressStatus>
                )}
                
                {researching && (
                  <div style={{ padding: '1rem' }}>
                    <ResearchProgress 
                      plan={researchPlan} 
                      currentStep={currentStep}
                      searchResults={searchResults}
                    />
                  </div>
                )}
                
                <div ref={messagesEndRef} />
              </>
            )}
          </ChatContainer>
          
          <InputContainer>
            <InputWrapper>
              <Input 
                type="text" 
                value={userIntent} 
                onChange={handleInputChange}
                placeholder={messages.length === 0 ? "What would you like to research?" : "Ask a follow-up question..."}
                disabled={currentStage !== 'init' && currentStage !== 'complete'}
                onKeyPress={(e) => e.key === 'Enter' && handleSubmit()}
              />
            </InputWrapper>
            <SendButton 
              onClick={handleSubmit}
              disabled={!userIntent.trim() || isSubmitting || (currentStage !== 'init' && currentStage !== 'complete')}
              title={
                currentStage !== 'init' && currentStage !== 'complete' 
                  ? "Please wait until the current research is complete" 
                  : "Send"
              }
            >
              {isSubmitting ? <ButtonSpinner /> : <FaPaperPlane />}
            </SendButton>
          </InputContainer>
        </>
      )}
    </Container>
  );
}

export default ResearchInterface; 