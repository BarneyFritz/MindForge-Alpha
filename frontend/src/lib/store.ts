import { writable } from 'svelte/store';

export type ModelConfig = {
  id: number;
  name: string;
  provider: string;
  model_id: string;
  temperature: number;
  max_tokens: number;
  enable_expand: boolean;
  enable_critique: boolean;
  enable_synth: boolean;
};

export const projects = writable<{ id: number; name: string; persistent_memory: boolean }[]>([]);
export const models = writable<ModelConfig[]>([]);
export const selectedProjectId = writable<number | null>(null);
export const seed = writable<string>('');
export const context = writable<string>('');
export const sessionResult = writable<any>(null);
export const phaseStatus = writable<string>('idle');