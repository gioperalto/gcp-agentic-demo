import type { ChatEvent } from '../types/chat';
import type { User, LoginRequest, LoginResponse } from '../types/user';
import type { ApplicationRequest, ApplicationResponse } from '../types/application';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Token storage
let authToken: string | null = localStorage.getItem('auth_token');

export function setAuthToken(token: string | null) {
  authToken = token;
  if (token) {
    localStorage.setItem('auth_token', token);
  } else {
    localStorage.removeItem('auth_token');
  }
}

export function getAuthToken(): string | null {
  return authToken;
}

function getHeaders(): HeadersInit {
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
  };

  if (authToken) {
    headers['Authorization'] = `Bearer ${authToken}`;
  }

  return headers;
}

// Authentication endpoints
export async function login(credentials: LoginRequest): Promise<LoginResponse> {
  const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(credentials),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Login failed');
  }

  const data: LoginResponse = await response.json();
  setAuthToken(data.access_token);
  return data;
}

export async function getCurrentUser(): Promise<User> {
  const response = await fetch(`${API_BASE_URL}/api/auth/me`, {
    headers: getHeaders(),
  });

  if (!response.ok) {
    if (response.status === 401) {
      setAuthToken(null);
      throw new Error('Not authenticated');
    }
    throw new Error('Failed to fetch user data');
  }

  return response.json();
}

export async function logout() {
  setAuthToken(null);
}

// Card application endpoint
export async function applyForCard(request: ApplicationRequest): Promise<ApplicationResponse> {
  const response = await fetch(`${API_BASE_URL}/api/cards/apply`, {
    method: 'POST',
    headers: getHeaders(),
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    if (response.status === 401) {
      setAuthToken(null);
      throw new Error('Not authenticated');
    }
    const error = await response.json();
    throw new Error(error.detail || 'Application failed');
  }

  return response.json();
}

// Existing chat streaming function

export async function* streamChatResponse(message: string, sessionId: string = 'default'): AsyncGenerator<ChatEvent> {
  const response = await fetch(`${API_BASE_URL}/api/chat/stream`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      message,
      session_id: sessionId,
    }),
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  const reader = response.body?.getReader();
  const decoder = new TextDecoder();

  if (!reader) {
    throw new Error('Response body is null');
  }

  let buffer = '';

  while (true) {
    const { done, value } = await reader.read();

    if (done) {
      break;
    }

    buffer += decoder.decode(value, { stream: true });

    const lines = buffer.split('\n');
    buffer = lines.pop() || '';

    for (const line of lines) {
      if (line.startsWith('data: ')) {
        const jsonStr = line.slice(6);
        try {
          const event: ChatEvent = JSON.parse(jsonStr);
          yield event;
        } catch (e) {
          console.error('Failed to parse SSE data:', e);
        }
      }
    }
  }
}
