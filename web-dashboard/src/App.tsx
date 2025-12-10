import { createTheme, CssBaseline, ThemeProvider } from '@mui/material';
import React from 'react';
import { Toaster } from 'react-hot-toast';
import { QueryClient, QueryClientProvider } from 'react-query';
import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom';

// Pages
import Dashboard from './pages/Dashboard';
import Deployments from './pages/Deployments';
import Logs from './pages/Logs';
import Monitoring from './pages/Monitoring';
import Security from './pages/Security';
import Settings from './pages/Settings';
import Terminal from './pages/Terminal';

// Components
import ErrorBoundary from './components/ErrorBoundary';
import Layout from './components/Layout';

// Create React Query client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 30000,
    },
  },
});

// Create dark theme
const darkTheme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#00ff41',
    },
    secondary: {
      main: '#00d4ff',
    },
    background: {
      default: '#0a0e27',
      paper: '#1a1f3a',
    },
    error: {
      main: '#ff4444',
    },
    warning: {
      main: '#ffaa00',
    },
    success: {
      main: '#00ff41',
    },
  },
  typography: {
    fontFamily: '"Roboto Mono", "Courier New", monospace',
    h1: {
      fontSize: '2.5rem',
      fontWeight: 700,
    },
    h2: {
      fontSize: '2rem',
      fontWeight: 600,
    },
  },
  components: {
    MuiPaper: {
      styleOverrides: {
        root: {
          backgroundImage: 'none',
          borderRadius: 8,
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          textTransform: 'none',
          fontWeight: 600,
        },
      },
    },
  },
});

const App: React.FC = () => {
  return (
    <ErrorBoundary>
      <QueryClientProvider client={queryClient}>
        <ThemeProvider theme={darkTheme}>
          <CssBaseline />
          <BrowserRouter>
            <Layout>
              <Routes>
                <Route path="/" element={<Navigate to="/dashboard" replace />} />
                <Route path="/dashboard" element={<Dashboard />} />
                <Route path="/monitoring" element={<Monitoring />} />
                <Route path="/deployments" element={<Deployments />} />
                <Route path="/security" element={<Security />} />
                <Route path="/logs" element={<Logs />} />
                <Route path="/terminal" element={<Terminal />} />
                <Route path="/settings" element={<Settings />} />
              </Routes>
            </Layout>
          </BrowserRouter>
          <Toaster
            position="top-right"
            toastOptions={{
              duration: 4000,
              style: {
                background: '#1a1f3a',
                color: '#fff',
                border: '1px solid #00ff41',
              },
              success: {
                iconTheme: {
                  primary: '#00ff41',
                  secondary: '#0a0e27',
                },
              },
              error: {
                iconTheme: {
                  primary: '#ff4444',
                  secondary: '#0a0e27',
                },
              },
            }}
          />
        </ThemeProvider>
      </QueryClientProvider>
    </ErrorBoundary>
  );
};

export default App;
