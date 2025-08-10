<script lang="ts">
  export let tabs: { id: string; label: string }[];
  export let current: string;
  export let onSelect: (id: string) => void;
</script>

<div class="tabs">
  {#each tabs as t}
    <button class:active={current === t.id} on:click={() => onSelect(t.id)}>{t.label}</button>
  {/each}
</div>

<style>
  .tabs { display: flex; gap: 8px; border-bottom: 1px solid #eee; margin-top: 8px; }
  .tabs button { padding: 6px 10px; background: transparent; border: none; border-bottom: 2px solid transparent; cursor: pointer; }
  .tabs button.active { border-color: #333; font-weight: 600; }
</style>