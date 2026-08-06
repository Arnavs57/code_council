# Code Council AI — Frontend

React + TypeScript + Vite + Tailwind CSS v4 + shadcn/ui.

The **Engineering Mission Control Center** for the AI Engineering Governance
Platform. This phase ships the UI foundation only: shell, routing, design
system, reusable primitives, placeholder pages and the Mission Control
dashboard skeleton. No business features, live streams or charts yet.

---

## Quick start

```bash
cd frontend
npm install
npm run dev          # http://localhost:5173
```

## Scripts

| Command | Purpose |
|---------|---------|
| `npm run dev` | Dev server with HMR |
| `npm run build` | Type-check (`tsc -b`) + production build |
| `npm run preview` | Serve the production build |
| `npm run lint` | ESLint |
| `npm run typecheck` | TypeScript check only |

## Architecture

| Folder | Responsibility |
|--------|----------------|
| `src/components/ui/` | Design-system primitives (shadcn-style, themeable) |
| `src/components/layout/` | App shell: navbar, sidebar, activity rail, grids |
| `src/components/dashboard/` | Mission Control sections (placeholders today) |
| `src/pages/` | Route-level pages (thin composition) |
| `src/contexts/` | Theme + feature state providers (placeholders) |
| `src/services/` | REST client, WS client, notifications, event stream (architecture only) |
| `src/types/` | Domain interfaces mirroring the backend schemas |
| `src/constants/` | Labels, routes, agent roles, status metadata |
| `src/utils/` + `src/lib/` | Pure helpers (`cn`, formatting) |
| `src/styles/` | Design tokens (Tailwind v4), animations |
| `src/hooks/` | Shared hooks (media query, mounted) |
| `src/assets/` | Static brand assets |

## Design system

- **Dark-first "ops theater" theme** with a light variant.
- Tokens via CSS variables in `src/styles/index.css` (Tailwind v4 `@theme`).
- Typography: Inter (UI) + JetBrains Mono (data), via Fontsource.
- Motion: CSS-only primitives (respect `prefers-reduced-motion`); a motion
  library will be evaluated in the live phase if state-driven animation
  demands it.

## Roadmap hooks

- `services/ws/client.ts` — cursor-resume reconnect for the live stream.
- `contexts/dashboard-context.tsx` — the future event-reducer projection.
- `components/dashboard/*` — each panel documents where its live data plugs in.
