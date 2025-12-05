# Branch Protection Setup Guide

To fully protect your `main` branch, you need to configure branch protection rules in GitHub. Follow these steps:

## Step 1: Go to Repository Settings

1. Navigate to your repository on GitHub: `https://github.com/Deeperthanuthink/tradieralpaca`
2. Click on **Settings** tab
3. In the left sidebar, click **Branches** under "Code and automation"

## Step 2: Add Branch Protection Rule

1. Click **Add rule** (or **Add branch protection rule**)
2. In "Branch name pattern", enter: `main`

## Step 3: Configure Protection Settings

Enable the following options:

### Required Status Checks
- ✅ **Require status checks to pass before merging**
- ✅ **Require branches to be up to date before merging**
- Add these required status checks:
  - `Code Quality Checks`
  - `Run Tests`
  - `Python Syntax Check`
  - `Security Scan`
  - `CI Success`

### Pull Request Requirements
- ✅ **Require a pull request before merging**
- ✅ **Require approvals** (set to 1 or more)
- ✅ **Dismiss stale pull request approvals when new commits are pushed**

### Additional Protections (Recommended)
- ✅ **Require conversation resolution before merging**
- ✅ **Do not allow bypassing the above settings**
- ✅ **Restrict who can push to matching branches** (optional, for teams)

## Step 4: Save Changes

Click **Create** or **Save changes** at the bottom of the page.

---

## Workflow Summary

After setup, your workflow will be:

1. **Push to `testing` branch** → CI Pipeline runs automatically
2. **CI Passes** → Auto-creates PR to `main` (or updates existing)
3. **CI Fails** → Code stays in `testing`, no PR created
4. **Review & Approve PR** → Merge to `main` is enabled
5. **Merge to `main`** → Production-ready code deployed

## Testing the Pipeline

```bash
# Create and switch to testing branch
git checkout -b testing

# Make changes
# ...

# Commit and push
git add .
git commit -m "Test CI pipeline"
git push origin testing
```

Then check the **Actions** tab in GitHub to see the pipeline run.
