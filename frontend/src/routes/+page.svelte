<script lang="ts">
  import { onMount } from 'svelte';
  import { projects, models, selectedProjectId, seed, context, sessionResult, phaseStatus } from '$lib/store';
  import { listProjects, createProject, patchProject, listModels, addModel, runPipeline, exportSession } from '$lib/api';
  import AddModelModal from '$lib/components/AddModelModal.svelte';
  import Tabs from '$lib/components/Tabs.svelte';
  import Mindmap from '$lib/components/Mindmap.svelte';
  import Kanban from '$lib/components/Kanban.svelte';
  import ExportMenu from '$lib/components/ExportMenu.svelte';

  let showModal = false;
  let tab = 'summary';
  let projectName = '';

  let expand: number[] = [];
  let critique: number[] = [];
  let synth: number | null = null;

  onMount(async () => {
    const ps = await listProjects();
    projects.set(ps);
    if (ps.length === 0) {
      const p = await createProject('Default Project');
      projects.set([p]);
      selectedProjectId.set(p.id);
      projectName = p.name;
    } else {
      selectedProjectId.set(ps[0].id);
      projectName = ps[0].name;
    }
    const ms = await listModels();
    models.set(ms);
  });

  function togglePhase(list: number[], id: number) {
    if (list.includes(id)) return list.filter(x => x !== id);
    return [...list, id];
  }

  async function doRun(kind: 'full' | 'critique' | 'synth') {
    phaseStatus.set('running');
    const payload: any = {
      projectId: get(selectedProjectId) ?? 1,
      seed: get(seed),
      context: get(context),
      models: { expand: [], critique: [], synth: null },
      persist: false,
    };
    if (kind === 'full') {
      payload.models.expand = expand;
      payload.models.critique = critique;
      payload.models.synth = synth;
    } else if (kind === 'critique') {
      payload.models.expand = [];
      payload.models.critique = critique;
      payload.models.synth = synth;
    } else if (kind === 'synth') {
      payload.models.expand = [];
      payload.models.critique = [];
      payload.models.synth = synth;
    }
    const res = await runPipeline(payload);
    sessionResult.set(res);
    phaseStatus.set('idle');
    tab = 'summary';
  }

  import { get } from 'svelte/store';
  import { models as modelsStore } from '$lib/store';

  function onAddModelSave(e: CustomEvent) {
    addModel(e.detail).then(async () => {
      const ms = await listModels();
      models.set(ms);
    })
  }

  async function onExport(e: CustomEvent) {
    const fmt = e.detail.fmt;
    const sess = get(sessionResult);
    if (!sess) return;
    const out = await exportSession(projectName || 'project', sess, [fmt]);
    alert('Exported: ' + out.paths.join(', '));
  }
</script>

<div class="layout">
  <aside>
    <h3>Project</h3>
    <button on:click={async () => { const p = await createProject('Project ' + Math.floor(Math.random()*1000)); projects.update(x=>[...x,p]); selectedProjectId.set(p.id); projectName = p.name; }}>+ New</button>
    <div class="models">
      <div class="head">
        <h3>Models</h3>
        <button on:click={() => showModal = true}>+ Add model</button>
      </div>
      {#await listModels() then ms}
        {#each ms as m}
          <div class="model">
            <div class="title">{m.name} <span class="badge">{m.provider}</span></div>
            <div class="toggles">
              <label><input type="checkbox" on:change={() => expand = togglePhase(expand, m.id)} /> Expand</label>
              <label><input type="checkbox" on:change={() => critique = togglePhase(critique, m.id)} /> Critique</label>
              <label><input type="radio" name="synth" on:change={() => synth = m.id} /> Synth</label>
            </div>
          </div>
        {/each}
      {/await}
    </div>
  </aside>
  <main>
    <div class="inputs">
      <textarea placeholder="Seed" bind:value={$seed}></textarea>
      <textarea placeholder="Context (optional)" bind:value={$context}></textarea>
      <div class="actions">
        <button on:click={() => doRun('full')}>Run Brainstorm</button>
        <button on:click={() => doRun('critique')}>Run Critique Only</button>
        <button on:click={() => doRun('synth')}>Run Synthesis Only</button>
      </div>
    </div>

    <Tabs {tabs}={[
      { id: 'summary', label: 'Summary' },
      { id: 'ideas', label: 'Ideas' },
      { id: 'critiques', label: 'Critiques' },
      { id: 'mindmap', label: 'Mindmap' },
      { id: 'kanban', label: 'Kanban' },
    ]} bind:current={tab} onSelect={(id) => tab = id} />

    {#if $sessionResult}
      <div class="topbar">
        <ExportMenu session={$sessionResult} {projectName} on:export={onExport} />
      </div>
      {#if tab === 'summary'}
        <div class="markdown">{$sessionResult.summary?.markdown}</div>
      {:else if tab === 'ideas'}
        <ul>{#each $sessionResult.ideas as i}<li><b>{i.modelRef}</b>: {i.text}</li>{/each}</ul>
      {:else if tab === 'critiques'}
        <ul>{#each $sessionResult.critiques as c}<li>Idea {c.ideaId} by <b>{c.criticRef}</b>: {c.text}</li>{/each}</ul>
      {:else if tab === 'mindmap'}
        <Mindmap mermaidSrc={$sessionResult.mermaid} />
      {:else if tab === 'kanban'}
        <Kanban summaryMarkdown={$sessionResult.summary?.markdown || ''} />
      {/if}
    {:else}
      <div class="placeholder">Run a session to see results.</div>
    {/if}
  </main>
</div>

<AddModelModal bind:show={showModal} on:save={onAddModelSave} />

<style>
  .layout { display: grid; grid-template-columns: 320px 1fr; min-height: 100vh; }
  aside { padding: 12px; border-right: 1px solid #eee; display: grid; gap: 12px; }
  main { padding: 12px; }
  .models .head { display: flex; align-items: center; justify-content: space-between; }
  .model { border: 1px solid #eee; padding: 8px; border-radius: 6px; margin-bottom: 8px; }
  .title { font-weight: 600; margin-bottom: 6px; }
  .badge { font-size: 12px; padding: 2px 6px; background: #f3f4f6; border-radius: 999px; }
  .toggles { display: flex; gap: 10px; align-items: center; }
  .inputs { display: grid; gap: 8px; }
  textarea { min-height: 80px; padding: 8px; }
  .actions { display: flex; gap: 8px; }
  .topbar { display: flex; justify-content: flex-end; margin: 8px 0; }
  .placeholder { color: #999; }
</style>