// middleware.ts
import { NextRequest, NextResponse } from 'next/server';

export function middleware(req: NextRequest) {
  // ... 미들웨어 로직 ...
  return NextResponse.next();
}

export const config = {
  matcher: [
    /*
     * 모든 경로와 일치하지만, 아래 경로는 제외:
     * - .swa (Azure Static Web Apps 내부 경로)
     * - _next/static (정적 파일)
     * - _next/image (이미지 최적화 파일)
     * - favicon.ico (파비콘 파일)
     */
    '/((?!.swa|_next/static|_next/image|favicon.ico).*)',
  ],
};
