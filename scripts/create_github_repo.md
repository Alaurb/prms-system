# Create GitHub Repository

GitHub CLI is available as a portable tool at:

```text
C:\Users\10335\OneDrive\文档\格式修改\tools\gh\bin\gh.exe
```

Log in first:

```powershell
& 'C:\Users\10335\OneDrive\文档\格式修改\tools\gh\bin\gh.exe' auth login
```

Then create and push the repository with:

```powershell
cd C:\Users\10335\OneDrive\文档\格式修改\prms-system
& 'C:\Users\10335\OneDrive\文档\格式修改\tools\gh\bin\gh.exe' repo create prms-system --public --source . --remote origin --push
```

If the repository is created manually on GitHub, push with:

```powershell
cd C:\Users\10335\OneDrive\文档\格式修改\prms-system
git remote add origin https://github.com/<your-account>/prms-system.git
git branch -M main
git push -u origin main
```
