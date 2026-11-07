import { ref, computed } from 'vue';

export type Theme = 'light' | 'dark';

const theme = ref<Theme>('light');

export function useTheme() {
  function initTheme() {
    const saved = localStorage.getItem('lms_theme') as Theme | null;
    if (saved === 'dark' || saved === 'light') {
      theme.value = saved;
    } else {
      // Default to education light theme
      theme.value = 'light';
    }
    applyTheme(theme.value);
  }

  function applyTheme(t: Theme) {
    const root = document.documentElement;
    if (t === 'dark') {
      root.classList.add('dark');
      root.setAttribute('data-theme', 'dark');
    } else {
      root.classList.remove('dark');
      root.setAttribute('data-theme', 'light');
    }
    localStorage.setItem('lms_theme', t);
  }

  function toggleTheme() {
    theme.value = theme.value === 'dark' ? 'light' : 'dark';
    applyTheme(theme.value);
  }

  function setTheme(t: Theme) {
    theme.value = t;
    applyTheme(t);
  }

  return {
    theme,
    isDark: computed(() => theme.value === 'dark'),
    toggleTheme,
    setTheme,
    initTheme,
  };
}
