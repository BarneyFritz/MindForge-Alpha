<script lang="ts">
  import { onMount } from 'svelte';
  export let summaryMarkdown: string = '';
  let todos: string[] = [];

  function parseActions(md: string) {
    const lines = md.split('\n');
    let capture = false;
    const items: string[] = [];
    for (const line of lines) {
      if (line.toLowerCase().includes('next actions')) { capture = true; continue; }
      if (capture && line.trim().startsWith('-')) items.push(line.replace(/^\s*-\s*/, ''));
      else if (capture && line.trim() && !line.trim().startsWith('-')) break;
    }
    return items;
  }

  $: todos = parseActions(summaryMarkdown);
</script>

<div class="kanban">
  <div class="col">
    <h4>To Do</h4>
    <ul>
      {#each todos as t}
        <li>{t}</li>
      {/each}
    </ul>
  </div>
</div>

<style>
  .kanban { display: grid; grid-template-columns: 1fr; gap: 12px; }
  .col { background: #f9fafb; padding: 8px; border: 1px solid #e5e7eb; border-radius: 6px; }
  ul { list-style: disc; padding-left: 20px; }
</style>