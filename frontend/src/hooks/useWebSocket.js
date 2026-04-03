import { useState, useEffect, useCallback, useRef } from 'react';

export default function useWebSocket(channel) {
  const [data, setData] = useState(null);
  const [isConnected, setIsConnected] = useState(false);
  const [lastMessage, setLastMessage] = useState(null);
  const socketRef = useRef(null);
  const reconnectTimeoutRef = useRef(null);

  const connect = useCallback(() => {
    const url = `ws://localhost:8000/ws/${channel}`;
    const socket = new WebSocket(url);

    socket.onopen = () => {
      setIsConnected(true);
      console.log(`WS: Connected to ${channel}`);
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
    };

    socket.onmessage = (event) => {
      try {
        const parsed = JSON.parse(event.data);
        setData(parsed);
        setLastMessage(parsed);
      } catch (err) {
        console.error('WS: Message parsing error:', err);
      }
    };

    socket.onclose = () => {
      setIsConnected(false);
      console.log(`WS: Disconnected from ${channel}, reconnecting in 3s...`);
      reconnectTimeoutRef.current = setTimeout(() => {
        connect();
      }, 3000);
    };

    socket.onerror = (err) => {
      console.error('WS: Error:', err);
      socket.close();
    };

    socketRef.current = socket;
  }, [channel]);

  useEffect(() => {
    connect();
    return () => {
      if (socketRef.current) {
        socketRef.current.close();
      }
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
    };
  }, [connect]);

  return { data, isConnected, lastMessage };
}
