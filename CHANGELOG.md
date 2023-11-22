# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2023-11-21

### Added
- Offical release of XAgent Container Images on DockerHub, now you can just download and play XAgent, see our dockerhub [page](https://hub.docker.com/u/xagentteam) for more information.
- Localhost models [XAgentLlama-7B-preview](https://huggingface.co/XAgentTeam/XAgentLlama-7B-preview), [XAgentLlama-34B-preview](https://huggingface.co/XAgentTeam/XAgentLLaMa-34B-preview) developped for XAgent is now available on HuggingFace, click [here](https://huggingface.co/collections/XAgentTeam/xagentllm-655ae4091c419bb072940e74) to learn more.
- **XAgentGen** is released to enhance the usability and stability of Localhost models for XAgent. Check out the [XAgentGen](XAgentGen/README.md) for more details.
- **WebUI** is updated! Now you can browse files in workspace! **History replay** is also available now!
- Mysql integration for data management, including runtime interactive data and running records.
- Redis integration for managing the state of components during interaction processes.
- Docker and initialization for Mysql and Redis included within the project setup.
- New exception handling processes, with custom exception classes for different runtime errors.
- Session sharing feature, allowing users to share their sessions with the community.

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
