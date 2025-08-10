import { svelte } from '@sveltejs/vite-plugin-svelte';
import { defineConfig } from 'vite';

export default defineConfig({
  plugins: [svelte()],
  server: {
    port: 5173,
    proxy: {
      '/auth': 'http://127.0.0.1:8000',
      '/projects': 'http://127.0.0.1:8000',
      '/brainstorm': 'http://127.0.0.1:8000',
      '/export': 'http://127.0.0.1:8000'
    }
  }
});