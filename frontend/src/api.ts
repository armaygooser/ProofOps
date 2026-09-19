import type { DemoState } from './types';

async function request(path: string, options?: RequestInit): Promise<DemoState> {
  const response = await fetch(path, {
    ...options,
    headers: { 'Content-Type': 'application/json', ...options?.headers },
  });
  if (!response.ok) {
    const payload = await response.json().catch(() => ({ detail: '请求失败' }));
    throw new Error(payload.detail ?? `HTTP ${response.status}`);
  }
  return response.json() as Promise<DemoState>;
}

export const demoApi = {
  get: () => request('/api/demo'),
  post: (path: string, body?: object) => request(`/api/demo/${path}`, {
    method: 'POST',
    body: body ? JSON.stringify(body) : undefined,
  }),
};
