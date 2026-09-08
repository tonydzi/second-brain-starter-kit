# Paths: what to change before you run anything

This kit was extracted from one running fleet (Windows desktops, a MacBook, a Linux anchor). The
**method** is portable; the **paths** are not. Nothing here auto-detects your machine.

## Placeholders used in the skills

Skill documentation uses these placeholders instead of the original drive letters. Substitute your
own locations, or export the matching environment variables and let your agent expand them.

| Placeholder | What it is | Typical value |
|---|---|---|
| `$VAULT_ROOT` | The Obsidian vault the second brain lives in | `~/Obsidian/My-Knowledge` |
| `$IMPORTS_ROOT` | Scratch + engine directory next to the vault | `~/Obsidian/_imports` |
| `<GDRIVE_ROOT>` | Mounted cloud-drive folder used for offsite backup | `~/Google Drive` |
| `<GDRIVE_ROOT_2>` | Second cloud-drive account, if you run one | `D:\GoogleDrive` |
| `<LOCAL_BACKUP_DIR>` | Second local disk holding the backup copy | `D:\ObsidianBackup` |
| `<GITHUB_ROOT>` | Where your git checkouts live | `~/GitHub` |
| `<CRM_REPOS_ROOT>` | Read-only checkouts of the CRM repos | `~/GitHub/crm` |
| `<TELEGRAM_MCP_DIR>` | Checkout of the Telegram MCP server | `~/mcp/telegram-mcp` |
| `<TG_WATCH_DIR>` | Telegram watch daemon | `~/mcp/tg-watch-daemon` |
| `<AUTOMATION_BROWSERS_ROOT>` | Dedicated browser profiles for automation | `~/AutomationBrowsers` |
| `<MIGRATION_DRIVE>` | External disk used when moving the hub role | any removable drive |

## The engines are a different story

Scripts under `engines/` still carry the original absolute paths as module-level constants. They are
published as **reference implementations**, not as a turnkey install: read one, take the logic, and
point it at your own directories. Every such file starts with a one-line note saying so.

Cleaning all of them into environment lookups would be a rewrite of working code with no test suite
on your side to catch the breakage, which is a worse trade than an honest label. If you adapt one,
a pull request is welcome.

## Skills are the portable part

The 100 `skills/*/SKILL.md` files are the product. They describe procedure, gates and verdicts, and
most of them touch no absolute path at all.
