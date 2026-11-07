# Publish from Android Termux

The target owner is `SlimNationworkz`. This project is **not yet a public GitHub
repository** until you create and push it. Keep the existing private ForgeRelay
repository untouched.

## Prepare and verify

1. Install Termux packages if missing: `pkg install python git unzip`.
2. Extract the project ZIP into your Termux home folder.
3. Run:

```sh
cd ~/ai-verification-lab
python -m unittest discover -s tests -v
python ai_verify.py --candidate examples/fixed.py --spec specs/usernames.json
python ai_verify.py --candidate examples/buggy.py --spec specs/usernames.json
# The second command intentionally exits 1: that is SUCCESSFUL detection.
```

## Create an empty public GitHub repo

Open `https://github.com/new` in your browser, choose owner
`SlimNationworkz`, name it `ai-verification-lab`, set **Public**, and leave
README/license/gitignore initialization **unchecked** (we already include them).

## Initialize and push from Termux

```sh
cd ~/ai-verification-lab
git init -b main
git config user.name 'SlimNationworkz'
# Prefer a GitHub private/noreply commit identity to exposing your login email:
git config user.email '323934782+SlimNationworkz@users.noreply.github.com'
git add .
git commit -m 'Initial independent AI verification lab'
git remote add origin https://github.com/SlimNationworkz/ai-verification-lab.git
git push -u origin main
```

GitHub requires authentication to push. Passwords do not work for HTTPS Git
operations. You can use GitHub CLI (`gh auth login`) if available and authenticated
through its browser/device flow, then `gh auth setup-git` before pushing. Do not
paste passwords, tokens, recovery codes, or private keys into a chat or repository.

If you prefer a browser-only upload, the GitHub website can upload files after
you create the repository, but the Termux `git` path preserves all directories
and the GitHub Actions workflow more reliably.

When published, the intended public URL is:
`https://github.com/SlimNationworkz/ai-verification-lab`

## After publication

Check the **Actions** tab for a passing `Independent verifier checks` workflow.
Only then use the GitHub URL in job applications. Do not describe this as
paid client work or claim verified GitHub Actions status until the run completes.
