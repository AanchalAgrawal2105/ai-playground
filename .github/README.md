# GitHub Automation & CI/CD

This directory contains all GitHub automation, CI/CD workflows, and repository configuration.

## Contents

### Workflows (`.github/workflows/`)

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| **ci.yml** | PRs, push to dev | Code quality, tests, security checks |
| **pr-validation.yml** | PRs to main | PR title, size, secrets, description checks |
| **deploy.yml** | Push to main, tags | Build Docker image, deploy to staging/prod |

### Configuration Files

| File | Purpose |
|------|---------|
| **CODEOWNERS** | Automatic review requests |
| **dependabot.yml** | Automated dependency updates |
| **labeler.yml** | Auto-label PRs based on files |
| **markdown-link-check-config.json** | Link validation config |

### Templates

| Template | Purpose |
|----------|---------|
| **PULL_REQUEST_TEMPLATE.md** | PR template with checklist |

## Quick Start

### For Developers

1. **Create feature branch:**
   ```bash
   git checkout -b feature/123-my-feature
   ```

2. **Make changes and commit:**
   ```bash
   git add .
   git commit -m "feat(component): Add feature"
   ```

3. **Push and create PR:**
   ```bash
   git push origin feature/123-my-feature
   # Create PR via GitHub UI
   ```

4. **CI will automatically:**
   - Run tests
   - Check code quality
   - Scan for security issues
   - Validate PR format
   - Request code owner reviews

### For Maintainers

1. **Review PR** - Check code, tests, docs
2. **Approve PR** - Once satisfied
3. **Merge** - CI will handle deployment
4. **Monitor** - Check deployment status

## CI/CD Pipeline

```
┌─────────────────────────────────────────────────────┐
│                 Developer Workflow                   │
└─────────────────────────────────────────────────────┘
                          │
                          ↓
┌─────────────────────────────────────────────────────┐
│            Create PR to dev/main                     │
│                                                      │
│  Triggers:                                          │
│  • ci.yml (tests, quality, security)                │
│  • pr-validation.yml (title, size, secrets)         │
│  • Auto-label based on changed files                │
│  • Request reviews from project owner                 │
└─────────────────────────────────────────────────────┘
                          │
                          ↓
┌─────────────────────────────────────────────────────┐
│              All Checks Pass ✅                      │
│                                                      │
│  Required:                                          │
│  • Code quality (black, flake8, isort)              │
│  • Unit tests (Python 3.9, 3.10, 3.11)             │
│  • Security scan (safety, bandit, gitleaks)         │
│  • Import verification                              │
│  • Documentation check                              │
│  • PR validation (title, description, size)         │
│  • Repository owner approval (YOU must approve)     │
└─────────────────────────────────────────────────────┘
                          │
                          ↓
┌─────────────────────────────────────────────────────┐
│                  Merge to main                       │
│                                                      │
│  Triggers deploy.yml:                               │
│  • Build Docker image                               │
│  • Push to Docker Hub                               │
│  • Deploy to staging                                │
│  • Run smoke tests                                  │
└─────────────────────────────────────────────────────┘
                          │
                          ↓
┌─────────────────────────────────────────────────────┐
│           Create Release Tag (v*)                    │
│                                                      │
│  Triggers deploy.yml:                               │
│  • Deploy to production                             │
│  • Create GitHub release                            │
│  • Send Slack notification                          │
└─────────────────────────────────────────────────────┘
```

## Status Checks

### Required for PR Approval

| Check | Description | Blocking |
|-------|-------------|----------|
| Code Quality | black, isort, flake8, mypy | ✅ Yes |
| Unit Tests | pytest on 3.9, 3.10, 3.11 | ✅ Yes |
| Security | safety, bandit, gitleaks | ✅ Yes |
| Import Verification | All imports work | ✅ Yes |
| Documentation | Docs exist, links work | ✅ Yes |
| Build | Package builds correctly | ✅ Yes |
| PR Title | Conventional commits format | ✅ Yes |
| PR Description | >50 characters | ✅ Yes |
| Secret Scan | No secrets in code | ✅ Yes |
| Project Owner | Required reviewers | ✅ Yes |

## Branch Protection

### `main` Branch

- ✅ Require 1 approval (from YOU as repository owner)
- ✅ Require code owner review (YOU)
- ✅ All status checks must pass
- ✅ No force push
- ✅ No deletions
- ✅ Linear history
- ✅ Signed commits (recommended)
- ⚠️ **Only YOU can approve and merge to main**

### `dev` Branch

- ✅ Require 1 approval (from YOU as repository owner)
- ✅ Basic status checks
- ✅ No force push
- ✅ No deletions
- ⚠️ **Only YOU can approve and merge to dev**

Configure in GitHub Settings → Branches → Add rule.

## Automated Updates

### Dependabot

- **Weekly updates** for Python dependencies
- **Weekly updates** for GitHub Actions
- **Automatic PRs** with changelogs
- **Auto-labeled** for easy triage

### Auto-Labeling

PRs are automatically labeled based on changed files:

| Label | Triggers On |
|-------|------------|
| `documentation` | `*.md`, `docs/**` |
| `tests` | `tests/**`, `**/test_*.py` |
| `ci/cd` | `.github/**` |
| `deployment` | `**/deploy/**`, Dockerfiles |
| `dependencies` | `requirements*.txt` |
| `core` | `src/core/**` |
| `tools` | `src/tools/**` |
| `monitoring` | `src/monitoring/**` |

## Security

### Secret Scanning

- **Gitleaks** scans all PRs for secrets
- **Fails build** if secrets detected
- **Historical scan** on main branch

### Dependency Scanning

- **Safety** checks for known vulnerabilities
- **Weekly scans** via Dependabot
- **Automatic PRs** for security updates

### Code Scanning

- **Bandit** security linting
- **Reports** uploaded as artifacts
- **Non-blocking** but should be addressed

## Monitoring

### Workflow Status

View all workflow runs:
```
https://github.com/OWNER/REPO/actions
```

### Coverage Reports

Coverage uploaded to Codecov:
```
https://codecov.io/gh/OWNER/REPO
```

### Security Reports

View Dependabot alerts:
```
https://github.com/OWNER/REPO/security/dependabot
```

## Troubleshooting

### CI Failing

1. **Check logs** in GitHub Actions
2. **Run locally**:
   ```bash
   # Code quality
   black agents/ --check
   flake8 agents/

   # Tests
   pytest agents/airflow_intelligence/tests/
   ```
3. **Fix issues** and push

### PR Blocked

1. **Check required checks** in PR
2. **View failed check logs**
3. **Request help** if stuck

### Deployment Failed

1. **Check deploy.yml logs**
2. **Rollback** if needed
3. **Create hotfix** if critical

## Best Practices

### Commits

✅ Use conventional commits: `type(scope): message`
✅ Sign commits for security
✅ Keep commits atomic and focused

### Pull Requests

✅ Small, focused PRs (<500 lines)
✅ Meaningful descriptions
✅ Tests for new code
✅ Update documentation

### Testing

✅ Write tests first (TDD)
✅ >80% coverage
✅ Test edge cases
✅ Mock external dependencies

## Resources

- **[GitHub Actions Docs](https://docs.github.com/en/actions)** - Official docs
- **[Conventional Commits](https://www.conventionalcommits.org/)** - Commit format
- **[Branch Protection](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository)** - Protection setup

## Support

Questions about CI/CD? Contact:
- **Project Owner** - General CI/CD questions
- **Project Owner** - Security scan issues
- **Project Owner** - Code review questions

---

**Maintained By:** Project Owner
**Last Updated:** 2026-03-06
