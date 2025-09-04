import { NextResponse } from 'next/server'
import { createRouteHandlerClient } from '@supabase/ssr'

export async function POST(req: Request) {
  const { email } = await req.json()
  const response = NextResponse.json({ ok: true })
  const supabase = createRouteHandlerClient({
    cookies: {
      get(name: string) { return undefined },
      set() {},
      remove() {},
    },
  })
  const { error } = await supabase.auth.signInWithOtp({ email, options: { emailRedirectTo: '/auth/callback' } })
  if (error) return NextResponse.json({ error: error.message }, { status: 400 })
  return response
}

