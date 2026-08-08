import type { InputHTMLAttributes } from 'react';
import styles from './SearchBar.module.css';

interface SearchBarProps extends Omit<InputHTMLAttributes<HTMLInputElement>, 'type' | 'onChange'> {
  value: string;
  onChange: (value: string) => void;
}

/**
 * Medication query input, rounded-pill style per the Accueil/Recherche
 * search bar (docs/figma-inspection.md, Screens 1-3). Placeholder copy is
 * the exact French text observed on the Accueil screen.
 */
export function SearchBar({ value, onChange, ...inputProps }: SearchBarProps) {
  return (
    <input
      type="text"
      className={styles.input}
      placeholder="Quel médicaments recherchez-vous"
      value={value}
      onChange={(event) => onChange(event.target.value)}
      {...inputProps}
    />
  );
}
