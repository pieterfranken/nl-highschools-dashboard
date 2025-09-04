import { getServerSupabase } from './supabase/server'

export type ClientKpis = {
  clientCount: number
  totalEnrollment: number
  avgEnrollment: number
  withWebsitePct: number
  byProvince: Record<string, { count: number; enrollment: number }>
  byLevel: Record<'VMBO' | 'HAVO' | 'VWO', { count: number; enrollment: number }>
}

export async function getClientKpis(): Promise<ClientKpis> {
  const supabase = getServerSupabase()

  // Get client school ids
  const { data: idsRows, error: idsErr } = await supabase.from('client_schools').select('school_id')
  if (idsErr) throw idsErr
  const ids = (idsRows || []).map((r: any) => r.school_id)
  if (ids.length === 0) {
    return {
      clientCount: 0,
      totalEnrollment: 0,
      avgEnrollment: 0,
      withWebsitePct: 0,
      byProvince: {},
      byLevel: { VMBO: { count: 0, enrollment: 0 }, HAVO: { count: 0, enrollment: 0 }, VWO: { count: 0, enrollment: 0 } },
    }
  }

  // Fetch selected fields for those schools
  const { data, error } = await supabase
    .from('schools')
    .select('id, province, enrollment_total, has_website, vmbo, havo, vwo')
    .in('id', ids)
  if (error) throw error

  const clientCount = data.length
  const totalEnrollment = data.reduce((acc: number, r: any) => acc + (r.enrollment_total ?? 0), 0)
  const avgEnrollment = clientCount ? Math.round(totalEnrollment / clientCount) : 0
  const withWebsitePct = clientCount
    ? Math.round(((data.filter((r: any) => r.has_website).length / clientCount) * 100 + Number.EPSILON) * 10) / 10
    : 0

  const byProvince: Record<string, { count: number; enrollment: number }> = {}
  for (const r of data as any[]) {
    const key = r.province ?? 'Unknown'
    if (!byProvince[key]) byProvince[key] = { count: 0, enrollment: 0 }
    byProvince[key].count += 1
    byProvince[key].enrollment += r.enrollment_total ?? 0
  }

  const byLevel = {
    VMBO: { count: 0, enrollment: 0 },
    HAVO: { count: 0, enrollment: 0 },
    VWO: { count: 0, enrollment: 0 },
  } as Record<'VMBO' | 'HAVO' | 'VWO', { count: number; enrollment: number }>
  for (const r of data as any[]) {
    if (r.vmbo) { byLevel.VMBO.count++; byLevel.VMBO.enrollment += r.enrollment_total ?? 0 }
    if (r.havo) { byLevel.HAVO.count++; byLevel.HAVO.enrollment += r.enrollment_total ?? 0 }
    if (r.vwo)  { byLevel.VWO.count++;  byLevel.VWO.enrollment += r.enrollment_total ?? 0 }
  }

  return { clientCount, totalEnrollment, avgEnrollment, withWebsitePct, byProvince, byLevel }
}

