# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2023-11-21

### Added

- Mysql integration for data management, including runtime interactive data and running records.
- Redis integration for managing the state of components during interaction processes.
- Docker and initialization for Mysql and Redis included within the project setup.
- New exception handling processes, with custom exception classes for different runtime errors.
- Session sharing feature, allowing users to share their sessions with the community.
- Tuna mirror of debian.([#206](https://github.com/OpenBMB/XAgent/issues/206)) 

### Changed

- Removed some global variables, now using `XAgent.core.XAgentCoreComponents` for better modularity and encapsulation.
- Overhauled the project structure of XAgentServer for improved organization and maintainability.

### Removed

- XAgentIO.
- Local file storage mode and its support mechanisms.

### Fixed

- Fix various bugs in `XAgentServer` as reported in project issues.

## [0.1.0] - 2023-10-16

- Initial setup and integration of the `Toolserver`, `XAgent`, `XAgentIO`, `XAgentServer`, and `XAgentWeb` components.
