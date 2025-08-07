streamlit_app.py
import streamlit as st

# Constants
TAX_RATE = 0.30  # 30% tax on chargeable income

st.set_page_config(page_title="Uganda Business Income Tax Calculator (ITA Cap 338)", layout="wide")

st.title("Uganda Business Income Tax Computation (ITA Cap 338)")

st.markdown("""
This application computes Business Income Tax payable or claimable based on Uganda's Income Tax Act Cap 338.
Please input all amounts in Ugandan Shillings (UGX).
""")

# SECTION 1: Basic Info
st.header("1. Basic Information & Profit Before Income Tax (PBIT)")
title = st.text_input("Business/Company Name or Title", max_chars=100)
pbit = st.number_input("Profit Before Income Tax (PBIT)", min_value=0.0, format="%.2f")

# SECTION 2: Addbacks / Disallowables (Disallowable Expenses)
st.header("2. Addbacks / Disallowables (Add to PBIT)")
st.markdown("Referencing ITA Cap 338 Sections")

addbacks = {}

addbacks['Depreciation (Section 22(3)(b))'] = st.number_input("1. Depreciation", min_value=0.0, format="%.2f")
addbacks['Amortisation'] = st.number_input("2. Amortisation", min_value=0.0, format="%.2f")
addbacks['Redundancy'] = st.number_input("3. Redundancy", min_value=0.0, format="%.2f")
addbacks['Domestic/Private Expenditure (Section 22(3)(a))'] = st.number_input("4. Expenditure or Loss of Domestic or Private Nature", min_value=0.0, format="%.2f")
addbacks['Capital Gain (Sections 22(1)(b), 47, 48)'] = st.number_input("5. Gains and Losses on Disposal of Business Assets (Capital Gain)", min_value=0.0, format="%.2f")
addbacks['Rental Income Loss (Section 22(1)(c))'] = st.number_input("6. Expenditure or Loss in the case of Rental Income", min_value=0.0, format="%.2f")
addbacks['Expenses Exceeding 50% of Rental Income (Section 22(2))'] = st.number_input("7. Expenses Exceeding 50% of Rental Income", min_value=0.0, format="%.2f")
addbacks['Capital Nature Expenditure (Section 22(3)(b))'] = st.number_input("8. Expenditure or Loss of Capital Nature / Cost Base of Asset", min_value=0.0, format="%.2f")
addbacks['Recoverable Expenditure (Section 22(3)(c))'] = st.number_input("9. Expenditure or Loss Recoverable Under Insurance, Contract, Indemnity", min_value=0.0, format="%.2f")
addbacks['Income Tax Paid Abroad (Section 22(3)(d))'] = st.number_input("10. Income Tax Payable in Uganda or Abroad", min_value=0.0, format="%.2f")
addbacks['Capitalised Income (Section 22(3)(e))'] = st.number_input("11. Income Carried to Reserve Fund or Capitalised", min_value=0.0, format="%.2f")
addbacks['Gift Cost not in Recipient Income (Section 22(3)(f))'] = st.number_input("12. Cost of Gift to Individual not in Recipient’s Gross Income", min_value=0.0, format="%.2f")
addbacks['Fines or Penalties (Section 22(3)(g))'] = st.number_input("13. Fine or Penalty Paid to Government or Authority", min_value=0.0, format="%.2f")
addbacks['Employee Retirement Contributions (Section 22(3)(h))'] = st.number_input("14. Employee's Retirement Fund Contributions", min_value=0.0, format="%.2f")
addbacks['Life Insurance Premiums (Section 22(3)(i))'] = st.number_input("15. Life Insurance Premiums", min_value=0.0, format="%.2f")
addbacks['Pension Payments (Section 22(3)(j))'] = st.number_input("16. Pension Payments Made to Any Person", min_value=0.0, format="%.2f")
addbacks['Alimony / Allowance (Section 22(3)(k))'] = st.number_input("17. Alimony/Allowance under Judicial Order", min_value=0.0, format="%.2f")
addbacks['Suppliers without TIN > UGX5M (Section 22(3)(l))'] = st.number_input("18. Expenditure Above UGX 5M from Suppliers Without TIN", min_value=0.0, format="%.2f")
addbacks['EFRIS Suppliers w/o e-invoices (Section 22(3)(m))'] = st.number_input("19. Expenses from EFRIS-designated Suppliers Not Supported by e-invoices/e-receipts", min_value=0.0, format="%.2f")
addbacks['Debt Obligation Principal (Section 25)'] = st.number_input("20. Debt Obligation (Principal Loan Amount)", min_value=0.0, format="%.2f")
addbacks['Interest on Capital Assets (Sections 22(3) & 50(2))'] = st.number_input("21. Interest Paid on Capital Assets (Included in Cost Base)", min_value=0.0, format="%.2f")
addbacks['Interest on Fixed Capital (Section 25(1))'] = st.number_input("22. Interest on Fixed Capital", min_value=0.0, format="%.2f")
addbacks['Bad Debts Recovered (Section 61)'] = st.number_input("23. Bad Debts Recovered (Recouped Expenditure)", min_value=0.0, format="%.2f")
addbacks['General Provision for Bad Debts (Section 24)'] = st.number_input("24. General Provision for Bad Debts Not Included in Gross Income", min_value=0.0, format="%.2f")
addbacks['Entertainment Income (Section 23)'] = st.number_input("25. Entertainment Income", min_value=0.0, format="%.2f")
addbacks['Meal & Refreshment Expenses (Section 23)'] = st.number_input("26. Expenses on Meals and Refreshments", min_value=0.0, format="%.2f")
addbacks['Charitable Donations to Non-Exempt Orgs (Section 33(1))'] = st.number_input("27. Charitable Donations to Non-Exempt Organisation", min_value=0.0, format="%.2f")
addbacks['Charitable Donations >5% Chargeable Income (Section 33(3))'] = st.number_input("28. Charitable Donations in Excess of 5% Chargeable Income", min_value=0.0, format="%.2f")
addbacks['Legal Fees'] = st.number_input("29. Legal Fees", min_value=0.0, format="%.2f")
addbacks['Legal Expenses - Capital Items (Section 50)'] = st.number_input("30. Legal Expenses Incidental to Capital Items", min_value=0.0, format="%.2f")
addbacks['Legal Expenses - New Trade Rights'] = st.number_input("31. Legal Expenses to Acquire New or Future Trade Rights", min_value=0.0, format="%.2f")
addbacks['Legal Expenses - Breach of Law'] = st.number_input("32. Legal Expenses on Breach of Law", min_value=0.0, format="%.2f")
addbacks['Cost of Breach of Contract - Capital Account'] = st.number_input("33. Cost of Breach of Contract on Capital Account", min_value=0.0, format="%.2f")
addbacks['Legal Expenses on Breach of Contract - Capital Account'] = st.number_input("34. Legal Expenses on Breach of Contract in relation to Capital Account", min_value=0.0, format="%.2f")
addbacks['Legal Expenses on Loan Renewals - Non-commercial'] = st.number_input("35. Legal Expenses on Renewal of Loans (Ordinary/Non-Commercial)", min_value=0.0, format="%.2f")
addbacks['Bad Debts by Senior Employee/Management'] = st.number_input("36. Bad Debts Incurred by Senior Employee or Management", min_value=0.0, format="%.2f")
addbacks['General Provisions Bad Debts (FI Credit Classification)'] = st.number_input("37. General Provisions of Bad Debts (Financial Institutions)", min_value=0.0, format="%.2f")
addbacks['Loss on Sale of Fixed Assets (Section 22(3)(b))'] = st.number_input("38. Loss on Sale of Fixed Assets", min_value=0.0, format="%.2f")
addbacks['Loss on Other Capital Items (Section 22(3)(b))'] = st.number_input("39. Loss on Other Capital Items", min_value=0.0, format="%.2f")
addbacks['Expenditure on Share Capital Increase (Section 22(3)(b))'] = st.number_input("40. Expenditure on Increase in Share Capital", min_value=0.0, format="%.2f")
addbacks['Dividends Paid (Section 22(3)(d))'] = st.number_input("41. Dividends Paid", min_value=0.0, format="%.2f")
addbacks['Provision for Bad Debts (Non-Financial Institutions) (Section 24)'] = st.number_input("42. Provision for Bad Debts Not for Financial Institutions", min_value=0.0, format="%.2f")
addbacks['Increase in Provision for Bad Debts (Section 24)'] = st.number_input("43. Increase in Provision for Bad Debts", min_value=0.0, format="%.2f")
addbacks['Debt Collection Expenses related to Capital Expenditure'] = st.number_input("44. Debt Collection Expenses in relation to Capital Expenditure", min_value=0.0, format="%.2f")
addbacks['Foreign Currency Debt Gains (Section 46(2))'] = st.number_input("45. Foreign Currency Debt Gains (Realised Gain)", min_value=0.0, format="%.2f")
addbacks['Costs incidental to Capital Asset (Stamp Duty, Section 50)'] = st.number_input("46. Costs Incidental to Cost Base of Capital Asset", min_value=0.0, format="%.2f")
addbacks['Non-Business Expenses (Section 22)'] = st.number_input("47. Non-Business Expenses", min_value=0.0, format="%.2f")
addbacks['Miscellaneous Staff Costs'] = st.number_input("48. Miscellaneous Staff Costs", min_value=0.0, format="%.2f")
addbacks['Staff Costs - Commuting (Section 22(4)(b))'] = st.number_input("49. Staff Costs (Transport Commuting from Home to Work)", min_value=0.0, format="%.2f")
addbacks['First Time Work Permits'] = st.number_input("50. First Time Work Permits", min_value=0.0, format="%.2f")
addbacks['Unrealised Foreign Exchange Losses (Section 46(3))'] = st.number_input("51. Unrealised Foreign Exchange Losses", min_value=0.0, format="%.2f")
addbacks['Foreign Currency Debt Losses (Section 46)'] = st.number_input("52. Foreign Currency Debt Losses", min_value=0.0, format="%.2f")
addbacks['Education Expenditure (Non Section 32)'] = st.number_input("53. Expenditure on Education", min_value=0.0, format="%.2f")
addbacks['Donations (Non Section 33)'] = st.number_input("54. Donations", min_value=0.0, format="%.2f")
addbacks['Decommissioning Expenditure by Licensee (Section 99(2))'] = st.number_input("55. Decommissioning Expenditure by Licensee", min_value=0.0, format="%.2f")
addbacks['Telephone Costs (10%)'] = st.number_input("56. Telephone Costs (10%)", min_value=0.0, format="%.2f")
addbacks['Revaluation Loss'] = st.number_input("57. Revaluation Loss", min_value=0.0, format="%.2f")
addbacks['Interest Expense on Treasury Bills (Section 139(e))'] = st.number_input("58. Interest Expense on Treasury Bills", min_value=0.0, format="%.2f")
addbacks['Burial Expenses (Section 22(3)(b))'] = st.number_input("59. Burial Expenses", min_value=0.0, format="%.2f")
addbacks['Subscription (Section 22(3)(a))'] = st.number_input("60. Subscription", min_value=0.0, format="%.2f")
addbacks['Interest on Directors Debit Balances (Section 22(3)(a))'] = st.number_input("61. Interest on Directors’ Debit Balances", min_value=0.0, format="%.2f")
addbacks['Entertainment Expenses (Section 23)'] = st.number_input("62. Entertainment Expenses", min_value=0.0, format="%.2f")
addbacks['Gifts (Section 22(3)(f))'] = st.number_input("63. Gifts", min_value=0.0, format="%.2f")
addbacks['Dividends Paid (Section 22(3)(d))'] = st.number_input("64. Dividends Paid (duplicate)", min_value=0.0, format="%.2f")
addbacks['Income Carried to Reserve Fund (Section 22(3)(e))'] = st.number_input("65. Income Carried to Reserve Fund", min_value=0.0, format="%.2f")
addbacks['Impairment Losses on Loans and Advances'] = st.number_input("66. Impairment Losses on Loans and Advances", min_value=0.0, format="%.2f")
addbacks['Interest Expense on Treasury Bonds (Section 139(e))'] = st.number_input("67. Interest Expense on Treasury Bonds", min_value=0.0, format="%.2f")
addbacks['Staff Leave Provisions (Section 22(4)(b))'] = st.number_input("68. Staff Leave Provisions", min_value=0.0, format="%.2f")
addbacks['Increase in Gratuity'] = st.number_input("69. Increase in Gratuity", min_value=0.0, format="%.2f")
addbacks['Balancing Charge (Sections 27(5) & 18(1))'] = st.number_input("70. Balancing Charge", min_value=0.0, format="%.2f")

# SECTION 3: Calculate Adjusted Profit
adjusted_profit = pbit + sum(addbacks.values())

st.markdown(f"### Adjusted Profit: UGX {adjusted_profit:,.2f}")

# SECTION 4: Allowables / Deductions
st.header("3. Allowables / Deductions (Subtract from Adjusted Profit)")
allowables = {}

allowables['Wear & Tear (Section 27(1))'] = st.number_input("1. Wear & Tear", min_value=0.0, format="%.2f")
allowables['Industrial Building Allowance (5% for 20 years) (Section 28(1))'] = st.number_input("2. Industrial Building Allowance", min_value=0.0, format="%.2f")
allowables['Startup Costs (25%) (Section 28)'] = st.number_input("3. Startup Costs (25%)", min_value=0.0, format="%.2f")
allowables['Reverse VAT (Section 22(1)(a))'] = st.number_input("4. Reverse VAT", min_value=0.0, format="%.2f")
allowables['Listing Business with Uganda Stock Exchange (Section 29(2)(a))'] = st.number_input("5. Listing Business with Uganda Stock Exchange", min_value=0.0, format="%.2f")
allowables['Registration Fees, Accountant Fees, Legal Fees, Advertising, Training (Section 29(2)(b))'] = st.number_input("6. Registration, Accountant, Legal, Advertising, Training Fees", min_value=0.0, format="%.2f")
allowables['Expenses in Acquiring Intangible Asset (Section 30(1))'] = st.number_input("7. Expenses in Acquiring Intangible Asset", min_value=0.0, format="%.2f")
allowables['Disposal of Intangible Asset (Section 30(2))'] = st.number_input("8. Disposal of Intangible Asset", min_value=0.0, format="%.2f")
allowables['Minor Capital Expenditure (Minor Capex) (Section 26(2))'] = st.number_input("9. Minor Capital Expenditure (Minor Capex)", min_value=0.0, format="%.2f")
allowables['Revenue Expenditures - Repairs & Maintenance (Section 26)'] = st.number_input("10. Revenue Expenditures (Repairs & Maintenance)", min_value=0.0, format="%.2f")
allowables['Expenditure on Scientific Research (Section 31(1))'] = st.number_input("11. Expenditure on Scientific Research", min_value=0.0, format="%.2f")
allowables['Expenditure on Training (Education) (Section 32(1))'] = st.number_input("12. Expenditure on Training (Education)", min_value=0.0, format="%.2f")
allowables['Charitable Donations to Exempt Organisations (Section 33(1))'] = st.number_input("13. Charitable Donations to Exempt Organisations", min_value=0.0, format="%.2f")
allowables['Charitable Donations Up to 5% Chargeable Income (Section 33(3))'] = st.number_input("14. Charitable Donations Up to 5% Chargeable Income", min_value=0.0, format="%.2f")
allowables['Expenditure on Farming (Section 34)'] = st.number_input("15. Expenditure on Farming", min_value=0.0, format="%.2f")
allowables['Apportionment of Deductions (Section 35)'] = st.number_input("16. Apportionment of Deductions", min_value=0.0, format="%.2f")
allowables['Carry Forward Losses from Previous Period (Section 36(1))'] = st.number_input("17. Carry Forward Losses from Previous Period", min_value=0.0, format="%.2f")
allowables['Carry Forward Losses Upto 50% after 7 Years (Section 36(6))'] = st.number_input("18. Carry Forward Losses Up to 50% after 7 Years", min_value=0.0, format="%.2f")
allowables['Disposal of Trading Stock (Section 44(1))'] = st.number_input("19. Disposal of Trading Stock", min_value=0.0, format="%.2f")
allowables['Foreign Currency Debt Loss (Realised Exchange Loss) (Section 46(3))'] = st.number_input("20. Foreign Currency Debt Loss (Realised Exchange Loss)", min_value=0.0, format="%.2f")
allowables['Loss on Disposal of Asset (Section 48)'] = st.number_input("21. Loss on Disposal of Asset", min_value=0.0, format="%.2f")
allowables['Exclusion of Doctrine Mutuality (Section 59(3))'] = st.number_input("22. Exclusion of Doctrine Mutuality", min_value=0.0, format="%.2f")
allowables['Partnership Loss for Resident Partner (Section 66(3))'] = st.number_input("23. Partnership Loss for Resident Partner", min_value=0.0, format="%.2f")
allowables['Partnership Loss for Non-Resident Partner (Section 66(4))'] = st.number_input("24. Partnership Loss for Non-Resident Partner", min_value=0.0, format="%.2f")
allowables['Expenditure or Loss by Trustee Beneficiary (Section 71(5))'] = st.number_input("25. Expenditure or Loss by Trustee Beneficiary", min_value=0.0, format="%.2f")
allowables['Expenditure or Loss by Beneficiary of Deceased Estate (Section 72(2))'] = st.number_input("26. Expenditure or Loss by Beneficiary of Deceased Estate", min_value=0.0, format="%.2f")
allowables['Limitation on Deduction for Petroleum Operations (Section 91(1))'] = st.number_input("27. Limitation on Deduction - Petroleum Operations", min_value=0.0, format="%.2f")
allowables['Decommission Costs & Expenditures - Petroleum (Section 99(2))'] = st.number_input("28. Decommission Costs & Expenditures - Petroleum", min_value=0.0, format="%.2f")
allowables['Unrealised Gains (Section 46)'] = st.number_input("29. Unrealised Gains", min_value=0.0, format="%.2f")
allowables['Impairment of Asset'] = st.number_input("30. Impairment of Asset", min_value=0.0, format="%.2f")
allowables['Decrease in Provision for Bad Debts (Section 24)'] = st.number_input("31. Decrease in Provision for Bad Debts", min_value=0.0, format="%.2f")
allowables['Bad Debts Written Off (Section 24)'] = st.number_input("32. Bad Debts Written Off", min_value=0.0, format="%.2f")
allowables['Staff Costs - Business Travel (Section 22)'] = st.number_input("33. Staff Costs - Business Travel Expenses", min_value=0.0, format="%.2f")
allowables['Private Employer Disability Tax (Section 22(1)(e))'] = st.number_input("34. 2% Income Tax Payable for Private Employers with 5% Disabled Employees", min_value=0.0, format="%.2f")
allowables['Rental Income Expenditure & Losses (Section 22(1)(c)(2))'] = st.number_input("35. Rental Income Expenditure & Losses", min_value=0.0, format="%.2f")
allowables['Local Service Tax (Section 22(1)(d))'] = st.number_input("36. Local Service Tax", min_value=0.0, format="%.2f")
allowables['Interest Income on Treasury Bills (Section 139(a))'] = st.number_input("37. Interest Income on Treasury Bills", min_value=0.0, format="%.2f")
allowables['Interest on Circulating Capital'] = st.number_input("38. Interest on Circulating Capital", min_value=0.0, format="%.2f")
allowables['Interest Income on Treasury Bonds (Section 139(a))'] = st.number_input("39. Interest Income on Treasury Bonds", min_value=0.0, format="%.2f")
allowables['Specific Provisions for Bad Debts (Financial Institutions)'] = st.number_input("40. Specific Provisions for Bad Debts (F.I.)", min_value=0.0, format="%.2f")
allowables['Revaluation Gains (Financial Institutions)'] = st.number_input("41. Revaluation Gains (F.I.)", min_value=0.0, format="%.2f")
allowables['Rental Income (Section 5(3)(a))'] = st.number_input("42. Rental Income", min_value=0.0, format="%.2f")
allowables['Interest Income from Treasury Bills (Section 139(a)(c)(d))'] = st.number_input("43. Interest Income from Treasury Bills", min_value=0.0, format="%.2f")
allowables['Interest Income from Treasury Bonds (Section 139(a)(c)(d))'] = st.number_input("44. Interest Income from Treasury Bonds", min_value=0.0, format="%.2f")
allowables['Legal Expenses on Breach of Contract to Revenue Account'] = st.number_input("45. Legal Expenses on Breach of Contract to Revenue Account", min_value=0.0, format="%.2f")
allowables['Legal Expenses on Maintenance of Capital Assets'] = st.number_input("46. Legal Expenses on Maintenance of Capital Assets", min_value=0.0, format="%.2f")
allowables['Legal Expenses on Existing Trade Rights'] = st.number_input("47. Legal Expenses on Already Existing Trade Rights", min_value=0.0, format="%.2f")
allowables['Legal Expenses Incidental to Revenue Items'] = st.number_input("48. Legal Expenses Incidental to Revenue Items", min_value=0.0, format="%.2f")
allowables['Legal Expenses on Debt Collection - Trade Debts'] = st.number_input("49. Legal Expenses on Debt Collection Related to Trade Debts", min_value=0.0, format="%.2f")
allowables['Closing Tax Written Down Value < UGX1M (Section 27(6))'] = st.number_input("50. Closing Tax Written Down Value Less Than 1 Million", min_value=0.0, format="%.2f")
allowables['Intangible Assets'] = st.number_input("51. Intangible Assets", min_value=0.0, format="%.2f")
allowables['Legal Expenses for Renewal of Loans (Financial Institutions)'] = st.number_input("52. Legal Expenses for Renewal of Loans", min_value=0.0, format="%.2f")
allowables['Interest on Debt Obligation (Loan) (Section 25(1))'] = st.number_input("53. Interest on Debt Obligation", min_value=0.0, format="%.2f")
allowables['Interest on Debt Obligation by Group Member (30% EBITDA) (Section 25(3))'] = st.number_input("54. Interest on Debt Obligation by Group Member", min_value=0.0, format="%.2f")
allowables['Gains & Losses on Disposal of Assets (Section 22(1)(b))'] = st.number_input("55. Gains & Losses on Disposal of Assets", min_value=0.0, format="%.2f")
allowables['Balancing Allowance (Sections 27(7))'] = st.number_input("56. Balancing Allowance", min_value=0.0, format="%.2f")

# SECTION 5: Sum Allowables
total_allowables = sum(allowables.values())

# SECTION 6: Compute Chargeable Income
chargeable_income = adjusted_profit - total_allowables

st.markdown(f"### Chargeable Income: UGX {chargeable_income:,.2f}")

# SECTION 7: Provisional Tax & Withholding Tax
st.header("4. Taxes Paid & Adjustments")

provisional_tax = st.number_input("Provisional Taxes Paid", min_value=0.0, format="%.2f")
withholding_tax = st.number_input("Withholding Tax Deducted", min_value=0.0, format="%.2f")

# Provision adjustments
st.subheader("5. Provision Adjustments")

increase_in_provision = st.number_input("Increase in Provision (Add)", min_value=0.0, format="%.2f")
decrease_in_provision = st.number_input("Decrease in Provision (Less)", min_value=0.0, format="%.2f")

# Apply provision adjustments to chargeable income
chargeable_income_adjusted = chargeable_income + increase_in_provision - decrease_in_provision

st.markdown(f"### Adjusted Chargeable Income (after provisions): UGX {chargeable_income_adjusted:,.2f}")

# SECTION 8: Final Tax Computation
tax_payable = chargeable_income_adjusted * TAX_RATE

final_tax_payable = tax_payable - provisional_tax - withholding_tax

st.header("6. Final Tax Computation")

st.markdown(f"**Tax Payable (30% of Adjusted Chargeable Income):** UGX {tax_payable:,.2f}")
st.markdown(f"**Less: Provisional Tax Paid:** UGX {provisional_tax:,.2f}")
st.markdown(f"**Less: Withholding Tax:** UGX {withholding_tax:,.2f}")
st.markdown(f"---")
st.markdown(f"### **Final Income Tax Payable / Claimable:** UGX {final_tax_payable:,.2f}")

# Optionally display messages if tax is negative (claimable)
if final_tax_payable < 0:
    st.success("Note: Tax payable is negative; this implies a claimable/refundable tax amount.")

# SECTION 9: Additional Notes
st.header("7. Additional Notes")

additional_notes = st.text_area("Additional Notes (if any)", height=150)

# Export to CSV or Excel - basic example
import pandas as pd
from io import BytesIO

def to_excel(df):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name='Tax Computation')
    writer.save()
    processed_data = output.getvalue()
    return processed_data

if st.button("Download Computation Summary as Excel"):
    # Prepare data for export
    data_export = {
        "Title": [title],
        "PBIT": [pbit],
        "Adjusted Profit": [adjusted_profit],
        "Total Allowables": [total_allowables],
        "Chargeable Income": [chargeable_income],
        "Increase in Provision": [increase_in_provision],
        "Decrease in Provision": [decrease_in_provision],
        "Adjusted Chargeable Income": [chargeable_income_adjusted],
        "Tax Payable (30%)": [tax_payable],
        "Provisional Tax Paid": [provisional_tax],
        "Withholding Tax": [withholding_tax],
        "Final Tax Payable / Claimable": [final_tax_payable],
        "Additional Notes": [additional_notes],
    }
    df_export = pd.DataFrame(data_export)
    excel_data = to_excel(df_export)
    st.download_button(label="Download Excel File",
                       data=excel_data,
                       file_name='uganda_tax_computation.xlsx',
                       mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

st.markdown("---")
st.markdown("**Disclaimer:** This app is a simplified tax computation tool based on Uganda ITA Cap 338 and should not replace professional tax advice.")


