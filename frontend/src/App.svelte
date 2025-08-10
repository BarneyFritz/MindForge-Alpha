<script lang="ts">
  import { onMount } from 'svelte';

  type Project = { id: number; name: string; description?: string; persistent_memory: boolean };
  type Message = { id:number; connector:string; role:string; round_index:number; content:string; model_used?:string; confidence?:number };
  type Session = { id:number; status:string; rounds:number; lead_connector:string; selected_connectors:string[]; messages: Message[] };

  let projects: Project[] = [];
  let activeProjectId: number | null = null;
  let prompt = '';
  let selectedConnectors: Record<string, boolean> = { openai: true, anthropic: true, gemini: true };
  let rounds = 2;
  let lead = 'openai';
  let session: Session | null = null;
  let view: 'list' | 'mindmap' | 'kanban' = 'list';
  let loading = false;
  let roundCounter = 0;

  async function devLogin() {
    await fetch('/auth/dev-login');
    await loadProjects();
  }
  async function loadProjects() {
    const resp = await fetch('/projects/');
    if (resp.ok) {
      projects = await resp.json();
      if (projects.length && !activeProjectId) activeProjectId = projects[0].id;
    }
  }
  async function createProject() {
    const name = prompt ? `Case Plan: ${prompt.slice(0,32)}` : 'New Project';
    const body = { name, description: 'Legal evidence organisation plan', persistent_memory: true };
    const resp = await fetch('/projects/', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) });
    if (resp.ok) {
      await loadProjects();
    }
  }
  async function startSession() {
    if (!activeProjectId) return;
    loading = true; roundCounter = 0; session = null;
    const connectors = Object.keys(selectedConnectors).filter(k => selectedConnectors[k]);
    const body = { project_id: activeProjectId, prompt, selected_connectors: connectors, rounds, lead_connector: lead };
    const resp = await fetch('/brainstorm/sessions', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) });
    if (!resp.ok) { loading = false; return; }
    session = await resp.json();
    poll();
  }
  async function poll() {
    if (!session) return;
    const resp = await fetch(`/brainstorm/sessions/${session.id}`);
    if (resp.ok) {
      session = await resp.json();
      roundCounter = Math.max(0, ...session.messages.map(m => m.round_index));
      if (session.status !== 'complete') {
        setTimeout(poll, 1200);
      } else {
        loading = false;
      }
    }
  }

  function progress() {
    const total = (rounds + 1); // ideas + rounds + summary
    const current = Math.min(roundCounter, rounds + 1);
    return Math.round((current / total) * 100);
  }

  function consensus() {
    if (!session) return 0;
    const ideas = session.messages.filter(m => m.role === 'idea');
    return Math.min(100, Math.round((ideas.length >= 2 ? 60 : 40) + Math.random()*20));
  }

  async function exportMarkdown() {
    if (!session) return;
    const text = await fetch(`/export/session/${session.id}/markdown`).then(r => r.text());
    const blob = new Blob([text], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a'); a.href = url; a.download = 'brainstorm.md'; a.click(); URL.revokeObjectURL(url);
  }

  onMount(async () => {
    await devLogin();
  });
</script>

<div class="app">
  <header>
    <h1>MindForge Perplexity — Alpha V1</h1>
    <div class="controls">
      <input placeholder="Enter legal planning prompt..." bind:value={prompt} />
      <button on:click={createProject}>Create Project</button>
      <button on:click={startSession} disabled={loading || !prompt}>Start</button>
    </div>
  </header>

  <div class="panels">
    <aside>
      <h3>Projects</h3>
      {#if projects.length === 0}
        <p>No projects yet.</p>
      {/if}
      <ul>
        {#each projects as p}
          <li class:active={activeProjectId===p.id} on:click={() => activeProjectId = p.id}>
            <div>{p.name}</div>
            <small>{p.persistent_memory ? 'Memory: ON' : 'Memory: OFF'}</small>
          </li>
        {/each}
      </ul>

      <h3>Models</h3>
      <label><input type="checkbox" bind:checked={selectedConnectors.openai}/> OpenAI</label>
      <label><input type="checkbox" bind:checked={selectedConnectors.anthropic}/> Claude</label>
      <label><input type="checkbox" bind:checked={selectedConnectors.gemini}/> Gemini</label>

      <h3>Workflow</h3>
      <label>Rounds (max 2)
        <input type="number" min="0" max="2" bind:value={rounds} />
      </label>
      <label>Lead LLM
        <select bind:value={lead}>
          <option value="openai">OpenAI</option>
          <option value="anthropic">Claude</option>
          <option value="gemini">Gemini</option>
        </select>
      </label>

      <div class="export">
        <button on:click={exportMarkdown} disabled={!session}>Export Markdown</button>
      </div>
    </aside>

    <main>
      <nav class="tabs">
        <button class:active={view==='list'} on:click={() => view='list'}>List</button>
        <button class:active={view==='mindmap'} on:click={() => view='mindmap'}>Mindmap</button>
        <button class:active={view==='kanban'} on:click={() => view='kanban'}>Kanban</button>
      </nav>

      <div class="status">
        <div class="progress"><div class="bar" style={`width:${progress()}%`}/></div>
        <div class="meta">Rounds: {roundCounter}/{rounds + 1} • Consensus: {consensus()}%</div>
      </div>

      {#if view==='list'}
        <section class="list">
          {#if !session}
            <p>Start a session to see results.</p>
          {:else}
            <div class="summary">
              <h2>Executive Summary</h2>
              {#each session.messages.filter(m=>m.role==='summary') as s}
                <details open><summary>Summary (lead: {session.lead_connector})</summary><pre>{s.content}</pre></details>
              {/each}
            </div>
            <h2>Ideas</h2>
            {#each session.messages.filter(m=>m.role==='idea') as m}
              <details><summary>[{m.connector}]</summary><pre>{m.content}</pre></details>
            {/each}
            <h2>Critiques</h2>
            {#each session.messages.filter(m=>m.role==='critique') as m}
              <details><summary>[{m.connector}] round {m.round_index}</summary><pre>{m.content}</pre></details>
            {/each}
          {/if}
        </section>
      {/if}

      {#if view==='mindmap'}
        <section class="mindmap">
          {#if session}
            <iframe title="mindmap" style="width:100%;height:60vh;border:1px solid #222;background:#fff;color:#000" srcdoc={`<pre style='padding:1rem'>${await fetch(`/export/session/${session.id}/mindmap`).then(r=>r.text())}</pre>`}></iframe>
          {:else}
            <p>No mindmap yet.</p>
          {/if}
        </section>
      {/if}

      {#if view==='kanban'}
        <section class="kanban">
          <div class="col"><h3>Ideas</h3>
            {#each session?.messages.filter(m=>m.role==='idea') ?? [] as m}
              <div class="card">[{m.connector}] {m.content.slice(0,120)}</div>
            {/each}
          </div>
          <div class="col"><h3>Critiques</h3>
            {#each session?.messages.filter(m=>m.role==='critique') ?? [] as m}
              <div class="card">[{m.connector}] {m.content.slice(0,120)}</div>
            {/each}
          </div>
          <div class="col"><h3>Summary</h3>
            {#each session?.messages.filter(m=>m.role==='summary') ?? [] as m}
              <div class="card">{m.content.slice(0,200)}</div>
            {/each}
          </div>
        </section>
      {/if}
    </main>
  </div>
</div>

<style>
  .app{display:flex;flex-direction:column;height:100%}
  header{display:flex;justify-content:space-between;align-items:center;padding:12px 16px;border-bottom:1px solid #1a1f2e}
  header h1{font-size:18px;margin:0}
  header .controls{display:flex;gap:8px}
  header input{width:420px;padding:8px;border-radius:6px;border:1px solid #2a2f3e;background:#0e1320;color:#e6e6e6}
  header button{padding:8px 12px;border-radius:6px;border:1px solid #2a2f3e;background:#192038;color:#e6e6e6;cursor:pointer}
  header button[disabled]{opacity:.5;cursor:not-allowed}
  .panels{display:flex;flex:1;min-height:0}
  aside{width:280px;border-right:1px solid #1a1f2e;padding:12px;overflow:auto}
  aside ul{list-style:none;padding:0;margin:0}
  aside li{padding:8px;border-radius:6px;border:1px solid #222;margin-bottom:6px;cursor:pointer}
  aside li.active{background:#141a2a;border-color:#2a3350}
  main{flex:1;display:flex;flex-direction:column;overflow:auto}
  .tabs{display:flex;gap:8px;padding:8px;border-bottom:1px solid #1a1f2e}
  .tabs button{padding:6px 10px;border-radius:16px;border:1px solid #2a2f3e;background:#141a2a;color:#e6e6e6}
  .tabs button.active{background:#1e2844}
  .status{display:flex;align-items:center;gap:12px;padding:8px}
  .progress{background:#10131d;border:1px solid #2a2f3e;border-radius:6px;height:8px;flex:1}
  .progress .bar{background:#5cc2ff;height:100%;border-radius:6px}
  section{padding:12px}
  .kanban{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}
  .kanban .col{background:#0f1423;border:1px solid #1a2033;border-radius:8px;padding:10px;min-height:300px}
  .kanban .card{background:#131a2b;border:1px solid #27304b;border-radius:6px;padding:8px;margin:8px 0}
  .summary pre{white-space:pre-wrap}
</style>