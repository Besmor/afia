/**
 * French display label and row-icon family for each `Medication.form` value
 * (`backend/app/models/pharmacy.py`, `MedicationForm`). Used by the Landing
 * page's autocomplete dropdown (Block F).
 */

const FORM_LABELS_FR: Record<string, string> = {
  tablet: 'Comprimé',
  capsule: 'Gélule',
  syrup: 'Sirop',
  injection: 'Injection',
  ointment: 'Pommade',
  drops: 'Gouttes',
  suppository: 'Suppositoire',
  sachet: 'Sachet',
};

/** Solid oral forms get the capsule row icon; everything else gets the droplet. */
const LIQUID_OR_OTHER_FORMS = new Set(['syrup', 'injection', 'ointment', 'drops']);

export function formLabelFr(form: string): string {
  return FORM_LABELS_FR[form] ?? form;
}

export function isCapsuleFormIcon(form: string): boolean {
  return !LIQUID_OR_OTHER_FORMS.has(form);
}
