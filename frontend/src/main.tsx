import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
// Leaflet's own stylesheet, imported once here so every Leaflet instance
// (currently just ResultsMap) gets correct tile/marker layout without a
// per-page import (see frontend/src/components/ResultsMap.tsx).
import 'leaflet/dist/leaflet.css'
import './styles/base.css'
import App from './App.tsx'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <BrowserRouter>
      <App />
    </BrowserRouter>
  </StrictMode>,
)
