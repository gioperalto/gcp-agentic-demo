import type { Message } from '../types/chat';
import Markdown from 'react-markdown';
import './ChatMessage.css';

interface ChatMessageProps {
  message: Message;
}

export function ChatMessage({ message }: ChatMessageProps) {
  const getMessageClass = () => {
    if (message.type === 'user') return 'message user-message';
    if (message.type === 'transfer') return 'message transfer-message';
    return 'message agent-message';
  };

  const getAgentLabel = () => {
    if (message.type === 'user') return 'You';
    if (message.type === 'transfer') return '🔄 Transfer';
    return message.agent || 'Agent';
  };

  return (
    <div className={getMessageClass()}>
      <div className="message-header">
        <span className="message-sender">{getAgentLabel()}</span>
        <span className="message-time">
          {message.timestamp.toLocaleTimeString([], {
            hour: '2-digit',
            minute: '2-digit'
          })}
        </span>
      </div>
      <div className="message-content">
        <Markdown>{message.content}</Markdown>
      </div>
    </div>
  );
}
