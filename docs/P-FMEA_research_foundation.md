# P-FMEA — Research Foundation (Dr.Indus)

Datum: 2026-07-19 | Účel: podklad pro vývoj AI nástroje na tvorbu Process FMEA

---

## 1. Závazné standardy a normy

| Standard | Rok | Role |
|---|---|---|
| **AIAG & VDA FMEA Handbook, 1st Ed.** | 2019 | Primární metodika — 7-Step Approach, Action Priority (AP). Nahrazuje AIAG 4th Ed. (2008) i VDA 4. **Toto je core standard nástroje.** |
| **IATF 16949:2016** | 2016 | QMS automotive. Klauzule 8.3.5.1 (DFMEA v design outputs), 8.3.5.2 (PFMEA v process design outputs). FMEA = "living document". |
| **AIAG APQP 3rd Ed.** | 2024 | PFMEA jako součást APQP fáze 3 (Process Design). |
| **AIAG Control Plan, 1st Ed. (samostatný)** | 2024 | Control Plan vyčleněn z APQP — přímá vazba PFD → PFMEA → CP. |
| **AIAG PPAP 4th Ed.** | 2006 | PFMEA je povinný element PPAP submission. |
| **VDA 2 (PPA)** | — | Německý ekvivalent PPAP. |
| **SAE J1739** | 2021 | US alternativa (Ford ji stále referencuje). |
| **IEC 60812** | 2018 | Obecná FMEA/FMECA norma (mimo automotive — strojírenství, elektro). |
| **MIL-STD-1629A** | — | FMECA pro defense/aerospace (kriticality analysis). |
| **ISO 9001:2015** | — | Risk-based thinking — FMEA jako nástroj naplnění. |

⚠️ Handbook AIAG-VDA je placený copyrightovaný dokument (AIAG store ~$100+, VDA QMC). Do nástroje nelze kopírovat texty tabulek 1:1 — nutno parafrázovat/licencovat, nebo nechat zákazníka nahrát vlastní hodnoticí katalogy.

---

## 2. Metodika: 7-Step Approach (AIAG-VDA 2019)

1. **Planning & Preparation** — scope, 5T (InTent, Timing, Team, Tasks, Tools), hlavička dokumentu, baseline/family FMEA
2. **Structure Analysis** — Process Item → Process Step → Process Work Element (4M: Machine, Man, Material, EnvironMent). Vizualizace: structure tree nebo process flow diagram
3. **Function Analysis** — funkce každé úrovně struktury, product/process characteristics
4. **Failure Analysis** — Failure Effects (FE) ↔ Failure Mode (FM) ↔ Failure Cause (FC) — failure chain napříč úrovněmi
5. **Risk Analysis** — Severity (S), Occurrence (O), Detection (D) 1–10; Prevention & Detection Controls; **Action Priority (AP): H/M/L z lookup tabulky** (ne RPN součin)
6. **Optimization** — akce, odpovědnost, termín, status (Open→Completed), re-rating
7. **Results Documentation** — report, komunikace interně i zákazníkovi

Klíčové změny vs. staré metodiky:

- RPN → **AP (High/Medium/Low)** — deterministická lookup tabulka S×O×D
- High AP bez akce vyžaduje písemné zdůvodnění (auditní požadavek)
- Severity je fixní (dopad na zákazníka) — nesmí se snižovat kvůli AP
- Struktura povinná před analýzou funkcí/selhání (VDA dědictví)

---

## 3. Hodnoticí tabulky (pro implementaci)

- **Severity (S) 1–10**: dopad na koncového uživatele + na vlastní/následný závod + regulatorní. S=9–10 safety/regulatory.
- **Occurrence (O) 1–10**: vázáno na účinnost prevention controls; v praxi korelace s Cpk (Cpk ≥ 1,67 → O=1; Cpk < 0,33 → O=10).
- **Detection (D) 1–10**: účinnost detekčních metod — poka-yoke/automatická in-line detekce D=2–3, manuální vizuální kontrola D=6–8, žádná detekce D=10.
- **AP tabulka**: plná matice AIAG-VDA 2019 (H/M/L) — implementovat jako fixní backend logiku, ne AI odhad.

---

## 4. Povinná dokumentová vazba (auditní požadavek IATF)

**Process Flow Diagram (PFD) ⇄ PFMEA ⇄ Control Plan** — stejná čísla a názvy operací ve všech třech. Special Characteristics (SC/CC) z DFMEA/PFMEA musí být označeny v CP. Controls v PFMEA = kontroly v CP. Tohle je největší zdroj auditních neshod → **hlavní selling point nástroje: automatická synchronizace PFD → PFMEA → CP**.

---

## 5. Konkurence (pro positioning)

| Nástroj | Model | Poznámka |
|---|---|---|
| APIS IQ-FMEA/IQ-RM | desktop, drahý | De-facto standard OEM/Tier1 v Evropě. Složitý, strmá křivka učení |
| PLATO e1ns / SCIO | SaaS, enterprise | Modularita, integrace DRBFM/8D/CAPA |
| Relyence FMEA | SaaS | Moderní UI, AIAG-VDA, AI features |
| ReliaSoft XFMEA (HBM Prenscia) | desktop/server | Reliability suite |
| Sphera FMEA-Pro, Knowllence TDC, Omnex AquaPro | různé | Střední segment |
| AI-native: fmeatool.ai, qualityengineer.ai, Qhubio | SaaS | Nová vlna — generují PFMEA z dokumentace, export Excel |

Mezera na trhu: ~60 % firem stále dělá FMEA v Excelu. Cenově dostupný AI-first nástroj s CZ/DE/EN lokalizací, knihovnami a plnou vazbou PFD→PFMEA→CP pro SME výrobní podniky = prostor pro Dr.Indus.

---

## 6. AI přístup (ověřeno výzkumem i trhem)

- LLM + **RAG nad knihovnami** (foundation/family FMEA, katalogy failure modes, lessons learned) — standardní architektura publikovaná v literatuře (Cambridge Design Science 2025, Springer 2026)
- Multi-modální vstup: 2D výkres (PDF/DXF) → extrakce charakteristik a tolerancí; process flow → generování struktury
- **Human-in-the-loop povinně** — AI navrhuje FM/FE/FC a ratingy, inženýr schvaluje; AP počítá deterministický backend, nikdy LLM
- Agentic workflow s quality gates (konzistence failure chains, úplnost 4M)

---

## 7. Funkční scope nástroje (draft)

1. **Projekt/díl management** — hlavička (zákazník, díl, číslo, revize), family/baseline FMEA
2. **Process Flowchart editor** — grafický, číslované operace, sync do PFMEA
3. **2D výkres viewer** — PDF/DXF, ballooning charakteristik, link na process steps
4. **Structure/Function/Failure analysis** — tree view + spreadsheet view (Form B-like)
5. **Knihovny**: failure modes dle technologie (obrábění, svařování, lisování, montáž, lakování…), controls, akce — učí se z dokončených FMEA
6. **AI generátor** — z PFD + výkresu + popisu navrhne kompletní draft PFMEA
7. **AP engine** — fixní AIAG-VDA logika, barevné kódování H/M/L
8. **Control Plan generátor** — automaticky z PFMEA
9. **Akce tracking** — odpovědnost, termíny, status, notifikace
10. **Export** — Excel (AIAG-VDA Form), PDF, MSR XML (dlouhodobě: FMEA MSR exchange format)
11. **Revize/audit trail** — living document, verze, kdo-co-kdy
12. **Multi-jazyk** — CZ/EN/DE minimum

---

## 8. Otevřené body před vývojem

- [ ] Licencování ratingových tabulek AIAG-VDA (parafráze vs. customer-supplied katalogy)
- [ ] Tech stack rozhodnutí (návrh: web app — React + FastAPI/Node + Postgres; Claude API pro AI vrstvu)
- [ ] Datový model: graf (structure tree + failure net) vs. relační — doporučení: relační DB s grafovými vazbami
- [ ] DXF parsing knihovna (ezdxf) vs. jen PDF rendering
- [ ] Cenový model: SaaS per-seat vs. on-premise licence (výrobní podniky často vyžadují on-prem kvůli IP)
- [ ] Pilotní zákazník pro validaci
