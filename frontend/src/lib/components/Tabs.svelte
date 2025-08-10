<script lang="ts">
  export let tabs: string[] = [];
  export let active: string;
  export let onSelect: (t: string) => void;
</script>

<div style="display:flex; gap:8px; border-bottom:1px solid #eee; margin-bottom:8px;">
  {#each tabs as t}
    <div class="tab {t===active ? 'active' : ''}" on:click={() => onSelect(t)}>{t}</div>
  {/each}
</div>