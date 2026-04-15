# WearImpact Frontend

## Setup

1. Install dependencies:

```bash
npm install
```

2. Create local environment file:

```bash
cp .env.example .env.local
```

3. Fill `VITE_MAPBOX_ACCESS_TOKEN` in `.env.local`.

4. Start development server:

```bash
npm run dev
```

## Environment Variables

- `VITE_API_BASE_URL`: Backend API base URL.
- `VITE_MAPBOX_ACCESS_TOKEN`: Mapbox public access token used by the Eco Shop map view.
- `VITE_MAPBOX_STYLE_URL`: Optional custom map style URL, defaults to `mapbox://styles/mapbox/streets-v12`.
