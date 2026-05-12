import axios, { AxiosInstance } from 'axios';
import { 
  ComfyUIWorkflow, 
  QueuePromptResponse, 
  UploadResponse, 
  HistoryEntry,
  WebSocketMessage 
} from '@/types';

export interface WebSocketCallbacks {
  onProgress?: (data: { value: number; max: number }) => void;
  onExecuting?: (node: string) => void;
  onExecuted?: (node: string, output: any) => void;
  onError?: (error: any) => void;
  onClose?: (event: CloseEvent) => void;
}

export class ComfyUIClient {
  private baseURL: string;
  private wsURL: string;
  private clientId: string;
  private client: AxiosInstance;
  private ws: WebSocket | null = null;
  private wsCallbacks: WebSocketCallbacks | null = null;
  private wsReconnectTimer: ReturnType<typeof setTimeout> | null = null;
  private wsReconnectAttempts = 0;
  private static WS_MAX_RECONNECT = 5;
  private static WS_RECONNECT_DELAY = 3000;

  constructor(baseURL: string = 'http://127.0.0.1:8188') {
    this.baseURL = baseURL;
    this.wsURL = baseURL.replace('http://', 'ws://').replace('https://', 'wss://');
    this.clientId = this.generateClientId();
    this.client = axios.create({
      baseURL: this.baseURL,
      timeout: 30000,
    });
  }

  private generateClientId(): string {
    return `client_${Math.random().toString(36).substring(2, 15)}`;
  }

  async queuePrompt(workflow: ComfyUIWorkflow): Promise<string> {
    const response = await this.client.post<QueuePromptResponse>('/prompt', {
      prompt: workflow,
      client_id: this.clientId,
    });
    return response.data.prompt_id;
  }

  async uploadImage(file: File): Promise<UploadResponse> {
    const formData = new FormData();
    formData.append('image', file);
    
    const response = await this.client.post<UploadResponse>('/upload/image', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    
    return response.data;
  }

  async getHistory(promptId: string): Promise<HistoryEntry> {
    const response = await this.client.get<Record<string, HistoryEntry>>(`/history/${promptId}`);
    return response.data[promptId];
  }

  async interrupt(): Promise<void> {
    await this.client.post('/interrupt');
  }

  async clearQueue(): Promise<void> {
    await this.client.post('/queue', { clear: true });
  }

  getImageUrl(filename: string, subfolder: string = '', type: string = 'output'): string {
    const params = new URLSearchParams({ filename, subfolder, type });
    return `${this.baseURL}/view?${params}`;
  }

  connectWebSocket(callbacks: WebSocketCallbacks): WebSocket {
    this.wsCallbacks = callbacks;
    this.ws = new WebSocket(`${this.wsURL}/ws?clientId=${this.clientId}`);
    
    this.ws.onmessage = (event) => {
      if (typeof event.data !== 'string') return;
      try {
        const message: WebSocketMessage = JSON.parse(event.data);
        
        switch (message.type) {
          case 'progress':
            this.wsCallbacks?.onProgress?.(message.data as { value: number; max: number });
            break;
          case 'executing':
            this.wsCallbacks?.onExecuting?.((message.data as { node: string }).node);
            break;
          case 'executed':
            const executedData = message.data as { node: string; output: any };
            this.wsCallbacks?.onExecuted?.(executedData.node, executedData.output);
            break;
          case 'execution_error':
            this.wsCallbacks?.onError?.(message.data);
            break;
        }
      } catch (err) {
        console.error('WebSocket message parse error:', err);
      }
    };
    
    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      this.wsCallbacks?.onError?.(error);
    };

    this.ws.onclose = (event) => {
      if (!event.wasClean && this.wsCallbacks) {
        console.warn('WebSocket disconnected unexpectedly:', event.code, event.reason);
        this.wsCallbacks?.onClose?.(event);
        this.scheduleReconnect();
      }
      this.ws = null;
    };
    
    return this.ws;
  }

  disconnectWebSocket(): void {
    if (this.wsReconnectTimer) {
      clearTimeout(this.wsReconnectTimer);
      this.wsReconnectTimer = null;
      this.wsReconnectAttempts = 0;
    }
    if (this.ws) {
      this.ws.onclose = null;
      this.ws.close();
      this.ws = null;
    }
  }

  private scheduleReconnect(): void {
    if (this.wsReconnectAttempts >= ComfyUIClient.WS_MAX_RECONNECT) {
      console.error('WebSocket max reconnect attempts reached');
      return;
    }
    this.wsReconnectAttempts++;
    const delay = ComfyUIClient.WS_RECONNECT_DELAY * this.wsReconnectAttempts;
    console.warn(`WebSocket reconnecting in ${delay}ms (attempt ${this.wsReconnectAttempts}/${ComfyUIClient.WS_MAX_RECONNECT})`);
    this.wsReconnectTimer = setTimeout(() => {
      if (this.wsCallbacks) {
        this.connectWebSocket(this.wsCallbacks);
        this.wsReconnectAttempts = 0;
      }
    }, delay);
  }

  getClientId(): string {
    return this.clientId;
  }
}

export const comfyUIClient = new ComfyUIClient();
