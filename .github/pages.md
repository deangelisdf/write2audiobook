# Deploy pages workflows

Updates to the `mkdocs.yml` file or any file in the `docs` directory trigger one of two GitHub Actions workflows.
These workflows keep the deployed version of the documentation site up to date with the document files in the `main` branch.

Both workflows call a reusable workflow called `deploy-pages.yml`. This workflow runs the `mkdocs gh-deploy` command.
To make sure that the command only pushes the most recent version of the docs, there is a concurrency lock on this workflow.
The lock cancels running actions and launches a new one when it's triggered.

## auto-deploy-pages

This workflow runs when a pull request has met the following criteria:

- It has been merged into the `main` branch.
- It includes changes to the `mkdocs.yml` file or any file in the `docs` directory.

## man-deploy-pages

This workflow runs when there a push meets the following criteria:

- It is to the `main` branch.
- It includes changes to the `mkdocs.yml` file or any file in the `docs` directory.

You can also trigger this flow manually using the [GitHub Actions extension](https://marketplace.visualstudio.com/items?itemName=GitHub.vscode-github-actions) in VS Code.
