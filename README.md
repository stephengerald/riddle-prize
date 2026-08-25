# Riddle Prize

Runs a bounded riddle contest with creator and player commit/reveal protection plus semantic answer judging.

## Why GenLayer

Validators decide whether a revealed answer is semantically correct under creator-committed answer criteria, accepting equivalent wording rather than exact strings.

## Reusable workflow

The creator commits answer criteria, players commit answers, the creator closes entries and reveals criteria, players reveal, and consensus judges each answer up to the winner cap. Constructor parameters create a new independent instance, so the code is reusable; state is not shared between deployments.

The contract is deliberately non-custodial. It records a decision, entitlement, score, or approval signal and never transfers GEN.

## Evidence boundary

The riddle, revealed answer criteria, and player answer are the complete evidence set. No web or third-party source is collected.

## Verify locally

```powershell
genvm-lint check contracts/riddle_prize.py
genvm-lint typecheck contracts/riddle_prize.py
pytest tests/direct -q
python tests/run_glsim.py --validators 5
```

With GLSim running in another terminal:

```powershell
gltest tests/integration/test_glsim_consensus.py --network localnet -q
```

The live smoke test requires fresh test-only keys in `GENLAYER_PRIVATE_KEY`, `GENLAYER_SECONDARY_PRIVATE_KEY`. Never commit a `.env` file or use a production wallet.

```powershell
gltest tests/integration/test_studionet_smoke.py --network studionet -s -q --default-wait-interval=6000 --default-wait-retries=240
```

Use the documented 6-second StudioNet polling interval to stay comfortably below public endpoint limits.

See `ARCHITECTURE.md`, `SOURCE_POLICY.md`, `SECURITY.md`, `AUDIT.md`, and `deployments/studionet.json` for the review boundary and exact public evidence.
