# Product Manager — a protoAgent plugin bundle

A **bundle** (ADR 0040): a curated, pinned set of plugins you install with one command.
`product-archetype` stands up a **product-manager** agent — it researches, strategizes, runs
discovery, writes the specs, and keeps the product's decisions and hypotheses as auditable
memory, with everything visualized inline.

It's the **Product**-Manager counterpart to [`project-manager-archetype`](https://github.com/protoLabsAI/project-manager-archetype),
the **Project**-Manager archetype (board-driven shipping — decompose an idea and ship it through
coding agents). Same "PM," two jobs: this one decides *what* to build and *why*; that one drives
*getting it built*.

## What's in it

| Plugin | Role |
|---|---|
| **[pm](https://github.com/protoLabsAI/pm-plugin)** | The Product Manager toolkit — 65 PM skills (discovery, strategy, execution, research, GTM, analytics), a markdown-native **PM Brain** (decisions / hypotheses / stakeholders with provenance-enforced evidence), five specialist subagents, and a brain dashboard. |
| **[artifact](https://github.com/protoLabsAI/artifact-plugin)** | Generative UI — render roadmaps (Mermaid gantt), funnels and metrics (chart.js), personas and journey maps (React / SVG), wireframes, and markdown specs **inline**, instead of handing back files. |

The pairing is the point: a product manager lives on diagrams, charts, and one-pager mockups.
The PM toolkit decides and remembers; artifact shows.

The two members are **pinned to release tags** — `product-archetype` is a *tested combo*, not
"whatever's latest." The installer locks the resolved commit SHA in `plugins.lock`; CI re-checks
the pins weekly and opens a PR when a member cuts a new release (ADR 0049).

## Install

```bash
python -m server plugin install https://github.com/protoLabsAI/product-archetype
```

That fans out and installs each member (pinned in `plugins.lock`). It does **not** enable
anything — install ≠ enable ≠ trust. To turn the bundle on, apply the suggested list to your
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

## Pin-bump PR lifecycle (explicit-approval model, [#2645][issue-2645])

The scheduled `bump` job pushes to a single, stable branch — `bump-pins` — and keeps **at
most one** open pin-bump PR at a time. A later scheduled run that finds more bumps
force-pushes that same branch, updating the PR in place instead of piling up duplicates.
Treat `bump-pins` as bot-owned: it's rewritten wholesale every run, so hand edits to it
don't survive the next bump.

GitHub does **not** auto-start a `pull_request` workflow run for a PR opened with the
repository `GITHUB_TOKEN` — it's held `action_required` until someone with write access
clicks **Approve and run workflows** on the Actions tab (recursion-prevention; see
[GitHub's docs][gh-token-docs]). This repo has no GitHub App installation or PAT
provisioned to avoid that, so it deliberately runs the **explicit-approval model** instead:

- **Approving is a documented, one-click operator responsibility, not a bug.** Watch the
  repo's Actions tab (or PR notifications) for the pin-bump PR and approve its run so
  `validate` actually runs before merge (this bundle's CI job is named `validate`, not
  `verify` — see the `bundle` workflow, `.github/workflows/ci.yml`).
- **The `bump` job makes a stall visible instead of silent.** After pushing, it polls
  (bounded wait) for the run it should have queued. If that run comes back
  `action_required` — or never shows up at all, which is worse — the job **fails**,
  comments on the PR, and adds a `needs-approval` label. An unapproved pin-bump PR then
  shows up as a red weekly schedule, not a PR quietly rotting for weeks.
- **ADR 0049's invariant still holds either way:** `validate` still has to pass before
  merge — this only makes sure someone notices it needs to be *started*.

[issue-2645]: https://github.com/protoLabsAI/protoAgent/issues/2645
[gh-token-docs]: https://docs.github.com/en/actions/concepts/security/github_token#when-github_token-triggers-workflow-runs

---
A [protoAgent](https://github.com/protoLabsAI/protoAgent) bundle. MIT.
