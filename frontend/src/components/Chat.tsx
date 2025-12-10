import { useState, useRef, useEffect } from 'react';
import { ulid } from 'ulid';
import type { Message } from '../types/chat';
import { streamChatResponse } from '../utils/api';
import { ChatMessage } from './ChatMessage';
import { ChatInput } from './ChatInput';
import './Chat.css';

export function Chat() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [currentAgent, setCurrentAgent] = useState<string>('Sam');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const currentMessageRef = useRef<string>('');
  const currentAgentRef = useRef<string>('Sam');
  const sessionIdRef = useRef<string>(ulid());

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Add initial message from Sam when component mounts
  useEffect(() => {
    const initialMessage: Message = {
      id: 'initial_sam_message',
      type: 'agent',
      content: "Hi! I'm Sam, your travel planner. How can I help you today? 🌟",
      agent: 'Sam',
      timestamp: new Date(),
    };
    setMessages([initialMessage]);
  }, []);

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

  return (
    <div className="chat-container">
      <div className="chat-header">
        <div className="header-content">
          <h1>🌍 Travel Planner</h1>
          <p className="header-subtitle">
            Plan your perfect trip with help from {currentAgent}
          </p>
        </div>
      </div>

      <div className="messages-container">
        {messages.length === 0 && (
          <div className="welcome-message">
            <div className="welcome-icon">✈️</div>
            <h2>Welcome to Travel Planner!</h2>
            <p>
              I'm Sam, your travel coordinator. I work with a team of specialists:
            </p>
            <ul className="specialists-list">
              <li>✈️ <strong>Jenny</strong> - Flight searches</li>
              <li>🏨 <strong>Marcus</strong> - Accommodation bookings</li>
              <li>🗺️ <strong>Sofia</strong> - Itinerary planning</li>
              <li>💰 <strong>Alex</strong> - Budget management</li>
            </ul>
            <p>Ask me anything about your travel plans!</p>
          </div>
        )}

        {messages.map((message) => (
          <ChatMessage key={message.id} message={message} />
        ))}

        {isLoading && (
          <div className="typing-indicator">
            <span></span>
            <span></span>
            <span></span>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      <ChatInput onSendMessage={handleSendMessage} disabled={isLoading} />
    </div>
  );
}
