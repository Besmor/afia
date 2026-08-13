import { useEffect, useRef, useState } from 'react';
import type { KeyboardEvent } from 'react';
import { fetchAutocomplete, type AutocompleteResult } from '../lib/api';
import { useDebouncedValue } from '../lib/useDebouncedValue';
import { formLabelFr, isCapsuleFormIcon } from '../lib/medicationForm';
import { IconCapsule, IconCheck, IconDrop } from './icons';
import { SearchBar } from './SearchBar';
import styles from './MedicationSearch.module.css';

const AUTOCOMPLETE_DEBOUNCE_MS = 200;

interface MedicationSearchProps {
  /** Free-text query, only meaningful while no `medication` is selected. */
  query: string;
  onQueryChange: (value: string) => void;
  medication: AutocompleteResult | null;
  onMedicationChange: (value: AutocompleteResult | null) => void;
  dose: AutocompleteResult | null;
  onDoseChange: (value: AutocompleteResult | null) => void;
  /** Enter pressed with no suggestion highlighted: fall back to the free-text search path. */
  onSubmitFreeText: () => void;
}

/**
 * Landing page search bar (Block F): free-text input with an autocomplete
 * dropdown (`Recherche.svg` / `Recherche-Sélection.svg`), which on picking a
 * row splits into a `[ médicament | Dose ]` bar with its own dose dropdown
 * (`Dose_selection.svg` / `Dose_selected.svg`).
 */
export function MedicationSearch({
  query,
  onQueryChange,
  medication,
  onMedicationChange,
  dose,
  onDoseChange,
  onSubmitFreeText,
}: MedicationSearchProps) {
  const [suggestions, setSuggestions] = useState<AutocompleteResult[]>([]);
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const [activeIndex, setActiveIndex] = useState(-1);

  const [doseOptions, setDoseOptions] = useState<AutocompleteResult[]>([]);
  const [doseOpen, setDoseOpen] = useState(false);
  const [doseActiveIndex, setDoseActiveIndex] = useState(-1);

  const debouncedQuery = useDebouncedValue(query, AUTOCOMPLETE_DEBOUNCE_MS);
  const containerRef = useRef<HTMLDivElement>(null);
  const doseTriggerRef = useRef<HTMLButtonElement>(null);

  // Autocomplete while in free-text mode (no medication picked yet).
  useEffect(() => {
    if (medication || debouncedQuery.trim().length < 1) {
      setSuggestions([]);
      setDropdownOpen(false);
      return;
    }

    let cancelled = false;
    fetchAutocomplete(debouncedQuery)
      .then((results) => {
        if (cancelled) return;
        setSuggestions(results);
        setDropdownOpen(results.length > 0);
        setActiveIndex(-1);
      })
      .catch(() => {
        if (cancelled) return;
        setSuggestions([]);
        setDropdownOpen(false);
      });

    return () => {
      cancelled = true;
    };
  }, [debouncedQuery, medication]);

  // Once a medication is picked, fetch its dose siblings (every catalogue
  // row sharing the same INN) for the dose dropdown.
  useEffect(() => {
    if (!medication) {
      setDoseOptions([]);
      return;
    }

    let cancelled = false;
    fetchAutocomplete(medication.inn)
      .then((results) => {
        if (cancelled) return;
        setDoseOptions(results.filter((row) => row.inn === medication.inn));
      })
      .catch(() => {
        if (cancelled) return;
        setDoseOptions([]);
      });

    return () => {
      cancelled = true;
    };
  }, [medication]);

  // The dose dropdown opens automatically right after picking a medication
  // (Dose_selection.svg), and focus moves to its trigger for keyboard users.
  useEffect(() => {
    if (medication) {
      setDoseOpen(true);
      doseTriggerRef.current?.focus();
    }
  }, [medication]);

  useEffect(() => {
    function handlePointerDown(event: MouseEvent) {
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
        setDropdownOpen(false);
        setDoseOpen(false);
      }
    }

    document.addEventListener('mousedown', handlePointerDown);
    return () => document.removeEventListener('mousedown', handlePointerDown);
  }, []);

  function selectMedication(result: AutocompleteResult) {
    onMedicationChange(result);
    onDoseChange(null);
    onQueryChange(result.inn);
    setDropdownOpen(false);
    setActiveIndex(-1);
  }

  function selectDose(result: AutocompleteResult) {
    onDoseChange(result);
    setDoseOpen(false);
    setDoseActiveIndex(-1);
  }

  /** Editing the medication field after a pick reverts to free-text mode. */
  function handleMedicationFieldChange(value: string) {
    onMedicationChange(null);
    onDoseChange(null);
    onQueryChange(value);
  }

  function handleInputKeyDown(event: KeyboardEvent<HTMLInputElement>) {
    if (!dropdownOpen || suggestions.length === 0) {
      if (event.key === 'Enter') onSubmitFreeText();
      return;
    }

    switch (event.key) {
      case 'ArrowDown':
        event.preventDefault();
        setActiveIndex((i) => Math.min(i + 1, suggestions.length - 1));
        break;
      case 'ArrowUp':
        event.preventDefault();
        setActiveIndex((i) => Math.max(i - 1, 0));
        break;
      case 'Enter':
        event.preventDefault();
        if (activeIndex >= 0) selectMedication(suggestions[activeIndex]);
        else onSubmitFreeText();
        break;
      case 'Escape':
        setDropdownOpen(false);
        setActiveIndex(-1);
        break;
      default:
        break;
    }
  }

  function handleDoseKeyDown(event: KeyboardEvent<HTMLButtonElement>) {
    if (!doseOpen) {
      if (event.key === 'Enter' || event.key === ' ') {
        event.preventDefault();
        setDoseOpen(true);
      }
      return;
    }

    switch (event.key) {
      case 'ArrowDown':
        event.preventDefault();
        setDoseActiveIndex((i) => Math.min(i + 1, doseOptions.length - 1));
        break;
      case 'ArrowUp':
        event.preventDefault();
        setDoseActiveIndex((i) => Math.max(i - 1, 0));
        break;
      case 'Enter':
        event.preventDefault();
        if (doseActiveIndex >= 0) selectDose(doseOptions[doseActiveIndex]);
        break;
      case 'Escape':
        setDoseOpen(false);
        setDoseActiveIndex(-1);
        break;
      default:
        break;
    }
  }

  if (!medication) {
    return (
      <div className={styles.container} ref={containerRef}>
        <SearchBar
          value={query}
          onChange={onQueryChange}
          onKeyDown={handleInputKeyDown}
          onFocus={() => suggestions.length > 0 && setDropdownOpen(true)}
        />

        {dropdownOpen && (
          <ul className={styles.dropdown} role="listbox">
            {suggestions.map((suggestion, index) => (
              <li key={suggestion.id}>
                <button
                  type="button"
                  className={`${styles.row} ${index === activeIndex ? styles.rowActive : ''}`}
                  onMouseEnter={() => setActiveIndex(index)}
                  onClick={() => selectMedication(suggestion)}
                  role="option"
                  aria-selected={index === activeIndex}
                >
                  {isCapsuleFormIcon(suggestion.form) ? (
                    <IconCapsule className={styles.rowIcon} />
                  ) : (
                    <IconDrop className={styles.rowIcon} />
                  )}
                  <span className={styles.rowText}>
                    <span className={styles.rowInn}>{suggestion.inn}</span>
                    <span className={styles.rowSecondary}>
                      {formLabelFr(suggestion.form)} · {suggestion.strength}
                      {suggestion.matched_brand && (
                        <>
                          {' · '}
                          <span className={styles.rowBrand}>({suggestion.matched_brand})</span>
                        </>
                      )}
                    </span>
                  </span>
                  {index === activeIndex && <IconCheck className={styles.rowCheck} />}
                </button>
              </li>
            ))}
          </ul>
        )}
      </div>
    );
  }

  return (
    <div className={styles.container} ref={containerRef}>
      <div className={styles.split}>
        <input
          className={styles.medicationField}
          value={medication.inn}
          onChange={(event) => handleMedicationFieldChange(event.target.value)}
          aria-label="Médicament"
        />
        <button
          ref={doseTriggerRef}
          type="button"
          className={styles.doseTrigger}
          onClick={() => setDoseOpen((open) => !open)}
          onKeyDown={handleDoseKeyDown}
          aria-haspopup="listbox"
          aria-expanded={doseOpen}
        >
          <span className={dose ? styles.doseValue : styles.dosePlaceholder}>
            {dose ? dose.strength : 'Dose'}
          </span>
        </button>
      </div>

      {/* Rendered outside .split (which clips to its rounded corners via
          overflow: hidden) so the absolutely-positioned dropdown isn't
          clipped along with it. */}
      {doseOpen && (
        <ul className={styles.doseDropdown} role="listbox">
          {doseOptions.map((option, index) => (
            <li key={option.id}>
              <button
                type="button"
                className={`${styles.doseRow} ${
                  index === doseActiveIndex || dose?.id === option.id ? styles.doseRowActive : ''
                }`}
                onMouseEnter={() => setDoseActiveIndex(index)}
                onClick={() => selectDose(option)}
                role="option"
                aria-selected={dose?.id === option.id}
              >
                {option.strength}
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
