# app.py — TaxIntellilytics (Income Tax Module, Uganda)
# Single-file Streamlit app: P&L mapping, full addbacks/allowables, progressive brackets,
# credits & exemptions, QuickBooks stub, SQLite history, URA CSV/Excel export.

import os
import io
import json
import sqlite3
from datetime import datetime
from typing import List, Dict, Tuple

import numpy as np
import pandas as pd
import streamlit as st

# ----------------------------
# App Config
# ----------------------------
st.set_page_config(page_title="TaxIntellilytics — Income Tax (Uganda)", layout="wide")
st.title("💼 TaxIntellilytics — Income Tax (Uganda)")
st.caption("Automating, Analyzing, and Advancing Tax Compliance in Uganda")

DB_PATH = "taxintellilytics_history.sqlite"

# ----------------------------
# SQLite Setup (History)
# ----------------------------
def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS income_tax_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_name TEXT,
            taxpayer_type TEXT,
            year INTEGER,
            period TEXT,
            revenue REAL,
            cogs REAL,
            opex REAL,
            other_income REAL,
            other_expenses REAL,
            pbit REAL,
            capital_allowances REAL,
            exemptions REAL,
            taxable_income REAL,
            gross_tax REAL,
            credits_wht REAL,
            credits_foreign REAL,
            rebates REAL,
            net_tax_payable REAL,
            metadata_json TEXT,
            created_at TEXT
        );
        """)
init_db()

def save_history(row: dict):
    with sqlite3.connect(DB_PATH) as conn:
        cols = ",".join(row.keys())
        placeholders = ",".join(["?"] * len(row))
        conn.execute(f"INSERT INTO income_tax_history ({cols}) VALUES ({placeholders})", list(row.values()))
        conn.commit()

def load_history(client_filter: str = "") -> pd.DataFrame:
    with sqlite3.connect(DB_PATH) as conn:
        df = pd.read_sql_query("SELECT * FROM income_tax_history ORDER BY year DESC, created_at DESC", conn)
    if client_filter and not df.empty:
        df = df[df["client_name"].str.contains(client_filter, case=False, na=False)]
    return df

# ----------------------------
# QuickBooks SDK (Optional stub)
# ----------------------------
def qb_is_available():
    try:
        import intuitlib, quickbooks  # noqa
        return True
    except Exception:
        return False

def qb_env_ready():
    required = ["QB_CLIENT_ID", "QB_CLIENT_SECRET", "QB_REDIRECT_URI", "QB_ENVIRONMENT", "QB_REALM_ID"]
    return all(os.getenv(k) for k in required)

def qb_connect_button():
    st.subheader("🔗 QuickBooks Connection (Optional)")
    if not qb_is_available():
        st.info("QuickBooks SDK not installed. Install `intuit-oauth` and `python-quickbooks` to enable.")
        return None
    if not qb_env_ready():
        st.warning("Set env vars QB_CLIENT_ID, QB_CLIENT_SECRET, QB_REDIRECT_URI, QB_ENVIRONMENT, QB_REALM_ID to enable OAuth2.")
        return None
    st.write("Environment ready ✅. (This is a simulated button for demo.)")
    if st.button("Fetch P&L from QuickBooks (Simulated)"):
        data = {
            "Account": ["Income:Sales", "Income:Other Income", "COGS", "Expenses:Rent", "Expenses:Salaries"],
            "Amount": [250_000_000, 10_000_000, 90_000_000, 30_000_000, 60_000_000],
        }
        df = pd.DataFrame(data)
        st.success("Fetched P&L (simulated).")
        st.dataframe(df)
        return df
    return None

# ----------------------------
# File Upload & P&L Mapping
# ----------------------------
def parse_financial_file(uploaded) -> pd.DataFrame:
    try:
        return pd.read_excel(uploaded)
    except Exception:
        uploaded.seek(0)
        return pd.read_csv(uploaded)

def auto_map_pl(df: pd.DataFrame) -> Tuple[float, float, float, float, float]:
    cols = {c.lower().strip(): c for c in df.columns}
    revenue = df[cols.get("revenue")].sum() if "revenue" in cols else 0.0
    cogs = df[cols.get("cogs")].sum() if "cogs" in cols else 0.0
    opex = df[cols.get("operating_expenses")].sum() if "operating_expenses" in cols else 0.0
    other_income = df[cols.get("other_income")].sum() if "other_income" in cols else 0.0
    other_expenses = df[cols.get("other_expenses")].sum() if "other_expenses" in cols else 0.0

    if "account" in cols and "amount" in cols:
        tmp = df[[cols["account"], cols["amount"]]].copy()
        tmp.columns = ["Account", "Amount"]
        revenue += tmp[tmp["Account"].str.contains("income|sales|revenue", case=False, na=False)]["Amount"].sum()
        cogs += tmp[tmp["Account"].str.contains("cogs|cost of goods", case=False, na=False)]["Amount"].sum()
        opex += tmp[tmp["Account"].str.contains("expense|utilities|rent|salary|transport|admin", case=False, na=False)]["Amount"].sum()
        other_income += tmp[tmp["Account"].str.contains("other income|gain", case=False, na=False)]["Amount"].sum()
        other_expenses += tmp[tmp["Account"].str.contains("other expense|loss", case=False, na=False)]["Amount"].sum()

    return float(revenue), float(cogs), float(opex), float(other_income), float(other_expenses)

# ----------------------------
# Tax Computation
# ----------------------------
def compute_individual_tax_brackets(taxable_income: float, brackets: List[Dict]) -> float:
    if taxable_income <= 0:
        return 0.0
    tax = 0.0
    for i, b in enumerate(brackets):
        threshold = b["threshold"]
        rate = b["rate"]
        fixed = b.get("fixed", 0.0)
        next_threshold = brackets[i + 1]["threshold"] if i + 1 < len(brackets) else None

        if taxable_income > threshold:
            upper = taxable_income if next_threshold is None else min(taxable_income, next_threshold)
            taxable_slice = max(0.0, upper - threshold)
            tax = fixed + taxable_slice * rate
        else:
            break
    return round(max(0.0, tax), 2)

def compute_company_tax(taxable_income: float, company_rate: float = 0.30) -> float:
    if taxable_income <= 0:
        return 0.0
    return round(taxable_income * company_rate, 2)

def apply_credits_and_rebates(gross_tax: float, credits_wht: float, credits_foreign: float, rebates: float) -> float:
    return max(0.0, gross_tax - credits_wht - credits_foreign - rebates)

# ----------------------------
# URA Form Schemas & Validation (DT-2001, DT-2002)
# ----------------------------
URA_SCHEMAS = {
    "DT-2001": {  # Individual with business income
        "fields": [
            ("TIN", "str"), ("Taxpayer Name", "str"), ("Period", "str"),
            ("Year", "int"), ("Business Income (UGX)", "float"),
            ("Allowable Deductions (UGX)", "float"),
            ("Capital Allowances (UGX)", "float"),
            ("Exemptions (UGX)", "float"),
            ("Taxable Income (UGX)", "float"),
            ("Gross Tax (UGX)", "float"),
            ("WHT Credits (UGX)", "float"),
            ("Foreign Tax Credit (UGX)", "float"),
            ("Rebates (UGX)", "float"),
            ("Net Tax Payable (UGX)", "float")
        ]
    },
    "DT-2002": {  # Non-individual (company)
        "fields": [
            ("TIN", "str"), ("Entity Name", "str"), ("Period", "str"),
            ("Year", "int"), ("Gross Turnover (UGX)", "float"),
            ("COGS (UGX)", "float"), ("Operating Expenses (UGX)", "float"),
            ("Other Income (UGX)", "float"), ("Other Expenses (UGX)", "float"),
            ("Capital Allowances (UGX)", "float"), ("Exemptions (UGX)", "float"),
            ("Taxable Income (UGX)", "float"), ("Gross Tax (UGX)", "float"),
            ("WHT Credits (UGX)", "float"), ("Foreign Tax Credit (UGX)", "float"),
            ("Rebates (UGX)", "float"), ("Net Tax Payable (UGX)", "float")
        ]
    }
}

def validate_and_build_return(form_code: str, payload: dict) -> pd.DataFrame:
    schema = URA_SCHEMAS[form_code]["fields"]
    out = {}
    for field, ftype in schema:
        if field not in payload:
            raise ValueError(f"Missing required field: {field}")
        val = payload[field]
        if ftype == "int":
            out[field] = int(val)
        elif ftype == "float":
            out[field] = float(val)
        else:
            out[field] = str(val)
    return pd.DataFrame([out])

# ----------------------------
# Sidebar Configuration
# ----------------------------
with st.sidebar:
    st.header("⚙️ Configuration")
    taxpayer_type = st.selectbox("Taxpayer Type", ["company", "individual"])
    tax_year = st.number_input("Year", min_value=2000, max_value=datetime.now().year, value=datetime.now().year, step=1)
    period_label = st.text_input("Period label (e.g., FY2024/25)", value=f"FY{tax_year}")

    st.markdown("### Individual Progressive Brackets (editable JSON)")
    default_brackets = [
        {"threshold": 0.0, "rate": 0.0, "fixed": 0.0},
        {"threshold": 2_820_000.0, "rate": 0.10, "fixed": 0.0},
        {"threshold": 4_020_000.0, "rate": 0.20, "fixed": 120_000.0},
        {"threshold": 4_920_000.0, "rate": 0.30, "fixed": 360_000.0},
        {"threshold": 10_000_000.0, "rate": 0.40, "fixed": 1_830_000.0},
    ]
    brackets_json = st.text_area("Brackets JSON", value=json.dumps(default_brackets, indent=2), height=180)
    try:
        individual_brackets = sorted(json.loads(brackets_json), key=lambda x: x["threshold"])
        st.success("Brackets loaded.")
    except Exception as e:
        st.error(f"Invalid brackets JSON: {e}")
        individual_brackets = default_brackets

    st.markdown("### Company Rate")
    company_rate = st.number_input("Company Income Tax Rate", min_value=0.0, max_value=1.0, value=0.30, step=0.01)

# ----------------------------
# Tabs
# ----------------------------
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "1) Data Import", "2) P&L Mapping", "3) Compute & Credits", "4) Dashboard", "5) Export & URA Forms"
])

# Shared session state placeholders
if "pl_df" not in st.session_state:
    st.session_state["pl_df"] = None
if "mapped_values" not in st.session_state:
    st.session_state["mapped_values"] = {}

# ----------------------------
# Tab 1: Data Import
# ----------------------------
with tab1:
    st.subheader("📂 Upload Financials (CSV/XLSX) or Connect to QuickBooks")
    qb_df = qb_connect_button()
    uploaded = st.file_uploader("Upload P&L / Trial Balance (CSV or Excel)", type=["csv", "xlsx"])
    df = None
    if qb_df is not None:
        df = qb_df
    if uploaded:
        up = parse_financial_file(uploaded)
        df = up if df is None else pd.concat([df, up], ignore_index=True)
    if df is not None and not df.empty:
        st.session_state["pl_df"] = df
        st.write("### Preview (first 100 rows)")
        st.dataframe(df.head(100))
    else:
        st.info("Upload a file or use QuickBooks (simulated) to proceed.")

# ----------------------------
# Tab 2: P&L Mapping
# ----------------------------
with tab2:
    st.subheader("🧭 Map P&L → Revenue / COGS / OPEX / Other")
    if st.session_state["pl_df"] is None:
        st.warning("No data found. Go to 'Data Import' first or manually enter P&L below.")
    else:
        df = st.session_state["pl_df"].copy()
        st.write("Auto-detect common columns (Account/Amount) or provide manual values.")
        if st.button("Auto-Map P&L from uploaded file"):
            revenue, cogs, opex, other_income, other_expenses = auto_map_pl(df)
            st.session_state["mapped_values"] = {
                "revenue": revenue, "cogs": cogs, "opex": opex,
                "other_income": other_income, "other_expenses": other_expenses
            }
            st.success("Auto-mapping complete (you can override the values).")

    mv = st.session_state.get("mapped_values", {})
    st.markdown("#### Manual / Override entries")
    revenue = st.number_input("Revenue (UGX)", min_value=0.0, value=float(mv.get("revenue", 0.0)), step=1000.0, format="%.2f")
    cogs = st.number_input("COGS (UGX)", min_value=0.0, value=float(mv.get("cogs", 0.0)), step=1000.0, format="%.2f")
    opex = st.number_input("Operating Expenses (UGX)", min_value=0.0, value=float(mv.get("opex", 0.0)), step=1000.0, format="%.2f")
    other_income = st.number_input("Other Income (UGX)", min_value=0.0, value=float(mv.get("other_income", 0.0)), step=1000.0, format="%.2f")
    other_expenses = st.number_input("Other Expenses (UGX)", min_value=0.0, value=float(mv.get("other_expenses", 0.0)), step=1000.0, format="%.2f")

    st.session_state["mapped_values"] = {
        "revenue": revenue, "cogs": cogs, "opex": opex,
        "other_income": other_income, "other_expenses": other_expenses
    }
    pbit_manual = (revenue + other_income) - (cogs + opex + other_expenses)
    st.metric("Derived Profit / (Loss) Before Allowances (PBIT)", f"UGX {pbit_manual:,.2f}")

# ----------------------------
# Tab 3: Compute & Credits (with full Addbacks & Allowables)
# ----------------------------
with tab3:
    st.subheader("🧮 Compute Tax, Apply Credits & Exemptions")

    client_name = st.text_input("Client Name", value="Acme Ltd")
    tin = st.text_input("TIN (optional)")

    mv = st.session_state.get("mapped_values", {})
    revenue = mv.get("revenue", 0.0)
    cogs = mv.get("cogs", 0.0)
    opex = mv.get("opex", 0.0)
    other_income = mv.get("other_income", 0.0)
    other_expenses = mv.get("other_expenses", 0.0)
    pbit = (revenue + other_income) - (cogs + opex + other_expenses)

    st.markdown("### P&L summary")
    st.write(pd.DataFrame([{
        "Revenue": revenue, "COGS": cogs, "OPEX": opex,
        "Other Income": other_income, "Other Expenses": other_expenses,
        "PBIT": pbit
    }]).T)

    # --- Addbacks (Disallowables) — use the full list provided, displayed in an expander
    addbacks_labels = [
        "Depreciation (Section 22(3)(b))","Amortisation","Redundancy",
        "Domestic/Private Expenditure (Section 22(3)(a))",
        "Capital Gain (Sections 22(1)(b), 47, 48)","Rental Income Loss (Section 22(1)(c))",
        "Expenses Exceeding 50% of Rental Income (Section 22(2))",
        "Capital Nature Expenditure (Section 22(3)(b))","Recoverable Expenditure (Section 22(3)(c))",
        "Income Tax Paid Abroad (Section 22(3)(d))","Capitalised Income (Section 22(3)(e))",
        "Gift Cost not in Recipient Income (Section 22(3)(f))","Fines or Penalties (Section 22(3)(g))",
        "Employee Retirement Contributions (Section 22(3)(h))","Life Insurance Premiums (Section 22(3)(i))",
        "Pension Payments (Section 22(3)(j))","Alimony / Allowance (Section 22(3)(k))",
        "Suppliers without TIN > UGX5M (Section 22(3)(l))","EFRIS Suppliers w/o e-invoices (Section 22(3)(m))",
        "Debt Obligation Principal (Section 25)","Interest on Capital Assets (Sections 22(3) & 50(2))",
        "Interest on Fixed Capital (Section 25(1))","Bad Debts Recovered (Section 61)",
        "General Provision for Bad Debts (Section 24)","Entertainment Income (Section 23)",
        "Meal & Refreshment Expenses (Section 23)","Charitable Donations to Non-Exempt Orgs (Section 33(1))",
        "Charitable Donations >5% Chargeable Income (Section 33(3))","Legal Fees",
        "Legal Expenses - Capital Items (Section 50)","Legal Expenses - New Trade Rights",
        "Legal Expenses - Breach of Law","Cost of Breach of Contract - Capital Account",
        "Legal Expenses on Breach of Contract - Capital Account","Legal Expenses on Loan Renewals - Non-commercial",
        "Bad Debts by Senior Employee/Management","General Provisions Bad Debts (FI Credit Classification)",
        "Loss on Sale of Fixed Assets (Section 22(3)(b))","Loss on Other Capital Items (Section 22(3)(b))",
        "Expenditure on Share Capital Increase (Section 22(3)(b))","Dividends Paid (Section 22(3)(d))",
        "Provision for Bad Debts (Non-Financial Institutions) (Section 24)",
        "Increase in Provision for Bad Debts (Section 24)","Debt Collection Expenses related to Capital Expenditure",
        "Foreign Currency Debt Gains (Section 46(2))","Costs incidental to Capital Asset (Stamp Duty, Section 50)",
        "Non-Business Expenses (Section 22)","Miscellaneous Staff Costs",
        "Staff Costs - Commuting (Section 22(4)(b))","First Time Work Permits",
        "Unrealised Foreign Exchange Losses (Section 46(3))","Foreign Currency Debt Losses (Section 46)",
        "Education Expenditure (Non Section 32)","Donations (Non Section 33)",
        "Decommissioning Expenditure by Licensee (Section 99(2))","Telephone Costs (10%)",
        "Revaluation Loss","Interest Expense on Treasury Bills (Section 139(e))",
        "Burial Expenses (Section 22(3)(b))","Subscription (Section 22(3)(a))",
        "Interest on Directors Debit Balances (Section 22(3)(a))","Entertainment Expenses (Section 23)",
        "Gifts (Section 22(3)(f))","Dividends Paid (duplicate)","Income Carried to Reserve Fund (Section 22(3)(e))",
        "Impairment Losses on Loans and Advances","Interest Expense on Treasury Bonds (Section 139(e))",
        "Staff Leave Provisions (Section 22(4)(b))","Increase in Gratuity","Balancing Charge (Sections 27(5) & 18(1))"
    ]

    addbacks = {}
    with st.expander("Show / Enter Addbacks (Disallowable Expenses) — full list", expanded=False):
        for label in addbacks_labels:
            key = f"addback__{label}"
            addbacks[label] = st.number_input(label, min_value=0.0, value=float(st.session_state.get(key, 0.0)), format="%.2f", key=key)

    total_addbacks = sum(addbacks.values())
    adjusted_profit = pbit + total_addbacks
    st.markdown(f"### Adjusted Profit (PBIT + Addbacks): UGX {adjusted_profit:,.2f}")

    # --- Allowables (Deductions) — full list
    allowables_labels = [
        "Wear & Tear (Section 27(1))","Industrial Building Allowance (5% for 20 years) (Section 28(1))",
        "Startup Costs (25%) (Section 28)","Reverse VAT (Section 22(1)(a))",
        "Listing Business with Uganda Stock Exchange (Section 29(2)(a))",
        "Registration Fees, Accountant Fees, Legal Fees, Advertising, Training (Section 29(2)(b))",
        "Expenses in Acquiring Intangible Asset (Section 30(1))","Disposal of Intangible Asset (Section 30(2))",
        "Minor Capital Expenditure (Minor Capex) (Section 26(2))","Revenue Expenditures - Repairs & Maintenance (Section 26)",
        "Expenditure on Scientific Research (Section 31(1))","Expenditure on Training (Education) (Section 32(1))",
        "Charitable Donations to Exempt Organisations (Section 33(1))","Charitable Donations Up to 5% Chargeable Income (Section 33(3))",
        "Expenditure on Farming (Section 34)","Apportionment of Deductions (Section 35)",
        "Carry Forward Losses from Previous Period (Section 36(1))","Carry Forward Losses Upto 50% after 7 Years (Section 36(6))",
        "Disposal of Trading Stock (Section 44(1))","Foreign Currency Debt Loss (Realised Exchange Loss) (Section 46(3))",
        "Loss on Disposal of Asset (Section 48)","Exclusion of Doctrine Mutuality (Section 59(3))",
        "Partnership Loss for Resident Partner (Section 66(3))","Partnership Loss for Non-Resident Partner (Section 66(4))",
        "Expenditure or Loss by Trustee Beneficiary (Section 71(5))","Expenditure or Loss by Beneficiary of Deceased Estate (Section 72(2))",
        "Limitation on Deduction for Petroleum Operations (Section 91(1))","Decommission Costs & Expenditures - Petroleum (Section 99(2))",
        "Unrealised Gains (Section 46)","Impairment of Asset","Decrease in Provision for Bad Debts (Section 24)",
        "Bad Debts Written Off (Section 24)","Staff Costs - Business Travel (Section 22)",
        "Private Employer Disability Tax (Section 22(1)(e))","Rental Income Expenditure & Losses (Section 22(1)(c)(2))",
        "Local Service Tax (Section 22(1)(d))","Interest Income on Treasury Bills (Section 139(a))",
        "Interest on Circulating Capital","Interest Income on Treasury Bonds (Section 139(a))",
        "Specific Provisions for Bad Debts (Financial Institutions)","Revaluation Gains (Financial Institutions)",
        "Rental Income (Section 5(3)(a))","Interest Income from Treasury Bills (Section 139(a)(c)(d))",
        "Interest Income from Treasury Bonds (Section 139(a)(c)(d))","Legal Expenses on Breach of Contract to Revenue Account",
        "Legal Expenses on Maintenance of Capital Assets","Legal Expenses on Existing Trade Rights",
        "Legal Expenses Incidental to Revenue Items","Legal Expenses on Debt Collection - Trade Debts",
        "Closing Tax Written Down Value < UGX1M (Section 27(6))","Intangible Assets",
        "Legal Expenses for Renewal of Loans (Financial Institutions)","Interest on Debt Obligation (Loan) (Section 25(1))",
        "Interest on Debt Obligation by Group Member (30% EBITDA) (Section 25(3))","Gains & Losses on Disposal of Assets (Section 22(1)(b))",
        "Balancing Allowance (Sections 27(7))"
    ]

    allowables = {}
    with st.expander("Show / Enter Allowables (Deductions) — full list", expanded=False):
        for label in allowables_labels:
            key = f"allowable__{label}"
            allowables[label] = st.number_input(label, min_value=0.0, value=float(st.session_state.get(key, 0.0)), format="%.2f", key=key)

    total_allowables = sum(allowables.values())
    chargeable_income = max(0.0, adjusted_profit - total_allowables)
    st.markdown(f"### Chargeable Income (after allowables): UGX {chargeable_income:,.2f}")

    # --- Credits, allowances and adjustments
    st.markdown("### Credits, Capital Allowances & Rebates")
    col1, col2, col3 = st.columns(3)
    with col1:
        capital_allowances = st.number_input("Capital Allowances (UGX)", min_value=0.0, value=0.0, format="%.2f")
        exemptions = st.number_input("Exemptions (UGX)", min_value=0.0, value=0.0, format="%.2f")
    with col2:
        credits_wht = st.number_input("WHT Credits (UGX)", min_value=0.0, value=0.0, format="%.2f")
        credits_foreign = st.number_input("Foreign Tax Credit (UGX)", min_value=0.0, value=0.0, format="%.2f")
    with col3:
        rebates = st.number_input("Rebates (UGX)", min_value=0.0, value=0.0, format="%.2f")
        provisional_tax_paid = st.number_input("Provisional Tax Paid (UGX)", min_value=0.0, value=0.0, format="%.2f")

    # Adjust taxable income by capital allowances & exemptions (policy: we recompute on adjusted taxable)
    adjusted_taxable_income = max(0.0, chargeable_income - capital_allowances - exemptions)
    if taxpayer_type.lower() == "company":
        gross_tax = compute_company_tax(adjusted_taxable_income, company_rate=company_rate)
    else:
        gross_tax = compute_individual_tax_brackets(adjusted_taxable_income, individual_brackets)

    net_tax_payable = apply_credits_and_rebates(gross_tax, credits_wht, credits_foreign, rebates)
    net_tax_after_provisional = max(0.0, net_tax_payable - provisional_tax_paid)

    st.metric("Taxable Income (after capital allowances & exemptions)", f"UGX {adjusted_taxable_income:,.2f}")
    st.metric("Gross Tax (before credits)", f"UGX {gross_tax:,.2f}")
    st.metric("Net Tax Payable (after credits & rebates)", f"UGX {net_tax_payable:,.2f}")
    st.metric("Net Tax Payable (after provisional payments)", f"UGX {net_tax_after_provisional:,.2f}")

    if st.button("💾 Save Computation to History"):
        row = {
            "client_name": client_name,
            "taxpayer_type": taxpayer_type,
            "year": int(tax_year),
            "period": period_label,
            "revenue": revenue, "cogs": cogs, "opex": opex,
            "other_income": other_income, "other_expenses": other_expenses,
            "pbit": pbit,
            "capital_allowances": capital_allowances, "exemptions": exemptions,
            "taxable_income": adjusted_taxable_income, "gross_tax": gross_tax,
            "credits_wht": credits_wht, "credits_foreign": credits_foreign,
            "rebates": rebates, "net_tax_payable": net_tax_after_provisional,
            "metadata_json": json.dumps({"TIN": tin}),
            "created_at": datetime.utcnow().isoformat()
        }
        save_history(row)
        st.success("Saved to history.")

# ----------------------------
# Tab 4: Dashboard
# ----------------------------
with tab4:
    st.subheader("📊 Multi-Year History Dashboard")
    client_filter = st.text_input("Filter by client name (optional)", "")
    hist = load_history(client_filter)
    if hist.empty:
        st.info("No saved history yet.")
    else:
        st.dataframe(hist.head(200))
        st.markdown("#### Net Tax by Year")
        pivot = hist.groupby(["year"])["net_tax_payable"].sum().reset_index()
        st.line_chart(pivot.rename(columns={"net_tax_payable": "Net Tax Payable"}).set_index("year"))
        st.markdown("#### Taxable Income vs Gross Tax (latest 30)")
        st.bar_chart(hist.head(30).set_index("created_at")[["taxable_income", "gross_tax"]])

# ----------------------------
# Tab 5: Export & URA Forms
# ----------------------------
with tab5:
    st.subheader("📤 URA Return CSV / Excel (DT-2001 / DT-2002) with Validation")
    latest = load_history().head(1)
    suggested_client = latest["client_name"].iloc[0] if not latest.empty else ""
    suggested_year = int(latest["year"].iloc[0]) if not latest.empty else tax_year
    suggested_period = latest["period"].iloc[0] if not latest.empty else period_label
    suggested_net_tax = float(latest["net_tax_payable"].iloc[0]) if not latest.empty else 0.0
    suggested_taxable = float(latest["taxable_income"].iloc[0]) if not latest.empty else 0.0
    suggested_gross = float(latest["gross_tax"].iloc[0]) if not latest.empty else 0.0

    st.markdown("Fill the required fields to build a URA-compliant CSV/Excel.")
    form_code = "DT-2002" if taxpayer_type.lower() == "company" else "DT-2001"
    st.info(f"Selected Form: **{form_code}**")

    TIN_input = st.text_input("TIN (required)", value=json.loads(latest["metadata_json"].iloc[0])["TIN"] if not latest.empty and latest["metadata_json"].iloc[0] else "")

    if form_code == "DT-2001":
        taxpayer_name = st.text_input("Taxpayer Name", value=suggested_client)
        business_income = st.number_input("Business Income (UGX)", min_value=0.0, value=suggested_taxable, format="%.2f")
        allowable_deductions = st.number_input("Allowable Deductions (UGX)", min_value=0.0, value=0.0, format="%.2f")
        capital_allowances_f = st.number_input("Capital Allowances (UGX)", min_value=0.0, value=0.0, format="%.2f")
        exemptions_f = st.number_input("Exemptions (UGX)", min_value=0.0, value=0.0, format="%.2f")
        gross_tax_f = st.number_input("Gross Tax (UGX)", min_value=0.0, value=suggested_gross, format="%.2f")
        wht_f = st.number_input("WHT Credits (UGX)", min_value=0.0, value=0.0, format="%.2f")
        foreign_f = st.number_input("Foreign Tax Credit (UGX)", min_value=0.0, value=0.0, format="%.2f")
        rebates_f = st.number_input("Rebates (UGX)", min_value=0.0, value=0.0, format="%.2f")

        payload = {
            "TIN": TIN_input,
            "Taxpayer Name": taxpayer_name,
            "Period": suggested_period,
            "Year": suggested_year,
            "Business Income (UGX)": business_income,
            "Allowable Deductions (UGX)": allowable_deductions,
            "Capital Allowances (UGX)": capital_allowances_f,
            "Exemptions (UGX)": exemptions_f,
            "Taxable Income (UGX)": max(0.0, business_income - allowable_deductions - capital_allowances_f - exemptions_f),
            "Gross Tax (UGX)": gross_tax_f,
            "WHT Credits (UGX)": wht_f,
            "Foreign Tax Credit (UGX)": foreign_f,
            "Rebates (UGX)": rebates_f,
            "Net Tax Payable (UGX)": max(0.0, gross_tax_f - wht_f - foreign_f - rebates_f)
        }

    else:  # DT-2002
        entity_name = st.text_input("Entity Name", value=suggested_client)
        gross_turnover = st.number_input("Gross Turnover (UGX)", min_value=0.0, value=float(latest["revenue"].iloc[0]) if not latest.empty else 0.0, format="%.2f")
        cogs_f = st.number_input("COGS (UGX)", min_value=0.0, value=float(latest["cogs"].iloc[0]) if not latest.empty else 0.0, format="%.2f")
        opex_f = st.number_input("Operating Expenses (UGX)", min_value=0.0, value=float(latest["opex"].iloc[0]) if not latest.empty else 0.0, format="%.2f")
        other_income_f = st.number_input("Other Income (UGX)", min_value=0.0, value=float(latest["other_income"].iloc[0]) if not latest.empty else 0.0, format="%.2f")
        other_expenses_f = st.number_input("Other Expenses (UGX)", min_value=0.0, value=float(latest["other_expenses"].iloc[0]) if not latest.empty else 0.0, format="%.2f")
        capital_allowances_f = st.number_input("Capital Allowances (UGX)", min_value=0.0, value=0.0, format="%.2f")
        exemptions_f = st.number_input("Exemptions (UGX)", min_value=0.0, value=0.0, format="%.2f")
        gross_tax_f = st.number_input("Gross Tax (UGX)", min_value=0.0, value=suggested_gross, format="%.2f")
        wht_f = st.number_input("WHT Credits (UGX)", min_value=0.0, value=0.0, format="%.2f")
        foreign_f = st.number_input("Foreign Tax Credit (UGX)", min_value=0.0, value=0.0, format="%.2f")
        rebates_f = st.number_input("Rebates (UGX)", min_value=0.0, value=0.0, format="%.2f")

        taxable_income_calc = max(0.0, (gross_turnover + other_income_f) - (cogs_f + opex_f + other_expenses_f) - capital_allowances_f - exemptions_f)
        payload = {
            "TIN": TIN_input,
            "Entity Name": entity_name,
            "Period": suggested_period,
            "Year": suggested_year,
            "Gross Turnover (UGX)": gross_turnover,
            "COGS (UGX)": cogs_f,
            "Operating Expenses (UGX)": opex_f,
            "Other Income (UGX)": other_income_f,
            "Other Expenses (UGX)": other_expenses_f,
            "Capital Allowances (UGX)": capital_allowances_f,
            "Exemptions (UGX)": exemptions_f,
            "Taxable Income (UGX)": taxable_income_calc,
            "Gross Tax (UGX)": gross_tax_f,
            "WHT Credits (UGX)": wht_f,
            "Foreign Tax Credit (UGX)": foreign_f,
            "Rebates (UGX)": rebates_f,
            "Net Tax Payable (UGX)": max(0.0, gross_tax_f - wht_f - foreign_f - rebates_f)
        }

    if st.button("✅ Validate & Build CSV / Excel"):
        try:
            df_return = validate_and_build_return(form_code, payload)
            st.success("Validation passed. Download your URA return below.")
            csv_bytes = df_return.to_csv(index=False).encode("utf-8")
            st.download_button(label="📥 Download URA Return CSV", data=csv_bytes, file_name=f"{form_code}_{payload.get('Year')}_{payload.get('TIN','')}.csv", mime="text/csv")
            # Excel
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
                df_return.to_excel(writer, index=False, sheet_name=form_code)
                writer.save()
            st.download_button(label="📥 Download URA Return Excel", data=buffer.getvalue(), file_name=f"{form_code}_{payload.get('Year')}_{payload.get('TIN','')}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            st.dataframe(df_return)
        except Exception as e:
            st.error(f"Validation failed: {e}")

# ----------------------------
# Footer Notes
# ----------------------------
st.markdown("---")
st.markdown("""
**Notes & Next Steps**
- Brackets in the sidebar are editable — make sure these match the official URA schedule for the relevant year.
- QuickBooks integration is a stub here. For production, implement OAuth2 callback endpoints and token persistence; then call the QuickBooks Reports API (ProfitAndLoss).
- URA schemas here are minimal; extend them to include all required URA fields, field lengths, and validation rules.
- Add authentication, role-based access, and secure storage before using in production.
- This tool is designed to speed internal computations and should not replace professional tax advice or formal URA filing procedures.
""")

st.markdown("---")
st.markdown("**Disclaimer:** This app is a simplified tax computation tool based on Uganda ITA Cap 338.")


