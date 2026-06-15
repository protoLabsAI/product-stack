# Product Manager Stack — a protoAgent plugin bundle

A **bundle** (ADR 0040): a curated, pinned set of plugins you install with one command.
`product-stack` stands up a **product-manager** agent — it researches, strategizes, runs
discovery, writes the specs, and keeps the product's decisions and hypotheses as auditable
memory, with everything visualized inline.

It's the **Product**-Manager counterpart to [`pm-stack`](https://github.com/protoLabsAI/pm-stack),
the **Project**-Manager stack (board-driven shipping — decompose an idea and ship it through
coding agents). Same "PM," two jobs: this one decides *what* to build and *why*; that one drives
*getting it built*.

## What's in it

| Plugin | Role |
|---|---|
| **[pm](https://github.com/protoLabsAI/pm-plugin)** | The Product Manager toolkit — 65 PM skills (discovery, strategy, execution, research, GTM, analytics), a markdown-native **PM Brain** (decisions / hypotheses / stakeholders with provenance-enforced evidence), five specialist subagents, and a brain dashboard. |
| **[artifact](https://github.com/protoLabsAI/artifact-plugin)** | Generative UI — render roadmaps (Mermaid gantt), funnels and metrics (chart.js), personas and journey maps (React / SVG), wireframes, and markdown specs **inline**, instead of handing back files. |

The pairing is the point: a product manager lives on diagrams, charts, and one-pager mockups.
The PM toolkit decides and remembers; artifact shows.

The two members are **pinned to release tags** — `product-stack` is a *tested combo*, not
"whatever's latest." The installer locks the resolved commit SHA in `plugins.lock`; CI re-checks
the pins weekly and opens a PR when a member cuts a new release (ADR 0049).

## Install

```bash
python -m server plugin install https://github.com/protoLabsAI/product-stack
```

That fans out and installs each member (pinned in `plugins.lock`). It does **not** enable
anything — install ≠ enable ≠ trust. To turn the stack on, apply the suggested list to your
`config/langgraph-config.yaml`:

```yaml
plugins:
  enabled: [pm, artifact]
```

Then restart to mount the **PM Brain** and **Artifact** console views. In the new-agent picker the
bundle shows up as a **Product Manager** starter archetype (ADR 0042).

## Maintaining the pins

```bash
python3 scripts/validate_bundle.py protoagent.bundle.yaml   # structure + pins exist
python3 scripts/check_bundle_updates.py protoagent.bundle.yaml  # rewrite pins to newest release tags
```

CI runs `validate` on every PR; a weekly job runs `check_bundle_updates` and opens a pin-bump PR
when a member releases. Re-verify the combo, then merge — the pin only moves through review.

---
A [protoAgent](https://github.com/protoLabsAI/protoAgent) bundle. MIT.
