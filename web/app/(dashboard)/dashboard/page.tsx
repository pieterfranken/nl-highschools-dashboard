import { getServerSupabase } from '@/lib/supabase/server'
import { getClientKpis } from '@/lib/client-kpis'

export const dynamic = 'force-dynamic'

export default async function DashboardPage() {
  const supabase = getServerSupabase()
  const { count } = await supabase.from('schools').select('id', { count: 'exact', head: true })

  const kpis = await getClientKpis()

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-semibold">Overview</h2>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="rounded-md border p-4">
          <div className="text-sm text-slate-600">Total schools</div>
          <div className="text-3xl font-bold">{typeof count === 'number' ? count : '—'}</div>
        </div>
        <div className="rounded-md border p-4">
          <div className="text-sm text-slate-600">Client schools</div>
          <div className="text-3xl font-bold">{kpis.clientCount}</div>
        </div>
        <div className="rounded-md border p-4">
          <div className="text-sm text-slate-600">Client enrollment (total)</div>
          <div className="text-3xl font-bold">{kpis.totalEnrollment.toLocaleString('nl-NL')}</div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="rounded-md border p-4">
          <div className="text-sm text-slate-600">Avg. enrollment per client school</div>
          <div className="text-3xl font-bold">{kpis.avgEnrollment.toLocaleString('nl-NL')}</div>
        </div>
        <div className="rounded-md border p-4">
          <div className="text-sm text-slate-600">Client websites</div>
          <div className="text-3xl font-bold">{kpis.withWebsitePct}%</div>
        </div>
        <div className="rounded-md border p-4">
          <div className="text-sm text-slate-600">VMBO / HAVO / VWO (client share)</div>
          <div className="text-3xl font-bold text-slate-800">
            {kpis.byLevel.VMBO.count} / {kpis.byLevel.HAVO.count} / {kpis.byLevel.VWO.count}
          </div>
        </div>
      </div>

      <div className="rounded-md border p-4">
        <div className="text-sm text-slate-600 mb-2">Clients by province (count • enrollment)</div>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-sm">
          {Object.entries(kpis.byProvince)
            .sort((a, b) => a[0].localeCompare(b[0]))
            .map(([prov, v]) => (
              <div key={prov} className="flex items-center justify-between gap-2">
                <div className="text-slate-700">{prov.replace(/-/g, ' ')}</div>
                <div className="text-slate-900">{v.count} • {v.enrollment.toLocaleString('nl-NL')}</div>
              </div>
            ))}
        </div>
      </div>
    </div>
  )
}

