import { getCurrentUser as apiGetCurrentUser, login as apiLogin, logout as apiLogout } from './api';
import type { User, LoginRequest } from '../types/user';

let currentUser: User | null = null;

export async function login(credentials: LoginRequest): Promise<User> {
  try {
    const response = await apiLogin(credentials);
    currentUser = response.user;
    return response.user;
  } catch (error) {
    console.error('Login error:', error);
    throw error;
  }
}

export async function logout(): Promise<void> {
  await apiLogout();
  currentUser = null;
}

export async function fetchCurrentUser(): Promise<User | null> {
  try {
    currentUser = await apiGetCurrentUser();
    return currentUser;
  } catch (error) {
    console.error('Failed to fetch current user:', error);
    currentUser = null;
    return null;
  }
}

export function getCachedUser(): User | null {
  return currentUser;
}

export function checkAuthentication(): boolean {
  return currentUser !== null;
}

export function getUserCardType(): 'legionnaire' | 'tribune' | 'none' {
  return currentUser?.currentCard || 'none';
}
