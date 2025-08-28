import type { NextConfig } from 'next'

const nextConfig: NextConfig = {
  // Standalone 빌드 활성화 (중요!)
  output: 'standalone',
  
  // src 디렉토리 사용 명시
  // Next.js는 자동으로 src/app을 감지하지만 명시하면 더 안전
  experimental: {
    // App Router 최적화
    typedRoutes: true,
    serverActions: {
      bodySizeLimit: '2mb',
    },
  },
  
  // 이미지 최적화 (Azure에서는 unoptimized 권장)
  images: {
    unoptimized: true,
  },
  
  // 압축 활성화
  compress: true,
  
  // 보안 헤더
  poweredByHeader: false,
  
  // 정적 파일 경로
  assetPrefix: process.env.ASSET_PREFIX || '',
  
  // 환경 변수
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || '',
  },
  
  // 웹팩 설정 (필요시)
  webpack: (config, { isServer }) => {
    // Azure 배포 시 필요한 설정
    if (!isServer) {
      config.resolve.fallback = {
        ...config.resolve.fallback,
        fs: false,
        net: false,
        tls: false,
      }
    }
    return config
  },
}

export default nextConfig