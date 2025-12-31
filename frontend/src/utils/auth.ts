// Mock authentication utilities

export type User = {
  id: string;
  name: string;
  email: string;
  cardType: 'legionnaire' | 'tribune' | 'none';
};

// Mock user data
const mockUser: User = {
  id: '1',
  name: 'John Doe',
  email: 'john.doe@example.com',
  cardType: 'legionnaire', // Change this to 'tribune' or 'none' to test different states
};

// Mock authentication state
let isAuthenticated = true; // Change to false to test logged out state

export const login = (_email: string, _password: string): Promise<User> => {
  return new Promise((resolve) => {
    setTimeout(() => {
      isAuthenticated = true;
      resolve(mockUser);
    }, 500);
  });
};

export const logout = (): Promise<void> => {
  return new Promise((resolve) => {
    setTimeout(() => {
      isAuthenticated = false;
      resolve();
    }, 300);
  });
};

export const getCurrentUser = (): User | null => {
  return isAuthenticated ? mockUser : null;
};

export const checkAuthentication = (): boolean => {
  return isAuthenticated;
};

export const getUserCardType = (): 'legionnaire' | 'tribune' | 'none' => {
  const user = getCurrentUser();
  return user ? user.cardType : 'none';
};
