<script lang="ts">
  import { Exports } from '$lib/api';
  export let projectName: string = 'project';
  export let payload: any = null;
  let open = false;

  async function doExport(fmt: string) {
    if (!payload) return;
    const res = await Exports.export(projectName, payload, [fmt]);
    alert('Exported:\n' + res.paths.join('\n'));
  }
</script>

<div style="position:relative;">
  <button class="button" on:click={() => open = !open}>Export to…</button>
  {#if open}
    <div style="position:absolute; background:#fff; border:1px solid #ddd; border-radius:6px; padding:6px; z-index:5;">
      <div class="button" on:click={() => doExport('md')}>Markdown</div>
      <div class="button" on:click={() => doExport('json')}>JSON</div>
      <div class="button" on:click={() => doExport('mmd')}>Mermaid (.mmd)</div>
      <div class="button" on:click={() => doExport('csv')}>CSV (actions)</div>
    </div>
  {/if}
</div>