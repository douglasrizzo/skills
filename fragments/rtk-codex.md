# RTK - Rust Token Killer (Codex)

**Usage**: Token-optimized CLI proxy. Always prefix shell commands with `rtk`.

## Rule

```bash
rtk git status        rtk git diff
rtk gh pr view        rtk gh run view
rtk uv run pytest     rtk uv run ruff check .
rtk ls                rtk which <cmd>
```

## Meta commands

```bash
rtk gain              # Token savings analytics
rtk gain --history    # Command usage history with savings
rtk proxy <cmd>       # Run raw command without RTK filtering (debugging)
```

## Verification

```bash
rtk --version
rtk gain
which rtk
```
