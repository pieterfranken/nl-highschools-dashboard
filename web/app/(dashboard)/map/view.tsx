"use client";
import { useMemo, useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { MapContainer as RLMapContainer, TileLayer as RLTileLayer, CircleMarker as RLCircleMarker } from 'react-leaflet'
import 'leaflet/dist/leaflet.css'
import type { School } from '@/lib/types'
import { setClient } from '../schools/actions'

// Avoid type noise from react-leaflet generics in our setup
const MapContainer = RLMapContainer as any
const TileLayer = RLTileLayer as any
const CircleMarker = RLCircleMarker as any

export default function MapClient({ schools, clientIds, provinces = [], sizes = [], denominations = [], initialFilters = {} as any }: { schools: School[]; clientIds: string[]; provinces?: string[]; sizes?: string[]; denominations?: string[]; initialFilters?: any }) {
  const router = useRouter()
  const [onlyClients, setOnlyClients] = useState(false)
  const [selected, setSelected] = useState<School | null>(null)
  const defaults = useMemo(() => ({
    province: initialFilters.province || '',
    size: initialFilters.size || '',
    denomination: initialFilters.denomination || '',
    levels: Array.isArray(initialFilters.levels) ? initialFilters.levels.filter((l: string)=>['VMBO','HAVO','VWO'].includes(l)) : [],
  }), [JSON.stringify(initialFilters)])
  const [filters, setFilters] = useState(defaults)
  useEffect(() => setFilters(defaults), [defaults])
  const isClient = useMemo(() => new Set(clientIds), [clientIds])
  const filtered = useMemo(() => (onlyClients ? schools.filter(s => isClient.has(s.id)) : schools), [onlyClients, schools, isClient])
  const center: [number, number] = [52.1326, 5.2913]
  const selectedIsClient = selected ? isClient.has(selected.id) : false

  return (
    <div className="w-full space-y-3">
      <form method="GET" className="flex flex-wrap items-end gap-3">
        <div>
          <label className="block text-xs text-slate-600 mb-1">Province</label>
          <select name="province" value={filters.province} onChange={(e)=>setFilters({ ...filters, province: e.target.value })} className="border rounded px-2 py-1 text-sm">
            <option value="">All</option>
            {provinces.map((p) => (
              <option key={p} value={p}>{p.replace(/-/g, ' ')}</option>
            ))}
          </select>
        </div>
        <div>
          <label className="block text-xs text-slate-600 mb-1">Size</label>
          <select name="size" value={filters.size} onChange={(e)=>setFilters({ ...filters, size: e.target.value })} className="border rounded px-2 py-1 text-sm">
            <option value="">All</option>
            {sizes.map((s) => (
              <option key={s} value={s}>{s}</option>
            ))}
          </select>
        </div>
        <div>
          <label className="block text-xs text-slate-600 mb-1">Denomination</label>
          <select name="denomination" value={filters.denomination} onChange={(e)=>setFilters({ ...filters, denomination: e.target.value })} className="border rounded px-2 py-1 text-sm">
            <option value="">All</option>
            {denominations.map((d) => (
              <option key={d} value={d}>{d}</option>
            ))}
          </select>
        </div>
        <div>
          <label className="block text-xs text-slate-600 mb-1">Levels</label>
          <div className="flex gap-2 text-sm">
            {['VMBO','HAVO','VWO'].map((lvl) => (
              <label key={lvl} className="flex items-center gap-1">
                <input type="checkbox" name="levels" value={lvl} checked={filters.levels.includes(lvl)} onChange={(e)=> setFilters({ ...filters, levels: e.target.checked ? [...filters.levels, lvl] : filters.levels.filter((x: string)=>x!==lvl) }) } /> {lvl}
              </label>
            ))}
          </div>
        </div>
        <div className="ml-auto flex items-center gap-3">
          <label className="flex items-center gap-2 text-sm text-slate-700">
            <input type="checkbox" name="onlyClients" value="1" checked={onlyClients} onChange={(e) => setOnlyClients(e.target.checked)} /> Only clients
          </label>
          <button
            type="button"
            onClick={(e)=>{ e.preventDefault(); setOnlyClients(false); setFilters({ province:'', size:'', denomination:'', levels: [] }); router.push('/map'); }}
            className="text-sm border rounded px-3 py-1 hover:bg-slate-50"
          >
            Clear all
          </button>
          <button type="submit" className="text-sm border rounded px-3 py-1 hover:bg-slate-50">Apply</button>
        </div>
      </form>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
        <div className="md:col-span-2">
          <div className="w-full h-[600px]">
            <MapContainer center={center} zoom={7} className="h-full w-full">
              <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" attribution="&copy; OpenStreetMap contributors" />
              {(() => {
                const nonClients = filtered.filter((s) => !isClient.has(s.id))
                const clients = filtered.filter((s) => isClient.has(s.id))
                const render = (s: School, client: boolean) => {
                  if (s.latitude == null || s.longitude == null) return null
                  const color = client ? '#2ca02c' : '#1f77b4'
                  return (
                    <CircleMarker
                      key={s.id}
                      center={[s.latitude, s.longitude]}
                      radius={client ? 6 : 5}
                      pathOptions={{ color, fillColor: color, fillOpacity: 0.8 }}
                      eventHandlers={{ click: () => setSelected(s) }}
                    />
                  )
                }
                return (
                  <>
                    {nonClients.map((s) => render(s, false))}
                    {clients.map((s) => render(s, true))}
                  </>
                )
              })()}
            </MapContainer>
          </div>
        </div>
        <div className="md:col-span-1">
          {selected ? (
            <div className="border rounded p-4 bg-white/70 backdrop-blur-sm h-[600px] overflow-auto">
              <div className="flex items-start justify-between gap-4">
                <div>
                  <div className="text-lg font-semibold">{selected.school_name}</div>
                  <div className="text-sm text-slate-600">{[selected.city, selected.province].filter(Boolean).join(', ')}</div>
                </div>
                <div className={`text-xs px-2 py-1 rounded ${selectedIsClient ? 'bg-green-100 text-green-700' : 'bg-slate-100 text-slate-700'}`}>
                  {selectedIsClient ? 'Client' : 'Not client'}
                </div>
              </div>

              <div className="mt-3 grid grid-cols-1 md:grid-cols-2 gap-3 text-sm">
                {selected.levels_offered && (
                  <div><span className="text-slate-500">Levels:</span> {selected.levels_offered}</div>
                )}
                {selected.education_structure && (
                  <div><span className="text-slate-500">Structure:</span> {selected.education_structure}</div>
                )}
                {selected.enrollment_total != null && (
                  <div><span className="text-slate-500">Enrollment:</span> {selected.enrollment_total}</div>
                )}
                {selected.school_size_category && (
                  <div><span className="text-slate-500">Size:</span> {selected.school_size_category}</div>
                )}
                {selected.denomination && (
                  <div><span className="text-slate-500">Denomination:</span> {selected.denomination}</div>
                )}
                {selected.phone_formatted && (
                  <div><span className="text-slate-500">Phone:</span> {selected.phone_formatted}</div>
                )}
                {selected.website && (
                  <div>
                    <a href={(selected.website||'').startsWith('http') ? (selected.website as string) : `https://${(selected.website||'').replace(/^\/+/, '')}`} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">Visit website</a>
                  </div>
                )}
              </div>

              <div className="mt-4 flex items-center gap-3">
                <form action={setClient}>
                  <input type="hidden" name="schoolId" value={selected.id} />
                  <input type="hidden" name="op" value={selectedIsClient ? 'remove' : 'add'} />
                  <button type="submit" className="text-sm border rounded px-3 py-1 hover:bg-slate-50">
                    {selectedIsClient ? 'Remove from clients' : 'Add to clients'}
                  </button>
                </form>
                <button onClick={() => setSelected(null)} className="text-sm text-slate-600 hover:underline">Close</button>
              </div>
            </div>
          ) : (
            <div className="h-[600px] border rounded p-4 text-sm text-slate-600 flex items-center justify-center">
              Click a school on the map to see details.
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

