import { useCallback, useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { fetchSearch, type SearchResult } from '../lib/api';
import { DEFAULT_LOCATION } from '../lib/location';
import { PrimaryButton } from '../components/PrimaryButton';
import { PharmacyCard } from '../components/PharmacyCard';
import { ResultsMap } from '../components/ResultsMap';
import { IconChevronLeft, IconFilter, IconListView, IconMap } from '../components/icons';
import styles from './Results.module.css';

type RequestState =
  | { status: 'loading' }
  | { status: 'error' }
  | { status: 'success'; results: SearchResult[] };

type ResultsView = 'list' | 'map';

/**
 * Results screen (docs/figma-inspection.md, Screen 5 — NOT INSPECTED in
 * Figma, see PharmacyCard's tier-badge comment; built from
 * `design-refs/Vue Liste-Résultat des recherches.svg` /
 * `results-list.png`). FT-6 Block A wired the E2E search call; Block B
 * replaced the raw JSON dump with styled cards; Block G (this file) adds the
 * Liste/Maps view toggle from `design-refs/Vue Maps-Résultat des
 * recherches*.svg`.
 *
 * The filter-popup content from the Figma frame still has no backing logic
 * — per CLAUDE.md's critical-path scope, only the filter *icon* is
 * rendered, inert.
 */
export function Results() {
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
  const query = searchParams.get('q') ?? '';
  const userLat = Number(searchParams.get('user_lat'));
  const userLon = Number(searchParams.get('user_lon'));
  // ResultsMap needs a always-valid centre even if this page were opened
  // directly without user_lat/user_lon (PharmacyCard's list rendering
  // already tolerates NaN here unchanged, so only the new map path guards
  // against it).
  const mapUserLat = Number.isFinite(userLat) ? userLat : DEFAULT_LOCATION.lat;
  const mapUserLon = Number.isFinite(userLon) ? userLon : DEFAULT_LOCATION.lon;

  // Precise path (Block F): Landing's autocomplete + dose picker navigates
  // here with medication_id/strength/inn instead of a free-text q.
  const medicationIdParam = searchParams.get('medication_id');
  const medicationId = medicationIdParam !== null ? Number(medicationIdParam) : undefined;
  const strength = searchParams.get('strength') ?? undefined;
  const inn = searchParams.get('inn') ?? '';
  // Set only when Landing's autocomplete matched a brand name (Task #30).
  // Leads the heading/card so a brand search doesn't read as "not found".
  const brand = searchParams.get('brand');

  const displayLabel = brand ?? inn;
  const displayTerm = medicationId !== undefined ? `${displayLabel} ${strength ?? ''}`.trim() : query;

  const [state, setState] = useState<RequestState>({ status: 'loading' });
  // Liste/Maps toggle (Block G), kept in the `view` URL param so browser
  // Back from Pharmacy Detail restores the view the user was on rather than
  // always resetting to 'list'.
  const view: ResultsView = searchParams.get('view') === 'map' ? 'map' : 'list';

  function setView(next: ResultsView) {
    setSearchParams(
      (previous) => {
        const params = new URLSearchParams(previous);
        if (next === 'map') {
          params.set('view', 'map');
        } else {
          params.delete('view');
        }
        return params;
      },
      { replace: true },
    );
  }

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

        <div className={styles.headingWrap}>
          <h1 className={styles.heading}>Résultats pour {displayTerm}</h1>
          {medicationId !== undefined && brand && <p className={styles.headingSubtitle}>({inn})</p>}
        </div>

        <button type="button" className={styles.iconButton} aria-label="Filtrer">
          <IconFilter className={styles.icon} />
        </button>
      </header>

      <div className={styles.viewToggle} role="tablist" aria-label="Affichage des résultats">
        <button
          type="button"
          role="tab"
          aria-selected={view === 'list'}
          className={view === 'list' ? styles.toggleButtonActive : styles.toggleButton}
          onClick={() => setView('list')}
        >
          <IconListView className={styles.toggleIcon} />
          Liste
        </button>
        <button
          type="button"
          role="tab"
          aria-selected={view === 'map'}
          className={view === 'map' ? styles.toggleButtonActive : styles.toggleButton}
          onClick={() => setView('map')}
        >
          <IconMap className={styles.toggleIcon} />
          Maps
        </button>
      </div>

      {state.status === 'success' && view === 'list' && (
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

      {state.status === 'success' && view === 'list' && state.results.length === 0 && (
        <div className={styles.emptyBox}>
          <p className={styles.emptyText}>
            Aucune pharmacie n'a été trouvée pour « {displayTerm} ». Essayez un autre médicament ou
            vérifiez l'orthographe.
          </p>
        </div>
      )}

      {state.status === 'success' && view === 'list' && state.results.length > 0 && (
        <ul className={styles.list}>
          {state.results.map((result) => (
            <li key={`${result.pharmacy_id}-${result.medication_id}`}>
              <PharmacyCard result={result} userLat={userLat} userLon={userLon} brand={brand ?? undefined} />
            </li>
          ))}
        </ul>
      )}

      {state.status === 'success' && view === 'map' && (
        <div className={styles.mapFrame}>
          <ResultsMap
            results={state.results}
            userLat={mapUserLat}
            userLon={mapUserLon}
            brand={brand ?? undefined}
          />
        </div>
      )}
    </main>
  );
}
