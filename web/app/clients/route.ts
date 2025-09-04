import { NextResponse } from 'next/server'

// Redirect old /clients route to the new /schools route
export async function GET() {
  return NextResponse.redirect(new URL('/schools', process.env.NEXT_PUBLIC_SITE_URL || 'http://localhost:3000'))
}

export const dynamic = 'force-dynamic'

