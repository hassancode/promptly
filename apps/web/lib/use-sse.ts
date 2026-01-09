/**
 * SSE (Server-Sent Events) Client Hook
 *
 * React hook for connecting to SSE endpoints and handling real-time events.
 */
import { useEffect, useRef, useState, useCallback } from 'react';

export interface SSEEvent {
  event: string;
  data: any;
}

export interface UseSSEOptions {
  onEvent?: (event: SSEEvent) => void;
  onError?: (error: Error) => void;
  onOpen?: () => void;
  onClose?: () => void;
  reconnectInterval?: number;
  maxReconnectAttempts?: number;
}

export interface UseSSEResult {
  isConnected: boolean;
  error: Error | null;
  reconnect: () => void;
  close: () => void;
}

/**
 * Hook for Server-Sent Events connection
 *
 * @param url - SSE endpoint URL
 * @param options - Configuration options
 * @returns Connection state and control methods
 */
export function useSSE(
  url: string | null,
  options: UseSSEOptions = {}
): UseSSEResult {
  const {
    onEvent,
    onError,
    onOpen,
    onClose,
    reconnectInterval = 3000,
    maxReconnectAttempts = 3,
  } = options;

  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const eventSourceRef = useRef<EventSource | null>(null);
  const reconnectAttemptsRef = useRef(0);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  const close = useCallback(() => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
      eventSourceRef.current = null;
      setIsConnected(false);
      onClose?.();
    }

    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }
  }, [onClose]);

  const connect = useCallback(() => {
    if (!url) return;

    // Close existing connection
    close();

    try {
      const eventSource = new EventSource(url, {
        withCredentials: true, // Include cookies
      });

      eventSourceRef.current = eventSource;

      // Connection opened
      eventSource.onopen = () => {
        setIsConnected(true);
        setError(null);
        reconnectAttemptsRef.current = 0;
        onOpen?.();
      };

      // Generic message handler
      eventSource.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          onEvent?.({ event: 'message', data });
        } catch (e) {
          console.error('Failed to parse SSE message:', e);
        }
      };

      // Error handler
      eventSource.onerror = (err) => {
        const error = new Error('SSE connection error');
        setError(error);
        setIsConnected(false);
        onError?.(error);

        // Close the connection
        eventSource.close();

        // Attempt reconnection
        if (reconnectAttemptsRef.current < maxReconnectAttempts) {
          reconnectAttemptsRef.current++;
          console.log(
            `SSE reconnecting... (attempt ${reconnectAttemptsRef.current}/${maxReconnectAttempts})`
          );

          reconnectTimeoutRef.current = setTimeout(() => {
            connect();
          }, reconnectInterval);
        } else {
          console.error('SSE max reconnection attempts reached');
          close();
        }
      };

      // Custom event listeners
      const eventTypes = [
        'provider_started',
        'provider_completed',
        'provider_failed',
        'progress_update',
        'analysis_complete',
        'error',
      ];

      eventTypes.forEach((eventType) => {
        eventSource.addEventListener(eventType, (event: any) => {
          try {
            const data = JSON.parse(event.data);
            onEvent?.({ event: eventType, data });
          } catch (e) {
            console.error(`Failed to parse ${eventType} event:`, e);
          }
        });
      });
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Failed to connect to SSE');
      setError(error);
      onError?.(error);
    }
  }, [url, onEvent, onError, onOpen, close, reconnectInterval, maxReconnectAttempts]);

  // Connect on mount or when URL changes
  useEffect(() => {
    if (url) {
      connect();
    }

    // Cleanup on unmount
    return () => {
      close();
    };
  }, [url, connect, close]);

  return {
    isConnected,
    error,
    reconnect: connect,
    close,
  };
}
