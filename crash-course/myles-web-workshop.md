# "Ship a Site" Workshop
### GitHub + AI + Cloudflare — building and selling small business websites

**Instructor:** Jeremiah Cargill
**Student:** Myles
**Format:** 3 sessions × ~2 hrs, or one 6-hour Saturday with breaks
**Goal:** By the end, Myles can walk into a business, pitch, and deliver a live, custom-domain website in under a day — repeatably, for near-zero hosting cost.

---

## Why this stack

Myles is already doing the hard part: walking in the door and asking for the business. What he needs is a delivery method that is:

| Requirement | How this stack solves it |
|---|---|
| Cheap enough to profit at $500–$1,500/site | GitHub Pages hosting = $0. Cloudflare DNS = $0. Domain ≈ $10–12/yr at cost. |
| Fast enough to close and deliver same week | AI generates the site; you review and commit. |
| Editable without being a developer | AI makes the edits; GitHub keeps every version. |
| Doesn't break when he's not looking | Static HTML — nothing to patch, nothing to hack, no WordPress plugin hell. |
| Recurring revenue | Maintenance retainer, content updates, domain/email management. |

**The honest limitation, say it out loud:** static sites don't do e-commerce carts, logins, or databases out of the box. That's fine — 80% of small businesses need a brochure site with hours, services, photos, and a contact button. Know where the ceiling is so you don't oversell.

---

# SESSION 1 — Foundations (2 hrs)

## 1.1 How a website actually works (30 min, whiteboard, no computers)

Draw this. Make Myles draw it back to you.

```
   Customer types:  joesbarbershop.com
            │
            ▼
   ┌─────────────────┐
   │   DNS lookup    │  ← "What's the address for this name?"
   │  (Cloudflare)   │     Cloudflare answers.
   └────────┬────────┘
            │  returns an IP
            ▼
   ┌─────────────────┐
   │  Web host       │  ← "Give me the files."
   │ (GitHub Pages)  │     Serves index.html, CSS, images
   └────────┬────────┘
            │
            ▼
   Browser renders the page
```

**The three things a client is actually buying:**
1. **A domain** — the name. Rented yearly. (Cloudflare Registrar)
2. **Hosting** — the computer that hands out the files. (GitHub Pages)
3. **The site itself** — the files. (Built with AI, stored in GitHub)

**Teaching check:** Ask Myles — "If a client says 'my website is down,' what are the three places you look?" He should be able to name DNS, hosting, and the files.

**Vocabulary card** (make him keep this):
- **Domain** — the name you rent
- **DNS** — the phone book that maps name → server
- **A record** — points a name at an IP address
- **CNAME** — points a name at *another name*
- **Repo (repository)** — a folder of files with full history
- **Commit** — a saved snapshot with a note about what changed
- **Push** — send your commits up to GitHub
- **Deploy** — make the files live on the internet
- **Static site** — plain HTML/CSS/JS, no server-side code
- **SSL/TLS** — the padlock; the "s" in https

## 1.2 GitHub from zero (45 min, hands-on)

Do this live, together, on his machine.

1. Create the GitHub account. Use a professional username — it will show up in URLs. `mylesbuilds`, not `myles420xd`.
2. Turn on 2FA immediately. Non-negotiable — this account will hold client property.
3. Create a repo: `test-site`. Public. Check "Add a README."
4. Edit the README in the browser. Commit. Show him the commit history.
5. **Break something on purpose.** Delete half the README, commit it, then revert the commit. This is the single most important confidence-builder — he needs to feel that *nothing he does is permanent*.

**The mental model to install:** GitHub is not "for programmers." It's a filing cabinet that remembers every version of every file and never loses anything. That's it.

## 1.3 GitHub Pages — first site live (30 min)

1. In `test-site`, create a file called `index.html`.
2. Paste in a minimal page:
   ```html
   <!DOCTYPE html>
   <html>
   <head><title>It works</title></head>
   <body><h1>Myles was here</h1></body>
   </html>
   ```
3. Settings → Pages → Source: `Deploy from a branch` → `main` / `/ (root)` → Save.
4. Wait 60 seconds. Visit `https://<username>.github.io/test-site/`.

**He now has a live website on the internet.** Stop and let that land. That moment is the whole hook of the class.

5. Change the `<h1>`, commit, refresh in a minute. Show that edit → commit → live is the entire loop.

## 1.4 Session 1 homework
- Create a second repo named exactly `<username>.github.io` (this one publishes at the root URL — his portfolio).
- Put a one-page "about me / what I build" page there.
- Come to Session 2 with the name of one real local business he wants to build a demo for.

---

# SESSION 2 — Building with AI (2 hrs)

## 2.1 The three ways to get AI-generated code into GitHub

Teach all three. He'll use #1 to learn and #2 or #3 to earn.

**Method 1 — Copy/paste (start here)**
Prompt the AI → it outputs `index.html` → he copies it → pastes into GitHub's web editor → commits.
Slow, but zero setup and he sees every step. Use this for the first two sites.

**Method 2 — AI connected directly to the repo**
Both Claude and ChatGPT can be connected to GitHub so the AI reads the repo and proposes changes directly — Claude via its GitHub connector or Claude Code, ChatGPT via its GitHub integration. Setup: authorize the connector, grant access to only the specific repos, then ask in plain English: *"In the joes-barbershop repo, update the hours section — they're now closed Mondays and open until 7 on Fridays."*

> Connector names and capabilities change frequently. Before the session, verify the current setup steps in the live docs rather than trusting a screenshot from six months ago. Grant repo access narrowly — never blanket "all repositories" on an account holding client work.

**Method 3 — Local clone + AI coding tool**
Clone the repo to his laptop, run an agentic coding tool in that folder, let it edit files and push. Fastest for real work. This is a Session 3 stretch goal, not a day-one skill.

## 2.2 Prompting for websites — the part most people get wrong

Bad prompt: *"Make me a website for a barbershop."*
Result: generic purple gradient template that looks like every AI site on earth.

**The intake-to-prompt method.** Have him collect these from the client *before* he touches a keyboard:

- Business name, tagline, what they actually do (in the owner's words)
- Address, phone, email, hours
- 5–10 real photos (phone photos are fine; stock photos kill credibility)
- Services + prices (or "call for pricing")
- Social links, Google Business profile link
- 2–3 real reviews to quote
- Two competitor sites they like, two they hate, and *why*
- Their existing logo and colors, if any

**Prompt skeleton to memorize:**

```
Build a single-file index.html for [BUSINESS], a [TYPE] in [CITY].

Audience: [who walks in the door]
Goal: get visitors to [call / book / visit]

Sections, in order:
  hero with tagline + big call button
  services with prices
  about (use this copy: "...")
  gallery placeholders for 6 photos
  reviews (3 quoted below)
  hours + address + embedded map link
  footer with phone, email, socials

Style: [e.g. "dark, industrial, heavy sans-serif — think
motorcycle shop, not tech startup"]. Not generic. No purple
gradients. No lorem ipsum — use the real copy below.

Requirements:
  - single self-contained HTML file, inline CSS
  - mobile-first, must look right on a phone
  - click-to-call links (tel:) on every phone number
  - semantic HTML, alt text on images
  - loads fast, no heavy frameworks

Real content:
[paste the intake sheet]
```

**Then iterate.** Never accept the first output. Teach the follow-up muscle:
- "The hero is too tall on mobile — cut it to 60vh."
- "Make the call button sticky at the bottom on phones."
- "The gold is too yellow, go more brass."

## 2.3 Live lab (45 min)
Myles builds the demo site for the real business he picked, start to finish, in a new repo, live on GitHub Pages. Jeremiah coaches but doesn't touch the keyboard.

## 2.4 Session 2 homework
Build a second demo — different industry, different visual style. The point is proving to himself that the stack isn't one template.

---

# SESSION 3 — Domains, DNS, and delivering to a paying client (2 hrs)

## 3.1 Cloudflare account + domain (30 min)

1. Create Cloudflare account, enable 2FA.
2. **Register a domain through Cloudflare Registrar.** Key selling point: Cloudflare sells domains at cost with no first-year bait pricing and no renewal gouging. Compare a `.com` price there vs. a big-box registrar in front of him — the difference is his margin.
3. If the client already owns a domain elsewhere, you either (a) transfer it in, or (b) leave it registered where it is and just point its nameservers at Cloudflare. Option (b) is faster and less scary for a nervous client.

**Client-ownership rule — teach this as ethics, not just process:** the domain should be registered in the *client's* name and, ideally, their own account with Myles added as a user. Holding a client's domain hostage is how you get a reputation you can't outrun. Put it in writing: *"You own your domain. I manage it for you."*

## 3.2 Pointing a domain at GitHub Pages (45 min, hands-on)

In the repo: Settings → Pages → Custom domain → enter `joesbarbershop.com` → Save. This creates a `CNAME` file in the repo.

In Cloudflare DNS, add:

| Type | Name | Value |
|---|---|---|
| A | `@` | `185.199.108.153` |
| A | `@` | `185.199.109.153` |
| A | `@` | `185.199.110.153` |
| A | `@` | `185.199.111.153` |
| CNAME | `www` | `<username>.github.io` |

> Verify these IPs against GitHub's current Pages documentation before every deployment — they have changed before and will change again. Never teach an IP as permanent truth.

**The Cloudflare proxy gotcha — this is where beginners lose an afternoon.** Cloudflare's orange-cloud proxy sits in front of the origin. Combined with GitHub Pages issuing its own certificate, you can get redirect loops or cert errors.

Teach the safe default:
1. Set the records to **DNS only** (grey cloud) first.
2. Wait for GitHub Pages to show the cert as issued, then check **Enforce HTTPS** in repo settings.
3. *Only then*, if you want Cloudflare's CDN and analytics, flip the proxy on — and make sure Cloudflare SSL/TLS mode is **Full** or **Full (strict)**, never "Flexible." Flexible causes infinite redirect loops with Pages.

**Debugging drill — do this live.** Deliberately break it, then fix it:
- Delete one A record → see what happens.
- Set SSL mode to Flexible → watch the redirect loop → fix it.
- `dig joesbarbershop.com` and `nslookup` from terminal so he can prove where a problem lives.

**DNS propagation reality check:** it's usually minutes on Cloudflare, but tell clients "up to 24 hours" so you're never the one who was wrong.

## 3.3 Cloudflare extras that become upsells (20 min)
- **Email Routing** — free. `info@joesbarbershop.com` forwards to their Gmail. Client thinks this is magic. It takes four minutes.
- **Analytics** — free, privacy-friendly traffic numbers. Perfect for the monthly report that justifies a retainer.
- **Cloudflare Pages** (level-2 path) — connects to a GitHub repo and handles build + hosting + DNS in one platform. Worth showing him as the natural next step once he's comfortable, especially if he ever needs build steps or serverless forms.

## 3.4 The delivery workflow (25 min)

Write this on a card. It's the repeatable process.

```
1. INTAKE      — 20-min sit-down, fill the intake sheet, collect photos
2. QUOTE       — package + price + what's included, in writing
3. DEPOSIT     — 50% up front, before you build. Always.
4. BUILD       — AI draft → your revisions → 2 rounds with client
5. DOMAIN      — register/point, in client's name
6. GO LIVE     — DNS, HTTPS, test on a real phone
7. HANDOFF     — walkthrough, credentials doc, "how to request changes"
8. BALANCE     — collect the other 50%
9. RETAIN      — monthly maintenance, or per-change pricing
```

**Pre-launch checklist:**
- [ ] Loads on iPhone and Android, not just his laptop
- [ ] Every phone number is a `tel:` link
- [ ] Address links to Google Maps
- [ ] Padlock shows; `http://` redirects to `https://`
- [ ] Both `domain.com` and `www.domain.com` work
- [ ] Page title and meta description written (not "Document")
- [ ] Favicon set
- [ ] Contact form or call button actually works — test it
- [ ] Real photos, no stock, no placeholders
- [ ] No typos in the business name or phone number (check twice)

---

# Packaging and pricing (discuss, don't lecture)

Rough starting frame for his market — he should adjust to what people actually pay locally:

| Package | Includes | Ballpark |
|---|---|---|
| **Starter** | 1-page site, domain setup, HTTPS, click-to-call, mobile | $500–$800 |
| **Standard** | 4–5 pages, gallery, contact form, email routing, Google Business setup | $1,000–$1,800 |
| **Care plan** | Hosting managed, monthly edits, domain renewal, analytics report | $50–$150/mo |

**Costs to him:** domain ~$10/yr, hosting $0, his time. That's the whole pitch — margin lives in speed, not markup.

**The two things that will bite him:**
1. **Scope creep.** "Can you also add online booking / a shop / a member login?" — that's a different product. Quote it separately or say no.
2. **Getting paid.** Deposit up front, balance before final handoff of credentials. Not after.

---

# What to bring / setup before the class

**Myles brings:** laptop (not a phone), charger, email address he actually checks, a payment method for domain purchase, and the name of one real local business.

**Jeremiah has ready:** GitHub and Cloudflare accounts open on a projector or shared screen, one throwaway domain to demo DNS live, the printed vocabulary card and delivery checklist, and one deliberately broken site to debug together.

---

# Stretch topics (Session 4, if he's hungry)

- Git on the command line: `clone`, `add`, `commit`, `push`, branches, pull requests
- A reusable starter template repo so site #10 takes an hour instead of a day
- Form handling on a static site (form services, or Cloudflare Workers)
- Google Business Profile + basic local SEO — often worth more to the client than the site
- Cloudflare Workers for lightweight dynamic features
- Building a config-driven generator so one JSON file spins up a whole branded site

---

# The one thing to say at the end

The stack isn't the moat. Anybody can watch a video on GitHub Pages. What Myles already has that most people building websites don't is that **he walks in the door and asks.** The tech just makes sure he can say yes when they say yes.
