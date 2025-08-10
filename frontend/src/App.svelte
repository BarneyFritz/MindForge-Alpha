<script lang="ts">
  import Page from './routes/+page.svelte';
  let demo = false;
  (async () => {
    const res = await fetch('/api/auth/config');
    const cfg = await res.json();
    demo = !cfg.enabled;
  })();
</script>

<svelte:head>
  <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
  <script>mermaid?.initialize?.({ startOnLoad: false });</script>
</svelte:head>

{#if demo}
  <div class="demo-banner">Demo mode: Google login disabled.</div>
{/if}
<Page />

<style>
  .demo-banner {
    background: #fff3cd;
    color: #664d03;
    padding: 8px 12px;
    border-bottom: 1px solid #ffe69c;
    font-size: 14px;
  }
</style>