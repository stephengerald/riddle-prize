# Architecture

## State machine

The creator commits answer criteria, players commit answers, the creator closes entries and reveals criteria, players reveal, and consensus judges each answer up to the winner cap.

The relevant roles are riddle creator and players. Write methods enforce role, phase, uniqueness, and bounded-storage rules before any state transition.

## Consensus boundary

Validators decide whether a revealed answer is semantically correct under creator-committed answer criteria, accepting equivalent wording rather than exact strings. The leader returns a small JSON schema; validators independently rerun the same decision function and accept only exact enum or bitmask values. Malformed model output raises a tagged model error and writes no decision.

## Deterministic boundary

Enrollment, authorization, commitments, counters, phase changes, caps, masks, and any score or credit arithmetic are deterministic contract logic. Only semantic interpretation of the stored evidence occurs inside `run_nondet_unsafe`.

## Off-chain boundary

Wallet custody, identity verification, indexing, notifications, private file storage, source authentication, money movement, legal process, and user-interface behavior are outside this repository. The contract records winners but holds no prize funds. Creator-selected criteria can be poor even though commitments prevent changing them after deployment.
