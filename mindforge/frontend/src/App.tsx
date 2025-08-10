function App() {
  return (
    <div className="min-h-screen bg-gray-50 text-gray-900">
      <header className="border-b bg-white">
        <div className="mx-auto max-w-6xl px-4 py-4 flex items-center justify-between">
          <h1 className="text-xl font-semibold">MindForge</h1>
          <nav className="flex gap-4 text-sm">
            <a href="#" className="hover:underline">Mind Map</a>
            <a href="#" className="hover:underline">Kanban</a>
            <a href="#" className="hover:underline">Metrics</a>
          </nav>
        </div>
      </header>
      <main className="mx-auto max-w-6xl px-4 py-8">
        <div className="grid md:grid-cols-3 gap-6">
          <section className="md:col-span-2 bg-white rounded-lg shadow p-4 h-[480px] flex items-center justify-center">
            <span className="text-gray-400">MindMap visualization placeholder</span>
          </section>
          <aside className="bg-white rounded-lg shadow p-4 h-[480px]">
            <h2 className="font-medium mb-2">Anti-Chaos Settings</h2>
            <div className="space-y-3 text-sm">
              <label className="flex items-center justify-between"><span>Critique Rounds</span><input type="number" className="border rounded px-2 py-1 w-20" defaultValue={2}/></label>
              <label className="flex items-center justify-between"><span>Min Response Length</span><input type="number" className="border rounded px-2 py-1 w-20" defaultValue={100}/></label>
              <label className="flex items-center justify-between"><span>Timeout (s)</span><input type="number" className="border rounded px-2 py-1 w-20" defaultValue={60}/></label>
              <label className="flex items-center justify-between"><span>Quality Threshold</span><input type="number" step="0.1" className="border rounded px-2 py-1 w-20" defaultValue={0.5}/></label>
            </div>
          </aside>
        </div>
        <div className="mt-6 bg-white rounded-lg shadow p-4 h-[320px] flex items-center justify-center">
          <span className="text-gray-400">Kanban board placeholder</span>
        </div>
      </main>
    </div>
  )
}

export default App
