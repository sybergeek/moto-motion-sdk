# RaceXplained follower-conversion playbook

This is an editorial layer for future reels. It helps a viewer understand what RaceXplained consistently publishes and why a future explanation may be worth returning for. It does not predict followers, reach or virality, and it never overrides the retention playbook, approved narration or factual checks.

## Principles

- Deliver the hook, explanation and payoff before asking for a follow.
- A reel may intentionally have no explicit CTA.
- Prefer a specific, credible reason to return: recurring education, a real planned episode, an ongoing racing story, consistent niche expertise, or a published related reel.
- Keep the CTA to a natural closing beat; visual-only delivery is often enough.
- Do not use misleading cliffhangers, generic engagement bait, unsupported promises or long promotional outros.

## Planning checklist

Before approval, record the target audience, the reason to return, and an optional series. Choose a CTA strategy only if it adds value. For `next_episode`, reference a planned or scheduled content ID. For `related_reel`, reference a published reel ID. A disabled CTA has no placeholder text.

The SDK strategies are: no explicit CTA, subtle visual, direct follow, next episode, series, related reel and profile discovery. Their metadata includes placement, suggested duration, risks and validation rules. Initial 1–2 second durations are guidelines, not platform benchmarks.

## RaceXplained series

| ID | Series | Scope |
|---|---|---|
| `the_science` | The Science | Racing physics, motorcycle dynamics, aerodynamics, braking, traction, suspension and racing lines |
| `the_stories` | The Stories | Championship battles, rivalries, records, milestones and history |
| `the_breakdown` | The Breakdown | Incidents, overtaking, strategy and decisive technical moments |

Series identity should use existing branding and style tokens. Do not add a lengthy animated intro.

## Examples

Good: “Next: why MotoGP riders trail brake.” when the planned topic is recorded and the payoff is complete.

Good: “More F1 & MotoGP explained → RaceXplained” as a restrained visual closing cue.

Bad: “Follow now or you’ll miss the answer.” This withholds value and disrupts trust.

Bad: “Next week we reveal the secret…” when no planned content reference exists.

## Profile checklist

The SDK cannot edit Instagram profiles. Review manually: clear F1/MotoGP positioning, recognizable RaceXplained identity, concise value proposition, three representative pinned reels, consistent visual branding and organized related content. Do not report these as applied by the SDK.

## Measurement

Record views, reach, watch time, completion, retention, replays, likes, comments, shares, saves, reel-attributed profile visits and reel-attributed follows when an authorized source provides them. Use null for unavailable values. Keep net account follower change separate; it is not reel-attributed follows.

Derived diagnostics are only calculated when their denominators exist:

- `attributed_follows / views`
- `1000 * attributed_follows / views`
- `attributed_profile_visits / views`
- `attributed_follows / attributed_profile_visits`

The last is an approximate diagnostic ratio unless matched funnel data exists. Views are not unique viewers or reach. Record observation windows and delayed updates so non-comparable periods are not presented as a clean comparison.

## Experiments

Log the experiment ID, reel, CTA strategy, category, series, publication date, observation window, metrics and notes. Compare similar reels where possible. These records are observational unless actual randomized assignment occurred; note topic, date, exposure, hook, event and sample-size confounders. Never optimize follows at the expense of retention, credibility or relevance.

