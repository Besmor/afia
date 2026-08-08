import type { ButtonHTMLAttributes, ReactNode } from 'react';
import styles from './PrimaryButton.module.css';

interface PrimaryButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  children: ReactNode;
}

/** Full-width pill CTA matching the "Rechercher" button on Accueil (see docs/figma-inspection.md, Screen 1). */
export function PrimaryButton({ children, ...buttonProps }: PrimaryButtonProps) {
  return (
    <button type="button" className={styles.button} {...buttonProps}>
      {children}
    </button>
  );
}
