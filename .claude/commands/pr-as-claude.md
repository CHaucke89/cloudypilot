---
description: Open a PR authored by claude[bot] through the open-pr job in claude.yaml
argument-hint: "[branch] [base]"
---

Open a pull request as claude[bot] instead of as Chris. Only do this because this command was run; every other PR still opens under Chris's account.

Arguments: `$ARGUMENTS`
- First argument is the head branch. Default: the current branch (`git branch --show-current`).
- Second argument is the base branch. Default: `master`.

Steps:

1. Make sure the head branch exists on `origin` and is up to date (`git ls-remote --heads origin <branch>`). If it isn't pushed, push it with `git push -u origin <branch>`. Stop if the branch is `master` or if a PR is already open for it (`gh pr list --head <branch> --state open`).
2. Write a title and body from the commits on `<base>..<branch>`, matching the style of recent PRs (`[area] Short summary` title, a short body saying what changed). No attribution, signatures or session links.
3. Dispatch the workflow. The `open-pr` job runs `gh pr create` with the Claude app's token, which is what makes claude[bot] the author:

   ```
   gh workflow run claude.yaml --ref master -f head=<branch> -f base=<base> -f title="<title>" -f body="<body>" -f draft=true
   ```

   If `gh` isn't available, use the GitHub MCP `actions_run_trigger` tool with the same workflow, ref and inputs.
4. Find the run (`gh run list --workflow claude.yaml --event workflow_dispatch --limit 1 --json databaseId,status`) and wait for it with `gh run watch <id> --exit-status`.
5. Report the PR URL and confirm its author is `claude[bot]` (`gh pr list --head <branch> --json url,author`). If the run failed or no PR exists, show the failing step from `gh run view <id> --log-failed`.
