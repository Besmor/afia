import { useEffect, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import L from 'leaflet';
import { MapContainer, Marker, TileLayer, useMap, useMapEvents, ZoomControl } from 'react-leaflet';
import type { SearchResult } from '../lib/api';
import { formatDistance, haversineDistanceMeters } from '../lib/geo';
import { formatPriceGnf } from '../lib/format';
import { computeStatus } from '../lib/openingStatus';
import {
  IconBookmark,
  IconClose,
  IconDirections,
  IconPharmacyCross,
  IconPin,
  IconStock,
} from './icons';
import { PrimaryButton } from './PrimaryButton';
import styles from './ResultsMap.module.css';

/** `${pharmacy_id}-${medication_id}`, same composite key the results list uses (Results.tsx). */
function resultKey(result: SearchResult): string {
  return `${result.pharmacy_id}-${result.medication_id}`;
}

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
function FitBounds({ points }: { points: L.LatLngTuple[] }) {
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

/** Closes the selected-pin card when the map background (not a marker) is clicked. */
function MapClickHandler({ onBackgroundClick }: { onBackgroundClick: () => void }) {
  useMapEvents({ click: onBackgroundClick });
  return null;
}

interface SelectedPharmacyCardProps {
  result: SearchResult;
  userLat: number;
  userLon: number;
  onClose: () => void;
}

/**
 * Popover card for the selected pin, from `Vue Maps-Résultat des
 * recherches-Pharmacie sélectionné.svg`. Reuses the same status/distance/
 * price helpers as PharmacyCard (Results list view).
 */
function SelectedPharmacyCard({ result, userLat, userLon, onClose }: SelectedPharmacyCardProps) {
  const navigate = useNavigate();

  const distanceMeters = haversineDistanceMeters(userLat, userLon, result.latitude, result.longitude);
  const status = computeStatus(result.opens_at, result.closes_at, result.open_on_sunday);

  // Walking engine, matching the app's walking-distance ranking ethos
  // (CLAUDE.md, Friesen et al. 2025) rather than OSM's driving default.
  const directionsHref =
    `https://www.openstreetmap.org/directions?engine=fossgis_osrm_foot&route=` +
    `${userLat}%2C${userLon}%3B${result.latitude}%2C${result.longitude}`;

  function handleViewPharmacy() {
    const params = new URLSearchParams({ medication_id: String(result.medication_id) });
    // Same pattern as PharmacyCard.tsx: medication_id stays in the query
    // string for a shareable/directly-openable URL, full result also
    // travels as router state so Detail needs no second fetch for it.
    navigate(`/pharmacy/${result.pharmacy_id}?${params.toString()}`, {
      state: { medicationResult: result },
    });
  }

  return (
    <div className={styles.card}>
      <button type="button" className={styles.cardClose} onClick={onClose} aria-label="Fermer">
        <IconClose className={styles.cardCloseIcon} />
      </button>

      <div className={styles.cardHeader}>
        <IconPharmacyCross className={styles.cardCross} />
        <div className={styles.cardTitleBlock}>
          <h3 className={styles.cardName}>{result.pharmacy_name}</h3>
          <div className={styles.cardMeta}>
            <IconPin className={styles.cardPinIcon} />
            <span>{formatDistance(distanceMeters)} de vous</span>
            <span className={styles.cardDot} aria-hidden="true" />
            <span className={status.label === 'OUVERTE' ? styles.statusOpen : styles.statusClosed}>
              {status.label}
            </span>
            {status.isOnCall && (
              <>
                <span className={styles.cardDot} aria-hidden="true" />
                <span className={styles.onCallBadge}>De garde</span>
              </>
            )}
          </div>
        </div>
      </div>

      <div className={styles.cardStockRow}>
        <span className={styles.stockPill}>
          <IconStock className={styles.stockIcon} />
          En stock
        </span>
        <span className={styles.cardPrice}>{formatPriceGnf(result.price_gnf)}</span>
      </div>

      {/*
       * Phone intentionally omitted here: SearchResult (backend/app/api/
       * search.py) carries no phone field, unlike PharmacyDetail's
       * fetchPharmacy response. Per the task brief, hide the line rather
       * than firing a second request from this popover just for it.
       */}

      <div className={styles.cardActionsRow}>
        <a
          href={directionsHref}
          target="_blank"
          rel="noreferrer"
          className={styles.iconCircleButton}
          aria-label="Itinéraire"
        >
          <IconDirections className={styles.iconCircleGlyph} />
        </a>
        {/* Bookmarking is visual only for the MVP (out of critical-path scope, CLAUDE.md). */}
        <button
          type="button"
          className={styles.iconCircleButton}
          aria-disabled="true"
          aria-label="Enregistrer (bientôt disponible)"
          onClick={(event) => event.preventDefault()}
        >
          <IconBookmark className={styles.iconCircleGlyph} />
        </button>
      </div>

      <PrimaryButton onClick={handleViewPharmacy}>voir la pharmacie</PrimaryButton>
    </div>
  );
}

/**
 * Map view for the Results screen (Block G). Renders OpenStreetMap tiles
 * (no API key, no Google tiles, unlike the Figma mockup) with a user
 * marker and one green price pin per result; clicking a pin opens
 * `SelectedPharmacyCard` above the map.
 */
export function ResultsMap({ results, userLat, userLon }: ResultsMapProps) {
  const [selectedKey, setSelectedKey] = useState<string | null>(null);

  const pins = results.slice(0, MAX_PINS);
  const pharmacyCount = new Set(results.map((r) => r.pharmacy_id)).size;
  const selectedResult = pins.find((r) => resultKey(r) === selectedKey) ?? null;

  const boundsPoints = useMemo<L.LatLngTuple[]>(() => {
    const topResults = results.slice(0, MAX_PINS);
    return [[userLat, userLon], ...topResults.map((r): [number, number] => [r.latitude, r.longitude])];
  }, [results, userLat, userLon]);

  return (
    <div className={styles.wrap}>
      <div className={styles.overlayTop}>
        <p className={styles.banner}>
          Résultats de la recherche : <strong>{pharmacyCount} pharmacies trouvées</strong>
        </p>

        {selectedResult && (
          <SelectedPharmacyCard
            result={selectedResult}
            userLat={userLat}
            userLon={userLon}
            onClose={() => setSelectedKey(null)}
          />
        )}
      </div>

      <MapContainer center={[userLat, userLon]} zoom={14} zoomControl={false} className={styles.map}>
        <TileLayer url={TILE_URL} attribution={TILE_ATTRIBUTION} />
        <ZoomControl position="bottomright" />
        <FitBounds points={boundsPoints} />
        <MapClickHandler onBackgroundClick={() => setSelectedKey(null)} />

        <Marker position={[userLat, userLon]} icon={userIcon} interactive={false} keyboard={false} />

        {pins.map((result) => (
          <Marker
            key={resultKey(result)}
            position={[result.latitude, result.longitude]}
            icon={buildPharmacyIcon(result.price_gnf)}
            eventHandlers={{ click: () => setSelectedKey(resultKey(result)) }}
          />
        ))}
      </MapContainer>
    </div>
  );
}
