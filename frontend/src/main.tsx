import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import App from './App.tsx'
import './index.css'

import { ThemeProvider } from './components/theme/ThemeProvider.tsx'
import { AuthProvider } from './contexts/AuthContext.tsx'
import { WebSocketProvider } from './contexts/WebSocketProvider.tsx'
import { ErrorBoundary } from './components/layout/ErrorBoundary.tsx'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
})

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <ErrorBoundary>
      <ThemeProvider defaultTheme="system" storageKey="sentinelx-ui-theme">
        <QueryClientProvider client={queryClient}>
          <AuthProvider>
            <WebSocketProvider>
              <BrowserRouter>
                <App />
              </BrowserRouter>
            </WebSocketProvider>
          </AuthProvider>
        </QueryClientProvider>
      </ThemeProvider>
    </ErrorBoundary>
  </React.StrictMode>,
)
