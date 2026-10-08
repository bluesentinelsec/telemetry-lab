# Dissertation Reframe: Why Emission Still Matters When Detections Are Robust

Historical working notes preserved during integration. These framing arguments and early numerical claims are not the authoritative experiment scope or confirmed results; use the versioned qualification records and study protocols for those.

Second-opinion notes on impact, proposal/defense risk, and how to frame the substrate → telemetry → detection work when shipped rules mostly do not flip.

---

## The trap you’re in

You’re evaluating the work with this scorecard:

| Finding | Score you give it |
|---|---|
| Telemetry changes a lot | Interesting lab fact |
| Detections usually don’t flip | Therefore emission doesn’t matter |
| One mechanism-keyed exception | Existence proof, feels thin |

That scorecard assumes the only research question worth asking is:

> Does substrate change whether the SOC gets an alert?

That is **one** operational question. Your study was designed (and your RQs already say this) to answer a different, prior question:

> Is telemetry a stable proxy for behavior across implementations?

Those are not the same. If you only value the first, a robust detection result feels like a null. If you value the second, a robust detection result is **information**, not failure — and the emission result is not a “so what.”

---

## Core claim (the result worth defending)

**Substrate massively changes telemetry emission, yet shipped behavioral rules almost never flip — except where rules key on substrate-variable mechanisms rather than substrate-invariant effects. That decoupling, and its boundary, is the result.**

You did not fail to find substrate→detection impact; you found that impact is rare, localized, and explained — and that emission and detection outcomes are largely decoupled under modern rule construction.

---

## Why “detections are the same” does **not** make emission irrelevant

### 1. Same alert ≠ same evidence, same validation, same science

Binary fire/no-fire is a **coarse** outcome. Shipped rules can fire on a small invariant subset while the rest of the telemetry (volume, sequences, symbols, init noise) still differs by 10–27×.

That still matters for:

- **Rule authoring:** which features are safe to key on (stable invariants) vs which are runtime artifacts (loader noise, `set_robust_list`, clone variants, etc.)
- **False-positive risk:** rules that *look* behavioral but are actually toolchain fingerprints
- **Validation claims:** “this ATT&CK technique is covered” when you only tested one language/runtime
- **Forensics / investigation:** same alert, different process tree, library load story, syscall narrative
- **Data cost / SNR:** noisier substrates change storage, baselining, and analyst load even when the rule still fires
- **Future analytics:** sequence models, graph/provenance detectors, anomaly systems *will* see emission differences even when a hand-written Sigma rule does not

You measured the **input** to detection. Showing that the input moves while a particular class of detector stays put is a *relationship* result, not a non-result.

### 2. Robust detections are a finding about the field — not a waste of yours

A controlled study that says:

> Under effect-keyed rules and native-equivalent implementations, substrate rarely flips outcomes; under mechanism-keyed syscall rules, it can, and here is exactly why.

…is **more useful** than an untested worry (“runtimes might break everything”) or an untested assumption (“behavior ⇒ stable telemetry ⇒ stable detection”).

Detection engineering’s whole brand is “we detect *behavior*, not tools.” Your work is one of the few attempts to put an experimental boundary under that claim:

- **Where the brand holds:** effect-keyed rules, event-level sensors
- **Where it cracks:** mechanism-keyed predicates on substrate-variable intermediates (Go I/O model vs C `dup2`)

That is impact on **theory + practice**, not a consolation prize.

### 3. Adversary emulation impact is *not* lessened — it is refined

Your gloom version:

> Emulation impact is lessened if detections don’t flip.

The accurate version:

> Emulation impact changes from “language choice breaks detection” to “language choice changes what you are actually testing.”

Purple teams and Atomic/Caldera-style harnesses still need this, because:

| Emulation question | Your result |
|---|---|
| Will a different runtime evade our effect-keyed rules? | Usually **no** — transfer is safer than folklore suggests |
| Is validation against one Go binary “representative behavior”? | **Telemetry-wise, no** — emission is not interchangeable |
| Are we overfitting coverage maps to one toolchain? | **Risk remains** for mechanism-keyed / low-level rules |
| Which harness language for realistic *telemetry* of cloud-native malware? | Now empirically grounded, not taste |

“Detections don’t flip” **increases** confidence that single-language purple teaming is OK *for a defined class of rules*. That is operationally valuable. “Everything is fine always” would be false; “everything is broken always” would also be false. You found the middle with a mechanism. That is what defenses need.

If emulation only mattered when alerts flip, half of detection validation literature would be meaningless. Emulation is also about **telemetry fidelity, coverage honesty, and not mistaking implementation for TTP**.

### 4. The real primary impact (not stealth)

Stealth/noise ranking is real but **secondary**, and leading with it weakens a defense-oriented dissertation.

**Primary impact (what matters if detections are robust):**

1. **Foundational measurement for detection engineering**
   First controlled isolation of substrate as IV with functional equivalence held fixed. The field has been building on an unmeasured assumption.

2. **Feature hygiene for rule authors**
   Stable vs implementation-dependent telemetry is directly actionable: “detect the effect, not the runtime.”

3. **Boundary condition on behavioral detection theory**
   ATT&CK/Pyramid treat telemetry as behavior proxy; you show the proxy is **noisy** but many shipped analytics are **robust to that noise** — until they key on mechanism.

4. **Validation methodology**
   When multi-runtime testing is mandatory vs wasteful. Saves defender effort *and* catches the rare fragile class.

5. **Interpretation of research/datasets**
   Malware and emulation studies that mix languages without controlling substrate are confounded. You give a confound magnitude (volume, Jaccard, init fraction).

6. **Cloud-native realism**
   Static Go, musl/Alpine, mixed C++ ABIs are not exotic — they *are* the modern host. Measuring them is not toy work.

**Secondary impact:** offensive awareness of noisy vs quiet runtimes; mechanism-keyed blind spots.

If someone asks “so what if detections don’t flip?”, the short answer is:

> Then defenders still need to know *why* they don’t, *when* they might, and which telemetry features are behavior vs substrate — or they will keep overfitting, over-claiming coverage, and misreading research.

---

## Proposal vs dissertation: is this “enough”?

### Proposal defense

Proposals pass on **gap + design + feasibility + significance of the *stated* purpose**, not on a guaranteed dramatic outcome.

Your Ch1 purpose is already:

> measure how substrate influences **telemetry emitted** by functionally equivalent programs.

That is a complete, defensible dissertation aim. Detection flip is **motivation and optional downstream probe**, not the pass/fail criterion you owe the committee.

Risk at proposal: overselling “we will show detections break across languages.”
Fix: sell **measurement of the behavior↔telemetry assumption**, with detection outcomes as a *conditional secondary probe* (decoupling + boundary).

### Dissertation defense

Weak version (fails the “so what”):

> Telemetry differs. We found one Go reverse shell evasion. The end.

Strong version (defendable):

> We quantified substrate→telemetry under controlled equivalence. Emission variance is large and systematic. Shipped effect-keyed detections are largely robust to that variance; mechanism-keyed syscall rules are not, for explained runtime-I/O reasons. Therefore: (a) behavioral detection’s robustness is earned by feature choice, not by telemetry stability; (b) validation and rule design should treat substrate as a controlled factor where predicates are mechanism-like; (c) emission baselines define which features are Pyramid-stable.

Committees punish **overclaim** and **uncontrolled confounds** more often than they punish **nuanced results**. A clean causal chain with a precise boundary is not “weak”; a vague “substrate matters for security” with no mechanism is.

Your fear (“too weak to pass”) usually comes from comparing yourself to a different dissertation — one that *promises* product-breaking evasion rates. That study would be harder to ground honestly under your constraints (native-only, shipped rules, no LOLBins). Honesty + mechanism often **beats** flashy n=1 without theory.

---

## Reframe the emotional equation

You’re saying:

> I proved telemetry differs — so what, detections are the same. :(

Try this instead:

> I proved the **input** to detection changes a lot, and the **output** of modern effect-keyed rules mostly doesn’t. That means robustness is a property of **rule construction**, not of a stable world. I located where construction fails. That is the contribution.

Or even sharper for a defense slide:

> **Telemetry is not behavior. Detection can still work — when it refuses to pretend they are the same.**

That is not a small idea. It cuts against both naive ATT&CK operationalization and naive “just change language to evade.”

---

## What would make impact *feel* stronger without changing the science

You don’t need more dramatic flips. You need **stakeholders and decisions** in the write-up:

| Stakeholder | Decision your results inform |
|---|---|
| Detection engineer | Key on effect paths; multi-runtime test only mechanism-like predicates |
| Purple team | Single-language Atomic is OK for effect-keyed coverage; not a free pass for syscall/fd rules |
| Emulation platform authors | Document substrate; don’t treat one binary as the technique |
| Researchers | Control or report language/runtime when claiming behavioral ground truth |
| Product vendors | “Behavioral” claims need invariant feature evidence, not one harness language |

Add **one** soft detection metric if you can (evidence volume / field completeness when the rule fires). That answers “same detection, different quality” without requiring more evasions — and undercuts the “so what, same alert” line with data.

---

## Direct answers to the “so what?” spiral

**“What about my research matters if detection outcomes are robust?”**
It matters because robustness was **unproven**, is **conditional**, and rests on **which telemetry features rules use** — and you are measuring those features. Robustness without that map is luck; with your map it is engineering.

**“I proved emissions differ — so what?”**
Because detection, emulation, research, and baselining all consume emissions. Same alert on different evidence is not “nothing happened.” And the field’s core abstraction (behavior → telemetry → detection) is only as strong as the middle term.

**“Only value is which runtime is noisier (stealth)?”**
No. That is the **narrowest** use. The stronger uses are invariant feature selection, validation methodology, confound control, and the decoupling/boundary result.

**“Seems weak.”**
It seems weak only if the only acceptable impact is **alert flips**. That is an attacker-centric scoreboard. Your dissertation is (and should stay) **detection-engineering science**: how observation works. On that scoreboard, emission + decoupling + boundary is adequate — if you **own that framing** in the proposal and never apologize for not being a catalog of evasions.

---

## Practical advice for proposal and self-evaluation

1. **Stop using “detection flip rate” as self-worth for the dissertation.** Align self-evaluation with the actual RQs.
2. **Lead significance with:** assumptions of behavioral detection; feature hygiene; validation methodology; decoupling.
3. **Position reverse shell as boundary evidence**, not the whole impact story.
4. **Say out loud in proposal:** a robust detection result is still a result; a precise null with mechanism is stronger than a vague positive.
5. **Optional polish:** one soft metric + effect/mechanism rule taxonomy so “same fire” is clearly not “same everything.”

---

## Closing

You did not spend years proving a trivia fact. You measured the middle of the detection stack and found that **modern rules often ignore the variance you measured** — which is both good news for defenders and a warning about where they still key on the wrong layer. That is impact. It is quieter than “everything is broken,” and that is why it is more likely to be true — and still worth a dissertation.
