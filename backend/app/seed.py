"""Seed: bootstrap organizace, admin uživatel a default (parafrázované) katalogy S/O/D.

Texty kritérií jsou VLASTNÍ PARAFRÁZE, nikoli citace AIAG-VDA Handbooku.
Zákazník si může nahrát/editovat vlastní katalog per-org.
"""
from sqlalchemy import select

from app.config import settings
from app.core.security import hash_password
from app.db import SessionLocal
from app.models import (CatalogKind, Organization, RatingCatalog,
                        RatingCatalogEntry, Role, User)

SEVERITY = [
    (10, "Bezpečnost / legislativa", "Ztráta bezpečné funkce vozidla bez varování nebo nesplnění zákonného požadavku."),
    (9, "Bezpečnost s varováním", "Ztráta bezpečné funkce s varováním; hrozí regulatorní neshoda."),
    (8, "Ztráta primární funkce", "Výrobek nepoužitelný; ve vlastním závodě nutná likvidace nebo 100% třídění."),
    (7, "Omezená primární funkce", "Výrazné snížení funkce; přepracování mimo linku."),
    (6, "Ztráta sekundární funkce", "Komfortní funkce nefunguje; přepracování na lince mimo takt."),
    (5, "Omezená sekundární funkce", "Snížený komfort; část dávky nutno přepracovat."),
    (4, "Výrazně vnímaná vada vzhledu", "Vzhled/hluk vadí většině zákazníků; přepracování na stanovišti."),
    (3, "Mírně vnímaná vada", "Vzhled/hluk vadí části zákazníků; drobná úprava."),
    (2, "Nepatrně vnímaná vada", "Vadu zaznamenají jen nároční zákazníci; zanedbatelný dopad na proces."),
    (1, "Bez dopadu", "Žádný rozeznatelný dopad na zákazníka ani na proces."),
]

OCCURRENCE = [
    (10, "Extrémně vysoká", "Bez prevence; závada se vyskytuje prakticky trvale."),
    (9, "Velmi vysoká", "Prevence minimální; opakovaný výskyt v sériové výrobě."),
    (8, "Vysoká", "Prevence slabá, proces nezpůsobilý (orientačně Cpk < 0,55)."),
    (7, "Mírně vysoká", "Prevence částečně účinná; časté odchylky."),
    (6, "Střední", "Prevence účinná u části příčin (orientačně Cpk ≈ 0,78)."),
    (5, "Mírně střední", "Proces obdobný předchozím s občasnými neshodami."),
    (4, "Nízká", "Prevence účinná (orientačně Cpk ≈ 1,00)."),
    (3, "Velmi nízká", "Prevence velmi účinná; ojedinělé neshody (Cpk ≈ 1,33)."),
    (2, "Extrémně nízká", "Prevence brání většině neshod (Cpk ≈ 1,67)."),
    (1, "Vyloučená", "Prevence konstrukčně vylučuje vznik příčiny (Cpk ≥ 1,67, poka-yoke procesu)."),
]

DETECTION = [
    (10, "Žádná detekce", "Vada není a nemůže být odhalena."),
    (9, "Velmi nepravděpodobná", "Náhodná nebo nepravidelná kontrola bez definované metody."),
    (8, "Nepravděpodobná", "Vizuální kontrola operátorem, nedefinovaný postup."),
    (7, "Velmi nízká", "Vizuální kontrola dle instrukce, bez pomůcky."),
    (6, "Nízká", "Manuální měření / kontrola s pomůckou, namátkově."),
    (5, "Střední", "Manuální měření 100 % kusů s definovaným postupem."),
    (4, "Mírně vysoká", "Strojní měření off-line s vyhodnocením."),
    (3, "Vysoká", "Automatická in-line detekce s hlášením odchylky."),
    (2, "Velmi vysoká", "Automatická detekce se zastavením procesu a blokací kusu."),
    (1, "Jistá", "Poka-yoke — vznik nebo průchod vady je fyzicky vyloučen."),
]

CATALOGS = [
    (CatalogKind.severity, "Severity (default CZ)", SEVERITY),
    (CatalogKind.occurrence, "Occurrence (default CZ)", OCCURRENCE),
    (CatalogKind.detection, "Detection (default CZ)", DETECTION),
]


def run() -> None:
    db = SessionLocal()
    try:
        org = db.scalar(select(Organization).where(Organization.slug == "default"))
        if not org:
            org = Organization(name="Dr.Indus (default)", slug="default")
            db.add(org)
            db.flush()

        if not db.scalar(select(User).where(User.email == settings.bootstrap_admin_email)):
            db.add(User(organization_id=org.id, email=settings.bootstrap_admin_email,
                        full_name="Bootstrap Admin", role=Role.admin,
                        hashed_password=hash_password(settings.bootstrap_admin_password)))

        for kind, name, rows in CATALOGS:
            if db.scalar(select(RatingCatalog).where(RatingCatalog.kind == kind,
                                                     RatingCatalog.organization_id.is_(None))):
                continue
            catalog = RatingCatalog(organization_id=None, kind=kind, name=name,
                                    locale="cs", is_default=True)
            db.add(catalog)
            db.flush()
            for value, label, criteria in rows:
                db.add(RatingCatalogEntry(catalog_id=catalog.id, value=value,
                                          label=label, criteria=criteria))
        db.commit()
        print("seed: hotovo")
    finally:
        db.close()


if __name__ == "__main__":
    run()
