import NextDynamic from 'next/dynamic'
import { listMapSchools, listProvinces, getClientSet, listDenominations, listSizes } from '@/lib/queries'

const MapClient = NextDynamic(() => import('./view'), { ssr: false })

export const dynamic = 'force-dynamic'

export default async function MapPage({ searchParams }: { searchParams?: Record<string, string | string[]> }) {
  const rawProvince = (searchParams?.province || '') as string
  const size = (searchParams?.size || '') as string
  const denom = (searchParams?.denomination || '') as string
  const levels = Array.isArray(searchParams?.levels)
    ? (searchParams?.levels as string[])
    : (searchParams?.levels ? String(searchParams?.levels).split(',') : [])
  const search = (searchParams?.q || '') as string

  // Fetch lookup lists first so we can canonicalize province names from URL
  const [provinces, sizes, denominations] = await Promise.all([
    listProvinces(),
    listSizes(),
    listDenominations(),
  ])

  // Canonicalize province from URL to match DB values (handles "zuid holland" -> "Zuid-Holland")
  const norm = (s: string) => s.toLowerCase().replace(/\s|-/g, '')
  const province = provinces.find((p) => norm(p) === norm(rawProvince)) || rawProvince

  const [schools, clients] = await Promise.all([
    listMapSchools({ province: province || null, size: size || null, denomination: denom || null, levels, search }, 5000),
    getClientSet(),
  ])

  const key = `p=${province}|s=${size}|d=${denom}|lv=${[...levels].sort().join(',')}|q=${search}`

  return (
    <div className="space-y-4">
      <h2 className="text-2xl font-semibold">Map</h2>
      <p className="text-sm text-slate-600">Filter and explore schools. Client schools are highlighted.</p>
      <MapClient
        key={key}
        schools={schools}
        clientIds={[...clients]}
        provinces={provinces}
        sizes={sizes}
        denominations={denominations}
        initialFilters={{ province, size, denomination: denom, levels, search }}
      />
    </div>
  )
}

