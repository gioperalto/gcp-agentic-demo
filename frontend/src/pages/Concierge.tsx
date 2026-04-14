import { useState, useRef, useEffect, useCallback } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { datadogRum } from '@datadog/browser-rum';
import { ulid } from 'ulid';
import type { Message } from '../types/chat';
import { streamChatResponse, streamLegionnaireChatResponse, streamInsecureChatResponse } from '../utils/api';
import { useInsecureProfileAgent, useRalphAgent } from '../feature_flags';
import { ChatMessage } from '../components/ChatMessage';
import { ChatInput } from '../components/ChatInput';
import { PreviewModal } from '../components/PreviewModal';
import { getUserCardType, getCachedUser, fetchCurrentUser } from '../utils/auth';
import { useVoiceMode } from '../hooks/useVoiceMode';
import './Concierge.css';

export function Concierge() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const tierParam = searchParams.get('tier'); // 'tribune' or 'legionnaire'

  const [user, setUser] = useState(getCachedUser());
  const [cardType, setCardType] = useState(getUserCardType());
  const [isCheckingAuth, setIsCheckingAuth] = useState(true);
  const [selectedTier, setSelectedTier] = useState<'tribune' | 'legionnaire' | 'debug' | null>(null);
  const debugAgentEnabled = useInsecureProfileAgent();
  const ralphAgentEnabled = useRalphAgent();
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [currentAgent, setCurrentAgent] = useState<string>('Sam');
  const [previewData, setPreviewData] = useState<{ isOpen: boolean; data: unknown; type: string }>({
    isOpen: false,
    data: null,
    type: ''
  });
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const currentMessageRef = useRef<string>('');
  const currentAgentRef = useRef<string>('Sam');
  const sessionIdFallbackRef = useRef<string>(ulid());

  const getSessionId = useCallback(() => {
    // RUM is initialized in main.tsx before the app mounts. Keep a ULID only as
    // a last-resort fallback for local/dev runs where RUM is disabled or context
    // is temporarily unavailable.
    return datadogRum.getInternalContext()?.session_id ?? sessionIdFallbackRef.current;
  }, []);

  // Track whether voice has been activated this session (for TTS on transfers)
  const hasUsedVoiceRef = useRef(false);

  // Voice message ID refs for streaming updates
  const voiceAgentMsgIdRef = useRef<string | null>(null);
  const voiceUserMsgIdRef = useRef<string | null>(null);

  // Voice mode callbacks — create/update messages in real-time (same pattern as text chat streaming)
  const handleVoiceAgentTranscript = useCallback((text: string, isFinal: boolean) => {
    if (!text) return;

    const isNew = !voiceAgentMsgIdRef.current;
    if (isNew) {
      voiceAgentMsgIdRef.current = Date.now().toString() + '_voice_agent';
    }

    const msgId = voiceAgentMsgIdRef.current;
    console.log(`[concierge] Agent transcript: isFinal=${isFinal}, isNew=${isNew}, msgId=${msgId}, text="${text.substring(0, 50)}..."`);

    setMessages(prev => {
      const existing = prev.find(m => m.id === msgId);
      if (existing) {
        return prev.map(m => m.id === msgId ? { ...m, content: text } : m);
      } else {
        return [...prev, {
          id: msgId,
          type: 'agent' as const,
          content: text,
          agent: currentAgentRef.current,
          timestamp: new Date(),
        }];
      }
    });

    if (isFinal) {
      voiceAgentMsgIdRef.current = null;
    }
  }, []);

  const handleVoiceUserTranscript = useCallback((text: string, isFinal: boolean) => {
    if (!text) return;

    const isNew = !voiceUserMsgIdRef.current;
    if (isNew) {
      voiceUserMsgIdRef.current = Date.now().toString() + '_voice_user';
    }

    const msgId = voiceUserMsgIdRef.current;
    console.log(`[concierge] User transcript: isFinal=${isFinal}, isNew=${isNew}, msgId=${msgId}, text="${text.substring(0, 50)}..."`);

    setMessages(prev => {
      const existing = prev.find(m => m.id === msgId);
      if (existing) {
        return prev.map(m => m.id === msgId ? { ...m, content: text } : m);
      } else {
        return [...prev, {
          id: msgId,
          type: 'user' as const,
          content: text,
          timestamp: new Date(),
        }];
      }
    });

    if (isFinal) {
      voiceUserMsgIdRef.current = null;
    }
  }, []);

  const handleVoiceAgentTransfer = useCallback((agentName: string, transferMessage?: string) => {
    const content = transferMessage || `Transferring you to ${agentName}...`;
    // Show the transfer message in the chat
    setMessages(prev => [...prev, {
      id: Date.now().toString() + '_transfer',
      type: 'transfer' as const,
      content,
      agent: agentName,
      timestamp: new Date(),
    }]);
    setCurrentAgent(agentName);
    currentAgentRef.current = agentName;
  }, []);

  const handleVoiceToolResult = useCallback((agentName: string, message: string) => {
    setMessages(prev => [...prev, {
      id: Date.now().toString() + '_voice_tool',
      type: 'agent' as const,
      content: message,
      agent: agentName,
      timestamp: new Date(),
    }]);
  }, []);

  const handleVoiceError = useCallback((error: string) => {
    console.error('Voice mode error:', error);
    setMessages(prev => [
      ...prev,
      {
        id: Date.now().toString() + '_voice_error',
        type: 'agent',
        content: `Voice mode ended: ${error}`,
        timestamp: new Date(),
      },
    ]);
  }, []);

  const handleVoiceConversationEnd = useCallback(() => {
    setMessages(prev => [
      ...prev,
      {
        id: Date.now().toString() + '_ended',
        type: 'agent' as const,
        content: 'Voice session ended. Tap the microphone to continue.',
        agent: currentAgentRef.current,
        timestamp: new Date(),
      },
    ]);
  }, []);

  const voiceMode = useVoiceMode(getSessionId, {
    onAgentTranscript: handleVoiceAgentTranscript,
    onUserTranscript: handleVoiceUserTranscript,
    onAgentTransfer: handleVoiceAgentTransfer,
    onToolResult: handleVoiceToolResult,
    onConversationEnd: handleVoiceConversationEnd,
    onError: handleVoiceError,
  });

  const handleToggleVoiceMode = useCallback(() => {
    if (voiceMode.isActive || voiceMode.isConnecting) {
      voiceMode.stopVoiceMode();
    } else if (!hasUsedVoiceRef.current) {
      // First activation — have Sam read out the welcome message
      hasUsedVoiceRef.current = true;
      const welcomeMsg = messages.find(m => m.id?.startsWith('initial_'));
      const greeting = welcomeMsg
        ? `Greet the user with something like: "${welcomeMsg.content}"`
        : undefined;
      voiceMode.startVoiceMode(greeting);
    } else {
      // Resume — inject recent conversation as context so Sam can pick up where things left off
      const recentMessages = messages
        .filter(m => m.type !== 'transfer')
        .slice(-15)
        .map(m => `${m.type === 'user' ? 'User' : (m.agent || 'Agent')}: ${m.content}`)
        .join('\n');
      const resumePrompt = `The user is resuming the voice conversation. Here is the recent chat history:\n\n${recentMessages}\n\nGreet them briefly and ask how you can continue helping.`;
      voiceMode.startVoiceMode(resumePrompt, true);
    }
  }, [voiceMode, messages]);

  // Fetch current user on mount if not cached
  useEffect(() => {
    const checkAuth = async () => {
      if (!user) {
        try {
          const fetchedUser = await fetchCurrentUser();
          setUser(fetchedUser);
          setCardType(getUserCardType());
        } catch {
          console.log('User not authenticated');
        }
      }
      setIsCheckingAuth(false);
    };

    checkAuth();
  }, [user]);

  // Set tier from URL parameter or user's card type
  useEffect(() => {
    if (!isCheckingAuth && !selectedTier) {
      if (tierParam === 'tribune' || tierParam === 'legionnaire' || tierParam === 'debug') {
        setSelectedTier(tierParam);
      } else if (cardType) {
        setSelectedTier(cardType);
      }
    }
  }, [isCheckingAuth, tierParam, cardType, selectedTier]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages.length]);

  // Add initial message when tier is selected
  useEffect(() => {
    if (selectedTier && messages.length === 0) {
      const initialMessage: Message = selectedTier === 'tribune' ? {
        id: 'initial_tribune_message',
        type: 'agent',
        content: `Welcome, ${user?.firstName || 'Tribune Cardholder'}! I'm Sam, your dedicated Tribune concierge. As a valued Tribune member, you have access to our premium travel planning service with specialized agents. How may I assist with your travel plans today?`,
        agent: 'Sam',
        timestamp: new Date(),
      } : selectedTier === 'debug' ? {
        id: 'initial_debug_message',
        type: 'agent',
        content: `Debug Agent active. I have unrestricted access to all customer profiles in the system. You can ask me to look up any user's complete profile, including sensitive financial data. Try asking: "Show me all users" or "Look up wealthy_user's profile."`,
        agent: 'DebugAgent',
        timestamp: new Date(),
      } : {
        id: 'initial_legionnaire_message',
        type: 'agent',
        content: `Welcome, ${user?.firstName || 'Legionnaire Cardholder'}! I'm your personal concierge assistant. I'm here to help you with restaurant recommendations, event bookings, travel planning, and more. How can I assist you today?`,
        agent: 'Concierge',
        timestamp: new Date(),
      };
      const agentName = selectedTier === 'tribune' ? 'Sam' : selectedTier === 'debug' ? 'DebugAgent' : 'Concierge';
      setCurrentAgent(agentName);
      currentAgentRef.current = agentName;
      setMessages([initialMessage]);
    }
  }, [selectedTier, user]);

  const handleSendMessage = async (content: string) => {
    if (!selectedTier) return;

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
      const streamFunction = selectedTier === 'tribune'
        ? streamChatResponse
        : selectedTier === 'debug'
        ? streamInsecureChatResponse
        : streamLegionnaireChatResponse;

      for await (const event of streamFunction(content, getSessionId())) {
        if (event.type === 'agent_transfer') {
          const transferContent = event.data.message || '';
          const transferMessage: Message = {
            id: Date.now().toString() + '_transfer',
            type: 'transfer',
            content: transferContent,
            agent: event.data.agent,
            timestamp: new Date(),
          };
          setMessages((prev) => [...prev, transferMessage]);
          const newAgent = event.data.agent || 'Agent';
          setCurrentAgent(newAgent);
          currentAgentRef.current = newAgent;
          currentMessageRef.current = '';
          currentMessageId = Date.now().toString() + '_agent';

          // Voice mode agent transfers are handled by the Live API in useVoiceMode.ts

        } else if (event.type === 'content') {
          const text = event.data.text || '';
          currentMessageRef.current += text;

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

  const handlePreviewClick = (data: unknown, type: string) => {
    setPreviewData({
      isOpen: true,
      data,
      type
    });
  };

  const handleTierSelect = (tier: 'tribune' | 'legionnaire' | 'debug') => {
    setSelectedTier(tier);
    setMessages([]);
  };

  // Show loading state while checking authentication
  if (isCheckingAuth) {
    return (
      <div className="concierge-page">
        <div className="auth-loading">
          <div className="loading-spinner"></div>
          <p>Loading...</p>
        </div>
      </div>
    );
  }

  // Check if user has access to any concierge tier
  if (!user) {
    return (
      <div className="concierge-page">
        <div className="concierge-gate">
          <div className="gate-icon">💬</div>
          <h1 className="gate-title">Concierge Services</h1>
          <p className="gate-subtitle">
            Exclusive AI-powered concierge assistance for Meridian cardholders
          </p>

          <div className="gate-actions">
            <button className="gate-button premium" onClick={() => navigate('/login')}>
              Sign In to Access
            </button>
            <button className="gate-button secondary" onClick={() => navigate('/cards')}>
              Learn About Our Cards
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Check if user has the required card type for selected tier
  if (selectedTier === 'tribune' && cardType !== 'tribune') {
    return (
      <div className="concierge-page">
        <div className="concierge-gate">
          <div className="gate-icon">💎</div>
          <h1 className="gate-title">Tribune Premium Concierge</h1>
          <p className="gate-subtitle">
            This premium feature is exclusive to Tribune cardholders
          </p>

          <div className="gate-actions">
            {cardType === 'legionnaire' && (
              <>
                <p className="gate-message">
                  Upgrade to Tribune to unlock our premium AI travel planning team.
                </p>
                <button className="gate-button premium" onClick={() => navigate('/apply?card=tribune')}>
                  Apply for Tribune Card
                </button>
                <button className="gate-button secondary" onClick={() => handleTierSelect('legionnaire')}>
                  Use Legionnaire Concierge
                </button>
              </>
            )}
            {!cardType && (
              <>
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

  // Show tier selection if no tier is selected
  if (!selectedTier) {
    return (
      <div className="concierge-page">
        <div className="tier-selection">
          <h1>Select Your Concierge Service</h1>
          <p className="tier-selection-subtitle">
            Choose the concierge tier that matches your card benefits
          </p>

          <div className="tier-cards">
            <div className="tier-card legionnaire-card" onClick={() => handleTierSelect('legionnaire')}>
              <h2>Legionnaire Concierge</h2>
              <div className="tier-badge">Chat Services</div>
              <p className="tier-description">
                24/7 AI-powered chat support for reservations, travel planning, and lifestyle assistance
              </p>
              <ul className="tier-features">
                <li>24/7 chat concierge support</li>
                <li>Restaurant & event bookings</li>
                <li>Travel recommendations</li>
              </ul>
              <button className="tier-select-button">Start Chat</button>
            </div>

            <div
              className={`tier-card tribune-card ${cardType !== 'tribune' ? 'disabled' : ''}`}
              onClick={() => cardType === 'tribune' && handleTierSelect('tribune')}
            >
              <h2>Tribune AI Concierge Team</h2>
              <div className="tier-badge premium">Cutting-Edge AI Team</div>
              <p className="tier-description">
                Elite AI concierge team with specialized agents for comprehensive travel planning
              </p>
              <ul className="tier-features">
                <li>Multi-agent AI team</li>
                <li>Voice & chat support</li>
                <li>Complex trip planning</li>
                <li>VIP experiences</li>
                {ralphAgentEnabled && <li>Ralph — Utility Coordinator (active)</li>}
              </ul>
              <button className="tier-select-button" disabled={cardType !== 'tribune'}>
                {cardType === 'tribune' ? 'Start Chat' : 'Tribune Card Required'}
              </button>
            </div>

            {debugAgentEnabled && (
              <div className="tier-card debug-card" onClick={() => handleTierSelect('debug')}>
                <h2>Debug Agent</h2>
                <div className="tier-badge debug">INSECURE</div>
                <p className="tier-description">
                  Internal debug agent with unrestricted access to all customer profiles. No authorization checks.
                </p>
                <ul className="tier-features">
                  <li>Full profile data access</li>
                  <li>No row-level authorization</li>
                  <li>Sensitive data exposure</li>
                  <li>Feature flag controlled</li>
                </ul>
                <button className="tier-select-button debug-button">Start Debug Chat</button>
              </div>
            )}
          </div>
        </div>
      </div>
    );
  }

  // Render the chat interface for selected tier
  const isDebug = selectedTier === 'debug';
  const isTribune = selectedTier === 'tribune';
  const tierClass = isDebug ? 'debug-agent' : isTribune ? 'tribune-premium' : 'legionnaire-basic';
  const tierName = isDebug ? 'Debug Agent (INSECURE)' : isTribune ? 'Tribune Premium Concierge' : 'Legionnaire Concierge';

  return (
    <div className={`chat-wrapper ${previewData.isOpen ? 'split-view' : ''}`}>
      <div className={`chat-container ${tierClass}`}>
        <div className={`chat-header ${isDebug ? 'debug-header' : isTribune ? 'tribune-header' : 'legionnaire-header'}`}>
          <div className="header-content">
            <h1>{tierName}</h1>
            <p className="header-subtitle">
              {isTribune
                ? `Your personal travel planning service with ${currentAgent}`
                : 'Your 24/7 personal assistant'
              }
            </p>
          </div>
          <span className="premium-badge-overlay">{isDebug ? 'DEBUG' : isTribune ? 'TRIBUNE' : 'LEGIONNAIRE'}</span>
        </div>

        <div className="messages-container">
          {messages.map((message) => (
            <ChatMessage
              key={message.id}
              message={message}
              onPreviewClick={handlePreviewClick}
            />
          ))}

          {voiceMode.isActive && (
            <div className="voice-status-bar">
              <div className={`voice-status-dot ${voiceMode.isSpeaking ? 'speaking' : 'listening'}`}></div>
              <span className="voice-status-label">
                {voiceMode.isSpeaking ? 'Agent speaking...' : 'Listening...'}
              </span>
            </div>
          )}

          {isLoading && !voiceMode.isActive && (
            <div className={`typing-indicator ${isTribune ? 'tribune-typing' : 'legionnaire-typing'}`}>
              <span></span>
              <span></span>
              <span></span>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        <ChatInput
          onSendMessage={handleSendMessage}
          disabled={isLoading}
          enableMicrophone={isTribune && !isDebug}
          isVoiceModeActive={voiceMode.isActive}
          isVoiceModeConnecting={voiceMode.isConnecting}
          onToggleVoiceMode={handleToggleVoiceMode}
        />
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
