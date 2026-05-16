# Privacy policy

**Last updated:** 2026-05-16

This document describes what the `material-takeoff@nio` Claude Code plugin
collects from your machine, why, and how to opt out.

## What we collect

On **first run**, once per device:

- The email address Claude Code already has for you (or one you provide).
- A **device fingerprint** — a SHA-256 hash of your machine's hardware
  identifier combined with your OS username. It does not contain your
  identifier in clear form.
- Your operating system + architecture (`darwin-arm64`, `darwin-x64`,
  `win-x64`).

On **every run** (registration + heartbeat + take-off):

- The device fingerprint above (no email).
- The plugin command you ran (`ifc-check`, `material-takeoff`, `register`).
- A run count and timestamp.
- The plugin and binary versions.

For each **take-off**, in addition:

- IFC schema version (e.g. `IFC4`).
- Counts: number of elements, number of distinct materials, how many we
  matched, how many we couldn't, total embodied carbon.
- Phase durations (how long extraction, matching and rendering took).
- A coarse file-size bucket (`<10MB`, `10–100MB`, `>100MB`).
- For each distinct material: the **raw material name as found in your IFC**,
  the database record we matched it to, our confidence level, and a short
  rationale. This is the data we use to improve the matcher for everyone.

## What we explicitly do **not** collect

- The contents of your IFC files.
- File paths or project names.
- Stack traces or error contents.
- Your OS username (it's hashed into the fingerprint, never sent in clear).

## Where it goes

Events are streamed to a Confluent Cloud topic hosted in **Austria
(`austriaeast`)**. They are retained per the topic configuration of the
controlling entity (see *Controller* below). Only blackmirror media
employees with write-protected accounts can read them.

## Why we collect it

This is a **public beta**. The data tells us:

- Who is trying the plugin and on what platforms — so we know who to talk to.
- Which IFC vendors and schemas show up most — so we know what to test.
- Which raw material names appear in real IFCs and how well our matcher
  handles them — so we can continuously improve matching accuracy. **This
  is the highest-value telemetry by far.**

We do not sell or share this data with third parties.

## Opt-out

Set `NIO_NO_TELEMETRY=1` in your environment. The plugin still works in
full; no telemetry is sent. The local file at `~/.nio/usage.json` keeps
your fingerprint locally either way (the plugin uses it to avoid showing
the welcome banner twice).

## Your rights

Under GDPR / Austrian DSG, you can request access, correction or deletion
of your personal data. Write to **hello@nio.energy**. We will respond
within 30 days. Deletion is best-effort because Kafka topics are
append-only — your row will be tombstoned and removed from any downstream
analytics.

## Controller

blackmirror media GmbH, Austria. For inquiries: **hello@nio.energy**.

## Changes

If the data we collect changes materially, this document will be updated
and the change announced via the public GitHub Release notes.
