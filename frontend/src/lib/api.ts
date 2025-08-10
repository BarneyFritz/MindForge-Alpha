export async function listProjects() {
  const r = await fetch('/api/projects');
  return r.json();
}

export async function createProject(name: string) {
  const r = await fetch('/api/projects', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ name }) });
  return r.json();
}

export async function patchProject(id: number, payload: any) {
  const r = await fetch(`/api/projects/${id}`, { method: 'PATCH', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
  return r.json();
}

export async function listModels() {
  const r = await fetch('/api/models');
  return r.json();
}

export async function addModel(payload: any) {
  const r = await fetch('/api/models', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
  return r.json();
}

export async function runPipeline(payload: any) {
  const r = await fetch('/api/run', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
  return r.json();
}

export async function exportSession(projectName: string, session: any, formats: string[]) {
  const r = await fetch('/api/export', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ projectName, session, formats }) });
  return r.json();
}