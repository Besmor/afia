/** Number/currency formatting helpers shared by the search results and pharmacy detail screens. */

/**
 * Formats a Guinean Franc amount with a thin space every 3 digits, e.g.
 * `15000` -> "15 000 GNF" (matches the price styling on the Figma results
 * card, `frontend/design-refs/Vue Liste-Résultat des recherches.svg`).
 * Uses U+202F (narrow no-break space), the typographic thin space French
 * number grouping expects, rather than a plain space.
 */
export function formatPriceGnf(priceGnf: number): string {
  const grouped = Math.round(priceGnf)
    .toString()
    .replace(/\B(?=(\d{3})+(?!\d))/g, ' ');

  return `${grouped} GNF`;
}
