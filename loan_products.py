import numpy as np
import pandas as pd


N_PERIOD = {
    'monthly': 12,
    'weekly': 52,
}


class LoanProduct:
    '''Standard compounding loan product'''

    def __init__(
        self, loan, rate, num_years=30, loan_years=None,
        payment_freq='monthly', annual_fee=0,
    ):
        self._loan = loan
        self._rate = rate
        self._num_years = num_years
        self._loan_years = loan_years if loan_years is not None else num_years
        self._payment_freq = payment_freq
        self._annual_fee = annual_fee
        self._n_period = N_PERIOD[self._payment_freq]
        self._n = self._n_period * self._num_years
        self._r = self._rate / 100 / self._n_period
        self.periodic_payment = self._calc_periodic_payment()

        self.total_fees = self._calc_total_fees()
        self.total_payment = self._calc_total_payment()
        self.interest_payment = self._calc_interest()
        self.payment_hist = self._calc_payment_hist()

    def _calc_periodic_payment(self):
        '''Calculate periodic payment given parameters; use:
        discount_factor = {[(1 + r)^n] - 1} / [r(1 + r)^n]
        '''
        compound = (1 + self._r) ** self._n
        discount_factor = (compound - 1) / self._r / compound
        return self._loan / discount_factor

    def _calc_total_fees(self):
        '''Total fees paid over `loan_years`
        '''
        return self._annual_fee * self._loan_years

    def _calc_total_payment(self):
        '''Total payment over all `num_years`
        '''
        return self.periodic_payment * self._n + self.total_fees

    def _calc_interest(self):
        '''Total interest paid over all `num_years`
        '''
        return self.total_payment - self.total_fees - self._loan

    def _calc_payment_hist(self) -> pd.DataFrame:
        '''Historical payments by period (in years)
        '''
        n_loan = self._n_period * self._loan_years
        df = pd.DataFrame(
            index=np.arange(n_loan),
            columns=[
                'year',
                'amount_paid',
                'amount_owing',
                'interest',
                'interest_paid',
                'fees_paid',
                'offset_total',
                '_periodic_payment',
                '_periodic_fee',
            ],
            dtype=float,
        )
        df['year'] = (df.index + 1) / self._n_period
        df['_periodic_payment'] = self.periodic_payment
        df['_periodic_fee'] = self._annual_fee / self._n_period
        df['interest'] = self.interest_payment / self._n

        df['amount_paid'] = df['_periodic_payment'].cumsum()
        df['interest_paid'] = df['interest'].cumsum()
        df['fees_paid'] = df['_periodic_fee'].cumsum()

        df['amount_owing'] = self._loan - df['amount_paid']
        df['offset_total'] = 0

        return df.drop(columns=['_periodic_payment', '_periodic_fee'])


class LoanOffset(LoanProduct):
    '''Loan with offset account / facility

    Args:
        offset_first_idx (int): period idx of first offset_periodic
        contribution
    '''

    def __init__(
        self, loan, rate,
        offset0, offset_periodic, offset_first_idx=0,
        num_years=30, loan_years=None,
        payment_freq='monthly', annual_fee=0,
    ):
        self._offset0 = offset0
        self.offset_periodic = offset_periodic
        self.offset_first_idx = offset_first_idx

        super().__init__(
            loan, rate, num_years, loan_years, payment_freq, annual_fee)

        self.payment_hist = self._calc_payment_hist()
        self.total_fees = self._calc_total_fees2()

    def _calc_total_fees2(self):
        return self._annual_fee * self.payment_hist['year'].iloc[-1]

    def _calc_amount_owing(self, amount_owing, offset_total, idx=0) -> dict:
        '''Recursive calculation of amount owing given fixed periodic offset
        contribution
        '''
        if idx >= self.offset_first_idx:
            offset_total += self.offset_periodic
        interest = np.max([(amount_owing - offset_total) * self._r, 0])
        amount_owing += (interest - self.periodic_payment)

        if amount_owing <= 1e-5:
            return {
                'amount_owing': [amount_owing],
                'interest': [interest],
                'offset_total': [offset_total],
            }
        else:
            tmp = self._calc_amount_owing(amount_owing, offset_total, idx + 1)
            return {
                'amount_owing': [amount_owing] + tmp['amount_owing'],
                'interest': [interest] + tmp['interest'],
                'offset_total': [offset_total] + tmp['offset_total'],
            }

    def _calc_payment_hist(self) -> pd.DataFrame:
        '''Historical payments by period (in years)
        '''
        n_loan = self._n_period * self._loan_years
        df = pd.DataFrame(
            index=np.arange(n_loan),
            columns=[
                'year',
                'amount_paid',
                'amount_owing',
                'interest',
                'interest_paid',
                'offset_total',
                'fees_paid',
                '_periodic_payment',
                '_periodic_fee',
            ],
            dtype=float,
        )
        df['year'] = (df.index + 1) / self._n_period
        df['_periodic_payment'] = self.periodic_payment
        df['_periodic_fee'] = self._annual_fee / self._n_period
        cols = ['amount_owing', 'interest', 'offset_total']
        df[cols] = pd.DataFrame(self._calc_amount_owing(
            self._loan, offset_total=self._offset0)
        )
        df['amount_paid'] = df['_periodic_payment'].cumsum()
        df['interest_paid'] = df['interest'].cumsum()
        df['fees_paid'] = df['_periodic_fee'].cumsum()

        return df.drop(columns=['_periodic_payment', '_periodic_fee']).dropna()
