/**
 * Straight-line distance helpers for the Results screen's "X km de vous"
 * label.
 *
 * This is plain haversine, with no walking-realism correction. The
 * backend's own ranking (`walking_distance_m` in
 * `backend/app/services/ranking.py`) multiplies the same haversine figure
 * by a constant 1.4 walking-realism factor (Friesen et al. 2025) before
 * scoring. A constant factor applied uniformly to every pharmacy never
 * changes relative ordering, so the plain distance calculated here still
 * sorts consistently with the backend's ranked response; it is just not
 * the literal metres a pedestrian would walk.
 */

const EARTH_RADIUS_M = 6_371_000;

function toRadians(degrees: number): number {
  return (degrees * Math.PI) / 180;
}

/** Great-circle distance in metres between two lat/lon points. */
export function haversineDistanceMeters(
  lat1: number,
  lon1: number,
  lat2: number,
  lon2: number,
): number {
  const dLat = toRadians(lat2 - lat1);
  const dLon = toRadians(lon2 - lon1);

  const a =
    Math.sin(dLat / 2) ** 2 +
    Math.cos(toRadians(lat1)) * Math.cos(toRadians(lat2)) * Math.sin(dLon / 2) ** 2;

  return 2 * EARTH_RADIUS_M * Math.asin(Math.sqrt(a));
}

/** Formats a metre distance as "150 m" below 1 km, or "1.2 km" from 1 km up. */
export function formatDistance(meters: number): string {
  if (meters < 1000) {
    return `${Math.round(meters)} m`;
  }

  return `${(meters / 1000).toFixed(1)} km`;
}
