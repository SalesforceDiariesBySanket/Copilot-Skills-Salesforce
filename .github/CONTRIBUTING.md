
## Code of Conduct

Please be respectful and professional in all interactions.

## Getting Started

1. Fork the repository
2. Clone your fork locally
3. Create a feature branch: `git checkout -b feature/your-feature-name`
4. Make your changes
5. Commit with meaningful messages: `git commit -m "feat: add new feature"`
6. Push to your fork: `git push origin feature/your-feature-name`
7. Create a Pull Request

## Development Setup

```bash
# Install dependencies
npm install

# Install Salesforce CLI
npm install --global @salesforce/cli

# Create a scratch org
sf org create scratch --definition-file config/project-scratch-def.json --alias dev
```

## Code Standards

### Apex
- Follow [Salesforce Apex Code Style Guide](https://developer.salesforce.com/docs/atlas.en-us.apexcode.meta/apexcode/apex_coding_style.htm)
- Use meaningful variable and method names
- Add comments for complex logic
- Keep methods focused and small

### Lightning Web Components (LWC)
- Use ES6+ syntax
- Follow [LWC Best Practices](https://developer.salesforce.com/docs/component-library/documentation/en/lwc/lwc.create_components_best_practices)
- Use `@wire` decorators for data binding
- Handle errors appropriately

### JavaScript/Node.js
- Follow ESLint configuration
- Use async/await instead of callbacks
- Add JSDoc comments

### Git Commit Messages
- Use conventional commits: `type(scope): description`
- Types: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `chore`
- Example: `feat(trigger): add new validation logic`

## Pull Request Process

1. Ensure all tests pass locally
2. Update documentation if needed
3. Follow the PR template
4. Request review from relevant team members
5. Address feedback promptly
6. Squash commits before merge if requested

## Testing

```bash
# Run all tests
npm test

# Run tests with coverage
npm test -- --coverage

# Run specific test file
npm test -- test/specific.test.js

# Run Apex tests on scratch org
sf apex run test --target-org dev --wait 30
```

## Deployment

1. Ensure all tests pass
2. Get code review approval
3. Merge to main branch
4. CI/CD pipeline automatically deploys to production

## Reporting Issues

Use GitHub Issues with appropriate templates:
- Bug Report: For reporting bugs
- Feature Request: For new feature ideas

## Questions?

Feel free to open an issue or contact the team for clarification.

Thank you for contributing!
