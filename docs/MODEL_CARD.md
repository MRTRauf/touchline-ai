# Model card — phase2-audit-v2

## Intended use and scientific status

The 2025/26 period was exposed in initial smoke development: no rerun, plan hash or refactor restores an untouched holdout. All revised 2025/26 results are changed-cohort, post-hoc checks. Upstream openplay_xg_v1 training cutoff is unresolved risk, not proof of leakage; local time splits cannot establish upstream availability. Historical eligibility is not verified by source-listed ages; age is neither a predictor nor an identity validator. Outcomes outside the observed five-league population are incomplete. Only descriptive screening and qualified retrospective conditional regression are supported; genuine prospective recruitment deployment is not.

Intended users: analysts/scouts examining transparent historical evidence and prediction errors. Non-users: autonomous recruiters, valuation/medical/contract systems and anyone asserting intrinsic talent, availability, injury risk, agency relationships, transfer probability or causal club effects. Descriptive screening remains primary. Data: **[openplay (Noah Bair)](https://github.com/nlbair/openplay)**, **CC BY 4.0**, original data-v0.1.0. Independent portfolio; not an official product of any football club, agency, or league.

## Target, scope and population

Target: `90*(non_penalty_goals+xa)/known next-season expanded minutes`. NPG is an observed event count; xA sums upstream modeled xG of linked assisted shots, not actual assists. Feature role AM/W or ST, >=900 feature minutes; outcome >=450 target minutes; all ages without age-based eligibility claims. Aggregate all covered club/league stints before per 90, one source-ID/person-season label. Target role/club/age never enters X or role eligibility. Missing outcomes remain missing, never zero. Unknown next-season destinations are not inferred.

Original source 2018/19–2025/26, eng/esp/ita/ger/fra, 427,078 stats rows, 21,490 person-seasons, 22,556 stints; 40 league-seasons, minimum 98.42% event coverage, 26 known missing matches, six issue matches. France 2019/20 was shortened. Known-issue/unknown-exposure person-seasons are excluded from primary features/labels, retained in audits; no repair of goals/events/minutes. Unflagged events are not thereby guaranteed correct.

## Identity and stale ages

3223/3228 players with >=3 seasons have constant listed ages. Stale age cannot justify identity rejection. V2 checks repeated normalized full names, stat/lineup names, roster slots, same-team-match name collisions and multiple-team positive minutes on a date. Unresolved evidence quarantines that source ID cumulatively through the observed season; later flags never rewrite past rows. Distinct IDs are never joined by name. Same-name collisions across different rosters remain audit warnings. V2 detected 0 uncertain person-seasons and 166 same-name-other-ID person-season warnings. No independent registry/birthdate proof exists: an undetectable source-ID reuse with identical name/context remains a limitation. No ages were reconstructed.

Before/after eligibility (policy fixed before inspecting revised accuracy; not adjusted to match target counts):

| cohort | linked_valid_pairs | latest_features | latest_labels |
| --- | --- | --- | --- |
| reviewed_v1 | 2692 | 477 | 362 |
| revised_v2 | 2773 | 524 | 391 |


## Features, fitting and temporal controls

22 predictors: 16 event rates, expanded minutes, stint count, adjacent prior-season minutes/rate, feature-season role and dominant league. No age/ID/future club/target minutes/target role/Phase 1 score. Missing historical lags use train-fitted median imputation with indicators; numeric scaling and category encoding are inside each fitted sklearn Pipeline. Eight eligible older origins inherited untrustworthy prior-season lags during intermediate QA: flagged/unknown-exposure/ambiguous prior values are now masked, with lag_source_quality_warning retained. This source-quality correction changed no outcomes, cohort criteria, feature allowlist or tuning grid; the intermediate v2 snapshot was preserved. No outcome imputation or full-dataset normalization.

Expanding validation targets 2021/2122/2223/2324; each train label precedes that validation. Each historical parameter uses only earlier validation folds, first registered candidate on first fold. Final parameters selected on those four past validation periods only: {'ridge': 100.0, 'boosting': 30.0, 'shrinkage': 0.5}. Final train targets <=2324: 2010 rows; calibration 2425: 372; post-hoc 2526 observed labels: 391. Every displayed historical fold has predictions for all eligible feature records, not only future survivors. The earliest 1819-origin/1920-target pairs supply initial training labels; no prediction is claimed for that initial block without earlier training data:

| split | season | target_season | all_candidates | observed |
| --- | --- | --- | --- | --- |
| calibration | 2324 | 2425 | 527 | 372 |
| test | 2425 | 2526 | 524 | 391 |
| validation | 1920 | 2021 | 523 | 423 |
| validation | 2021 | 2122 | 539 | 414 |
| validation | 2122 | 2223 | 521 | 399 |
| validation | 2223 | 2324 | 528 | 384 |


Ridge alpha 1/10/100; boosting L2=10/30, 120 iterations, learning_rate .05, 15 leaves, minimum leaf size 30, no random early stopping; seed 42, CPU 2 threads. These original settings were not changed to improve 2526. Mean and persistence baselines are supplemented by `train_role_mean+w*(current_rate-train_role_mean)`, w∈{0,.25,.5,.75,1}, selected from past validation only. Simplicity preference permits shrinkage if within 1% of ML validation MAE. Complexity is not credited for all improvement over noisy unshrunk persistence. Smoke uses earlier pseudo-periods only, separately stored and never treated as scientific final scores.

## Original versus revised post-hoc numerical evidence

Different populations: cross-version changes are not a controlled measure of software improvement. Reviewed-v1 metrics remain in their original directories; the added v1 shrinkage row is explicitly post-hoc and independently recomputed (tiny float32/64 differences from reviewer rounding possible). Errors are rate units per90, not percentages of talent.

| cohort | model | n | mae | rmse | spearman |
| --- | --- | --- | --- | --- | --- |
| reviewed_v1_fixed | role_mean | 362 | 0.135109841 | 0.172774448 | 0.278483122 |
| reviewed_v1_fixed | persistence | 362 | 0.141378828 | 0.183720929 | 0.453171860 |
| reviewed_v1_fixed | ridge | 362 | 0.112690886 | 0.145095393 | 0.540033399 |
| reviewed_v1_fixed | boosting | 362 | 0.117463992 | 0.149629252 | 0.513464582 |
| reviewed_v1_fixed_added_comparator_post_hoc | shrinkage | 362 | 0.121478946 | 0.154101587 | 0.485441475 |
| revised_v2_changed_cohort_post_hoc | role_mean | 391 | 0.133196011 | 0.170413775 | 0.277730358 |
| revised_v2_changed_cohort_post_hoc | persistence | 391 | 0.140658918 | 0.183016814 | 0.448245051 |
| revised_v2_changed_cohort_post_hoc | shrinkage | 391 | 0.120564797 | 0.153122323 | 0.479433044 |
| revised_v2_changed_cohort_post_hoc | ridge | 391 | 0.111879434 | 0.144490004 | 0.532709271 |
| revised_v2_changed_cohort_post_hoc | boosting | 391 | 0.115676342 | 0.146855280 | 0.509946520 |


Selected-model paired gains, positive = baseline MAE minus selected-model MAE, 500 player-cluster bootstrap draws:

| baseline | gain | low | high |
| --- | --- | --- | --- |
| role_mean | 0.021316577 | 0.013032708 | 0.030536770 |
| persistence | 0.028779484 | 0.021607493 | 0.036494682 |
| shrinkage | 0.008685363 | 0.004110543 | 0.013002814 |


The incremental benefit versus shrinkage is substantially smaller than versus persistence. Bootstrap intervals condition on fixed models and observed outcomes; they omit identity/source errors, missing outcomes, model-selection/development uncertainty and potential upstream temporal leakage.

All five models, chronological folds and calibration/post-hoc period:

| split | target_season | model | n_train | train_players | n_validation | n_test | unique_players | mae | rmse | median_ae | r2 | spearman | interval_coverage | interval_width |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| validation | 2021 | role_mean | 390 | 390 | 423 | 0 | 423 | 0.147394235 | 0.193463841 | 0.123246819 | 0.062318618 | 0.259076045 | — | — |
| validation | 2021 | persistence | 390 | 390 | 423 | 0 | 423 | 0.143365368 | 0.185601125 | 0.118997753 | 0.136987890 | 0.483899859 | — | — |
| validation | 2122 | role_mean | 813 | 536 | 414 | 0 | 414 | 0.147984667 | 0.184925867 | 0.127356298 | 0.050885816 | 0.226227024 | — | — |
| validation | 2122 | persistence | 813 | 536 | 414 | 0 | 414 | 0.137416018 | 0.178420938 | 0.112902679 | 0.116483278 | 0.545769476 | — | — |
| validation | 2223 | role_mean | 1227 | 668 | 399 | 0 | 399 | 0.139643993 | 0.175708281 | 0.118411332 | 0.021223230 | 0.184854306 | — | — |
| validation | 2223 | persistence | 1227 | 668 | 399 | 0 | 399 | 0.141071123 | 0.177580166 | 0.120440573 | 0.000257602 | 0.452670873 | — | — |
| validation | 2324 | role_mean | 1626 | 765 | 384 | 0 | 384 | 0.141961559 | 0.181539280 | 0.112206474 | 0.048970242 | 0.246200514 | — | — |
| validation | 2324 | persistence | 1626 | 765 | 384 | 0 | 384 | 0.134893454 | 0.174834815 | 0.106327713 | 0.117918472 | 0.487789071 | — | — |
| validation | 2021 | shrinkage | 390 | 390 | 423 | 0 | 423 | 0.147394235 | 0.193463841 | 0.123246819 | 0.062318618 | 0.259076045 | — | — |
| validation | 2021 | ridge | 390 | 390 | 423 | 0 | 423 | 0.124623536 | 0.165719370 | 0.098186515 | 0.311978152 | 0.552757225 | — | — |
| validation | 2021 | boosting | 390 | 390 | 423 | 0 | 423 | 0.123073459 | 0.163500970 | 0.090555595 | 0.330275246 | 0.563064631 | — | — |
| validation | 2122 | shrinkage | 813 | 536 | 414 | 0 | 414 | 0.125921050 | 0.157671826 | 0.105370238 | 0.310028214 | 0.551422830 | — | — |
| validation | 2122 | ridge | 813 | 536 | 414 | 0 | 414 | 0.118454073 | 0.152608971 | 0.097098301 | 0.353626915 | 0.583878582 | — | — |
| validation | 2122 | boosting | 813 | 536 | 414 | 0 | 414 | 0.124870684 | 0.159700310 | 0.104304642 | 0.292160724 | 0.534863065 | — | — |
| validation | 2223 | shrinkage | 1227 | 668 | 399 | 0 | 399 | 0.127922484 | 0.155694301 | 0.115009397 | 0.231498658 | 0.466504893 | — | — |
| validation | 2223 | ridge | 1227 | 668 | 399 | 0 | 399 | 0.122356072 | 0.152116303 | 0.106448551 | 0.266414532 | 0.506341482 | — | — |
| validation | 2223 | boosting | 1227 | 668 | 399 | 0 | 399 | 0.123605718 | 0.154354723 | 0.114794150 | 0.244665985 | 0.465290928 | — | — |
| validation | 2324 | shrinkage | 1626 | 765 | 384 | 0 | 384 | 0.122559118 | 0.158397986 | 0.095009781 | 0.275977270 | 0.508607499 | — | — |
| validation | 2324 | ridge | 1626 | 765 | 384 | 0 | 384 | 0.120234616 | 0.156979004 | 0.095212929 | 0.288891245 | 0.526131277 | — | — |
| validation | 2324 | boosting | 1626 | 765 | 384 | 0 | 384 | 0.126088718 | 0.163321030 | 0.105412615 | 0.230272307 | 0.476520167 | — | — |
| calibration | 2425 | role_mean | 2010 | 874 | 372 | 0 | 372 | 0.145044694 | 0.191479960 | 0.122733139 | 0.041612641 | 0.239238893 | 0.903225806 | 0.616306238 |
| calibration | 2425 | persistence | 2010 | 874 | 372 | 0 | 372 | 0.145233850 | 0.187231867 | 0.116688430 | 0.083665670 | 0.516880103 | 0.903225806 | 0.586021536 |
| calibration | 2425 | shrinkage | 2010 | 874 | 372 | 0 | 372 | 0.127232777 | 0.167002239 | 0.102241829 | 0.270980732 | 0.521010296 | 0.903225806 | 0.517944871 |
| calibration | 2425 | ridge | 2010 | 874 | 372 | 0 | 372 | 0.116350704 | 0.156207484 | 0.091797957 | 0.362180059 | 0.605384355 | 0.903225806 | 0.480029726 |
| calibration | 2425 | boosting | 2010 | 874 | 372 | 0 | 372 | 0.120137514 | 0.161186071 | 0.093973253 | 0.320875436 | 0.582666200 | 0.903225806 | 0.507366749 |
| test | 2526 | role_mean | 2010 | 874 | 0 | 391 | 391 | 0.133196011 | 0.170413775 | 0.114026472 | 0.070550105 | 0.277730358 | 0.938618926 | 0.616306238 |
| test | 2526 | persistence | 2010 | 874 | 0 | 391 | 391 | 0.140658918 | 0.183016814 | 0.115304321 | -0.072009339 | 0.448245051 | 0.905370844 | 0.587962056 |
| test | 2526 | shrinkage | 2010 | 874 | 0 | 391 | 391 | 0.120564797 | 0.153122323 | 0.100721210 | 0.249598647 | 0.479433044 | 0.915601023 | 0.517956965 |
| test | 2526 | ridge | 2010 | 874 | 0 | 391 | 391 | 0.111879434 | 0.144490004 | 0.089066651 | 0.331821967 | 0.532709271 | 0.890025575 | 0.480015153 |
| test | 2526 | boosting | 2010 | 874 | 0 | 391 | 391 | 0.115676342 | 0.146855280 | 0.092419178 | 0.309766997 | 0.509946520 | 0.910485934 | 0.507085231 |


## Empirical uncertainty and missing outcomes

Nominal 90% bands use the finite-sample absolute calibration-residual quantile with lower truncation 0. Calibration labels are not fitted by the final estimator. They are exploratory descriptions, not reliable individual probabilities or exchangeability guarantees. V2 calibration/test share 243 players (reviewed v1 shared 231). Average coverage hides role differences; per-role counts/coverage:

| model | role | n | coverage | mean_width | nominal | guarantee |
| --- | --- | --- | --- | --- | --- | --- |
| role_mean | AM/W | 264 | 0.965909091 | 0.616306238 | 0.900000000 | False |
| role_mean | ST | 127 | 0.881889764 | 0.616306238 | 0.900000000 | False |
| persistence | AM/W | 264 | 0.924242424 | 0.579991538 | 0.900000000 | False |
| persistence | ST | 127 | 0.866141732 | 0.604530690 | 0.900000000 | False |
| shrinkage | AM/W | 264 | 0.931818182 | 0.517187266 | 0.900000000 | False |
| shrinkage | ST | 127 | 0.881889764 | 0.519556969 | 0.900000000 | False |
| ridge | AM/W | 264 | 0.905303030 | 0.478589325 | 0.900000000 | False |
| ridge | ST | 127 | 0.858267717 | 0.482979079 | 0.900000000 | False |
| boosting | AM/W | 264 | 0.931818182 | 0.504848206 | 0.900000000 | False |
| boosting | ST | 127 | 0.866141732 | 0.511735424 | 0.900000000 | False |


Reviewed v1 Ridge: AM/W 90.98% (n=244), ST 86.44% (n=118), overall 89.50%; this does not establish uniform 90% coverage. Earlier rolling folds have no independent calibration block, so their bands are explicitly unavailable. Small subgroup metrics n<30 are suppressed.

Current outcome states, 391/524=74.62% usable:

| reason | n |
| --- | --- |
| observed_eligible | 391 |
| absent_unknown_destination | 93 |
| observed_below_target_minutes | 34 |
| observed_excluded_quality | 3 |
| squad_only_or_unusable | 3 |


Observed versus missing prior-feature distributions:

| target_season | observed | n | mean_prior_minutes | mean_prior_rate | multi_stint_share |
| --- | --- | --- | --- | --- | --- |
| 1920 | False | 122 | 1686.204918033 | 0.286049000 | 0.049180328 |
| 1920 | True | 390 | 2096.125641026 | 0.406013400 | 0.066666667 |
| 2021 | False | 100 | 1615.860000000 | 0.304393000 | 0.060000000 |
| 2021 | True | 423 | 1980.825059102 | 0.398300620 | 0.066193853 |
| 2122 | False | 125 | 1587.952000000 | 0.289744900 | 0.088000000 |
| 2122 | True | 414 | 2014.442028986 | 0.392796520 | 0.050724638 |
| 2223 | False | 122 | 1591.573770492 | 0.274846940 | 0.049180328 |
| 2223 | True | 399 | 2002.588972431 | 0.401053760 | 0.102756892 |
| 2324 | False | 144 | 1633.048611111 | 0.305437240 | 0.090277778 |
| 2324 | True | 384 | 2008.729166667 | 0.385807480 | 0.117187500 |
| 2425 | False | 155 | 1698.922580645 | 0.313544780 | 0.083870968 |
| 2425 | True | 372 | 2027.064516129 | 0.406075400 | 0.088709677 |
| 2526 | False | 133 | 1612.706766917 | 0.305315800 | 0.090225564 |
| 2526 | True | 391 | 1998.322250639 | 0.401629100 | 0.071611253 |


Reviewed v1 observed 362/477=75.9%, mean prior minutes ~2001 versus ~1603 missing/unusable. Revised flow above replaces none of that historical evidence. Role/league/exposure/transfer breakdowns:

| dimension | group | model | n | suppressed | mae | rmse | median_ae | r2 | spearman | spearman_warning |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| role | AM/W | role_mean | 264 | False | 0.124777979 | 0.160485309 | 0.107411116 | -0.018680211 | — | undefined_small_or_constant |
| role | ST | role_mean | 127 | False | 0.150694913 | 0.189394250 | 0.132966399 | -0.000434973 | — | undefined_small_or_constant |
| comp | eng | role_mean | 94 | False | 0.116873831 | 0.146258763 | 0.099634901 | 0.006836580 | 0.141531622 | — |
| comp | esp | role_mean | 93 | False | 0.128785424 | 0.163361644 | 0.108843014 | 0.162557802 | 0.492685437 | — |
| comp | fra | role_mean | 59 | False | 0.136066190 | 0.182101032 | 0.100585371 | 0.062660935 | 0.266258952 | — |
| comp | ger | role_mean | 67 | False | 0.149261555 | 0.198083839 | 0.132128954 | 0.006934141 | 0.162736968 | — |
| comp | ita | role_mean | 78 | False | 0.142154184 | 0.170853387 | 0.126835696 | -0.085545227 | 0.208040629 | — |
| age_group | historical_age_unavailable | role_mean | 391 | False | 0.133196011 | 0.170413775 | 0.114026472 | 0.070550105 | 0.277730358 | — |
| exposure_bucket | 900-1799 | role_mean | 167 | False | 0.125216394 | 0.153672844 | 0.114369676 | -0.010713717 | 0.226935119 | — |
| exposure_bucket | 1800-2699 | role_mean | 151 | False | 0.140540918 | 0.185167344 | 0.122749269 | 0.093081486 | 0.331646921 | — |
| exposure_bucket | 2700+ | role_mean | 73 | False | 0.136257862 | 0.174931815 | 0.108435318 | 0.076423971 | 0.272878280 | — |
| multi_stint | multiple | role_mean | 28 | True | — | — | — | — | — | — |
| multi_stint | single | role_mean | 363 | False | 0.132922611 | 0.170913702 | 0.114026472 | 0.072088902 | 0.278730756 | — |
| role | AM/W | persistence | 264 | False | 0.130665607 | 0.166367799 | 0.111832924 | -0.094727041 | 0.433842261 | — |
| role | ST | persistence | 127 | False | 0.161432415 | 0.213511119 | 0.126547575 | -0.271441188 | 0.342543120 | — |
| comp | eng | persistence | 94 | False | 0.138096282 | 0.176591844 | 0.118443191 | -0.447832113 | 0.356124697 | — |
| comp | esp | persistence | 93 | False | 0.126159905 | 0.170731137 | 0.108187675 | 0.085296969 | 0.544761422 | — |
| comp | fra | persistence | 59 | False | 0.154576997 | 0.209115005 | 0.113210529 | -0.236067805 | 0.445178258 | — |
| comp | ger | persistence | 67 | False | 0.157016203 | 0.191398794 | 0.128763080 | 0.072832161 | 0.452031287 | — |
| comp | ita | persistence | 78 | False | 0.136456242 | 0.176137938 | 0.109572239 | -0.153736276 | 0.345312915 | — |
| age_group | historical_age_unavailable | persistence | 391 | False | 0.140658918 | 0.183016814 | 0.115304321 | -0.072009339 | 0.448245051 | — |
| exposure_bucket | 900-1799 | persistence | 167 | False | 0.150203074 | 0.197281648 | 0.124501139 | -0.665740245 | 0.280986220 | — |
| exposure_bucket | 1800-2699 | persistence | 151 | False | 0.136108068 | 0.172975184 | 0.110603005 | 0.208579899 | 0.545162077 | — |
| exposure_bucket | 2700+ | persistence | 73 | False | 0.128238429 | 0.168757530 | 0.106797755 | 0.140469352 | 0.529896335 | — |
| multi_stint | multiple | persistence | 28 | True | — | — | — | — | — | — |
| multi_stint | single | persistence | 363 | False | 0.141788641 | 0.183822694 | 0.116408795 | -0.073373481 | 0.447454103 | — |
| role | AM/W | shrinkage | 264 | False | 0.110773983 | 0.139559291 | 0.089950781 | 0.229655805 | 0.433842261 | — |
| role | ST | shrinkage | 127 | False | 0.140917356 | 0.178040212 | 0.119195014 | 0.115920153 | 0.342543120 | — |
| comp | eng | shrinkage | 94 | False | 0.115089035 | 0.143537715 | 0.103000231 | 0.043447122 | 0.365675685 | — |
| comp | esp | shrinkage | 93 | False | 0.109236327 | 0.140648726 | 0.092779800 | 0.379236377 | 0.601280177 | — |
| comp | fra | shrinkage | 59 | False | 0.124710901 | 0.164029519 | 0.087676004 | 0.239470743 | 0.495558153 | — |
| comp | ger | shrinkage | 67 | False | 0.134398127 | 0.168603309 | 0.116373241 | 0.280530890 | 0.456700455 | — |
| comp | ita | shrinkage | 78 | False | 0.125652183 | 0.156036233 | 0.105414446 | 0.094576741 | 0.383730194 | — |
| age_group | historical_age_unavailable | shrinkage | 391 | False | 0.120564797 | 0.153122323 | 0.100721210 | 0.249598647 | 0.479433044 | — |
| exposure_bucket | 900-1799 | shrinkage | 167 | False | 0.123279165 | 0.155177935 | 0.103294984 | -0.030608791 | 0.320846259 | — |
| exposure_bucket | 1800-2699 | shrinkage | 151 | False | 0.118853374 | 0.152836897 | 0.100524724 | 0.382131724 | 0.586754967 | — |
| exposure_bucket | 2700+ | shrinkage | 73 | False | 0.117895282 | 0.148920392 | 0.092285484 | 0.330665223 | 0.535634950 | — |
| multi_stint | multiple | shrinkage | 28 | True | — | — | — | — | — | — |
| multi_stint | single | shrinkage | 363 | False | 0.120719541 | 0.153595146 | 0.100822195 | 0.250610532 | 0.478987612 | — |
| role | AM/W | ridge | 264 | False | 0.103485559 | 0.131414734 | 0.084276709 | 0.316945397 | 0.522921952 | — |
| role | ST | ridge | 127 | False | 0.129328118 | 0.168453188 | 0.105098299 | 0.208567728 | 0.401586520 | — |
| comp | eng | ridge | 94 | False | 0.118722340 | 0.144185208 | 0.098255678 | 0.034797718 | 0.423819673 | — |
| comp | esp | ridge | 93 | False | 0.099503109 | 0.131183727 | 0.068128058 | 0.459974108 | 0.641640058 | — |
| comp | fra | ridge | 59 | False | 0.121495500 | 0.167793370 | 0.080309746 | 0.204167824 | 0.498012858 | — |
| comp | ger | ridge | 67 | False | 0.114302103 | 0.145876481 | 0.097124915 | 0.461419627 | 0.542621119 | — |
| comp | ita | ridge | 78 | False | 0.109034540 | 0.139666060 | 0.085480076 | 0.274591740 | 0.508542091 | — |
| age_group | historical_age_unavailable | ridge | 391 | False | 0.111879434 | 0.144490004 | 0.089066651 | 0.331821967 | 0.532709271 | — |
| exposure_bucket | 900-1799 | ridge | 167 | False | 0.112052819 | 0.148216752 | 0.088060769 | 0.059782165 | 0.387005679 | — |
| exposure_bucket | 1800-2699 | ridge | 151 | False | 0.114825407 | 0.144078984 | 0.097330838 | 0.450913519 | 0.613154409 | — |
| exposure_bucket | 2700+ | ridge | 73 | False | 0.105389060 | 0.136481527 | 0.082829066 | 0.437810419 | 0.629705048 | — |
| multi_stint | multiple | ridge | 28 | True | — | — | — | — | — | — |
| multi_stint | single | ridge | 363 | False | 0.113357670 | 0.145955011 | 0.091650368 | 0.323308648 | 0.524209342 | — |
| role | AM/W | boosting | 264 | False | 0.108516070 | 0.136613354 | 0.090488740 | 0.261834720 | 0.498370171 | — |
| role | ST | boosting | 127 | False | 0.130560689 | 0.166137312 | 0.098932683 | 0.230179199 | 0.409507405 | — |
| comp | eng | boosting | 94 | False | 0.116473747 | 0.142274312 | 0.102837894 | 0.060211965 | 0.438023336 | — |
| comp | esp | boosting | 93 | False | 0.105962151 | 0.139687140 | 0.078992399 | 0.387695428 | 0.571379547 | — |
| comp | fra | boosting | 59 | False | 0.121728267 | 0.163125663 | 0.093748537 | 0.247829177 | 0.470660432 | — |
| comp | ger | boosting | 67 | False | 0.125239439 | 0.151813684 | 0.117278579 | 0.416686801 | 0.538390933 | — |
| comp | ita | boosting | 78 | False | 0.113505480 | 0.143264071 | 0.097523285 | 0.236735063 | 0.493215645 | — |
| age_group | historical_age_unavailable | boosting | 391 | False | 0.115676342 | 0.146855280 | 0.092419178 | 0.309766997 | 0.509946520 | — |
| exposure_bucket | 900-1799 | boosting | 167 | False | 0.115150764 | 0.148633699 | 0.089026023 | 0.054484885 | 0.353656714 | — |
| exposure_bucket | 1800-2699 | boosting | 151 | False | 0.116474633 | 0.146550005 | 0.096113887 | 0.431917838 | 0.595047055 | — |
| exposure_bucket | 2700+ | boosting | 73 | False | 0.115227435 | 0.143351206 | 0.092419178 | 0.379791452 | 0.602616315 | — |
| multi_stint | multiple | boosting | 28 | True | — | — | — | — | — | — |
| multi_stint | single | boosting | 363 | False | 0.117235184 | 0.148283777 | 0.095125035 | 0.301542662 | 0.501648026 | — |


Frozen-model exposure/tail/stint sensitivity, never used to tune 2526:

| setting | model | n | mae | rmse | median_ae | r2 | spearman | spearman_warning |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| all_primary | role_mean | 391 | 0.133196011 | 0.170413775 | 0.114026472 | 0.070550105 | 0.277730358 | — |
| all_primary | persistence | 391 | 0.140658918 | 0.183016814 | 0.115304321 | -0.072009339 | 0.448245051 | — |
| all_primary | shrinkage | 391 | 0.120564797 | 0.153122323 | 0.100721210 | 0.249598647 | 0.479433044 | — |
| all_primary | ridge | 391 | 0.111879434 | 0.144490004 | 0.089066651 | 0.331821967 | 0.532709271 | — |
| all_primary | boosting | 391 | 0.115676342 | 0.146855280 | 0.092419178 | 0.309766997 | 0.509946520 | — |
| higher_exposure | role_mean | 201 | 0.136256254 | 0.179536934 | 0.108435318 | 0.080699252 | 0.309478719 | — |
| higher_exposure | persistence | 201 | 0.128391834 | 0.166066463 | 0.103591457 | 0.213472568 | 0.537826215 | — |
| higher_exposure | shrinkage | 201 | 0.114701767 | 0.147189357 | 0.093645781 | 0.382121873 | 0.565894784 | — |
| higher_exposure | ridge | 201 | 0.107203510 | 0.134635246 | 0.088136495 | 0.483027386 | 0.624756909 | — |
| higher_exposure | boosting | 201 | 0.111214533 | 0.139539310 | 0.092419178 | 0.444680216 | 0.598452786 | — |
| without_top_5pct_prior_output | role_mean | 371 | 0.125569281 | 0.157151837 | 0.108435318 | 0.043324729 | 0.261917942 | — |
| without_top_5pct_prior_output | persistence | 371 | 0.133124815 | 0.171166177 | 0.110603005 | -0.134910279 | 0.379484510 | — |
| without_top_5pct_prior_output | shrinkage | 371 | 0.117720246 | 0.148740710 | 0.098423421 | 0.142991112 | 0.415013266 | — |
| without_top_5pct_prior_output | ridge | 371 | 0.109276192 | 0.140567077 | 0.087887552 | 0.234592249 | 0.475884588 | — |
| without_top_5pct_prior_output | boosting | 371 | 0.112021439 | 0.142318402 | 0.091874466 | 0.215401010 | 0.454051469 | — |
| single_stint_only | role_mean | 363 | 0.132922611 | 0.170913702 | 0.114026472 | 0.072088902 | 0.278730756 | — |
| single_stint_only | persistence | 363 | 0.141788641 | 0.183822694 | 0.116408795 | -0.073373481 | 0.447454103 | — |
| single_stint_only | shrinkage | 363 | 0.120719541 | 0.153595146 | 0.100822195 | 0.250610532 | 0.478987612 | — |
| single_stint_only | ridge | 363 | 0.113357670 | 0.145955011 | 0.091650368 | 0.323308648 | 0.524209342 | — |
| single_stint_only | boosting | 363 | 0.117235184 | 0.148283777 | 0.095125035 | 0.301542662 | 0.501648026 | — |


## Explanations, UI and provenance

Every row carries fold_id, parameter and training_target_cutoff. Exact fitted fold pipelines/preprocessors are retained locally in estimators.joblib, with matching standardized Ridge coefficient and retrospective out-of-fit permutation tables. The page filters explanations by exact fold/model and suppresses unavailable explanations. The displayed family is selected retrospectively across registered validation folds; exact earlier-fit views are not an as-of deployment simulation. Correlation/proxies prevent causal interpretations. Numeric coefficients are standardized associations; category terms are offsets, not development recommendations.

Before each cache lookup, verify model/data manifests and every consumed report/data table (including pairs and coverage). Content identities key the cache; another post-read verification detects changes during loading. Warm-cache tampering fails. No model pickle is deserialized by Streamlit. Original reviewed artifacts are inventoried and immutable; see reports/audit_remediation/original_inventory.json and docs/archive/phase2_reviewed.

Data manifest SHA256 `cc0e7f46b65991596ae6aec3498c9b25d6a3df33aa1c5fedbc5cbe8fa61a84bd`; model manifestSHA256 `d603a23c89817ddc88f3f238b5b867716e018f9b871297d34a19767aef694f95`; estimatorSHA256 `8972108b11551a5adfe3dabbf149e35e63421f60a4dbc0d135e21d4d55f8961f`. Source/checksum/config/code/environment/command details remain in linked manifests. Source files are original openplay distributions, not synthetic production fallbacks; artifacts/models/reports stay local and ignored. Own-code license is not inferred from CC BY4.0.

## Deployment restrictions and fairness

Do not use as operational recruitment, valuation, verified age eligibility or private circumstance inference. Coverage selects men's top-five-league participants; missing outcomes/survival, league strength, possession, team/opponent context, roles and exposure remain confounded. No protected attributes or nationality/ethnicity are inferred. A held-out label threshold selects participation, not latent ability. An independent locked replication/future season and upstream xG/age provenance are future work, never retroactively manufactured. Human handoff requires video, role/tactics/context, sample integrity and properly sourced contract/availability information. No push/merge/deployment without approval.
