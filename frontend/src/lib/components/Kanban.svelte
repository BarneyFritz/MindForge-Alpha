<script lang="ts">
  export let summaryMarkdown: string = '';

  type Card = { id: number; title: string; desc: string };
  let todos: Card[] = [];

  $: parse();

  function parse() {
    const lines = summaryMarkdown.split('\n');
    const out: Card[] = [];
    let capture = false;
    for (const line of lines) {
      if (line.toLowerCase().includes('next actions')) { capture = true; continue; }
      if (capture) {
        if (/^\s*[-*]|^\s*\d+[.)]/.test(line)) {
          const text = line.replace(/^\s*[-*\d.)]+\s*/, '').trim();
          out.push({ id: out.length + 1, title: text.slice(0, 40), desc: text });
        } else if (line.trim() === '') {
          break;
        }
      }
    }
    todos = out;
  }
</script>

{#if todos.length === 0}
  <div>No actions detected. Ensure the synthesis lists Next Actions.</div>
{:else}
  <div style="display:grid; grid-template-columns: 1fr 1fr 1fr; gap: 12px;">
    <div>
      <h4>To Do</h4>
      {#each todos as t}
        <div style="border:1px solid #ddd; border-radius:6px; padding:8px; margin-bottom:8px;">
          <strong>{t.title}</strong>
          <div style="font-size:12px; opacity:0.8;">{t.desc}</div>
        </div>
      {/each}
    </div>
    <div>
      <h4>In Progress</h4>
      <div style="color:#999">(drag-drop local state can be added later)</div>
    </div>
    <div>
      <h4>Done</h4>
    </div>
  </div>
{/if}