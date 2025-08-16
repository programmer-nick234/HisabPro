import { useState, useEffect, createContext, useContext } from 'react';
import { authAPI } from '@/lib/api';
import toast from 'react-hot-toast';

interface User {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  profile: {
    company_name: string;
    phone: string;
    address: string;
    gst_number: string;
    logo?: string;
  };
}

interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (username: string, password: string) => Promise<boolean>;
  register: (data: any) => Promise<boolean>;
  logout: () => void;
  updateProfile: (data: any) => Promise<boolean>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    try {
      // Check if we're on the client side
      if (typeof window === 'undefined') {
        setLoading(false);
        return;
      }

      const token = localStorage.getItem('access_token');
      if (token) {
        const response = await authAPI.getUser();
        setUser(response.data);
      }
    } catch (error) {
      if (typeof window !== 'undefined') {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user');
      }
    } finally {
      setLoading(false);
    }
  };

  const login = async (username: string, password: string): Promise<boolean> => {
    try {
      const response = await authAPI.login({ username, password });
      const { user: userData, tokens } = response.data;
      
      if (typeof window !== 'undefined') {
        localStorage.setItem('access_token', tokens.access);
        localStorage.setItem('refresh_token', tokens.refresh);
        localStorage.setItem('user', JSON.stringify(userData));
      }
      
      setUser(userData);
      toast.success('Login successful!');
      return true;
    } catch (error: any) {
      const message = error.response?.data?.error || 'Login failed';
      toast.error(message);
      return false;
    }
  };

  const register = async (data: any): Promise<boolean> => {
    try {
      const response = await authAPI.register(data);
      const { user: userData, tokens } = response.data;
      
      if (typeof window !== 'undefined') {
        localStorage.setItem('access_token', tokens.access);
        localStorage.setItem('refresh_token', tokens.refresh);
        localStorage.setItem('user', JSON.stringify(userData));
      }
      
      setUser(userData);
      toast.success('Registration successful!');
      return true;
    } catch (error: any) {
      const message = error.response?.data?.error || 'Registration failed';
      toast.error(message);
      return false;
    }
  };

  const logout = () => {
    if (typeof window !== 'undefined') {
      const refreshToken = localStorage.getItem('refresh_token');
      if (refreshToken) {
        authAPI.logout({ refresh_token: refreshToken }).catch(() => {});
      }
      
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('user');
    }
    
    setUser(null);
    toast.success('Logged out successfully');
  };

  const updateProfile = async (data: any): Promise<boolean> => {
    try {
      const response = await authAPI.updateProfile(data);
      setUser(response.data);
      if (typeof window !== 'undefined') {
        localStorage.setItem('user', JSON.stringify(response.data));
      }
      toast.success('Profile updated successfully!');
      return true;
    } catch (error: any) {
      const message = error.response?.data?.error || 'Profile update failed';
      toast.error(message);
      return false;
    }
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout, updateProfile }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextType {
  // Check if we're on the client side
  if (typeof window === 'undefined') {
    // Return a default context for SSR
    return {
      user: null,
      loading: true,
      login: async () => false,
      register: async () => false,
      logout: () => {},
      updateProfile: async () => false,
    };
  }

  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
