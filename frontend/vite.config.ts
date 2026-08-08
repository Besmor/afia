import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    // Proxy API calls to the local FastAPI backend (see RUNBOOK.md for how
    // to start it) so the browser never makes a cross-origin request and
    // the backend needs no CORS middleware. See src/lib/api.ts.
    proxy: {
      '/search': 'http://localhost:8000',
    },
  },
})
