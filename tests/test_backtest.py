import unittest
from zce_cup.backtest import Bar, Contract, backtest

C = Contract('DEMO', 10, 1, 2, 0.1, 1)
B = [Bar(f'2026-11-11T21:{i:02d}', p, p+2, p-2, p) for i,p in enumerate([100,110,120,115])]

class TestBacktest(unittest.TestCase):
    def test_next_bar_no_lookahead(self):
        r = backtest(B, [1,0,0,0], C)
        self.assertEqual(len(r.trades), 1)
        self.assertEqual(r.trades[0].entry, 111)
        self.assertEqual(r.trades[0].exit, 119)
        self.assertEqual(r.total_pnl, 76)
    def test_short(self):
        r = backtest(B, [-1,0,0,0], C)
        self.assertEqual(r.trades[0].entry, 109)
        self.assertEqual(r.trades[0].exit, 121)
        self.assertEqual(r.total_pnl, -124)
    def test_margin_blocks(self):
        r = backtest(B, [1,1,1,1], Contract('X',100000,1,0,0.5), 500000)
        self.assertFalse(r.trades)
    def test_bad_signals(self):
        with self.assertRaises(ValueError):
            backtest(B,[2,0,0,0],C)
    def test_bad_bars(self):
        with self.assertRaises(ValueError):
            Bar('x', 10, 9, 8, 10)
    def test_flat(self):
        r = backtest(B,[0]*4,C)
        self.assertEqual(r.total_pnl,0)
        self.assertEqual(r.max_drawdown_pct,0)

if __name__ == '__main__': unittest.main()
