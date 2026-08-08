import { DISTRICTS, type District } from '../constants/districts';
import styles from './DistrictPicker.module.css';

interface DistrictPickerProps {
  onSelect: (district: District) => void;
}

/**
 * Fallback location UI shown when browser geolocation is denied or
 * unavailable. Lists the 5 Conakry districts we have synthetic pharmacy
 * coverage for (see `src/constants/districts.ts`), styled as the design
 * system's list-row card pattern.
 */
export function DistrictPicker({ onSelect }: DistrictPickerProps) {
  return (
    <div>
      <p className={styles.message}>
        Nous avons besoin de votre position pour trouver les pharmacies les plus proches. Veuillez
        autoriser l'accès à la localisation dans les réglages, ou choisissez votre commune ci-dessous.
      </p>
      <div className={styles.card}>
        {DISTRICTS.map((district) => (
          <button
            key={district.name}
            type="button"
            className={styles.row}
            onClick={() => onSelect(district)}
          >
            <img
              className={styles.icon}
              src="/illustrations/icon-pharmacie-cartes.svg"
              alt=""
              aria-hidden="true"
            />
            {district.name}
          </button>
        ))}
      </div>
    </div>
  );
}
