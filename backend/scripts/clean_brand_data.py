"""
Data cleaning script for Epic 4 brand data.

Input:
  - Ethical_Fashion_Brand_Scores.csv  (brand → company mapping + score)
  - company_data.csv                  (company-level detailed scores)

Output:
  - backend/data/brands_cleaned.csv
  - backend/data/companies_cleaned.csv
  - backend/data/cleaning_report.txt
"""

import csv
import os

ROOT = os.path.join(os.path.dirname(__file__), "..", "..")
DATA_OUT = os.path.join(os.path.dirname(__file__), "..", "data")

BRANDS_IN = os.path.join(ROOT, "Ethical_Fashion_Brand_Scores.csv")
COMPANY_IN = os.path.join(ROOT, "company_data.csv")
BRANDS_OUT = os.path.join(DATA_OUT, "brands_cleaned.csv")
COMPANY_OUT = os.path.join(DATA_OUT, "companies_cleaned.csv")
REPORT_OUT = os.path.join(DATA_OUT, "cleaning_report.txt")


# ---------------------------------------------------------------------------
# Fix 0: brand name corrections (garbled / encoding errors in source data)
# ---------------------------------------------------------------------------
BRAND_NAME_FIX = {
    # Cyrillic "Масрас" is a mis-encoding of "Macpac"
    "\u041c\u0430\u0441\u0440\u0430\u0441": "Macpac",
}


# ---------------------------------------------------------------------------
# Fix 1: company name mapping (brands CSV → company CSV canonical names)
# ---------------------------------------------------------------------------
COMPANY_NAME_MAP = {
    "APG& CO":                  "APG & Co",
    "On Holding AG":            "On Holding",
    "Overland Footwear Group":  "Overland",
    "St\u00fcssy":              "Stussy",     # Stüssy → Stussy
    "Universal Store":          "Universal Store Holdings Ltd",
    # Cyrillic "Масрас" (garbled encoding of Macpac)
    "\u041c\u0430\u0441\u0440\u0430\u0441": "Macpac",
}


# ---------------------------------------------------------------------------
# Fix 2: score "<1" → 0  (applied to company_data only)
# ---------------------------------------------------------------------------
NUMERIC_FIELDS = [
    "Tracing&Risk_score(all stage Production ) ",   # note trailing space in source
    "environmental_sustainability_score(score_out_of_21)",
]


# ---------------------------------------------------------------------------
# Fix 3: Adidas / New Balance footwear vs apparel
#
# Decision: add a `product_category` column to company records.
#   - Companies whose name ends with "(Footwear)" → "footwear"
#   - All others → "general"
#
# Rationale: WearImpact focuses on clothing, so "general" covers apparel.
# When both exist (Adidas + Adidas Footwear), the application will display
# them as two separate records with clear category labels, letting users
# choose which is relevant to their purchase.
# ---------------------------------------------------------------------------
def get_product_category(company_name: str) -> str:
    if "(Footwear)" in company_name:
        return "footwear"
    return "general"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def clean_numeric(value: str) -> str:
    """Replace '<1' sentinel with '0'; leave everything else untouched."""
    return "0" if str(value).strip() == "<1" else str(value).strip()


def normalise_company_name(name: str) -> str:
    """Normalise company name: straighten curly quotes, apply mapping."""
    # Normalise curly/smart quotes to straight apostrophe before any lookup
    stripped = name.strip().replace("\u2019", "'").replace("\u2018", "'")
    return COMPANY_NAME_MAP.get(stripped, stripped)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def clean_brands(report_lines: list) -> list[dict]:
    rows = []
    changes = []

    with open(BRANDS_IN, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            original_company = row["COMPANY"].strip()
            canonical = normalise_company_name(original_company)

            if canonical != original_company:
                changes.append(
                    f"  brands: COMPANY '{original_company}' → '{canonical}'"
                )

            raw_brand = row["BRAND"].strip()
            brand_name = BRAND_NAME_FIX.get(raw_brand, raw_brand)

            rows.append(
                {
                    "brand_name": brand_name,
                    "company_name": canonical,
                    "score": row["ethical_fashion_brand_score"].strip(),
                }
            )

    report_lines.append(f"\n[brands] {len(rows)} rows processed.")
    report_lines.append(f"[brands] {len(changes)} company name corrections:")
    report_lines.extend(changes)
    return rows


def clean_companies(report_lines: list) -> list[dict]:
    rows = []
    numeric_fixes = []

    with open(COMPANY_IN, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames

        for row in reader:
            cleaned = {k: v.strip() for k, v in row.items()}
            # Normalise curly quotes in Company name so it matches brands join key
            cleaned["Company"] = cleaned["Company"].replace("\u2019", "'").replace("\u2018", "'")

            # Fix 2: replace <1 in numeric score fields
            for field in NUMERIC_FIELDS:
                if field in cleaned:
                    original = cleaned[field]
                    cleaned[field] = clean_numeric(original)
                    if original != cleaned[field]:
                        numeric_fixes.append(
                            f"  {cleaned['Company']} | {field}: '{original}' → '0'"
                        )

            # Fix 3: add product_category column
            cleaned["product_category"] = get_product_category(cleaned["Company"])

            rows.append(cleaned)

    report_lines.append(f"\n[companies] {len(rows)} rows processed.")
    report_lines.append(
        f"[companies] {len(numeric_fixes)} '<1' values replaced with '0':"
    )
    report_lines.extend(numeric_fixes)

    footwear = [r for r in rows if r["product_category"] == "footwear"]
    report_lines.append(
        f"\n[companies] product_category='footwear' assigned to {len(footwear)} companies:"
    )
    for r in footwear:
        report_lines.append(f"  {r['Company']}")

    return rows, fieldnames


def write_brands(rows: list[dict]):
    with open(BRANDS_OUT, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["brand_name", "company_name", "score"])
        writer.writeheader()
        writer.writerows(rows)


def write_companies(rows: list[dict], original_fieldnames: list):
    # Strip trailing/leading spaces from field names and normalise curly quotes
    clean_fields = [f.strip().replace("\u2019", "'").replace("\u2018", "'")
                    for f in original_fieldnames]
    out_fields = clean_fields + ["product_category"]

    # Re-key each row with the cleaned field names
    clean_rows = []
    for row in rows:
        new_row = {}
        for orig, clean in zip(original_fieldnames, clean_fields):
            val = row.get(orig, row.get(clean, ""))
            # Normalise curly quotes in values too
            new_row[clean] = str(val).replace("\u2019", "'").replace("\u2018", "'")
        new_row["product_category"] = row["product_category"]
        clean_rows.append(new_row)

    with open(COMPANY_OUT, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=out_fields)
        writer.writeheader()
        writer.writerows(clean_rows)


def verify_join(brands: list[dict], companies: list[dict], report_lines: list):
    """Check every brand's company_name resolves to exactly one company record."""
    company_names = {r["Company"] for r in companies}
    unresolved = set()

    for b in brands:
        if b["company_name"] not in company_names:
            unresolved.add(b["company_name"])

    report_lines.append(f"\n[verify] Brands with unresolved company join: {len(unresolved)}")
    for name in sorted(unresolved):
        report_lines.append(f"  !! UNRESOLVED: '{name}'")

    if not unresolved:
        report_lines.append("  All brands resolve correctly to a company record.")


def main():
    os.makedirs(DATA_OUT, exist_ok=True)
    report_lines = ["=== Data Cleaning Report ==="]

    brands = clean_brands(report_lines)
    companies, orig_fields = clean_companies(report_lines)

    verify_join(brands, companies, report_lines)

    write_brands(brands)
    write_companies(companies, orig_fields)

    report_lines.append(f"\n[output] brands_cleaned.csv  → {len(brands)} rows")
    report_lines.append(f"[output] companies_cleaned.csv → {len(companies)} rows")
    report_lines.append("\nDone.")

    report_text = "\n".join(report_lines)
    with open(REPORT_OUT, "w", encoding="utf-8") as f:
        f.write(report_text)

    print(report_text)


if __name__ == "__main__":
    main()
