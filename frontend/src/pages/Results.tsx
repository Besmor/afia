import { useSearchParams } from 'react-router-dom';

/**
 * Placeholder for the results screen (docs/figma-inspection.md, Screen 5 —
 * not yet inspected, see the Figma access blocker noted at the top of that
 * doc). This page only exists so the Landing screen's navigation has
 * somewhere to land; the real implementation is a separate ticket.
 */
export function Results() {
  const [searchParams] = useSearchParams();

  return (
    <main style={{ padding: 'var(--spacing-2xl)', fontFamily: 'Manrope, sans-serif' }}>
      <h1 style={{ fontFamily: "'Baloo Tamma 2', sans-serif", color: 'var(--color-secondary-04)' }}>
        Résultats (à venir)
      </h1>
      <p>q = {searchParams.get('q')}</p>
      <p>user_lat = {searchParams.get('user_lat')}</p>
      <p>user_lon = {searchParams.get('user_lon')}</p>
    </main>
  );
}
