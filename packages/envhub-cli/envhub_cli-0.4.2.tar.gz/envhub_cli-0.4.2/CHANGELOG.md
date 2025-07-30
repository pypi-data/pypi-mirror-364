# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

[//]: # (## [Unreleased])

## [0.4.2] - 2023-07-25

### Fixed
- Fixed version update notification not showing when running `envhub --version`
  - The version check now runs synchronously when using the `--version` flag
  - Improved error handling for version checking

## [0.4.1] - 2023-07-25

### Added
- Added support for environment variable injection in production environments
- Enhanced compatibility with various cloud hosting platforms

### Changed
- Changed the mechanism for decrypting environment variables
    - Before this release, the decryption mechanism involved retrieving the encrypted data form cloud. 
    - Now, the decryption mechanism is based on the content of the .env file.
    - So, the user will have to pull from the project first before using the decrypt or any other command

## [0.3.6] - 2025-07-22

### Added

- Core functionality for secure environment variable management
- User authentication and authorization
- Environment variable encryption at rest
- Team collaboration features

[unreleased]: https://github.com/Okaymisba/EnvHub/compare/v0.4.1...HEAD
[0.4.2]: https://github.com/Okaymisba/EnvHub/releases/tag/v0.4.2
[0.4.1]: https://github.com/Okaymisba/EnvHub/releases/tag/v0.4.1
[0.3.6]: https://github.com/Okaymisba/EnvHub/releases/tag/v0.3.6
