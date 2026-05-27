---
name: nbsc-downstream-verify
description: Use after updating the nbsc library to deploy it on secondvds and verify that okama-scripts inflation updater (CNY.INFL) works without 403 errors. Covers poetry install, manual run, log checks, and systemd timer verification.
---

# NBSC Downstream Verify

Deploy an updated nbsc library to secondvds and verify the okama-scripts inflation pipeline works.

## When to Use

- After completing changes to nbsc (any stage of the update plan)
- After bumping nbsc version in `pyproject.toml`
- When checking if the CNY.INFL daily updater has recovered after a fix

## Deployment Steps

### 1. SSH to secondvds and navigate to okama-scripts

```bash
ssh secondvds
cd /var/www/scripts/okama-scripts
```

### 2. Update nbsc dependency

```bash
# Activate the okama-scripts venv
source $(poetry env info -p)/bin/activate

# If nbsc is installed from local path:
pip install -e /path/to/nbsc

# If nbsc is installed from git:
pip install --upgrade git+https://github.com/mbk-dev/nbsc.git@master
```

### 3. Run inflation updater manually

```bash
cd /var/www/scripts/okama-scripts
python -m src.database.inflation 2>&1 | tee /tmp/nbsc-verify.log
```

Check output for:
- **Success:** `CNY.INFL` row updated without errors
- **Failure:** `Error while updating CNY.INFL: 403` or `ConnectionError` or `KeyError`

### 4. Check error logs

```bash
# Recent error files
ls -lt /var/www/scripts/log/update_inflation/ | head -5

# Check latest errors file for CNY.INFL
grep -i "CNY.INFL\|403\|nbsc" /var/www/scripts/log/update_inflation/*_errors.txt | tail -20
```

### 5. Verify systemd timer

```bash
# Check timer status
systemctl status okama-inflation.timer
systemctl status okama-inflation.service

# Check recent journal
journalctl -u okama-inflation.service --since "1 hour ago" --no-pager
```

## Acceptance Criteria

All must pass:

- [ ] `python -m src.database.inflation` exits 0
- [ ] No `403` or `Error while updating CNY.INFL` in output
- [ ] CPI value for latest month is reasonable (99-105 range for YoY index)
- [ ] `/var/www/scripts/log/update_inflation/*_errors.txt` has no new CNY.INFL errors
- [ ] `okama-inflation.service` shows successful last run (or next scheduled run succeeds)

## Rollback

If the new nbsc breaks other series:

```bash
ssh secondvds
cd /var/www/scripts/okama-scripts
pip install nbsc==0.1.x  # previous working version
```

## Common Issues

- **`ModuleNotFoundError: nbsc`** — wrong venv activated. Check `which python` points to the okama-scripts poetry venv.
- **`KeyError: 'A01010G01'`** — `codes.json` is missing this legacy code mapping. Run nbs-data-discovery to fill it.
- **`ConnectionError` to data.stats.gov.cn** — NBS may be temporarily down or blocking the server IP. Try through proxy: check if `use-proxy` skill applies.
- **Timer not firing** — check `systemctl list-timers --all | grep inflation` for next trigger time.
