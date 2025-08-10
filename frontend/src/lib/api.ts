export async function api<T>(path: string, options: RequestInit = {}): Promise<T> {
  const res = await fetch(`/api${path}`, {
    headers: { 'Content-Type': 'application/json', ...(options.headers || {}) },
    credentials: 'include',
    ...options
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export const Projects = {
  list: () => api<any[]>(`/projects`),
  create: (name: string) => api(`/projects`, { method: 'POST', body: JSON.stringify({ name }) }),
  update: (id: number, data: any) => api(`/projects/${id}`, { method: 'PATCH', body: JSON.stringify(data) })
};

export const Models = {
  list: () => api<any[]>(`/models`),
  add: (data: any) => api(`/models`, { method: 'POST', body: JSON.stringify(data) }),
  seed: () => api(`/models/seed`, { method: 'POST' })
};

export const Run = {
  run: (body: any) => api(`/run`, { method: 'POST', body: JSON.stringify(body) })
};

export const Exports = {
  export: (project: string, payload: any, formats: string[]) => api(`/export`, { method: 'POST', body: JSON.stringify({ project, payload, formats }) })
};

export const Health = {
  status: () => api(`/health`),
  keys: () => api(`/test-keys`)
};