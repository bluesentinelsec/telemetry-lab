package main

import (
	"os/exec"
	"testing"
)

func TestEmptyExitsZero(t *testing.T) {
	cmd := exec.Command("go", "run", ".")
	err := cmd.Run()
	if err != nil {
		t.Fatalf("expected exit code 0, got error: %v", err)
	}
}
