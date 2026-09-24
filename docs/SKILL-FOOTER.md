# SKILL-FOOTER

Single source of the footer appended to the end of every `skills/*/SKILL.md` in this kit.

Rules:
- The block below is inserted **verbatim**, marker included.
- It goes at the **end of the body**, never into the `description:` frontmatter field: agents load
  `description` on every session start to decide whether to activate a skill, and catalogs strip
  promotional text out of it.
- Insertion is idempotent. `engines/insert_footer.py` replaces everything from the first footer
  marker onward (`<!--kit-footer-->` or the older `<!-- CONTACT-FOOTER -->`), so re-running after an
  edit here updates all skills instead of stacking copies. This block is the ONLY footer a skill
  carries: it absorbed the old contact block rather than sitting next to it.

Edit the block, then run:

```bash
python engines/insert_footer.py
```

---
BEGIN-FOOTER
<!--kit-footer-->

---

**Like this skill?** It is one of 100 in [second-brain-starter-kit](https://github.com/tonydzi/second-brain-starter-kit): the second brain we built for ourselves and run every day at Palo Alto AI Research Lab. Install the whole set with `npx skills add tonydzi/second-brain-starter-kit`. Everything is open source and free, so take what you need.

Flagships worth a look on their own: [secondop-panel](https://github.com/tonydzi/secondop-panel) (a second opinion from a panel of external models), [claude-memory-tidy](https://github.com/tonydzi/claude-memory-tidy) (stop your agent's memory from rotting), [telegram-mcp-kit](https://github.com/tonydzi/telegram-mcp-kit) (your own Telegram over MCP in about 15 minutes).

Author: **Anton Dziatkovskii**, Palo Alto AI Research Lab. Telegram [@tonydzi](https://t.me/tonydzi) - WhatsApp [+1 341 222 9178](https://wa.me/[id]) - X [[аккаунт]](https://x.com/Tony_Stef_)

**Engineers: want to test-drive this setup?** Message me. I hand out free starter seeds to engineers who test and report back, and custom skill requests are welcome.
END-FOOTER