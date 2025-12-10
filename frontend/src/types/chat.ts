export interface Message {
  id: string;
  type: 'user' | 'agent' | 'transfer';
  content: string;
  agent?: string;
  timestamp: Date;
}

export interface ChatEvent {
  type: 'agent_transfer' | 'content' | 'done' | 'error';
  data: {
    text?: string;
    agent?: string;
    message?: string;
    detail?: string;
  };
}
