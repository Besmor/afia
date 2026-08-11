import { useNavigate } from 'react-router-dom';
import type { SearchResult } from '../lib/api';
import { formatDistance, haversineDistanceMeters } from '../lib/geo';
import { formatPriceGnf } from '../lib/format';
import { IconChevronRight, IconPharmacyCross, IconPin, IconStock } from './icons';
import styles from './PharmacyCard.module.css';

interface PharmacyCardProps {
  result: SearchResult;
  userLat: number;
  userLon: number;
}

/**
 * Digital-maturity tier badge colours/labels. Screen 5 was never inspected
 * in Figma (docs/figma-inspection.md marks it NOT INSPECTED, blocked by the
 * MCP rate limit) and the design has no digital-maturity affordance at all
 * — this badge surfaces backend ranking data (`app/services/ranking.py`,
 * `TIER_TRUST_SCORES`) that the design never accounted for. Ramp goes from
 * neutral grey (no digital footprint) to full primary green (API-linked,
 * the most trusted/freshest tier), reusing only existing design tokens.
 */
const TIER_BADGE: Record<string, { label: string; background: string; color: string }> = {
  NONE: {
    label: 'Non numérique',
    background: 'var(--color-gray-02-30)',
    color: 'var(--color-gray-02-80)',
  },
  BASIC_WEBSITE: {
    label: 'Site web',
    background: 'var(--color-accent-022)',
    color: 'var(--color-accent-03)',
  },
  ECOMMERCE_PARTIAL: {
    label: 'E-commerce partiel',
    background: 'var(--color-secondary-02)',
    color: 'var(--color-secondary-05)',
  },
  ECOMMERCE_FULL: {
    label: 'E-commerce complet',
    background: 'var(--color-secondary-01)',
    color: 'var(--color-secondary-06)',
  },
  API_LINKED: {
    label: 'Connectée (API)',
    background: 'var(--color-primary-01)',
    color: 'var(--color-gray-02-10)',
  },
};

const FALLBACK_TIER_BADGE = { label: 'Maturité inconnue', background: 'var(--color-gray-02-30)', color: 'var(--color-gray-02-80)' };

/**
 * One pharmacy/stock match on the Results screen. Adapted from the Figma
 * list-row card (`Vue Liste-Résultat des recherches.svg`): the OUVERTE/
 * FERMÉE/"De garde" pills from the design have no backing data in
 * `SearchResult` (no opening-hours or on-call fields are returned by
 * `GET /search`), so that row is replaced with the district, calculated
 * distance and the digital-maturity badge above.
 */
export function PharmacyCard({ result, userLat, userLon }: PharmacyCardProps) {
  const navigate = useNavigate();

  const distanceMeters = haversineDistanceMeters(
    userLat,
    userLon,
    result.latitude,
    result.longitude,
  );
  const tierBadge = TIER_BADGE[result.digital_maturity] ?? FALLBACK_TIER_BADGE;

  function handleClick() {
    const params = new URLSearchParams({ medication_id: String(result.medication_id) });
    // Full result is also passed as router state, so PharmacyDetail can show
    // the medication name/stock/price without a second fetch. `medication_id`
    // stays in the query string too so the route is still meaningful if
    // shared or opened directly (state would then just be absent).
    navigate(`/pharmacy/${result.pharmacy_id}?${params.toString()}`, {
      state: { medicationResult: result },
    });
  }

  return (
    <button type="button" className={styles.card} onClick={handleClick}>
      <div className={styles.header}>
        <IconPharmacyCross className={styles.crossIcon} />
        <div className={styles.titleBlock}>
          <h3 className={styles.name}>{result.pharmacy_name}</h3>
          <p className={styles.variant}>
            {result.medication_form}, {result.medication_strength}
          </p>
        </div>
        <IconChevronRight className={styles.chevron} />
      </div>

      <div className={styles.meta}>
        <IconPin className={styles.pinIcon} />
        <span>{result.district}</span>
        <span className={styles.dot} aria-hidden="true" />
        <span>{formatDistance(distanceMeters)}</span>
        <span
          className={styles.tierBadge}
          style={{ background: tierBadge.background, color: tierBadge.color }}
        >
          {tierBadge.label}
        </span>
      </div>

      <div className={styles.footer}>
        <span className={styles.stockPill}>
          <IconStock className={styles.stockIcon} />
          {result.quantity} en stock
        </span>
        <span className={styles.price}>{formatPriceGnf(result.price_gnf)}</span>
      </div>
    </button>
  );
}
