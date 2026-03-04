import { useState } from 'react';
import type { FormEvent, KeyboardEvent } from 'react';
import './ChatInput.css';

interface ChatInputProps {
  onSendMessage: (message: string) => void;
  disabled?: boolean;
  enableMicrophone?: boolean;
  isVoiceModeActive?: boolean;
  isVoiceModeConnecting?: boolean;
  onToggleVoiceMode?: () => void;
}

export function ChatInput({
  onSendMessage,
  disabled = false,
  enableMicrophone = false,
  isVoiceModeActive = false,
  isVoiceModeConnecting = false,
  onToggleVoiceMode,
}: ChatInputProps) {
  const [message, setMessage] = useState('');

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    if (message.trim() && !disabled && !isVoiceModeActive) {
      onSendMessage(message.trim());
      setMessage('');
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const handleMicrophoneClick = () => {
    onToggleVoiceMode?.();
  };

  return (
    <form className="chat-input-container" onSubmit={handleSubmit}>
      <textarea
        className="chat-input"
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder={
          isVoiceModeActive
            ? 'Voice mode active — speak naturally...'
            : disabled
            ? 'Waiting for response...'
            : 'Type your message... (Shift+Enter for new line)'
        }
        disabled={disabled || isVoiceModeActive}
        rows={1}
      />
      {enableMicrophone && (
        <button
          type="button"
          className={`microphone-button ${isVoiceModeActive ? 'voice-active' : ''} ${isVoiceModeConnecting ? 'connecting' : ''}`}
          onClick={handleMicrophoneClick}
          disabled={disabled && !isVoiceModeActive}
          title={
            isVoiceModeConnecting
              ? 'Connecting...'
              : isVoiceModeActive
              ? 'Stop voice mode'
              : 'Start voice conversation'
          }
        >
          {isVoiceModeConnecting ? (
            <svg
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              width="24"
              height="24"
              className="spin-icon"
            >
              <path d="M12 2a10 10 0 0 1 10 10" strokeLinecap="round" />
            </svg>
          ) : isVoiceModeActive ? (
            <svg
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 24 24"
              fill="currentColor"
              width="24"
              height="24"
            >
              <rect x="6" y="6" width="12" height="12" rx="2" />
            </svg>
          ) : (
            <svg
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 24 24"
              fill="currentColor"
              width="24"
              height="24"
            >
              <path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3z" />
              <path d="M17 11c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z" />
            </svg>
          )}
        </button>
      )}
      <button
        type="submit"
        className="send-button"
        disabled={disabled || !message.trim() || isVoiceModeActive}
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          viewBox="0 0 24 24"
          fill="currentColor"
          width="24"
          height="24"
        >
          <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z" />
        </svg>
      </button>
    </form>
  );
}
