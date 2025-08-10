<script lang="ts">
  import { onMount } from 'svelte';
  export let mermaidSrc: string = '';
  let container: HTMLDivElement;
  let showSource = false;

  async function render() {
    // @ts-ignore
    if (window.mermaid && mermaidSrc) {
      // @ts-ignore
      await window.mermaid.render('mindmap', mermaidSrc, (svg: string) => {
        container.innerHTML = svg;
      });
    }
  }

  $: mermaidSrc, render();
</script>

<div class="mindmap">
  <div class="actions">
    <label><input type="checkbox" bind:checked={showSource}/> View source</label>
    {#if mermaidSrc}
    <a href={`data:text/plain;charset=utf-8,${encodeURIComponent(mermaidSrc)}`} download="mindmap.mmd">Export .mmd</a>
    {/if}
  </div>
  {#if showSource}
    <pre><code>{mermaidSrc}</code></pre>
  {/if}
  <div bind:this={container}></div>
</div>

<style>
  .mindmap .actions { display: flex; gap: 12px; align-items: center; margin-bottom: 8px; }
  pre { background: #f7f7f7; padding: 8px; overflow: auto; }
</style>