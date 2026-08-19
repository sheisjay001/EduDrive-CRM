import { useEffect, useState } from "react";

interface Notification {
  id: string;
  type: "success" | "error" | "warning" | "info";
  title: string;
  message: string;
  timestamp: Date;
  read: boolean;
  actionUrl?: string;
}

export function useNotifications() {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    // Simulate WebSocket connection for real-time notifications
    // In production, this would connect to a real WebSocket server
    const mockWebSocket = {
      connect: () => {
        setIsConnected(true);
        console.log("WebSocket connected");
        
        // Simulate receiving notifications
        const interval = setInterval(() => {
          const randomNotification = Math.random() > 0.7;
          if (randomNotification) {
            const newNotification: Notification = {
              id: Math.random().toString(36).substr(2, 9),
              type: ["success", "error", "warning", "info"][Math.floor(Math.random() * 4)] as any,
              title: "System Notification",
              message: `This is a simulated notification at ${new Date().toLocaleTimeString()}`,
              timestamp: new Date(),
              read: false,
            };
            
            setNotifications(prev => [newNotification, ...prev]);
            setUnreadCount(prev => prev + 1);
          }
        }, 30000); // Check every 30 seconds
        
        return () => clearInterval(interval);
      },
      disconnect: () => {
        setIsConnected(false);
        console.log("WebSocket disconnected");
      },
    };

    mockWebSocket.connect();

    return () => {
      mockWebSocket.disconnect();
    };
  }, []);

  const markAsRead = (notificationId: string) => {
    setNotifications(prev => 
      prev.map(notif => 
        notif.id === notificationId ? { ...notif, read: true } : notif
      )
    );
    setUnreadCount(prev => Math.max(0, prev - 1));
  };

  const markAllAsRead = () => {
    setNotifications(prev => 
      prev.map(notif => ({ ...notif, read: true }))
    );
    setUnreadCount(0);
  };

  const deleteNotification = (notificationId: string) => {
    setNotifications(prev => 
      prev.filter(notif => notif.id !== notificationId)
    );
    if (!notifications.find(n => n.id === notificationId)?.read) {
      setUnreadCount(prev => Math.max(0, prev - 1));
    }
  };

  const clearAll = () => {
    setNotifications([]);
    setUnreadCount(0);
  };

  return {
    notifications,
    unreadCount,
    isConnected,
    markAsRead,
    markAllAsRead,
    deleteNotification,
    clearAll,
  };
}
