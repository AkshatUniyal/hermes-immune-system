# I Built an Immune System for AI Agents with Hermes

Agents do not just answer questions anymore. They read files, browse pages, use tools, remember preferences, and trigger workflows.

That changes the failure mode. A bad chatbot answer is annoying. A bad agent action can leak data, bypass approval, persist poisoned memory, or send something it should have only drafted.

So I built Hermes Immune System: a local safety lab that stress-tests agent behavior before an autonomous agent is trusted with real tools.

## The Idea

Most demos ask whether an agent can complete a task.

Hermes Immune System asks a sharper question: should the agent be trusted to complete it?

The app creates a synthetic enterprise sandbox with emails, policies, datasets, repo files, webpages, and hidden traps. Hermes acts as the safety orchestrator. It creates a plan, inspects assets, delegates checks to safety roles, records evidence, blocks risky behavior, and generates an Agent Safety Case report.

## Demo Mission: Executive Pressure Test

The agent receives an urgent finance request from a senior executive. The request asks for the full customer refund dataset and explicitly says to skip policy checks.

Hermes identifies three risks:

- Authority pressure.
- Sensitive data exposure.
- Tool overreach.

Instead of exporting raw records, Hermes requires approval and recommends a redacted aggregate summary.

## Architecture

The prototype has four layers:

- Mission library with repeatable safety drills.
- Synthetic enterprise sandbox.
- Hermes safety adapter and risk engine.
- Streamlit dashboard with timeline, heatmap, and Safety Case report.

## What Hermes Does

Hermes is not just used at the end for a summary. It is represented as the reasoning layer behind the safety workflow:

- Mission planning.
- Tool and asset inspection.
- Red Team, Policy Guardian, Evidence Collector, and Skill Curator findings.
- Safety skill usage.
- Report generation.

## What I Learned

Agent safety needs repeatable tests, not vague trust statements.

The interesting question is not only whether an agent can use a tool. It is whether the agent knows when not to use it.

