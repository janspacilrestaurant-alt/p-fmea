# P-FMEA — Dr.Indus

Nástroj pro tvorbu Process FMEA dle AIAG-VDA FMEA Handbook 1st Ed. (2019).

**Stav: M1 — Skeleton** (repo, Docker, DB schéma, auth, CRUD projekty, AP engine).

## Rychlý start

```bash
cp .env.example .env      # uprav JWT_SECRET a bootstrap admin heslo
docker compose up --build
```

- API + Swagger: http://localhost:8000/docs
- Frontend: http://localhost:5173
- Výchozí admin: `admin@drindus.local` / heslo z `.env`

Migrace a seed se spouští automaticky při startu backendu.

## Struktura

```
backend/app/
  core/ap.py          # ← AP engine (deterministický, nikdy LLM)
  core/security.py    # JWT + role admin/engineer/viewer
  models/             # Organization, User, Project, Part, ProcessStep,
                      # StructureNode, FailureMode/Effect/Cause,
                      # OptimizationAction, RatingCatalog
  api/routes/         # auth, projects, risk
  seed.py             # bootstrap org/admin + parafrázované katalogy S/O/D
frontend/src/         # React + Vite skeleton (login, seznam projektů)
docs/                 # research foundation + project spec
```

## Testy

```bash
cd backend && pytest
```

## ⚠️ Před produkčním nasazením

- **Ověřit AP matici** v `backend/app/core/ap.py` proti licencované kopii
  AIAG-VDA FMEA Handbook 1st Ed. (2019), Table AP. Matice v repu je implementována
  z veřejně popsané struktury a musí být zkontrolována kvalifikovaným inženýrem.
- Texty ratingových katalogů jsou vlastní parafráze — nikoli citace Handbooku.
- Změnit `JWT_SECRET` a bootstrap admin heslo.
