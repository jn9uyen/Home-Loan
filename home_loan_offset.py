'''
home_loan_offset.py
Single offset account only (no fixed)
'''

import sys
import importlib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from loan_products import LoanOffset, LoanProduct

# importlib.reload(sys.modules['loan_products'])

PROPERTY_PRICE = 1000000
STAMP_DUTY = 40000
FEES = 2000
LVR = 0.8
NUM_YEARS = 30

# ATHENA
FIXED_LOAN_YEARS = 0
RATE_VARIABLE = 2.24
ANNUAL_FEE_VARIABLE = 0

ANNUAL_FEE_FIXED = 0
FUNDS = 300000
SURPLUS_MTH = 2000
EXPENSE0 = 10000

self = lambda: None
self.gross_price = PROPERTY_PRICE + STAMP_DUTY + FEES
self.loan = PROPERTY_PRICE * LVR
self.deposit = self.gross_price - self.loan

# Funds surplus goes into offset account
self.funds_surplus = FUNDS - self.deposit - EXPENSE0

self.remaining_years = NUM_YEARS - FIXED_LOAN_YEARS

self.offset_split_ratio = np.linspace(0, 1, num=100)
self.acct_offset = None
self.acct_fixed = None


self.acct_offset = LoanOffset(
    self.loan, rate=RATE_VARIABLE,
    offset0=self.funds_surplus, offset_periodic=SURPLUS_MTH,
    offset_first_idx=0,
    num_years=NUM_YEARS, loan_years=None,
    payment_freq='monthly', annual_fee=ANNUAL_FEE_VARIABLE,
)

interest_paid = self.acct_offset.payment_hist['interest_paid'].iloc[-1]
print(f'Interest paid: ${interest_paid}')
