## v7.0.4 (Wallaby) - 2025-04-21

### Fixed
- Fixed references to 'project_journal' in various mode definitions and knowledge base files to align with the standard hidden folder structure (e.g., `.tasks/`, `.docs/`).

### Changed
- Updated the build workflow (`.workflows/WF-CREATE-ROO-CMD-BUILD-001.md`) to include a step for creating a GitHub release using the `gh` CLI and attaching the build artifact.