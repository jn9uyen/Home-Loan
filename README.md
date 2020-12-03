# Home-Loan
Calculate optimal split between variable and fixed rate products.

## Optimal Split

Run `home_loan.py`. Input parameters are global variables declared within the file. Parameters:

- PROPERTY_PRICE
- STAMP_DUTY
- FEES: legal fees
- LVR: loan to value ratio (e.g. 0.8)
- NUM_YEARS: e.g 30
- FIXED_LOAN_YEARS: e.g. 2
- RATE_VARIABLE: percentage (e.g. 2.49)
- RATE_FIXED: percentage (e.g. 1.88)
- ANNUAL_FEE_VARIABLE
- ANNUAL_FEE_FIXED: leave as 0 if there is a package fee for both variable and fixed products
- FUNDS: cash amount to contribute towards loan shortfall; leftover goes into offset account
- SURPLUS_MTH: monthly savings to contribute to offset
- EXPENSE0: any initial non-loan related expenses (e.g. furniture)

The script outputs the optimal split in `figures/total_paid.png`, which accounts for total interest and fees paid over the loan duration (e.g. 30 years).

## Total Interest Paid on Single Offset Account

Run `home_loan_offset.py`.
