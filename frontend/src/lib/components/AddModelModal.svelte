<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  const dispatch = createEventDispatcher();

  export let show = false;
  let name = '';
  let provider = 'openai';
  let model_id = '';
  let temperature = 0.7;
  let max_tokens = 1000;
  let enable_expand = true;
  let enable_critique = true;
  let enable_synth = true;

  function close() { show = false; dispatch('close'); }
  async function save() {
    dispatch('save', { name, provider, model_id, temperature, max_tokens, enable_expand, enable_critique, enable_synth });
    close();
  }
</script>

{#if show}
  <div class="overlay" on:click|self={close}>
    <div class="modal">
      <h3>Add Model</h3>
      <label>Name <input bind:value={name} /></label>
      <label>Provider
        <select bind:value={provider}>
          <option value="openai">OpenAI</option>
          <option value="anthropic">Anthropic</option>
          <option value="gemini">Gemini</option>
          <option value="perplexity">Perplexity</option>
        </select>
      </label>
      <label>Model ID <input bind:value={model_id} placeholder="e.g. gpt-4o-mini"/></label>
      <label>Temperature <input type="number" step="0.1" min="0" max="2" bind:value={temperature} /></label>
      <label>Max tokens <input type="number" min="1" bind:value={max_tokens} /></label>
      <div class="toggles">
        <label><input type="checkbox" bind:checked={enable_expand}/> Expand</label>
        <label><input type="checkbox" bind:checked={enable_critique}/> Critique</label>
        <label><input type="checkbox" bind:checked={enable_synth}/> Synthesis</label>
      </div>
      <div class="actions">
        <button on:click={close}>Cancel</button>
        <button class="primary" on:click={save}>Save</button>
      </div>
    </div>
  </div>
{/if}

<style>
  .overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.35); display: grid; place-items: center; }
  .modal { background: white; padding: 16px; width: 360px; max-width: 90vw; border-radius: 8px; display: grid; gap: 8px; }
  .modal h3 { margin: 0 0 8px; }
  label { display: grid; gap: 4px; font-size: 14px; }
  input, select { padding: 6px 8px; border: 1px solid #ccc; border-radius: 4px; }
  .toggles { display: flex; gap: 12px; margin-top: 4px; }
  .actions { display: flex; justify-content: flex-end; gap: 8px; margin-top: 8px; }
  .primary { background: #111827; color: white; padding: 6px 10px; border-radius: 4px; }
</style>