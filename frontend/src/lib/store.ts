import { writable } from 'svelte/store';

export const selectedProjectId = writable<number | null>(null);
export const projects = writable<any[]>([]);
export const models = writable<any[]>([]);

export const seedText = writable('');
export const contextText = writable('');

export const expandModelIds = writable<number[]>([]);
export const critiqueModelIds = writable<number[]>([]);
export const synthModelId = writable<number | null>(null);

export const runResult = writable<any | null>(null);
export const activeTab = writable<'Summary' | 'Ideas' | 'Critiques' | 'Mindmap' | 'Kanban'>('Summary');
export const demoMode = writable<boolean>(true);