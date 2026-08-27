# Git Basics

A quick-reference cheat sheet for the everyday Git commands used on this project.

## Setup

```bash
git init                          # create a new repo in the current directory
git clone <url>                   # copy a remote repo to your machine
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
```

## Checking status and history

```bash
git status                        # see staged/unstaged/untracked changes
git log                           # commit history
git log --oneline                 # condensed history, one line per commit
git diff                          # unstaged changes vs. last commit
git diff --staged                 # staged changes vs. last commit
```

## Staging and committing

```bash
git add <file>                    # stage a specific file
git add .                         # stage everything in the current directory
git commit -m "message"           # commit staged changes
git commit -am "message"          # stage + commit tracked file changes in one step
```

## Branching

```bash
git branch                        # list local branches
git branch <name>                 # create a new branch
git checkout <name>                # switch to a branch
git checkout -b <name>             # create and switch in one step
git switch <name>                  # modern alternative to checkout
git switch -c <name>                # create and switch (modern alternative)
git branch -d <name>                # delete a branch (safe, only if merged)
```

## Merging and rebasing

```bash
git merge <branch>                 # merge a branch into the current one
git rebase <branch>                 # replay current branch's commits on top of another
```

## Remotes

```bash
git remote -v                      # list configured remotes
git remote add origin <url>        # add a remote named "origin"
git fetch                          # download remote changes without merging
git pull                           # fetch + merge (or rebase) from the remote
git push                           # upload local commits to the remote
git push -u origin <branch>        # push and set the branch to track the remote
```

## Undoing changes

```bash
git restore <file>                 # discard unstaged changes to a file
git restore --staged <file>        # unstage a file (keep the changes)
git reset --soft HEAD~1            # undo the last commit, keep changes staged
git reset --hard HEAD~1            # undo the last commit and discard changes (destructive)
git revert <commit>                # create a new commit that undoes a previous one (safe for shared history)
```

## Stashing

```bash
git stash                          # temporarily shelve uncommitted changes
git stash pop                      # reapply the most recent stash
git stash list                     # see all stashed changes
```

## Pull requests (GitHub CLI)

```bash
gh pr create                       # open a pull request from the current branch
gh pr list                         # list open pull requests
gh pr view <number>                 # view a pull request
gh pr checkout <number>             # check out a pull request locally
```
