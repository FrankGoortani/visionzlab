#!/usr/bin/env python3
"""Generate the static VisionzLab site.

Pages are plain HTML written into the repo and served by GitHub Pages as-is;
this script only removes the need to hand-copy the header, footer, analytics
and structured data across pages. Python 3 standard library only.

    python3 tools/build.py        # rewrite every page, sitemap.xml and llms.txt
"""
import datetime
import html
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE = "https://visionzlab.com"
BRAND = "VisionzLab"
TODAY = datetime.date.today().isoformat()

# Contact and analytics endpoints. Both are personal-account hostnames for now;
# swap them here once brand-neutral replacements exist.
CONTACT_URL = "https://frankgoortani.typeform.com/to/VaoYV6iJ"
UMAMI_HOST = "https://goortani.synology.me:3100"
UMAMI_SITE_ID = "571a5a54-c7bd-41d4-969d-3026dae95234"

LEGAL_NAME = "VisionZone One Consulting Inc."
EMAIL_GENERAL = "frank@visionzlab.com"
EMAIL_SALES = "asal@visionzlab.com"

ORG_ID = f"{SITE}/#organization"
ORG = {
    "@type": "ProfessionalService",
    "@id": ORG_ID,
    "name": BRAND,
    "url": f"{SITE}/",
    "logo": f"{SITE}/public/preview.webp",
    "description": "VisionzLab helps small and mid-sized businesses put AI to work — "
                   "from teaching teams to build their own agents to building and running AI employees.",
    "legalName": "VisionZone One Consulting Inc.",
    "email": "frank@visionzlab.com",
    "areaServed": ["CA", "US"],
    "address": {"@type": "PostalAddress", "addressRegion": "ON", "addressCountry": "CA"},
    "contactPoint": [
        {"@type": "ContactPoint", "contactType": "sales", "email": "asal@visionzlab.com",
         "areaServed": ["CA", "US"], "availableLanguage": ["en"]},
        {"@type": "ContactPoint", "contactType": "customer support", "email": "frank@visionzlab.com",
         "areaServed": ["CA", "US"], "availableLanguage": ["en"]},
    ],
}

e = html.escape

# --------------------------------------------------------------------------
# Content
# --------------------------------------------------------------------------

TIERS = [
    {
        "slug": "services/ai-training/",
        "tier": "Teach",
        "nav": "AI Training",
        "title": "AI Agent Training for Small Businesses",
        "description": "Hands-on workshops and coaching that teach your team to set up and run "
                       "their own AI agents and automations with tools you already pay for.",
        "lead": "We teach your team to build and run their own AI agents — so the know-how stays in-house.",
        "for": "Owners and teams who want to do it themselves and need someone to show them how.",
        "get": [
            "A hands-on workshop built around your own day-to-day work, not generic demos",
            "Your team sets up its first working agents during the session",
            "A written playbook: which tools, which tasks, which guardrails",
            "Follow-up coaching sessions as your team takes on more",
        ],
        "how": [
            ("Pick the work", "We spend a short call finding the repetitive tasks worth automating first."),
            ("Workshop", "A half-day or full-day session where your team builds, with us beside them."),
            ("Coach", "Short check-ins while your team rolls agents out to real work."),
        ],
        "next": "services/ai-agent-setup/",
        "faq": [
            ("Do we need technical staff?", "No. The workshops are designed for business teams. "
             "If you have technical people, we go deeper with them."),
            ("Which tools do you teach?", "The ones that fit your business — usually the AI assistants and "
             "automation tools you already have access to. We don't sell software licences."),
            ("Can you do it remotely?", "Yes. Workshops run online or on site."),
        ],
    },
    {
        "slug": "services/ai-agent-setup/",
        "tier": "Guided setup",
        "nav": "Agent Setup",
        "title": "AI Agent Setup Service",
        "description": "We set up your first AI agent with your team, connect it to your tools, "
                       "and hand it over with a playbook so you can run it yourselves.",
        "lead": "We set up your first AI agent alongside your team, then hand it over with everything you need to run it.",
        "for": "Businesses that want a working agent quickly, and want to own it afterwards.",
        "get": [
            "One agent configured for a real task in your business",
            "Connected to the tools and data it needs, with sensible permissions",
            "Your team trained on running, adjusting and checking it",
            "A handover playbook and a short support window after go-live",
        ],
        "how": [
            ("Scope", "We agree one task, what good looks like, and what the agent may and may not do."),
            ("Set up together", "We configure it with your team in the room, so nothing is a black box."),
            ("Hand over", "You run it. We stay on call for a short window to tune it."),
        ],
        "next": "services/ai-development/",
        "faq": [
            ("How long does setup take?", "Usually days, not months, for a single well-defined task."),
            ("Who owns the agent?", "You do. It runs on your accounts and tools."),
            ("What if it needs more than off-the-shelf tools?", "Then it's a build — see AI Agent Development."),
        ],
    },
    {
        "slug": "services/ai-development/",
        "tier": "Build",
        "nav": "AI Development",
        "title": "Custom AI Agent Development",
        "description": "Fixed-scope, fixed-price development of production AI agents and automations, "
                       "built to your requirements and handed over to your team.",
        "lead": "We design and build a production AI agent or automation to your requirements, at a fixed price, and hand it over.",
        "for": "Businesses with a clear use case that off-the-shelf tools can't handle.",
        "get": [
            "A production-grade AI agent or automation, integrated with your systems",
            "Human approval steps, audit logs and guardrails where they matter",
            "Fixed scope and fixed price agreed before work starts",
            "Documentation and a handover so your team can own it",
        ],
        "how": [
            ("Discovery", "A short paid sprint that ends in a working prototype and a costed plan."),
            ("Build", "Milestone-based delivery with demos along the way."),
            ("Hand over", "Production release, documentation and training for your team."),
        ],
        "next": "services/ai-employee/",
        "faq": [
            ("How long does a build take?", "Most first builds take 4–12 weeks depending on scope and integrations."),
            ("Do you work with our existing systems?", "Yes. Integration with what you already run is the point."),
            ("What happens after handover?", "You own it. If you'd rather we keep it running, see AI Employee."),
        ],
    },
    {
        "slug": "services/ai-employee/",
        "tier": "Build & maintain",
        "nav": "AI Employee",
        "title": "Managed AI Employee for Your Business",
        "description": "We build an AI employee for a defined role — bookkeeping, intake, reporting, follow-ups — "
                       "and keep it working for a monthly fee. Cheaper than a hire.",
        "lead": "We build an AI employee for a defined role in your business and keep it working for a monthly fee.",
        "for": "Businesses that want the result without having to maintain the technology.",
        "get": [
            "An AI employee set up for one defined role, such as routine bookkeeping or intake",
            "Regular maintenance: updates, fixes and improvements on a schedule",
            "A monthly report on what it did and where a person had to step in",
            "People stay in charge of anything that needs judgment or sign-off",
        ],
        "how": [
            ("Define the role", "We map the tasks, the rules, and where a person must approve."),
            ("Build and launch", "We build it, run it alongside your team, then hand it the work."),
            ("Maintain", "We look after it month to month so it keeps doing the job well."),
        ],
        "next": "services/ai-team/",
        "faq": [
            ("Is this cheaper than hiring?", "For routine, rules-based work it usually is — a setup fee and a "
             "predictable monthly fee instead of a salary."),
            ("What does maintenance include?", "Scheduled care: updates, fixes within business days, and "
             "improvements. It is not a 24/7 on-call service."),
            ("Who checks its work?", "Your team approves anything sensitive. The AI employee prepares; people decide."),
        ],
    },
    {
        "slug": "services/ai-team/",
        "tier": "Embedded capacity",
        "nav": "AI Team",
        "title": "An AI Engineering Team Instead of a New Hire",
        "description": "Before you hire a software or AI engineer, consider senior AI engineering capacity on "
                       "retainer, building what the role would build with an AI-first stack.",
        "lead": "Senior AI engineering capacity on retainer — building what a new hire would build, without the hire.",
        "for": "Companies about to hire for software, automation or AI work.",
        "get": [
            "Senior architects and engineers working as an extension of your team",
            "An AI-first delivery stack, so small teams ship what larger ones used to",
            "Flexible monthly capacity you can scale up or down",
            "No recruiting cycle, no ramp-up, no long-term headcount commitment",
        ],
        "how": [
            ("Share the role", "Send us the job description. We tell you which parts we can take on."),
            ("Agree capacity", "A monthly retainer or flexible capacity, agreed together and sized to the work."),
            ("Ship", "We work in your tools and rhythm, with regular demos and reviews."),
        ],
        "next": None,
        "faq": [
            ("Is this staff augmentation?", "Partly. You get senior people, but we also bring the AI tooling "
             "and delivery approach that make a small team go further."),
            ("Can we start small?", "Yes. Many clients start with one defined project and grow from there."),
            ("Where is the team?", "Based in Canada, working with clients across Canada and the US."),
        ],
    },
]

PLAYS = [
    {
        "slug": "for/small-business/",
        "nav": "Small Business",
        "title": "AI for Small Business",
        "description": "Practical AI for owner-run businesses: learn to build your own agents, get one set up "
                       "with you, or have us build and run one.",
        "lead": "Practical AI for owner-run businesses — start small, keep control, grow from there.",
        "body": [
            "You don't need an AI strategy deck. You need the repetitive work off your team's plate.",
            "Most small businesses start by learning to set up a few agents themselves. When something "
            "needs more than off-the-shelf tools, we build it. If you'd rather not look after it, we run it for you.",
        ],
        "tiers": [0, 1, 3],
        "ref": "play-a",
    },
    {
        "slug": "for/accountants-bookkeepers/",
        "nav": "Accountants & Bookkeepers",
        "title": "AI Bookkeeping Automation for Accounting Firms",
        "description": "An AI employee that handles routine bookkeeping tasks for accounting and bookkeeping "
                       "practices — or training so your team can build it themselves.",
        "lead": "An AI employee for the routine bookkeeping work — so your team spends its time on clients.",
        "body": [
            "Categorising transactions, chasing missing receipts, reconciling, preparing month-end packages: "
            "rules-based work that eats hours every week.",
            "We can teach your team to automate it, set it up with you, or build and maintain an AI employee "
            "that does it for a monthly fee. Your accountants stay in charge of every judgment and every sign-off.",
            "Client financial data is handled under clear privacy and security terms in every engagement.",
        ],
        "tiers": [0, 1, 3],
        "ref": "play-c",
    },
    {
        "slug": "instead-of-hiring/",
        "nav": "Instead of Hiring",
        "title": "Hiring an AI or Software Engineer? Try This First",
        "description": "Before you fill a software, automation or AI role, see whether a senior AI engineering "
                       "team can build what the role would build — faster, with no hiring cycle.",
        "lead": "Before you fill that software or AI role, see whether we can build what it would build.",
        "body": [
            "Hiring takes months, and the first quarter of any new role is ramp-up. Much of what a new software "
            "or AI hire is asked to build — integrations, internal tools, automations, AI agents — we can deliver "
            "as a defined project or as ongoing capacity.",
            "Send us the job description. We'll tell you plainly which parts we can take on, how long it would "
            "take, and what it would cost — and which parts really do need a permanent hire.",
        ],
        "tiers": [2, 4],
        "ref": "play-b",
    },
]

USE_CASES = [
    {
        "slug": "use-cases/market-intelligence/",
        "nav": "Market Intelligence",
        "title": "AI Market Intelligence Agent",
        "description": "An AI agent that tracks competitors, pricing, news and market signals and delivers a "
                       "weekly brief your leadership team can act on.",
        "lead": "An AI agent that watches your market and competitors, and turns it into a brief your team reads every week.",
        "for": "Leadership, strategy and product teams that need to know what competitors and the market are doing.",
        "does": [
            "Tracks competitor websites, pricing pages, product releases, job postings and news",
            "Reads public filings, industry publications and reports you point it at",
            "Flags what changed, why it may matter, and what to watch next",
            "Delivers a weekly brief, with sources linked for every point",
        ],
        "people": "Your team decides what it means and what to do about it. The agent gathers, summarises "
                  "and cites; it doesn't set strategy.",
        "tiers": [1, 2, 3],
        "faq": [
            ("Which sources can it use?", "Public sources plus any subscriptions and internal documents you "
             "give it access to. Every point in a brief links back to its source."),
            ("How is this different from a news alert?", "It reads, compares and summarises across sources, "
             "and tells you what changed since last week instead of sending every mention."),
            ("Can we start small?", "Yes. Most teams start with a handful of competitors and one weekly brief."),
        ],
    },
    {
        "slug": "use-cases/prospect-research/",
        "nav": "Prospect Research",
        "title": "AI Prospect Research and Account Planning Agent",
        "description": "An AI agent that researches target accounts, maps buying teams and drafts account plans, "
                       "so your business development team spends its time selling.",
        "lead": "An AI agent that researches target accounts and drafts account plans, so your team spends its time selling.",
        "for": "Business development and sales teams who lose hours to research before every conversation.",
        "does": [
            "Builds a profile of each target account from public sources",
            "Finds recent events worth starting a conversation about",
            "Maps likely decision-makers and the roles that matter",
            "Drafts an account plan and first-call questions for your team to edit",
        ],
        "people": "Your team chooses the accounts, checks the research and owns every conversation. "
                  "The agent prepares; it never contacts anyone on its own.",
        "tiers": [1, 2, 3],
        "faq": [
            ("Does it send emails or messages?", "No. It researches and drafts. Your team reviews, decides and sends."),
            ("Does it work with our CRM?", "Yes. It can read from and write research back to the CRM you use."),
            ("How accurate is it?", "Every fact links to its source, so your team can check before using it."),
        ],
    },
    {
        "slug": "use-cases/planning-okrs/",
        "nav": "Planning & OKRs",
        "title": "AI Planning and OKR Assistant",
        "description": "An AI assistant that turns leadership goals into tracked objectives and key results, "
                       "collects progress from your tools, and writes the monthly update.",
        "lead": "An AI assistant that turns your goals into tracked objectives, and keeps everyone current on progress.",
        "for": "Leadership teams who set goals well and then lose track of them between planning sessions.",
        "does": [
            "Helps turn goals into clear objectives, key results and owners",
            "Collects progress from the tools your team already uses",
            "Flags what is behind, blocked or at risk, before the review meeting",
            "Drafts the monthly progress update for leadership to review",
        ],
        "people": "Leadership sets the goals and makes the calls. The assistant keeps the plan current and "
                  "the reporting done.",
        "tiers": [0, 1, 2],
        "faq": [
            ("Do we need OKR software?", "No. It can work from spreadsheets, documents and project tools you already have."),
            ("Can you facilitate the planning session?", "We help your team set it up so the assistant has a "
             "clear plan to track. Your leadership team owns the goals."),
            ("Who sees the data?", "Only the people you choose. It runs on your accounts and permissions."),
        ],
    },
    {
        "slug": "use-cases/financial-reporting/",
        "nav": "Financial Reporting",
        "title": "AI Financial Reporting Agent",
        "description": "An AI agent that pulls numbers from your accounting and business systems, prepares "
                       "monthly reports and drafts variance commentary for your finance team to review.",
        "lead": "An AI agent that prepares your monthly reporting and drafts the commentary, for your finance team to review.",
        "for": "Owners and finance teams who spend days every month assembling the same reports.",
        "does": [
            "Pulls figures from your accounting and business systems",
            "Prepares monthly management reports and dashboards",
            "Drafts variance commentary: what moved, by how much, and the likely drivers",
            "Prepares the inputs for forecasts and budget reviews",
        ],
        "people": "Your finance team reviews every report and owns every number and decision. The agent "
                  "prepares; it does not give financial advice or sign off.",
        "tiers": [1, 2, 3],
        "faq": [
            ("Which systems does it work with?", "Common accounting and spreadsheet tools, plus other business "
             "systems with an export or an API. We confirm this in the discovery session."),
            ("Is our financial data safe?", "It runs on your accounts with the permissions you set, under clear "
             "privacy and security terms in every engagement."),
            ("Does it replace our accountant?", "No. It takes the assembly work off your team so they can focus "
             "on judgment and advice."),
        ],
    },
]

FAQ_SPRINT = [
    ("What does the sprint cost?", "It's a fixed fee agreed before we start, based on the size of the workflow."),
    ("What if the answer is no-go?", "Then you've spent a few weeks, not a budget, finding out — and you keep the findings."),
    ("Is there a free option?", "Yes. The first conversation is a free discovery session, with a short memo afterwards."),
]

ASAL = {
    "slug": "team/asal-matinsadeghy/",
    "name": "Asal Matinsadeghy",
    "role": "VP Business Development",
}

# --------------------------------------------------------------------------
# Rendering
# --------------------------------------------------------------------------


def url(slug):
    return f"{SITE}/{slug}"


def rel(from_slug, to_slug):
    """Relative link between two page slugs (directory-style)."""
    depth = from_slug.count("/")
    return "../" * depth + to_slug if to_slug else ("../" * depth or "./")


SECTION_NAMES = {"services/": "Services", "use-cases/": "Use Cases"}


def breadcrumbs_ld(slug, title):
    crumbs = [("", "Home")]
    section = slug.split("/")[0] + "/"
    if slug.count("/") > 1 and section in SECTION_NAMES:
        crumbs.append((section, SECTION_NAMES[section]))
    crumbs.append((slug, title))
    return {"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": n, "item": url(s)} for i, (s, n) in enumerate(crumbs)]}


def contact(ref, label="Book a free discovery session", cls="btn"):
    return (f'<a class="{cls}" href="{CONTACT_URL}#ref={e(ref)}" data-contact data-ref="{e(ref)}" '
            f'data-umami-event="contact_click" data-umami-event-location="{e(ref)}" '
            f'target="_blank" rel="noopener">{e(label)}</a>')


def faq_html(faq):
    items = "".join(f"<details><summary>{e(q)}</summary><p>{e(a)}</p></details>" for q, a in faq)
    return f'<section class="section"><h2>Questions</h2><div class="faq">{items}</div></section>'


def faq_ld(faq):
    return {"@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq]}


def ladder(slug, highlight=None, only=None):
    cards = []
    for i, t in enumerate(TIERS):
        if only is not None and i not in only:
            continue
        on = " card-on" if t["slug"] == highlight else ""
        cards.append(
            f'<a class="card{on}" href="{rel(slug, t["slug"])}">'
            f'<span class="tag">{i + 1} · {e(t["tier"])}</span>'
            f'<h3>{e(t["nav"])}</h3><p>{e(t["lead"])}</p></a>')
    return f'<div class="cards">{"".join(cards)}</div>'


def page(slug, title, description, main, ld=None, ref="site"):
    canonical = url(slug)
    full_title = f"{title} | {BRAND}" if slug else f"{BRAND} | {title}"
    nav = [("services/", "Services"), ("use-cases/", "Use Cases"), ("discovery-sprint/", "Discovery Sprint"),
           ("about/", "About")]
    nav_html = "".join(f'<a href="{rel(slug, s)}">{e(n)}</a>' for s, n in nav)
    foot_tiers = "".join(f'<li><a href="{rel(slug, t["slug"])}">{e(t["nav"])}</a></li>' for t in TIERS)
    foot_plays = "".join(f'<li><a href="{rel(slug, p["slug"])}">{e(p["nav"])}</a></li>' for p in PLAYS)
    foot_uses = "".join(f'<li><a href="{rel(slug, u["slug"])}">{e(u["nav"])}</a></li>' for u in USE_CASES)
    graph = [ORG] + (ld or []) + ([breadcrumbs_ld(slug, title)] if slug else [])
    css = rel(slug, "site.css")
    return f"""<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{e(full_title)}</title>
    <meta name="description" content="{e(description)}" />
    <meta name="robots" content="index, follow" />
    <link rel="canonical" href="{canonical}" />
    <meta property="og:type" content="website" />
    <meta property="og:site_name" content="{BRAND}" />
    <meta property="og:title" content="{e(full_title)}" />
    <meta property="og:description" content="{e(description)}" />
    <meta property="og:url" content="{canonical}" />
    <meta property="og:image" content="{SITE}/public/preview.webp" />
    <meta name="twitter:card" content="summary_large_image" />
    <meta name="twitter:title" content="{e(full_title)}" />
    <meta name="twitter:description" content="{e(description)}" />
    <meta name="twitter:image" content="{SITE}/public/preview.webp" />
    <link rel="icon" href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><text y=%22.9em%22 font-size=%2290%22>V</text></svg>" />
    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
    <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" />
    <link rel="stylesheet" href="{css}" />
    <script type="application/ld+json">{json.dumps({"@context": "https://schema.org", "@graph": graph}, indent=None)}</script>
  </head>
  <body>
    <header class="top">
      <div class="wrap top-in">
        <a class="brand" href="{rel(slug, '')}">{BRAND}</a>
        <nav class="nav">{nav_html}{contact(ref + '-nav', 'Book a call', 'btn btn-sm')}</nav>
      </div>
    </header>
    <main>
{main}
    </main>
    <footer class="foot">
      <div class="wrap foot-in">
        <div><a class="brand" href="{rel(slug, '')}">{BRAND}</a>
          <p class="muted">AI agents and automation for small and mid-sized businesses.<br />
          Based in Ontario, Canada · serving Canada and the US.</p></div>
        <div><h4>Services</h4><ul>{foot_tiers}<li><a href="{rel(slug, 'discovery-sprint/')}">Discovery Sprint</a></li></ul></div>
        <div><h4>Use cases</h4><ul>{foot_uses}</ul></div>
        <div><h4>Who we help</h4><ul>{foot_plays}</ul></div>
        <div><h4>Company</h4><ul><li><a href="{rel(slug, 'about/')}">About</a></li>
          <li><a href="{rel(slug, ASAL['slug'])}">Business Development</a></li>
          <li><a href="mailto:{EMAIL_SALES}">{EMAIL_SALES}</a></li>
          <li><a href="mailto:{EMAIL_GENERAL}">{EMAIL_GENERAL}</a></li></ul></div>
      </div>
      <div class="wrap muted small">© {datetime.date.today().year} {LEGAL_NAME} · {BRAND} is a brand of
        {LEGAL_NAME}, an Ontario corporation.</div>
    </footer>
    <script>
{TRACKER_JS}
    </script>
  </body>
</html>
"""


TRACKER_JS = """      (function () {
        // Carry ?ref= from the landing URL into every contact link so the lead
        // source survives to the booking form (lead-source rules, section 3).
        var params = new URLSearchParams(location.search);
        var inbound = params.get('ref');
        if (inbound) { try { sessionStorage.setItem('vz_ref', inbound); } catch (_) {} }
        var stored = null;
        try { stored = sessionStorage.getItem('vz_ref'); } catch (_) {}
        document.querySelectorAll('[data-contact]').forEach(function (a) {
          var ref = stored ? stored + '~' + a.getAttribute('data-ref') : a.getAttribute('data-ref');
          a.href = a.href.split('#')[0] + '#ref=' + encodeURIComponent(ref);
        });

        var UMAMI_HOST = '__UMAMI_HOST__';
        var UMAMI_ID = '__UMAMI_ID__';
        var queue = [];
        function track(name, data) {
          if (window.umami && typeof window.umami.track === 'function') {
            try { window.umami.track(name, data || {}); } catch (_) {}
          } else { queue.push([name, data || {}]); }
        }
        function load() {
          if (!UMAMI_ID) return;
          var s = document.createElement('script');
          s.defer = true; s.src = UMAMI_HOST + '/script.js';
          s.setAttribute('data-website-id', UMAMI_ID);
          s.onload = function () { queue.splice(0).forEach(function (q) { track(q[0], q[1]); }); };
          document.head.appendChild(s);
        }
        document.addEventListener('click', function (ev) {
          var el = ev.target.closest && ev.target.closest('[data-umami-event]');
          if (el) track(el.getAttribute('data-umami-event'), {
            location: el.getAttribute('data-umami-event-location') || '', ref: stored || '' });
        }, { capture: true });
        if (document.readyState === 'complete') load();
        else window.addEventListener('load', load, { once: true });
      })();"""


def hero(h1, lead, ref, eyebrow=None, cta="Book a free discovery session"):
    eb = f'<p class="eyebrow">{e(eyebrow)}</p>' if eyebrow else ""
    return (f'<section class="hero"><div class="wrap">{eb}<h1>{e(h1)}</h1>'
            f'<p class="lead">{e(lead)}</p><div class="actions">{contact(ref, cta)}</div></div></section>')


def cta_band(ref):
    return (f'<section class="band"><div class="wrap band-in"><div><h2>Not sure where to start?</h2>'
            f'<p>Book a free discovery session. We\'ll look at your work together and tell you plainly '
            f'where AI would help — and where it wouldn\'t.</p></div>{contact(ref)}</div></section>')


def service_ld(slug, name, description):
    return {"@type": "Service", "@id": url(slug) + "#service", "name": name, "description": description,
            "provider": {"@id": ORG_ID}, "areaServed": ["CA", "US"], "url": url(slug)}


# --------------------------------------------------------------------------
# Pages
# --------------------------------------------------------------------------


def build_home():
    slug = ""
    main = f"""
{hero("AI that takes work off your team's plate.",
      "We help small and mid-sized businesses put AI agents to work — from teaching your team to build "
      "their own, to building and running an AI employee for you.", "home", "AI agents & automation")}
<section class="section"><div class="wrap split">
  <div><p class="eyebrow">Start here</p><h2>The Discovery Sprint</h2>
  <p>A short, paid sprint on one of your workflows. In 2–4 weeks you get a working prototype, a costed
  build plan and a clear go/no-go — before you commit to anything bigger.</p>
  <p><a class="link" href="discovery-sprint/">How the sprint works →</a></p></div>
  <picture><source srcset="public/computer.webp" type="image/webp" />
  <img src="public/computer.svg" alt="" width="640" height="540" class="art" fetchpriority="high" /></picture>
</div></section>
<section class="section alt"><div class="wrap">
  <p class="eyebrow">Five ways to work with us</p>
  <h2>Do it yourself, do it together, or let us do it.</h2>
  <p class="muted">Start wherever fits. Most clients begin small and move up as they see results.</p>
  {ladder(slug)}
</div></section>
<section class="section"><div class="wrap">
  <p class="eyebrow">Use cases</p><h2>Agents for strategy, growth and finance teams.</h2>
  {use_case_cards(slug)}
  <p style="margin-top:20px"><a class="link" href="use-cases/">All use cases →</a></p>
</div></section>
<section class="section alt"><div class="wrap">
  <p class="eyebrow">Who we help</p><h2>Built for businesses without an AI team.</h2>
  <div class="cards cards-3">{''.join(f'<a class="card" href="{p["slug"]}"><h3>{e(p["nav"])}</h3><p>{e(p["lead"])}</p></a>' for p in PLAYS)}</div>
</div></section>
{cta_band("home-band")}"""
    return page(slug, "AI Agents & Automation for Small Businesses",
                ORG["description"], main, ref="home")


def build_services():
    slug = "services/"
    desc = ("Five ways to put AI to work: AI training, guided agent setup, custom AI development, "
            "a managed AI employee, or an AI engineering team instead of a hire.")
    main = f"""
{hero("Five ways to work with us", "From teaching your team to building and running it for you. "
      "Pick the level of help that fits — and change it as you go.", "services")}
<section class="section"><div class="wrap">{ladder(slug)}</div></section>
{cta_band("services-band")}"""
    return page(slug, "AI Services", desc, main, ref="services")


def build_tier(i):
    t = TIERS[i]
    slug = t["slug"]
    get = "".join(f"<li>{e(x)}</li>" for x in t["get"])
    how = "".join(f'<li><strong>{e(a)}</strong><span>{e(b)}</span></li>' for a, b in t["how"])
    nxt = ""
    if t["next"]:
        n = next(x for x in TIERS if x["slug"] == t["next"])
        nxt = f'<p><a class="link" href="{rel(slug, n["slug"])}">Need more? See {e(n["nav"])} →</a></p>'
    ref = slug.split("/")[1]
    main = f"""
{hero(t["title"], t["lead"], ref, f'Service {i + 1} of 5 · {t["tier"]}')}
<section class="section"><div class="wrap split">
  <div><h2>Who it's for</h2><p>{e(t["for"])}</p><h2>What you get</h2><ul class="ticks">{get}</ul>{nxt}</div>
  <div><h2>How it works</h2><ol class="steps">{how}</ol></div>
</div></section>
<div class="wrap">{faq_html(t["faq"])}</div>
<section class="section alt"><div class="wrap"><h2>All five services</h2>{ladder(slug, highlight=slug)}</div></section>
{cta_band(ref + "-band")}"""
    return page(slug, t["title"], t["description"], main,
                ld=[service_ld(slug, t["title"], t["description"]), faq_ld(t["faq"])], ref=ref)


def build_play(p):
    slug = p["slug"]
    body = "".join(f"<p>{e(x)}</p>" for x in p["body"])
    main = f"""
{hero(p["title"], p["lead"], p["ref"])}
<section class="section"><div class="wrap narrow">{body}</div></section>
<section class="section alt"><div class="wrap"><h2>Where clients usually start</h2>{ladder(slug, only=p["tiers"])}
<p><a class="link" href="{rel(slug, 'services/')}">See all five services →</a></p></div></section>
{cta_band(p["ref"] + "-band")}"""
    return page(slug, p["title"], p["description"], main, ref=p["ref"])


def use_case_cards(slug, exclude=None):
    cards = "".join(
        f'<a class="card" href="{rel(slug, u["slug"])}"><span class="tag">Use case</span>'
        f'<h3>{e(u["nav"])}</h3><p>{e(u["lead"])}</p></a>' for u in USE_CASES if u["slug"] != exclude)
    return f'<div class="cards cards-3">{cards}</div>'


def build_use_cases():
    slug = "use-cases/"
    desc = ("AI agents for leadership, business development and finance teams: market intelligence, prospect "
            "research, planning and OKRs, and financial reporting.")
    main = f"""
{hero("AI agents for strategy, growth and finance teams", "Agents that do the research, tracking and "
      "reporting behind good decisions — so your people can spend their time making them.", "use-cases", "Use cases")}
<section class="section"><div class="wrap">{use_case_cards(slug)}
<p class="muted" style="margin-top:28px">Every use case can be taught, set up with you, built, or built and run
for you. <a class="link" href="{rel(slug, 'services/')}">See the five ways to work with us →</a></p></div></section>
{cta_band("use-cases-band")}"""
    return page(slug, "AI Agent Use Cases", desc, main, ref="use-cases")


def build_use_case(u):
    slug = u["slug"]
    does = "".join(f"<li>{e(x)}</li>" for x in u["does"])
    ref = "uc-" + slug.split("/")[1]
    main = f"""
{hero(u["title"], u["lead"], ref, "Use case")}
<section class="section"><div class="wrap split">
  <div><h2>Who it's for</h2><p>{e(u["for"])}</p><h2>What the agent does</h2><ul class="ticks">{does}</ul></div>
  <div><h2>What stays with your people</h2><p>{e(u["people"])}</p>
  <h2>How to get it</h2><p class="muted">Pick the level of help that fits.</p>{ladder(slug, only=u["tiers"])}</div>
</div></section>
<div class="wrap">{faq_html(u["faq"])}</div>
<section class="section alt"><div class="wrap"><h2>More use cases</h2>{use_case_cards(slug, exclude=slug)}</div></section>
{cta_band(ref + "-band")}"""
    return page(slug, u["title"], u["description"], main,
                ld=[service_ld(slug, u["title"], u["description"]), faq_ld(u["faq"])], ref=ref)


def build_sprint():
    slug = "discovery-sprint/"
    desc = ("A short, paid AI discovery sprint on one workflow: a working prototype, a costed build plan "
            "and a clear go/no-go in 2–4 weeks.")
    steps = [("Free discovery session", "A 60–90 minute conversation about your work, followed by a short memo "
              "with what we'd look at first."),
             ("Sprint kickoff", "We agree one workflow, the success measure, and access to what we need."),
             ("Prototype", "We build a working prototype on your real process."),
             ("Plan and decision", "You get a costed build plan and our honest go/no-go recommendation.")]
    how = "".join(f'<li><strong>{e(a)}</strong><span>{e(b)}</span></li>' for a, b in steps)
    main = f"""
{hero("The Discovery Sprint", "One workflow. Two to four weeks. A working prototype, a costed build plan "
      "and a clear go/no-go — before you commit to anything bigger.", "sprint", "Start here")}
<section class="section"><div class="wrap split">
  <div><h2>What you walk away with</h2><ul class="ticks">
    <li>A working prototype on your own process</li><li>A costed, phased build plan</li>
    <li>A clear go/no-go, with the reasons</li><li>A view of the risks and what would need to be true</li></ul></div>
  <div><h2>How it works</h2><ol class="steps">{how}</ol></div>
</div></section>
<div class="wrap">{faq_html(FAQ_SPRINT)}</div>
<section class="section alt"><div class="wrap"><h2>After the sprint</h2>
<p class="muted">Take the plan and build it yourselves, or pick the level of help that fits.</p>{ladder(slug, only=[0, 2, 3, 4])}</div></section>
{cta_band("sprint-band")}"""
    return page(slug, "AI Discovery Sprint", desc, main,
                ld=[service_ld(slug, "AI Discovery Sprint", desc), faq_ld(FAQ_SPRINT)], ref="sprint")


def build_about():
    slug = "about/"
    desc = ("VisionzLab is an AI studio that helps small and mid-sized businesses put AI agents to work, "
            "with senior architects and an AI-first way of building.")
    main = f"""
{hero("About VisionzLab", "We help businesses without an AI team put AI to work — practically, "
      "safely, and at a size that makes sense for them.", "about")}
<section class="section"><div class="wrap narrow">
  <h2>What we believe</h2>
  <p>Most businesses don't need an AI strategy. They need specific work taken off their team's plate, by
  something they can trust and understand.</p>
  <p>So we meet clients where they are. Some want to learn to do it themselves. Some want it built.
  Some want it built and looked after. We're comfortable with all three, and we'd rather start small
  and earn the next project than sell something too big.</p>
  <h2>How we work</h2>
  <ul class="ticks">
    <li><strong>Senior people.</strong> Architects with more than two decades of software and architecture
    experience, who have shipped production AI systems.</li>
    <li><strong>AI-first delivery.</strong> We build with AI ourselves, so small projects stay small and
    larger ones move fast.</li>
    <li><strong>People stay in charge.</strong> Approval steps, audit trails and clear limits on what an
    agent may do are part of every build.</li>
    <li><strong>Honest scoping.</strong> Fixed prices where the scope is clear, and a plain answer when AI
    isn't the right tool.</li>
  </ul>
  <h2>Where we work</h2>
  <p>We're based in Ontario, Canada, and work with clients across Canada and the United States, online or on site.</p>
  <p><a class="link" href="{rel(slug, ASAL['slug'])}">Meet our VP of Business Development →</a></p>
</div></section>
{cta_band("about-band")}"""
    return page(slug, "About", desc, main, ref="about")


def build_asal():
    slug = ASAL["slug"]
    name, role = ASAL["name"], ASAL["role"]
    desc = f"{name} is {role} at {BRAND}, the first point of contact for new clients."
    person = {"@type": "Person", "@id": url(slug) + "#person", "name": name, "jobTitle": role,
              "email": f"mailto:{EMAIL_SALES}",
              "worksFor": {"@id": ORG_ID}, "image": f"{SITE}/public/team/asal.jpg", "url": url(slug)}
    main = f"""
<section class="section"><div class="wrap person">
  <picture><source srcset="{rel(slug, 'public/team/asal.webp')}" type="image/webp" />
  <img src="{rel(slug, 'public/team/asal.jpg')}" alt="{e(name)}, {e(role)} at {BRAND}" width="720" height="900" class="portrait" /></picture>
  <div>
    <p class="eyebrow">{e(role)}</p>
    <h1>{e(name)}</h1>
    <p class="lead">Asal leads business development at {BRAND}. She is the first person most clients speak to,
    and stays their point of contact from the first conversation through delivery and beyond.</p>
    <p>She works with owners and leadership teams to find where AI can take real work off their people —
    and is just as quick to say when it can't. Her job is to make sure every engagement starts at the
    right size, with a clear outcome both sides can measure.</p>
    <div class="actions">{contact('asal', 'Book a conversation with Asal')}
      <a class="btn btn-ghost" href="mailto:{EMAIL_SALES}">{EMAIL_SALES}</a></div>
  </div>
</div></section>
{cta_band("asal-band")}"""
    return page(slug, f"{name}, {role}", desc, main, ld=[person], ref="asal")


def build_llms(pages):
    lines = [f"# {BRAND}", "",
             "> AI studio helping small and mid-sized businesses in Canada and the US put AI agents to work: "
             "training, guided agent setup, custom AI development, managed AI employees, and AI engineering "
             "capacity instead of a new hire.", "", "## Pages", ""]
    lines += [f"- [{t}]({url(s)}): {d}" for s, t, d in pages]
    lines += ["", "## Contact", "", f"- New business: {EMAIL_SALES}", f"- General: {EMAIL_GENERAL}",
              f"- Book a discovery session: {CONTACT_URL}", "",
              f"{BRAND} is a brand of {LEGAL_NAME}, an Ontario corporation.", ""]
    return "\n".join(lines)


def build_sitemap(slugs):
    rows = "".join(f"  <url>\n    <loc>{url(s)}</loc>\n    <lastmod>{TODAY}</lastmod>\n  </url>\n" for s in slugs)
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + rows + "</urlset>\n")


def main():
    global TRACKER_JS
    TRACKER_JS = (TRACKER_JS.replace("__UMAMI_HOST__", UMAMI_HOST)
                  .replace("__UMAMI_ID__", UMAMI_SITE_ID or ""))
    out = [("", build_home(), "Home", ORG["description"]),
           ("services/", build_services(), "Services", "The five ways to work with us."),
           ("discovery-sprint/", build_sprint(), "Discovery Sprint", "The paid sprint most engagements start with.")]
    out += [(t["slug"], build_tier(i), t["title"], t["description"]) for i, t in enumerate(TIERS)]
    out += [("use-cases/", build_use_cases(), "AI Agent Use Cases", "Agents for strategy, growth and finance teams.")]
    out += [(u["slug"], build_use_case(u), u["title"], u["description"]) for u in USE_CASES]
    out += [(p["slug"], build_play(p), p["title"], p["description"]) for p in PLAYS]
    out += [("about/", build_about(), "About", "Who we are and how we work."),
            (ASAL["slug"], build_asal(), f"{ASAL['name']}, {ASAL['role']}", "Business development and new clients.")]
    for slug, body, _, _ in out:
        path = ROOT / slug / "index.html"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(body)
    (ROOT / "sitemap.xml").write_text(build_sitemap([s for s, *_ in out]))
    (ROOT / "llms.txt").write_text(build_llms([(s, t, d) for s, _, t, d in out]))
    print(f"wrote {len(out)} pages, sitemap.xml, llms.txt")


if __name__ == "__main__":
    main()
