import { getServerSupabase } from './supabase/server'
import type { School } from './types'

export type Filters = {
  province?: string | null
  levels?: string[] // VMBO, HAVO, VWO only
  size?: string | null
  denomination?: string | null
  search?: string | null
  clientsOnly?: boolean | null
}

export async function getKpis(filters: Filters) {
  const supabase = getServerSupabase()
  let query = supabase.from('schools').select('*')

  if (filters.province) query = query.eq('province', filters.province)
  if (filters.size) query = query.eq('school_size_category', filters.size)
  if (filters.denomination) query = query.eq('denomination', filters.denomination)
  if (filters.search) {
    const s = filters.search
    query = query.or(`school_name.ilike.%${s}%,city.ilike.%${s}%`)
  }
  if (filters.levels && filters.levels.length) {
    // Include schools that offer at least one selected level
    const ors = filters.levels.map((lvl) => `${lvl.toLowerCase()}.eq.true`)
    query = query.or(ors.join(','))
  }

  const { data, error } = await query
  if (error) throw error

  const totalSchools = data.length
  const totalStudents = data.reduce((acc, r) => acc + (r.enrollment_total ?? 0), 0)
  const avgSize = totalSchools ? Math.round(totalStudents / totalSchools) : 0
  const websitePct = totalSchools
    ? Math.round(((data.filter((r) => r.has_website).length / totalSchools) * 100 + Number.EPSILON) * 10) / 10
    : 0

  return { totalSchools, totalStudents, avgSize, websitePct }
}

export async function listProvinces(): Promise<string[]> {
  const supabase = getServerSupabase()
  const pageSize = 1000
  const out = new Set<string>()
  for (let offset = 0; offset < 20000; offset += pageSize) {
    const { data, error } = await supabase
      .from('schools')
      .select('province')
      .not('province', 'is', null)
      .order('province', { ascending: true })
      .range(offset, offset + pageSize - 1)
    if (error) throw error
    if (!data || data.length === 0) break
    for (const r of data as any[]) if (r.province) out.add(r.province)
    if (data.length < pageSize) break
  }
  return Array.from(out).sort()
}

export async function listSizes(): Promise<string[]> {
  const supabase = getServerSupabase()
  const pageSize = 1000
  const out = new Set<string>()
  for (let offset = 0; offset < 20000; offset += pageSize) {
    const { data, error } = await supabase
      .from('schools')
      .select('school_size_category')
      .not('school_size_category', 'is', null)
      .order('school_size_category', { ascending: true })
      .range(offset, offset + pageSize - 1)
    if (error) throw error
    if (!data || data.length === 0) break
    for (const r of data as any[]) if (r.school_size_category) out.add(r.school_size_category)
    if (data.length < pageSize) break
  }
  return Array.from(out).sort()
}

export async function listDenominations(): Promise<string[]> {
  const supabase = getServerSupabase()
  const pageSize = 1000
  const out = new Set<string>()
  for (let offset = 0; offset < 20000; offset += pageSize) {
    const { data, error } = await supabase
      .from('schools')
      .select('denomination')
      .not('denomination', 'is', null)
      .order('denomination', { ascending: true })
      .range(offset, offset + pageSize - 1)
    if (error) throw error
    if (!data || data.length === 0) break
    for (const r of data as any[]) if (r.denomination) out.add(r.denomination)
    if (data.length < pageSize) break
  }
  return Array.from(out).sort()
}

export async function findSchools(filters: Filters, limit = 200): Promise<School[]> {
  const supabase = getServerSupabase()
  let query = supabase.from('schools').select('*').limit(limit)

  if (filters.province) query = query.eq('province', filters.province)
  if (filters.size) query = query.eq('school_size_category', filters.size)
  if (filters.denomination) query = query.eq('denomination', filters.denomination)
  if (filters.search) {
    const s = filters.search
    query = query.or(`school_name.ilike.%${s}%,city.ilike.%${s}%`)
  }
  if (filters.levels && filters.levels.length) {
    const ors = filters.levels.map((lvl) => `${lvl.toLowerCase()}.eq.true`)
    query = query.or(ors.join(','))
  }

  const { data, error } = await query
  if (error) throw error
  return (data || []) as School[]
}

export async function listMapSchools(filters: Filters, limit?: number): Promise<School[]> {
  const supabase = getServerSupabase()

  // PostgREST caps responses at ~1000 rows per request. Page through results to fetch all.
  const pageSize = 1000
  const maxRows = typeof limit === 'number' && Number.isFinite(limit) ? limit : 10000

  const makeBase = () => {
    let q = supabase
      .from('schools')
      .select('*')
      .not('latitude', 'is', null)
      .not('longitude', 'is', null)
      .order('id', { ascending: true })

    if (filters.province) q = q.eq('province', filters.province)
    if (filters.size) q = q.eq('school_size_category', filters.size)
    if (filters.denomination) q = q.eq('denomination', filters.denomination)
    if (filters.search) {
      const s = filters.search
      q = q.or(`school_name.ilike.%${s}%,city.ilike.%${s}%`)
    }
    if (filters.levels && filters.levels.length) {
      const ors = filters.levels.map((lvl) => `${lvl.toLowerCase()}.eq.true`)
      q = q.or(ors.join(','))
    }
    return q
  }

  const out: School[] = []
  for (let offset = 0; out.length < maxRows; offset += pageSize) {
    const end = offset + Math.min(pageSize, maxRows - out.length) - 1
    const { data, error } = await makeBase().range(offset, end)
    if (error) throw error
    if (!data || data.length === 0) break
    out.push(...(data as School[]))
    if (data.length < pageSize) break // last page
  }
  return out
}

export async function getClientSet(): Promise<Set<string>> {
  const supabase = getServerSupabase()
  const { data, error } = await supabase.from('client_schools').select('school_id')
  if (error) throw error
  return new Set((data || []).map((r) => r.school_id as string))
}

