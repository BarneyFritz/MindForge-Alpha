<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  export let session: any;
  export let projectName: string;
  const dispatch = createEventDispatcher();

  async function exportAll(fmt: string) {
    dispatch('export', { fmt });
  }
</script>

<div class="export-menu">
  <span>Export to:</span>
  <button on:click={() => exportAll('md')}>Markdown</button>
  <button on:click={() => exportAll('json')}>JSON</button>
  <button on:click={() => exportAll('mmd')}>Mermaid</button>
  <button on:click={() => exportAll('csv')}>CSV Actions</button>
</div>

<style>
  .export-menu { display: flex; gap: 8px; align-items: center; }
  .export-menu button { padding: 4px 8px; }
</style>