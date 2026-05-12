type EventCallback = (data?: unknown) => void;

class EventBus {
  private listeners: Map<string, EventCallback[]> = new Map();

  emit(event: string, data?: unknown) {
    const callbacks = this.listeners.get(event);
    if (callbacks) {
      callbacks.forEach(callback => callback(data));
    }
  }

  on(event: string, callback: EventCallback) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, []);
    }
    this.listeners.get(event)!.push(callback);

    return () => {
      const callbacks = this.listeners.get(event);
      if (callbacks) {
        const index = callbacks.indexOf(callback);
        if (index > -1) {
          callbacks.splice(index, 1);
        }
      }
    };
  }
}

export const eventBus = new EventBus();

export const Events = {
  OPEN_SETTINGS: 'open_settings',
  OPEN_USER_PANEL: 'open_user_panel',
  REFRESH_CHARACTER_LIST: 'refresh_character_list'
};
