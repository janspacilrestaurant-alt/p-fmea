# P-FMEA — Project Specification v1.0 (Dr.Indus)

Schválená rozhodnutí: parafrázované + customer katalogy | React+FastAPI+Postgres | relační model | PDF (DXF ve v2) | hybrid SaaS/on-prem

---

## 1. Architektura

```
┌─────────────────────────────────────────────────┐
│  Frontend: React + TypeScript + Vite            │
│  - Tailwind CSS, shadcn/ui                      │
│  - React Flow (process flowchart editor)        │
│  - react-pdf (výkres viewer + ballooning)       │
│  - TanStack Table (FMEA spreadsheet view)       │
│  - Zustand (state), TanStack Query (API)        │
├─────────────────────────────────────────────────┤
│  Backend: FastAPI (Python 3.12)                 │
│  - SQLAlchemy 2 + Alembic (migrace)             │
│  - Pydantic v2 (validace)                       │
│  - openpyxl (Excel export AIAG-VDA Form)        │
│  - WeasyPrint (PDF reporty)                     │
│  - Auth: JWT + role (admin/engineer/viewer)     │
├─────────────────────────────────────────────────┤
│  AI vrstva: Claude API (anthropic SDK)          │
│  - Vision: extrakce charakteristik z PDF výkresu│
│  - Generátor: draft PFMEA z PFD + kontextu      │
│  - RAG: pgvector nad knihovnami failure modes   │
│  - Volitelný customer API key (on-prem)         │
├─────────────────────────────────────────────────┤
│  DB: PostgreSQL 16 + pgvector                   │
│  Deploy: Docker Compose (SaaS i on-prem)        │
└─────────────────────────────────────────────────┘
```

## 2. Datový model (core entity)

```
Organization ─┬─ User (role)
              └─ Project ─┬─ Part (číslo, revize, zákazník)
                          ├─ Drawing (PDF, balloons → Characteristic)
                          ├─ ProcessFlow ─ ProcessStep (číslo op., název)
                          ├─ PFMEA (revize, status, baseline_id)
                          └─ ControlPlan (generovaný z PFMEA)

PFMEA struktura (AIAG-VDA 7 kroků):
StructureNode (process_item | process_step | work_element[4M])
  └─ Function ─ Characteristic (product/process, special_char flag)
       └─ FailureMode ─┬─ FailureEffect (úroveň výš, severity)
                       └─ FailureCause (úroveň níž, occurrence)
                            ├─ PreventionControl
                            ├─ DetectionControl (detection)
                            └─ Action (typ, odpovědnost, termín, status, re-rating S/O/D)

AP = deterministická funkce ap_lookup(S, O, D) → H/M/L  [backend, nikdy LLM]

Knihovny:
RatingCatalog (S/O/D tabulky — default parafrázované, editovatelné per-org)
LibraryItem (failure_mode | cause | control | action; technologie-tag; embedding)
```

Vazba PFD ⇄ PFMEA ⇄ CP: ProcessStep je sdílená entita — číslo a název operace jediný zdroj pravdy, změna se propíše všude.

## 3. MVP scope (v1)

| # | Modul | Obsah |
|---|---|---|
| 1 | Auth + org + projekty | JWT, role, multi-tenant |
| 2 | Process Flow editor | React Flow, číslované operace, symboly (operace/kontrola/transport/sklad) |
| 3 | Drawing viewer | PDF upload, zoom, ballooning charakteristik, link na ProcessStep |
| 4 | PFMEA editor | tree view (structure) + tabulkový view (Form B-like), 7 kroků |
| 5 | Rating + AP | editovatelné katalogy S/O/D, AP engine, barevné H/M/L |
| 6 | AI generátor | z PFD + výkresu + popisu technologie → draft failure chains, human-in-the-loop schvalování |
| 7 | Knihovny | seed: obrábění, montáž, svařování, lisování; učení z dokončených FMEA |
| 8 | Control Plan | auto-generace z PFMEA, editace |
| 9 | Akce tracking | odpovědnost, termín, status, re-rating |
| 10 | Export | Excel (AIAG-VDA Form), PDF report |
| 11 | Audit trail | revize FMEA, change log (living document) |
| 12 | i18n | CZ/EN/DE |

**v2 (po pilotu):** DXF parsing (ezdxf), FMEA-MSR, notifikace, API integrace (ERP/QMS), family/baseline FMEA workflow, dashboard KPI.

## 4. Milníky

1. **M1 — Skeleton** (repo, Docker, DB schéma, auth, CRUD projekty)
2. **M2 — Core FMEA** (structure/function/failure editor, rating, AP engine)
3. **M3 — PFD + Drawing** (flowchart editor, PDF ballooning, sync na PFMEA)
4. **M4 — AI vrstva** (vision extrakce, generátor, RAG knihovny)
5. **M5 — CP + Export + audit trail**
6. **M6 — Polish + i18n + pilot deployment**

## 5. Repo struktura (návrh)

```
p-fmea/
├─ CLAUDE.md              # kontext pro Claude Code
├─ docker-compose.yml
├─ backend/
│  ├─ app/ (api/, models/, services/, ai/, exports/)
│  ├─ alembic/
│  └─ tests/
├─ frontend/
│  └─ src/ (features/, components/, lib/)
└─ docs/ (research, spec, katalogy)
```

## 6. První kroky v Claude Code

1. Založit repo `p-fmea`, zkopírovat tento spec + research do `docs/`
2. Vytvořit `CLAUDE.md` (stack, konvence, doménová pravidla — zejm. AP nikdy přes LLM)
3. M1: Docker Compose (Postgres+pgvector, FastAPI, Vite), Alembic init, DB schéma dle §2, auth
4. Seed parafrázovaných ratingových katalogů (S/O/D + AP matice)
