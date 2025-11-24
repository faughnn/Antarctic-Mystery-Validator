# Testing Guide - How to View Results Remotely

## 🎯 Quick Answer

**Where to see test results:** https://github.com/faughnn/Antarctic-Mystery-Validator/actions

---

## 📍 Step-by-Step: Viewing Test Results on GitHub

### Method 1: GitHub Actions Tab (Recommended)

1. **Go to your repository on GitHub**
   ```
   https://github.com/faughnn/Antarctic-Mystery-Validator
   ```

2. **Click the "Actions" tab** (top navigation bar)
   - You'll see a list of all workflow runs
   - Each run shows: ✅ green checkmark (passed) or ❌ red X (failed)

3. **Click on any workflow run** to see details
   - Example: "Add GitHub Actions workflow for automated testing"

4. **Click "validate" job** (under "Jobs" section on the left)

5. **See the Python output**
   - Look for the "Run Mystery Validator" step
   - Click to expand and see full colored output
   - Shows exactly what you'd see running `python3 main.py` locally

6. **View the Summary** (easier to read)
   - Click "Summary" at the top
   - Scroll down to see formatted validation results
   - Shows pass/fail for each validation

### Method 2: Status Badge (Quick Check)

1. **Open the README** on GitHub
   ```
   https://github.com/faughnn/Antarctic-Mystery-Validator/blob/main/README.md
   ```

2. **Look at the top**
   - Green badge = All tests passing ✅
   - Red badge = Some tests failing ❌
   - Click the badge to go directly to Actions

### Method 3: Download Full Logs

1. Go to any workflow run (see Method 1, steps 1-3)

2. **Scroll to bottom** of the page

3. **Find "Artifacts" section**
   - Shows: `validation-results`

4. **Click to download**
   - Gets a `.txt` file with complete validation output
   - Can open in any text editor
   - Preserves all color codes and formatting

### Method 4: Manual Run (Trigger on Demand)

1. Go to **Actions tab**

2. Click **"Mystery Validator"** workflow (left sidebar)

3. Click **"Run workflow"** button (top right)

4. Select your branch from dropdown

5. Click green **"Run workflow"** button

6. Wait ~30 seconds, then refresh page to see results

---

## 📊 What You'll See

### In the Actions Tab

```
✓ validate (1m 23s)
  ✓ Set up job (2s)
  ✓ Checkout code (1s)
  ✓ Set up Python (15s)
  ✓ Run Mystery Validator (48s)  ← Click here for Python output
  ✓ Upload validation results (3s)
  ✓ Comment validation status (2s)
  ✓ Post Set up Python (1s)
```

### Example Python Output

```
🧊 Antarctic Mystery Validator
================================================================================

Loading data files...
✓ Loaded 60 characters
✓ Loaded 295 scene evidence records
✓ Loaded 275 dialogue lines

Running validation checks...

================================================================================
VALIDATION RESULTS
================================================================================

✓ PASS - Everyone Appears
      All 60 characters appear in at least one scene.

✓ PASS - Death Scenes Valid
      All 60 dead characters have valid death scenes.

✓ PASS - Characters Have Identifying Clues
      All 60 characters have at least one identifying clue.

✓ PASS - Scenes Have Characters
      All 50 scenes have at least one character.

✗ FAIL - Dialogue Speakers Exist
      112 dialogue lines have empty/missing speakers

================================================================================
Summary: 4 passed, 1 failed
================================================================================
```

---

## 🔔 When Tests Run Automatically

Tests run automatically on:
- ✅ Every `git push` to any branch
- ✅ Every pull request
- ✅ Manual trigger (see Method 4 above)

You'll get:
- Email notification if tests fail (check GitHub notification settings)
- Status visible on pull requests
- Badge updates in README

---

## 💡 Pro Tips

1. **Bookmark the Actions page:**
   ```
   https://github.com/faughnn/Antarctic-Mystery-Validator/actions
   ```

2. **Filter by branch:**
   - Use the "Branch" dropdown on Actions page
   - See only results for your current branch

3. **Check before making changes:**
   - Look at the badge or Actions tab
   - Make sure tests are passing before starting new work

4. **Debug failures:**
   - Download the artifact for full logs
   - Look at the exact line where validation failed
   - Fix the issue and push again

5. **Compare runs:**
   - Click between different workflow runs
   - See how changes affected validation results

---

## ❓ Troubleshooting

### "I don't see any workflow runs"
- Wait 30-60 seconds after pushing
- Refresh the Actions page
- Make sure you're looking at the right branch

### "Workflow is stuck on 'Queued'"
- GitHub Actions might be busy
- Usually starts within 1-2 minutes
- Can have multiple runs queued

### "I want to cancel a run"
- Click on the running workflow
- Click "Cancel workflow" button (top right)

### "I don't see colored output"
- Click "View raw logs" for plain text
- Or download the artifact for the formatted version
- Colors may not show in some browsers

---

## 🚀 Quick Links

- **Actions Tab:** https://github.com/faughnn/Antarctic-Mystery-Validator/actions
- **Repository:** https://github.com/faughnn/Antarctic-Mystery-Validator
- **Workflow File:** `.github/workflows/validate.yml` (in your repo)

---

**That's it!** Every time you push code, just check the Actions tab to see if your mystery validator passes all checks. 🧊
