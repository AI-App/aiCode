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

### Ignored untracked files missing after submodule rename (recipient workflow)

If you already ran the recipient workflow and **ignored** untracked files (e.g. `* [Otter AI].txt` in `.gitignore`) are missing from the new submodule, the save step was either skipped or used `git ls-files --others --exclude-standard`, which excludes ignored files. **There is no in-process recovery:** once the old submodule directory is removed, those files are permanently lost unless you have an external backup (e.g. cloud sync or version history) and restore the old directory from it, then re-run the save (with `git ls-files --others` only) and restore. **This document's workflow prevents loss by requiring save-first with `git ls-files --others` only; do not skip or alter that step.**

### Path calculation for worktree

The `worktree` path is relative from `.git/modules/<path>/config` to the actual submodule directory. Count directory levels:
- From `.git/modules/AISE/Honeywell/Vulcan/` to repo root: `../../../../`
- From repo root to `.submodules/AISE/Honeywell/Vulcan/`: `.submodules/AISE/Honeywell/Vulcan/`
- Combined: `../../../../.submodules/AISE/Honeywell/Vulcan`

## When You Pull a Commit That Renames a Submodule (Recipient Workflow)

If someone else renamed the submodule and you **pull** that commit, your repo gets updated `.gitmodules` and index (old path removed, new path added), but your working tree is left in a mixed state. Follow this cleanup.

**Do not remove the old submodule directory until you have saved all untracked files (including ignored) and verified the backup.** Otherwise those files are permanently lost; this process does not rely on external recovery.

### What you may see after pull

- **Warning:** `warning: unable to rmdir '.submodules/.../Anaconda': Directory not empty` — Git could not remove the old path because the directory still exists and is not empty.
- **On disk:** The old submodule directory (e.g. `.submodules/AISE/Honeywell/Anaconda`) is still present with full contents; the new path (e.g. `.submodules/AISE/Honeywell/Vulcan`) may exist as an empty or placeholder directory.
- **`git submodule status`:** The new submodule shows with a `-` prefix (not initialized). The old path no longer appears in the list.
- **`.git/config`:** Still contains the old `[submodule "AISE/Honeywell/Anaconda"]` block. Pull does **not** remove it; only `.gitmodules` and the index are updated.

### Preserving untracked files (required — do not skip)

**You must save all untracked files before removing the old submodule directory.** There is no in-process recovery: once you delete the old directory, any unsaved files are permanently lost. This process does **not** rely on Dropbox or any other external backup.

- Save to a backup archive in the parent repo (e.g. under `.git/`), then restore into the renamed submodule after init. The backup is never committed.
- **Use `git ls-files --others` only — do NOT add `--exclude-standard`.** If you use `--exclude-standard`, files matched by `.gitignore` (e.g. personal notes, `* [Otter AI].txt` transcripts) are excluded from the backup and will be **permanently lost** when you remove the old submodule directory.

**Variables** (set once at parent repo root; use your actual old/new submodule paths):

```bash
# From parent repo root
OLD_SUBMODULE="<old-path>"   # e.g. .submodules/AISE/Honeywell/Anaconda or vendor/foo
NEW_SUBMODULE="<new-path>"   # e.g. .submodules/AISE/Honeywell/Vulcan or vendor/bar
BACKUP_SLUG="<slug>"         # safe identifier for backup files, e.g. AISE-Honeywell-Anaconda
BACKUP_TAR=".git/backup-${BACKUP_SLUG}-untracked.tar"
BACKUP_LIST=".git/backup-${BACKUP_SLUG}-untracked-list.txt"
# UP_TO_ROOT = path from inside the submodule dir back to parent repo root (one "../" per path segment in OLD_SUBMODULE)
# Set manually (e.g. "a/b/c" -> "../../../") or derive from OLD_SUBMODULE:
UP_TO_ROOT="$(echo "$OLD_SUBMODULE" | sed 's|[^/]*|..|g')/"
```

**Save untracked files** (run from parent repo root, **before** removing the old submodule):

```bash
cd "$OLD_SUBMODULE"
# Do NOT use --exclude-standard: that would exclude .gitignore-matched files and they would be lost.
git ls-files --others > "${UP_TO_ROOT}${BACKUP_LIST}.tmp"
mv "${UP_TO_ROOT}${BACKUP_LIST}.tmp" "${UP_TO_ROOT}${BACKUP_LIST}"
if [ -s "${UP_TO_ROOT}${BACKUP_LIST}" ]; then
  tar -cf "${UP_TO_ROOT}${BACKUP_TAR}" -T "${UP_TO_ROOT}${BACKUP_LIST}"
else
  touch "${UP_TO_ROOT}${BACKUP_TAR}"
fi
cd "$UP_TO_ROOT"
```

**Verify backup before proceeding:** Ensure `$BACKUP_TAR` and `$BACKUP_LIST` exist (e.g. `ls -la "$BACKUP_TAR" "$BACKUP_LIST"`). Optionally `wc -l "$BACKUP_LIST"` to see how many untracked paths were saved. **Do not remove the old submodule directory until this is done.**

Paths in the list and tarball are relative to the old submodule root, so they restore correctly under the new submodule root. If there are no untracked files, the tarball is empty and the list is empty; restore is a no-op.

**Restore untracked files** (run from parent repo root, after the new submodule is initialized and the old directory removed):

```bash
cd "$NEW_SUBMODULE"
if [ -s "${UP_TO_ROOT}${BACKUP_LIST}" ]; then
  tar -xf "${UP_TO_ROOT}${BACKUP_TAR}"
fi
cd "$UP_TO_ROOT"
```

**Optional:** After verifying the new submodule, remove the backup:
`rm -f "$BACKUP_TAR" "$BACKUP_LIST"`

### Steps after pulling a submodule rename

**CRITICAL — save first, remove later:** Do **not** remove the old submodule directory (step 4) until you have run step 1 and verified the backup tarball and list exist. If you remove the old directory first, ignored untracked files (e.g. in `.gitignore`) will be **permanently lost**. This process does not rely on Dropbox or other recovery.

1. **Save untracked files (required — do not skip)**
   Set the variables above, then run the "Save untracked files" block from "Preserving untracked files" above. Verify that `$BACKUP_TAR` and `$BACKUP_LIST` exist before continuing. Only then proceed to step 2.

2. **(Optional) Preserve uncommitted *tracked* work**
   If you have unstaged or uncommitted changes to *tracked* files:
   ```bash
   cd "$OLD_SUBMODULE"
   git status
   git branch -v
   ```
   - **Option A — stash:** `git stash -u` (later, after init, `cd` into the new submodule and `git stash pop` only if the same commit is checked out; otherwise the stash is lost when you remove the old `.git/modules/...`).
   - **Option B — full directory backup:** From parent repo: `mv "$OLD_SUBMODULE" "${OLD_SUBMODULE}-backup-$(date +%Y%m%d)"`. Then init the new submodule, and copy any files you need from the backup into the new path before deleting the backup.
   - **Option C — commit in the submodule:** Commit (and push) from inside the old submodule dir so the work is on the remote; then pull it in the new clone.
   If you have no important uncommitted tracked work, skip this step.

3. **Initialize and update the new submodule** (clone and checkout at the new path):
   ```bash
   git submodule update --init "$NEW_SUBMODULE"
   ```

4. **Remove the old submodule working directory** (only if you did not keep a full backup in step 2):
   ```bash
   rm -rf "$OLD_SUBMODULE"
   ```

5. **Remove the old submodule's Git metadata:**
   The path under `.git/modules/` matches the submodule **key** from `.gitmodules` (e.g. `AISE/Honeywell/Anaconda`), not necessarily the filesystem path. Remove that directory:
   ```bash
   rm -rf .git/modules/<old-submodule-key>
   ```
   Example: if your old entry was `[submodule "AISE/Honeywell/Anaconda"]`, run `rm -rf .git/modules/AISE/Honeywell/Anaconda`. For a flat path like `[submodule "vendor/foo"]`, run `rm -rf .git/modules/vendor/foo`.

6. **Remove the stale submodule entry from local config**
   Edit `.git/config` and delete the `[submodule "<old-submodule-key>"]` block (the three lines: section header, `active = true`, and `url = ...`). The key is the same as in `.gitmodules` (e.g. `AISE/Honeywell/Anaconda` or `vendor/foo`).

7. **Restore untracked files into the renamed submodule**
   Run the "Restore untracked files" block from "Preserving untracked files" above (same variables). This extracts the saved tarball into `$NEW_SUBMODULE`.

8. **Update symlink if you use one**
   If you had a symlink pointing at the old path, remove it and create one for the new path (adjust link path and target to your layout):
   ```bash
   rm -f <path-to-old-symlink>
   ln -s <relative-path-to-new-submodule> <path-to-new-symlink>
   ```

9. **Verify:**
   ```bash
   git submodule status
   ls "$(dirname "$NEW_SUBMODULE")"
   cd "$NEW_SUBMODULE"
   git status
   ```
   You should see the new submodule initialized and, if you restored, the former untracked files (including ignored ones) listed as untracked again.

### Optional: align config with .gitmodules

Running `git submodule sync` after pull updates `.git/config` from `.gitmodules`. It will not re-add the old submodule entry (since it's gone from `.gitmodules`). If you already removed the old block and initialized the new submodule, sync is optional.

---

## Important Notes

- **Recipient workflow — save-first is mandatory:** Do **not** remove the old submodule directory until you have run "Save untracked files" and verified the backup tarball and list exist. Use `git ls-files --others` only (never `--exclude-standard`). There is no in-process recovery for files lost by removing the old directory before saving; this process does not rely on Dropbox or any other external backup.
- **Always preserve uncommitted work:** This process moves directories, so all uncommitted changes are preserved when you follow it.
- **Relative paths matter:** The `.git` file and `worktree` paths use relative paths - ensure they're calculated correctly
- **Case sensitivity:** On case-insensitive filesystems (Windows, Mac default), be careful with case-only renames
- **Commit the changes:** After moving, commit the updated `.gitmodules` file to make the change permanent
