# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-01-XX

### Added
- Initial PyPI release
- Message content analysis with `check_message_contents` method
- Image processing utilities for Teams attachments
- Mixpanel telemetry integration with user identification
- HTTP client with connection pooling
- Activity class extensions for Bot Framework
- Comprehensive error handling and logging
- Async/await support throughout

### Features
- **Message Analysis**: Detect text, images, and files in Teams messages
- **Image Processing**: Download and base64 encode images from various attachment types
- **Telemetry Tracking**: Track bot usage, user interactions, and performance metrics
- **Connection Pooling**: Efficient HTTP client management for external APIs
- **User Identification**: Advanced user tracking with identity merging

### Dependencies
- mixpanel>=2.2.0
- httpx>=0.24.0
- botbuilder-core>=4.14.0
- pydantic>=1.8.0

## [Unreleased]

### Planned
- Enhanced error handling
- Additional telemetry events
- Performance optimizations
- Extended documentation