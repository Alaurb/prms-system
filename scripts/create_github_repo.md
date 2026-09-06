# Create GitHub Repository

Install GitHub CLI or use a portable `gh` executable. Log in first:

```powershell
gh auth login
```

Then create and push the repository with:

```powershell
cd <repo>
gh repo create prms-system --public --source . --remote origin --push
```

If the repository is created manually on GitHub, push with:

```powershell
cd <repo>
git remote add origin https://github.com/<your-account>/prms-system.git
git branch -M main
git push -u origin main
```
