import { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { ulid } from 'ulid';
import type { Message } from '../types/chat';
import { streamChatResponse } from '../utils/api';
import { ChatMessage } from './ChatMessage';
import { ChatInput } from './ChatInput';
import { PreviewModal } from './PreviewModal';
import { getUserCardType, getCachedUser, fetchCurrentUser } from '../utils/auth';
import './Chat.css';

export function Chat() {
  const navigate = useNavigate();
  const [user, setUser] = useState(getCachedUser());
  const [cardType, setCardType] = useState(getUserCardType());
  const [isCheckingAuth, setIsCheckingAuth] = useState(true);
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [currentAgent, setCurrentAgent] = useState<string>('Sam');
  const [previewData, setPreviewData] = useState<{ isOpen: boolean; data: any; type: string }>({
    isOpen: false,
    data: null,
    type: ''
  });
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const currentMessageRef = useRef<string>('');
  const currentAgentRef = useRef<string>('Sam');
  const sessionIdRef = useRef<string>(ulid());

  const hasPremiumAccess = cardType === 'tribune';

  // Fetch current user on mount if not cached
  useEffect(() => {
    const checkAuth = async () => {
      if (!user) {
        try {
          const fetchedUser = await fetchCurrentUser();
          setUser(fetchedUser);
          setCardType(getUserCardType());
        } catch (error) {
          console.log('User not authenticated');
        }
      }
      setIsCheckingAuth(false);
    };

    checkAuth();
  }, []);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Add initial message from Sam when component mounts
  useEffect(() => {
    if (hasPremiumAccess && !isCheckingAuth) {
      const initialMessage: Message = {
        id: 'initial_sam_message',
        type: 'agent',
        content: `Welcome, ${user?.username || 'Tribune Cardholder'}! I'm Sam, your dedicated Tribune concierge. As a valued Tribune member, you have access to our premium travel planning service. How may I assist with your travel plans today?`,
        agent: 'Sam',
        timestamp: new Date(),
      };
      setMessages([initialMessage]);
    }
  }, [hasPremiumAccess, user, isCheckingAuth]);

  const handleSendMessage = async (content: string) => {
    // Add user message
    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);
    currentMessageRef.current = '';

    try {
      let currentMessageId = Date.now().toString() + '_agent';

      for await (const event of streamChatResponse(content, sessionIdRef.current)) {
        if (event.type === 'agent_transfer') {
          // Add transfer message
          const transferMessage: Message = {
            id: Date.now().toString() + '_transfer',
            type: 'transfer',
            content: event.data.message || '',
            agent: event.data.agent,
            timestamp: new Date(),
          };
          setMessages((prev) => [...prev, transferMessage]);
          const newAgent = event.data.agent || 'Agent';
          setCurrentAgent(newAgent);
          currentAgentRef.current = newAgent;

          // Start new agent message
          currentMessageRef.current = '';
          currentMessageId = Date.now().toString() + '_agent';

        } else if (event.type === 'content') {
          const text = event.data.text || '';
          currentMessageRef.current += text;

          // Update or create agent message
          setMessages((prev) => {
            const existing = prev.find((m) => m.id === currentMessageId);
            if (existing) {
              return prev.map((m) =>
                m.id === currentMessageId
                  ? { ...m, content: currentMessageRef.current }
                  : m
              );
            } else {
              return [
                ...prev,
                {
                  id: currentMessageId,
                  type: 'agent',
                  content: currentMessageRef.current,
                  agent: currentAgentRef.current,
                  timestamp: new Date(),
                },
              ];
            }
          });

        } else if (event.type === 'done') {
          setIsLoading(false);
        } else if (event.type === 'error') {
          console.error('Chat error:', event.data.message);
          setMessages((prev) => [
            ...prev,
            {
              id: Date.now().toString(),
              type: 'agent',
              content: `Error: ${event.data.message}`,
              timestamp: new Date(),
            },
          ]);
          setIsLoading(false);
        }
      }
    } catch (error) {
      console.error('Failed to send message:', error);
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now().toString(),
          type: 'agent',
          content: 'Sorry, there was an error processing your request.',
          timestamp: new Date(),
        },
      ]);
      setIsLoading(false);
    }
  };

  const handlePreviewClick = (data: any, type: string) => {
    setPreviewData({
      isOpen: true,
      data,
      type
    });
  };

  // Show loading state while checking authentication
  if (isCheckingAuth) {
    return (
      <div className="chat-page">
        <div className="auth-loading">
          <div className="loading-spinner"></div>
          <p>Loading...</p>
        </div>
      </div>
    );
  }

  // Render premium access gate for non-Tribune users
  if (!hasPremiumAccess) {
    return (
      <div className="chat-page">
        <div className="premium-gate">
          <div className="gate-icon">💎</div>
          <h1 className="gate-title">Tribune Premium Concierge</h1>
          <p className="gate-subtitle">
            Exclusive AI-powered travel planning available only to Tribune cardholders
          </p>

          <div className="gate-features">
            <h3>Premium Features Include:</h3>
            <ul className="features-list">
              <li>
                <span className="feature-icon">✈️</span>
                <div className="feature-content">
                  <strong>Personalized Travel Planning</strong>
                  <p>AI-powered itinerary creation tailored to your preferences</p>
                </div>
              </li>
              <li>
                <span className="feature-icon">🏨</span>
                <div className="feature-content">
                  <strong>Luxury Accommodation Search</strong>
                  <p>Exclusive access to premium hotels and resorts worldwide</p>
                </div>
              </li>
              <li>
                <span className="feature-icon">🌍</span>
                <div className="feature-content">
                  <strong>Multi-Specialist Team</strong>
                  <p>Dedicated experts for flights, hotels, dining, and attractions</p>
                </div>
              </li>
              <li>
                <span className="feature-icon">💼</span>
                <div className="feature-content">
                  <strong>24/7 Concierge Support</strong>
                  <p>Round-the-clock assistance for all your travel needs</p>
                </div>
              </li>
            </ul>
          </div>

          <div className="gate-actions">
            {!user ? (
              <>
                <button className="gate-button premium" onClick={() => navigate('/login')}>
                  Sign In to Access
                </button>
                <button className="gate-button secondary" onClick={() => navigate('/cards')}>
                  Learn About Tribune Card
                </button>
              </>
            ) : (
              <>
                <p className="gate-message">
                  This premium feature is exclusive to Tribune cardholders.
                  {cardType === 'legionnaire' ? ' Upgrade to Tribune to unlock this benefit.' : ' Apply for a Tribune card to get started.'}
                </p>
                <button className="gate-button premium" onClick={() => navigate('/apply?card=tribune')}>
                  Apply for Tribune Card
                </button>
                <button className="gate-button secondary" onClick={() => navigate('/cards')}>
                  Compare Cards
                </button>
              </>
            )}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={`chat-wrapper ${previewData.isOpen ? 'split-view' : ''}`}>
      <div className="chat-container tribune-premium">
        <div className="chat-header tribune-header">
          <div className="header-content">
            <h1>Tribune Premium Concierge</h1>
            <p className="header-subtitle">
              Your personal travel planning service with {currentAgent}
            </p>
          </div>
          <span className="premium-badge-overlay">TRIBUNE</span>
        </div>

        <div className="messages-container">
          {messages.length === 0 && (
            <div className="welcome-message tribune-welcome">
              <div className="welcome-icon">💎</div>
              <h2>Welcome, Tribune Cardholder</h2>
              <p>
                I'm Sam, your dedicated travel concierge. I coordinate with a team of luxury travel specialists:
              </p>
              <ul className="specialists-list">
                <li>✈️ <strong>Jenny</strong> - Private aviation & first-class flights</li>
                <li>🏨 <strong>Marcus</strong> - Luxury estates & exclusive hotels</li>
                <li>🗺️ <strong>Sofia</strong> - Bespoke itineraries & VIP experiences</li>
                <li>🍽️ <strong>Luca</strong> - Michelin-starred dining reservations</li>
                <li>💰 <strong>Alex</strong> - Premium rewards optimization</li>
              </ul>
              <p className="premium-tagline">Where would you like to go?</p>
            </div>
          )}

          {messages.map((message) => (
            <ChatMessage
              key={message.id}
              message={message}
              onPreviewClick={handlePreviewClick}
            />
          ))}

          {isLoading && (
            <div className="typing-indicator tribune-typing">
              <span></span>
              <span></span>
              <span></span>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        <ChatInput onSendMessage={handleSendMessage} disabled={isLoading} />
      </div>

      <PreviewModal
        isOpen={previewData.isOpen}
        onClose={() => setPreviewData({ isOpen: false, data: null, type: '' })}
        data={previewData.data}
        type={previewData.type}
      />
    </div>
  );
}
