<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import { Models } from '$lib/api';

  const dispatch = createEventDispatcher();

  export let open = false;

  let name = '';
  let provider = 'openai';
  let model_id = '';
  let temperature = 0.7;
  let max_tokens = 512;
  let enable_expand = true;
  let enable_critique = true;
  let enable_synth = true;

  async function save() {
    await Models.add({ name, provider, model_id, temperature, max_tokens, enable_expand, enable_critique, enable_synth });
    dispatch('saved');
  }
</script>

{#if open}
  <div style="position:fixed; inset:0; background:#0007; display:flex; align-items:center; justify-content:center;">
    <div style="background:#fff; padding:16px; width:520px; border-radius:8px;">
      <h3>Add model</h3>
      <label>Name</label>
      <input bind:value={name} placeholder="Display name" />

      <label>Provider</label>
      <select bind:value={provider}>
        <option value="openai">OpenAI</option>
        <option value="anthropic">Anthropic</option>
        <option value="gemini">Gemini</option>
        <option value="perplexity">Perplexity</option>
      </select>

      <label>Model ID</label>
      <input bind:value={model_id} placeholder="e.g. gpt-4o-mini" />

      <div style="display:grid; grid-template-columns:1fr 1fr; gap:8px;">
        <div>
          <label>Temperature</label>
          <input type="number" step="0.1" bind:value={temperature} />
        </div>
        <div>
          <label>Max tokens</label>
          <input type="number" bind:value={max_tokens} />
        </div>
      </div>

      <div>
        <label><input type="checkbox" bind:checked={enable_expand} /> Enable Expand</label>
        <label style="margin-left:12px;"><input type="checkbox" bind:checked={enable_critique} /> Enable Critique</label>
        <label style="margin-left:12px;"><input type="checkbox" bind:checked={enable_synth} /> Enable Synth</label>
      </div>

      <div style="display:flex; gap:8px; justify-content:flex-end; margin-top:12px;">
        <button class="button" on:click={() => dispatch('close')}>Cancel</button>
        <button class="button" on:click={save}>Save</button>
      </div>
    </div>
  </div>
{/if}