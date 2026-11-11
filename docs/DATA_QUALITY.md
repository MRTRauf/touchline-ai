# Final public data-quality audit

Read-only audit of the original release. The approved bundle, historical inputs, saved estimates and model metrics are not rewritten. No retraining or corrected rates are generated. The public QA overlay contains exclusion flags only.

## Every public numeric field

| Table / field | Negative | Missing | Minimum |
| --- | ---: | ---: | ---: |
| board.player_id | 0 | 0 | 2987 |
| board.team_id | 0 | 0 | 13 |
| board.minutes | 0 | 0 | 900 |
| board.screening_score | 0 | 121 | 17.7166496 |
| board.known_issue_matches | 0 | 0 | 0 |
| board.progressive_passes_p90 | 0 | 0 | 0 |
| board.passes_into_box_p90 | 0 | 0 | 0 |
| board.passes_final_third_p90 | 121 | 0 | -20.023407 |
| board.key_passes_p90 | 0 | 0 | 0 |
| board.xa_p90 | 0 | 0 | 0 |
| board.npxg_p90 | 0 | 0 | 0 |
| board.dribbles_completed_p90 | 0 | 0 | 0 |
| board.ball_recoveries_p90 | 0 | 0 | 0.347222222 |
| board.interceptions_p90 | 0 | 0 | 0 |
| board.tackles_won_p90 | 0 | 0 | 0 |
| board.crosses_completed_p90 | 0 | 0 | 0 |
| board.shots_p90 | 0 | 0 | 0 |
| board.non_penalty_goals_p90 | 0 | 0 | 0 |
| board.clearances_p90 | 0 | 0 | 0 |
| board.aerials_won_p90 | 0 | 0 | 0 |
| board.passes_completed_p90 | 826 | 0 | -35.6781354 |
| predictions.player_id | 0 | 0 | 6227 |
| predictions.minutes | 0 | 0 | 900 |
| predictions.current_rate | 0 | 0 | 0.0317323804 |
| predictions.role_mean | 0 | 0 | 0.341454059 |
| predictions.persistence | 0 | 0 | 0.0317323804 |
| predictions.shrinkage | 0 | 0 | 0.18659322 |
| predictions.ridge | 0 | 0 | 0.107561365 |
| predictions.ridge_low | 0 | 0 | 0 |
| predictions.ridge_high | 0 | 0 | 0.349282646 |
| predictions.target_rate | 0 | 133 | 0.0453620553 |
| metrics.n | 0 | 0 | 391 |
| metrics.mae | 0 | 0 | 0.111879434 |
| metrics.rmse | 0 | 0 | 0.144490004 |
| metrics.spearman | 0 | 0 | 0.277730358 |

The only negative stored fields are passes_final_third_p90 (121) and passes_completed_p90 (826). Stored minutes, goals/rates, xA/npxG, defensive rates, scores, forecasts and both bounds have no negatives. Counts of raw goals are not a public bundle field; raw source counts were checked below. 121 missing screens are goalkeepers, not zero-rated outfield players. 133 missing target rates are absent/unusable outcomes, never zero.

## Cause and valid/invalid classification

Nonnegative pass counts become invalid signed per-90 values because the preserved producer evaluates `90 * agg[count] / minutes` while the aggregated pass totals still have dtype int16. Multiplication wraps before division. The same bug also creates positive corrupted rates; simply masking negatives would miss them. This is a derived arithmetic defect, not a negative raw count or inferred source correction.

Checksum-verified original player-match source. All inspected production count/rate inputs below are nonnegative before aggregation.

| Raw field | Negative rows |
| --- | ---: |
| minutes_played | 0 |
| goals | 0 |
| progressive_passes | 0 |
| passes_into_box | 0 |
| passes_final_third | 0 |
| key_passes | 0 |
| xa | 0 |
| npxg | 0 |
| dribbles_completed | 0 |
| ball_recoveries | 0 |
| interceptions | 0 |
| tackles_won | 0 |
| crosses_completed | 0 |
| shots | 0 |
| non_penalty_goals | 0 |
| clearances | 0 |
| aerials_won | 0 |
| passes_completed | 0 |

Join/exposure: 1,652 unique four-part player/team/competition/season records matched one-to-one; minutes agree exactly. Raw player-match keys are unique. Source-flagged non-lineup/unknown minutes and zero-minute appearances are filtered using the existing producer policy; no join duplication or missing-minute imputation explains these negatives.

| Derived field | All corrupted | Negative subset | Positive corrupted |
| --- | ---: | ---: | ---: |
| passes_final_third_p90 | 124 | 121 | 3 |

| Player / ID | Team ID | Raw season count | Stored /90 |
| --- | ---: | ---: | ---: |
| Bryan Mbeumo / 353377 | 189 | 468 | -6.222694659 |
| Mohamed Salah / 108226 | 26 | 487 | -5.845946674 |
| Cole Palmer / 395692 | 15 | 540 | -4.792303339 |

| passes_completed_p90 | 1315 | 826 | 489 |

| Player / ID | Team ID | Raw season count | Stored /90 |
| --- | ---: | ---: | ---: |
| Bryan Mbeumo / 353377 | 189 | 872 | 3.439808663 |
| Mohamed Salah / 108226 | 26 | 892 | 3.970913008 |
| Cole Palmer / 395692 | 15 | 1140 | -8.056593096 |


## Presentation policy and sample effects

1315 distinct records have at least one corrupted rate (1,439 field observations). Mask those exact 124 final-third and 1,315 completed-pass values, including positive overflows, as unavailable. Do not replace them with recalculated values or zero. Retain the records for all other valid statistics.

Final-third passes enter the CM/DM reference pool; the frozen CM/DM score ordering cannot be defended merely by removing the 124 affected measurements. Suppress all 347 CM/DM scores in the new analytical views, without repairing saved scores. Completed passes are not used by any screening role. The remaining role scores are preserved.

Ranking eligibility before user filters: 1184 of 1,652 records; 347 CM/DM unavailable plus 121 unscored goalkeepers. Profile percentiles use finite metric-specific same-role/season pools with displayed sample sizes, independent of board filters. Similarity uses only complete valid role-feature records, retains the original exposure shrinkage/standardization/cosine algorithm, and filters displayed candidates after normalization.

## Signed analytical values

| Calculation | Negative count | Interpretation |
| --- | ---: | --- |
| Ridge minus later observed rate | 156 | Valid directional rate difference; not a count |

Examples: Robert Lewandowski (ID 29400): -0.079103; Danny Welbeck (ID 39308): -0.078687.

| Ridge minus current rate | 266 | Valid directional rate difference; not a count |

Examples: Dani Rodríguez (ID 6227): -0.037111; Cristhian Stuani (ID 24400): -0.124408.

| Ridge minus shrinkage | 312 | Valid directional rate difference; not a count |

Examples: Dani Rodríguez (ID 6227): -0.064749; Cristhian Stuani (ID 24400): -0.025187.

CB: 356 complete valid records; 31865 negative cosine pairs among 63184 unordered distinct-player pairs. Valid negative cosine means opposite standardized directions, not negative performance or probability.
Negative signed progressive_passes contributions: 30840 distinct-player pairs (valid directional terms).
Negative signed interceptions contributions: 31580 distinct-player pairs (valid directional terms).
Negative signed aerials_won contributions: 31427 distinct-player pairs (valid directional terms).
Negative signed ball_recoveries contributions: 30952 distinct-player pairs (valid directional terms).
Negative signed tackles_won contributions: 31198 distinct-player pairs (valid directional terms).
Example: Nathan Collins / Cristhian Mosquera: -0.168568. Signed feature contributions may likewise be negative and must not be clamped.

FB/WB: 292 complete valid records; 21301 negative cosine pairs among 42485 unordered distinct-player pairs. Valid negative cosine means opposite standardized directions, not negative performance or probability.
Negative signed progressive_passes contributions: 20691 distinct-player pairs (valid directional terms).
Negative signed passes_into_box contributions: 20955 distinct-player pairs (valid directional terms).
Negative signed xa contributions: 20691 distinct-player pairs (valid directional terms).
Negative signed ball_recoveries contributions: 21147 distinct-player pairs (valid directional terms).
Negative signed tackles_won contributions: 21171 distinct-player pairs (valid directional terms).
Negative signed dribbles_completed contributions: 20787 distinct-player pairs (valid directional terms).
Example: Milos Kerkez / Giovanni Di Lorenzo: -0.229486. Signed feature contributions may likewise be negative and must not be clamped.

CM/DM: 300 complete valid records; 22362 negative cosine pairs among 44849 unordered distinct-player pairs. Valid negative cosine means opposite standardized directions, not negative performance or probability.
Negative signed progressive_passes contributions: 22419 distinct-player pairs (valid directional terms).
Negative signed passes_final_third contributions: 22210 distinct-player pairs (valid directional terms).
Negative signed key_passes contributions: 21716 distinct-player pairs (valid directional terms).
Negative signed ball_recoveries contributions: 22474 distinct-player pairs (valid directional terms).
Negative signed interceptions contributions: 22451 distinct-player pairs (valid directional terms).
Negative signed xa contributions: 21599 distinct-player pairs (valid directional terms).
Example: Jesper Karlström / João Gomes: -0.138783. Signed feature contributions may likewise be negative and must not be clamped.

AM/W: 356 complete valid records; 31260 negative cosine pairs among 63189 unordered distinct-player pairs. Valid negative cosine means opposite standardized directions, not negative performance or probability.
Negative signed xa contributions: 31108 distinct-player pairs (valid directional terms).
Negative signed key_passes contributions: 30900 distinct-player pairs (valid directional terms).
Negative signed dribbles_completed contributions: 31284 distinct-player pairs (valid directional terms).
Negative signed passes_into_box contributions: 31108 distinct-player pairs (valid directional terms).
Negative signed npxg contributions: 30843 distinct-player pairs (valid directional terms).
Negative signed progressive_passes contributions: 30528 distinct-player pairs (valid directional terms).
Example: Bryan Mbeumo / Antoine Semenyo: -0.247033. Signed feature contributions may likewise be negative and must not be clamped.

ST: 180 complete valid records; 7981 negative cosine pairs among 16110 unordered distinct-player pairs. Valid negative cosine means opposite standardized directions, not negative performance or probability.
Negative signed npxg contributions: 7904 distinct-player pairs (valid directional terms).
Negative signed shots contributions: 7776 distinct-player pairs (valid directional terms).
Negative signed non_penalty_goals contributions: 7904 distinct-player pairs (valid directional terms).
Negative signed xa contributions: 7811 distinct-player pairs (valid directional terms).
Negative signed key_passes contributions: 7904 distinct-player pairs (valid directional terms).
Negative signed dribbles_completed contributions: 7776 distinct-player pairs (valid directional terms).
Example: Roberto Piccoli / Kylian Mbappé: -0.484635. Signed feature contributions may likewise be negative and must not be clamped.

Total valid-pool negative similarities: 114769/229817 distinct-player pairs. Positive similarity can also reflect shared low output. UI differences and forecast residuals preserve signs.

Percentiles are defined in [0,100] on finite valid values; no negative percentiles. Zero-vector cosine is undefined and excluded. The preserved source screen, ranges, forecasts and MAE/RMSE/Spearman table remain byte-identical. Spearman can in general be negative but none of the five saved metric values is negative. Negative forecast intervals, if ever supplied in a future reviewed release, must be labeled model ranges rather than silently clipped; this release has none.

## Biographical provenance

The approved public bundle has no verified age, date of birth or nationality. Cached lineups provide source-listed age only; methodology records 3,223/3,228 players with constant listed ages across at least three seasons. Neither cached lineups nor player-match schema contains nationality or birthdate. No reliably identity-matched licensed biography file is available. No name/club/country inference or scraping was used. Age-based and nationality-based ranking remain unavailable. Optional future contract: docs/BIOGRAPHY_ENRICHMENT.md.

## Boundaries

This audit diagnoses descriptive arithmetic using the local cached original release. It does not re-evaluate or retrain missing forecasting archives, modify historical model inputs, or establish prospective recruitment validity. Upstream xG historical provenance remains unresolved, 2025/26 was exposed, missing outcomes are selective, and historical age eligibility is unverified. openplay (Noah Bair), CC BY 4.0 attribution remains intact.
