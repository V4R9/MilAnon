# ADR-002: Mapping Database

## Status
Accepted — 2026-03-23

## Context
MilAnon needs persistent storage for entity-to-placeholder mappings that survive across sessions. The same person ("Müller") must always map to `[PERSON_007]` whether processed today or in 6 months. The database must also store reference data (Swiss municipalities, military unit patterns).

## Options Considered

### Option A: SQLite
- **Pro:** Zero configuration, single file, Python stdlib support (`sqlite3`), excellent for single-user local apps, portable, inspectable with any SQLite client. Handles 100K+ entities easily.
- **Con:** No concurrent write access (not relevant — single-user CLI).

### Option B: JSON files
- **Pro:** Human-readable, no driver needed, trivial to implement.
- **Con:** No query capability, no indexing, poor performance at scale, no ACID transactions, corruption risk on crash during write.

### Option C: PostgreSQL / MySQL
- **Pro:** Full RDBMS, concurrent access, network-capable.
- **Con:** Massive overkill for a local single-user tool. Requires running a server. Violates the "all local, zero configuration" principle.

### Option D: TinyDB (document store)
- **Pro:** Pure Python, JSON-based, simple API.
- **Con:** No SQL queries, limited indexing, poor performance with complex lookups across entity types.

## Decision
**SQLite** via Python's built-in `sqlite3` module. Single database file stored locally (default: `~/.milanon/milanon.db`).

## Rationale
SQLite is purpose-built for this use case: a local, single-user application that needs persistent, queryable storage with ACID guarantees. The database is a single file that can be backed up by copying it. The normalized_value column with case-insensitive matching solves the "WEGMÜLLER" vs "Wegmüller" problem. Indexes on normalized values give us fast lookups even with thousands of entities.

## Consequences
- Database file at `~/.milanon/milanon.db` (configurable via CLI flag or env var).
- Schema migrations handled via version table + migration scripts.
- The `.db` file is in `.gitignore` — it contains PII and must never be committed.
- Repository pattern: `SqliteMappingRepository` implements `MappingRepository` protocol.
- User can inspect the database with any SQLite client (DB Browser for SQLite, `sqlite3` CLI).
