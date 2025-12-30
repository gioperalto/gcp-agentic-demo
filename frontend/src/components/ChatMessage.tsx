import type { Message } from '../types/chat';
import './ChatMessage.css';

interface ChatMessageProps {
  message: Message;
  onPreviewClick?: (data: any, type: string) => void;
}

export function ChatMessage({ message, onPreviewClick }: ChatMessageProps) {
  // Log message content to help debug preview links
  if (message.type === 'agent' && message.content.includes('preview://')) {
    console.log('[ChatMessage] Agent message contains preview:// links:', message.content);
  }

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

  const handlePreviewClick = (href: string, e: React.MouseEvent) => {
    e.preventDefault();
    console.log('[ChatMessage] Preview button clicked:', href);

    // Parse preview:// links
    if (href.startsWith('preview://')) {
      try {
        const urlParts = href.replace('preview://', '').split('/');
        const type = urlParts[0];
        const dataString = urlParts.slice(1).join('/');
        console.log('[ChatMessage] Parsing preview link - Type:', type, 'DataString length:', dataString.length);
        const data = JSON.parse(decodeURIComponent(dataString));
        console.log('[ChatMessage] Successfully parsed preview data:', { type, data });

        if (onPreviewClick) {
          onPreviewClick(data, type);
        }
      } catch (error) {
        console.error('[ChatMessage] Failed to parse preview data:', error);
        console.error('[ChatMessage] Original href:', href);
      }
    }
  };

  // Convert markdown-style links to HTML with buttons for preview links
  const renderHTMLContent = (content: string) => {
    // Replace markdown links with HTML
    let html = content;

    // Convert markdown links to HTML buttons for preview links and regular links for others
    html = html.replace(/\[([^\]]+)\]\(([^)]+)\)/g, (_match, text, url) => {
      if (url.startsWith('preview://')) {
        // Create a button for preview links
        return `<button class="preview-button" data-preview-url="${url}">${text}</button>`;
      } else {
        // Create regular links for external URLs
        return `<a href="${url}" target="_blank" rel="noopener noreferrer">${text}</a>`;
      }
    });

    // Convert markdown bold
    html = html.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
    html = html.replace(/__([^_]+)__/g, '<strong>$1</strong>');

    // Convert markdown italic
    html = html.replace(/\*([^*]+)\*/g, '<em>$1</em>');
    html = html.replace(/_([^_]+)_/g, '<em>$1</em>');

    // Convert line breaks
    html = html.replace(/\n/g, '<br/>');

    // Convert bullet lists
    html = html.replace(/^- (.+)$/gm, '<li>$1</li>');
    html = html.replace(/(<li>.*<\/li>)/s, '<ul>$1</ul>');

    return html;
  };

  const handleButtonClick = (e: React.MouseEvent<HTMLDivElement>) => {
    const target = e.target as HTMLElement;
    if (target.classList.contains('preview-button')) {
      const url = target.getAttribute('data-preview-url');
      if (url) {
        handlePreviewClick(url, e);
      }
    }
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
      <div
        className="message-content"
        onClick={handleButtonClick}
        dangerouslySetInnerHTML={{ __html: renderHTMLContent(message.content) }}
      />
    </div>
  );
}
