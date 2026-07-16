package stat

import (
	"math"
	"testing"
)

func TestMannWhitneyIdentical(t *testing.T) {
	x := []float64{5, 5, 5, 5}
	y := []float64{5, 5, 5, 5}
	u, p := MannWhitneyU(x, y)
	if u != 8 { // n1*n2/2 = 8
		t.Errorf("U = %v, want 8", u)
	}
	if p < 0.99 {
		t.Errorf("identical samples p = %v, want ~1", p)
	}
}

func TestMannWhitneySeparated(t *testing.T) {
	// Fully separated groups -> U=0 and a small p.
	x := []float64{1, 2, 3, 4, 5}
	y := []float64{6, 7, 8, 9, 10}
	u, p := MannWhitneyU(x, y)
	if u != 0 {
		t.Errorf("U = %v, want 0", u)
	}
	if p > 0.05 {
		t.Errorf("separated samples p = %v, want < 0.05", p)
	}
}

func TestMannWhitneyKnown(t *testing.T) {
	// Only pair with x>y is (5,4), so U=1.
	x := []float64{1, 2, 3, 5}
	y := []float64{4, 6, 7, 8}
	u, _ := MannWhitneyU(x, y)
	if u != 1 {
		t.Errorf("U = %v, want 1", u)
	}
}

func TestBenjaminiHochberg(t *testing.T) {
	// Order preserved; monotonic; bounded by 1.
	in := []float64{0.01, 0.5, 0.001, 0.04}
	got := BenjaminiHochberg(in)
	if len(got) != 4 {
		t.Fatalf("len = %d", len(got))
	}
	for i, v := range got {
		if v < in[i]-1e-9 { // adjusted >= raw
			t.Errorf("adj[%d]=%v < raw=%v", i, v, in[i])
		}
		if v > 1 {
			t.Errorf("adj[%d]=%v > 1", i, v)
		}
	}
	// smallest raw p (0.001, rank1 of 4) -> 0.001*4/1 = 0.004
	if math.Abs(got[2]-0.004) > 1e-9 {
		t.Errorf("adj for 0.001 = %v, want 0.004", got[2])
	}
}

func TestMedian(t *testing.T) {
	if Median([]float64{3, 1, 2}) != 2 {
		t.Error("odd median")
	}
	if Median([]float64{4, 1, 2, 3}) != 2.5 {
		t.Error("even median")
	}
}
