# My investment calculator

Funds vs banks projection calculator (Svelte + Vite).

## Setup

```bash
npm install
```

## Dev

```bash
npm run dev
```

## Refresh market data (no API keys)

```bash
npm run update:data
# or separately:
npm run update:funds     # Nordnet fund list SSR pages
npm run update:banks     # Forbrukerrådet bankinnskudd JSON
npm run update:history   # Nordnet price history for default funds (needs Chrome + selenium)
```

History files land in `public/history/{orderBookId}.json`. For every fund:

```bash
npm run update:history:all
```

Optional favicon pass for banks:

```bash
python scripts/fix_icon_urls.py
```

## Deploy

```bash
npm run build
npm run deploy
```

## Notes

- Icons: https://icon-sets.iconify.design/
- The chart is a **historical backtest**: pick a start date, apply monthly contributions on real Nordnet return paths (ups and downs).
- Fund values subtract fees and an illustrative ASK tax (37.84% of profit).
- Banks use today’s `rentesats1` compounded over the same dates (dashed lines).
