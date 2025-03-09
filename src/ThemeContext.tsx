import React, { createContext, useState, useContext, useEffect, ReactNode } from 'react';

// Define theme types
export type ThemeMode = 'light' | 'dark';

// Define theme colors
export interface ThemeColors {
  background: string;
  text: string;
  primary: string;
  secondary: string;
  border: string;
  cardBackground: string;
  userMessageBg: string;
  aiMessageBg: string;
  inputBackground: string;
  footerBackground: string;
  success: string;
  error: string;
}

// Theme definitions
export const themes: Record<ThemeMode, ThemeColors> = {
  light: {
    background: '#f9fafb',
    text: '#1a1a1a',
    primary: '#2563eb',
    secondary: '#4b5563',
    border: '#e0e0e0',
    cardBackground: '#f8f9fa',
    userMessageBg: '#e9f5ff',
    aiMessageBg: '#ffffff',
    inputBackground: '#ffffff',
    footerBackground: '#ffffff',
    success: '#22c55e',
    error: '#ef4444'
  },
  dark: {
    background: '#111827',
    text: '#f3f4f6',
    primary: '#3b82f6',
    secondary: '#9ca3af',
    border: '#374151',
    cardBackground: '#1f2937',
    userMessageBg: '#1e3a8a',
    aiMessageBg: '#1f2937',
    inputBackground: '#1f2937',
    footerBackground: '#1f2937',
    success: '#10b981',
    error: '#ef4444'
  }
};

// Create the context
interface ThemeContextType {
  themeMode: ThemeMode;
  colors: ThemeColors;
  toggleTheme: () => void;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

// Create a provider component
interface ThemeProviderProps {
  children: ReactNode;
}

export const ThemeProvider: React.FC<ThemeProviderProps> = ({ children }) => {
  // Check if user has a saved preference or use system preference
  const getSavedTheme = (): ThemeMode => {
    const savedTheme = localStorage.getItem('theme') as ThemeMode;
    if (savedTheme && (savedTheme === 'light' || savedTheme === 'dark')) {
      return savedTheme;
    }
    
    // Check system preference
    if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
      return 'dark';
    }
    
    return 'light';
  };

  const [themeMode, setThemeMode] = useState<ThemeMode>(getSavedTheme);
  const colors = themes[themeMode];

  // Toggle between light and dark mode
  const toggleTheme = () => {
    setThemeMode(prevMode => {
      const newMode = prevMode === 'light' ? 'dark' : 'light';
      localStorage.setItem('theme', newMode);
      return newMode;
    });
  };

  // Update document body background when theme changes
  useEffect(() => {
    document.body.style.backgroundColor = colors.background;
    document.body.style.color = colors.text;
  }, [colors]);

  return (
    <ThemeContext.Provider value={{ themeMode, colors, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  );
};

// Custom hook to use the theme context
export const useTheme = (): ThemeContextType => {
  const context = useContext(ThemeContext);
  if (context === undefined) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
}; 