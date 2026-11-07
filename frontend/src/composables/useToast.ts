import { ref } from 'vue';

export type ToastType = 'success' | 'error' | 'info' | 'warning';

export interface Toast {
  id: string;
  type: ToastType;
  title: string;
  message?: string;
  duration?: number;
}

const toasts = ref<Toast[]>([]);

export function useToast() {
  function addToast(type: ToastType, title: string, message?: string, duration = 4000) {
    const id = Math.random().toString(36).substring(2, 9);
    const toast: Toast = { id, type, title, message, duration };
    toasts.value.push(toast);

    if (duration > 0) {
      setTimeout(() => {
        removeToast(id);
      }, duration);
    }
    return id;
  }

  function removeToast(id: string) {
    toasts.value = toasts.value.filter(t => t.id !== id);
  }

  return {
    toasts,
    addToast,
    removeToast,
    success: (title: string, message?: string, duration = 4000) => addToast('success', title, message, duration),
    error: (title: string, message?: string, duration = 5000) => addToast('error', title, message, duration),
    info: (title: string, message?: string, duration = 4000) => addToast('info', title, message, duration),
    warning: (title: string, message?: string, duration = 4000) => addToast('warning', title, message, duration),
  };
}
