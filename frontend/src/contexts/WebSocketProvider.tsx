import React, { createContext, useContext, useEffect, useRef, useState } from "react";
import { useAuth } from "./AuthContext";

type ConnectionStatus = "connecting" | "connected" | "disconnected" | "error";

type WSCallback = (data: unknown) => void;

interface WebSocketContextType {
  status: ConnectionStatus;
  sendMessage: (event: string, payload: unknown) => void;
  subscribe: (event: string, callback: WSCallback) => () => void;
}

const WebSocketContext = createContext<WebSocketContextType | undefined>(undefined);

const WS_URL = import.meta.env.VITE_WS_URL || "ws://localhost:8000/api/v1/ws/dashboard";

export function WebSocketProvider({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, token } = useAuth();
  const [status, setStatus] = useState<ConnectionStatus>("disconnected");
  
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<number | null>(null);
  const subscribersRef = useRef<Map<string, Set<WSCallback>>>(new Map());

  const subscribe = (event: string, callback: WSCallback) => {
    if (!subscribersRef.current.has(event)) {
      subscribersRef.current.set(event, new Set());
    }
    subscribersRef.current.get(event)!.add(callback);

    // Return unsubscribe function
    return () => {
      const callbacks = subscribersRef.current.get(event);
      if (callbacks) {
        callbacks.delete(callback);
        if (callbacks.size === 0) {
          subscribersRef.current.delete(event);
        }
      }
    };
  };

  useEffect(() => {
    if (!isAuthenticated || !token) {
      if (wsRef.current) {
        wsRef.current.close();
        wsRef.current = null;
      }
      setStatus("disconnected");
      return;
    }

    let isSubscribed = true;

    const connect = () => {
      setStatus("connecting");
      
      const ws = new WebSocket(WS_URL, ["bearer", token]);
      
      ws.onopen = () => {
        if (!isSubscribed) return;
      };

      ws.onmessage = (event) => {
        if (!isSubscribed) return;
        try {
          const data = JSON.parse(event.data);
          
          // Dispatch to subscribers
          const eventType = data.event;
          if (eventType === "AUTH_OK") {
            setStatus("connected");
          }
          if (eventType && subscribersRef.current.has(eventType)) {
            subscribersRef.current.get(eventType)!.forEach(cb => cb(data.payload ?? data));
          }
          // Also dispatch to a catch-all listener if needed
          if (subscribersRef.current.has("*")) {
            subscribersRef.current.get("*")!.forEach(cb => cb(data.payload ?? data));
          }
        } catch (e) {
          console.error("Failed to parse WS message", e);
        }
      };

      ws.onclose = () => {
        if (!isSubscribed) return;
        setStatus("disconnected");
        reconnectTimeoutRef.current = window.setTimeout(connect, 3000);
      };

      ws.onerror = () => {
        if (!isSubscribed) return;
        setStatus("error");
      };

      wsRef.current = ws;
    };

    connect();

    return () => {
      isSubscribed = false;
      if (reconnectTimeoutRef.current) clearTimeout(reconnectTimeoutRef.current);
      if (wsRef.current) {
        wsRef.current.close();
        wsRef.current = null;
      }
    };
  }, [isAuthenticated, token]);

  const sendMessage = (event: string, payload: unknown) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({
        schema_version: "1.0",
        event,
        request_id: crypto.randomUUID(),
        timestamp: new Date().toISOString(),
        payload
      }));
    } else {
      console.warn("WebSocket is not connected");
    }
  };

  return (
    <WebSocketContext.Provider value={{ status, sendMessage, subscribe }}>
      {children}
    </WebSocketContext.Provider>
  );
}

// eslint-disable-next-line react-refresh/only-export-components
export const useWebSocket = () => {
  const context = useContext(WebSocketContext);
  if (context === undefined) {
    throw new Error("useWebSocket must be used within a WebSocketProvider");
  }
  return context;
};
