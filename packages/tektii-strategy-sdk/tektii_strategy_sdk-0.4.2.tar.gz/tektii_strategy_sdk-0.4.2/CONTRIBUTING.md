# Contributing to Tektii Strategy SDK

## Commit Message Format

This project uses [Conventional Commits](https://www.conventionalcommits.org/) for automated versioning and changelog generation.

### Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- **feat**: A new feature (triggers minor version bump)
- **fix**: A bug fix (triggers patch version bump)
- **perf**: Performance improvements (triggers patch version bump)
- **docs**: Documentation only changes
- **style**: Code style changes (formatting, missing semi-colons, etc)
- **refactor**: Code refactoring without changing functionality
- **test**: Adding or updating tests
- **chore**: Changes to build process or auxiliary tools

### Breaking Changes

For breaking changes, add `BREAKING CHANGE:` in the footer or append `!` after the type:

```
feat!: remove deprecated API endpoints

BREAKING CHANGE: The /api/v1/strategies endpoint has been removed.
Use /api/v2/strategies instead.
```

This triggers a major version bump.

### Examples

```bash
# Feature
feat(strategy): add support for stop-loss orders

# Bug fix
fix(server): handle connection timeout gracefully

# Breaking change
feat(api)!: change order structure in API response

# Performance improvement
perf(engine): optimize event processing loop
```

## Development Workflow

1. Fork the repository
2. Create a feature branch from `main`
3. Make your changes
4. Run quality checks: `make check`
5. Commit using conventional commit format
6. Push your branch and create a pull request

## Release Process

Releases are fully automated:

1. Merge PR to `main` with conventional commits
2. Semantic-release analyzes commits and determines version bump
3. Creates git tag and GitHub release
4. Publishes to PyPI automatically

No manual version updates needed!
