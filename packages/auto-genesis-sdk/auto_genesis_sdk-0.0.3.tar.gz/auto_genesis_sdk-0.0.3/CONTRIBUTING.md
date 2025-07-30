# Contributing to Autonomize SDK Python

First off, thank you for considering contributing to Autonomize SDK! It's people like you that make Autonomize SDK such a great tool.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Development Process](#development-process)
  - [Branching Strategy](#branching-strategy)
  - [Branch Naming Convention](#branch-naming-convention)
- [Pull Request Process](#pull-request-process)
  - [Creating Pull Requests](#creating-pull-requests)
  - [PR Review Requirements](#pr-review-requirements)
- [Development Setup](#development-setup)
- [Commit Guidelines](#commit-guidelines)
- [Version Management with Commitizen](#version-management-with-commitizen)
- [Code Review Process](#code-review-process)

## Code of Conduct

This project and everyone participating in it is governed by our Code of Conduct. By participating, you are expected to uphold this code.

## Development Process

### Branching Strategy

We follow a trunk-based development strategy with `develop` as our main integration branch:

- All feature development should branch from the latest `develop`
- Protected branches:
  - `develop`: Main integration branch
  - `demo`: Stable code for demonstration
  - `main`: Production-ready code

### Branch Naming Convention

Use the following prefixes for your branches:

- `feature/`: For new features
  - Example: `feature/AUT-1234-telemetry-fast-api`
- `refactor/`: For code reorganization
  - Example: `refactor/AUT-1212-optimize-processing`
- `fix/`: For bug fixes
  - Example: `fix/AUT-5678-login-error`
- `hotfix/`: For urgent fixes
  - Example: `hotfix/AUT-9012-critical-bug`
- `epic/`: For related module sets
  - Example: `epic/AUT-3333-new-module`

## Pull Request Process

### Creating Pull Requests

1. **Size and Scope**
   - Keep PRs focused and small
   - Aim for 1:1 mapping with JIRA tickets
   - Avoid combining multiple unrelated changes

2. **PR Title Format**
   ```
   [JIRA-TICKET] Brief description
   Example: [AUT-1234] Implement telemetry metrics
   ```

3. **PR Description Template**
   ```markdown
   ## Description
   - Brief explanation of changes
   - Important context or design decisions
   - Known limitations or future considerations

   ## Testing
   - Description of tests performed
   - Steps to test the changes
   - Any testing prerequisites
   ```

4. **Code Quality Requirements**
   - Ensure all tests pass
   - Add new tests for new functionality
   - Follow project's code style (enforced by Black)
   - Update documentation as needed

### PR Review Requirements

- Minimum of two approvals required:
  - One peer review
  - One CodeOwner review
- All CI checks must pass
- No merge conflicts with the target branch

## Development Setup

1. Fork and clone the repository
   ```bash
   git clone https://github.com/autonomize-ai/autonomize-sdk-python.git
   ```

2. Set up your development environment
   ```bash
   cd autonomize-sdk-python
   poetry install
   ```

3. Set up pre-commit hooks
   ```bash
   poetry run pre-commit install
   ```

## Commit Guidelines

1. **Format**
   ```
   JIRA-TICKET: Brief description of changes

   - Detailed bullet points if needed
   ```

2. **Best Practices**
   - Start with JIRA ticket number
   - Use present tense ("Add feature" not "Added feature")
   - Keep first line under 50 characters
   - Multiple tickets: Use parentheses (AUT-123, AUT-124)

3. **Before Committing**
   - Run pre-commit hooks
   - Run tests locally
   - Squash related commits

## Version Management with Commitizen

We use Commitizen to manage versions and generate changelogs in this repository.

1. **Making Commits with Commitizen**
   - After making changes, stage your files:
     ```bash
     git add <files>
     ```
   - Use Commitizen to create your commit from the package directory:
     ```bash
     cz commit
     ```
   - Follow the interactive prompts to:
     - Select commit type
     - Enter scope
     - Write commit message
     - Provide a description
     - Specify BREAKING CHANGES (if any)
     - Reference issues

2. **Bumping Versions**
   - After your changes are complete, bump the version:
     ```bash
     cz bump
     ```
   - This will:
     - Update version in pyproject.toml
     - Create a git tag locally
     - Update the changelog

3. **Pushing Changes with Tags**
   - Push your branch including the version tags:
     ```bash
     git push origin feature/your-branch --tags
     ```

This approach ensures consistent versioning across the project and automatically generates comprehensive changelogs based on your commits.

## Code Review Process

### For Reviewers

1. **Response Time**
   - Communicate delays if unable to review promptly

2. **Review Focus Areas**
   - Functionality and correctness
   - Code style and readability
   - Performance considerations
   - Test coverage
   - Documentation completeness

3. **Feedback Guidelines**
   - Be specific and constructive
   - Explain reasoning behind suggestions
   - Focus on important issues over style preferences
   - Provide examples when possible

### For Authors

1. **Responding to Reviews**
   - Address all comments promptly
   - Explain your reasoning if you disagree
   - Notify reviewers when ready for re-review

2. **Maintaining PRs**
   - Keep branches up to date with develop
   - Resolve conflicts promptly
   - Don't let PRs become stale

## Questions?

Don't hesitate to reach out to the core team if you have any questions or need clarification on any part of the contribution process.
