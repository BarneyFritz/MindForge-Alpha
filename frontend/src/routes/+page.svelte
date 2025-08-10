<script lang="ts">
  import { onMount } from 'svelte';
  import { Projects, Models, Run, Health } from '$lib/api';
  import { projects, selectedProjectId, models, seedText, contextText, expandModelIds, critiqueModelIds, synthModelId, runResult, activeTab, demoMode } from '$lib/store';
  import AddModelModal from '$lib/components/AddModelModal.svelte';
  import Tabs from '$lib/components/Tabs.svelte';
  import Mindmap from '$lib/components/Mindmap.svelte';
  import Kanban from '$lib/components/Kanban.svelte';
  import ExportMenu from '$lib/components/ExportMenu.svelte';

  let showAddModel = false;

  async function refresh() {
    const [ps, ms, keys] = await Promise.all([Projects.list(), Models.list(), Health.keys()]);
    projects.set(ps);
    if (ps.length && $selectedProjectId == null) selectedProjectId.set(ps[0].id);
    models.set(ms);
    demoMode.set(!keys.google_oauth);
  }

  onMount(async () => {
    await Models.seed();
    await refresh();
  });

  async function createProject() {
    const name = prompt('Project name?');
    if (!name) return;
    await Projects.create(name);
    await refresh();
  }

  async function runBrainstorm() {
    if ($selectedProjectId == null) { alert('Select a project'); return; }
    const body = {
      projectId: $selectedProjectId,
      seed: $seedText,
      context: $contextText,
      models: { expand: $expandModelIds, critique: $critiqueModelIds, synth: $synthModelId },
      persist: true
    };
    const res = await Run.run(body);
    runResult.set(res);
    activeTab.set('Summary');
  }
</script>

<div class="container">
  <div class="sidebar">
    {#if $demoMode}
      <div style="background:#fff7d6; border:1px solid #eed37a; padding:8px; border-radius:6px; margin-bottom:8px;">Demo mode: Google login disabled.</div>
    {/if}

    <h3>Projects</h3>
    <div>
      <button class="button" on:click={createProject}>+ Create</button>
    </div>
    <div>
      {#each $projects as p}
        <div>
          <label>
            <input type="radio" name="project" value={p.id} checked={p.id === $selectedProjectId} on:change={() => selectedProjectId.set(p.id)} />
            {p.name}
          </label>
        </div>
      {/each}
    </div>

    <hr />

    <h3>Models</h3>
    <div style="margin-bottom:8px;">
      <button class="button" on:click={() => showAddModel = true}>+ Add model</button>
    </div>
    <div>
      <div><strong>Expand</strong></div>
      {#each $models as m}
        <label><input type="checkbox" checked={$expandModelIds.includes(m.id)} on:change={(e) => expandModelIds.update(x => e.target.checked ? Array.from(new Set([...x, m.id])) : x.filter(id => id!==m.id))} /> {m.name} <span class="badge">{m.provider}</span></label>
      {/each}
    </div>
    <div style="margin-top:8px;">
      <div><strong>Critique</strong></div>
      {#each $models as m}
        <label><input type="checkbox" checked={$critiqueModelIds.includes(m.id)} on:change={(e) => critiqueModelIds.update(x => e.target.checked ? Array.from(new Set([...x, m.id])) : x.filter(id => id!==m.id))} /> {m.name} <span class="badge">{m.provider}</span></label>
      {/each}
    </div>
    <div style="margin-top:8px;">
      <div><strong>Synthesis</strong></div>
      <select bind:value={$synthModelId}>
        <option value={null}>Select…</option>
        {#each $models as m}
          <option value={m.id}>{m.name} ({m.provider})</option>
        {/each}
      </select>
    </div>
  </div>

  <div class="main">
    <h2>MindForge Brainstormer</h2>

    <div style="display:grid; grid-template-columns:1fr 1fr; gap:8px;">
      <div>
        <label>Seed</label>
        <textarea rows="6" bind:value={$seedText} placeholder="Problem seed…"></textarea>
      </div>
      <div>
        <label>Context (optional)</label>
        <textarea rows="6" bind:value={$contextText} placeholder="Constraints, audience, goals…"></textarea>
      </div>
    </div>

    <div style="margin:8px 0; display:flex; gap:8px;">
      <button class="button" on:click={runBrainstorm}>Run Brainstorm</button>
    </div>

    <Tabs {active}={ $activeTab } {tabs}={['Summary','Ideas','Critiques','Mindmap','Kanban']} onSelect={(t)=>activeTab.set(t)} />

    {#if $runResult}
      {#if $activeTab === 'Summary'}
        <ExportMenu projectName={`project-${$selectedProjectId}`} payload={$runResult} />
        <div class="content" style="white-space:pre-wrap;">{$runResult.summary?.markdown || 'No summary yet.'}</div>
      {:else if $activeTab === 'Ideas'}
        <ul>
          {#each $runResult.ideas as idea}
            <li>
              <div class="badge">{idea.modelRef}</div>
              <div style="white-space:pre-wrap;">{idea.text}</div>
            </li>
          {/each}
        </ul>
      {:else if $activeTab === 'Critiques'}
        <ul>
          {#each $runResult.critiques as c}
            <li>
              <div class="badge">Idea {c.ideaId}</div>
              <div class="badge">{c.criticRef}</div>
              <div style="white-space:pre-wrap;">{c.text}</div>
            </li>
          {/each}
        </ul>
      {:else if $activeTab === 'Mindmap'}
        <Mindmap mermaidSrc={$runResult.mermaid} />
      {:else if $activeTab === 'Kanban'}
        <Kanban summaryMarkdown={$runResult.summary?.markdown || ''} />
      {/if}
    {:else}
      <div>Run a brainstorm to see results.</div>
    {/if}
  </div>
</div>

<AddModelModal bind:open={showAddModel} on:close={() => showAddModel=false} on:saved={() => { showAddModel=false; refresh(); }} />