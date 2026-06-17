# Package Age Guard (Supply Chain Security)

**Mandate:** Never install a third-party package that was first published or last republished within the last 14 days. The supply-chain worm wave of 2025-2026 (npm `chalk`, `debug`, `is-arrayish`, `shai-hulud`, PyPI `colorama` typo-squats, Crates `serde-malicious-impl`) has made fresh-publish-then-exfiltrate the dominant attack vector. Caught within 14 days, almost always. Not caught before that.

This rule is non-negotiable. Bypass only with explicit one-line user authorization, recorded in the PR description.

---

## 1. Pre-install check (mandatory before any new dep)

Before running `npm install <pkg>`, `pip install <pkg>`, `cargo add <pkg>`, `go get <pkg>`, `gem install <pkg>`, or `pnpm add <pkg>`, run the appropriate age check:

### npm / pnpm / yarn

```bash
npm view <pkg> time.modified time.created
# Verify both 'created' and 'modified' are > 14 days ago
```

### pip / uv

```bash
# Fetches release history
pip index versions <pkg> 2>/dev/null
# Or use the JSON API for first/last upload time
curl -s https://pypi.org/pypi/<pkg>/json | jq '.releases | to_entries | sort_by(.value[0].upload_time) | .[-1].value[0].upload_time'
```

### cargo

```bash
cargo info <pkg>  # cargo >= 1.80
# Or use crates.io API
curl -s https://crates.io/api/v1/crates/<pkg> | jq '.crate.updated_at, .crate.created_at'
```

### go

```bash
go mod download -x <pkg>@latest 2>&1 | head -5
# Then check the proxy for publish date
curl -s "https://proxy.golang.org/<pkg>/@v/<version>.info" | jq '.Time'
```

### gem

```bash
gem search <pkg> -d  # shows date
# Or query rubygems.org/api/v1/gems/<pkg>.json
```

---

## 2. The "look at Twitter" supplementary check

Before installing any package you haven't used before:

1. Search Twitter / X for the package name.
2. Look for posts in the last 7 days flagging it as compromised.
3. Check Hugging Face / Snyk / Socket.dev advisories.

This is fast (under 60 seconds) and catches things even a 14-day delay misses.

---

## 3. If the package fails the age check

Default action: **do not install**. Try in this order:

1. Pin to the previous version that is older than 14 days.
2. Find an alternative package that is older / more established.
3. Vendor the relevant function manually (often the package is 30 lines).
4. Ask the user with: "Package `<name>` is `<X>` days old (younger than 14d guard). Newer than last known safe version `<vN>`. Proceed anyway?"

Only proceed if the user authorizes explicitly in chat. Record the override in the commit message:

```
feat: add <feature>

Bypassed package-age-guard for <pkg>@<version> (published <X> days ago).
Authorized by user in chat <date>. Reason: <e.g. only impl with WebRTC support>.
```

---

## 4. Post-incident sweep (when a CVE drops)

When Twitter / X surfaces a supply-chain incident (e.g. "package `<X>` versions `<a>-<b>` shipped malicious post-install"):

1. Search the project lockfile:
   ```bash
   # npm
   grep -rE '"<pkg>"\s*:\s*"<vulnerable-range>"' package-lock.json pnpm-lock.yaml yarn.lock
   # pypi
   grep -E '^<pkg>==<vulnerable>' requirements*.txt poetry.lock uv.lock
   # cargo
   grep -E 'name = "<pkg>"' Cargo.lock
   ```

2. Search node_modules / site-packages directly for the package:
   ```bash
   find node_modules -type d -name "<pkg>" -maxdepth 4 2>/dev/null
   find ~/.venv*/lib -type d -name "<pkg>" 2>/dev/null
   ```

3. Search OS-wide for trojan signatures the tweet/CVE specifies (often `~/.npmrc`, `~/.ssh`, `~/.aws/credentials` exfiltration).

4. If hit: revoke credentials in that env, force-rotate API keys in `.env`, audit recent commits for leaked secrets, run `git secrets --scan`.

Real-world example: a system one version behind a compromised npm package was scanned clean in minutes. This is fast - do it any time you see a Twitter post about npm/pypi/crates being compromised.

---

## 5. Wire into the agent (system prompt addition)

When kicking off any session that may add dependencies, the agent should self-impose:

> Before any `npm install`, `pip install`, `cargo add`, etc., run the package age check from `.claude/rules/package-age-guard.md`. Block if < 14 days. If blocked, surface to the user with the override prompt template.

This is enforced by the `autonomous-self-healing.md` reflex: a failed age check is classified as `missing_dependency` with a forced-pause variant - install is blocked and the user is consulted.

---

## 6. Why 14 days

- npm worm waves (2025-2026) all detected within 4-12 days by Snyk / Socket / community.
- 14 days = enough margin to catch detections published 1-2 days after the worm.
- Going longer (30 / 60 days) blocks too many legit updates from active packages.
- Going shorter (7 days) misses ~15% of incidents.

If you maintain a list of trusted publishers (`anthropic`, `@anthropic-ai`, `vercel`, `openai`, `stripe`, `cloudflare`, `microsoft`, `google`), they can be exempted with a config file - but only if they signed the package. Default to enforce.

---

## 7. Anti-patterns

- ❌ Installing a "famous" package without checking age. Brand recognition does not equal safety; the brand's account can be hijacked.
- ❌ Trusting "I've used this before" - a hijacked account can ship a malicious version to an existing trusted package.
- ❌ Running `npm audit fix --force` without re-running the age check on the new versions it pulls.
- ❌ Skipping the check on dev-dependencies. Post-install scripts in devDeps are the most common vector.
- ❌ Auto-merging Dependabot / Renovate PRs without age check on each updated package.
