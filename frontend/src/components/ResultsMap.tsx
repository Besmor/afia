import { useEffect, useMemo } from 'react';
import L from 'leaflet';
import { MapContainer, Marker, TileLayer, useMap, ZoomControl } from 'react-leaflet';
import type { SearchResult } from '../lib/api';
import { formatPriceGnf } from '../lib/format';
import styles from './ResultsMap.module.css';

interface ResultsMapProps {
  results: SearchResult[];
  userLat: number;
  userLon: number;
}

/** Only the top N results get a pin; matches the `limit=10` Results.tsx already asks the API for. */
const MAX_PINS = 10;

const TILE_URL = 'https://tile.openstreetmap.org/{z}/{x}/{y}.png';
const TILE_ATTRIBUTION =
  '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors';

/** White medical-cross glyph inlined as a raw SVG string for the DivIcon HTML (see buildPharmacyIcon). */
const PIN_CROSS_SVG =
  '<svg viewBox="0 0 24 24" width="13" height="13" fill="none" aria-hidden="true">' +
  '<path d="M12 5v14M5 12h14" stroke="#ffffff" stroke-width="3.5" stroke-linecap="round"/></svg>';

/**
 * Solid blue dot, no directional arrow (out of MVP scope per the task
 * brief). `divIcon` renders raw HTML rather than an image, so no default
 * Leaflet marker asset is ever requested (avoids the well-known missing
 * marker-icon.png 404).
 */
const userIcon = L.divIcon({
  className: styles.userMarkerWrap,
  html: `<span class="${styles.userDot}"></span>`,
  iconSize: [0, 0],
  iconAnchor: [0, 0],
});

/**
 * Pill-shaped price pin (`+ 15 000 GNF` on green, downward tail) from
 * `Vue Maps-Résultat des recherches.svg`. Built per-marker since the price
 * text differs; the wrapper's `translate(-50%, -100%)` (see .module.css)
 * anchors the tail's tip, not the pill, to the pharmacy coordinate.
 */
function buildPharmacyIcon(priceGnf: number): L.DivIcon {
  return L.divIcon({
    className: styles.pricePinWrap,
    html:
      `<div class="${styles.pricePin}">${PIN_CROSS_SVG}<span>${formatPriceGnf(priceGnf)}</span></div>` +
      `<div class="${styles.pricePinTail}"></div>`,
    iconSize: [0, 0],
    iconAnchor: [0, 0],
  });
}

/**
 * Fits the map to user + pharmacy coordinates once, on mount. Declarative
 * `bounds`/`boundsOptions` props on `MapContainer` compute against the
 * container's size at construction time, which can still be unlaid-out
 * (its CSS `calc(100vh - …)` height not yet applied) — that produced wildly
 * wrong zoom/pan in manual testing. Doing it imperatively inside a
 * `useEffect`, which only runs after the browser has committed layout,
 * fixes that; `invalidateSize()` is cheap extra insurance for the same
 * class of stale-size issue.
 */
function FitBounds({ points }: { points: L.LatLngExpression[] }) {
  const map = useMap();

  useEffect(() => {
    map.invalidateSize();

    if (points.length > 1) {
      map.fitBounds(points, { padding: [48, 48] });
    } else if (points.length === 1) {
      map.setView(points[0], 14);
    }
    // `points` is memoised by the caller on `results`, so this only re-runs
    // when a new search actually loads, not on every render.
  }, [map, points]);

  return null;
}

/**
 * Map view for the Results screen (Block G). Renders OpenStreetMap tiles
 * (no API key, no Google tiles, unlike the Figma mockup) with a user
 * marker and one green price pin per result.
 */
export function ResultsMap({ results, userLat, userLon }: ResultsMapProps) {
  const pins = results.slice(0, MAX_PINS);
  const pharmacyCount = new Set(results.map((r) => r.pharmacy_id)).size;

  const boundsPoints = useMemo<L.LatLngExpression[]>(() => {
    const topResults = results.slice(0, MAX_PINS);
    return [[userLat, userLon], ...topResults.map((r): [number, number] => [r.latitude, r.longitude])];
  }, [results, userLat, userLon]);

  return (
    <div className={styles.wrap}>
      <div className={styles.overlayTop}>
        <p className={styles.banner}>
          Résultats de la recherche : <strong>{pharmacyCount} pharmacies trouvées</strong>
        </p>
      </div>

      <MapContainer center={[userLat, userLon]} zoom={14} zoomControl={false} className={styles.map}>
        <TileLayer url={TILE_URL} attribution={TILE_ATTRIBUTION} />
        <ZoomControl position="bottomright" />
        <FitBounds points={boundsPoints} />

        <Marker position={[userLat, userLon]} icon={userIcon} interactive={false} keyboard={false} />

        {pins.map((result) => (
          <Marker
            key={`${result.pharmacy_id}-${result.medication_id}`}
            position={[result.latitude, result.longitude]}
            icon={buildPharmacyIcon(result.price_gnf)}
          />
        ))}
      </MapContainer>
    </div>
  );
}
