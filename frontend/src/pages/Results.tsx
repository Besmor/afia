import { useCallback, useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { fetchSearch, type SearchResult } from '../lib/api';
import { PrimaryButton } from '../components/PrimaryButton';
import { PharmacyCard } from '../components/PharmacyCard';
import { IconChevronLeft, IconFilter } from '../components/icons';
import styles from './Results.module.css';

type RequestState =
  | { status: 'loading' }
  | { status: 'error' }
  | { status: 'success'; results: SearchResult[] };

/**
 * Results screen (docs/figma-inspection.md, Screen 5 — NOT INSPECTED in
 * Figma, see PharmacyCard's tier-badge comment; built from
 * `design-refs/Vue Liste-Résultat des recherches.svg` /
 * `results-list.png`). FT-6 Block A wired the E2E search call; this is
 * Block B, replacing the raw JSON dump with styled cards.
 *
 * The OUVERTE/FERMÉE/"De garde"/"Liste"-"Maps" toggle and filter-popup
 * content from the Figma frame have no backing data or functionality yet
 * (no opening-hours fields, no map view, no filter logic) — per CLAUDE.md's
 * critical-path scope, only the filter *icon* is rendered, inert.
 */
export function Results() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const query = searchParams.get('q') ?? '';
  const userLat = Number(searchParams.get('user_lat'));
  const userLon = Number(searchParams.get('user_lon'));

  // Precise path (Block F): Landing's autocomplete + dose picker navigates
  // here with medication_id/strength/inn instead of a free-text q.
  const medicationIdParam = searchParams.get('medication_id');
  const medicationId = medicationIdParam !== null ? Number(medicationIdParam) : undefined;
  const strength = searchParams.get('strength') ?? undefined;
  const inn = searchParams.get('inn') ?? '';

  const displayTerm = medicationId !== undefined ? `${inn} ${strength ?? ''}`.trim() : query;

  const [state, setState] = useState<RequestState>({ status: 'loading' });

  const runSearch = useCallback(() => {
    setState({ status: 'loading' });

    fetchSearch(query, userLat, userLon, 10, medicationId !== undefined ? { medicationId, strength } : undefined)
      .then((results) => {
        setState({ status: 'success', results });
      })
      .catch(() => {
        setState({ status: 'error' });
      });
  }, [query, userLat, userLon, medicationId, strength]);

  useEffect(() => {
    runSearch();
  }, [runSearch]);

  const pharmacyCount =
    state.status === 'success' ? new Set(state.results.map((r) => r.pharmacy_id)).size : 0;

  return (
    <main className={styles.page}>
      <header className={styles.header}>
        <button
          type="button"
          className={styles.iconButton}
          onClick={() => navigate('/')}
          aria-label="Retour"
        >
          <IconChevronLeft className={styles.icon} />
        </button>

        <h1 className={styles.heading}>Résultats pour {displayTerm}</h1>

        <button type="button" className={styles.iconButton} aria-label="Filtrer">
          <IconFilter className={styles.icon} />
        </button>
      </header>

      {state.status === 'success' && (
        <p className={styles.count}>{pharmacyCount} pharmacies trouvées</p>
      )}

      {state.status === 'loading' && <p className={styles.status}>Recherche en cours…</p>}

      {state.status === 'error' && (
        <div className={styles.errorBox}>
          <p className={styles.errorText}>
            Impossible de charger les résultats. Vérifiez que le backend tourne sur localhost:8000.
          </p>
          <PrimaryButton onClick={runSearch}>Réessayer</PrimaryButton>
        </div>
      )}

      {state.status === 'success' && state.results.length === 0 && (
        <div className={styles.emptyBox}>
          <p className={styles.emptyText}>
            Aucune pharmacie n'a été trouvée pour « {displayTerm} ». Essayez un autre médicament ou
            vérifiez l'orthographe.
          </p>
        </div>
      )}

      {state.status === 'success' && state.results.length > 0 && (
        <ul className={styles.list}>
          {state.results.map((result) => (
            <li key={`${result.pharmacy_id}-${result.medication_id}`}>
              <PharmacyCard result={result} userLat={userLat} userLon={userLon} />
            </li>
          ))}
        </ul>
      )}
    </main>
  );
}
