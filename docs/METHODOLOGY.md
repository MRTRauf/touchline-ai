# Methodology and boundaries

**Retrospective descriptive screening** is the primary workflow. Forecast Lab is **qualified retrospective conditional regression**, not a demonstrated prospective recruitment service. No score or estimate represents latent talent, value, availability, injury risk, representation or causal club fit. Independent portfolio; independent project.

Data: **[openplay (Noah Bair)](https://github.com/nlbair/openplay)**, **CC BY 4.0**, original `data-v0.1.0`, package0.1.0. Counts and source dictionaries are inspected, cached and checksum-verified. Historical years are genuine observations, not copies or synthetic production examples. Event presence does not guarantee completeness; missing matches/source issue records remain auditable.

## Source time and age

Across at least three observed seasons, 3,223/3,228 players have constant listed ages. These source attributes cannot establish historical eligibility, and no birthdays or historical ages are reconstructed. Optional source-listed-age exploration defaults off and excludes unknown values only when enabled. Its exported warning explicitly states that historical eligibility is not verified. The stored legacy youth flag in the frozen Phase 1 snapshot is not exported or used as historical evidence.

Age is absent from forecast predictors **and identity rejection rules**. Source IDs link observations; names never merge IDs. Normalized full-name continuity, stats/lineup agreement, roster-slot consistency and incompatible same-team-match name/ID or same-date team appearances flag ambiguity. Quarantine flags are cumulative through the observed season, not imposed on earlier rows using later evidence. Same names on distinct IDs/rosters remain separate audit warnings. External identity verification remains unavailable; a source-ID reuse that evades these checks is still possible.

Every inspected historical match identifies `openplay_xg_v1`; its historical training cutoff is unresolved. Chronological local splitting cannot establish that upstream xG/xA were frozen at a historical decision date. Treat this as unresolved risk, not demonstrated leakage. The 2025/26 period was exposed during initial smoke development; no later refactor, hash or rerun restores an independent untouched comparison.

## Descriptive screen and comparables

The preserved Phase 1 analytical key is `(comp, season, player_id, team_id)`. Appearance keys add match_id; duplicates fail. Known expanded minutes include stoppage time, with 0–150 appearance and 1–6,000 season sanity bounds. Explicitly source-flagged unknown-minute appearances and zero-minute rows are excluded and counted; missing selected event metrics are not zero-filled. Per90 =90×sum(count)/sum(known expanded minutes). The descriptive screen requires900 minutes per team/league stint.

Starting positions map to CB, FB/WB, CM/DM, AM/W, ST, GK or Unknown; dominant broad role uses starting minutes, deterministic alphabetical ties. Substitute-only players remain Unknown. GK/Unknown are unscored. These are deployment proxies, not verified intrinsic roles.

Each role's feature weights are in src/features.py. For N eligible records in a season-role pool, percentile=100×(average rank−0.5)/N. Ties use their midpoint. Exposure weight=minutes/(minutes+900); each score contribution=feature weight×[50+exposure weight×(percentile−50)]. Contributions sum to a heuristic screening score, not validated confidence or future ability. Board filters do not change the reference pool. More defensive events can reflect lower possession, and correlated attacking rates can double-count output.

Similarity shrinks role features toward the minutes-weighted season-role mean, standardizes within that descriptive pool and computes cosine. It excludes every stint with the anchor's source ID, has no implicit feature imputation and rejects zero-vector comparisons. Positive signed terms can reflect shared low output; cosine can be negative and is not probability. Unsupported/small pools show explicit empty states.

## Longitudinal population and target

The separate v2 research covers2018/19–2025/26 in eng/esp/ita/ger/fra. Preserve all positive-minute stints before modeling exposure thresholds. Sum covered team/league stints to one person-season before recomputing rates. The categorical league predictor is the league of the largest observed team/league stint; it is not a league-strength adjustment. Source IDs, stints and broad roles remain auditable.

Primary target=90×(next-season non_penalty_goals+xa)/known next-season expanded minutes. NPG is an event outcome; xA is modeled shot-setup value, not actual assists. Feature-season AM/W/ST,>=900 feature minutes,>=450 target minutes; future role is not an inclusion condition. Missing destinations/participation are not inferred and absent outcomes never become zero. Known-issue/unknown-minute person-seasons and independently ambiguous IDs are excluded from primary eligibility, not silently repaired.

Observed, below-threshold, excluded-quality, squad-only/unusable and unknown-absence outcomes stay separate. Regression estimates apply conditional on observation. Missing-label cohorts have different prior exposure/output; no participation model or world-player extrapolation is implied.

## Chronology, baselines and explanations

Use train-only imputation/scaling/encoding inside pipelines. Allowlisted features exclude age, identifiers, future club/role/minutes and descriptive screening percentiles. Adjacent past lags stay missing when absent. Unique person/target-season keys and exact adjacent season mapping are required; no random row holdout.

Rolling validation targets2021/2122/2223/2324 use earlier training labels. Hyperparameters and shrinkage weights for a historical fold use only earlier validation folds. Final train labels<=2324; calibration2425; previously exposed2526 is a changed-cohort **post-hoc** comparison. Mean, persistence, validation-selected shrinkage, regularized Ridge and modest boosting are reported together. No2025/26 tuning, feature selection, accuracy-driven cohort adjustment or claim of an independent new holdout.

Historical predictions include all feature-eligible people, not just future survivors. Metrics use only observed valid labels. Every row records the exact fitted fold, parameter and training-label cutoff. Saved fold pipelines/preprocessing and matching coefficient/permutation tables support explanations; unavailable explanations are suppressed. Coefficients are standardized associations, not causal effects or training advice. See MODEL_CARD for actual metrics and configuration.

## Uncertainty and verification

Nominal90% empirical bands use absolute calibration residuals and lower clipping0. Report per-role counts/coverage; marginal coverage is not an individual guarantee. Repeated players between calibration/test and temporal drift undermine exchangeability. Player-cluster bootstrap gains condition on observed outcomes and fixed models, omitting source, identity and model-selection uncertainty. Small subgroup cells n<30 are suppressed.

Verify every consumed data/report artifact before cache lookup; content identities invalidate warm caches and post-read checks detect changes during loading. Models are not deserialized in Streamlit. The feasibility gate checks exact coverage scope, unique keys, trustworthy denominators, chronological mapping and consistent role/exposure/identity/quality/label eligibility.

Original reviewed v1 data/models/reports remain unchanged and separately inventoried. Revised eligibility and metrics use v2 paths and are labeled changed-cohort/post-hoc; their differences are not evidence that a software fix improved accuracy. See PHASE2_AUDIT_REMEDIATION, PHASE2_VALIDATION, the original protocol deviations and archived narratives. Private attributes remain absent. Real decisions still require video, tactical/league context, sample review and independently sourced availability information.
