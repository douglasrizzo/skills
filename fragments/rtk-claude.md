# RTK - Rust Token Killer (Claude Code)

**Usage**: Token-optimized CLI proxy (60–90% savings on dev operations).

## Hook-based usage

All shell commands are automatically rewritten by the `PostToolUse` hook:

```
git status  →  rtk git status   (transparent, zero token overhead)
```

Do **not** prefix commands manually — the hook handles it.

## Meta commands (use rtk directly)

```bash
rtk gain              # Token savings analytics
rtk gain --history    # Command usage history with savings
rtk discover          # Analyze session history for missed opportunities
rtk proxy <cmd>       # Run raw command without RTK filtering (debugging)
```

## Verification

```bash
rtk --version         # Should show: rtk X.Y.Z
rtk gain              # Should work (not "command not found")
which rtk             # Verify correct binary
```

> **Name collision:** If `rtk gain` fails, you may have `reachingforthejack/rtk`
> (Rust Type Kit) installed instead of Rust Token Killer.
