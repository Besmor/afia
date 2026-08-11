import { useCallback, useEffect, useState } from 'react';
import { useLocation, useNavigate, useParams, useSearchParams } from 'react-router-dom';
import { fetchPharmacy, type PharmacyDetail as PharmacyDetailData, type SearchResult } from '../lib/api';
import { formatDistance, haversineDistanceMeters } from '../lib/geo';
import { formatPriceGnf, formatTime } from '../lib/format';
import { DEFAULT_LOCATION, getUserLocation, type UserLocation } from '../lib/location';
import {
  IconChevronDown,
  IconChevronLeft,
  IconDirections,
  IconPhone,
  IconShare,
  IconStock,
} from '../components/icons';
import styles from './PharmacyDetail.module.css';

type RequestState =
  | { status: 'loading' }
  | { status: 'error' }
  | { status: 'success'; pharmacy: PharmacyDetailData };

type TabKey = 'medicaments' | 'infos';

const TABS: { key: TabKey; label: string }[] = [
  { key: 'medicaments', label: 'Médicaments' },
  { key: 'infos', label: 'Infos Générales' },
];

/** Tabs shown per the Figma frame but out of MVP scope (CLAUDE.md critical path). */
const DISABLED_TABS = ['Moyen de paiement', 'Avis utilisateurs'];

const DAYS_OF_WEEK = ['Dimanche', 'Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi'];

/**
 * Pharmacy Detail screen (FT-8), built from the Figma "Info générales" and
 * "médicaments" frames (`design-refs/Détails pharmacie-*.svg` /
 * `pharmacy-detail-*.png`). Reached from `PharmacyCard` with
 * `/pharmacy/:pharmacyId?medication_id=X`; `medication_id` is kept in the
 * URL so the route stays meaningful if shared or opened directly, while the
 * full `SearchResult` also travels as router state (see PharmacyCard.tsx)
 * so this page does not need a second endpoint to show the medication that
 * was searched for.
 *
 * Per the task brief: no real photos (solid colour block), no live
 * open/closed or "de garde" logic (static placeholders, fast-follow task),
 * no real map (placeholder rectangle), no booking CTA, Moyen de paiement
 * and Avis utilisateurs are out of MVP scope.
 */
export function PharmacyDetail() {
  const { pharmacyId } = useParams<{ pharmacyId: string }>();
  const navigate = useNavigate();
  const routerLocation = useLocation();
  const [searchParams] = useSearchParams();

  const medicationId = searchParams.get('medication_id');
  const medicationResult =
    (routerLocation.state as { medicationResult?: SearchResult } | null)?.medicationResult ?? null;

  const [state, setState] = useState<RequestState>({ status: 'loading' });
  const [userLocation, setUserLocation] = useState<UserLocation | null>(null);
  const [activeTab, setActiveTab] = useState<TabKey>('infos');
  const [descriptionExpanded, setDescriptionExpanded] = useState(false);

  const loadPharmacy = useCallback(() => {
    if (!pharmacyId) return;

    setState({ status: 'loading' });
    fetchPharmacy(pharmacyId)
      .then((pharmacy) => setState({ status: 'success', pharmacy }))
      .catch(() => setState({ status: 'error' }));
  }, [pharmacyId]);

  useEffect(() => {
    loadPharmacy();
  }, [loadPharmacy]);

  // Best-effort distance for the meta row; not gated on (falls back to the
  // Kaloum centroid), same resolution strategy as Landing.tsx.
  useEffect(() => {
    let cancelled = false;

    getUserLocation()
      .then((resolved) => {
        if (!cancelled) setUserLocation(resolved);
      })
      .catch(() => {
        if (!cancelled) setUserLocation(DEFAULT_LOCATION);
      });

    return () => {
      cancelled = true;
    };
  }, []);

  const pharmacy = state.status === 'success' ? state.pharmacy : null;
  const distanceMeters =
    pharmacy && userLocation
      ? haversineDistanceMeters(userLocation.lat, userLocation.lon, pharmacy.latitude, pharmacy.longitude)
      : null;

  return (
    <main className={styles.page}>
      <div className={styles.photo}>
        <button
          type="button"
          className={`${styles.photoIconButton} ${styles.photoIconButtonLeft}`}
          onClick={() => navigate(-1)}
          aria-label="Retour"
        >
          <IconChevronLeft className={styles.photoIcon} />
        </button>
        <button
          type="button"
          className={`${styles.photoIconButton} ${styles.photoIconButtonRight}`}
          aria-label="Partager"
        >
          <IconShare className={styles.photoIcon} />
        </button>
      </div>

      {state.status === 'loading' && <p className={styles.status}>Chargement de la pharmacie…</p>}

      {state.status === 'error' && (
        <div className={styles.errorBox}>
          <p className={styles.errorText}>
            Impossible de charger cette pharmacie. Vérifiez que le backend tourne sur localhost:8000.
          </p>
          <button type="button" className={styles.retryButton} onClick={loadPharmacy}>
            Réessayer
          </button>
        </div>
      )}

      {pharmacy && (
        <div className={styles.body}>
          <h1 className={styles.name}>{pharmacy.name}</h1>

          <div className={styles.metaRow}>
            {distanceMeters !== null && <span>{formatDistance(distanceMeters)} de vous</span>}
            {distanceMeters !== null && <span className={styles.dot} aria-hidden="true" />}
            {/* Placeholder: no on-call/open-closed data yet (fast-follow task); static per design. */}
            <span>De garde</span>
            <span className={styles.dot} aria-hidden="true" />
            <span className={styles.statusPill}>OUVERTE</span>
            <span className={styles.dot} aria-hidden="true" />
            <span className={styles.closesAt}>
              Ferme à ({formatTime(pharmacy.closes_at)})
              <IconChevronDown className={styles.chevronDownIcon} />
            </span>
          </div>

          <div className={styles.addressRow}>
            <span>{pharmacy.district}, Conakry, Guinée</span>
            <IconDirections className={styles.directionsIcon} />
          </div>

          <div className={styles.mapPlaceholder}>Carte (à venir)</div>

          {medicationId && (
            <div className={styles.medicationBanner}>
              <IconStock className={styles.medicationBannerIcon} />
              <span>
                Pour&nbsp;:{' '}
                <strong>
                  {medicationResult
                    ? `${medicationResult.medication_inn}, ${medicationResult.medication_strength}`
                    : `médicament #${medicationId}`}
                </strong>
              </span>
            </div>
          )}

          <div className={styles.tabStrip}>
            {TABS.map((tab) => (
              <button
                key={tab.key}
                type="button"
                className={activeTab === tab.key ? styles.tabActive : styles.tab}
                onClick={() => setActiveTab(tab.key)}
              >
                {tab.label}
              </button>
            ))}
            {DISABLED_TABS.map((label) => (
              <button key={label} type="button" className={styles.tabDisabled} disabled title="Bientôt disponible">
                {label} <span className={styles.tabDisabledHint}>(à venir)</span>
              </button>
            ))}
          </div>

          {activeTab === 'medicaments' && (
            <section className={styles.tabContent} aria-label="Médicaments">
              <h2 className={styles.sectionHeading}>Médicaments disponibles</h2>
              {medicationResult ? (
                <div className={styles.medicationCard}>
                  <div>
                    <p className={styles.medicationName}>
                      {medicationResult.medication_inn}, {medicationResult.medication_form},{' '}
                      {medicationResult.medication_strength}
                    </p>
                    <span className={styles.stockPill}>
                      <IconStock className={styles.stockIcon} />
                      {medicationResult.quantity} en stock
                    </span>
                  </div>
                  <span className={styles.price}>{formatPriceGnf(medicationResult.price_gnf)}</span>
                </div>
              ) : (
                <p className={styles.placeholderText}>
                  Aucun médicament sélectionné. Lancez une recherche pour voir la disponibilité dans cette
                  pharmacie.
                </p>
              )}
              <p className={styles.placeholderText}>Catalogue complet de la pharmacie à venir.</p>
            </section>
          )}

          {activeTab === 'infos' && (
            <section className={styles.tabContent} aria-label="Infos Générales">
              <h2 className={styles.sectionHeading}>Infos Générales</h2>
              <p className={styles.description}>
                {descriptionExpanded
                  ? "Description détaillée à venir. Cette pharmacie fait partie de l'écosystème synthétique Afia, calibré sur le scan de maturité numérique de Conakry."
                  : "Description à venir. Cette pharmacie fait partie de l'écosystème synthétique Afia."}
                {!descriptionExpanded && (
                  <button
                    type="button"
                    className={styles.readMoreButton}
                    onClick={() => setDescriptionExpanded(true)}
                  >
                    Tout lire
                  </button>
                )}
              </p>

              <div className={styles.contactRow}>
                <div>
                  <p className={styles.contactLabel}>Site web</p>
                  <p className={styles.contactValue}>Non renseigné</p>
                </div>
                <div>
                  <p className={styles.contactLabel}>Téléphone</p>
                  <p className={styles.contactValue}>{pharmacy.phone ?? 'Non renseigné'}</p>
                </div>
                {pharmacy.phone && (
                  <a href={`tel:${pharmacy.phone}`} className={styles.callButton}>
                    <IconPhone className={styles.callIcon} />
                    Appeler
                  </a>
                )}
              </div>

              <h3 className={styles.sectionHeading}>Horaires d&apos;ouvertures</h3>
              <ul className={styles.hoursList}>
                {DAYS_OF_WEEK.map((day, index) => {
                  const isSunday = index === 0;
                  const isOpen = !isSunday || pharmacy.open_on_sunday;

                  return (
                    <li key={day} className={styles.hoursRow}>
                      <span className={styles.hoursDay}>{day}</span>
                      <span className={isOpen ? styles.hoursTime : styles.hoursClosed}>
                        {isOpen ? `${formatTime(pharmacy.opens_at)}–${formatTime(pharmacy.closes_at)}` : 'Fermé'}
                      </span>
                    </li>
                  );
                })}
              </ul>
            </section>
          )}
        </div>
      )}
    </main>
  );
}
