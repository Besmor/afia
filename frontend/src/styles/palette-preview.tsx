// TEMPORARY token-preview page (FT-5). Renders every design token from
// src/styles/tokens.css as a swatch/type-sample grid so we can visually
// verify the Figma-derived tokens resolve correctly. Preserved as a
// dev-time tool after FT-6 replaced it with the real Landing screen in
// src/App.tsx; not routed to anywhere.

type Swatch = { name: string; varName: string };

const grayscale: Swatch[] = [
  { name: 'Gray_02 / 10', varName: '--color-gray-02-10' },
  { name: 'Gray_02 / 20', varName: '--color-gray-02-20' },
  { name: 'Gray_02 / 30', varName: '--color-gray-02-30' },
  { name: 'Gray_02 / 40', varName: '--color-gray-02-40' },
  { name: 'Gray_02 / 50', varName: '--color-gray-02-50' },
  { name: 'Gray_02 / 60', varName: '--color-gray-02-60' },
  { name: 'Gray_02 / 70', varName: '--color-gray-02-70' },
  { name: 'Gray_02 / 80', varName: '--color-gray-02-80' },
  { name: 'Gray_02 / 90', varName: '--color-gray-02-90' },
  { name: 'Gray_02 / 100', varName: '--color-gray-02-100' },
  { name: 'Black', varName: '--color-black' },
];

const brandGreens: Swatch[] = [
  { name: 'Background 01', varName: '--color-background-01' },
  { name: 'Main color', varName: '--color-main' },
  { name: 'Main red', varName: '--color-main-red' },
  { name: 'Main red 2', varName: '--color-main-red-2' },
  { name: 'Primary 01', varName: '--color-primary-01' },
  { name: 'Primary 02', varName: '--color-primary-02' },
  { name: 'Secondary 01', varName: '--color-secondary-01' },
  { name: 'Secondary 02', varName: '--color-secondary-02' },
  { name: 'Secondary 03', varName: '--color-secondary-03' },
  { name: 'Secondary 04', varName: '--color-secondary-04' },
  { name: 'Secondary 05', varName: '--color-secondary-05' },
  { name: 'Secondary 06', varName: '--color-secondary-06' },
];

const semantic: Swatch[] = [
  { name: 'Danger', varName: '--color-danger' },
  { name: 'Warning', varName: '--color-warning' },
  { name: 'Info', varName: '--color-info' },
  { name: 'Success', varName: '--color-success' },
];

const accent: Swatch[] = [
  { name: 'Accent color', varName: '--color-accent' },
  { name: 'Accent color 01', varName: '--color-accent-01' },
  { name: 'Accent color 02', varName: '--color-accent-02' },
  { name: 'Accent color 022', varName: '--color-accent-022' },
  { name: 'Accent color 03', varName: '--color-accent-03' },
  { name: 'Accent color 04', varName: '--color-accent-04' },
  { name: 'Accent color 05', varName: '--color-accent-05' },
];

const typeScale: { name: string; sizeVar: string; weightVar: string }[] = [
  { name: 'H1', sizeVar: '--font-size-h1', weightVar: '--font-weight-regular' },
  { name: 'H2', sizeVar: '--font-size-h2', weightVar: '--font-weight-regular' },
  { name: 'H3', sizeVar: '--font-size-h3', weightVar: '--font-weight-regular' },
  { name: 'H4', sizeVar: '--font-size-h4', weightVar: '--font-weight-regular' },
  { name: 'H5', sizeVar: '--font-size-h5', weightVar: '--font-weight-regular' },
  { name: 'Title1', sizeVar: '--font-size-title1', weightVar: '--font-weight-regular' },
  { name: 'Title2', sizeVar: '--font-size-title2', weightVar: '--font-weight-regular' },
  { name: 'Body', sizeVar: '--font-size-body', weightVar: '--font-weight-medium' },
  { name: 'Caption', sizeVar: '--font-size-caption', weightVar: '--font-weight-semibold' },
];

function ColorGroup({ title, swatches }: { title: string; swatches: Swatch[] }) {
  return (
    <section style={{ marginBottom: '2rem' }}>
      <h2 style={{ fontFamily: 'Inter, sans-serif', fontSize: '1rem', marginBottom: '0.75rem' }}>
        {title}
      </h2>
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.75rem' }}>
        {swatches.map((s) => (
          <div key={s.varName} style={{ width: '120px', fontFamily: 'Inter, sans-serif' }}>
            <div
              style={{
                background: `var(${s.varName})`,
                height: '64px',
                borderRadius: 'var(--radius-md)',
                border: '1px solid var(--color-gray-02-30)',
              }}
            />
            <p style={{ fontSize: '0.75rem', marginTop: '0.375rem' }}>{s.name}</p>
            <code style={{ fontSize: '0.625rem', color: 'var(--color-gray-02-70)' }}>
              {s.varName}
            </code>
          </div>
        ))}
      </div>
    </section>
  );
}

export function PalettePreview() {
  return (
    <main style={{ padding: 'var(--spacing-2xl)', maxWidth: '960px', margin: '0 auto' }}>
      <h1 style={{ fontSize: 'var(--font-size-h3)', marginBottom: 'var(--spacing-lg)' }}>
        Afia — token preview (temporary, FT-5)
      </h1>

      <ColorGroup title="Grayscale" swatches={grayscale} />
      <ColorGroup title="Brand greens" swatches={brandGreens} />
      <ColorGroup title="Semantic" swatches={semantic} />
      <ColorGroup title="Accent" swatches={accent} />

      <section>
        <h2 style={{ fontFamily: 'Inter, sans-serif', fontSize: '1rem', marginBottom: 'var(--spacing-lg)' }}>
          Type scale (documented Inter/Roboto styles)
        </h2>
        {typeScale.map((t) => (
          <p
            key={t.name}
            style={{
              fontFamily: 'Inter, sans-serif',
              fontSize: `var(${t.sizeVar})`,
              fontWeight: `var(${t.weightVar})` as unknown as number,
              lineHeight: 'var(--line-height-base)',
              marginBottom: 'var(--spacing-sm)',
            }}
          >
            {t.name} — {t.sizeVar}
          </p>
        ))}
      </section>
    </main>
  );
}
