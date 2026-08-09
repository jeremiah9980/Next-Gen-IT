# Module 2 — "Secure & Seen"
### Security + presence for small business · the complete field manual
**Track:** Next-Gen IT field training · Module 2 of 3 · v2 (expanded field edition)
**Prerequisite:** Ship a Site complete — at least one live client site delivered
**Format:** 3 sessions × ~2.5 hrs · every session ends with a graded drill
**Instructor:** Jeremiah Cargill · **Student:** Myles

---

## Why this module exists

Module 1 made Myles a website guy. Website guys are a commodity — every market has five, and the ceiling is a one-time project fee. This module makes him something rarer: the person a business owner calls about *anything with a plug or a password*. That's what a technology company is at the small end — not a product, but a trusted relationship with recurring reasons to exist.

The business logic: a website is bought once; security and presence are *maintained*. Maintained means monthly, monthly means a company instead of a gig. Every skill here maps to a rung on the Next-Gen IT offer ladder, and every one is something the audit portal already measures. Myles isn't learning theory — he's learning to see, explain, and sell what the 30-point audit finds.

**The frame, installed on day one:** small businesses don't buy "cybersecurity" or "SEO." Those words mean nothing at a barbershop counter. They buy *"nobody can steal your money through your email"* and *"people searching for a barber in Georgetown find you first."* This module is learning the real mechanisms well enough to say them in those words — honestly.

**The ethics rail, repeated every session:** we sell protection, never fear. Every risk claim must be true, specific to *their* domain, and demonstrable on the report. The line between security consultant and scareware salesman is whether you can show your evidence. We always can. If Myles ever catches himself exaggerating a finding to close, the deal is off and we talk — one inflated claim costs more reputation than ten lost sales.

## The money model (so Myles knows what he's building toward)

Time-and-margin math per offer, at Option B comp (50% sourced-and-built, 20% sourced-only):

| Offer | Price | Delivery time | Hard cost | Myles' cut (B) | His effective rate |
|---|---|---|---|---|---|
| Security Starter | $400–700 | 3–4 hrs total | ~$0 | $80–140 (20%, J executes DNS) | pitch-only income |
| Presence Pack | $350–600 | 3–5 hrs | ~$0 | $175–300 (50%, his build) | ~$60–75/hr |
| Care Plan upgraded | $100–250/mo | 1–2 hrs/mo | ~$0 | 10% month-one spiff | recurring is company revenue |
| Full Audit + Remediation | $750–2,500 | 6–15 hrs | ~$0 | 20% sourced | biggest single checks |

The picture to hold: **ten care-plan clients at $150/mo is $18k/yr of revenue that renews itself** while new projects stack on top. Every session in this module exists to make that column grow. Websites open the door; this module is the reason the door stays open.

---

# SESSION 1 — Security a small business actually needs (2.5 hrs)

### Run of show
| Time | Segment |
|---|---|
| 0:00–0:35 | 1.1 Threat model + the wire-fraud story |
| 0:35–1:30 | 1.2 Email security deep dive + live lab |
| 1:30–2:00 | 1.3 Account hygiene package + templates |
| 2:00–2:15 | 1.4 The do-not-sell list (test-gated) |
| 2:15–2:30 | Drill: pitch two real audit findings, graded |

## 1.1 Threat model of a main-street business (35 min, whiteboard)

Skip the hacker-in-a-hoodie mythology. The threats that actually hit five-person businesses, in order of frequency:

| # | Threat | How it happens | What it costs |
|---|---|---|---|
| 1 | **Email compromise / wire fraud** | Spoofed or hijacked email tricks someone into paying a fake invoice or rerouting a payment | $5k–$100k+, rarely recovered |
| 2 | **Account takeover** | Password reused from a breached site opens their email, bank, socials | Locked out of their own business |
| 3 | **Phishing** | Employee clicks a fake login page | The on-ramp to #1 and #2 |
| 4 | **Data loss** | Dead laptop, stolen phone, ransomware, no backup | Customer list, invoices, photos — gone |
| 5 | **Reputation hijack** | Unclaimed Google listing edited; look-alike domain registered | Customers literally routed elsewhere |

What's *not* on the list: nation-states, zero-days, firewalls. Small businesses get hurt by boring things. We sell boring protection, done properly.

**The wire-fraud story — memorize it as a story, because stories close.**
Tell it in second person, about ninety seconds:

> "Here's how it actually happens. A landscaping company — real case pattern, happens every week somewhere — is finishing a $40,000 patio job. The customer gets an email from the company: 'Hey, we've updated our banking, here's the new account for the final payment.' Same logo, same signature, reads exactly right. Customer wires $18,000. Two weeks later the *real* landscaper calls asking where the payment is. The email came from a domain one letter off — or worse, from the landscaper's actual address, because their email had no protection and anyone could send as them. The money's gone. The customer's furious at the landscaper, who did nothing wrong except leave a door open they didn't know existed. The fight over who eats the $18,000 destroys the relationship either way.
> The door is a settings problem. It takes us about an hour to close. That's what I'm here about."

**Teaching check:** Myles tells that story back cold, no notes, in his own words, keeping the three beats — the convincing email, the gone money, the door that was always closable. If he can tell it at a counter, everything in this session sells itself.

## 1.2 Email security — the crown jewel skill (55 min, hands-on)

Deepest technical content in the module, highest-converting pitch in the portfolio — because *the audit proves the problem before we say a word.*

### The three records, twice each — real and translated

**SPF (Sender Policy Framework)**
- *Real:* a DNS TXT record listing which servers may send mail for the domain. Receiving servers check the envelope sender's domain, fetch the record, and compare the sending IP against the list.
- *Counter:* "A public list of who's allowed to send email wearing your name. No list, anyone qualifies."
- *Anatomy of a real record:*
```
v=spf1 include:_spf.google.com include:sendgrid.net -all
│      │                        │                   │
│      │                        │                   └─ hard fail everyone else
│      │                        └─ their invoice/marketing tool
│      └─ their mail provider (Google Workspace here)
└─ version tag, always first
```
- *The endings matter:* `-all` = reject others (strict) · `~all` = softfail/suspicious (common safe default) · `+all` = allow everyone (worse than nothing — flag it hard on any audit).
- *The gotcha to know:* SPF allows a maximum of 10 DNS lookups. Businesses that bolted on tool after tool (Mailchimp + QuickBooks + booking app + CRM…) blow the limit and their SPF silently stops working. The audit catches this; it's an easy, impressive fix.

**DKIM (DomainKeys Identified Mail)**
- *Real:* the mail server signs each outgoing message with a private key; the public key sits in DNS at `selector._domainkey.domain.com`. Receivers verify the signature — proving the message came from an authorized system and wasn't altered.
- *Counter:* "A tamper-proof seal on every email you send. Broken seal, inboxes get suspicious."
- *Field note:* DKIM is enabled inside the mail provider (Google Workspace / Microsoft 365 admin), then the generated record is published in DNS. Two dashboards, one fix.

**DMARC (Domain-based Message Authentication, Reporting & Conformance)**
- *Real:* the policy record at `_dmarc.domain.com` telling receivers what to do when SPF/DKIM fail alignment — and where to email aggregate reports about who's sending as the domain.
- *Counter:* "The enforcement rule. SPF and DKIM are the locks; DMARC is the instruction to actually use them — and it sends you a report of everyone trying your door."
- *Anatomy:*
```
v=DMARC1; p=quarantine; rua=mailto:dmarc@theirbiz.com; pct=100
│         │             │                              │
│         │             │                              └─ applies to 100% of mail
│         │             └─ where aggregate reports go
│         └─ policy: none → quarantine → reject
└─ version
```
- **The deployment discipline — this is professional judgment, teach it hard:** always start at `p=none` (monitor only). Read the reports for 2–4 weeks. Only move to `quarantine`, then `reject`, once reports confirm every *legitimate* sender (the booking tool nobody remembered, the payroll service) is SPF/DKIM-aligned. Jumping straight to `p=reject` can vaporize a client's own invoices — the one mistake in this trade that turns a customer into an enemy in a day.

### The verification commands (Myles runs these himself)
```
dig TXT theirbiz.com                     # find SPF among TXT records
dig TXT _dmarc.theirbiz.com              # DMARC policy, or nothing = unprotected
dig TXT selector1._domainkey.theirbiz.com  # DKIM (selector varies by provider:
                                           # google, selector1/selector2 for M365)
nslookup -type=TXT theirbiz.com          # same thing on Windows
```
This matters beyond diagnosis: when a skeptical owner says "prove it," Myles opens a terminal *at the counter* and shows them their own empty DMARC lookup. Nothing in the pitch arsenal beats live evidence from public DNS.

### The pitch, verbatim
> "Right now, anyone on earth can send an email that says it's from you — to your customers, your bank, your vendors — and most inboxes will deliver it. I'm not guessing; here's the check on your actual domain, and here's how you can verify it yourself. Closing this is a settings fix, not a construction project. About an hour of work, and afterward you get a monthly report of anyone who tries."

### Lab (30 min inside the 55)
Pull five pipeline businesses through the audit portal. For each: read the email findings aloud, translate to counter-language, say the pitch customized. Then execute one full fix on the Next-Gen IT test domain in Cloudflare: publish SPF, enable DKIM in the mail provider, publish `p=none` DMARC, run the dig commands to confirm propagation.

**Lane rule:** Myles diagnoses and pitches; the record changes are Jeremiah's until sign-off. A wrong DMARC policy stops a business's real mail — not a learn-on-a-client mistake we take.

## 1.3 The account hygiene package (30 min)

The cheapest, most valuable hour a small business will ever buy. Four components, delivered in one sitting:

**1 — Password manager.** Deployed for owner + staff, shared vault for business logins. Kills reuse, solves the sticky note, gives continuity when an employee leaves. Field policy: recommend one mainstream manager and know it cold rather than comparison-shopping in front of the client; competence beats catalogs.

**2 — 2FA on the money paths, in priority order:** email first (it resets everything else), then bank, domain registrar, Google Business, payment processors, socials. App-based or hardware key over SMS wherever the service allows — SMS is better than nothing but SIM-swaps are real; say exactly that, no more.

**3 — The Access Inventory — the quiet masterstroke.** One page, template below, listing every account the business runs on, who holds it, how it's recovered. Half of small businesses cannot answer "who owns your domain login?" The page is worth the fee alone — and *we author it*, which makes Next-Gen IT the system of record. Every future engagement starts by pulling this sheet.

```
ACCESS INVENTORY — [Business] — maintained by Next-Gen IT — [date]
──────────────────────────────────────────────────────────────
Account          Where          Owner login      2FA   Recovery
Domain           Cloudflare     owner@biz.com    ✓app  owner cell
Email            Google WS      owner@biz.com    ✓app  recovery codes in vault
Website          GitHub         nextgenit mgd    ✓     J. Cargill
Google Business  google.com     owner@biz.com    ✓     owner cell
Bank             [bank]         (not stored)     ✓     — client-held only
Facebook page    Admin: owner + [REMOVE: ex-employee J.D.]
──────────────────────────────────────────────────────────────
Rule: bank credentials are NEVER stored by us. We record that 2FA
exists, nothing else. Findings in [brackets] = action items.
```

**4 — The backup answer.** One question — "if this laptop dies today, what's gone?" — then usually one fix: turning on the cloud sync inside the subscription they already pay for (Drive/OneDrive), plus phone photo backup for the businesses whose entire portfolio lives in a camera roll.

**Hands-on:** Myles builds his own vault, 2FAs his own money paths, writes his own access inventory tonight. You cannot sell hygiene you don't practice, and owners ask "do you do this yourself?" more often than you'd think.

## 1.4 What we do NOT sell (15 min — test-gated; recited cold at graduation)

A small tech company survives on knowing its edges:

- We don't sell "hack-proof." Nothing is. We sell *dramatically harder to hurt* — measurably.
- We don't do compliance attestations (HIPAA, PCI, SOC 2). We *prepare* a business to work with someone who does; the referral moment builds more trust than the fake expertise ever would.
- We don't touch anything mid-incident. Active compromise = isolate, preserve evidence, call Jeremiah; Jeremiah decides if it escalates to a specialist. Field reps never improvise forensics — well-meaning cleanup destroys the evidence an insurer or investigator needs.
- We don't install software we can't explain. No reselling mystery antivirus for margin.
- We don't store client bank credentials. Ever. Documented as policy on the access inventory itself.
- We never exaggerate a finding. The report says what it says.

### Session 1 drill (graded)
Two real audit findings from the pipeline, pitched to Jeremiah-as-owner. Scored 1–5 on: accuracy (is every claim true?), translation (would a barber understand it?), evidence (did he show, not just tell?), close (did he land on a fix and a price?). 16/20 to pass; below that, re-drill next session before new content.

**Homework:** audit five pipeline businesses; one paragraph each — the single worst finding, in counter-language. These become live pitches in Session 2.

---

# SESSION 2 — Presence: found, chosen, believed (2.5 hrs)

### Run of show
| Time | Segment |
|---|---|
| 0:00–0:20 | 2.1 Local search reality + homework review |
| 0:20–1:15 | 2.2 Google Business Profile — full build, live |
| 1:15–1:45 | 2.3 The review engine + reply templates |
| 1:45–2:10 | 2.4 The spoofing surface — where the module halves meet |
| 2:10–2:30 | Drill: 10-minute presence teardown of a surprise business |

## 2.1 The local search reality (20 min)

For a main-street business, presence is the whole surface a customer touches before walking in:

```
need → Google search / Maps → Business Profile → reviews → website → call or door
```

The website (Module 1) is one link. Most businesses are broken at the *first* links: unclaimed or hollow Google profile, twelve reviews with zero replies, hours wrong since 2024. Fixing those often moves revenue more than the website does — which is why presence is the most honest upsell in the portfolio. Say that to clients in exactly those words; honesty about what matters most is a differentiator by itself.

Homework review: each of the five findings paragraphs read aloud, red-penned live for exaggeration and jargon.

## 2.2 Google Business Profile — the 45-minute miracle (55 min, live build)

Highest-ROI task in local presence, and free — which makes it a devastating trust-builder inside a bundle.

**The 18-point build checklist (laminate it):**

*Claim & control*
1. Profile claimed and verified; ownership documented on the Access Inventory (presence work feeds security work — this loop is the whole module)
2. Every current manager reviewed; stale admins removed
3. Recovery method confirmed on the owning Google account, 2FA on

*Core data*
4. Exact legal/DBA name — no keyword stuffing ("Joe's Barbershop," not "Joe's Barbershop | Best Fades Georgetown TX"; stuffing risks suspension)
5. Primary category precise; all valid subcategories added
6. Hours + holiday hours + "more hours" (senior, appointment-only) where relevant
7. Phone = the number they answer; local number over tracking number
8. Website link to the new site; appointment link if they book online
9. Service area configured correctly for mobile businesses

*Rich content*
10. Description ~750 chars in the owner's voice, keywords natural, no superlative spam
11. 10+ real photos: storefront (helps people find the door), interior, team, work product — geotagged phone photos beat stock here too
12. Logo + cover image set
13. Products/services with prices where the category supports it
14. Attributes (veteran-owned, wheelchair accessible, wifi…) — filters people actually use
15. Q&A section seeded: post the five questions customers always ask, answer them as the business

*Ongoing*
16. Messaging enabled only if the owner will answer within hours — a dead chat is worse than none
17. First Google Post published (offer/update) — shows the profile is alive
18. Photo cadence set: 2–3 new photos monthly (this is care-plan material)

**NAP consistency sweep:** Name, Address, Phone *identical to the character* across profile, website footer, Facebook, Yelp, Apple Maps, Nextdoor, and the big data aggregators. "Suite 200" vs "#200" counts. Mismatches quietly erode local ranking. It's a 30-minute mechanical sweep with a checklist — exactly the tedious work a service fee is for.

**Live build:** run the full 18 points on a real, consenting pipeline business during the session. Before/after screenshots — that pair of images becomes standing sales collateral.

## 2.3 The review engine (30 min)

Reviews are the #1 conversion factor in local search, and almost nobody runs a *system* for them.

**The machine we install — four parts:**
1. **The link**: short review URL + QR code, printed at the register, on invoices, in the email signature.
2. **The habit**: ask every happy customer *at the moment of the compliment* — "that means a lot, would you put that in a Google review? Takes thirty seconds, here's the code." Scripted, practiced, tied to a trigger that already happens daily.
3. **The reply discipline**: owner replies to *every* review within a week. Replies are written for the next hundred readers, not the reviewer.
4. **The monitoring**: new-review alerts on, checked in the care-plan monthly sweep.

**Reply templates (put these in the client handoff doc):**

*5-star:* "Thanks [name] — the [specific thing they mentioned] means a lot to us. See you next time."
*(Always echo one specific detail; it proves a human read it and salts keywords honestly.)*

*Negative, calm formula — acknowledge, own what's ours, move it offline, never argue facts publicly:*
"[Name], thanks for the honest feedback — a [wait time / miscommunication] like that isn't the experience we want anyone to have. I'd like to make it right; call me directly at [number] and ask for [owner]. — [Owner name]"

*Fake/malicious review:* don't engage in the thread beyond one neutral line ("We have no record of this visit and would welcome the chance to verify — please contact us"); flag it through the platform's removal process; document. Never flame.

**The hard ethical line, said to every client in these words:** we never write fake reviews, never buy reviews, never review-gate — filtering unhappy customers away from the review page violates platform rules and risks the listing. We build the *asking machine*; customers supply the truth. Clients will ask for the shady version. The answer is the same every time, and the reason ("it can get your listing suspended, and it's your listing") lands better than the ethics alone.

## 2.4 The spoofing surface — where the halves meet (25 min)

The proof that security and presence are one product:

- **Look-alike domains:** is `theirbiz.co`, the common typo, or the hyphenated variant registered — and by whom? Five-minute check (`whois`, registrar search). If clear: defensive registration at ~$12/yr, pointed at their real site — cheap insurance and a line item that sells itself. If *taken by someone suspicious*: that's a finding for Jeremiah, not a field fix.
- **Deliverability as presence:** their SPF/DMARC posture (Session 1) decides whether their own quotes and invoices land in customers' spam folders. "Your emails go to spam" is a presence complaint powered by a security fix — the two halves selling each other in one sentence.
- **Profile takeover surface:** who can edit the Google listing, the Facebook page, Instagram? Ex-employee still admin? Discovered doing presence work, filed as account hygiene, fixed in the Security Starter. One walk-through, three products.

### Session 2 drill (graded)
Jeremiah names a surprise local business. Myles has 10 minutes and a laptop: GBP state, review count/reply rate, NAP spot-check, look-alike check, SPF/DMARC dig. Then a 2-minute verbal teardown: three worst findings, in counter-language, with what he'd charge. Same 20-point rubric.

**Homework:** full written presence workup on one pipeline business — the drill, in document form, priced. It becomes a real leave-behind.

---

# SESSION 3 — The audit as a product, and the company around it (2.5 hrs)

### Run of show
| Time | Segment |
|---|---|
| 0:00–0:45 | 3.1 Audit end-to-end + the findings page |
| 0:45–1:10 | 3.2 The expanded ladder + bundle math |
| 1:10–1:40 | 3.3 Pitch scripts + the full objection bank, role-played |
| 1:40–2:15 | 3.4 The company wrapper |
| 2:15–2:30 | Graduation exam briefing |

## 3.1 Running the Next-Gen IT audit end-to-end (45 min)

Sessions 1–2 taught what the 30-point audit *measures*. Now Myles operates the machine:

1. Run the portal against a target domain
2. Read every section — email health, website/SEO, marketing, tech/CRM — connecting each finding to the session where he learned its meaning
3. Convert the scored report into a **findings page** using the standard template:

```
DOMAIN HEALTH FINDINGS — [Business] — [date] — prepared by Next-Gen IT
Overall: 61/100 (C+)   Verify any item yourself — ask us how.
──────────────────────────────────────────────────────────────
#  FINDING                    WHAT IT MEANS FOR YOU              FIX IS IN
1  No DMARC record            Anyone can send email as you;      Security
   [HIGH]                     you'd never know                   Starter
2  Google listing unclaimed   Anyone can edit your hours,        Presence
   [HIGH]                     photos, and phone number           Pack
3  SPF ends in +all           Your "allowed senders" list        Security
   [HIGH]                     allows everyone — worse than none  Starter
4  No reply to any review     37 reviews, 0 responses — reads    Presence
   [MED]                      as "nobody's home"                 Pack
5  theirbiz.co unregistered   $12/yr closes a door before        Presence
   [LOW]                      someone impersonates you           Pack
──────────────────────────────────────────────────────────────
Security Starter $XXX · Presence Pack $XXX · Both + Care Plan: $XXX + $XXX/mo
Most of this is done within one week of go-ahead.
```

Rules for the page: max 6 findings (more numbs), severity-ordered, every line survives "prove it," every line maps to a purchasable fix, one page total. The page *is* the quote — no separate proposal document at this tier.

4. Deliver it: lead with the two scariest **true** findings, close on "here's the fix, here's the price, done in a week."

**Drill inside the session:** full report presented to Jeremiah playing a skeptical owner. Mandatory curveballs: "my nephew does our computers" · "we've never been hacked in 20 years" · "how do I know you're not making this up." That last one always gets the same answer: *the report is generated from public records about your own domain — here's the terminal, verify it yourself.* Evidence is the close.

## 3.2 The expanded offer ladder (25 min)

| Offer | Contents | Price | Delivery |
|---|---|---|---|
| **Security Starter** | SPF/DKIM/DMARC fixed (staged rollout) · password manager + 2FA on money paths · access inventory authored · backup check | $400–700 | Myles pitches/diagnoses · Jeremiah executes DNS + signs off |
| **Presence Pack** | GBP 18-point build · NAP sweep · review engine installed with templates · look-alike check/registration | $350–600 | Myles end-to-end after this module |
| **Care Plan (upgraded)** | Module 1 plan **+** quarterly re-audit · DMARC report review · GBP upkeep + monthly photos/post · review monitoring | $100–250/mo | Split |
| **Full Audit + Remediation** | 30-point report + everything above, scoped | $750–2,500 | Jeremiah leads |

**The bundle move:** Security Starter + Presence Pack quoted together at a round number below the sum (e.g., $650+$450 → "$999 for both, one week") converts dramatically better than either alone, and every bundle client gets the care-plan pitch at handoff — which is the strategic point. A care plan that's "we host your site" churns; a care plan that's "we re-audit you quarterly and keep your email posture, listing, and reviews healthy" renews itself. **The Starter and the Pack exist to give the care plan substance.**

## 3.3 Pitch scripts and the objection bank (30 min, role-played until boring)

**Three doors, three openings — full scripts:**

*Door 1 — has a decent website already:*
> "I'm not here to sell you a website — yours is actually fine. I run a local IT shop and we ran a free health check on your domain — the same public-records check a bank or insurer would run. Two things came up I'd want to know about if I owned this place. Got two minutes? …If not, here's the page; my number's on it."

*Door 2 — bought the website from us:*
> "Everything I built you is healthy — site's fast, cert's clean. While I was in there I checked the stuff *around* the site: your Google listing and your email security. Couple of open doors. Here's the one-pager; the whole thing's about a week of work."

*Door 3 — cold, no website:* Module 1 pitch leads. The free snapshot seeds Module 2 findings for the follow-up; the website closes the deal; security and presence build the relationship.

**The objection bank — ten, with answers:**

1. *"My nephew handles our computers."* → "Great — this report will make his job easier. Want me to send it to him? Happy to walk him through it." *(Never fight the nephew. Recruit the nephew. Half the time the nephew becomes the internal champion.)*
2. *"We're too small to be a target."* → "The fraud that hits businesses your size is automated — it doesn't know how small you are. It just found your open door. This report is it finding you."
3. *"We've never been hacked."* → "Most businesses who get hit said the same thing the week before. But honestly — you might be right, and that's why everything on this page is prevention priced like prevention, not disaster recovery priced like disaster."
4. *"How do I know this is real?"* → "Every line comes from public records about your own domain. Here — verify this one yourself right now." *(Open the terminal. This objection is a gift.)*
5. *"Sounds expensive."* → "The whole starter is less than one no-show weekend costs you. And the wire-fraud version of this conversation starts at five figures."
6. *"I don't have time."* → "You need about twenty minutes total across the whole thing. We do the work; you approve it."
7. *"Can you just do the Google listing part?"* → "Absolutely." *(Unbundling is fine. A $400 client who trusts you becomes a $150/mo client. Never guilt the smaller yes.)*
8. *"My website company said they handle security."* → "They might handle the website's security — this is about your *email* and your *listing*, which usually aren't theirs. Easy to check: ask them what your DMARC policy is. If they answer, you're in good hands and I'll shake yours."
9. *"Send me something."* → "This page is the something." *(The findings page exists so 'send me something' is a close, not an exit.)*
10. *"Is this a scam?"* → Respect it — it means their instincts work. "Fair question, and honestly the fact that you ask is a good sign. Here's who I am, here's the local businesses we've done this for, and nothing here requires you to give me a password or a payment today. Verify the findings first."

**The tone rule over all ten:** calm, unhurried, evidence-forward. The rep who needs the sale loses it. We have a pipeline; any single "no" is fine, and it shows.

## 3.4 The company wrapper (35 min — the "start a technology company" part)

The skills are now a catalog. A company is the structure around it. Orientation, not legal advice — standing rule: **verify current requirements and costs with the Texas SOS, the IRS, and a CPA/attorney before acting.**

**Entity.** A Texas LLC is the standard wrapper — liability separation matters the day you touch a client's DNS. Formation filing with the state + an operating agreement (even single-member; banks and disputes both ask for it) + EIN from the IRS + a separate business bank account from day one. Commingling personal and business money is the classic way small operators pierce their own liability shield.

**Insurance.** General liability *plus* **tech E&O / professional liability** — E&O is the one that matters in this trade, because it's what answers for "the DNS change broke our email for a day." Modest monthly cost at this scale; non-optional once there are real clients. Get quotes before the first Security Starter ships.

**Paper.** Every engagement on a signed one-pager: scope, price, deposit terms, timeline, the ownership promise ("you own your domain, your site, your accounts"), what's explicitly out of scope, and a limitation-of-liability clause a lawyer has reviewed once. Skeleton:

```
SERVICE AGREEMENT — one page
Client: ____  Provider: ____  Date: ____
SCOPE (exactly what's included): ...
NOT INCLUDED (the scope-creep fence): ...
PRICE: $___  ·  50% deposit to begin · balance at completion
TIMELINE: __ business days from deposit + client materials
OWNERSHIP: Client owns their domain, website, and all accounts.
  Provider manages them under this agreement and hands over
  full credentials at completion or termination.
LIABILITY: [attorney-reviewed limitation clause]
Signatures: ____________    ____________
```

**Books.** Real invoicing software from client one · every expense logged · a fixed percentage of every payment moved to a separate tax account on receipt so quarterly estimates never hurt · a CPA conversation before the first $10k, not after.

**The relationship decision — explicit, written, signed at module end.** Two legitimate structures:
- *(a) Rep inside Next-Gen IT:* the launch-plan agreement, Option B comp, Next-Gen IT's insurance and entity cover the work, clients are Next-Gen IT's.
- *(b) Myles' own LLC subcontracting under Next-Gen IT:* his entity, his E&O, a subcontractor agreement governing brand use, pricing floors, and client ownership.
Path (a) now, with a written option to convert to (b) at a milestone (say, 10 closed deals), is the natural sequence. Either version includes mutual non-solicitation of each other's clients. **The wrong answer is ambiguity** — handshakes are how good partnerships die.

---

# Graduation exam

One real pipeline business gets the full treatment, Jeremiah observing silently:
audit run → findings page authored → bundle quoted → pitch delivered live, objections included.

**Scoring rubric (pass = 34/40, and any Integrity score below 5 is an automatic fail regardless of total):**

| Dimension | /5 | What 5 looks like |
|---|---|---|
| Technical accuracy | 5 | Every claim on the findings page is true and correctly explained |
| Translation | 5 | Zero unexplained jargon; a barber follows every sentence |
| Evidence | 5 | Offered live verification unprompted at least once |
| Findings page craft | 5 | One page, ≤6 findings, severity-ordered, every line priced |
| Pitch delivery | 5 | Story-led open, calm tone, clean close on fix + price |
| Objection handling | 5 | Two curveballs handled without flinching or overreaching |
| Do-not-sell recital | 5 | The 1.4 list, cold, plus *why* for each line |
| Integrity | 5 | No exaggeration anywhere, even under pressure to close |

If it closes, the business becomes his first Module 2 client and the comp agreement's first real test.

## Graduation criteria, compact

Unassisted, Myles can: tell the wire-fraud story cold · explain and *dig-verify* SPF/DKIM/DMARC and read their status on any audit · execute the 18-point GBP build and NAP sweep · install the review engine and state its ethical lines from memory · run the audit and author a findings page in under an hour · recite the do-not-sell list with reasons · and name, on signed paper, which company structure he operates under.

---

# 90-day post-module ramp

**Days 1–30 — Reps.** Every pipeline business gets a findings page. Target: 10 delivered, 3 closed (any package). Weekly pipeline call unchanged; every pitch debriefed in two minutes — what landed, what stalled.
**Days 31–60 — Bundles.** Lead with the $999-style bundle; target 2 bundle closes and the first 3 care plans signed at the upgraded tier. First quarterly re-audit executed on a Module 1 client (proving the renewal motion works).
**Days 61–90 — The decision.** Real numbers on the table: close rate by door type, revenue by rung, hours per delivery. If the milestones hit, the (a)→(b) conversion conversation happens on schedule, with data instead of vibes.

**Module 3 preview — "Run the Book":** operating the client base as a machine. Care-plan delivery workflows, the monthly report that justifies every retainer, quarterly re-audit cadence, referral engineering ("who else on this street should I check?"), invoicing discipline, tax rhythm, and the math of the first subcontracted hour.

---

*The through-line of all three modules: evidence, ownership, honesty. We show our findings, the client owns their assets, and every claim survives "prove it." That's the moat a small technology company actually has — and it compounds, because every honest report makes the next door easier to walk through.*
