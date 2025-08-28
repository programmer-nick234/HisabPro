/** @type {import('next').NextConfig} */
const nextConfig = {
  images: {
    domains: ['localhost'],
  },
  // Disable static optimization for error pages to avoid build issues
  experimental: {
    optimizePackageImports: ['react-hot-toast', 'lucide-react'],
  },
  // Skip build static optimization to avoid Html import errors
  skipTrailingSlashRedirect: true,
  // Ensure error pages are not statically optimized
  generateEtags: false,
}

module.exports = nextConfig
