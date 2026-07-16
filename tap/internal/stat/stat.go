// Package stat holds the small, self-contained statistics tap needs: the
// Mann-Whitney U test (the dissertation's chosen significance test — simple,
// non-parametric, widely accepted) and the Benjamini-Hochberg correction for the
// many pairwise comparisons. Implemented directly to keep tap dependency-free.
package stat

import (
	"math"
	"sort"
)

// MannWhitneyU returns the U statistic and the two-sided p-value for the null
// hypothesis that x and y come from the same distribution. It uses the normal
// approximation with tie and continuity corrections, which is standard for the
// sample sizes here (tens of repeated executions). Empty inputs yield p=1.
func MannWhitneyU(x, y []float64) (u, p float64) {
	n1, n2 := len(x), len(y)
	if n1 == 0 || n2 == 0 {
		return 0, 1
	}

	type item struct {
		v   float64
		grp int
	}
	all := make([]item, 0, n1+n2)
	for _, v := range x {
		all = append(all, item{v, 0})
	}
	for _, v := range y {
		all = append(all, item{v, 1})
	}
	sort.Slice(all, func(i, j int) bool { return all[i].v < all[j].v })

	// Average ranks for ties (ranks are 1-based).
	ranks := make([]float64, len(all))
	var tieSum float64
	for i := 0; i < len(all); {
		j := i
		for j+1 < len(all) && all[j+1].v == all[i].v {
			j++
		}
		avg := float64(i+j+2) / 2.0
		for k := i; k <= j; k++ {
			ranks[k] = avg
		}
		t := float64(j - i + 1)
		tieSum += t*t*t - t
		i = j + 1
	}

	var r1 float64
	for k := range all {
		if all[k].grp == 0 {
			r1 += ranks[k]
		}
	}
	u1 := r1 - float64(n1*(n1+1))/2
	u2 := float64(n1*n2) - u1
	u = math.Min(u1, u2)

	N := float64(n1 + n2)
	meanU := float64(n1*n2) / 2
	sigma := math.Sqrt(float64(n1*n2) / 12.0 * ((N + 1) - tieSum/(N*(N-1))))
	if sigma == 0 {
		return u, 1
	}
	z := (math.Abs(u-meanU) - 0.5) / sigma // continuity correction
	if z < 0 {
		z = 0
	}
	p = math.Erfc(z / math.Sqrt2) // two-sided
	return u, p
}

// BenjaminiHochberg returns FDR-adjusted p-values, preserving input order.
func BenjaminiHochberg(pvals []float64) []float64 {
	m := len(pvals)
	if m == 0 {
		return nil
	}
	idx := make([]int, m)
	for i := range idx {
		idx[i] = i
	}
	sort.Slice(idx, func(a, b int) bool { return pvals[idx[a]] < pvals[idx[b]] })

	adj := make([]float64, m)
	prev := 1.0
	for k := m - 1; k >= 0; k-- {
		i := idx[k]
		val := pvals[i] * float64(m) / float64(k+1)
		if val > prev {
			val = prev
		}
		if val > 1 {
			val = 1
		}
		adj[i] = val
		prev = val
	}
	return adj
}

// Median returns the median of xs (does not mutate xs). Empty -> 0.
func Median(xs []float64) float64 {
	n := len(xs)
	if n == 0 {
		return 0
	}
	s := append([]float64(nil), xs...)
	sort.Float64s(s)
	if n%2 == 1 {
		return s[n/2]
	}
	return (s[n/2-1] + s[n/2]) / 2
}
