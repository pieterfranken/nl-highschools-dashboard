'use server'
import { cookies } from 'next/headers'
import { createServerClient } from '@supabase/ssr'
import { revalidatePath } from 'next/cache'

function supaFromCookies() {
  const store = cookies()
  return createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    { cookies: { get: (k: string) => store.get(k)?.value } }
  )
}

// Public server action: no auth required. Uses RLS that allows anonymous writes.
export async function setClient(formData: FormData) {
  const schoolId = String(formData.get('schoolId') ?? '')
  const op = String(formData.get('op') ?? '')
  if (!schoolId || !op) return
  const supabase = supaFromCookies()

  if (op === 'add') {
    const { error } = await supabase.from('client_schools').upsert({ school_id: schoolId })
    if (error) throw error
  } else if (op === 'remove') {
    const { error } = await supabase.from('client_schools').delete().eq('school_id', schoolId)
    if (error) throw error
  }
  // Refresh server components that depend on client list
  revalidatePath('/schools')
  revalidatePath('/map')
}

