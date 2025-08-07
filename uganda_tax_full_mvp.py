import streamlit as st

st.set_page_config(page_title="Uganda ITA Cap 338 Tax Computation", layout="wide")
st.title("🇺🇬 Uganda Business Income Tax Computation (ITA Cap 338)")

st.markdown("""
This app computes Business Income Tax liability under the Uganda Income Tax Act Cap 338 using detailed tax computation rules.
Fill the relevant fields below. Leave zero if not applicable.
""")

# SECTION 1: Basic inputs and PBIT
st.header("1. Basic Income and Adjustments")

pbit = st.number_input("Profit Before Income Tax (PBIT)", min_value=0.0, step=1000.0, format="%.2f")

st.subheader("Addbacks (Disallowables) — Sections cited")

depreciation = st.number_input("1. Depreciation (22(3)(b))", 0.0, step=1000.0, format="%.2f")
amortisation = st.number_input("2. Amortisation", 0.0, step=1000.0, format="%.2f")
redundancy = st.number_input("3. Redundancy", 0.0, step=1000.0, format="%.2f")
domestic_expenses = st.number_input("4. Expenditure/Loss of Domestic or Private Nature (22(3)(a))", 0.0, step=1000.0, format="%.2f")
capital_gains_losses = st.number_input("5. Gains/Losses on Disposal of Business Assets (22(1)(b), 47, 48)", 0.0, step=1000.0, format="%.2f")
rental_expenses_loss = st.number_input("6. Expenditure/Loss in Rental Income (22(1)(c))", 0.0, step=1000.0, format="%.2f")
exceeding_50pct_rental = st.number_input("8. Expenses Exceeding 50% of Rental Income (22(2))", 0.0, step=1000.0, format="%.2f")
capital_nature_expenses = st.number_input("9. Expenditure or Loss of Capital Nature (22(3)(b))", 0.0, step=1000.0, format="%.2f")
recoverable_expenses = st.number_input("10. Expenses Recoverable under Insurance/Contract (22(3)(c))", 0.0, step=1000.0, format="%.2f")
foreign_income_tax = st.number_input("11. Income Tax Payable in Uganda or Abroad (22(3)(d))", 0.0, step=1000.0, format="%.2f")
capitalised_income = st.number_input("12. Income Carried to Reserve or Capitalised (22(3)(e))", 0.0, step=1000.0, format="%.2f")
gift_cost = st.number_input("13. Cost of Gift to Individual not included in Recipient's Gross Income (22(3)(f))", 0.0, step=1000.0, format="%.2f")
fines_penalties = st.number_input("14. Fines or Penalties Paid to Government (22(3)(g))", 0.0, step=1000.0, format="%.2f")
retirement_fund = st.number_input("15. Employee's Retirement Fund Contributions (22(3)(h))", 0.0, step=1000.0, format="%.2f")
life_insurance = st.number_input("16. Life Insurance Premiums (22(3)(i))", 0.0, step=1000.0, format="%.2f")
pension_payments = st.number_input("17. Pension Payments to Any Person (22(3)(j))", 0.0, step=1000.0, format="%.2f")
alimony_allowance = st.number_input("18. Alimony/Allowance under Judicial Order (22(3)(k))", 0.0, step=1000.0, format="%.2f")
suppliers_no_tin = st.number_input("19. Expenses > UGX 5M from Suppliers Without TIN (22(3)(l))", 0.0, step=1000.0, format="%.2f")
efris_suppliers_no_invoice = st.number_input("20. Expenses from EFRIS Suppliers Not Supported by e-invoices/e-receipts (22(3)(m))", 0.0, step=1000.0, format="%.2f")
debt_obligation_principal = st.number_input("21. Debt Obligation Principal (25)", 0.0, step=1000.0, format="%.2f")
interest_on_capital_assets = st.number_input("22. Interest on Capital Assets Included in Cost Base (22(3) & 50(2))", 0.0, step=1000.0, format="%.2f")
interest_on_fixed_capital = st.number_input("23. Interest on Fixed Capital (25(1))", 0.0, step=1000.0, format="%.2f")
bad_debts_recovered = st.number_input("24. Bad Debts Recovered (61)", 0.0, step=1000.0, format="%.2f")
general_prov_bad_debts = st.number_input("25. General Provision for Bad Debts (24)", 0.0, step=1000.0, format="%.2f")
entertainment_income = st.number_input("26. Entertainment Income (23)", 0.0, step=1000.0, format="%.2f")
meal_refreshment_expenses = st.number_input("27. Expenses on Meals and Refreshments (23)", 0.0, step=1000.0, format="%.2f")
charitable_non_exempt = st.number_input("28. Charitable Donations to Non-exempt Organisation (33(1))", 0.0, step=1000.0, format="%.2f")
charitable_excess_5pct = st.number_input("29. Charitable Donations > 5% Chargeable Income (33(3))", 0.0, step=1000.0, format="%.2f")
legal_fees = st.number_input("30. Legal Fees (22(3)(b))", 0.0, step=1000.0, format="%.2f")
legal_exp_capital_items = st.number_input("31. Legal Expenses Incidental to Capital Items (50)", 0.0, step=1000.0, format="%.2f")

# Add more fields similarly for other entries...

# SECTION 2: Allowable deductions
st.header("2. Allowable Deductions")

wear_and_tear = st.number_input("1. Wear and Tear (27(1))", 0.0, step=1000.0, format="%.2f")
industrial_building_allowance = st.number_input("2. Industrial Building Allowance (5% of cost base for 20 yrs) (28(1))", 0.0, step=1000.0, format="%.2f")
startup_costs_25pct = st.number_input("3. Start-up Costs (25%) (28)", 0.0, step=1000.0, format="%.2f")
reverse_vat = st.number_input("Reverse VAT (22(1)(a))", 0.0, step=1000.0, format="%.2f")
listing_ugx_stock_exchange = st.number_input("Listing on Uganda Stock Exchange (29(2)(a))", 0.0, step=1000.0, format="%.2f")
registration_fees = st.number_input("Registration Fees (URSB), Accountant, Legal, Advertising, Training (29(2)(b))", 0.0, step=1000.0, format="%.2f")
expenses_intangible_assets = st.number_input("Expenses on Acquiring Intangible Assets (30(1))", 0.0, step=1000.0, format="%.2f")

# ... and so on for the rest of deductions

# SECTION 3: Other Deductions and Taxes
st.header("3. Provisional Taxes and Withholding Taxes")

provisional_taxes_paid = st.number_input("Provisional Taxes Paid", 0.0, step=1000.0, format="%.2f")
withholding_taxes = st.number_input("Withholding Taxes", 0.0, step=1000.0, format="%.2f")

# Calculate Addbacks total (disallowables)
addbacks = (
    depreciation + amortisation + redundancy + domestic_expenses + capital_gains_losses + rental_expenses_loss + 
    exceeding_50pct_rental + capital_nature_expenses + recoverable_expenses + foreign_income_tax + capitalised_income + 
    gift_cost + fines_penalties + retirement_fund + life_insurance + pension_payments + alimony_allowance + suppliers_no_tin +
    efris_suppliers_no_invoice + debt_obligation_principal + interest_on_capital_assets + interest_on_fixed_capital + 
    bad_debts_recovered + general_prov_bad_debts + entertainment_income + meal_refreshment_expenses + charitable_non_exempt + 
    charitable_excess_5pct + legal_fees + legal_exp_capital_items
    # Add others as you add more fields
)

# Calculate Allowables total (deductions)
allowables = (
    wear_and_tear + industrial_building_allowance + startup_costs_25pct + reverse_vat + listing_ugx_stock_exchange + registration_fees + 
    expenses_intangible_assets
    # Add others as you add more fields
)

adjusted_profit = pbit + addbacks
chargeable_income = adjusted_profit - allowables

income_tax = round(chargeable_income * 0.30, 2)
final_tax = income_tax - provisional_taxes_paid - withholding_taxes

if st.button("Compute Tax"):
    st.subheader("Tax Computation Summary")
    st.write(f"**Adjusted Profit** (PBIT + Addbacks): UGX {adjusted_profit:,.2f}")
    st.write(f"**Chargeable Income** (Adjusted Profit - Allowables): UGX {chargeable_income:,.2f}")
    st.write(f"**Income Tax Payable (30%)**: UGX {income_tax:,.2f}")
    st.write(f"**Less: Provisional Taxes Paid**: UGX {provisional_taxes_paid:,.2f}")
    st.write(f"**Less: Withholding Taxes**: UGX {withholding_taxes:,.2f}")
    if final_tax >= 0:
        st.success(f"**Final Tax Payable**: UGX {final_tax:,.2f}")
    else:
        st.info(f"**Tax Refund Due**: UGX {abs(final_tax):,.2f}")

    st.markdown("""
    ---
    #### Notes:
    - All figures are input in Uganda Shillings (UGX).
    - This computation follows the Income Tax Act Cap 338, Uganda.
    - For detailed references, consult the specific sections cited next to each input.
    """)
else:
    st.info("Click the **Compute Tax** button to calculate your tax liability.")

