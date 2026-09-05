# Create GitHub Repository

The GitHub CLI is not available on this Windows environment yet. After installing and logging in with `gh auth login`, create and push the repository with:

```powershell
cd C:\Users\10335\OneDrive\文档\格式修改\prms-system
gh repo create prms-system --public --source . --remote origin --push
```

If the repository is created manually on GitHub, push with:

```powershell
cd C:\Users\10335\OneDrive\文档\格式修改\prms-system
git remote add origin https://github.com/<your-account>/prms-system.git
git branch -M main
git push -u origin main
```

