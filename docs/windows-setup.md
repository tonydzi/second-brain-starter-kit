# Windows & PowerShell Setup and Troubleshooting Guide

This guide covers setup, environment configuration, and common troubleshooting steps for running the Second Brain starter kit, AI CLI tools (Claude Code, Gemini CLI, Codex), and Model Context Protocol (MCP) servers on Windows using PowerShell.

---

## 1. PowerShell Execution Policy

### The Issue
By default, Windows restricts running PowerShell scripts (`.ps1`). When executing installation scripts or package runners, you may encounter:
```text
File C:\Users\<Username>\AppData\Roaming\npm\<script>.ps1 cannot be loaded because running scripts is disabled on this system.
```

### Solution
Allow signed and local scripts for the current user without requiring Administrator privileges:

```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned -Force
```

To verify your configuration:
```powershell
Get-ExecutionPolicy -List
```

If you need a one-off execution without changing system policies, launch PowerShell with bypass:
```powershell
powershell -ExecutionPolicy Bypass -File .\script.ps1
```

---

## 2. Node.js, npm, and Environment PATH Management

### The Issue
Global npm packages (such as `@anthropic-ai/claude-code`, Gemini CLI, or MCP servers) install successfully, but running them returns:
```text
'<command>' is not recognized as an internal or external command, operable program or batch file.
```

### Diagnosing Global npm Path
Check where npm places global binaries:
```powershell
npm config get prefix
```
On Windows, the default directory is typically:
```text
%APPDATA%\npm  (e.g., C:\Users\<Username>\AppData\Roaming\npm)
```

Verify whether this path is present in your session `$env:PATH`:
```powershell
$env:Path -split ';' | Where-Object { $_ -like '*npm*' }
```

### Refreshing PATH in Current PowerShell Session
Installers update the registry, but existing terminal sessions do not automatically inherit updated environment variables. Instead of restarting your entire terminal or PC, refresh `$env:Path` in-place:

```powershell
$env:Path = [Environment]::GetEnvironmentVariable('Path','Machine') + ';' +
            [Environment]::GetEnvironmentVariable('Path','User')
```

### Persistently Adding npm to User PATH
If `%APPDATA%\npm` is missing from your User PATH:

```powershell
$npmPath = Join-Path $env:APPDATA 'npm'
$userPath = [Environment]::GetEnvironmentVariable('Path', 'User')

if ($userPath -split ';' -notcontains $npmPath) {
    [Environment]::SetEnvironmentVariable('Path', "$userPath;$npmPath", 'User')
    $env:Path += ";$npmPath"
    Write-Host "Added $npmPath to User PATH."
}
```

---

## 3. MCP (Model Context Protocol) Server Configuration

MCP servers require configuration files specifying command executables and environment variables. On Windows, path syntax and file locations differ from Unix systems.

### Configuration File Locations

| Tool | Windows Config Path | Environment Variable Equivalent |
|---|---|---|
| **Claude Desktop** | `%APPDATA%\Claude\claude_desktop_config.json` | `$env:APPDATA\Claude\claude_desktop_config.json` |
| **Claude Code** | `%USERPROFILE%\.claude.json` / `%USERPROFILE%\.claude\` | `$env:USERPROFILE\.claude.json` |
| **Gemini CLI** | `%USERPROFILE%\.gemini\` | `$env:USERPROFILE\.gemini\` |

### Path Formatting in JSON
In JSON files on Windows:
- Always escape backslashes: `"C:\\Users\\<Username>\\AppData\\Roaming\\npm\\npx.cmd"`
- Alternatively, use forward slashes: `"C:/Users/<Username>/AppData/Roaming/npm/npx.cmd"`
- When referencing Windows commands like `npx`, point directly to `npx.cmd` if the client process fails to resolve batch files.

### Example MCP Configuration (`claude_desktop_config.json`)
```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "C:/Users/<Username>/Obsidian/Brain"
      ]
    },
    "custom-python-mcp": {
      "command": "python",
      "args": [
        "C:/Users/<Username>/lab/kit/tools/mcp_server.py"
      ],
      "env": {
        "PYTHONUTF8": "1"
      }
    }
  }
}
```

---

## 4. Windows & PowerShell Quick Troubleshooting Checklist

### A. PowerShell 5.1 vs PowerShell 7+ Chaining
- **Problem**: `command1 && command2` throws a parse error in Windows PowerShell 5.1.
- **Fix**: Use conditional branching in PS 5.1:
  ```powershell
  command1; if ($?) { command2 }
  ```
  Or upgrade to PowerShell 7 (`winget install --id Microsoft.PowerShell -e`).

### B. Python Store Alias ("0 KB Python.exe")
- **Problem**: Running `python` opens the Microsoft Store instead of Python.
- **Fix**: Disable Microsoft Store app execution aliases:
  1. Open Windows **Settings** → **Apps** → **Advanced app settings** → **App execution aliases**.
  2. Toggle off both `python.exe` and `python3.exe`.
  3. Or invoke python explicitly using the Windows Python launcher: `py -3`.

### C. UTF-8 File Encoding
- **Problem**: Non-ASCII characters (e.g., Cyrillic notes or unicode prompts) turn into mojibake / corrupted symbols.
- **Fix**: Windows PowerShell 5.1 defaults to ANSI or UTF-16 with `Out-File` and `Set-Content`. Always specify `-Encoding utf8`:
  ```powershell
  Set-Content -Path "note.md" -Value "Текст" -Encoding utf8
  Add-Content -Path "note.md" -Value "Строка" -Encoding utf8
  ```
  Set session encoding in your profile:
  ```powershell
  [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
  $OutputEncoding = [System.Text.Encoding]::UTF8
  ```

### D. Symlinks vs Directory Junctions
- **Problem**: Creating symbolic links (`New-Item -ItemType SymbolicLink`) requires Administrator privileges or Developer Mode enabled.
- **Fix**: Use Directory Junctions instead for folders; junctions do not require elevation:
  ```powershell
  New-Item -ItemType Junction -Path "$env:USERPROFILE\.claude\skills" -Target "$env:USERPROFILE\lab\kit\skills"
  ```

### E. MAX_PATH Limitations (260 Characters)
- **Problem**: Node/npm deeply nested dependencies fail with path-too-long errors.
- **Fix**: Keep workspace repositories close to root (e.g. `C:\lab` or `%USERPROFILE%\lab`). To enable long path support in Windows:
  ```powershell
  Set-ItemProperty -Path 'HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem' -Name 'LongPathsEnabled' -Value 1
  ```
  *(Requires Administrator privileges).*
