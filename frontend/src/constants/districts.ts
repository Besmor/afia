/**
 * Conakry district bounding boxes, copied verbatim from
 * `backend/app/data/conakry_district_bounds.json` (source: approximate
 * OpenStreetMap-derived commune bounding boxes, 2026-08). Used as the
 * fallback location picker when browser geolocation is denied or
 * unavailable — see `src/lib/location.ts` and `src/components/DistrictPicker.tsx`.
 *
 * Only the 5 real Conakry communes are exposed here; the backend's
 * "Unknown" catch-all bucket is not a user-facing option.
 */

export interface DistrictBounds {
  lat_min: number;
  lat_max: number;
  lon_min: number;
  lon_max: number;
}

export interface District {
  name: string;
  bounds: DistrictBounds;
  /** Centroid of the bounding box; used as the search origin for this district. */
  centroid: { lat: number; lon: number };
}

function centroidOf(bounds: DistrictBounds): { lat: number; lon: number } {
  return {
    lat: (bounds.lat_min + bounds.lat_max) / 2,
    lon: (bounds.lon_min + bounds.lon_max) / 2,
  };
}

const DISTRICT_BOUNDS: Record<string, DistrictBounds> = {
  Kaloum: { lat_min: 9.5, lat_max: 9.53, lon_min: -13.72, lon_max: -13.69 },
  Dixinn: { lat_min: 9.53, lat_max: 9.56, lon_min: -13.7, lon_max: -13.66 },
  Ratoma: { lat_min: 9.56, lat_max: 9.66, lon_min: -13.68, lon_max: -13.55 },
  Matam: { lat_min: 9.52, lat_max: 9.56, lon_min: -13.68, lon_max: -13.64 },
  Matoto: { lat_min: 9.54, lat_max: 9.62, lon_min: -13.64, lon_max: -13.51 },
};

export const DISTRICTS: District[] = Object.entries(DISTRICT_BOUNDS).map(([name, bounds]) => ({
  name,
  bounds,
  centroid: centroidOf(bounds),
}));

/**
 * Default search origin used when no location is available at all (no
 * geolocation, no district picked yet). Matches the backend's own default
 * (`DEFAULT_USER_LAT`/`DEFAULT_USER_LON` in `app/api/search.py`), the
 * Kaloum commune centroid.
 */
export const DEFAULT_CENTROID = DISTRICTS.find((d) => d.name === 'Kaloum')!.centroid;
