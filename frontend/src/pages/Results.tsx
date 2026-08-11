import { useCallback, useEffect, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { fetchSearch, type SearchResult } from '../lib/api';
import { PrimaryButton } from '../components/PrimaryButton';

type RequestState =
  | { status: 'loading' }
  | { status: 'error' }
  | { status: 'success'; results: SearchResult[] };

/**
 * Results screen (docs/figma-inspection.md, Screen 5). Wires the E2E search
 * call for FT-6 Block A: q/user_lat/user_lon come from the URL (set by
 * Landing.tsx), the raw response is dumped as JSON for now, and the styled
 * pharmacy card comes in Block B.
 */
export function Results() {
  const [searchParams] = useSearchParams();
  const query = searchParams.get('q') ?? '';
  const userLat = Number(searchParams.get('user_lat'));
  const userLon = Number(searchParams.get('user_lon'));

  const [state, setState] = useState<RequestState>({ status: 'loading' });

  const runSearch = useCallback(() => {
    setState({ status: 'loading' });

    fetchSearch(query, userLat, userLon)
      .then((results) => {
        setState({ status: 'success', results });
      })
      .catch(() => {
        setState({ status: 'error' });
      });
  }, [query, userLat, userLon]);

  useEffect(() => {
    runSearch();
  }, [runSearch]);

  return (
    <main style={{ padding: 'var(--spacing-2xl)', fontFamily: 'Manrope, sans-serif' }}>
      <h1 style={{ fontFamily: "'Baloo Tamma 2', sans-serif", color: 'var(--color-secondary-04)' }}>
        {state.status === 'success' ? 'Résultats' : 'Résultats (à venir)'}
      </h1>

      {state.status === 'loading' && <p>Recherche en cours...</p>}

      {state.status === 'error' && (
        <div>
          <p style={{ color: 'var(--color-danger)' }}>
            Impossible de charger les résultats. Vérifiez que le backend tourne sur localhost:8000.
          </p>
          <PrimaryButton onClick={runSearch}>Réessayer</PrimaryButton>
        </div>
      )}

      {state.status === 'success' && <pre>{JSON.stringify(state.results, null, 2)}</pre>}
    </main>
  );
}
