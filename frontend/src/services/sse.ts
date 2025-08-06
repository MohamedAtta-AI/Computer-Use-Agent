export interface SSEEvent {
  type: string;
  [key: string]: any;
}

export interface SSECallbacks {
  onMessage?: (event: SSEEvent) => void;
  onOpen?: () => void;
  onClose?: () => void;
  onError?: (error: Event) => void;
}

class SSEService {
  private eventSources: Map<string, EventSource> = new Map();
  private callbacks: Map<string, SSECallbacks> = new Map();
  private reconnectAttempts: Map<string, number> = new Map();
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000;

  connect(taskId: string, callbacks: SSECallbacks = {}): Promise<void> {
    // If already connected to this task, just update callbacks
    if (this.eventSources.has(taskId)) {
      this.callbacks.set(taskId, callbacks);
      return Promise.resolve();
    }

    this.callbacks.set(taskId, callbacks);
    this.reconnectAttempts.set(taskId, 0);

    return new Promise((resolve, reject) => {
      try {
        const eventSource = new EventSource(`http://localhost:8000/tasks/${taskId}/stream`);
        this.eventSources.set(taskId, eventSource);

        eventSource.onopen = () => {
          console.log('SSE connected for task:', taskId);
          this.reconnectAttempts.set(taskId, 0);
          callbacks.onOpen?.();
          resolve();
        };

        eventSource.onmessage = (event) => {
          try {
            console.log('SSE raw message received:', event.data);
            const data: SSEEvent = JSON.parse(event.data);
            console.log('SSE parsed message:', data);
            callbacks.onMessage?.(data);
          } catch (error) {
            console.error('Failed to parse SSE message:', error);
          }
        };

        eventSource.onerror = (error) => {
          console.error('SSE error for task:', taskId, error);
          callbacks.onError?.(error);
          
          // EventSource automatically reconnects, but we can track attempts
          if (eventSource.readyState === EventSource.CLOSED) {
            const attempts = this.reconnectAttempts.get(taskId) || 0;
            this.reconnectAttempts.set(taskId, attempts + 1);
            
            if (attempts >= this.maxReconnectAttempts) {
              this.disconnectTask(taskId);
              callbacks.onClose?.();
            }
          }
        };

      } catch (error) {
        console.error('Failed to create SSE connection for task:', taskId, error);
        reject(error);
      }
    });
  }

  disconnectTask(taskId: string): void {
    const eventSource = this.eventSources.get(taskId);
    if (eventSource) {
      eventSource.close();
      this.eventSources.delete(taskId);
      this.callbacks.delete(taskId);
      this.reconnectAttempts.delete(taskId);
      console.log('SSE disconnected for task:', taskId);
    }
  }

  disconnect(): void {
    // Disconnect all connections
    for (const [taskId, eventSource] of this.eventSources) {
      eventSource.close();
      console.log('SSE disconnected for task:', taskId);
    }
    this.eventSources.clear();
    this.callbacks.clear();
    this.reconnectAttempts.clear();
  }

  isConnected(taskId?: string): boolean {
    if (taskId) {
      const eventSource = this.eventSources.get(taskId);
      return eventSource?.readyState === EventSource.OPEN;
    }
    return this.eventSources.size > 0;
  }

  getConnectedTasks(): string[] {
    return Array.from(this.eventSources.keys());
  }
}

// Create singleton instance
export const sseService = new SSEService();
export default sseService; 