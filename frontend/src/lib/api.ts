/**
 * Barebones API client for the Afia backend (`backend/app/api/search.py`).
 *
 * Requests go to the relative `/search` path, which the Vite dev server
 * proxies to `http://localhost:8000` (see `vite.config.ts`) so the browser
 * never makes a cross-origin request and the backend needs no CORS
 * middleware. In production this assumes the PWA is served from behind the
 * same origin as the API, or the proxy target is swapped for a real one;
 * that deployment concern is out of scope for the local demo (see CLAUDE.md).
 */

export interface SearchResult {
  pharmacy_id: string;
  pharmacy_name: string;
  district: string;
  latitude: number;
  longitude: number;
  digital_maturity: string;
  medication_id: number;
  medication_inn: string;
  medication_form: string;
  medication_strength: string;
  quantity: number;
  price_gnf: number;
  last_verified_at: string;
}

export async function fetchSearch(
  query: string,
  lat: number,
  lon: number,
  limit = 10,
): Promise<SearchResult[]> {
  const params = new URLSearchParams({
    q: query,
    user_lat: String(lat),
    user_lon: String(lon),
    limit: String(limit),
  });

  const response = await fetch(`/search?${params.toString()}`);

  if (!response.ok) {
    throw new Error(`Search request failed with status ${response.status}`);
  }

  return response.json() as Promise<SearchResult[]>;
}

/**
 * Standalone pharmacy record (`GET /pharmacies/{id}`, `backend/app/api/pharmacies.py`).
 * No stock/medication data, unlike `SearchResult` — used by the Pharmacy
 * Detail screen, which is reached both from a search result and (in
 * principle) directly, so it cannot rely on the search response.
 */
export interface PharmacyDetail {
  id: string;
  name: string;
  district: string;
  latitude: number;
  longitude: number;
  digital_maturity: string;
  phone: string | null;
  opens_at: string;
  closes_at: string;
  open_on_sunday: boolean;
}

export async function fetchPharmacy(pharmacyId: string): Promise<PharmacyDetail> {
  const response = await fetch(`/pharmacies/${encodeURIComponent(pharmacyId)}`);

  if (response.status === 404) {
    throw new Error(`Pharmacy ${pharmacyId} not found`);
  }

  if (!response.ok) {
    throw new Error(`Pharmacy request failed with status ${response.status}`);
  }

  return response.json() as Promise<PharmacyDetail>;
}
