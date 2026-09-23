"""Numerical checks protecting repetition planning and cluster interpretation."""
import math
import unittest
from scipy.stats import t
from analyze import binomial, metrics, need, matrix_audit

class PlanningTests(unittest.TestCase):
    def test_required_count_is_minimum_satisfying_t_margin(self):
        for sd,margin in [(20,5),(1,5),(100,.5),(.3,.05)]:
            n=need(sd,margin)
            self.assertLessEqual(t.ppf(.975,n-1)*sd/math.sqrt(n),margin)
            if n>2:self.assertGreater(t.ppf(.975,n-2)*sd/math.sqrt(n-1),margin)

    def test_zero_observed_misses_still_has_uncertainty(self):
        result=binomial(60,60)
        self.assertAlmostEqual(result['opposite_upper_onesided'],.0487029133,places=9)
        self.assertLess(result['lower'],1)
        self.assertEqual(binomial(0,60)['opposite_upper_onesided'],result['opposite_upper_onesided'])

    def test_repeating_hosts_does_not_remove_host_uncertainty(self):
        a=metrics([90,100,110],['A','B','C'])
        b=metrics([90]*10+[100]*10+[110]*10,['A']*10+['B']*10+['C']*10)
        self.assertAlmostEqual(a['host_mean_ci95_half'],b['host_mean_ci95_half'])
        self.assertLess(b['ci95_half'],a['ci95_half'])
        self.assertEqual(b['within_host_sd'],0)
        self.assertGreater(b['between_host_sd'],0)

    def test_matrix_audit_does_not_hide_duplicate_or_missing_attempts(self):
        row=dict(os='linux',case='empty',config='linux-c-musl',host='A',repetition=1)
        audit=matrix_audit([row,row],[('linux','empty','linux-c-musl')])
        self.assertEqual(audit['expected_attempts'],30)
        self.assertEqual(len(audit['missing']),29)
        self.assertEqual(audit['duplicates'][0]['count'],2)
        self.assertFalse(audit['unexpected'])

    def test_power_and_tighter_precision_require_more_runs(self):
        self.assertGreater(need(20,5,power=.9),need(20,5))
        self.assertGreater(need(20,2.5),need(20,5))
        self.assertIsNone(need(20,0))

if __name__=='__main__':unittest.main()
