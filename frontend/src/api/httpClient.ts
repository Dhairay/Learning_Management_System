// HTTP Client with automatic Authorization and Organization Context headers
const API_BASE_URL = '/api/v1';

export async function apiRequest<T = any>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const token = localStorage.getItem('access_token');
  const orgSlug = localStorage.getItem('current_org_slug');

  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string> || {}),
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  if (orgSlug) {
    headers['X-Organization-Slug'] = orgSlug;
  }

  const url = endpoint.startsWith('http') ? endpoint : `${API_BASE_URL}${endpoint.startsWith('/') ? endpoint : '/' + endpoint}`;

  const response = await fetch(url, {
    ...options,
    headers,
  });

  if (response.status === 401) {
    // If token invalid, clear and emit or redirect
    const refreshToken = localStorage.getItem('refresh_token');
    if (refreshToken && !endpoint.includes('token/refresh')) {
      try {
        const refreshResp = await fetch(`${API_BASE_URL}/auth/token/refresh/`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ refresh: refreshToken }),
        });
        if (refreshResp.ok) {
          const data = await refreshResp.json();
          localStorage.setItem('access_token', data.access);
          headers['Authorization'] = `Bearer ${data.access}`;
          const retryResp = await fetch(url, { ...options, headers });
          if (!retryResp.ok) {
            const err = await retryResp.json().catch(() => ({ detail: 'Request failed' }));
            throw new Error(err.detail || 'Request failed');
          }
          return retryResp.json();
        }
      } catch (e) {
        // Fall through
      }
    }
  }

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ detail: `Error ${response.status}: ${response.statusText}` }));
    const message = errorData.detail || errorData.message || (typeof errorData === 'object' 
      ? Object.entries(errorData).map(([k, v]) => `${k}: ${Array.isArray(v) ? v.join(' ') : v}`).join(' | ') 
      : 'An unexpected error occurred');
    throw new Error(message);
  }

  if (response.status === 204) {
    return {} as T;
  }

  return response.json();
}
