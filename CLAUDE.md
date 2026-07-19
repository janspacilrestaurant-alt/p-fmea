# P-FMEA — kontext pro Claude Code

## Co to je
Webový nástroj pro tvorbu Process FMEA dle **AIAG-VDA FMEA Handbook 1st Ed. (2019)**,
7-Step Approach. Cílový segment: SME výrobní podniky (CZ/DE/EN).

## Stack
- Backend: FastAPI (Python 3.12), SQLAlchemy 2, Alembic, Pydantic v2
- Frontend: React 18 + TypeScript + Vite, TanStack Query, React Router, Zustand
- DB: PostgreSQL 16 + pgvector
- AI: Claude API (anthropic SDK) — vision, generátor draftů, RAG nad knihovnami
- Deploy: Docker Compose (SaaS i on-prem)

## Doménová pravidla — NEPORUŠOVAT
1. **AP se nikdy nepočítá LLM.** `app/core/ap.py::ap_lookup(S, O, D)` je jediný zdroj
   pravdy. Deterministická lookup tabulka. Žádný AI odhad, žádný RPN součin.
2. **Severity je fixní** — odráží dopad na zákazníka. Nesnižuje se, aby vyšlo lepší AP.
3. **High AP bez akce vyžaduje písemné zdůvodnění** (`no_action_justification`) —
   auditní požadavek IATF 16949.
4. **Human-in-the-loop povinně.** AI navrhuje FM/FE/FC a ratingy; inženýr schvaluje.
   Nikdy neuklidat AI výstup rovnou jako schválený.
5. **ProcessStep je sdílená entita** PFD ⇄ PFMEA ⇄ Control Plan. Číslo a název operace
   má jediný zdroj pravdy — změna se propíše do všech tří dokumentů.
6. **Žádné doslovné kopie AIAG-VDA textů.** Ratingové katalogy jsou vlastní parafráze
   nebo customer-supplied (`RatingCatalog` per-org).
7. **Struktura před analýzou.** Structure Analysis (Step 2) musí existovat před
   Function (3) a Failure (4).

## Konvence
- Backend: routery v `app/api/routes/`, business logika v `app/core/` a `app/services/`.
- Migrace vždy přes Alembic, nikdy `create_all` v produkci.
- Modely: UUID PK, `created_at`/`updated_at` přes mixiny.
- Frontend: `src/features/<doména>/`, sdílené v `src/components/`, API v `src/lib/api.ts`.
- Komentáře a UI texty česky, kód a identifikátory anglicky.
- Testy: `backend/tests/`, `pytest`. AP engine musí mít 100% pokrytí matice.

## Milníky
M1 skeleton (hotovo) → M2 core FMEA editor → M3 PFD + drawing →
M4 AI vrstva → M5 CP + export + audit trail → M6 polish + i18n + pilot.
