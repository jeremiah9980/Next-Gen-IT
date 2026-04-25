#!/usr/bin/env python3
"""
Next-Gen IT Domain Health Audit
Usage: python run_audit.py <domain> <output_dir>
Requires: ANTHROPIC_API_KEY environment variable
"""

import sys, os, json, re, subprocess, urllib.request, urllib.error
from datetime import datetime, timezone

# ── HELPERS ───────────────────────────────────────────────────────────────────

def clean_domain(raw):
    d = raw.lower().strip()
    for prefix in ('https://','http://','www.'):
        if d.startswith(prefix): d = d[len(prefix):]
    return d.split('/')[0]

def sh(cmd, timeout=30):
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        return (r.stdout + r.stderr).strip()
    except Exception as e:
        return f'[cmd failed: {e}]'

def fetch(url, timeout=15):
    try:
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (compatible; NextGenIT-Audit/2.0)'
        })
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.read().decode('utf-8', errors='ignore')[:60000]
    except Exception as e:
        return f'[fetch failed: {e}]'

# ── STEP 1: INFRASTRUCTURE ────────────────────────────────────────────────────

def run_infrastructure(domain):
    print(f'[1/5] Infrastructure scan for {domain}…')
    parts = []

    # Try skill script first, then inline
    script_candidates = [
        'skills/domain-health-audit/scripts/domain_audit.sh',
        os.path.join(os.path.dirname(__file__), 'domain_audit.sh'),
    ]
    ran_script = False
    for script in script_candidates:
        if os.path.isfile(script):
            out = sh(f'bash {script} {domain}', timeout=60)
            if out and '[cmd failed' not in out:
                parts.append(out)
                ran_script = True
                break

    if not ran_script:
        # Inline fallback
        parts.append('=== WHOIS ===')
        parts.append(sh(f'whois {domain} 2>/dev/null | grep -iE "(registrar:|creation date|expiry date|registry expiry|updated date|name server)" | head -20'))
        parts.append('=== NAMESERVERS ===')
        parts.append(sh(f'dig NS {domain} +short 2>/dev/null'))
        parts.append('=== A RECORD ===')
        parts.append(sh(f'dig A {domain} +short 2>/dev/null | head -5'))
        parts.append('=== MX ===')
        parts.append(sh(f'dig MX {domain} +short 2>/dev/null'))
        parts.append('=== SPF ===')
        parts.append(sh(f'dig TXT {domain} +short 2>/dev/null | grep -i spf'))
        parts.append('=== DMARC ===')
        parts.append(sh(f'dig TXT _dmarc.{domain} +short 2>/dev/null'))
        parts.append('=== HTTP HEADERS ===')
        parts.append(sh(f'curl -sI --max-time 10 --location https://{domain} 2>/dev/null | head -25'))
        parts.append('=== HTTP REDIRECT ===')
        parts.append(sh(f'curl -sI --max-time 8 http://{domain} 2>/dev/null | grep -iE "^(http/|location:)" | head -5'))
        parts.append('=== IP/ASN ===')
        ip = sh(f'dig A {domain} +short 2>/dev/null | head -1')
        if ip and not ip.startswith('['):
            parts.append(f'IP: {ip}')
            parts.append(fetch(f'https://ipinfo.io/{ip}/json', timeout=8))
        parts.append('=== ROBOTS ===')
        parts.append(sh(f'curl -sL --max-time 8 https://{domain}/robots.txt 2>/dev/null | head -15'))
        parts.append('=== SITEMAP ===')
        parts.append(sh(f'curl -sI --max-time 8 https://{domain}/sitemap.xml 2>/dev/null | grep -i "^HTTP/" | head -2'))

    return '\n'.join(parts)

# ── STEP 2: MXTOOLBOX ─────────────────────────────────────────────────────────

def run_mxtoolbox(domain):
    print('[2/5] Fetching MXToolbox results…')
    checks = ['mx', 'spf', 'dmarc', 'blacklist', 'dns']
    results = {}
    for check in checks:
        url = f'https://mxtoolbox.com/SuperTool.aspx?action={check}:{domain}&run=toolpage'
        html = fetch(url, timeout=20)
        if '[fetch failed' in html:
            results[check] = 'UNAVAILABLE'
        elif any(x in html for x in ['No problems found', 'Passed', 'passed']):
            results[check] = 'PASS'
        elif any(x in html for x in ['FAIL', 'Error', 'error', 'failed']):
            results[check] = 'FAIL'
        elif 'Warning' in html or 'warning' in html:
            results[check] = 'WARNING'
        else:
            results[check] = 'UNKNOWN'
    return results

# ── STEP 3: LIVE SITE ─────────────────────────────────────────────────────────

def run_site_fetch(domain):
    print('[3/5] Fetching live site HTML…')
    for url in [f'https://{domain}', f'https://www.{domain}', f'http://{domain}']:
        html = fetch(url, timeout=15)
        if '[fetch failed' not in html and len(html) > 200:
            return html
    return ''

# ── STEP 4: CLAUDE ANALYSIS ───────────────────────────────────────────────────

AUDIT_PROMPT = """You are an expert domain health auditor. Analyze this data for domain: {domain}

## Raw Infrastructure Data (WHOIS · DNS · HTTP headers):
{infra}

## MXToolbox Results:
{mxtoolbox}

## Live Site HTML (truncated):
{html}

Score each of the 30 audit items as PASS or FAIL based on evidence in the data.
Only mark PASS if you have direct evidence. Default to FAIL if unknown.

WEBSITE & SEO (1-10):
1. Site loads & SSL enforced
2. Mobile responsive (viewport meta)
3. IDX/MLS search present
4. Contact/lead capture form
5. Google Business Profile linked or embedded
6. Local keywords in title/description
7. Active blog/market updates
8. Sitemap returns 200
9. Analytics tag (GA4/GTM)
10. Schema/structured data markup

MARKETING & SOCIAL (11-20):
11. Facebook page linked
12. Instagram linked
13. Facebook Pixel installed
14. LinkedIn or YouTube linked
15. Email capture/newsletter form
16. Video content present
17. Client testimonials on site
18. 3+ social platforms consistent
19. Retargeting pixel (FB/Google Ads/LinkedIn)
20. Google Reviews widget

TECH STACK & CRM (21-30):
21. Real estate CRM identified (FollowUpBoss/kvCORE/LionDesk/Lofty/BoomTown etc)
22. Live chat or chatbot
23. Transaction management tool mentioned
24. E-signature tool
25. Online scheduling (Calendly/ShowingTime etc)
26. Marketing automation script
27. Google Tag Manager
28. Heatmap/session recording (Hotjar/Clarity)
29. IDX platform identified
30. HTTPS enforced (http→https redirect)

Respond ONLY with valid JSON (no markdown, no backticks, no explanation):
{{
  "registrar": "string",
  "dns_host": "string",
  "web_host": "string",
  "cms": "string",
  "email_provider": "string",
  "ip": "string",
  "domain_created": "string",
  "domain_expires": "string",
  "nameservers": ["string"],
  "mx_records": ["string"],
  "email_health": {{
    "mx_records": "PASS|FAIL",
    "spf": "PASS|FAIL|WARNING",
    "dmarc": "PASS|FAIL|WARNING",
    "dkim": "PASS|FAIL",
    "blacklist": "PASS|FAIL",
    "ssl": "PASS|FAIL"
  }},
  "scores": {{
    "website_seo": [
      {{"id":1,"label":"Site loads & SSL enforced","result":"PASS|FAIL","note":"brief evidence"}},
      {{"id":2,"label":"Mobile responsive","result":"PASS|FAIL","note":""}},
      {{"id":3,"label":"IDX/MLS search","result":"PASS|FAIL","note":""}},
      {{"id":4,"label":"Contact/lead form","result":"PASS|FAIL","note":""}},
      {{"id":5,"label":"Google Business Profile","result":"PASS|FAIL","note":""}},
      {{"id":6,"label":"Local keywords","result":"PASS|FAIL","note":""}},
      {{"id":7,"label":"Active blog/updates","result":"PASS|FAIL","note":""}},
      {{"id":8,"label":"Sitemap present","result":"PASS|FAIL","note":""}},
      {{"id":9,"label":"Analytics tag","result":"PASS|FAIL","note":""}},
      {{"id":10,"label":"Schema markup","result":"PASS|FAIL","note":""}}
    ],
    "marketing_social": [
      {{"id":11,"label":"Facebook page linked","result":"PASS|FAIL","note":""}},
      {{"id":12,"label":"Instagram linked","result":"PASS|FAIL","note":""}},
      {{"id":13,"label":"Facebook Pixel","result":"PASS|FAIL","note":""}},
      {{"id":14,"label":"LinkedIn or YouTube","result":"PASS|FAIL","note":""}},
      {{"id":15,"label":"Email capture/newsletter","result":"PASS|FAIL","note":""}},
      {{"id":16,"label":"Video content","result":"PASS|FAIL","note":""}},
      {{"id":17,"label":"Client testimonials","result":"PASS|FAIL","note":""}},
      {{"id":18,"label":"3+ social platforms","result":"PASS|FAIL","note":""}},
      {{"id":19,"label":"Retargeting pixel","result":"PASS|FAIL","note":""}},
      {{"id":20,"label":"Google Reviews widget","result":"PASS|FAIL","note":""}}
    ],
    "tech_crm": [
      {{"id":21,"label":"Real estate CRM","result":"PASS|FAIL","note":""}},
      {{"id":22,"label":"Live chat/chatbot","result":"PASS|FAIL","note":""}},
      {{"id":23,"label":"Transaction management","result":"PASS|FAIL","note":""}},
      {{"id":24,"label":"E-signature tool","result":"PASS|FAIL","note":""}},
      {{"id":25,"label":"Online scheduling","result":"PASS|FAIL","note":""}},
      {{"id":26,"label":"Marketing automation","result":"PASS|FAIL","note":""}},
      {{"id":27,"label":"Google Tag Manager","result":"PASS|FAIL","note":""}},
      {{"id":28,"label":"Heatmap/session recording","result":"PASS|FAIL","note":""}},
      {{"id":29,"label":"IDX platform","result":"PASS|FAIL","note":""}},
      {{"id":30,"label":"HTTPS enforced","result":"PASS|FAIL","note":""}}
    ]
  }},
  "total_score": 0,
  "website_score": 0,
  "marketing_score": 0,
  "tech_score": 0,
  "grade": "A|B|C|D|F",
  "recommendations": [
    {{"priority":1,"title":"string","detail":"string"}},
    {{"priority":2,"title":"string","detail":"string"}},
    {{"priority":3,"title":"string","detail":"string"}},
    {{"priority":4,"title":"string","detail":"string"}},
    {{"priority":5,"title":"string","detail":"string"}}
  ],
  "pitch_angle": "2-3 sentence sales pitch referencing the specific gaps found"
}}"""

def run_claude_analysis(domain, infra, mxtoolbox, site_html):
    print('[4/5] Running AI analysis…')
    import anthropic
    client = anthropic.Anthropic()
    prompt = AUDIT_PROMPT.format(
        domain=domain,
        infra=infra[:8000],
        mxtoolbox=json.dumps(mxtoolbox, indent=2),
        html=site_html[:14000],
    )
    msg = client.messages.create(
        model='claude-sonnet-4-5',
        max_tokens=4096,
        messages=[{'role':'user','content':prompt}]
    )
    raw = msg.content[0].text.strip()
    raw = re.sub(r'^```json\s*','',raw); raw = re.sub(r'^```\s*','',raw); raw = re.sub(r'\s*```$','',raw)
    data = json.loads(raw)

    # Compute / verify scores
    ws = sum(1 for x in data['scores']['website_seo']    if x['result']=='PASS')
    ms = sum(1 for x in data['scores']['marketing_social'] if x['result']=='PASS')
    ts = sum(1 for x in data['scores']['tech_crm']       if x['result']=='PASS')
    total = ws + ms + ts
    data.update({'website_score':ws,'marketing_score':ms,'tech_score':ts,'total_score':total})
    grade = 'A' if total>=25 else 'B' if total>=20 else 'C' if total>=14 else 'D' if total>=8 else 'F'
    data['grade'] = grade
    return data

# ── STEP 5: HTML REPORT ───────────────────────────────────────────────────────

def grade_color(g):
    return {'A':'#00e5a0','B':'#00b4ff','C':'#ffb547','D':'#ff7043','F':'#ff4d6a'}.get(g,'#64748b')

def status_tag(s):
    if s=='PASS':    return '<span style="color:#00e5a0;font-size:13px;font-weight:600">✅ PASS</span>'
    if s=='WARNING': return '<span style="color:#ffb547;font-size:13px;font-weight:600">⚠️ WARN</span>'
    return '<span style="color:#ff4d6a;font-size:13px;font-weight:600">❌ FAIL</span>'

def score_bar(score, max_s=10):
    pct = round((score/max_s)*100)
    color = '#00e5a0' if pct>=80 else '#ffb547' if pct>=50 else '#ff4d6a'
    return f'<div style="background:#0b1221;border-radius:4px;height:6px;overflow:hidden"><div style="width:{pct}%;height:6px;background:{color};border-radius:4px;transition:width 1s ease"></div></div>'

def build_rows(items):
    rows = ''
    for item in items:
        icon = '✅' if item['result']=='PASS' else '❌'
        note = item.get('note','') or ''
        rows += f'''<tr>
          <td style="padding:9px 12px;border-bottom:1px solid #0f1a2e;color:#4d6080;font-family:monospace;font-size:12px">{item['id']}</td>
          <td style="padding:9px 12px;border-bottom:1px solid #0f1a2e;font-size:13px;color:#c8d8f0">{item['label']}</td>
          <td style="padding:9px 12px;border-bottom:1px solid #0f1a2e;font-size:16px;text-align:center">{icon}</td>
          <td style="padding:9px 12px;border-bottom:1px solid #0f1a2e;font-size:11px;color:#4d6080;font-family:monospace">{note}</td>
        </tr>'''
    return rows

def infra_cell(label, value):
    return f'<div style="padding:12px"><div style="font-size:10px;letter-spacing:.08em;text-transform:uppercase;color:#4d6080;margin-bottom:4px">{label}</div><div style="font-size:13px;color:#c8d8f0;word-break:break-all">{value or "Unknown"}</div></div>'

def health_cell(label, status):
    if status in ('PASS',): bg,color,icon='rgba(0,229,160,.08)','#00e5a0','✅'
    elif status=='WARNING':  bg,color,icon='rgba(255,181,71,.08)','#ffb547','⚠️'
    else:                    bg,color,icon='rgba(255,77,106,.08)', '#ff4d6a','❌'
    return f'<div style="background:{bg};border-radius:8px;padding:14px;text-align:center"><div style="font-size:18px;margin-bottom:4px">{icon}</div><div style="font-size:12px;font-weight:600;color:{color}">{label}</div></div>'

def generate_html(domain, data, scan_date):
    grade = data.get('grade','F')
    total = data.get('total_score',0)
    gc    = grade_color(grade)
    eh    = data.get('email_health',{})
    sc    = data.get('scores',{})
    ns    = ', '.join(data.get('nameservers',[])[:3]) or 'N/A'
    mx    = ', '.join(data.get('mx_records',[])[:2]) or 'N/A'

    recs_html = ''
    for r in data.get('recommendations',[])[:5]:
        recs_html += f'''<div style="display:flex;gap:14px;background:#0b1221;border-radius:8px;padding:14px;margin-bottom:10px">
          <span style="color:#00b4ff;font-weight:700;font-size:15px;min-width:20px">{r.get('priority','')}</span>
          <div>
            <div style="color:#e8f0fe;font-weight:600;font-size:14px">{r.get('title','')}</div>
            <div style="color:#4d6080;font-size:13px;margin-top:4px;line-height:1.6">{r.get('detail','')}</div>
          </div></div>'''

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Audit: {domain} — Next-Gen IT</title>
<style>
  *{{box-sizing:border-box;margin:0;padding:0}}
  body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:#050a14;color:#e8f0fe;line-height:1.5}}
  .card{{background:#0b1821;border:1px solid rgba(0,180,255,.1);border-radius:14px;padding:24px;margin-bottom:24px}}
  h2{{font-size:12px;font-weight:600;color:#4d6080;letter-spacing:.1em;text-transform:uppercase;margin-bottom:16px}}
  table{{width:100%;border-collapse:collapse}}
  a{{color:#00b4ff;text-decoration:none}}
</style>
</head>
<body>
<!-- HEADER -->
<div style="background:linear-gradient(135deg,#0d1f3c,#050a14);padding:40px 32px;border-bottom:1px solid rgba(0,180,255,.1)">
  <div style="max-width:920px;margin:0 auto">
    <div style="display:flex;align-items:center;gap:12px;margin-bottom:8px">
      <div style="background:#00b4ff;color:#000;font-family:monospace;font-weight:700;font-size:12px;padding:5px 10px;border-radius:6px">NG</div>
      <span style="font-size:12px;letter-spacing:.1em;color:#00b4ff;text-transform:uppercase;font-weight:600">Next-Gen IT · Domain Audit</span>
    </div>
    <h1 style="font-size:clamp(22px,4vw,38px);font-weight:800;margin:10px 0 6px">{domain}</h1>
    <div style="color:#4d6080;font-size:13px;font-family:monospace">Scanned {scan_date}</div>
    <div style="display:flex;flex-wrap:wrap;gap:20px;margin-top:28px;align-items:center">
      <div style="background:#0b1221;border:2px solid {gc};border-radius:12px;padding:14px 28px;text-align:center">
        <div style="font-size:48px;font-weight:800;color:{gc};line-height:1">{grade}</div>
        <div style="font-size:11px;color:#4d6080;letter-spacing:.06em;margin-top:4px">GRADE</div>
      </div>
      <div>
        <div style="font-size:36px;font-weight:800;color:#e8f0fe">{total}<span style="font-size:18px;color:#4d6080">/30</span></div>
        <div style="font-size:12px;color:#4d6080;margin-bottom:10px">Overall Score</div>
        <div style="display:flex;gap:20px;flex-wrap:wrap">
          <span style="font-size:13px;color:#8da0b8">SEO <b style="color:#e8f0fe">{data.get('website_score',0)}/10</b></span>
          <span style="font-size:13px;color:#8da0b8">Marketing <b style="color:#e8f0fe">{data.get('marketing_score',0)}/10</b></span>
          <span style="font-size:13px;color:#8da0b8">Tech/CRM <b style="color:#e8f0fe">{data.get('tech_score',0)}/10</b></span>
        </div>
      </div>
    </div>
  </div>
</div>

<div style="max-width:920px;margin:32px auto;padding:0 24px">

  <!-- INFRASTRUCTURE -->
  <div class="card">
    <h2>Infrastructure</h2>
    <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));border:1px solid rgba(0,180,255,.08);border-radius:8px;overflow:hidden">
      {infra_cell("Registrar",data.get("registrar"))}
      {infra_cell("DNS Host",data.get("dns_host"))}
      {infra_cell("Web Host / CDN",data.get("web_host"))}
      {infra_cell("CMS / Platform",data.get("cms"))}
      {infra_cell("Email Provider",data.get("email_provider"))}
      {infra_cell("IP Address",data.get("ip"))}
      {infra_cell("Registered",data.get("domain_created"))}
      {infra_cell("Expires",data.get("domain_expires"))}
    </div>
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-top:16px;padding-top:16px;border-top:1px solid rgba(0,180,255,.06)">
      <div><div style="font-size:10px;text-transform:uppercase;letter-spacing:.08em;color:#4d6080;margin-bottom:4px">Nameservers</div><div style="font-family:monospace;font-size:12px;color:#8da0b8">{ns}</div></div>
      <div><div style="font-size:10px;text-transform:uppercase;letter-spacing:.08em;color:#4d6080;margin-bottom:4px">MX Records</div><div style="font-family:monospace;font-size:12px;color:#8da0b8">{mx}</div></div>
    </div>
  </div>

  <!-- EMAIL HEALTH -->
  <div class="card">
    <h2>Email &amp; Domain Health</h2>
    <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:10px">
      {health_cell("MX Records",   eh.get("mx_records","FAIL"))}
      {health_cell("SPF",          eh.get("spf","FAIL"))}
      {health_cell("DMARC",        eh.get("dmarc","FAIL"))}
      {health_cell("DKIM",         eh.get("dkim","FAIL"))}
      {health_cell("Blacklist",    eh.get("blacklist","FAIL"))}
      {health_cell("SSL / HTTPS",  eh.get("ssl","FAIL"))}
    </div>
  </div>

  <!-- WEBSITE & SEO -->
  <div class="card">
    <h2>Website &amp; SEO — {data.get("website_score",0)}/10</h2>
    {score_bar(data.get("website_score",0))}
    <table style="margin-top:16px">
      <tbody>{build_rows(sc.get("website_seo",[]))}</tbody>
    </table>
  </div>

  <!-- MARKETING -->
  <div class="card">
    <h2>Marketing &amp; Social Media — {data.get("marketing_score",0)}/10</h2>
    {score_bar(data.get("marketing_score",0))}
    <table style="margin-top:16px">
      <tbody>{build_rows(sc.get("marketing_social",[]))}</tbody>
    </table>
  </div>

  <!-- TECH/CRM -->
  <div class="card">
    <h2>Tech Stack &amp; CRM — {data.get("tech_score",0)}/10</h2>
    {score_bar(data.get("tech_score",0))}
    <table style="margin-top:16px">
      <tbody>{build_rows(sc.get("tech_crm",[]))}</tbody>
    </table>
  </div>

  <!-- RECOMMENDATIONS -->
  <div class="card">
    <h2>Top Recommendations</h2>
    {recs_html}
  </div>

  <!-- PITCH -->
  <div class="card" style="border-color:rgba(0,180,255,.2);background:#0a1628">
    <h2 style="color:#00b4ff">Sales Pitch Angle</h2>
    <p style="font-size:15px;line-height:1.8;color:#c8d8f0">{data.get('pitch_angle','')}</p>
  </div>

  <div style="text-align:center;padding:32px 0;font-family:monospace;font-size:11px;color:#2a3a50">
    Generated by Next-Gen IT Domain Health Audit · {scan_date}<br>
    <a href="https://jeremiah9980.github.io/Next-Gen-IT/portal/">← Back to Portal</a>
  </div>

</div>
</body>
</html>'''

# ── MAIN ──────────────────────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 3:
        print('Usage: python run_audit.py <domain> <output_dir>', file=sys.stderr)
        sys.exit(1)

    domain     = clean_domain(sys.argv[1])
    output_dir = sys.argv[2]
    os.makedirs(output_dir, exist_ok=True)

    infra     = run_infrastructure(domain)
    mxtoolbox = run_mxtoolbox(domain)
    site_html = run_site_fetch(domain)
    data      = run_claude_analysis(domain, infra, mxtoolbox, site_html)

    scan_date = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')
    timestamp = datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')
    slug      = re.sub(r'[^a-z0-9\-]', '-', domain)
    filename  = f'{slug}-{timestamp}.html'

    print(f'[5/5] Writing report → reports/{filename}')
    html = generate_html(domain, data, scan_date)
    with open(os.path.join(output_dir, filename), 'w', encoding='utf-8') as f:
        f.write(html)

    meta = {
        'domain':      domain,
        'filename':    filename,
        'scan_date':   scan_date,
        'timestamp':   timestamp,
        'grade':       data.get('grade','F'),
        'total_score': data.get('total_score', 0),
        'url':         f'https://jeremiah9980.github.io/Next-Gen-IT/reports/{filename}'
    }
    with open(os.path.join(output_dir, '_latest_meta.json'), 'w') as f:
        json.dump(meta, f, indent=2)

    print(f'Done! Grade: {meta["grade"]} · Score: {meta["total_score"]}/30')
    print(json.dumps(meta))

if __name__ == '__main__':
    main()
