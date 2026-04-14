"""Epic 4 database seed script.

Reads backend/data/companies_cleaned.csv and backend/data/brands_cleaned.csv
and inserts all rows into the companies and brands tables.

Run ONCE after CREATE TABLE. Safe to re-run: truncates tables first.

Usage:
    DATABASE_URL=postgresql://user:pass@host/db python backend/scripts/seed_epic4.py
"""

import csv
import os

import psycopg2

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
COMPANIES_CSV = os.path.join(DATA_DIR, "companies_cleaned.csv")
BRANDS_CSV = os.path.join(DATA_DIR, "brands_cleaned.csv")

DATABASE_URL = os.environ["DATABASE_URL"]


def seed(conn):
    cur = conn.cursor()

    # Wipe existing data (safe for re-runs in dev/staging)
    cur.execute("TRUNCATE brands, companies RESTART IDENTITY CASCADE;")

    # Insert companies
    company_id_map = {}  # name → id (used for brand FK resolution)

    with open(COMPANIES_CSV, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            cur.execute(
                """
                INSERT INTO companies (
                    name, overall_score, governance_score,
                    tracing_score, env_score,
                    has_supplier_code, code_covers_raw_materials,
                    has_senior_accountability, assessed_fibre_impact,
                    sustainable_fibre_pct, has_emissions_target, product_category
                ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                RETURNING id
                """,
                (
                    row["Company"],
                    int(row["ethical_fashion_brand_score"]),
                    int(row["Policies&Governance_Score(out of 6)"]),
                    int(row["Tracing&Risk_score(all stage Production )"]),
                    int(row["environmental_sustainability_score(score_out_of_21)"]),
                    row["Does the company have a Code of Conduct for suppliers?"],
                    row["Does the Code apply to multiple levels of the supply chain including the raw materials level?"],
                    row["Does the company publicly disclose that it has a designated senior officer accountable for implementation, and a board committee/process tasked with oversight of its supply chain policies that address human rights and environmental sustainability?"],
                    row["Has the company assessed the environmental impact of its top three fibres and materials used in its apparel products and implemented learnings from assessment into product design and production?"],
                    row["What percentage of the company's final product is made from sustainable fibers?"],
                    row["Has the company published an emissions reduction target and decarbonisation strategy in line with the current UN Fashion Industry Charter for Climate Action?"],
                    row["product_category"],
                ),
            )
            (company_id,) = cur.fetchone()
            company_id_map[row["Company"]] = company_id

    print(f"[seed] {len(company_id_map)} companies inserted.")

    # Insert brands
    brands_inserted = 0
    unresolved = []

    with open(BRANDS_CSV, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            company_id = company_id_map.get(row["company_name"])
            if company_id is None:
                unresolved.append(row["company_name"])
                continue
            cur.execute(
                "INSERT INTO brands (brand_name, company_id, score) VALUES (%s, %s, %s)",
                (row["brand_name"], company_id, int(row["score"])),
            )
            brands_inserted += 1

    print(f"[seed] {brands_inserted} brands inserted.")
    if unresolved:
        print(f"[seed] WARNING: {len(unresolved)} brands had unresolved company: {set(unresolved)}")

    conn.commit()
    cur.close()


if __name__ == "__main__":
    conn = psycopg2.connect(DATABASE_URL)
    try:
        seed(conn)
        print("[seed] Done.")
    finally:
        conn.close()
