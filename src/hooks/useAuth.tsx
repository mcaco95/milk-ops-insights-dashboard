
import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { AuthUser, LoginRequest, LoginResponse } from '../types/auth';

interface AuthContextType {
  user: AuthUser | null;
  login: (credentials: LoginRequest) => Promise<void>;
  logout: () => void;
  isLoading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Check for existing auth on mount
    const token = localStorage.getItem('auth_token');
    const dairy_name = localStorage.getItem('dairy_name');
    const dairy_id = localStorage.getItem('dairy_id');
    const expires_at = localStorage.getItem('expires_at');

    if (token && dairy_name && dairy_id && expires_at) {
      const expirationTime = parseInt(expires_at);
      if (Date.now() < expirationTime) {
        setUser({ token, dairy_name, dairy_id, expires_at: expirationTime });
      } else {
        // Token expired, clear storage
        logout();
      }
    }
    setIsLoading(false);
  }, []);

  const login = async (credentials: LoginRequest) => {
    try {
      // Check for demo mode
      if (credentials.username === 'demo' && credentials.password === 'demo') {
        const mockResponse: LoginResponse = {
          token: 'demo-token-' + Date.now(),
          dairy_name: 'Sunrise Valley Dairy',
          dairy_id: 'demo-dairy-001',
          expires_in: 86400 // 24 hours
        };
        
        const expires_at = Date.now() + (mockResponse.expires_in * 1000);

        // Store in localStorage
        localStorage.setItem('auth_token', mockResponse.token);
        localStorage.setItem('dairy_name', mockResponse.dairy_name);
        localStorage.setItem('dairy_id', mockResponse.dairy_id);
        localStorage.setItem('expires_at', expires_at.toString());
        localStorage.setItem('demo_mode', 'true');

        setUser({
          token: mockResponse.token,
          dairy_name: mockResponse.dairy_name,
          dairy_id: mockResponse.dairy_id,
          expires_at,
        });
        return;
      }

      // Try real API login
      const response = await fetch('/api/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(credentials),
      });

      if (!response.ok) {
        throw new Error('Login failed');
      }

      const data: LoginResponse = await response.json();
      const expires_at = Date.now() + (data.expires_in * 1000);

      // Store in localStorage
      localStorage.setItem('auth_token', data.token);
      localStorage.setItem('dairy_name', data.dairy_name);
      localStorage.setItem('dairy_id', data.dairy_id);
      localStorage.setItem('expires_at', expires_at.toString());
      localStorage.removeItem('demo_mode'); // Clear demo mode

      setUser({
        token: data.token,
        dairy_name: data.dairy_name,
        dairy_id: data.dairy_id,
        expires_at,
      });
    } catch (error) {
      throw new Error('Invalid username or password');
    }
  };

  const logout = () => {
    localStorage.removeItem('auth_token');
    localStorage.removeItem('dairy_name');
    localStorage.removeItem('dairy_id');
    localStorage.removeItem('expires_at');
    localStorage.removeItem('demo_mode');
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, login, logout, isLoading }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
