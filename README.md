<div align="center">
	<h1>AGSA – Automated Government Service Agent</h1>
	<p><strong>Your agentic AI interface for discovering schemes, verifying documents, and guiding citizens through government service workflows.</strong></p>
	<p>
		<em>Stack:</em> Vite · React 18 · TypeScript · Radix UI + shadcn/ui · Tailwind CSS · React Router · TanStack Query · Framer Motion
	</p>
</div>

---

## 1. Quick Start

```bash
git clone <repo-url>
cd agsa-gov-agent-ai
npm install
npm run dev
```
Dev server (Vite) will print a local URL (default: http://localhost:5173).

## 2. Core Concept
AGSA simulates an AI assistant that:
- Onboards a user (Auth → KYC)
- Optionally links government service providers (DigiLocker, Aadhaar, UMANG) – currently mocked
- Enables a conversational assistant to surface eligible schemes, verify mock documents, and prepare a summarized application flow

All AI / backend integrations are placeholders, making it easy to progressively replace with real APIs (LLM gateway, identity, verification, eKYC, etc.).

## 3. Application Flow (Routes)
Route | File | Purpose
------|------|--------
`/` | `src/pages/Index.tsx` | Landing page (marketing sections + CTA)
`/auth` | `src/pages/Auth.tsx` | Login/Register with phone OTP or email (simulated)
`/kyc` | `src/pages/KYC.tsx` | Two-step profile + optional integrations (mock success/fail)
`/chat` | `src/pages/Chat.tsx` | Conversational assistant with contextual scripted flows
`*` | `src/pages/NotFound.tsx` | Fallback (404)

Router is configured in `src/App.tsx` via `react-router-dom`.

## 4. Key Files & Responsibilities
Category | File | Notes
---------|------|------
Entry | `index.html` | Base HTML, fonts, metadata, social OG tags
Bootstrap | `src/main.tsx` | Creates React root and renders `<App />`
App Shell | `src/App.tsx` | Providers: QueryClient, Tooltip, Toasters, Routes
UI System | `src/components/ui/*` | shadcn/ui + Radix primitives (accessible building blocks)
Global Layout Pieces | `Navbar.tsx`, `Hero.tsx`, `Features.tsx`, `HowItWorks.tsx`, `AccessibilityImpact.tsx`, `Demo.tsx`, `CallToAction.tsx`, `Footer.tsx` | Landing composition
State / Hooks | `src/hooks/use-toast.ts` | Toast dispatch wrapper
Utilities | `src/lib/utils.ts` | `cn` class name merge helper
Brand Assets | `src/assets/*` | Logo & hero background
Styling | `src/index.css`, `tailwind.config.ts`, `postcss.config.js` | Tailwind setup + global tokens
Config | `tsconfig*.json`, `vite.config.ts` | Build and TS path aliases (`@/`)

## 5. Chat Assistant Logic
The assistant in `Chat.tsx` is a state machine–like heuristic using keyword matching:
- Detects “scheme”, “benefit”, “subsidy” → eligibility flow
- Then “document”, “verify”, “yes” → document verification status messages
- Then “form”, “application”, “prepare” → application summary
Messages are stored in local component state; timestamps + simple formatted rendering.

To integrate a real LLM:
1. Extract `simulateAssistantResponse` into a service module.
2. Replace keyword logic with API call (e.g., `/api/chat` streaming).
3. Normalize responses into the `Message` shape.
4. Add loading & error states (TanStack Query or custom controller).

## 6. Mock Integrations (KYC)
File: `src/pages/KYC.tsx`
- Simulates asynchronous connections (`setTimeout`) to external services.
- Random 70% success per integration (DigiLocker, Aadhaar, UMANG).
- Replace with real REST/OAuth flows by extracting `handleIntegration`.

## 7. Styling & Design System
- Tailwind + shadcn-ui: consistent design tokens.
- `cn` helper merges conditional class sets.
- Motion embellishments via Framer Motion (entrances, micro interactions).

## 8. State & Data Layer
- Currently minimal; only local component state + React Query instantiation (no queries yet). Ready for:
	- Caching user profile / eligibility results
	- Polling application status
	- Pre-fetching scheme catalogs

## 9. Recommended Next Enhancements
Priority | Enhancement | Summary
---------|-------------|--------
P1 | Real Auth Adapter | Plug in OAuth / phone OTP provider (e.g., Firebase, custom backend)
P1 | Central API Client | Axios/fetch wrapper + error normalization
P1 | LLM Integration | Replace scripted chat with streaming model output (OpenAI / Azure / local)
P2 | Persistent State | Store chat + KYC progress in localStorage or backend
P2 | Accessibility Audit | Add focus outlines, ARIA live regions for chat updates
P2 | Testing Setup | Vitest + React Testing Library for critical flows
P3 | i18n | Add translation framework (e.g., i18next) for multilingual rollout
P3 | Analytics | Event tracking for funnel (landing → auth → kyc → chat)

## 10. How to Contribute / Extend
Use this lightweight branching model:
```bash
git checkout -b feat/<short-name>
# implement
git commit -m "feat(chat): add streaming support"
git push origin feat/<short-name>
```
Open a PR; include before/after screenshots for UI changes.

### Suggested Folder Additions (when scaling)
```
src/
	api/          # API clients, request/response schemas
	services/     # Domain logic (eligibility, documents, chat orchestration)
	store/        # Zustand / Redux / Jotai (if needed)
	types/        # Shared TypeScript types
	tests/        # Unit & integration tests
```

## 11. Environment & Configuration
Currently no `.env` file required. When adding backends define e.g.:
```
VITE_API_BASE_URL=https://api.example.com
VITE_OPENAI_API_KEY=... (never commit)
```
Access via `import.meta.env.VITE_API_BASE_URL`.

## 12. Scripts
Script | Purpose
-------|--------
`npm run dev` | Start Vite dev server
`npm run build` | Production build (outputs to `dist/`)
`npm run build:dev` | Development-mode build (useful for profiling)
`npm run preview` | Preview built assets locally
`npm run lint` | Run ESLint over the repo

## 13. Tech Decisions Rationale
- Vite: fast HMR & TS integration
- shadcn/ui + Radix: accessible primitives without heavy design overhead
- React Query prepared: future async data orchestration
- Framer Motion: subtle motion for perceived polish
- Keyword-based assistant: rapid prototyping before committing to LLM costs

## 14. Testing (Proposed Setup)
Install (future): `vitest`, `@testing-library/react`, `@testing-library/user-event`, `jsdom`.
Example test target candidates:
- Chat flow triggers (eligibility → documents → summary)
- KYC integration state transitions
- Auth mode switch (login/register + phone/email)

## 15. Accessibility Checklist (Current Gaps)
- Add `aria-live="polite"` region for incoming assistant messages
- Ensure focus trapping in dialogs (when added later)
- Provide skip-to-content link on landing
- Confirm color contrast (run tooling)

## 16. Deployment
Any static host works (Netlify, Vercel, Cloudflare Pages, GitHub Pages):
```bash
npm run build
# deploy dist/ directory
```
When adding server features, introduce a `/api` proxy in `vite.config.ts`.

## 17. Security Notes / Future
- Sanitize user input before sending to LLM / backend
- Rate limit scheme lookups
- Use token-based session (JWT / HttpOnly cookie) for persisted auth
- Implement audit logging for sensitive eligibility queries

## 18. File Change Map (Where to Add What)
Need | Modify File(s) | Notes
-----|----------------|------
Add real chat backend | `src/pages/Chat.tsx`, new `src/services/chat.ts` | Extract simulation → service
Persist user profile | `src/pages/Auth.tsx`, `src/pages/KYC.tsx`, add `src/api/user.ts` | Replace timeouts with API
Add scheme catalog | New: `src/api/schemes.ts`, `src/services/eligibility.ts` | Query + filter + rank
Add global store | New: `src/store/*` | Manage auth/session outside pages
Add dark mode toggle | `Navbar.tsx`, use `next-themes` or CSS class toggle | Tailwind `dark:` support

## 19. License
Add a LICENSE file if distributing (MIT recommended). Currently unspecified.

## 20. Maintainers
List maintainers & contact here (TBD).

---
Feel free to iterate quickly—this README is structured to evolve as real integrations replace the mocks.

> Tip: Start by extracting side-effect logic from pages into service modules; this keeps UI components lean and testable.

