# Git guide for two people on one repo

## The idea
`main` is the shared, working version. Each person works on their own **branch** (a private copy
of the work), then merges it into `main` when a piece is done. To see your friend's code, you
**pull** it from GitHub.

## One-time setup
1. Owner (Ramya): GitHub repo, Settings, Collaborators, Add people, add your friend's username.
   She accepts the invite by email.
2. Both: install Git, then
   `git config --global user.name "Your Name"` and `git config --global user.email "you@mail.com"`.
3. GitHub asks for a login on push. Use GitHub Desktop, or a Personal Access Token
   (GitHub, Settings, Developer settings, Tokens) as the password.

## Daily routine (memorise these 6 lines)
```bash
git switch main
git pull                          # get everyone's latest work
git switch -c ramya/cart-orders   # new branch for today's task (first time only)
# ... write code ...
git add .
git commit -m "Add cart and orders endpoints"
git push -u origin ramya/cart-orders
```
Then on GitHub click **Compare & pull request**, then **Merge**. Now `main` has your work.

## See your friend's code
```bash
git switch main
git pull                          # after she has merged her branch
git switch ramya/cart-orders
git merge main                    # bring her work into your branch
```
Or look at her branch directly: `git fetch` then `git switch friend/ai-interview`.

## Rules to avoid trouble
- Never code directly on `main`. Always on your branch.
- `git pull` before you start every session.
- Commit small and often, with a clear message.
- Edit only your own files. For `models.py` and `main.py`, tell each other first.
- Never commit `.env` or API keys (already in .gitignore).

## If you see a merge conflict
Git marks the file with `<<<<<<<`, `=======`, `>>>>>>>`. Keep the right lines, delete the markers,
then `git add <file>` and `git commit`.

## Useful checks
`git status` (what changed), `git branch` (which branch am I on), `git log --oneline` (history).
