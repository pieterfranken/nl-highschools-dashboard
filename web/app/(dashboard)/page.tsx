import { getServerSupabase } from '@/lib/supabase/server'

export default async function DashboardPage() {
  const supabase = getServerSupabase()
  const { count } = await supabase.from('schools').select('id', { count: 'exact', head: true })
  const total = typeof count === 'number' ? count : undefined

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-semibold">Overview</h2>
      <div className="grid grid-cols-2 gap-4">
        <div className="rounded-md border p-4">
          <div className="text-sm text-slate-600">Total Schools</div>
          <div className="text-3xl font-bold">{typeof total === 'number' ? total : '—'}</div>
        </div>
      </div>
    </div>
  )
}

