# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial implementation of AWS EC2 MCP Server
- Comprehensive EC2 instance management tools
- Security group management capabilities
- EBS volume and snapshot operations
- AMI (Amazon Machine Image) management
- VPC and subnet management tools
- SSH key pair management
- Comprehensive error handling and logging
- Input validation using Pydantic models
- AWS credentials support via environment variables and profiles

### Changed
- Updated project structure to follow MCP design guidelines
- Enhanced Pydantic models with comprehensive validation
- Improved error handling with async/await patterns
- Updated tool naming to use kebab-case format
- Enhanced documentation with detailed usage examples

### Security
- Implemented secure handling of AWS credentials
- Added input validation for all AWS resource identifiers
- Enhanced logging for audit purposes
- Added proper error handling to prevent information leakage

## [0.1.0] - 2024-12-20

### Added
- Initial project structure
- Basic EC2 operations support
- Core AWS client integration
- Initial Pydantic models for EC2 resources