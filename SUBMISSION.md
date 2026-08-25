# Submission: Riddle Prize

Project name: Riddle Prize

Repository: https://github.com/stephengerald/riddle-prize

StudioNet contract: https://explorer-studio.genlayer.com/address/0xd5e2249A5d181bBc7FF7c4A251aEB0Dd63E12616

Deployment transaction: https://explorer-studio.genlayer.com/tx/0x5f1178fb364c08afd0edd62142f0ef7c291e856a13ba986da5d5025b7ead8997

Intelligent transaction: https://explorer-studio.genlayer.com/tx/0x7a076f0953e32b399a1923af0c5cee159c57771db4f2e6264645180ef3aac049

Summary: Runs a bounded riddle contest with creator and player commit/reveal protection plus semantic answer judging.

Why it is GenLayer-native: Validators decide whether a revealed answer is semantically correct under creator-committed answer criteria, accepting equivalent wording rather than exact strings.

Evidence/source model: The riddle, revealed answer criteria, and player answer are the complete evidence set. No web or third-party source is collected.

Declared scope: Reusable, non-custodial prototype. The contract records winners but holds no prize funds. Creator-selected criteria can be poor even though commitments prevent changing them after deployment.

Review evidence: `AUDIT.md`, `SECURITY.md`, `SOURCE_POLICY.md`, and `deployments/studionet.json` bind the reviewed source hash to the public live result.
