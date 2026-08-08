/**
 * User location resolution for the Landing screen.
 *
 * `getUserLocation()` tries the browser Geolocation API and resolves with
 * the coordinates on success. It rejects (does not resolve with a fallback
 * itself) when geolocation is unsupported, denied, or times out, so the
 * caller (Landing.tsx) can decide how to degrade — in our case, showing
 * `DistrictPicker`. Once the user picks a district, the caller builds the
 * `UserLocation` for that choice with `fromDistrict()`.
 */

import { DEFAULT_CENTROID, type District } from '../constants/districts';

export interface UserLocation {
  lat: number;
  lon: number;
  source: 'geolocation' | 'picker' | 'default';
}

const GEOLOCATION_OPTIONS: PositionOptions = {
  enableHighAccuracy: false,
  timeout: 8000,
  maximumAge: 60_000,
};

export function getUserLocation(): Promise<UserLocation> {
  return new Promise((resolve, reject) => {
    if (!('geolocation' in navigator)) {
      reject(new Error('Geolocation is not available in this browser.'));
      return;
    }

    navigator.geolocation.getCurrentPosition(
      (position) => {
        resolve({
          lat: position.coords.latitude,
          lon: position.coords.longitude,
          source: 'geolocation',
        });
      },
      (error) => {
        reject(error);
      },
      GEOLOCATION_OPTIONS,
    );
  });
}

/** Builds a `UserLocation` from a district chosen in `DistrictPicker`. */
export function fromDistrict(district: District): UserLocation {
  return { lat: district.centroid.lat, lon: district.centroid.lon, source: 'picker' };
}

/** Kaloum centroid, matching the backend's own default search origin. */
export const DEFAULT_LOCATION: UserLocation = {
  lat: DEFAULT_CENTROID.lat,
  lon: DEFAULT_CENTROID.lon,
  source: 'default',
};
