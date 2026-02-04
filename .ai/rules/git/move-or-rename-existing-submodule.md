# Moving/Renaming Existing Git Submodules

This guide covers how to move or rename an already-cloned submodule while preserving all uncommitted work. This process updates all necessary Git configuration files without requiring deletion and re-cloning.

## Overview

When moving/renaming a submodule, you need to update:
1. `.gitmodules` - The submodule definition file
2. `.git/config` - Local repository configuration
3. `.git/modules/<old-path>/` - The submodule's Git metadata directory
4. The submodule directory itself
5. The `.git` file inside the submodule (points to the Git metadata)
6. The `worktree` path in the submodule's config file

## Step-by-Step Process

### Prerequisites

- The submodule is already cloned and initialized
- You may have uncommitted work in the submodule (this will be preserved)
- You know the current submodule name/path and the desired new name/path

### Step 1: Identify Current Configuration

First, check the current submodule configuration:

```bash
# Check .gitmodules for the current entry
cat .gitmodules | grep -A 2 "<submodule-name>"

# Check git submodule status
git submodule status

# Check local config
cat .git/config | grep -A 2 "<submodule-name>"
```

### Step 2: Update `.gitmodules`

Edit `.gitmodules` and update the submodule entry:

**Old entry:**
```
[submodule "AISE/Honeywell/Anaconda"]
  path = .submodules/AISE/Honeywell/Anaconda
  url = git@github.com:Aitomatic/Honeywell-Anaconda
```

**New entry (example):**
```
[submodule "AISE/Honeywell/Vulcan"]
  path = .submodules/AISE/Honeywell/Vulcan
  url = git@github.com:Aitomatic/Honeywell-Anaconda
```

**Note:** The `url` typically stays the same unless you're also changing the remote repository.

### Step 3: Move the Submodule Directory

Move the actual submodule directory to its new location:

```bash
# Example: Moving from .submodules/AISE/Honeywell/Anaconda to .submodules/AISE/Honeywell/Vulcan
# On Windows (PowerShell):
Move-Item -Path ".submodules\AISE\Honeywell\Anaconda" -Destination ".submodules\AISE\Honeywell\Vulcan"

# On Unix/Linux/Mac:
mv .submodules/AISE/Honeywell/Anaconda .submodules/AISE/Honeywell/Vulcan
```

**Important:** If you also have a working directory at a different location (e.g., `Honeywell/Anaconda`), move that too:

```bash
# Example: Moving from Honeywell/Anaconda to Honeywell/Vulcan
Move-Item -Path "Honeywell\Anaconda" -Destination "Honeywell\Vulcan"
```

### Step 4: Move the Git Metadata Directory

Move the submodule's Git metadata directory:

```bash
# On Windows (PowerShell):
Move-Item -Path ".git\modules\AISE\Honeywell\Anaconda" -Destination ".git\modules\AISE\Honeywell\Vulcan"

# On Unix/Linux/Mac:
mv .git/modules/AISE/Honeywell/Anaconda .git/modules/AISE/Honeywell/Vulcan
```

### Step 5: Update `.git/config`

Edit `.git/config` and update the submodule entry:

**Old entry:**
```
[submodule "AISE/Honeywell/Anaconda"]
  active = true
  url = git@github.com:Aitomatic/Honeywell-Anaconda
```

**New entry:**
```
[submodule "AISE/Honeywell/Vulcan"]
  active = true
  url = git@github.com:Aitomatic/Honeywell-Anaconda
```

### Step 6: Update the `.git` File in the Submodule

The `.git` file inside the submodule directory points to the Git metadata. Update it to reflect the new path:

**Old content:**
```
gitdir: ../../../../.git/modules/AISE/Honeywell/Anaconda
```

**New content:**
```
gitdir: ../../../../.git/modules/AISE/Honeywell/Vulcan
```

**Location:** `.submodules/AISE/Honeywell/Vulcan/.git` (or `Honeywell/Vulcan/.git` if you have a working directory there)

### Step 7: Update the Submodule's Config File

Update the `worktree` path in the submodule's own config file:

**File:** `.git/modules/AISE/Honeywell/Vulcan/config`

**Old:**
```
worktree = ../../../../../.submodules/AISE/Honeywell/Anaconda
```

**New:**
```
worktree = ../../../../../.submodules/AISE/Honeywell/Vulcan
```

**Note:** The relative path calculation depends on the depth. Count the `../` needed to go from `.git/modules/AISE/Honeywell/Vulcan/` to `.submodules/AISE/Honeywell/Vulcan/`.

### Step 8: Update the Index

Stage the changes to `.gitmodules`:

```bash
git add .gitmodules
```

If you moved the submodule directory, Git should detect it. Check status:

```bash
git status
```

### Step 9: Verify the Move

Verify that everything is working:

```bash
# Check submodule status (should show the new path)
git submodule status

# Verify the submodule is recognized
git submodule update --init --recursive

# Check that uncommitted work is preserved
cd .submodules/AISE/Honeywell/Vulcan  # or Honeywell/Vulcan
git status
```

## Complete Example: Renaming Anaconda to Vulcan

Assuming the submodule is currently at `.submodules/AISE/Honeywell/Anaconda` and you want to rename it to `Vulcan`:

1. **Update `.gitmodules`:**
   - Change `[submodule "AISE/Honeywell/Anaconda"]` to `[submodule "AISE/Honeywell/Vulcan"]`
   - Change `path = .submodules/AISE/Honeywell/Anaconda` to `path = .submodules/AISE/Honeywell/Vulcan`

2. **Move directories:**
   ```powershell
   Move-Item ".submodules\AISE\Honeywell\Anaconda" ".submodules\AISE\Honeywell\Vulcan"
   Move-Item ".git\modules\AISE\Honeywell\Anaconda" ".git\modules\AISE\Honeywell\Vulcan"
   # If you have a working directory:
   Move-Item "Honeywell\Anaconda" "Honeywell\Vulcan"
   ```

3. **Update `.git/config`:**
   - Change `[submodule "AISE/Honeywell/Anaconda"]` to `[submodule "AISE/Honeywell/Vulcan"]`

4. **Update `.submodules/AISE/Honeywell/Vulcan/.git`:**
   - Change `gitdir: ../../../../.git/modules/AISE/Honeywell/Anaconda` to `gitdir: ../../../../.git/modules/AISE/Honeywell/Vulcan`

5. **Update `.git/modules/AISE/Honeywell/Vulcan/config`:**
   - Change `worktree = ../../../../../.submodules/AISE/Honeywell/Anaconda` to `worktree = ../../../../../.submodules/AISE/Honeywell/Vulcan`

6. **Stage changes:**
   ```bash
   git add .gitmodules
   ```

## Troubleshooting

### Git doesn't recognize the submodule after move

- Verify all paths are updated correctly
- Check that the `.git` file in the submodule points to the correct location
- Ensure the `worktree` path in the submodule's config is correct
- Try: `git submodule sync` followed by `git submodule update --init`

### Uncommitted work is missing

- Check that you moved the directory (not copied)
- Verify the `worktree` path in `.git/modules/<new-path>/config` is correct
- The worktree should point to the actual submodule directory location

### Path calculation for worktree

The `worktree` path is relative from `.git/modules/<path>/config` to the actual submodule directory. Count directory levels:
- From `.git/modules/AISE/Honeywell/Vulcan/` to repo root: `../../../../`
- From repo root to `.submodules/AISE/Honeywell/Vulcan/`: `.submodules/AISE/Honeywell/Vulcan/`
- Combined: `../../../../.submodules/AISE/Honeywell/Vulcan`

## When You Pull a Commit That Renames a Submodule (Recipient Workflow)

If someone else renamed the submodule and you **pull** that commit, your repo gets updated `.gitmodules` and index (old path removed, new path added), but your working tree is left in a mixed state. Follow this cleanup.

### What you may see after pull

- **Warning:** `warning: unable to rmdir '.submodules/.../Anaconda': Directory not empty` — Git could not remove the old path because the directory still exists and is not empty.
- **On disk:** The old submodule directory (e.g. `.submodules/AISE/Honeywell/Anaconda`) is still present with full contents; the new path (e.g. `.submodules/AISE/Honeywell/Vulcan`) may exist as an empty or placeholder directory.
- **`git submodule status`:** The new submodule shows with a `-` prefix (not initialized). The old path no longer appears in the list.
- **`.git/config`:** Still contains the old `[submodule "AISE/Honeywell/Anaconda"]` block. Pull does **not** remove it; only `.gitmodules` and the index are updated.

### Steps after pulling a submodule rename

1. **Check for uncommitted work in the old submodule** (do this before removing anything):
   ```bash
   cd .submodules/AISE/Honeywell/Anaconda
   git status
   git branch -v
   ```
   If there are uncommitted changes or you're not on the branch you expect, **preserve that work** before cleanup:
   - **Option A — stash:** `git stash -u` (then you can later `cd` into the new Vulcan clone and `git stash pop` if the history matches).
   - **Option B — backup the directory:** From the parent repo, move the whole directory to a safe name so you can copy files or reattach later, e.g. `mv .submodules/AISE/Honeywell/Anaconda .submodules/AISE/Honeywell/Anaconda-backup-$(date +%Y%m%d)`. Then skip deleting that path in step 4 (only remove the one you didn't back up, or leave the backup in place and remove only `.git/modules/.../Anaconda` and the config entry so the backup is a plain folder).
   - **Option C — commit in the submodule:** If the submodule still has a remote, commit (and optionally push) from inside the old Anaconda dir so the work exists in the remote; then you can pull it into the new Vulcan clone if it's the same repo/URL.
   Only after you've either confirmed there is no important uncommitted work or you've preserved it, proceed with the steps below.

2. **Initialize and update the new submodule** (clone and checkout at the new path):
   ```bash
   git submodule update --init .submodules/AISE/Honeywell/Vulcan
   ```

3. **Remove the old submodule working directory** (only if you did not back it up in step 1):
   ```bash
   rm -rf .submodules/AISE/Honeywell/Anaconda
   ```

4. **Remove the old submodule’s Git metadata:**
   ```bash
   rm -rf .git/modules/AISE/Honeywell/Anaconda
   ```

5. **Remove the stale submodule entry from local config**
   Edit `.git/config` and delete the `[submodule "AISE/Honeywell/Anaconda"]` block (the three lines: section header, `active = true`, and `url = ...`).

6. **Verify:**
   ```bash
   git submodule status
   ls .submodules/AISE/Honeywell/
   ```
   You should see the new submodule (e.g. Vulcan) with a space prefix (initialized) and no Anaconda directory.

### Optional: align config with .gitmodules

Running `git submodule sync` after pull updates `.git/config` from `.gitmodules`. It will not re-add the old Anaconda entry (since it’s gone from `.gitmodules`). If you already removed the Anaconda block and initialized Vulcan, sync is optional.

---

## Important Notes

- **Always preserve uncommitted work:** This process moves directories, so all uncommitted changes are preserved
- **Relative paths matter:** The `.git` file and `worktree` paths use relative paths - ensure they're calculated correctly
- **Case sensitivity:** On case-insensitive filesystems (Windows, Mac default), be careful with case-only renames
- **Commit the changes:** After moving, commit the updated `.gitmodules` file to make the change permanent
