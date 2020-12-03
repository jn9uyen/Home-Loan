'''
home_loan.py
Calculate home loan payments, considering split loan + offset account
Joe Nguyen | 02 Nov 2020
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

# # HSBC
# FIXED_LOAN_YEARS = 2
# RATE_VARIABLE = 2.49
# RATE_FIXED = 1.88
# ANNUAL_FEE_VARIABLE = 195

# # UBANK
# FIXED_LOAN_YEARS = 2
# RATE_VARIABLE = 2.34
# RATE_FIXED = 1.95
# ANNUAL_FEE_VARIABLE = 0

# WBC
FIXED_LOAN_YEARS = 2
RATE_VARIABLE = 2.54
RATE_FIXED = 1.84
ANNUAL_FEE_VARIABLE = 395

ANNUAL_FEE_FIXED = 0
FUNDS = 300000
SURPLUS_MTH = 2000
EXPENSE0 = 10000


class SplitRatioSim():
    '''Calculate payments by split ratios between offset and fixed loans
    '''

    def __init__(self):
        self.gross_price = PROPERTY_PRICE + STAMP_DUTY + FEES
        self.loan = PROPERTY_PRICE * LVR
        self.deposit = self.gross_price - self.loan

        # Funds surplus goes into offset account
        self.funds_surplus = FUNDS - self.deposit - EXPENSE0

        self.remaining_years = NUM_YEARS - FIXED_LOAN_YEARS

        self.offset_split_ratio = np.linspace(0, 1, num=100)
        self.acct_offset = None
        self.acct_fixed = None

    def simulate(self):
        # Storage
        # amount_owing = []
        interest_paid = []
        fees_paid = []
        # offset_total = []

        for split in self.offset_split_ratio:

            self.acct_offset = LoanOffset(
                self.loan*split, rate=RATE_VARIABLE,
                offset0=self.funds_surplus, offset_periodic=SURPLUS_MTH,
                offset_first_idx=0,
                num_years=NUM_YEARS, loan_years=None,
                payment_freq='monthly', annual_fee=ANNUAL_FEE_VARIABLE,
            )

            # Fixed for `loan_years`; then resume as offset for remaining
            self.acct_fixed = LoanProduct(
                self.loan*(1 - split), rate=RATE_FIXED,
                num_years=NUM_YEARS,
                loan_years=FIXED_LOAN_YEARS,
                payment_freq='monthly', annual_fee=ANNUAL_FEE_FIXED,
            )
            fixed_amount_owing = (
                self.acct_fixed.payment_hist['amount_owing'].iloc[-1]
            )

            # Find period index where offset account interest payment = 0
            idx = np.where(
                self.acct_offset.payment_hist['interest'] <= 0)[0][0]
            zero_year = self.acct_offset.payment_hist['year'].iloc[idx]
            zero_year_rel = zero_year - FIXED_LOAN_YEARS
            zero_month_rel = round(zero_year_rel * 12)

            # Put remaining balance into offset account
            self.acct_remaining = LoanOffset(
                fixed_amount_owing, rate=RATE_VARIABLE,
                offset0=0, offset_periodic=SURPLUS_MTH,
                offset_first_idx=zero_month_rel,
                num_years=self.remaining_years,
                loan_years=self.remaining_years,
                payment_freq='monthly', annual_fee=0,
            )

            interest_paid = self._store_last_val(
                interest_paid, 'interest_paid', split)
            fees_paid = self._store_last_val(
                fees_paid, 'fees_paid', split)

        total_paid = list(np.array(interest_paid) + np.array(fees_paid))
        total_paid, total_paid_long = SplitRatioSim.change_to_df(
            total_paid, 'total_paid')

        # Reset `offset_split_pct` to original non-summed values
        total_paid['offset_split_pct'] /= 2
        total_paid_long['offset_split_pct'] /= 2

        # Calculate minimum interest split ratio
        total_paid_min = total_paid['total'].min()
        idx = total_paid['total'].idxmin()
        split_best = total_paid.loc[idx, 'offset_split_pct']

        print(f'Gross Price: ${self.gross_price}')
        print(f'Loan amount: ${self.loan}')
        print(f'Best offset split: {split_best}%')
        print(f'Best offset amount: ${self.loan * split_best / 100}')
        print(f'Best fixed amount: ${self.loan * (1 - split_best / 100)}')
        print(f'Total interest + fees: ${total_paid_min}')

        SplitRatioSim.save_plot(
            total_paid_long, 'total_paid', x_opt=split_best,
            text_opt=None,
            y_opt=pd.Series({
                'Gross price': self.gross_price,
                'Loan amount': self.loan,
                'Offset amount': self.loan * split_best / 100,
                'Fixed amount': self.loan * (1 - split_best / 100),
                'Interest + fees*': total_paid_min,
            }),
        )

    def _store_last_val(self, store_ls, colname, split):
        '''Store last value / final (payment) for offset/fix/remaining accounts
        '''
        offset_val = self.acct_offset.payment_hist[colname].iloc[-1]
        fixed_val = self.acct_fixed.payment_hist[colname].iloc[-1]
        remaining_val = self.acct_remaining.payment_hist[colname].iloc[-1]

        store_ls.append([
            split * 100,
            offset_val,
            fixed_val + remaining_val,
            offset_val + fixed_val + remaining_val,
        ])
        return store_ls

    @staticmethod
    def change_to_df(ls, colname):
        df = pd.DataFrame(
            ls,
            columns=[
                'offset_split_pct',
                'offset',
                'fixed',
                'total'
            ]
        ).round(2)

        df_long = pd.melt(
            df,
            id_vars=['offset_split_pct'],
            value_vars=['offset', 'fixed', 'total'],
            var_name=f'{colname}_component',
            value_name=f'{colname}_amount',
        )

        return df, df_long

    @staticmethod
    def save_plot(
        df, colname, x_opt=None, y_opt=None, text_opt=None, text_y_pos=None,
    ):
        f, ax = plt.subplots()
        sns.lineplot(
            x='offset_split_pct', y=f'{colname}_amount',
            hue=f'{colname}_component',
            data=df
        )
        ax.set_title(f'{colname} by Components')
        ax.grid()
        ax.legend(loc='lower right')
        # ax.legend(loc='upper center', bbox_to_anchor=(1.3, 1))

        # x optimal
        if x_opt is not None:
            ax.axvline(x=x_opt, c='lawngreen', ls='--', lw=3)

            if text_opt is None:
                text_opt = f'offset_split_pct*: {np.round(x_opt, 2)}'

            if y_opt is not None:
                for j in range(len(y_opt)):
                    text_opt += f'\n{y_opt.index[j]}: {y_opt[j].round(2)}'

            x_lims = ax.get_xlim()
            x_range = x_lims[1] - x_lims[0]
            x_delta = x_range * 0.05
            x_text_pos = x_opt + x_delta

            y_lims = ax.get_ylim()
            y_range = y_lims[1] - y_lims[0]
            y_delta = y_range * 0.05
            if text_y_pos is None:
                text_y_pos = (y_lims[0] + 0.8 * y_range) + y_delta

            ax.text(
                x=x_text_pos, y=text_y_pos, s=text_opt,
                fontsize=14, verticalalignment='top',
                bbox=dict(facecolor='yellow', alpha=0.3)
            )

        f.savefig(f'figures/{colname}.png')


def main():
    sim = SplitRatioSim()
    sim.simulate()


if __name__ == '__main__':
    main()
