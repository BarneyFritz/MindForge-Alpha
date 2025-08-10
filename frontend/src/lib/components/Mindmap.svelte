<script lang="ts">
  import { onMount } from 'svelte';
  export let mermaidSrc: string = '';
  let showSource = false;

  function render() {
    // @ts-ignore
    if (window.mermaid && mermaidSrc) {
      // @ts-ignore
      window.mermaid.initialize({ startOnLoad: false });
      const el = document.getElementById('mermaid');
      if (el) {
        // @ts-ignore
        window.mermaid.render('graphDiv', mermaidSrc, (svg: string) => {
          el.innerHTML = svg;
        });
      }
    }
  }

  onMount(render);
  $: mermaidSrc, render();
</script>

<div style="margin-bottom:8px;">
  <label><input type="checkbox" bind:checked={showSource} /> View source</label>
</div>
<div id="mermaid"></div>
{#if showSource}
  <pre style="white-space:pre-wrap; border:1px solid #eee; padding:8px;">{mermaidSrc}</pre>
{/if}