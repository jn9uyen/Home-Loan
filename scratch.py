'''
scratch.py
'''

import sys
import importlib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from loan_products import LoanOffset, LoanProduct


importlib.reload(sys.modules['loan_products'])


property_price = 1000000
stamp_duty = 40000
lvr = 0.8
fees = 2000
funds = 300000
surplus_mth = 2000
expense0 = 10000
annual_fee = 100

gross_price = property_price + stamp_duty + fees
loan = property_price * lvr
deposit = gross_price - loan

# Funds surplus goes into offset account
funds_surplus = funds - deposit - expense0

num_years = 30
fixed_loan_years = 2
remaining_years = num_years - fixed_loan_years

split = 0.15

acct_offset = LoanOffset(
    loan*split, rate=2.49,
    offset0=funds_surplus, offset_periodic=surplus_mth,
    offset_first_idx=0,
    num_years=num_years, loan_years=None,
    payment_freq='monthly', annual_fee=annual_fee,
)

acct_offset.total_fees
100 * 30


# Fixed for `loan_years`; then resume as offset for remaining
acct_fixed = LoanProduct(
    loan*(1 - split), rate=1.88, num_years=num_years,
    loan_years=fixed_loan_years,
    payment_freq='monthly', annual_fee=annual_fee,  # 390
)
acct_fixed.total_fees

fixed_amount_owing = (
    acct_fixed.payment_hist['amount_owing'].iloc[-1]
)

# Find period index where offset account interest payment = 0
idx = np.where(
    acct_offset.payment_hist['interest'] <= 0)[0][0]
zero_year = acct_offset.payment_hist['year'].iloc[idx]
zero_year_rel = zero_year - fixed_loan_years
zero_month_rel = round(zero_year_rel * 12)

# Put remaining balance into offset account
acct_remaining = LoanOffset(
    fixed_amount_owing, rate=2.49,
    offset0=0, offset_periodic=surplus_mth,
    offset_first_idx=zero_month_rel,
    num_years=remaining_years, loan_years=remaining_years,
    payment_freq='monthly', annual_fee=0,  # 390
)

zero_year
zero_year_rel
zero_month_rel

acct_offset.payment_hist.head()
acct_offset.payment_hist.tail()

acct_offset.payment_hist.iloc[idx-2:idx+2, :]

acct_fixed.payment_hist.head()
acct_fixed.payment_hist.tail()

acct_remaining.payment_hist.head(15)


athena = LoanOffset(
    loan, rate=2.24,
    offset0=funds_surplus, offset_periodic=surplus_mth,
    offset_first_idx=0,
    num_years=num_years, loan_years=None,
    payment_freq='monthly', annual_fee=0,
)
athena.payment_hist.tail()

athena2 = LoanOffset(
    loan, rate=2.19,
    offset0=funds_surplus, offset_periodic=surplus_mth,
    offset_first_idx=0,
    num_years=num_years, loan_years=None,
    payment_freq='monthly', annual_fee=0,
)
athena2.payment_hist.tail()


split = 1

acct_offset = LoanOffset(
    loan*split, rate=2.19,
    offset0=0, offset_periodic=surplus_mth, offset_first_idx=3,
    num_years=30, loan_years=None,
    payment_freq='monthly', annual_fee=0,
)
acct_offset.payment_hist.head()

idx = np.where(
    acct_offset.payment_hist['interest'] <= 0)[0][0]
zero_year = acct_offset.payment_hist['year'].iloc[idx]
zero_year

idx
acct_offset.payment_hist.iloc[idx, :]
