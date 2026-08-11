/**
 * Live OUVERTE/FERMÉE/"De garde" status for a pharmacy, shared by
 * PharmacyCard (Results) and PharmacyDetail's meta row.
 *
 * Simplification: this reads the browser's local time/day directly rather
 * than converting through a Conakry timezone lookup. For the local demo the
 * operator's machine is assumed to already be set close to Conakry time
 * (GMT, no DST); a production build would want an explicit
 * `Intl.DateTimeFormat` conversion instead. Documented here as the one
 * simplification this module makes.
 */

export type OpeningLabel = 'OUVERTE' | 'FERMÉE';

export interface OpeningStatus {
  label: OpeningLabel;
  /** "De garde": open on Sundays, when most pharmacies are closed. Shown
   *  whenever `open_on_sunday` is true, regardless of what day it is today,
   *  so users can plan ahead rather than only seeing it on a Sunday visit. */
  isOnCall: boolean;
}

/** Zero-padded "HH:MM:SS" for the given local time, comparable lexicographically
 *  against the backend's `time.isoformat()` strings (same fixed-width format). */
function toTimeString(date: Date): string {
  const hh = String(date.getHours()).padStart(2, '0');
  const mm = String(date.getMinutes()).padStart(2, '0');
  const ss = String(date.getSeconds()).padStart(2, '0');
  return `${hh}:${mm}:${ss}`;
}

export function computeStatus(
  opensAt: string,
  closesAt: string,
  openOnSunday: boolean,
  now: Date = new Date(),
): OpeningStatus {
  const isSunday = now.getDay() === 0;
  const nowTime = toTimeString(now);

  const label: OpeningLabel = isSunday
    ? openOnSunday
      ? 'OUVERTE'
      : 'FERMÉE'
    : opensAt <= nowTime && nowTime < closesAt
      ? 'OUVERTE'
      : 'FERMÉE';

  return { label, isOnCall: openOnSunday };
}
