import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { PrimaryButton } from '../components/PrimaryButton';
import { MedicationSearch } from '../components/MedicationSearch';
import { DistrictPicker } from '../components/DistrictPicker';
import { DEFAULT_LOCATION, fromDistrict, getUserLocation, type UserLocation } from '../lib/location';
import type { District } from '../constants/districts';
import type { AutocompleteResult } from '../lib/api';
import styles from './Landing.module.css';

type GeoStatus = 'checking' | 'resolved' | 'needs-picker';

const EMPTY_QUERY_MESSAGE = "Veuillez indiquer le nom d'un médicament pour lancer la recherche.";

/** Landing/search screen. See docs/figma-inspection.md, Screen 1 (Accueil). */
export function Landing() {
  const navigate = useNavigate();
  const [geoStatus, setGeoStatus] = useState<GeoStatus>('checking');
  const [location, setLocation] = useState<UserLocation | null>(null);
  const [query, setQuery] = useState('');
  const [medication, setMedication] = useState<AutocompleteResult | null>(null);
  const [dose, setDose] = useState<AutocompleteResult | null>(null);
  const [validationError, setValidationError] = useState<string | null>(null);

  // CTA is disabled only mid-pick: a medication chosen from the dropdown but
  // no dose yet. Plain free-text search (medication never picked) stays
  // enabled, same as before Block F.
  const searchDisabled = medication !== null && dose === null;

  useEffect(() => {
    let cancelled = false;

    getUserLocation()
      .then((resolved) => {
        if (cancelled) return;
        setLocation(resolved);
        setGeoStatus('resolved');
      })
      .catch(() => {
        if (cancelled) return;
        setGeoStatus('needs-picker');
      });

    return () => {
      cancelled = true;
    };
  }, []);

  function handleDistrictSelect(district: District) {
    setLocation(fromDistrict(district));
    setGeoStatus('resolved');
  }

  function handleSearch() {
    const origin = location ?? DEFAULT_LOCATION;

    if (medication && dose) {
      setValidationError(null);
      const params = new URLSearchParams({
        medication_id: String(dose.id),
        strength: dose.strength,
        inn: medication.inn,
        user_lat: String(origin.lat),
        user_lon: String(origin.lon),
      });
      // Carry the matched brand through so Results/Détail can lead with it
      // instead of the INN (Task #30, Reviewer 1's "walkaway moment").
      if (medication.matched_brand) {
        params.set('brand', medication.matched_brand);
      }
      navigate(`/results?${params.toString()}`);
      return;
    }

    if (searchDisabled) return; // medication picked, dose not yet: CTA should be disabled anyway

    if (query.trim() === '') {
      setValidationError(EMPTY_QUERY_MESSAGE);
      return;
    }

    setValidationError(null);
    const params = new URLSearchParams({
      q: query.trim(),
      user_lat: String(origin.lat),
      user_lon: String(origin.lon),
    });
    navigate(`/results?${params.toString()}`);
  }

  return (
    <div className={styles.page}>
      <img className={styles.backdrop} src="/illustrations/Background-img-mobile.svg" alt="" aria-hidden="true" />

      <div className={styles.content}>
        <header className={styles.header}>
          <img className={styles.logo} src="/afia-logo-lockup.svg" alt="Afia" />
        </header>

        <h1 className={styles.heading}>Trouvez vos médicaments</h1>

        <div className={styles.form}>
          {geoStatus === 'checking' && (
            <p className={styles.locationStatus}>Localisation en cours…</p>
          )}

          {geoStatus === 'needs-picker' && <DistrictPicker onSelect={handleDistrictSelect} />}

          <MedicationSearch
            query={query}
            onQueryChange={(value) => {
              setQuery(value);
              if (validationError) setValidationError(null);
            }}
            medication={medication}
            onMedicationChange={setMedication}
            dose={dose}
            onDoseChange={setDose}
            onSubmitFreeText={handleSearch}
          />

          {validationError && <p className={styles.validationError}>{validationError}</p>}

          <PrimaryButton onClick={handleSearch} disabled={searchDisabled} aria-disabled={searchDisabled}>
            Rechercher
          </PrimaryButton>
        </div>
      </div>
    </div>
  );
}
