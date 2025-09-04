import { type NextRequest, NextResponse } from 'next/server'
import { createRouteHandlerClient } from '@supabase/ssr'

export async function GET(req: NextRequest) {
  const requestUrl = new URL(req.url)
  const code = requestUrl.searchParams.get('code')
  const next = requestUrl.searchParams.get('next') ?? '/dashboard'

  if (code) {
    const response = NextResponse.redirect(new URL(next, requestUrl.origin))
    const supabase = createRouteHandlerClient({
      cookies: {
        get(name: string) {
          return req.cookies.get(name)?.value
        },
        set(name: string, value: string, options: any) {
          response.cookies.set({ name, value, ...options })
        },
        remove(name: string, options: any) {
          response.cookies.set({ name, value: '', ...options, maxAge: 0 })
        },
      },
    })
    await supabase.auth.exchangeCodeForSession(code)
    return response
  }

  return NextResponse.redirect(new URL('/auth/sign-in', requestUrl.origin))
}

