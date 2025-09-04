import { findSchools, getClientSet } from '@/lib/queries'
import { setClient } from './actions'
import { getServerSupabase } from '@/lib/supabase/server'

export const dynamic = 'force-dynamic'

export default async function SchoolsPage({
  searchParams,
}: {
  searchParams?: { q?: string; onlyClients?: string }
}) {
  const q = (searchParams?.q || '').toString().trim()
  const onlyClients = (searchParams?.onlyClients || '') === '1'

  const clients = await getClientSet()

  let schools = [] as Awaited<ReturnType<typeof findSchools>>
  if (q) {
    const results = await findSchools({ search: q }, 50)
    schools = onlyClients ? results.filter((s) => clients.has(s.id)) : results
  } else if (onlyClients) {
    // Show first 50 client schools when onlyClients is on without a search term
    const supabase = getServerSupabase()
    const { data } = await supabase.from('schools').select('*').in('id', [...clients]).limit(50)
    schools = (data as any) || []
  } else {
    // No query and not onlyClients: keep it clean, show nothing
    schools = []
  }

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-semibold">Schools</h2>

      <form method="GET" className="flex items-end gap-3">
        <div className="flex-1">
          <label htmlFor="q" className="block text-xs text-slate-600 mb-1">Search by name or city</label>
          <input id="q" name="q" defaultValue={q} placeholder="e.g., Amsterdam or Gymnasium" className="w-full border rounded px-3 py-2" />
        </div>
        <label className="flex items-center gap-2 text-sm text-slate-700">
          <input type="checkbox" name="onlyClients" value="1" defaultChecked={onlyClients} /> Only clients
        </label>
        <button type="submit" className="border rounded px-3 py-2 text-sm">Search</button>
      </form>

      {(!q && !onlyClients) ? (
        <div className="text-sm text-slate-600">Use the search to find schools, or toggle "Only clients" to view your client list.</div>
      ) : (
        <div className="space-y-2">
          {schools.length === 0 ? (
            <div className="text-sm text-slate-600">No matching schools.</div>
          ) : (
            schools.map((s) => {
              const isClient = clients.has(s.id)
              return (
                <form key={s.id} action={setClient} className="border rounded p-3">
                  <input type="hidden" name="schoolId" value={s.id} />
                  <input type="hidden" name="op" value={isClient ? 'remove' : 'add'} />
                  <div className="flex items-center gap-4">
                    <div className="flex-1">
                      <div className="font-medium">{s.school_name}</div>
                      <div className="text-xs text-slate-600">{s.city ?? ''}</div>
                    </div>
                    <div className="text-xs">{isClient ? 'Client' : 'Not client'}</div>
                    <button className="text-sm text-blue-600" type="submit">{isClient ? 'Remove' : 'Add'}</button>
                  </div>
                </form>
              )
            })
          )}
        </div>
      )}
    </div>
  )
}

