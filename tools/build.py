#!/usr/bin/env python3
"""Generate the static VisionzLab site.

Pages are plain HTML written into the repo and served by GitHub Pages as-is;
this script only removes the need to hand-copy the header, footer, analytics
and structured data across pages. Python 3 standard library only.

    python3 tools/build.py        # rewrite every page, sitemap.xml and llms.txt
"""
import datetime
import html
import html.parser
import json
import pathlib
import re
import subprocess

ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE = "https://visionzlab.com"
BRAND = "VisionzLab"
TODAY = datetime.date.today().isoformat()

# Contact and analytics endpoints. Both are personal-account hostnames for now;
# swap them here once brand-neutral replacements exist.
CONTACT_URL = "https://frankgoortani.typeform.com/to/VaoYV6iJ"
UMAMI_HOST = "https://nas.tailb423d6.ts.net"
UMAMI_SITE_ID = "571a5a54-c7bd-41d4-969d-3026dae95234"

# HubSpot booking form (VisionzLab account, form "VisionzLab - Book a discovery session"). Once HUBSPOT_FORM_ID
# is set, every "Book" button goes to the site's own /book/ page instead of CONTACT_URL; the form there creates
# the contact in HubSpot with the lead source in the hidden `vzl_ref` property. Values are from the form's embed code.
HUBSPOT_PORTAL_ID = "343785035"
HUBSPOT_REGION = "na3"
HUBSPOT_FORM_ID = "b480b50f-caa3-41e0-954c-d94193f284e3"
BOOK_SLUG = "book/"
# Frank's Google Calendar appointment schedule "AI Consultation" (60 min, Google Meet), the same booking page the
# outreach emails link to (calendar.app.google/yr17btY8j1g5b4BR8). /book/ shows it right after the HubSpot form is
# submitted, so a visitor requests and books in one visit. `?gv=true` is Google's embeddable view. "" turns it off.
BOOKING_CALENDAR_URL = ("https://calendar.google.com/calendar/appointments/schedules/"
                        "AcZssZ2_bzCYAv1rz3IjgukgLGWdTnOVV1FZv3tWqkG6UfWNOCVAJ-DWqKypeErih1wy5DE7hlsbq85K?gv=true")
# HubSpot Meetings scheduling page (Sales > Meetings in the VisionzLab portal), synced to the same Google Calendar.
# When set it replaces BOOKING_CALENDAR_URL: the booking is logged as a meeting on the HubSpot contact and still
# lands in Google Calendar. The page prefills name and email from the form just submitted.
HUBSPOT_MEETINGS_URL = "https://meetings-na3.hubspot.com/frank-goortani"

LEGAL_NAME = "VisionZone One Consulting Inc."

# Illustrations (generated in the site's isometric line-art style). Missing files fall back to computer.webp.
# An optional fourth item is a smaller copy for phones, (path, width), offered through srcset.
ART = {
    "hero": ("public/art/hero-agents.webp", 1200, 800, ("public/art/hero-agents-800.webp", 800)),
    "sprint": ("public/art/sprint.webp", 900, 900),
    "lab": ("public/art/lab.webp", 900, 900),
    "teach": ("public/art/tier-teach.webp", 900, 900),
    "setup": ("public/art/tier-setup.webp", 900, 900),
    "build": ("public/art/tier-build.webp", 900, 900),
    "employee": ("public/art/tier-employee.webp", 900, 900),
    "team": ("public/art/tier-team.webp", 900, 900),
    "security": ("public/art/security.webp", 900, 900),
}
EMAIL_GENERAL = "hello@visionzlab.com"  # alias on frank@ (Workspace, 2026-11-01): no extra mailbox
EMAIL_FRANK = "frank@visionzlab.com"
EMAIL_SALES = "asal@visionzlab.com"

# Brand search: "visionzlab" is one word that Google readily "corrects" to "vision lab". These spellings tell it
# (WebSite + Organization alternateName) that the variants all mean this site, so a brand query resolves here.
ALT_NAMES = ["Visionz Lab", "VisionZ Lab", "VisionzLab AI", "visionzlab.com"]
# Official profiles of the company itself (not of people). Add each one here once it is confirmed to be ours.
# Instagram is "visionzlabs" because @visionzlab is held by another agency; the others are "visionzlab".
# The footer lists them under Company in this order; the URLs alone become the Organization's sameAs.
SOCIAL_PROFILES = [
    ("LinkedIn", "https://www.linkedin.com/company/visionzlab-ai/"),  # confirmed ours 2026-10-31 (Asal listed, website field set)
    ("YouTube", "https://www.youtube.com/@visionzlab"),               # set up 2026-11-08
    ("Instagram", "https://www.instagram.com/visionzlabs/"),          # set up 2026-11-08, connected to the Facebook Page 11-12
    ("Facebook", "https://www.facebook.com/visionzlab"),              # Page, set up 2026-11-08
    ("TikTok", "https://www.tiktok.com/@visionzlab"),                 # set up 2026-11-09
]
SAME_AS = [url for _, url in SOCIAL_PROFILES]

# Who we serve, stated the same way everywhere. AI engines recommend vendors whose pages say who they serve and
# where (GEO study 2026-11-01). Size mirrors asal references/ICP.md: normally 75-1,000 staff, a heuristic, not a
# cutoff. Pricing is described by model only; rates are never published.
WHO_WE_SERVE = ("Businesses from owner-run firms up to about 1,000 people, usually without an in-house AI team, "
                "across Canada and the United States. We're based in Ontario and work online or on site.")

ORG_ID = f"{SITE}/#organization"
WEBSITE_ID = f"{SITE}/#website"
ORG = {
    "@type": "ProfessionalService",
    "@id": ORG_ID,
    "name": BRAND,
    "alternateName": ALT_NAMES,
    "slogan": "AI that takes work off your team's plate.",
    "url": f"{SITE}/",
    "logo": {"@type": "ImageObject", "url": f"{SITE}/public/logo.png"},
    "image": f"{SITE}/public/og.jpg",
    "knowsAbout": ["AI agents", "Business process automation", "AI training for small businesses",
                   "Document intake automation", "Order entry automation", "AI workflow design",
                   "Cybersecurity reviews for small businesses", "Vulnerability remediation",
                   "AI tool security and data access"],
    **({"sameAs": SAME_AS} if SAME_AS else {}),
    "description": "VisionzLab helps small and mid-sized businesses put AI to work — "
                   "from teaching teams to build their own agents to building and running AI employees.",
    "legalName": "VisionZone One Consulting Inc.",
    "email": EMAIL_GENERAL,
    "areaServed": ["CA", "US"],
    "founder": {"@id": f"{SITE}/team/frank-goortani/#person"},
    "address": {"@type": "PostalAddress", "addressRegion": "ON", "addressCountry": "CA"},
    "contactPoint": [
        {"@type": "ContactPoint", "contactType": "sales", "email": "asal@visionzlab.com",
         "areaServed": ["CA", "US"], "availableLanguage": ["en"]},
        {"@type": "ContactPoint", "contactType": "customer support", "email": EMAIL_GENERAL,
         "areaServed": ["CA", "US"], "availableLanguage": ["en"]},
    ],
}
WEBSITE = {"@type": "WebSite", "@id": WEBSITE_ID, "name": BRAND, "alternateName": ALT_NAMES, "url": f"{SITE}/",
           "inLanguage": "en", "publisher": {"@id": ORG_ID}}

e = html.escape

# --------------------------------------------------------------------------
# Content
# --------------------------------------------------------------------------

PRICING_SUMMARY = ("The first discovery session is free. The Discovery Sprint is a fixed fee agreed before it starts. "
                   "Builds are fixed-price for a fixed scope; managed AI employees and AI teams are monthly. "
                   "We don't publish rates: we quote a defined first step after the discovery session.")

TIERS = [
    {
        "slug": "services/ai-training/", "priced": "Quoted for the agreed sessions before work starts.", "art": "teach",
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
        "slug": "services/ai-agent-setup/", "priced": "Quoted for the agreed scope before work starts.", "art": "setup",
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
        "slug": "services/ai-development/", "priced": "A fixed price for a fixed scope, agreed before work starts.", "art": "build",
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
        "slug": "services/ai-employee/", "priced": "A setup fee plus a monthly fee, agreed before work starts.", "art": "employee",
        "tier": "Build & maintain",
        "nav": "AI Employee",
        "title": "Always-On AI Employee for Your Business",
        "description": "An always-on AI employee for one defined role, working from a company brain you own. "
                       "We build it and keep it working for a monthly fee.",
        "lead": "We organize how your company runs into a company brain you own, then put an always-on AI employee "
                "to work on one defined role and keep it working for a monthly fee.",
        "for": "Owner-led businesses that want the result without having to maintain the technology.",
        "get": [
            "A company brain: your offers, customers, suppliers, who decides what and how you do things, in one "
            "place you own, with a source and owner on each entry",
            "An always-on AI employee for one defined role, such as a daily operations brief, document intake, "
            "inbox triage, follow-ups, a first pass on quotes, or order entry",
            "Research skills written for your industry",
            "Regular maintenance: updates, fixes and improvements on a schedule",
            "A monthly report on what it did and where a person had to step in",
            "People stay in charge of anything that needs judgment or sign-off",
        ],
        "how": [
            ("Define the role", "We map the tasks, the rules, and where a person must approve."),
            ("Build the brain", "We connect your tools, write down how you work, and set who can see what."),
            ("Build and launch", "We build it, run it alongside your team, then hand it the work."),
            ("Maintain", "We look after it month to month so it keeps doing the job well."),
        ],
        "next": "services/ai-team/",
        "faq": [
            ("Does it really work around the clock?", "Yes. It keeps working when nobody is at a computer, and "
             "anything that matters waits for a person to approve it. Our own support is scheduled, within business days."),
            ("How is this different from ChatGPT or Copilot?", "Those tools only know what someone gives them. We organize "
             "what your company knows, keep it current and put it to work on a defined job."),
            ("Who owns the company brain?", "You do. It lives in accounts you control wherever possible, and it stays with "
             "you if you change AI provider or stop working with us."),
            ("Which AI does it use?", "You choose from our approved list of business plans whose terms exclude training "
             "on your data."),
            ("Is this cheaper than hiring?", "It depends on the scope, usage and human review needed. We agree a setup fee and a "
             "monthly fee so you can compare the total cost with your alternatives."),
            ("What does maintenance include?", "Scheduled care: updates, fixes within business days, and "
             "improvements. It is not a 24/7 on-call service."),
            ("Who checks its work?", "Your team approves anything sensitive. The AI employee prepares; people decide."),
        ],
    },
    {
        "slug": "services/ai-team/", "priced": "A monthly retainer sized to the work.", "art": "team",
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
            "Agreed scope, onboarding and monthly capacity without adding permanent headcount",
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
            ("Can we start small?", "Yes. We recommend starting with one defined project and reviewing the results before expanding."),
            ("Where is the team?", "Based in Ontario, Canada. We work with businesses across Canada and the US."),
        ],
    },
]

# Security Review (added 2026-11-03). A separate service, not a sixth rung on the AI ladder: it sells to the same
# businesses for a different reason. Research and claim limits: asal repo
# foundation/visionzlab/SECURITY_REVIEW_OFFER_2026-11-03.md. Claim rules: never "penetration test", never "certified",
# never a guarantee, never an insurer's decision; nothing runs on a client system without written authorisation.
SECURITY = {
    "slug": "services/security-review/", "art": "security",
    "alt": "Isometric illustration of a magnifying glass checking a laptop beside a server, "
           "with padlock and email icons",
    "tier": "Security",
    "nav": "Security Review",
    "title": "AI-Assisted Security Review for Small Businesses",
    "description": "A fixed-scope security review for small businesses: AI-assisted scans and settings checks, "
                   "a plain-English fix list, and help closing the gaps that matter.",
    "lead": "We find the gaps attackers try first, explain them in plain English and help you close them, with a "
            "senior engineer checking every finding.",
    "for": "Businesses without a security team, especially those facing a cyber insurance application, a customer "
           "security questionnaire or a supplier certification.",
    "question": ("How can a small business check its security now that AI is finding software flaws faster?",
                 "Start with the gaps attackers try first: internet-facing systems that are behind on patches, "
                 "email accounts without multi-factor sign-in, admin accounts, untested backups and files shared "
                 "too widely. A security review checks those against a recognised baseline and gives you a short, "
                 "ordered fix list."),
    "checks": [
        ("Internet-facing systems", "Firewalls, VPN and remote access, websites and exposed services, checked for "
         "known exploited flaws and out-of-date software."),
        ("Email and sign-in", "Multi-factor sign-in, admin accounts, password reuse risk, and the SPF, DKIM and "
         "DMARC records that stop others sending email as you."),
        ("Microsoft 365 or Google Workspace", "Your settings compared with published secure baselines, read-only."),
        ("Devices, patches and backups", "Patch status from the tools you already use, and whether backups are "
         "kept apart from your network and have actually been restored."),
        ("AI tools and agents", "Which AI tools your team uses, what data goes into them, and what files and "
         "inboxes an AI assistant or agent can reach."),
    ],
    "get": [
        "A review of your internet-facing systems, email and cloud settings, under a written authorisation you sign",
        "A check of the AI tools your team already uses: what data goes into them and who can see what",
        "A plain-English fix list in priority order, mapped to recognised baselines for small organisations",
        "Help patching and hardening the top items, alongside your IT person or provider",
        "Dated records of what was checked and fixed, for your insurer or a customer questionnaire",
    ],
    "how": [
        ("Agree scope in writing", "We agree which systems we may check and how. Nothing runs until you've signed "
         "a written authorisation."),
        ("Review", "AI tools scan and compare your settings with security baselines. A senior engineer checks every "
         "finding and removes the false alarms."),
        ("Fix", "We work through the top items with your team or IT provider and record each change."),
        ("Keep watch", "Optional: a monthly check for new flaws in the software you run, with a short report."),
    ],
    "priced": "A fixed fee for the review, agreed before work starts. Fixes are quoted from the findings; "
              "monthly monitoring is optional.",
    "faq": [
        ("Why does AI change our security risk?", "AI makes it faster and cheaper to find and exploit known software "
         "flaws, and to write convincing phishing emails. Most small-business breaches still start with the basics: "
         "an unpatched system, a reused password, an email account without multi-factor sign-in. We check those "
         "first."),
        ("Is this a penetration test?", "No. It's a review of the ways small businesses most often get breached. If "
         "your insurer, a customer or a certification asks for a formal penetration test, we'll say so and help "
         "you scope one."),
        ("Do you need access to our systems?", "Read-only access for the review, under a written authorisation that "
         "names what we may check. We don't keep copies of your business data, and every change is made with your "
         "team and recorded."),
        ("Can this help with our cyber insurance application?", "Yes. The fix list covers the controls insurers "
         "usually ask about, such as multi-factor sign-in, endpoint protection and tested backups, and you keep "
         "dated records of each. The insurer's decision is still theirs."),
        ("Is it safe to connect AI assistants to our email and files?", "It can be, once permissions are right. An "
         "AI assistant sees whatever the signed-in person can see, so files shared too widely become easy to "
         "find. We check sharing and permissions before you switch it on."),
        ("Will this make us unhackable?", "No one can honestly promise that. The review closes the gaps attackers "
         "try first and gives you a plan for the rest."),
    ],
    "ref": "security",
}

PLAYS = [
    {
        "slug": "for/distributors-manufacturers/",
        "question": ('How are distributors and manufacturers using AI agents for quotes and orders?',
                     'Mostly for the reading and re-keying. Agents read emailed RFQs and purchase orders, match items to the catalogue, draft the quote or enter the order in the ERP, and flag anything unusual. Inside sales and customer service approve each one before it goes out.'), "art": "build",
        "nav": "Distributors & Manufacturers",
        "title": "AI Quote & Order Automation for Distributors",
        "description": "AI agents that read incoming RFQs, purchase orders and supplier documents, draft quotes "
                       "and enter orders for your team to approve — built around your ERP.",
        "lead": "AI agents that turn emailed RFQs and purchase orders into draft quotes and entered orders, "
                "for your team to approve.",
        "body": [
            "Requests arrive as emails, PDFs and spreadsheets. Someone reads each one, looks up part numbers and "
            "pricing, re-keys it into the ERP, and chases what's missing. When volume spikes, quotes go out late "
            "and orders wait.",
            "We build agents that do the reading and the re-keying: they match items to your catalogue, draft the "
            "quote or the order, and flag anything unusual. Your inside sales and customer service teams approve "
            "every quote and every order before it goes anywhere.",
            "Most engagements start with a discovery sprint on one workflow, usually quotes or order entry, using "
            "your real documents.",
        ],
        "tiers": [1, 2, 3],
        "uses": ["use-cases/quote-rfq-intake/", "use-cases/order-entry/", "use-cases/document-intake/"],
        "faq": [("A customer sent us a cyber security questionnaire. Can you help?", "Yes. Our Security Review "
                 "checks the controls these questionnaires and supplier certifications usually ask about, such as "
                 "multi-factor sign-in, patching and backups, fixes the gaps with your team, and leaves you dated "
                 "records to answer from.")],
        "ref": "play-industrial",
    },
    {
        "slug": "for/machine-shops/",
        "question": ("How can a machine shop use AI to quote jobs faster from drawings and 3D models?",
                     "An AI quoting assistant reads the RFQ email, drawings, sketches and STEP files, lists what the "
                     "buyer left out, and drafts a cost from the shop's own rates, machines and past jobs. The "
                     "estimator checks it, sets the price and sends the quote."),
        "art": "lab",
        "nav": "Machine Shops & Fabricators",
        "title": "AI Quoting for Machine Shops and Fabricators",
        "description": "AI that reads RFQs, drawings, sketches and 3D models, asks the buyer what's missing and "
                       "drafts the quote for your estimator to approve.",
        "lead": "An AI first pass on every RFQ: it reads the drawings and models, lists the missing details and "
                "drafts the quote, and your estimator approves it.",
        "body": [
            "In most job shops, one or two busy people quote everything. Each RFQ arrives as an email with a "
            "PDF print, a STEP file, or sometimes a phone photo of a sketch. Someone works out the material, "
            "stock size, setups and outside processes, writes back for the missing tolerance or quantity, and "
            "prices it. Most of those quotes don't win, and buyers compare every reply with an instant-quote "
            "website.",
            "We build quoting assistants that do the first pass. They read the request and its files, measure "
            "the model, list the questions the buyer still needs to answer, and draft a cost from your own rates, "
            "machines and past jobs. Your estimator reviews it, sets the price and the date, and sends it.",
            "If an off-the-shelf quoting tool already fits your parts, we'll tell you, and help you set it up. "
            "Most engagements start with a discovery sprint on twenty of your recent, non-controlled RFQs, "
            "measured against what you actually quoted.",
        ],
        "guide": "guides/ai-quoting-for-machine-shops/",
        "tiers": [1, 2, 3],
        "uses": ["use-cases/quote-rfq-intake/", "use-cases/document-intake/", "use-cases/inbox-triage/"],
        "faq": [
            ("We already use a quoting tool. Do we need you?",
             "Maybe not. If your tool handles your parts and your team trusts its numbers, keep it. We help where "
             "requests are messy (sketches, PDFs with no model), where you want the draft calibrated on your own "
             "past jobs, or where quoting has to fit your inbox, your ERP and your quote template."),
            ("Can we keep customer drawings in Canada?",
             "Yes. We can host in Canada, delete files on a schedule you set, and keep your drawings out of model "
             "training. Drawings under the Controlled Goods Program or ITAR stay out of the system entirely."),
            ("Does it set our prices?",
             "No. It drafts a cost from the rates and rules you give it and shows its working. Your estimator "
             "sets the price, the delivery date and whether to quote at all."),
        ],
        "ref": "play-machine-shops",
    },
    {
        "slug": "for/insurance-brokers/",
        "question": ('How can an insurance brokerage use AI agents without losing the personal touch?',
                     'Give the agents the paperwork, not the relationships: reading submissions and certificates, tracking renewal dates, preparing follow-ups and sorting the inbox. Brokers review and send every client message.'), "art": "employee",
        "nav": "Insurance Brokers",
        "title": "AI Automation for P&C Insurance Brokers",
        "description": "AI agents for commercial and property & casualty brokerages and MGAs: submission intake, "
                       "certificates, renewals and claims intake, with brokers in control.",
        "lead": "AI agents that take submission, certificate and renewal paperwork off your brokers' desks.",
        "body": [
            "A commercial submission means pulling details out of emails, applications and loss runs and re-keying "
            "them for every market. Certificate requests and renewal prep repeat the same work all year.",
            "We build agents that extract and organise that information, prepare market-ready submission packages "
            "and renewal files, draft certificates for review, and sort incoming claims notices so the right person "
            "sees them first.",
            "Your licensed brokers stay in charge of advice, placement and every coverage decision. Agents prepare "
            "the paperwork; they never bind coverage or give advice. We work with commercial and P&C lines.",
        ],
        "faq": [("Can you help clients who struggle with cyber insurance applications?", "We work with the "
                 "business directly: our Security Review checks the controls insurers usually ask about and helps "
                 "close the gaps, with dated records of what changed. The application and the coverage advice "
                 "stay with the broker.")],
        "tiers": [1, 2, 3],
        "uses": ["use-cases/document-intake/", "use-cases/renewals-follow-up/", "use-cases/inbox-triage/"],
        "ref": "play-insurance",
    },
    {
        "slug": "for/accountants-bookkeepers/",
        "question": ('What can AI automate for a small accounting or bookkeeping firm?',
                     'The routine, rules-based work: reading receipts, invoices and statements, entering and matching the data, preparing monthly reports with draft commentary, and sorting client email. Your accountants review the output and keep the client relationships.'), "art": "employee",
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
        "uses": ["use-cases/document-intake/", "use-cases/financial-reporting/", "use-cases/inbox-triage/"],
        "faq": [("Can you check our firm's security too?", "Yes. Accounting firms hold exactly the data attackers "
                 "want. Our Security Review checks email and sign-in, cloud settings, client portals and backups, "
                 "and gives you a plain-English fix list. In the US it also helps you prepare the written "
                 "information security plan tax preparers are expected to keep.")],
        "ref": "play-c",
    },
    {
        "slug": "for/small-business/",
        "question": ('Where should a small business start with AI?',
                     'With one repetitive workflow that takes hours every week, such as answering the same emails or re-keying documents. Try it with tools you already pay for, keep a person approving the output, and measure the hours saved before doing more.'), "art": "teach",
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
        "slug": "for/mortgage-brokers/",
        "question": ('How can mortgage brokers use AI to track renewals and document requests?',
                     'An agent tracks renewal and maturity dates, organises document requests and prepares follow-ups for your team to review, so clients hear from you at the right time and nothing is sent without your approval.'), "art": "setup",
        "nav": "Mortgage Brokers",
        "title": "AI Automation for Mortgage Brokers and Agents",
        "description": "AI tools for mortgage brokerages and agents: renewal tracking and outreach, document "
                       "collection, lead follow-up and AI search visibility, in several languages.",
        "lead": "Track renewals, organise document requests and prepare follow-ups for your team to review.",
        "body": [
            "Renewals are the business you already earned, and they are easy to lose when maturity dates live in "
            "a spreadsheet. Document collection and lead follow-up take the rest of the week.",
            "We set up tools that track the maturity dates in your records and prompt timely outreach, send clients a clear "
            "checklist of what to gather, follow up with new enquiries, and help your website show up when "
            "people ask AI assistants for a broker. Client messages can be prepared in the languages your clients speak.",
            "You stay in charge of every recommendation and every application. The tools organise and remind; "
            "they don't quote rates or give mortgage advice.",
        ],
        "tiers": [0, 1, 3],
        "uses": ["use-cases/renewals-follow-up/", "use-cases/document-intake/", "use-cases/inbox-triage/"],
        "ref": "play-mortgage",
    },
    {
        "slug": "instead-of-hiring/",
        "question": ('Should we hire an operations assistant or set up an AI agent instead?',
                     'Split the role first. Reading, re-keying and chasing are often agent work; relationships, judgement and exceptions need a person. If most of the hours sit in the first group, test an agent with a person approving its work before you hire.'), "art": "team",
        "nav": "Before You Hire",
        "title": "Hiring for Order Entry, AR or an Engineer? Try This",
        "description": "Hiring for order entry, AR, data entry or an engineer? See which parts of the role an AI "
                       "agent can take on, and which really need a person, before you hire.",
        "lead": "Before you fill an operations or engineering role, find out which parts AI can take on, and "
                "which really need a person.",
        "body": [
            "Hiring takes months, and every new role starts with ramp-up. Before you post the job, or while you "
            "interview, it's worth knowing which parts of it need a person.",
            "Send us the job description. We'll tell you plainly which parts we can take on, how long it would "
            "take, and what it would cost — and which parts really do need a permanent hire.",
        ],
        "moments": [
            ("You've posted an order-entry, AR or data-entry role", [
                "Much of the job is the same steps every day: reading purchase orders, invoices and remittances, "
                "keying them into the ERP or accounting system, matching payments and chasing what's missing. "
                "Underwriting-assistant and inside-sales roles have their own version: submissions to assemble, "
                "quotes to prepare, follow-ups to send.",
                "An AI agent can take that repetitive part. It reads the documents, enters the data and flags "
                "anything unusual. Your team, or the person you hire, checks its work and spends the day on "
                "customers, exceptions and the calls that need a person.",
            ]),
            ("You're hiring a software or AI engineer", [
                "Much of what a new software or AI hire is asked to build — integrations, internal tools, "
                "automations, AI agents — we can deliver as a defined project or as ongoing capacity, without "
                "the hiring cycle or the ramp-up.",
            ]),
        ],
        "tiers": [2, 3, 4],
        "uses": ["use-cases/order-entry/", "use-cases/document-intake/", "use-cases/quote-rfq-intake/"],
        "ref": "play-b",
    },
]

USE_CASES = [
    {
        "slug": "use-cases/quote-rfq-intake/",
        "question": ('Can AI read RFQs and supplier quotes and draft the quote for our sales team?',
                     'Yes. An intake agent reads requests from email, PDFs and spreadsheets, matches the items to your catalogue, applies your pricing rules and drafts the quote. A salesperson reviews and sends it.'),
        "nav": "Quote & RFQ Intake",
        "title": "AI Quote and RFQ Intake Agent",
        "description": "An AI agent that reads incoming requests for quote, matches items to your catalogue and "
                       "pricing, and drafts the quote for your team to approve.",
        "lead": "An AI agent that reads incoming RFQs, matches items to your catalogue and drafts quotes for your team to review.",
        "for": "Distributors, manufacturers and brokers whose inside sales team re-keys requests from email, PDF and spreadsheets.",
        "does": [
            "Reads requests from email, PDFs, spreadsheets and web forms",
            "Matches items to your catalogue, including customer part numbers and substitutes",
            "Applies your pricing rules and flags anything outside them",
            "Drafts the quote in your system and lists what is missing or unclear",
        ],
        "people": "Your team checks and approves every quote before it is sent. The agent prepares; it never "
                  "commits to a price or a delivery date on its own.",
        "tiers": [2, 3],
        "faq": [
            ("Does it work with our ERP?", "Yes, where the ERP has an API, an import or a usable screen workflow. "
             "We confirm this in the discovery session."),
            ("What about unusual requests?", "It flags them for a person instead of guessing. You set the limits."),
            ("How do we know it's working?", "We measure quote turnaround and accuracy on your real requests "
             "during the discovery sprint, before you commit to a build."),
        ],
    },
    {
        "slug": "use-cases/order-entry/",
        "question": ('How can a distributor stop retyping customer orders from email into the ERP?',
                     "An order-entry agent reads each emailed or PDF purchase order, enters it in the ERP as a draft, checks it against the quote, price list and stock, and sends anything that doesn't match to a person. Your team approves instead of re-keying."),
        "nav": "Order Entry & Exceptions",
        "title": "AI Order Entry and Exceptions Agent",
        "description": "An AI agent that turns emailed and PDF purchase orders into entered orders, checks them "
                       "against price, stock and terms, and flags exceptions for your team.",
        "lead": "An AI agent that enters purchase orders from email and PDF, and flags the ones that need a person.",
        "for": "Customer service and order desk teams who re-key purchase orders and chase mismatches every day.",
        "does": [
            "Reads purchase orders from email, PDF and customer portals",
            "Enters them into your ERP or order system",
            "Checks price, quantity, stock and terms against what was quoted",
            "Routes exceptions to the right person with the reason attached",
        ],
        "people": "Your team handles every exception and approves anything outside the rules. Clean orders can be "
                  "held for approval or released automatically — your choice.",
        "tiers": [2, 3],
        "faq": [
            ("Can it release orders automatically?", "Only if you want it to, and only within limits you set. "
             "Many teams start with every order held for a quick approval."),
            ("What counts as an exception?", "Whatever you decide: price differences, unknown items, credit holds, "
             "short stock or unusual terms."),
            ("Who maintains it?", "Your team, after hand-over, or us on a scheduled maintenance plan."),
        ],
    },
    {
        "slug": "use-cases/document-intake/",
        "question": ('Can AI pull data out of invoices, forms and PDFs and enter it into our system?',
                     'Yes. A document-intake agent reads PDFs, scans, emails and spreadsheets, extracts the fields your system needs, checks them against rules you set and writes them in. Anything missing or mismatched goes to a person to resolve.'),
        "nav": "Document Intake",
        "title": "AI Document Intake and Data Extraction Agent",
        "description": "An AI agent that reads invoices, applications, shipping documents and forms, extracts the "
                       "data your systems need, and checks it before anyone re-keys it.",
        "lead": "An AI agent that reads the documents your team re-keys, and puts the data where it belongs.",
        "for": "Any team that copies information out of invoices, applications, forms or shipping documents by hand.",
        "does": [
            "Reads PDFs, scans, emails and spreadsheets",
            "Extracts the fields your systems need and checks them against rules you set",
            "Files the document and writes the data to your system",
            "Lists what is missing or doesn't match, for a person to resolve",
        ],
        "people": "Your team reviews anything the agent isn't sure about, and owns every decision made on the data.",
        "tiers": [1, 2, 3],
        "faq": [
            ("Which documents can it handle?", "Most business documents with a recognisable structure: invoices, "
             "purchase orders, applications, bills of lading, statements and forms."),
            ("What if a scan is poor?", "It flags low-confidence fields for a person instead of guessing."),
            ("Where does our data go?", "It runs on accounts and storage you control, under clear privacy and "
             "security terms in every engagement."),
        ],
    },
    {
        "slug": "use-cases/inbox-triage/",
        "question": ('Can AI sort a shared inbox and draft replies for my team?',
                     "Yes. An inbox agent reads incoming messages, sorts them by type and urgency, routes each one to the right person and drafts a reply from your templates and past answers. Urgent messages are flagged straight away, and your team reviews replies before they're sent."),
        "nav": "Inbox Triage",
        "title": "AI Shared Inbox Triage and Reply Drafting Agent",
        "description": "An AI agent that sorts a shared inbox, routes each message to the right person and drafts "
                       "replies for review, with routing rules agreed with your team.",
        "lead": "An AI agent that sorts incoming messages, routes them using agreed rules and drafts replies for review.",
        "for": "Teams working out of a shared inbox — sales, service, orders, claims or admin — where messages wait or get missed.",
        "does": [
            "Reads messages and supported attachments from the inboxes you connect",
            "Sorts by type and urgency, and routes to the right person or queue",
            "Drafts replies from your templates, policies and past answers",
            "Flags anything urgent or unusual straight away",
        ],
        "people": "Your team reads and sends every reply, or approves which simple ones can go automatically.",
        "tiers": [0, 1, 3],
        "faq": [
            ("Does it send replies on its own?", "Not unless you decide it should, for message types you choose."),
            ("Which email systems?", "Google Workspace and Microsoft 365, plus most help-desk tools."),
            ("Can we set it up ourselves?", "Often, yes. We can teach your team or set it up with you."),
        ],
    },
    {
        "slug": "use-cases/renewals-follow-up/",
        "question": ('How can AI help us stay on top of renewals and client follow-ups?',
                     'A renewals agent tracks renewal and maturity dates in your client records, prepares outreach at the right time with what the client needs to gather, and reminds your team when a lead goes quiet. Your team approves every message.'),
        "nav": "Renewals & Follow-up",
        "title": "AI Renewal Tracking and Client Follow-up Agent",
        "description": "An AI agent that tracks renewal and maturity dates, prepares timely outreach and follows "
                       "up with leads and clients, so no renewal or enquiry slips.",
        "lead": "An AI agent that tracks renewal dates in your records and prepares follow-ups for your team to approve.",
        "for": "Brokers, agents and service firms whose revenue depends on renewals and fast follow-up.",
        "does": [
            "Tracks renewal and maturity dates from your client records",
            "Prepares outreach at the right time, with what the client needs to gather",
            "Follows up with new enquiries and reminds your team when a lead goes quiet",
            "Prepares messages in the languages your clients speak",
        ],
        "people": "You decide who is contacted and what is said. The agent reminds and drafts; advice and "
                  "recommendations stay with you.",
        "tiers": [1, 3],
        "faq": [
            ("Does it contact clients directly?", "Only with messages you approve, through channels you choose, "
             "and in line with the consent rules that apply to you."),
            ("Does it work with our CRM?", "Yes, or with a spreadsheet if that's where your client list lives."),
            ("What does it cost to run?", "A setup fee, then a monthly fee if we maintain it. We agree both before we start."),
        ],
    },
    {
        "slug": "use-cases/market-intelligence/",
        "question": ('Can an AI agent monitor our competitors and send us a weekly market brief?',
                     'Yes. It tracks competitor websites, pricing pages, releases, job postings and news, plus the publications you point it at, and delivers a weekly brief on what changed and why it may matter, with a source linked for every point.'),
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
        "question": ('Can AI research target accounts and prepare account plans for our sales team?',
                     'Yes. A research agent profiles each target account from public sources, finds recent events worth a conversation, maps the roles that matter and drafts an account plan with first-call questions for your team to edit.'),
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
        "question": ('Can AI help us set OKRs and track progress without buying new software?',
                     'Yes. An assistant helps turn goals into objectives, key results and owners, collects progress from the tools your team already uses, flags what is behind or blocked before the review, and drafts the monthly update for leadership.'),
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
        "question": ('Can AI prepare our monthly management reports and variance commentary?',
                     'Yes. A reporting agent pulls figures from your accounting and business systems, prepares the monthly reports and drafts the variance commentary: what moved, by how much and the likely drivers. Your finance team reviews and signs off.'),
        "nav": "Financial Reporting",
        "title": "AI Financial Reporting Agent",
        "description": "An AI agent that pulls numbers from your accounting and business systems, prepares "
                       "monthly reports and drafts variance commentary for review.",
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
    ("What does an AI discovery sprint include, and what should it deliver?",
     "One workflow, tested on your own documents over two to four weeks. It should deliver a working prototype, "
     "a success measure checked on real examples, a costed build plan including what your team needs to run it, "
     "and a go/no-go recommendation with the reasons."),
    ("What does the sprint cost?", "It's a fixed fee agreed before we start, based on the size of the workflow."),
    ("What if the answer is no-go?", "Then you've spent a few weeks, not a budget, finding out — and you keep the findings."),
    ("Is there a free option?", "Yes. The first conversation is a free discovery session, with a short memo afterwards."),
]

# The 4S check. Mirrors foundation/VISIONZLAB_4S_MATURITY_2026-10-14.md in the asal repo: change a stage or a
# question there and here in the same week. Each stage has two yes/no checks; the first "no" is the stage.
MATURITY_SLUG = "ai-maturity/"
STAGES = [
    {
        "code": "S1", "name": "Strategy", "question": "Why AI, and where first?",
        "here": "People use AI tools on their own, but nobody has picked one piece of work for AI to take on, "
                "or nobody owns it. There's no number for what better would look like.",
        "next": "Choose one workflow, one owner and one number. A free discovery session does that with you; "
                "a discovery sprint then tests it on your own documents.",
        "link": "discovery-sprint/",
        "checks": ["There's one piece of work we'd most like AI to take on, and one person who owns it.",
                   "We know how we'd measure success: hours saved, fewer errors or faster turnaround."],
    },
    {
        "code": "S2", "name": "Solution", "question": "Does it work on our work?",
        "here": "You've chosen the work and maybe tried a tool, a trial or an automation. It hasn't been tested on "
                "your real documents, or nobody compared the result with how the work is done today.",
        "next": "Test it on your real work and measure it against today. That's what the discovery sprint is for: "
                "a working prototype, measured results and a clear go/no-go.",
        "link": "discovery-sprint/",
        "checks": ["We've tried an AI tool or automation on that work, using our real documents, not a demo.",
                   "We've compared the result with how the work is done today."],
    },
    {
        "code": "S3", "name": "Scale", "question": "Is it part of the day?",
        "here": "It works and you've measured it, but it's still a side experiment: one keen person uses it, or "
                "someone copies the results into your systems by hand.",
        "next": "Connect it to the system where the work ends up, and roll it out to the people who do the work.",
        "link": "services/ai-development/",
        "checks": ["The people who do that work use it as part of their normal week.",
                   "The result goes straight into the system where the work ends up, without anyone copying it across."],
    },
    {
        "code": "S4", "name": "Sustain", "question": "Will it keep working?",
        "here": "It's in daily use and connected. What's missing is an owner: someone who fixes and updates it when "
                "things change, checks what it produces, and keeps clear rules on what it may do alone.",
        "next": "Give it an owner and a schedule: regular checks, fixes and updates, with people approving what matters.",
        "link": "services/ai-employee/",
        "checks": ["Someone is responsible for fixing it, updating it and checking what it produces.",
                   "It's written down what it may do on its own, what needs a person's approval, and what "
                   "information it may use."],
    },
]
PAST_S4 = {
    "code": "done", "name": "Past stage four",
    "here": "That workflow is in good shape: chosen, measured, part of the day, and looked after.",
    "next": "The useful question now is which workflow comes next (it starts again at Strategy), or whether you "
            "need more building capacity than your team has.",
    "link": "services/ai-team/",
}
FAQ_MATURITY = [
    ("Is this an AI maturity assessment?", "It's a quick self-check, not an audit. Eight yes-or-no questions place "
     "one piece of work at one of four stages, so you know which step comes next."),
    ("Why one workflow and not the whole company?", "Because businesses are rarely at one stage everywhere. You can "
     "run invoicing smoothly with AI and still be deciding where to start on everything else. Start with the work "
     "that matters most."),
    ("What happens to my answers?", "We don't store them. Our analytics counts which stage people land on, without "
     "anything that identifies you. If you book a session, we'll go through the same questions together."),
    ("What if we're past stage four?", "Then that workflow is in good shape, and we'll say so. The useful question "
     "becomes which workflow is next."),
]

# Team pages. Positioning rule: these are the only pages that name a person. Never call Frank "CTO" here and
# never name his employer; the public record ends VisionzLab in 2023, so the copy stays timeless.
FRANK = {
    "slug": "team/frank-goortani/",
    "name": "Frank Goortani",
    "first": "Frank",
    "role": "Founder & Technical Principal",
    "email": EMAIL_FRANK,
    "photo": "frank",
    "description": "Frank Goortani founded VisionzLab and leads the technical side of every engagement. "
                   "Two decades as an architect at Uber, TD Bank and Canada Life.",
    "bio": ["Frank founded VisionzLab and leads the technical side of every engagement: what gets built, how "
            "it's built, and the agents themselves.",
            "He has spent more than twenty years designing and building software for startups and large "
            "enterprises, as a solution architect and technical lead at organisations including Uber, TD Bank, "
            "Canada Life and CAA. At Uber he led an award-winning AI initiative; at Canada Life he formed and "
            "scaled an in-house mobile team. He is TOGAF and PMP certified.",
            "Much of his work has been for security and privacy teams: data-request automation, enterprise "
            "sign-in built to OpenID and OAuth 2.0 guidelines, and handling of sensitive data to PCI standards. "
            "He leads VisionzLab's Security Review.",
            "On every project he makes sure the agents are safe to run: approval steps, audit trails and clear "
            "limits on what they may do."],
}
ASAL = {
    "slug": "team/asal-matin/",
    "name": "Asal Matin",
    "first": "Asal",
    "role": "VP Business Development",
    "email": EMAIL_SALES,
    "photo": "asal",
    "description": "Asal Matin is VP Business Development at VisionzLab, the first point of contact for new clients.",
    "bio": ["Asal leads business development at VisionzLab. She is the first person most clients speak to, and "
            "stays their point of contact from the first conversation through delivery and beyond.",
            "She works with owners and leadership teams to find where AI can take real work off their people — "
            "and is just as quick to say when it can't. Her job is to make sure every engagement starts at the "
            "right size, with a clear outcome both sides can measure."],
}
TEAM = [FRANK, ASAL]

# Experience page (tracker 3.3). VisionzLab has no client work of its own yet, so every card is the team's
# background from roles held before VisionzLab, at the level of Frank's public record on goortani.com. The
# positioning rule still applies: no employer or client is named here (they're on the homepage ribbon and the
# team page), no internal system names, no metrics beyond the public record, nothing in legal or clinics.
EXPERIENCE_SLUG = "experience/"
EXPERIENCE = [
    {
        "tag": "AI decision engine · Global technology platform",
        "title": "An AI decision engine for privacy reviews",
        "work": "Privacy reviews across a global technology platform.",
        "built": "An AI decision engine that automates privacy reviews. Our founder created it and led the "
                 "cross-functional engineering team that built it.",
        "outcome": "Adopted company-wide, and recognised with several internal awards, including the company's "
                   "Engineering Excellence Award in 2024.",
    },
    {
        "tag": "Security and privacy engineering · Technology, insurance, finance",
        "title": "Security and privacy built into production systems",
        "work": "Security and privacy teams at a global technology platform, a major Canadian insurer, and the "
                "finance systems of a large Canadian membership organisation.",
        "built": "Our founder led the development of data-request (DSAR) automation for the platform's security and "
                 "privacy teams, built enterprise sign-in to OpenID and OAuth 2.0 security guidelines at the "
                 "insurer, and designed a tokenised portal for sensitive information to PCI standards.",
        "outcome": "Security and privacy treated as part of the build, not an afterthought. It's the background "
                   "behind our Security Review.",
    },
    {
        "tag": "AI automation · Four industries",
        "title": "AI automation for growing businesses",
        "work": "Startups and established businesses in manufacturing, accounting, e-commerce and hospitality, "
                "each with its own AI automation project.",
        "built": "As a generative AI lead, our founder worked on the architecture of those projects.",
        "outcome": "AI automation delivered for clients in all four industries: the same kind of work our "
                   "services are built around.",
    },
    {
        "tag": "Teams and delivery · Insurance and retail",
        "title": "Engineering teams that ship",
        "work": "A major Canadian insurer building its own mobile capability, and a national retailer's "
                "e-commerce website with a large, distributed development team.",
        "built": "At the insurer, our founder established and led an in-house mobile development and architecture "
                 "team, from technical interviews to coaching and DevOps automation. At the retailer, he steered "
                 "more than sixty onshore and offshore developers.",
        "outcome": "A shared component library that streamlined front-end development across the insurer's teams.",
    },
    {
        "tag": "Teaching · Colleges and corporate programs",
        "title": "Teaching technical teams",
        "work": "Organisations moving to the cloud, and students learning to build software.",
        "built": "Hands-on cloud migration courses for organisations, data warehousing courses, and college "
                 "courses in software, mobile, web and business intelligence, often with the curriculum written "
                 "from scratch.",
        "outcome": "Courses delivered online and in person across North America. It's why our AI Training is "
                   "hands-on and built around your own work.",
    },
]
TRUST = [
    ("People approve what matters", "Approval steps, audit trails and clear limits on what an agent may do are "
     "part of every build. The agent prepares; people decide."),
    ("Proof on your own work first", "The Discovery Sprint takes one workflow and two to four weeks, and ends with "
     "a working prototype, a costed build plan and a clear go/no-go — before you commit to anything bigger."),
    ("Built on your accounts", "What we build runs on your accounts and tools, with the permissions you set. "
     "You own it."),
    ("We use it ourselves", "We run AI assistants in our own day-to-day work, and a person approves everything "
     "that goes out."),
]
FAQ_EXPERIENCE = [
    ("Is this VisionzLab's client work?", "No. It's our team's background, from roles held before VisionzLab. "
     "VisionzLab's own case studies will be added here as engagements complete."),
    ("Do you have client references?", "Not yet, and we'd rather say so than borrow someone else's. The Discovery "
     "Sprint is how you test us: a working prototype on your own work, and a clear go/no-go, before a bigger "
     "commitment."),
    ("Who would build our project?", "Every build is led by our founder, and every engagement starts with our "
     "business development lead, who stays your point of contact."),
]

# Retired URLs. GitHub Pages has no server redirects, so each old path gets a noindex page that points search
# engines at the new canonical and forwards visitors. Kept out of the sitemap and llms.txt.
REDIRECTS = {"team/asal-matinsadeghy/": ASAL["slug"]}

# --------------------------------------------------------------------------
# Resources: guides, free tools, privacy (added 2026-10-31)
# --------------------------------------------------------------------------

GUIDES_SLUG = "guides/"
TOOLS_SLUG = "free-tools/"
CALC_SLUG = "free-tools/hours-back-calculator/"
PRIVACY_SLUG = "privacy/"

# Security and privacy in the AI systems we build (added 2026-11-04). Source text, kept in step with this:
# foundation/visionzlab/SECURITY_AND_PRIVACY.md in the VisionzLab business repo. Wording rules: frameworks are
# "practices we follow", never certifications we hold; data is "never public", not "never touches the internet".
DATA_TRUST_SLUG = "security-and-privacy/"
DATA_TRUST = {
    "title": "How We Protect Your Data in AI Systems",
    "h1": "How we protect your data",
    "description": ("Approved AI models only, your data never used for training, nothing public, a person approves "
                    "every step. How VisionzLab keeps client data safe."),
    "lead": ("When you let an AI system work on your documents, the first question is the right one: where does my "
             "data go, and who can see it? Here is our answer for every system we build."),
    "sections": [
        ("Only approved AI models",
         "We use AI models from an approved list, never whatever tool is handy. A model is approved only if it "
         "meets all of these:",
         [("Business-grade terms", "We use the enterprise or API service, not the consumer app. Under those terms "
           "the provider does not use your data to train its models."),
          ("Known retention", "We know how long the provider keeps a request, if at all, and we pick the shortest "
           "setting available."),
          ("Independent audits at the provider", "The provider's own infrastructure is independently audited, for "
           "example with SOC 2 Type II or ISO 27001 reports, and we can share those reports with you."),
          ("A choice of region", "Where you need it, data is processed in a region you choose, such as Canada or "
           "the US."),
          ("You approve the models", "You approve which models touch your data before we start. To keep everything "
           "inside your own environment, we can run an open-weight model privately in your cloud account or on "
           "your own server. Free and consumer AI tools are never used with client data.")]),
        ("Your data is never used for training",
         "Your documents are used for one thing: doing your work.",
         [("No training", "They are not used to train or improve any AI model, ours or a provider's."),
          ("No shared datasets", "We don't build datasets from client material, and nothing from one client is "
           "ever used for another.")]),
        ("Your data stays private", None,
         [("Never public", "Client data is never published, shared, or reachable from the open internet. It isn't "
           "pasted into public chat tools or kept on personal devices."),
          ("Encrypted in transit and at rest", "Data moves only over encrypted connections between your systems "
           "and the approved model service, and it is encrypted wherever it's stored."),
          ("Your accounts where possible", "We prefer to build inside accounts you own and control: your Microsoft "
           "365, Google Workspace or cloud tenant. You keep the keys and can switch our access off at any time."),
          ("Least access", "The system and our team get only the access the work needs, read-only wherever that's "
           "enough, and access is removed when the work ends."),
          ("Kept only as long as needed", "Working copies are deleted or returned when the engagement ends, as "
           "agreed with you in writing.")]),
        ("People stay in charge", None,
         [("A person approves every action that matters", "Nothing is filed, sent, deleted or changed without "
           "someone saying yes."),
          ("When unsure, it asks", "Anything the system isn't confident about is set aside for a person. It is "
           "never guessed."),
          ("Every step is logged", "What came in, what the system proposed, who approved or changed it, and when. "
           "You can review it at any time."),
          ("Stop at any time", "Every system can be paused or switched off, and your work carries on the way it "
           "did before.")]),
        ("Guardrails built in", None,
         [("Defined boundaries", "Each system can reach only the folders, mailboxes and tools named in its scope."),
          ("Protection against manipulation", "Text inside a document is treated as content, never as an "
           "instruction, so a document can't tell the system to do something it shouldn't."),
          ("Sensitive details handled with care", "Personal identifiers can be masked or left out wherever the "
           "work doesn't need them."),
          ("Tested before it goes live", "We test each system on agreed samples, with results you can check, "
           "before it handles real work.")]),
    ],
    "standards": ("We design and run our work using the practices behind recognised security and privacy "
                  "frameworks, including SOC 2 (security, availability and confidentiality controls), GDPR (data "
                  "minimisation, purpose limitation, the rights of the people the data is about) and HIPAA "
                  "(safeguards for sensitive personal information), along with Canada's PIPEDA and the "
                  "confidentiality rules of your profession. These are practices we follow, not certifications we "
                  "claim. Where you need a certified party, the certification belongs to the model and cloud "
                  "providers we use, and we'll show you their reports."),
    "incident": ("If we ever find a problem that affects your data, we tell you promptly, explain what happened and "
                 "what we know, stop the affected system if needed, and work with you on the fix. Your contract "
                 "sets out the details."),
    "faq": [
        ("Is our data used to train AI models?",
         "No. We use only business-grade AI services whose terms exclude training on customer data, or open-weight "
         "models run privately in your own environment. Your documents are used only to do your work."),
        ("Which AI models do you use?",
         "Models from an approved list: enterprise services from major providers with no-training terms, known "
         "retention and independent audits, or a private open-weight model. You approve which ones touch your data "
         "before we start."),
        ("Is VisionzLab SOC 2 or HIPAA certified?",
         "No. We follow the practices behind SOC 2, GDPR, HIPAA and PIPEDA in how we design and run systems, but "
         "we don't claim those certifications. The model and cloud providers we use hold their own, and we can "
         "share their reports."),
        ("Can the AI act on its own?",
         "Not on anything that matters. It proposes, a person approves, and every step is logged. Anything it "
         "isn't sure about goes to a person."),
        ("Can we keep everything in Canada?",
         "Where you need it, we choose services that process data in Canada, or run the system inside your own "
         "cloud account in a Canadian region."),
    ],
}
GUIDES_PUBLISHED = "2026-10-31"

# Evergreen answers to questions owners search for. Each section is (heading, paragraphs, bullets).
GUIDES = [
    {
        "slug": "guides/choose-an-ai-automation-partner/",
        "nav": "Choosing an AI partner",
        "title": "How to Choose an AI Automation Partner",
        "h1": "How to choose an AI automation partner",
        "accent": "AI automation partner",
        "description": "Eight questions to ask before you hire an AI automation company or consultant, the "
                       "red flags to watch for, and how to keep the first project small.",
        "lead": "Most small businesses only buy AI help once or twice, so it's hard to tell a good partner from a "
                "good pitch. These are the questions that separate them.",
        "sections": [
            ("Start with one workflow, not a strategy", [
                "The best first project is one piece of work your team does every week: reading supplier quotes, "
                "keying orders, sorting a shared inbox, chasing renewals. It has inputs you can show a partner, a "
                "result you can check, and a person who knows when the output is wrong.",
                "A partner who wants to start with a company-wide AI strategy before touching any real work is "
                "asking you to pay for a document. Ask them to pick the workflow with you instead.",
            ], []),
            ("Eight questions to ask", [], [
                "Will you show it working on our own documents before we commit to a full build?",
                "Who approves what the AI produces, and where does that step sit in the workflow?",
                "Which accounts and permissions does it need, and can we turn them off ourselves?",
                "Who owns the prompts, code, configuration and accounts when the project ends?",
                "What does it cost to run each month after it's built: software, AI usage and support?",
                "How will we measure whether it worked, and who measures it?",
                "What happens when it meets something it hasn't seen before?",
                "If we stop working together, how do we keep it running or switch it off cleanly?",
            ]),
            ("Red flags", [], [
                "A demo on the vendor's sample data, but no offer to test on yours.",
                "Accuracy or savings figures quoted before anyone has seen your work.",
                "No named person on your side who approves the AI's output.",
                "Accounts, keys or code held by the vendor with no handover plan.",
                "A large up-front build with no smaller first step you can judge.",
            ]),
            ("Make the first step small enough to judge", [
                "Ask for a short, paid first step with a defined deliverable: a prototype on a sample of your real "
                "inputs, a measure of success you agree up front, and a costed plan for what comes next. If it "
                "doesn't work, you've spent a little and learned a lot. If it does, you have evidence for the "
                "bigger decision.",
                "That is how our own Discovery Sprint works, and it's a fair test to apply to any partner, including us.",
            ], []),
        ],
        "faq": [
            ("Which AI automation company is best for a small business?",
             "The one that will test on your own work before you commit, names who approves the output, hands over "
             "ownership of what it builds, and can tell you the monthly running cost. Use the eight questions above "
             "to compare any shortlist."),
            ("How much should an AI automation project cost?",
             "It depends on the workflow and how much help you want, from training your team to having a partner "
             "build and run it. Ask for a fixed price for a defined first step, and for the monthly running cost, "
             "before you sign anything larger."),
            ("Do we need a technical person on staff?",
             "Not to start. You need someone who knows the work well enough to judge the output. A good partner "
             "sets up the technical side and leaves you a playbook, or runs it for you."),
            ("Should we just use ChatGPT or Copilot ourselves?",
             "Often, yes, for individual tasks. A partner earns their fee when the work runs across systems, needs "
             "approval steps, or has to run reliably every day without someone prompting it."),
        ],
    },
    {
        "slug": "guides/ai-agent-vs-automation-vs-hire/",
        "nav": "Agent, automation or hire?",
        "title": "AI Agent, Automation or a New Hire? How to Decide",
        "h1": "AI agent, automation tool or a new hire?",
        "accent": "or a new hire?",
        "description": "A plain decision guide for small businesses: when rules-based automation is enough, when "
                       "an AI agent with human approval fits, and when the work needs a person.",
        "lead": "Three different tools for three different kinds of work. Picking the wrong one is the most common "
                "reason automation projects disappoint.",
        "sections": [
            ("Rules-based automation: fixed inputs, fixed rules", [
                "If the information arrives in the same shape every time and the steps never change, a rules-based "
                "tool is cheaper and more predictable than AI. Moving form submissions into a spreadsheet, sending "
                "a reminder three days before a due date, or copying a new customer into your CRM are rules-based "
                "jobs. Tools such as Zapier, Make, Power Automate or your own software's built-in rules do this well.",
            ], []),
            ("An AI agent: messy inputs, judgement within limits", [
                "If the work starts with reading something written for people (emails, PDFs, scanned forms, "
                "supplier quotes) and needs judgement inside clear limits, that is where an AI agent helps. It can "
                "read the request, match it to your catalogue or records, draft the reply or the entry, and flag "
                "what it isn't sure about.",
                "The safe pattern is that the agent prepares and a person approves. Your team stops re-keying and "
                "starts checking, which is faster and keeps the decisions with them.",
            ], []),
            ("A person: relationships, accountability, rare cases", [
                "Negotiating with a key customer, deciding on an exception that sets a precedent, or owning the "
                "result when something goes wrong is work for a person. So is any task that happens a few times a "
                "year: it isn't worth automating.",
            ], []),
            ("Signs a workflow is ready for an agent", [], [
                "It happens every week, often enough that the time adds up.",
                "Someone re-keys or copies information from documents or email into a system.",
                "You can show twenty real examples of the input and the correct result.",
                "A person on the team can tell quickly whether the output is right.",
                "The systems involved have an API, an import, or a usable screen workflow.",
            ]),
            ("Most real workflows use all three", [
                "A typical result: rules move the files, an agent reads them and drafts the entry, and a person "
                "approves the exceptions. Deciding which step belongs to which is most of the design work.",
            ], []),
        ],
        "faq": [
            ("Is an AI agent cheaper than hiring?",
             "Sometimes, for the reading and re-keying part of a role, but not for the judgement and relationships. "
             "Compare the agent's build and monthly running cost with the hours it takes back, measured on your "
             "own work. Our hours-back calculator is a quick first estimate."),
            ("What is the difference between an AI agent and automation?",
             "Automation follows fixed rules on structured data. An AI agent can read unstructured input such as "
             "email and documents, and decide within limits you set. Many workflows combine both."),
            ("Can an AI agent make mistakes?",
             "Yes. That's why the agent should flag uncertain cases and a person should approve anything that "
             "matters before it is sent or saved."),
        ],
    },
    {
        "slug": "guides/human-approval-for-ai-agents/",
        "nav": "Keeping a person in the loop",
        "title": "Human Approval for AI-Drafted Quotes and Emails",
        "h1": "Keeping a person in the loop when an AI agent drafts",
        "accent": "in the loop",
        "published": "2026-11-01",
        "description": "Let the agent draft and a person send. Where to put the approval step, what the reviewer "
                       "needs to see, and when it's safe to loosen it.",
        "lead": "Let the agent prepare and a person send. The agent puts its draft quote or email in a review "
                "queue, and nothing reaches a customer until someone with authority approves it.",
        "sections": [
            ("The rule: the agent drafts, a person sends", [
                "The simplest safe design gives the agent permission to create drafts and nothing more. It can read "
                "the request, look up your catalogue, prices and history, and write the quote or reply. Sending, "
                "committing a price, promising a date or changing a customer record stays with your team.",
                "Enforce this with permissions as well as instructions. If the agent's account can only save "
                "drafts, a bad prompt or an odd email can't make it send anything.",
            ], []),
            ("Where to put the approval step", [
                "Approve everything at first. As your team learns where the agent is reliable, keep the approval "
                "step on the work where a mistake is expensive or hard to undo:",
            ], [
                "Anything that commits a price, a discount, a delivery date or credit terms.",
                "First contact with a new customer or supplier.",
                "Anything outside your rules: unknown items, substitutes, unusual quantities or terms.",
                "Complaints, cancellations and anything with legal or safety wording.",
            ]),
            ("What the reviewer needs to see", [
                "An approval is only useful if the reviewer can check the draft quickly. Show these next to it:",
            ], [
                "The original request, so the draft can be compared with what the customer asked for.",
                "What the agent matched and where it came from: the item, the price list, the past order.",
                "What it wasn't sure about, flagged at the top rather than buried in the draft.",
                "Anything that differs from your standard terms.",
                "Approve, edit or reject in one step, with a short reason when they reject.",
            ]),
            ("Building it with the tools you already have", [
                "You rarely need new software for the review step. Drafts can sit in a shared mailbox's drafts "
                "folder, quotes can be saved in your ERP or CRM with a draft status, and a short message in Teams "
                "or Slack can point the reviewer to each one. What matters is that every draft, approval, edit and "
                "rejection is recorded.",
            ], []),
            ("When it's safe to loosen it", [
                "Use the approval record to decide. For each type of work, track how often drafts are approved "
                "without edits. Where that stays high and the cost of a mistake is small, such as a repeat order "
                "of standard items at list price, you can let the agent release within limits you set. Keep "
                "checking a sample of what it releases.",
            ], []),
            ("Red flags", [], [
                "The agent sends from a mailbox with full send rights \"just for now\".",
                "Reviewers approve without seeing the original request.",
                "Nothing records who approved what.",
                "Nobody can say which work the agent is allowed to release on its own.",
            ]),
        ],
        "faq": [
            ("Doesn't approving every draft cancel out the time saved?",
             "Checking a prepared draft against the original request is quicker than reading the request, looking "
             "everything up and typing the reply from scratch. The agent does the reading and matching; the "
             "decision stays with your team."),
            ("Can an AI agent ever send emails or quotes on its own?",
             "Only if you decide it should, within limits you set, for low-risk work where its approval record "
             "shows it is reliable. Keeping a person on every customer-facing message is also a sound permanent choice."),
            ("What should be logged?",
             "The incoming request, the agent's draft, who approved or changed it, what they changed, and when it "
             "was sent. That record is how you find problems and decide when to loosen the rules."),
        ],
    },
    {
        "slug": "guides/ai-quoting-for-machine-shops/",
        "nav": "AI quoting for machine shops",
        "eyebrow": "White paper",
        "title": "AI Quoting for Machine Shops: A 2026 Field Guide",
        "h1": "AI quoting for machine shops",
        "accent": "machine shops",
        "published": "2026-11-03",
        "description": "What AI quoting tools for CNC and fabrication shops do today, what they cost, where they "
                       "fall short on messy RFQs, and how to test one on your own work.",
        "lead": "Quoting takes up estimator hours in most job shops, and in 2026 AI quoting tools arrived in "
                "force. This paper covers what they do, what they cost, where they still fall short, and how a "
                "shop or a shop network can test one on its own requests.",
        "sections": [
            ("Why quoting is the bottleneck", [
                "In a typical job shop, a few people quote everything, usually the same people who run the floor. "
                "Every RFQ has to be read, the print checked against the model, the material and stock size "
                "worked out, setups and outside processes estimated, and the missing details chased. Most quotes "
                "don't win, so most of that time goes to work the shop never makes.",
                "Buyers have also changed. An engineer who needs a bracket tomorrow can upload a model to an "
                "instant-quote website and see a price in seconds. A local shop that takes three days to answer, "
                "or replies with a list of questions, loses that job before anyone compares quality.",
                "Not every shop feels this. An owner who quotes a handful of jobs a week, mostly for repeat "
                "customers, may spend very little time on it. The pain sits with shops that quote often: dozens "
                "of parts a week, many of them from new buyers.",
            ], []),
            ("What's on the market (October 2026)", [
                "There are two different markets, and it's easy to mix them up.",
                "Shop-side estimating tools work for the shop's estimator. They read the model and the print, "
                "estimate cycle time and cost, and build the quote. Examples: CloudNC Quote Agent, which launched "
                "in October 2026 (forward the RFQ or upload drawings and models, and it drafts a manufacturing "
                "plan, routing times and costs, and asks about anything missing), Paperless Parts, Machine "
                "Research, Toolpath, up2parts, Spanflug and DigiFabster (instant quoting on a shop's own website).",
                "Buyer-side instant-quote platforms work for the buyer. SendCutSend, Xometry and Protolabs Network "
                "give an instant price on upload, then make the part themselves or send it to their own suppliers. "
                "For a local shop, they are competitors, not tools.",
                "Published prices for shop-side tools, as listed by the vendors in October 2026:",
            ], [
                "Free for manual quoting, and US$2.50 a part for an AI agent (CloudNC).",
                "About US$75–125 a month for small-shop quoting tools.",
                "US$2,000–50,000 a year for white-label or enterprise quoting.",
                "Many vendors don't publish prices and quote after a demo.",
            ]),
            ("If a tool already fits, use it", [
                "If your requests arrive as clean STEP files and your parts are mostly milled or turned, trial one "
                "of the shop-side tools before you build anything. They are good and cheap, and they improve "
                "quickly. We'd tell a shop that, and help it set one up.",
            ], []),
            ("Where off-the-shelf tools fall short", [
                "The gaps we see are less about the estimating maths and more about everything around it:",
            ], [
                "Messy input. Real requests include a phone photo of a sketch, a PDF with no model, or an email "
                "with three attachments and a revision in the body. Most tools are built around clean CAD.",
                "Questions asked too late. The missing tolerance, finish or quantity is usually found by the "
                "estimator, days in. The questions should go to the buyer first, before anyone prices the job.",
                "Your own history. A draft is only as good as the rates, machines and past jobs behind it. Without "
                "your won and lost quotes and your actual hours, any tool is guessing.",
                "Where files live. Several tools host in the United States only. Shops under Canada's Controlled "
                "Goods Program, or with customers who ask, may need Canadian hosting and clear deletion rules.",
                "How it fits the day. Quotes have to come out of your inbox, into your quote template and your "
                "ERP (JobBOSS², ProShop, E2 or a spreadsheet), not into another login nobody opens.",
                "Shop networks. No tool we found sits between one buyer and many local shops, cleaning up the "
                "request and routing it to the shops that fit.",
            ]),
            ("How an AI quoting assistant works", [
                "The design we build is a first pass that prepares the quote, with a person approving it:",
            ], [
                "Reads the request wherever it arrives: email, web form, PDF print, sketch photo or STEP file.",
                "Pulls out the spec: material, quantity, tolerances, finish, outside processes and due date.",
                "Measures the model with an open-source CAD kernel: bounding box, stock size, volume, material "
                "removed and basic features.",
                "Lists what is missing or unclear, worded as questions the buyer can answer in one reply.",
                "Drafts a cost from your machines, rates, materials and markups, and finds similar past jobs.",
                "Puts the draft, its working and its doubts in front of your estimator to approve, edit or reject.",
            ]),
            ("What stays with the estimator", [
                "The assistant prepares; it never quotes on its own. The price, the delivery date, the decision "
                "not to quote, and anything it flags as uncertain stay with your people. Its account can save "
                "drafts and nothing more, so an odd request can't make it send anything.",
            ], []),
            ("For shop networks and associations", [
                "A regional network of shops can put the same first pass at its front door. A buyer uploads a "
                "sketch, PDF or model once. The assistant asks the buyer for what's missing, produces a clean "
                "request package and suggests the member shops that fit. Each shop still sets its own price. That "
                "makes the local route almost as easy as an instant-quote website, without a markup.",
                "A network can also fund the build the way many associations launch member services: members "
                "pledge a founding rate, and nothing is charged unless enough shops sign up by a set date.",
            ], []),
            ("How to test it on your own requests", [
                "Don't judge any quoting tool, ours included, on a vendor's sample part. Run a small test on your "
                "own work:",
            ], [
                "Pick twenty recent RFQs where you know what you quoted, whether you won, and the actual hours.",
                "Leave out anything under the Controlled Goods Program, ITAR or a customer NDA that forbids it.",
                "Measure the time to a first draft, the share of missing details it caught, and how close its "
                "cost came to your own quote.",
                "Decide from the numbers: buy a tool, build around your workflow, or keep quoting by hand.",
            ]),
            ("Red flags", [], [
                "Accuracy or savings figures before anyone has run your parts.",
                "No clear answer on where drawings are stored, who can see them and when they're deleted.",
                "Your drawings used to train the vendor's model by default.",
                "Quotes sent to customers without a person approving them.",
                "No way to use your own rates, machines and past jobs.",
            ]),
        ],
        "faq": [
            ("Can AI quote a CNC part from a sketch or a 3D model?",
             "It can draft one. From a STEP model it can measure stock size, volume and features and estimate "
             "cycle time; from a sketch or PDF it pulls out what it can and lists the questions for the buyer. An "
             "estimator should approve every price."),
            ("How much does AI quoting software cost for a machine shop?",
             "Published prices in October 2026 ran from free for manual quoting and US$2.50 a part for an AI agent, "
             "to about US$75–125 a month for small-shop tools and US$2,000–50,000 a year for white-label or "
             "enterprise quoting. A custom build is priced on scope."),
            ("Is it safe to upload customer drawings to an AI tool?",
             "Ask where files are stored, who can see them, whether they train the vendor's model and when they're "
             "deleted. Keep Controlled Goods Program and ITAR drawings out of any tool that isn't approved for them."),
            ("Will AI replace our estimator?",
             "No. It takes over the reading, measuring and chasing so your estimator spends their time on the "
             "judgement: the price, the risk and whether the job is worth taking."),
        ],
    },
]

# Workflow finder (homepage and /tools/): words a visitor might type, mapped to the page that answers them.
FINDER = {
    "use-cases/quote-rfq-intake/": ["quote", "rfq", "estimate", "pricing", "price list", "tender", "bid"],
    "for/machine-shops/": ["machin", "cnc", "job shop", "fabricat", "sheet metal", "sketch", "drawing", "step file",
                           "3d model", "cad", "cycle time", "estimator"],
    "use-cases/order-entry/": ["order", "purchase order", "po", "erp", "re-key", "rekey", "data entry", "sales order"],
    "use-cases/document-intake/": ["invoice", "pdf", "document", "paperwork", "scan", "form", "application",
                                   "receipt", "bill", "shipping"],
    "use-cases/inbox-triage/": ["email", "inbox", "mailbox", "e-mail", "customer service", "support", "enquir",
                                "inquir"],
    "use-cases/renewals-follow-up/": ["renewal", "follow up", "follow-up", "remind", "chas", "overdue",
                                      "collection", "expir"],
    "use-cases/market-intelligence/": ["competitor", "market", "news", "monitor", "industry"],
    "use-cases/prospect-research/": ["lead", "prospect", "outreach", "research", "crm", "sales list"],
    "use-cases/planning-okrs/": ["okr", "planning", "goal", "meeting", "strategy", "priorit"],
    "use-cases/financial-reporting/": ["report", "month-end", "month end", "reconcil", "bookkeep", "financial",
                                       "spreadsheet", "excel", "budget"],
    "services/ai-training/": ["learn", "train", "teach", "workshop", "chatgpt", "copilot", "staff", "course"],
    "services/security-review/": ["security", "secure", "cyber", "hack", "breach", "phishing", "ransomware",
                                  "vulnerab", "patch", "mfa", "password", "insurance questionnaire", "firewall"],
    "instead-of-hiring/": ["hire", "hiring", "developer", "engineer", "build an app", "software", "headcount"],
}
FINDER_EXAMPLES = ["Typing supplier quotes into our system", "Answering the shared inbox",
                   "Chasing renewals and overdue invoices", "Month-end reports in Excel"]

FAQ_HOME = [
    ("What is VisionzLab?",
     "VisionzLab (visionzlab.com, sometimes written Visionz Lab) is an AI studio based in Ontario, Canada. We help "
     "small and mid-sized businesses in Canada and the US put AI agents to work on everyday workflows such as "
     "documents, quotes, orders, email and follow-up, with people approving the decisions that matter."),
    ("Who do you work with?", WHO_WE_SERVE),
    ("Do we need technical staff to work with you?",
     "No. You need someone who knows the work and can check the output. We set up the technical side with your "
     "team and hand over a playbook, or build and run it for you."),
    ("How much does it cost?",
     "It depends on the workflow and how much help you want. We don't publish rates. After a free discovery "
     "session we quote a defined first step, usually the Discovery Sprint, before you commit to anything bigger."),
    ("How do you keep our data and decisions under control?",
     "Agents get only the accounts and permissions you give them, and approval steps, audit trails and limits on "
     "what an agent may do are part of every build. We agree what data is used, and who can see it, before work starts."),
    ("Can you check our security, not just build AI?",
     "Yes. Our Security Review checks the gaps attackers try first, including internet-facing systems, email and "
     "sign-in, cloud settings and the AI tools your team uses, and gives you a plain-English fix list. We then help "
     "you close the top items with your IT person or provider."),
    ("What if AI isn't the right answer for our problem?",
     "Then we'll say so. Some work is better handled by a simple rules-based automation or by a person, and the "
     "discovery session is where we tell you which."),
]

FAQ_TOOLS = [
    ("Do these tools send what I type anywhere?",
     "No. The workflow finder and the calculator run in your browser. We record only that a tool was used, not "
     "what you entered."),
    ("Are the calculator's results a quote or a promise?",
     "No. They're your own numbers multiplied out. The Discovery Sprint measures the real effect on a sample of "
     "your work."),
]

# --------------------------------------------------------------------------
# Rendering
# --------------------------------------------------------------------------


def url(slug):
    return f"{SITE}/{slug}"


def rel(from_slug, to_slug):
    """Relative link between two page slugs (directory-style)."""
    depth = from_slug.count("/")
    return "../" * depth + to_slug if to_slug else ("../" * depth or "./")


SECTION_NAMES = {"services/": "Services", "use-cases/": "Use Cases", "guides/": "Guides", "free-tools/": "Free tools"}


def breadcrumbs_ld(slug, title):
    crumbs = [("", "Home")]
    section = slug.split("/")[0] + "/"
    if slug.count("/") > 1 and section in SECTION_NAMES:
        crumbs.append((section, SECTION_NAMES[section]))
    crumbs.append((slug, title))
    return {"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": n, "item": url(s)} for i, (s, n) in enumerate(crumbs)]}


NUM_WORDS = {2: "Two", 3: "Three", 4: "Four", 5: "Five", 6: "Six", 7: "Seven", 8: "Eight"}


def contact(ref, label="Book a free discovery call", cls="btn", inner=None):
    """inner: pre-built HTML for the link body (the label is escaped otherwise)."""
    external = '' if CONTACT_URL.startswith(SITE) else ' target="_blank" rel="noopener"'
    return (f'<a class="{cls}" href="{CONTACT_URL}#ref={e(ref)}" data-contact data-ref="{e(ref)}" '
            f'data-umami-event="contact_click" data-umami-event-location="{e(ref)}"{external}>'
            f'{inner if inner is not None else e(label)}</a>')


def answer_first(qa):
    """The page's buyer question and its direct answer, straight under the hero (idea 13, answer-first).
    The pair stays first in FAQPage JSON-LD; the visible FAQ below lists only the follow-up questions."""
    q, a = qa
    return (f'<section class="section answer-first"><div class="wrap narrow"><p class="eyebrow">The short answer</p>'
            f'<h2>{e(q)}</h2><p class="big">{e(a)}</p></div></section>')


def faq_section(faq):
    return f'<section class="section"><div class="wrap">{faq_html(faq)}</div></section>' if faq else ""


def faq_html(faq):
    items = "".join(f"<details><summary>{e(q)}</summary><p>{e(a)}</p></details>" for q, a in faq)
    return f'<div class="faq-block"><h2>Questions</h2><div class="faq">{items}</div></div>'


def faq_ld(faq):
    return {"@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq]}


def art(slug, key, alt="", eager=False):
    path, w, h, *small = ART[key]
    if not (ROOT / path).exists():
        path, w, h, small = "public/computer.webp", 640, 540, []
    load = 'fetchpriority="high"' if eager else 'loading="lazy"'
    srcset = (f' srcset="{rel(slug, small[0][0])} {small[0][1]}w, {rel(slug, path)} {w}w"'
              ' sizes="(max-width: 860px) 100vw, 50vw"' if small else "")
    return (f'<img src="{rel(slug, path)}"{srcset} alt="{e(alt)}" width="{w}" height="{h}" {load} '
            'decoding="async" />')


def ladder(slug, highlight=None, only=None):
    cards = []
    for i, t in enumerate(TIERS):
        if only is not None and i not in only:
            continue
        on = " card-on" if t["slug"] == highlight else ""
        cards.append(
            f'<a class="card tier{on}" href="{rel(slug, t["slug"])}">'
            f'<span class="num">0{len(cards) + 1}</span><span class="tag">{e(t["tier"])}</span>'
            f'<div class="thumb">{art(slug, t["art"])}</div>'
            f'<h3>{e(t["nav"])}</h3><p>{e(t["lead"])}</p><span class="arrow">→</span></a>')
    return f'<div class="cards cards-tiers">{"".join(cards)}</div>'


OG_CARDS = {}  # card file name -> (eyebrow, title); filled by page(), rendered by render_og_cards()


def og_card_name(slug):
    return (slug.strip("/").replace("/", "--") or "home") + ".png"


def page(slug, title, description, main, ld=None, ref="site", image=None, og_type="website"):
    if image is None:
        section = slug.split("/")[0] + "/"
        eyebrow = SECTION_NAMES.get(section, "Guides" if slug.startswith("guides/") else "") if slug else ""
        if slug.startswith("for/"):
            eyebrow = "Who we help"
        OG_CARDS[og_card_name(slug)] = (eyebrow or BRAND, title)
        image = f"public/og/{og_card_name(slug)}"
    canonical = url(slug)
    full_title = f"{title} | {BRAND}" if slug else f"{BRAND} | {title}"
    nav = [("services/", "Services"), ("use-cases/", "Use Cases"), ("discovery-sprint/", "Discovery Sprint"),
           ("experience/", "Experience"), ("about/", "About")]
    def cur(s):
        return ' aria-current="page"' if slug == s else (' aria-current="true"' if slug.startswith(s) else "")
    nav_html = "".join(f'<a href="{rel(slug, s)}"{cur(s)}>{e(n)}</a>' for s, n in nav)
    foot_tiers = "".join(f'<li><a href="{rel(slug, t["slug"])}">{e(t["nav"])}</a></li>' for t in TIERS)
    foot_plays = "".join(f'<li><a href="{rel(slug, p["slug"])}">{e(p["nav"])}</a></li>' for p in PLAYS)
    foot_team = "".join(f'<li><a href="{rel(slug, m["slug"])}">{e(m["name"])}</a></li>' for m in TEAM)
    foot_guides = "".join(f'<li><a href="{rel(slug, g["slug"])}">{e(g["nav"])}</a></li>' for g in GUIDES)
    foot_social = "".join(f'<li><a href="{url}" rel="noopener">{label}</a></li>' for label, url in SOCIAL_PROFILES)
    foot_uses = "".join(f'<li><a href="{rel(slug, u["slug"])}">{e(u["nav"])}</a></li>' for u in USE_CASES)
    graph = [ORG] + ([WEBSITE] if not slug else []) + (ld or []) + ([breadcrumbs_ld(slug, title)] if slug else [])
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
    <link rel="alternate" type="application/rss+xml" title="{BRAND} guides" href="{SITE}/{GUIDES_SLUG}feed.xml" />
    <meta property="og:type" content="{og_type}" />
    <meta property="og:site_name" content="{BRAND}" />
    <meta property="og:title" content="{e(full_title)}" />
    <meta property="og:description" content="{e(description)}" />
    <meta property="og:url" content="{canonical}" />
    <meta property="og:image" content="{SITE}/{image}" />
    <meta name="twitter:card" content="summary_large_image" />
    <meta name="twitter:title" content="{e(full_title)}" />
    <meta name="twitter:description" content="{e(description)}" />
    <meta name="twitter:image" content="{SITE}/{image}" />
    <link rel="icon" type="image/svg+xml" href="data:image/svg+xml,%3Csvg%20xmlns%3D%22http%3A//www.w3.org/2000/svg%22%20viewBox%3D%220%200%20100%20100%22%3E%3Cg%20fill%3D%22%23E1FF3F%22%20stroke%3D%22%2316052D%22%20stroke-width%3D%223.5%22%20stroke-linejoin%3D%22round%22%3E%3Cpath%20d%3D%22M38%2027%20Q49.22%2048.78%2071%2060%20Q49.22%2071.22%2038%2093%20Q26.78%2071.22%205%2060%20Q26.78%2048.78%2038%2027%20Z%22/%3E%3Cpath%20d%3D%22M79%209%20Q84.1%2018.9%2094%2024%20Q84.1%2029.1%2079%2039%20Q73.9%2029.1%2064%2024%20Q73.9%2018.9%2079%209%20Z%22/%3E%3C/g%3E%3C/svg%3E" />
    <link rel="apple-touch-icon" href="{SITE}/public/logo.png" />
    <link rel="preload" href="{rel(slug, "public/fonts/inter-latin.woff2")}" as="font" type="font/woff2" crossorigin />
    <link rel="stylesheet" href="{css}" />
    <script type="application/ld+json">{json.dumps({"@context": "https://schema.org", "@graph": graph}, indent=None)}</script>
  </head>
  <body>
    <a class="skip-link" href="#main-content">Skip to content</a>
    <header class="top">
      <div class="wrap top-in">
        <a class="brand" href="{rel(slug, '')}"><svg class="mark" viewBox="0 0 100 100" aria-hidden="true"><g fill="#E1FF3F" stroke="#16052D" stroke-width="3.5" stroke-linejoin="round"><path d="M38 27 Q49.22 48.78 71 60 Q49.22 71.22 38 93 Q26.78 71.22 5 60 Q26.78 48.78 38 27 Z"/><path d="M79 9 Q84.1 18.9 94 24 Q84.1 29.1 79 39 Q73.9 29.1 64 24 Q73.9 18.9 79 9 Z"/></g></svg>{BRAND}</a>
        <nav class="nav" aria-label="Main navigation">{nav_html}{contact(ref + '-nav', 'Book a free discovery call', 'btn btn-sm')}</nav>
        <details class="mobile-menu"><summary>Menu</summary>
          <nav aria-label="Mobile navigation">{nav_html}{contact(ref + '-nav', 'Book a free discovery call', 'btn btn-sm')}</nav>
        </details>
      </div>
    </header>
    <main id="main-content" tabindex="-1">
{main}
    </main>
    <footer class="foot">
      <div class="wrap foot-in">
        <div><a class="brand" href="{rel(slug, '')}"><svg class="mark" viewBox="0 0 100 100" aria-hidden="true"><g fill="#E1FF3F" stroke="#16052D" stroke-width="3.5" stroke-linejoin="round"><path d="M38 27 Q49.22 48.78 71 60 Q49.22 71.22 38 93 Q26.78 71.22 5 60 Q26.78 48.78 38 27 Z"/><path d="M79 9 Q84.1 18.9 94 24 Q84.1 29.1 79 39 Q73.9 29.1 64 24 Q73.9 18.9 79 9 Z"/></g></svg>{BRAND}</a>
          <p class="muted">AI agents and automation for small and mid-sized businesses.<br />
          Based in Ontario, Canada · serving Canada and the US.</p></div>
        <div><h2>Services</h2><ul>{foot_tiers}<li><a href="{rel(slug, SECURITY["slug"])}">{SECURITY["nav"]}</a></li>
          <li><a href="{rel(slug, 'discovery-sprint/')}">Discovery Sprint</a></li>
          <li><a href="{rel(slug, MATURITY_SLUG)}">The 4S check</a></li></ul></div>
        <div><h2>Use cases</h2><ul>{foot_uses}</ul></div>
        <div><h2>Who we help</h2><ul>{foot_plays}</ul></div>
        <div><h2>Resources</h2><ul><li><a href="{rel(slug, GUIDES_SLUG)}">Guides</a></li>
          {foot_guides}<li><a href="{rel(slug, TOOLS_SLUG)}">Free tools</a></li>
          <li><a href="{rel(slug, CALC_SLUG)}">Hours-back calculator</a></li></ul></div>
        <div><h2>Company</h2><ul><li><a href="{rel(slug, 'about/')}">About</a></li>
          <li><a href="{rel(slug, EXPERIENCE_SLUG)}">Our experience</a></li>
          <li><a href="{rel(slug, DATA_TRUST_SLUG)}">Security and privacy</a></li>
          {foot_team}
          {foot_social}
          <li><a href="mailto:{EMAIL_SALES}">{EMAIL_SALES}</a></li>
          <li><a href="mailto:{EMAIL_GENERAL}">{EMAIL_GENERAL}</a></li></ul></div>
      </div>
      <div class="legal"><div class="wrap muted">© {datetime.date.today().year} {LEGAL_NAME} · {BRAND} is a brand of
        {LEGAL_NAME}, an Ontario corporation. · <a href="{rel(slug, PRIVACY_SLUG)}">Privacy</a></div></div>
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
        // Social and newsletter links carry UTM tags instead (career/_analytics/UTM.md):
        // ?utm_source=linkedin&utm_campaign=order-entry becomes ref "utm-linkedin-order-entry".
        var utmSource = params.get('utm_source');
        if (!inbound && utmSource) {
          var utmLabel = params.get('utm_campaign') || params.get('utm_content') || params.get('utm_medium');
          inbound = ['utm', utmSource, utmLabel].filter(Boolean).join('-').slice(0, 80);
        }
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


def headline(text, accent=None):
    """Wrap the accent phrase (default: everything after ' for ') in a lime highlight."""
    if accent is None and " for " in text:
        accent = text.split(" for ", 1)[1]
    if accent and text.endswith(accent):
        head = text[: -len(accent)]
        return f'{e(head)}<span class="hl">{e(accent)}</span>'
    return e(text)


def hero(h1, lead, ref, eyebrow=None, cta="Book a free discovery call", slug="", img=None, alt="",
         accent=None, tone="paper", second=None, stats=None, task=None):
    """task=(href, label): tool and index pages lead with their own action (D11). The task link becomes the
    filled primary, the discovery call drops to a ghost button, and the hero is compact so content shows."""
    eb = f'<p class="eyebrow">{e(eyebrow)}</p>' if eyebrow else ""
    sec = f'<a class="btn btn-ghost" href="{rel(slug, second[0])}">{e(second[1])}</a>' if second else ""
    if task:
        href = task[0] if task[0].startswith("#") else rel(slug, task[0])
        primary = "btn btn-ink" if tone == "lime" else "btn"
        actions = (f'<a class="{primary}" href="{href}" data-umami-event="page_task" data-umami-event-location="{e(ref)}">'
                   f'{e(task[1])}</a>{contact(ref, cta, "btn btn-ghost")}')
    else:
        actions = f"{contact(ref, cta)}{sec}"
    tone = f"{tone} hero-compact" if task else tone
    visual = f'<div class="frame">{art(slug, img, alt, eager=True)}</div>' if img else ""
    cls = "hero-split" if img else "hero-solo"
    side = visual
    if stats:
        # Plain text, not animated counters: crawlers and AI answer engines read the number as written.
        items = "".join(f'<li><strong>{e(v)}</strong><span>{e(t)}</span></li>' for v, t in stats)
        side = f'<div class="hero-side">{visual}<ul class="hero-stats">{items}</ul></div>'
    return (f'<section class="hero tone-{tone}"><div class="wrap {cls}"><div class="hero-copy">{eb}'
            f'<h1>{headline(h1, accent)}</h1><p class="lead">{e(lead)}</p>'
            f'<div class="actions">{actions}</div></div>{side}</div></section>')


def section_head(eyebrow, title, intro=None, accent=None):
    i = f'<p class="intro">{e(intro)}</p>' if intro else ""
    return f'<div class="sec-head"><p class="eyebrow">{e(eyebrow)}</p><h2>{headline(title, accent)}</h2>{i}</div>'


def sec_head_split(eyebrow, title, side, accent=None):
    """Section opener: the statement on the left, the short explanation on the right."""
    return (f'<div class="sec-split"><div><p class="eyebrow">{e(eyebrow)}</p><h2>{headline(title, accent)}</h2></div>'
            f'<p class="side">{e(side)}</p></div>')


def sec_foot(i, total, label, href=None, ref=None, slug="", second=None):
    """Section closing row: where you are on the page on the left, this section's own next step on the right.
    href links within the site; ref makes it a tracked contact link instead."""
    ticks = "".join('<i class="on"></i>' if n == i else "<i></i>" for n in range(1, total + 1))
    body = f'<span>{e(label)}</span><b class="go-box" aria-hidden="true">→</b>'
    go = contact(ref, cls="go", inner=body) if ref else f'<a class="go" href="{rel(slug, href)}">{body}</a>'
    sec = f'<a class="link" href="{rel(slug, second[0])}">{e(second[1])}</a>' if second else ""
    return (f'<div class="sec-foot"><div class="sec-pos"><span class="ticks-bar" aria-hidden="true">{ticks}</span>'
            f'<span class="sec-num">{i:02d} / {total:02d}</span></div><div class="sec-go">{sec}{go}</div></div>')


# Homepage proof grid: screens from the concept mocks in the asal repo (foundation/visionzlab/demos), run once and
# cropped to the review panel. Invented names and numbers only, and a person approves each step: never swap in a
# screen from a real client or employer system.
PROOF = [
    ("use-cases/quote-rfq-intake/", "quote-rfq-intake", "big",
     "Concept demo: an RFQ's three lines matched to the catalogue, one flagged for a person to check, and a draft reply"),
    ("use-cases/order-entry/", "order-entry", "small",
     "Concept demo: a purchase order checked against price, terms and ship-to, waiting for a person to release it"),
    ("use-cases/document-intake/", "document-intake", "big",
     "Concept demo: invoice fields extracted with their source, and a smudged PO reference left for a person"),
]


def proof_bento(slug):
    by_slug = {u["slug"]: u for u in USE_CASES}
    tiles = []
    for s, shot, size, alt in PROOF:
        u = by_slug[s]
        tiles.append(
            f'<a class="tile tile-{size}" href="{rel(slug, s)}"><div class="tile-copy"><span class="tag">Use case</span>'
            f'<h3>{e(u["nav"])}</h3><p>{e(u["lead"])}</p></div>'
            f'<div class="tile-shot"><img src="{rel(slug, f"public/proof/{shot}.webp")}" alt="{e(alt)}" width="1200" '
            f'height="750" loading="lazy" decoding="async" /><span class="tile-cap">Concept demo · invented data</span>'
            f'</div></a>')
    fast = (f'<a class="tile tile-small tile-fast" href="{rel(slug, "discovery-sprint/")}"><span class="tag">We move fast'
            '</span><p class="fast-num">2–4<small> weeks</small></p><p>From the start of a Discovery Sprint to a '
            'working prototype on your own documents, with a costed build plan and a clear go/no‑go.</p>'
            '<span class="arrow">→</span></a>')
    # Row 1: big, small. Row 2: small, big — so the grid alternates like a page spread.
    return f'<div class="bento">{tiles[0]}{tiles[1]}{fast}{tiles[2]}</div>'


def approach_4s(slug):
    cards = "".join(
        f'<a class="card pillar" href="{rel(slug, s["link"])}"><span class="pillar-num">0{n}</span>'
        f'<span class="tag">{e(s["code"])} · {e(s["name"])}</span><h3>{e(s["question"])}</h3>'
        f'<p>{e(s["next"])}</p><span class="arrow">→</span></a>' for n, s in enumerate(STAGES, 1))
    return f'<div class="cards cards-4">{cards}</div>'


# Logos are recoloured to ink and cropped to their artwork; h is the display height in px, tuned per mark
# so wordmarks and square badges read at the same visual weight.
CLIENTS = [("Uber", "uber", 927, 322, 24), ("TD Bank", "td-bank", 400, 358, 36),
           ("Canada Life", "canada-life", 834, 288, 30), ("The Home Depot", "the-home-depot", 226, 226, 40),
           ("CAA", "caa", 295, 203, 32)]


def clients(slug=""):
    """Past team experience, explicitly distinguished from VisionzLab client work."""
    li = "".join(f'<li><img src="{rel(slug, f"public/clients/{f}.svg")}" alt="{e(n)}" width="{w}" height="{h}" '
                 f'style="--h: {px}px" loading="lazy" decoding="async" /></li>' for n, f, w, h, px in CLIENTS)
    return (f'<section class="clients" aria-label="Organisations our team has worked for"><div class="wrap">'
            f'<div class="clients-heading"><p>Our team’s experience</p>'
            f'<a class="link" href="{rel(slug, EXPERIENCE_SLUG)}">Explore that experience →</a></div>'
            f'<ul class="client-logos">{li}</ul></div></section>')


def cta_band(ref):
    return (f'<section class="band"><div class="wrap band-in"><div><h2>Not sure where to <span class="hl">start?</span></h2>'
            f'<p>Book a free discovery call. We\'ll look at your work together and tell you plainly '
            f'where AI would help — and where it wouldn\'t.</p></div>{contact(ref)}</div></section>')


def service_ld(slug, name, description):
    return {"@type": "Service", "@id": url(slug) + "#service", "name": name, "description": description,
            "provider": {"@id": ORG_ID}, "areaServed": ["CA", "US"], "url": url(slug)}


def rows(slug, items):
    """Editorial list: big linked rows with an arrow."""
    li = "".join(f'<a class="row" href="{rel(slug, s)}"><h3>{e(t)}</h3><p>{e(d)}</p><span class="arrow">→</span></a>'
                 for s, t, d in items)
    return f'<div class="rows">{li}</div>'


# --------------------------------------------------------------------------
# Pages
# --------------------------------------------------------------------------


def build_home():
    slug = ""
    main = f"""
<div class="first-screen">
{hero("AI that takes work off your team's plate.",
      "We build AI-assisted workflows for documents, quotes, orders and follow-up — with your team "
      "approving the decisions that matter.", "home", "AI agents & automation",
      img="hero", alt="Isometric illustration of an AI agent handling documents, email, calendar and reports",
      accent="off your team's plate.", second=("experience/", "Explore our experience"),
      stats=[("2–4 weeks", "to a working prototype"), ("1 workflow", "to start with"),
             ("Free", "first discovery session")])}
{clients()}
</div>
{finder(slug)}

<section class="section tone-paper" id="proof"><div class="wrap">
  {sec_head_split("Concept demos", "Start with one practical workflow.",
                  "Three workflows we build often, shown as concept demos with invented data. In each one the "
                  "assistant prepares the work and a person approves it.", accent="practical workflow.")}
  {proof_bento(slug)}
  {sec_foot(1, 6, "See all use cases", href="use-cases/")}
</div></section>
<section class="section tone-lime"><div class="wrap">
  <div class="split">
  <div class="frame frame-paper">{art(slug, "sprint", "Isometric illustration of a laptop prototype, a roadmap and a checklist")}</div>
  <div><p class="eyebrow">Start here</p><h2>The Discovery <span class="hl">Sprint</span></h2>
  <p class="big">A short, paid sprint on one of your workflows. In 2–4 weeks you get a working prototype, a costed
  build plan and a clear go/no-go — before you commit to anything bigger.</p></div>
  </div>
  {sec_foot(2, 6, "How the sprint works", href="discovery-sprint/")}
</div></section>
<section class="section tone-paper"><div class="wrap">
  {sec_head_split("Who we help", "Built for businesses without an AI team.",
                  "Businesses where the same paperwork lands every day: quotes, orders, renewals and month-end. "
                  "Pick yours to see the workflows we'd start with.", accent="without an AI team.")}
  {rows(slug, [(p["slug"], p["nav"], p["lead"]) for p in PLAYS])}
  {sec_foot(3, 6, "Talk to us about your business", ref="home-who")}
</div></section>
<section class="section tone-lime" id="approach"><div class="wrap">
  {sec_head_split("Our approach · the 4S", "Four stages, one workflow at a time.",
                  "We place each workflow at one of four stages, then pick the step that moves it to the next. "
                  "The 4S check tells you where yours is: eight questions, about two minutes.",
                  accent="one workflow at a time.")}
  {approach_4s(slug)}
  {sec_foot(4, 6, "Take the 4S check", href=MATURITY_SLUG + "#check", second=("services/", "Compare the five services →"))}
</div></section>
<section class="section tone-paper"><div class="wrap">
  <div class="split">
  <div><p class="eyebrow">Security Review</p><h2>Worried about <span class="hl">AI-powered attacks?</span></h2>
  <p class="big">{e(SECURITY["lead"])} A fixed-scope review of your internet-facing systems, email, cloud
  settings and the AI tools your team already uses.</p></div>
  <div class="frame">{art(slug, SECURITY["art"], SECURITY["alt"])}</div>
  </div>
  {sec_foot(5, 6, "How the security review works", href=SECURITY["slug"])}
</div></section>
<section class="section tone-lime"><div class="wrap">
  <div class="split">
  <div><p class="eyebrow">About {BRAND}</p><h2>An AI studio for businesses <span class="hl">without an AI team</span></h2></div>
  <div><p class="big">{BRAND} is an AI studio based in Ontario, Canada, working with small and mid-sized businesses
  across Canada and the US. We teach teams to run their own agents, build agents with them, or build and run them
  for you, always with your people approving the decisions that matter.</p></div>
  </div>
  {sec_foot(6, 6, "About " + BRAND, href="about/", second=(GUIDES_SLUG, "Read our guides →"))}
</div></section>
<section class="section"><div class="wrap">{faq_html(FAQ_HOME)}</div></section>
{cta_band("home-band")}"""
    return page(slug, "AI Agents & Automation for Small Businesses",
                ORG["description"], main, ld=[faq_ld(FAQ_HOME)], ref="home")


def build_services():
    slug = "services/"
    desc = ("Five ways to put AI to work: AI training, guided agent setup, custom AI development, "
            "a managed AI employee, or an AI engineering team instead of a hire.")
    main = f"""
{hero("Five ways to work with us", "From teaching your team to building and running it for you. "
      "Pick the level of help that fits — and change it as you go.", "services", "Services", slug=slug,
      accent="work with us")}
<section class="section"><div class="wrap">{section_head("At a glance", "The five services", intro=(
    "AI Training teaches your team; AI Agent Setup configures agents with you; AI Development builds a custom "
    "agent you own; an AI Employee is built and run for you for a monthly fee; an AI Team gives you engineering "
    "capacity instead of a hire. The usual first step is a Discovery Sprint."), accent="services")}{ladder(slug)}</div></section>
<section class="section tone-paper"><div class="wrap split">
  <div><p class="eyebrow">Also</p><h2>{e(SECURITY["nav"])}</h2><p class="big">{e(SECURITY["lead"])}</p>
  <a class="link" href="{rel(slug, SECURITY["slug"])}">How the security review works →</a></div>
  <div class="frame">{art(slug, SECURITY["art"], SECURITY["alt"])}</div>
</div></section>
<section class="section tone-lime"><div class="wrap split">
  <div>{section_head("Pricing", "How pricing works", intro=PRICING_SUMMARY, accent="pricing")}</div>
  <div class="panel"><ul class="ticks"><li><strong>Discovery session:</strong> free, with a short memo afterwards</li>
  <li><strong>Discovery Sprint:</strong> a fixed fee agreed before it starts</li>{"".join(
      f'<li><strong>{e(t["nav"])}:</strong> {e(t["priced"][0].lower() + t["priced"][1:].rstrip("."))}</li>' for t in TIERS + [SECURITY])}</ul></div>
</div></section>
<section class="section"><div class="wrap narrow prose big"><h2>Who we work with</h2><p>{e(WHO_WE_SERVE)}</p></div></section>
{cta_band("services-band")}"""
    return page(slug, "AI Agent & Automation Services", desc, main, ref="services")


def build_tier(i):
    t = TIERS[i]
    slug = t["slug"]
    get = "".join(f"<li>{e(x)}</li>" for x in t["get"])
    how = "".join(f'<li><strong>{e(a)}</strong><span>{e(b)}</span></li>' for a, b in t["how"])
    nxt = ""
    if t["next"]:
        n = next(x for x in TIERS if x["slug"] == t["next"])
        nxt = f'<p class="more"><a class="link" href="{rel(slug, n["slug"])}">Need more? See {e(n["nav"])} →</a></p>'
    ref = slug.split("/")[1]
    main = f"""
{hero(t["title"], t["lead"], ref, f'Service 0{i + 1} · {t["tier"]}', slug=slug, img=t["art"],
      alt=f'Isometric illustration for {t["nav"]}')}
<section class="section tone-lime"><div class="wrap split">
  <div class="panel"><h2>Who it's for</h2><p class="big">{e(t["for"])}</p><h2>What you get</h2><ul class="ticks">{get}</ul><h2>How it's priced</h2><p class="big">{e(t["priced"])}</p>{nxt}</div>
  <div class="panel"><h2>How it works</h2><ol class="steps">{how}</ol></div>
</div></section>
<section class="section"><div class="wrap">{faq_html(t["faq"])}</div></section>
<section class="section tone-lime"><div class="wrap">{section_head("All services", "Five ways to work with us", accent="work with us")}{ladder(slug, highlight=slug)}</div></section>
{cta_band(ref + "-band")}"""
    return page(slug, t["title"], t["description"], main,
                ld=[service_ld(slug, t["title"], t["description"]), faq_ld(t["faq"])], ref=ref)


def build_security():
    s = SECURITY
    slug = s["slug"]
    faq = [s["question"]] + s["faq"]
    checks = "".join(f'<li><strong>{e(a)}</strong><span>{e(b)}</span></li>' for a, b in s["checks"])
    get = "".join(f"<li>{e(x)}</li>" for x in s["get"])
    how = "".join(f'<li><strong>{e(a)}</strong><span>{e(b)}</span></li>' for a, b in s["how"])
    main = f"""
{hero(s["title"], s["lead"], s["ref"], f'Service · {s["tier"]}', slug=slug, img=s["art"], alt=s["alt"])}
{answer_first(s["question"])}
<section class="section tone-lime"><div class="wrap narrow prose big">
  <h2>Why now</h2>
  <p>AI has made it cheaper to find software flaws and quicker to exploit them, and phishing emails now read like
  they came from a colleague. Large companies have security teams to keep up. Most small businesses have an IT
  person, a provider, or nobody.</p>
  <p>The good news is that most breaches still start with a short list of basics. A review that checks those
  properly, and a plan to fix them in order, removes most of the easy ways in.</p>
</div></section>
<section class="section"><div class="wrap split">
  <div class="panel"><h2>What we check</h2><ol class="steps">{checks}</ol></div>
  <div class="panel"><h2>Who it's for</h2><p class="big">{e(s["for"])}</p><h2>What you get</h2><ul class="ticks">{get}</ul>
  <h2>How it's priced</h2><p class="big">{e(s["priced"])}</p></div>
</div></section>
<section class="section tone-lime"><div class="wrap split">
  <div class="panel"><h2>How it works</h2><ol class="steps">{how}</ol></div>
  <div class="panel"><h2>What stays with people</h2><ul class="ticks">
  <li>A senior engineer reviews every finding before you see it</li>
  <li>Nothing changes on your systems without your approval</li>
  <li>Your team or IT provider stays in charge of your systems; we work alongside them</li>
  <li>We tell you plainly when you need a specialist we're not, such as a formal penetration test or an
  incident response firm</li></ul>
  <p class="more"><a class="link" href="{rel(slug, EXPERIENCE_SLUG)}">Our security and privacy background →</a></p></div>
</div></section>
{faq_section(s["faq"])}
<section class="section tone-lime"><div class="wrap">{section_head("AI services", "Five ways to put AI to work", accent="put AI to work")}{ladder(slug)}</div></section>
{cta_band(s["ref"] + "-band")}"""
    return page(slug, s["title"], s["description"], main,
                ld=[service_ld(slug, s["title"], s["description"]), faq_ld(faq)], ref=s["ref"])


def check_questions():
    """Every use case and industry page leads with the question a buyer would type into an AI engine.
    _analytics/scripts/prompts-from-site.py reads it back from FAQPage to keep the answer-share probe in sync."""
    for x in USE_CASES + PLAYS:
        q, a = x.get("question") or (None, None)
        assert q and q.endswith("?") and len(q) > 25 and a, f'{x["slug"]}: add "question": (buyer question, answer)'


def build_play(p):
    slug = p["slug"]
    body = "".join(f"<p>{e(x)}</p>" for x in p["body"])
    if p.get("guide"):
        g = next(x for x in GUIDES if x["slug"] == p["guide"])
        body += (f'<p><a class="link" href="{rel(slug, g["slug"])}">Read the {e(g.get("eyebrow", "guide").lower())}: '
                 f'{e(g["title"])} →</a></p>')
    moments = "".join(f'<div class="panel"><h2>{e(h)}</h2>{"".join(f"<p>{e(x)}</p>" for x in ps)}</div>'
                      for h, ps in p.get("moments", []))
    moments = f'<div class="wrap split moments">{moments}</div>' if moments else ""
    uses = ""
    if p.get("uses"):
        assert set(p["uses"]) <= {u["slug"] for u in USE_CASES}, f'unknown use case in {slug}: {p["uses"]}'
        uses = (f'<section class="section tone-lime"><div class="wrap">'
                f'{section_head("Use cases", "What we usually build first", accent="build first")}'
                f'{use_case_cards(slug, only=p["uses"])}</div></section>')
    main = f"""
{hero(p["title"], p["lead"], p["ref"], "Who we help", slug=slug, img=p["art"], alt=f'Isometric illustration for {p["nav"]}')}
{answer_first(p["question"])}
<section class="section tone-lime"><div class="wrap narrow prose big">{body}</div>{moments}</section>
<section class="section"><div class="wrap">{section_head("Where to start", "A recommended starting point", accent="starting point")}{ladder(slug, only=p["tiers"])}
<p class="more"><a class="link" href="{rel(slug, 'services/')}">See all five services →</a></p></div></section>
{uses}
{faq_section(p.get("faq", []))}
{cta_band(p["ref"] + "-band")}"""
    return page(slug, p["title"], p["description"], main, ld=[faq_ld([p["question"]] + p.get("faq", []))],
                ref=p["ref"])


def use_case_cards(slug, exclude=None, only=None):
    cards = "".join(
        f'<a class="card" href="{rel(slug, u["slug"])}"><span class="tag">Use case</span>'
        f'<h3>{e(u["nav"])}</h3><p>{e(u["lead"])}</p><span class="arrow">→</span></a>'
        for u in USE_CASES if u["slug"] != exclude and (only is None or u["slug"] in only))
    return f'<div class="cards cards-uc">{cards}</div>'


def build_use_cases():
    slug = "use-cases/"
    desc = ("AI agents for operations, sales and finance teams: RFQ and order intake, document intake, inbox "
            "triage, renewals, research, planning and financial reporting.")
    main = f"""
{hero("AI agents for operations, growth and finance teams", "Agents that do the reading, re-keying, tracking "
      "and reporting — so your people can spend their time on the decisions.", "use-cases",
      "Use cases", slug=slug, tone="lime", task=("#list", "Browse the use cases"))}
<section class="section" id="list"><div class="wrap">{section_head("Use cases", f"{len(USE_CASES)} workflows we build agents for", intro=(
    "Each one is a repetitive workflow where an agent reads, drafts or reconciles, and a person approves "
    "anything that reaches a customer, a supplier or the books."), accent="build agents for")}{use_case_cards(slug)}
<p class="more">Every use case can be taught, set up with you, built, or built and run for you.
<a class="link" href="{rel(slug, 'services/')}">See the five ways to work with us →</a></p></div></section>
{cta_band("use-cases-band")}"""
    return page(slug, "AI Agent Use Cases", desc, main, ref="use-cases")


def build_use_case(u):
    slug = u["slug"]
    does = "".join(f"<li>{e(x)}</li>" for x in u["does"])
    ref = "uc-" + slug.split("/")[1]
    main = f"""
{hero(u["title"], u["lead"], ref, "Use case", slug=slug, tone="lime")}
{answer_first(u["question"])}
<section class="section"><div class="wrap split">
  <div><h2>Who it's for</h2><p class="big">{e(u["for"])}</p><h2>What the agent does</h2><ul class="ticks">{does}</ul></div>
  <div class="panel panel-lime"><h2>What stays with your people</h2><p class="big">{e(u["people"])}</p></div>
</div></section>
<section class="section tone-lime"><div class="wrap">{section_head("How to get it", "Pick the level of help that fits", accent="that fits")}{ladder(slug, only=u["tiers"])}</div></section>
{faq_section(u["faq"])}
<section class="section tone-lime"><div class="wrap">{section_head("More", "More use cases", accent="use cases")}{use_case_cards(slug, exclude=slug)}</div></section>
{cta_band(ref + "-band")}"""
    return page(slug, u["title"], u["description"], main,
                ld=[service_ld(slug, u["title"], u["description"]), faq_ld([u["question"]] + u["faq"])], ref=ref)


def build_sprint():
    slug = "discovery-sprint/"
    desc = ("A short, paid AI discovery sprint on one workflow: a working prototype, a costed build plan "
            "and a clear go/no-go in 2–4 weeks.")
    steps = [("Free discovery call", "A 60–90 minute conversation about your work, followed by a short memo "
              "with what we'd look at first."),
             ("Sprint kickoff", "We agree one workflow, the success measure, and access to what we need."),
             ("Prototype", "We build a working prototype on your real process."),
             ("Plan and decision", "You get a costed build plan and our honest go/no-go recommendation.")]
    how = "".join(f'<li><strong>{e(a)}</strong><span>{e(b)}</span></li>' for a, b in steps)
    main = f"""
{hero("The Discovery Sprint", "One workflow. Two to four weeks. A working prototype, a costed build plan "
      "and a clear go/no-go — before you commit to anything bigger.", "sprint", "Start here", slug=slug,
      img="sprint", alt="Isometric illustration of a laptop prototype, a roadmap and a checklist", accent="Sprint",
      second=(MATURITY_SLUG, "Not sure? Take the 4S check"))}
<section class="section tone-lime"><div class="wrap split">
  <div class="panel"><h2>What you walk away with</h2><ul class="ticks">
    <li>A working prototype on your own process</li>
    <li>A success measure we agree at kickoff and check on your own documents</li>
    <li>A costed, phased build plan, including what your team would need to run it</li>
    <li>A clear go/no-go, with the reasons</li><li>A view of the risks and what would need to be true</li></ul></div>
  <div class="panel"><h2>How it works</h2><ol class="steps">{how}</ol></div>
</div></section>
<section class="section"><div class="wrap">{faq_html(FAQ_SPRINT)}</div></section>
<section class="section tone-lime"><div class="wrap">{section_head("After the sprint", "Build it yourselves, or pick the help that fits", accent="the help that fits")}{ladder(slug, only=[0, 2, 3, 4])}</div></section>
{cta_band("sprint-band")}"""
    return page(slug, "AI Discovery Sprint", desc, main,
                ld=[service_ld(slug, "AI Discovery Sprint", desc), faq_ld(FAQ_SPRINT)], ref="sprint")


def stage_cards(slug):
    cards = "".join(
        f'<a class="card" href="{rel(slug, MATURITY_SLUG)}#{s["code"].lower()}"><span class="num">{s["code"]}</span>'
        f'<span class="tag">{e(s["question"])}</span><h3>{e(s["name"])}</h3><p>{e(s["here"])}</p>'
        f'<span class="arrow">→</span></a>' for s in STAGES)
    return f'<div class="cards cards-4">{cards}</div>'


MATURITY_JS = """      (function () {
        // First unticked box decides the stage (two boxes per stage); a tick after it means a skipped stage.
        var form = document.getElementById('check-form');
        form.addEventListener('submit', function (ev) {
          ev.preventDefault();
          var boxes = Array.prototype.slice.call(form.querySelectorAll('input[type=checkbox]'));
          var first = boxes.findIndex(function (b) { return !b.checked; });
          var stage = first < 0 ? boxes.length / 2 : Math.floor(first / 2);
          var skipped = first >= 0 && boxes.slice(first).some(function (b) { return b.checked; });
          document.querySelectorAll('[data-result]').forEach(function (el) {
            el.hidden = Number(el.getAttribute('data-result')) !== stage;
          });
          document.getElementById('check-skip').hidden = !skipped;
          var out = document.getElementById('check-result');
          out.hidden = false;
          out.scrollIntoView({ behavior: 'smooth', block: 'start' });
          if (window.umami && typeof window.umami.track === 'function') {
            try { window.umami.track('maturity_result', { stage: String(stage + 1), skipped: skipped }); } catch (_) {}
          }
        });
      })();"""


def build_maturity():
    slug = MATURITY_SLUG
    desc = ("The 4S check: where is your business with AI? Eight yes-or-no questions place one workflow at "
            "Strategy, Solution, Scale or Sustain, and show the next step.")
    tiers = {t["slug"]: t["nav"] for t in TIERS}

    def label(target):
        if target == "discovery-sprint/":
            return "How the Discovery Sprint works"
        return f'See {tiers[target]}'  # KeyError on an unknown target: fail the build, don't mislabel

    def heading(stage):
        return stage["name"] if stage is PAST_S4 else f'{stage["code"]} {stage["name"]}'

    stages = "".join(
        f'<div class="card" id="{s["code"].lower()}"><span class="num">{s["code"]}</span>'
        f'<span class="tag">{e(s["question"])}</span><h3>{e(s["name"])}</h3>'
        f'<p><strong>You\'re here if:</strong> {e(s["here"])}</p>'
        f'<p><strong>What helps next:</strong> {e(s["next"])}</p>'
        f'<a class="link" href="{rel(slug, s["link"])}">{e(label(s["link"]))} →</a></div>' for s in STAGES)
    questions = [(s, text) for s in STAGES for text in s["checks"]]
    checks = "".join(
        f'<label><input type="checkbox" name="q{n}" /><span><span class="tag">{s["code"]} '
        f'{e(s["name"])}</span>{e(text)}</span></label>' for n, (s, text) in enumerate(questions, 1))
    results = "".join(
        f'<div data-result="{i}" hidden><p class="eyebrow">Your stage</p>'
        f'<h3>{e(heading(s))}</h3><p class="big">{e(s["here"])}</p>'
        f'<p class="big"><strong>What helps next:</strong> {e(s["next"])}</p>'
        f'<div class="actions">{contact("maturity-" + s["code"].lower(), "Talk it through with us")}'
        f'<a class="btn btn-ghost" href="{rel(slug, s["link"])}">{e(label(s["link"]))}</a></div></div>'
        for i, s in enumerate(STAGES + [PAST_S4]))
    main = f"""
{hero("Where is your business with AI?", "The 4S check: four stages, eight yes-or-no questions, about two minutes. "
      "It shows where you are on one piece of work, and the one step that moves you forward.", "maturity",
      "The 4S check", slug=slug, img="lab", alt="Isometric illustration of a small AI studio workspace",
      accent="with AI?", task=("#check", "Take the check"))}
<section class="section tone-lime"><div class="wrap">
  {section_head("Four stages", "Strategy, Solution, Scale, Sustain",
                "Each stage answers one question, and each depends on the one before.", accent="Sustain")}
  <div class="cards cards-4">{stages}</div>
</div></section>
<section class="section"><div class="wrap narrow prose big">
  <h2>Why the order <span class="hl">matters</span></h2>
  <p>A tool bought before anyone chose the work. A pilot nobody measured. An automation that one person set up and
  nobody looks after. Each is a skipped stage, and a skipped stage is where AI projects stall.</p>
  <p>So the check looks for the first gap, not the most advanced thing you've tried. Close that gap and the next
  stage gets much easier.</p>
</div></section>
<section class="section tone-lime" id="check"><div class="wrap narrow">
  {section_head("Take the check", "Pick one piece of work.", "Think of the work you'd most like AI to help with. "
                "Tick each statement that's true for it today. If it's only partly true, leave it unticked.",
                accent="one piece of work.")}
  <form class="panel check" id="check-form">{checks}
    <div class="actions"><button class="btn btn-ink" type="submit">See where you are</button></div>
    <noscript><p class="muted">Your stage is the first statement you left unticked: statements 1–2 are Strategy,
    3–4 Solution, 5–6 Scale and 7–8 Sustain. All ticked means that work is past stage four.</p></noscript>
  </form>
  <div class="panel result" id="check-result" hidden>
    <p class="skip" id="check-skip" hidden>You ticked a later statement but not an earlier one. That usually means
    a stage was skipped, and it's the first thing to fix.</p>
    {results}
  </div>
</div></section>
<section class="section"><div class="wrap">{faq_html(FAQ_MATURITY)}</div></section>
{cta_band("maturity-band")}
<script>
{MATURITY_JS}
</script>"""
    return page(slug, "The 4S Check: Where Is Your Business With AI?", desc, main, ld=[faq_ld(FAQ_MATURITY)],
                ref="maturity")


def build_about():
    slug = "about/"
    desc = ("VisionzLab is an AI studio that helps small and mid-sized businesses put AI agents to work, "
            "with senior architects and an AI-first way of building.")
    principles = [("Senior people", "Architects with more than two decades of software and architecture experience, "
                   "who have shipped production AI systems."),
                  ("AI-first delivery", "We build with AI ourselves, so small projects stay small and larger ones move fast."),
                  ("People stay in charge", "Approval steps, audit trails and clear limits on what an agent may do are "
                   "part of every build."),
                  ("Honest scoping", "Fixed prices where the scope is clear, and a plain answer when AI isn't the right tool.")]
    cards = "".join(f'<div class="card card-static"><span class="num">0{i + 1}</span><h3>{e(a)}</h3><p>{e(b)}</p></div>'
                    for i, (a, b) in enumerate(principles))
    main = f"""
{hero("About VisionzLab", "We help businesses without an AI team put AI to work — practically, "
      "safely, and at a size that makes sense for them.", "about", "About", slug=slug, img="lab",
      alt="Isometric illustration of a small AI studio workspace", accent="VisionzLab")}
<section class="section tone-lime"><div class="wrap narrow prose big">
  <h2>What we believe</h2>
  <p>Most businesses don't need an AI strategy. They need specific work taken off their team's plate, by
  something they can trust and understand.</p>
  <p>So we meet clients where they are. Some want to learn to do it themselves. Some want it built.
  Some want it built and looked after. We're comfortable with all three, and we'd rather start small
  and earn the next project than sell something too big.</p>
</div></section>
<section class="section"><div class="wrap">{section_head("How we work", "Four things we hold to", accent="hold to")}
<div class="cards cards-uc">{cards}</div>
<p class="more"><a class="link" href="{rel(slug, EXPERIENCE_SLUG)}">See what our team has built →</a></p></div></section>
<section class="section tone-lime"><div class="wrap split">
  <div><h2>Where we work</h2><p class="big">We're based in Ontario, Canada, and work with businesses across Canada and
  the United States, online or on site.</p></div>
  <div><h2>Who you'll talk to</h2><p class="big">Every engagement starts with our business development lead, and
  every build is led by our founder.</p>
  <div class="actions"><a class="btn btn-ink" href="{rel(slug, ASAL['slug'])}">Meet our VP of Business Development →</a>
  <a class="btn" href="{rel(slug, FRANK['slug'])}">Meet our founder →</a></div></div>
</div></section>
{cta_band("about-band")}"""
    return page(slug, "About", desc, main, ref="about")


def build_experience():
    slug = EXPERIENCE_SLUG
    desc = ("The experience behind VisionzLab: AI systems and software our team built before VisionzLab, "
            "and how we earn trust before we have case studies of our own.")
    labels = [("work", "The work"), ("built", "What was built"), ("outcome", "The outcome")]
    cards = "".join(
        f'<article class="card card-static proof"><span class="tag">{e(x["tag"])}</span><h3>{e(x["title"])}</h3>'
        f'<dl>{"".join(f"<dt>{e(n)}</dt><dd>{e(x[k])}</dd>" for k, n in labels)}</dl></article>'
        for x in EXPERIENCE)
    trust = "".join(f'<div class="card card-static"><span class="num">0{i + 1}</span><h3>{e(a)}</h3><p>{e(b)}</p></div>'
                    for i, (a, b) in enumerate(TRUST))
    main = f"""
{hero("What our team has built", "VisionzLab is a new practice, so this page is about the people. Before "
      "VisionzLab, our team spent more than twenty years building production software for large enterprises and "
      "startups, the last four of them building production AI systems.", "experience", "Our experience",
      slug=slug, img="build", alt="Isometric illustration of an AI system being assembled", accent="has built",
      second=(FRANK["slug"], "Meet our founder"))}
<section class="section tone-lime"><div class="wrap">
  {section_head("Before VisionzLab", "Experience behind the work", f"{NUM_WORDS[len(EXPERIENCE)]} examples from roles our founder held before "
                "VisionzLab. Most of the organisations appear on our homepage and on his page.",
                accent="the work")}
  <div class="cards cards-2">{cards}</div>
</div></section>
<section class="section"><div class="wrap split">
  <div><h2>Our own case studies are <span class="hl">coming</span></h2>
  <p class="big">VisionzLab doesn't have client case studies of its own yet, and we won't borrow anyone else's.
  As our engagements complete, we'll add them here, with each client's permission and with results measured on
  their own work.</p></div>
  <div class="panel panel-lime"><h2>Until then</h2><p class="big">Test us on your own work. A Discovery Sprint gives
  you a working prototype and a clear go/no-go in two to four weeks.</p>
  <div class="actions"><a class="btn btn-ink" href="{rel(slug, 'discovery-sprint/')}">How the sprint works →</a></div></div>
</div></section>
<section class="section tone-lime"><div class="wrap">
  {section_head("How we work", "What you can hold us to", accent="hold us to")}
  <div class="cards cards-4">{trust}</div>
</div></section>
<section class="section"><div class="wrap">{faq_html(FAQ_EXPERIENCE)}</div></section>
{cta_band("experience-band")}"""
    return page(slug, "Our Team's Experience", desc, main, ld=[faq_ld(FAQ_EXPERIENCE)], ref="experience")


def build_person(m):
    slug, name, role, photo = m["slug"], m["name"], m["role"], m["photo"]
    canonical = url(slug)
    person = {"@type": "Person", "@id": canonical + "#person", "name": name, "jobTitle": role,
              "email": f"mailto:{m['email']}", "worksFor": {"@id": ORG_ID},
              "image": f"{SITE}/public/team/{photo}.jpg", "url": canonical}
    profile = {"@type": "ProfilePage", "@id": canonical + "#page", "url": canonical, "name": f"{name}, {role}",
               "mainEntity": {"@id": person["@id"]}}
    lead, *rest = m["bio"]
    body = "".join(f'<p class="big">{e(t)}</p>' for t in rest)
    ref = photo
    main = f"""
<section class="hero tone-paper"><div class="wrap hero-split person">
  <div class="hero-copy">
    <p class="eyebrow">{e(role)}</p>
    <h1>{e(name)}</h1>
    <p class="lead">{e(lead)}</p>
    {body}
    <div class="actions">{contact(ref, inner=f'Book a free discovery call <span class="btn-sub">with {e(m["first"])}</span>')}
      <a class="btn btn-ghost" href="mailto:{m['email']}">{m['email']}</a></div>
  </div>
  <div class="frame frame-photo"><picture><source srcset="{rel(slug, f'public/team/{photo}.webp')}" type="image/webp" />
  <img src="{rel(slug, f'public/team/{photo}.jpg')}" alt="{e(name)}, {e(role)} at {BRAND}" width="720" height="900" fetchpriority="high" /></picture></div>
</div></section>
{cta_band(f"{ref}-band")}"""
    return page(slug, f"{name}, {role}", m["description"], main, ld=[person, profile], ref=ref,
                image=f"public/team/{photo}.jpg", og_type="profile")


BOOK_JS = """      (function () {
        // Lead source: #ref= from a site button, else ?ref= from an email or ad link, else what the
        // visitor arrived with earlier in the visit. HubSpot fills the hidden vzl_ref field from ?vzl_ref=.
        var q = new URLSearchParams(location.search);
        var h = new URLSearchParams(location.hash.slice(1));
        var stored = null;
        try { stored = sessionStorage.getItem('vz_ref'); } catch (_) {}
        var ref = h.get('ref') || q.get('ref') || stored || 'direct';
        if (q.get('ref') && h.get('ref')) ref = q.get('ref') + '~' + h.get('ref');
        q.set('vzl_ref', ref);
        history.replaceState(null, '', location.pathname + '?' + q.toString());
        var s = document.createElement('script');
        s.src = 'https://js-__REGION__.hsforms.net/forms/embed/__PORTAL__.js';
        s.defer = true;
        s.onerror = function () { document.getElementById('hs-form-fallback').hidden = false; };
        document.head.appendChild(s);
        // The embed dispatches this on the form container and it bubbles (checked in its script, 2026-10-20).
        // HubSpot Meetings: prefill name and email from the submitted form, then load the embed script, which
        // reads data-src from the container. Prefill is a convenience; the scheduler works without it.
        function showMeetings(meet, ev) {
          var load = function (vals) {
            var u = new URL(meet.getAttribute('data-src'));
            u.searchParams.set('embed', 'true');
            ['firstName', 'lastName', 'email'].forEach(function (k) { if (vals[k]) u.searchParams.set(k, vals[k]); });
            meet.setAttribute('data-src', u.toString());
            var m = document.createElement('script');
            m.src = 'https://static.hsappstatic.net/MeetingsEmbed/ex/MeetingsEmbedCode.js';
            document.body.appendChild(m);
          };
          try {
            var form = window.HubSpotFormsV4.getFormFromEvent(ev);
            Promise.resolve(form.getFormFieldValues()).then(function (fields) {
              var map = { '0-1/firstname': 'firstName', '0-1/lastname': 'lastName', '0-1/email': 'email' };
              var vals = {};
              (fields || []).forEach(function (f) { if (map[f.name]) vals[map[f.name]] = f.value; });
              load(vals);
            }, function () { load({}); });
          } catch (_) { load({}); }
        }
        document.addEventListener('hs-form-event:on-submission:success', function (ev) {
          var shown = false;
          // After the request goes in, show the appointment calendar so the visitor can book a time at once.
          // The iframe only loads now, so visitors who never submit don't load Google Calendar.
          var box = document.getElementById('pick-a-time');
          if (box && box.hidden) {
            var frame = box.querySelector('iframe');
            var meet = box.querySelector('.meetings-iframe-container');
            if (frame) frame.src = frame.getAttribute('data-src');
            if (meet) showMeetings(meet, ev);
            box.hidden = false;
            shown = true;
            setTimeout(function () { box.scrollIntoView({ behavior: 'smooth', block: 'start' }); }, 300);
          }
          if (window.umami && typeof window.umami.track === 'function') {
            try {
              window.umami.track('booking_submitted', { ref: ref });
              if (shown) window.umami.track('booking_calendar_shown', { ref: ref });
            } catch (_) {}
          }
        });
      })();"""


def build_book():
    slug = BOOK_SLUG
    desc = ("Book a free discovery call with VisionzLab. Tell us a little about your business and "
            "we'll find a time to talk.")
    js = BOOK_JS.replace("__REGION__", HUBSPOT_REGION).replace("__PORTAL__", HUBSPOT_PORTAL_ID)
    if HUBSPOT_MEETINGS_URL:
        picker = f"""<div class="meetings-iframe-container book-meetings" data-src="{HUBSPOT_MEETINGS_URL}"></div>
  <p class="muted small">Scheduler not showing? <a class="link" href="{HUBSPOT_MEETINGS_URL}"
    target="_blank" rel="noopener">Open it in a new tab</a>.</p>"""
    elif BOOKING_CALENDAR_URL:
        picker = f"""<iframe class="book-calendar" title="Pick a time for your discovery session"
    data-src="{BOOKING_CALENDAR_URL}" loading="lazy"></iframe>
  <p class="muted small">Calendar not showing? <a class="link" href="{BOOKING_CALENDAR_URL.split('?')[0]}"
    target="_blank" rel="noopener">Open it in a new tab</a>.</p>"""
    else:
        picker = ""
    if picker:
        book_next = ("Send the form, then pick a time from the calendar that appears, and the session is booked. "
                     "If none of the times suit you, we'll reply within one business day to find one.")
        calendar = f"""
<section class="tone-paper book-time" id="pick-a-time" hidden><div class="wrap">
  <h2>Thanks. Now pick a time.</h2>
  <p class="lead">Choose a slot and the session is booked: the invitation and Google Meet link arrive by email.
  If none of these times suit you, skip this step and we'll reply within one business day.</p>
  {picker}
</div></section>"""
    else:
        book_next = ("Send a request and we'll reply within one business day to arrange a time. "
                     "This form does not reserve an appointment.")
        calendar = ""
    main = f"""
<section class="hero tone-paper"><div class="wrap hero-split">
  <div class="hero-copy">
    <p class="eyebrow">Free discovery call</p>
    <h1>{headline("Let's talk about your work.", "your work.")}</h1>
    <p class="lead">A 60–90 minute conversation about where AI could take work off your team, and where it
    shouldn't. No preparation needed, and no obligation.</p>
    <p class="big">{book_next}</p>
    <h2 class="call-heading">What we'll cover</h2>
    <ul class="ticks"><li>The workflow taking up your team's time</li>
      <li>Where AI could help and where people should stay in control</li>
      <li>Whether a Discovery Sprint is a useful next step</li></ul>
    <p>Prefer email? <a class="link" href="mailto:{EMAIL_SALES}">{EMAIL_SALES}</a></p>
  </div>
  <div class="panel book-form">
    <div class="hs-form-frame" data-region="{HUBSPOT_REGION}" data-form-id="{HUBSPOT_FORM_ID}"
      data-portal-id="{HUBSPOT_PORTAL_ID}"></div>
    <p id="hs-form-fallback" hidden>The form didn't load. Email <a href="mailto:{EMAIL_SALES}">{EMAIL_SALES}</a>
    and we'll set up a time.</p>
    <noscript><p>Email <a href="mailto:{EMAIL_SALES}">{EMAIL_SALES}</a> and we'll set up a time.</p></noscript>
    <p class="muted small">We use these details only to reply to you and arrange the call.</p>
  </div>
</div></section>{calendar}
<script>
{js}
</script>"""
    return page(slug, "Book a free discovery call", desc, main, ref="book")


def page_title(slug):
    """Short name and lead for any finder target, from the content that owns it."""
    for u in USE_CASES:
        if u["slug"] == slug:
            return u["nav"], u["lead"]
    for t in TIERS + [SECURITY]:
        if t["slug"] == slug:
            return t["nav"], t["lead"]
    for p in PLAYS:
        if p["slug"] == slug:
            return p["nav"], p["lead"]
    raise KeyError(slug)  # a finder target with no page: fail the build


FINDER_JS = """      (function () {
        // Matches what the visitor typed against keyword lists, in the browser. The text is never sent anywhere;
        // analytics records only which page matched.
        var root = document.getElementById('finder');
        var data = JSON.parse(document.getElementById('finder-data').textContent);
        var input = root.querySelector('input');
        var out = root.querySelector('.finder-out');
        var cta = root.querySelector('[data-finder-cta]');
        var base = cta.href.split('#')[0];
        function show(ev) {
          if (ev) ev.preventDefault();
          // Keywords match at the start of a word ("reconcil" finds "reconciling"; "chase" doesn't match
          // "purchase"); keywords of three letters or fewer ("po", "erp") must be the whole word.
          var text = ' ' + input.value.toLowerCase().replace(/[^a-z0-9-]+/g, ' ') + ' ';
          var hits = data.map(function (d) {
            var score = d.k.filter(function (k) {
              return text.indexOf(' ' + k + (k.length <= 3 ? ' ' : '')) >= 0;
            }).length;
            return { d: d, score: score };
          }).filter(function (h) { return h.score > 0; })
            .sort(function (a, b) { return b.score - a.score; }).slice(0, 3);
          var list = out.querySelector('.finder-hits');
          list.innerHTML = '';
          hits.forEach(function (h) {
            var a = document.createElement('a');
            a.className = 'card'; a.href = h.d.u;
            a.innerHTML = '<span class="tag">Start here</span><h3></h3><p></p><span class="arrow">→</span>';
            a.querySelector('h3').textContent = h.d.n; a.querySelector('p').textContent = h.d.l;
            list.appendChild(a);
          });
          out.querySelector('[data-none]').hidden = hits.length > 0;
          out.hidden = false;
          var match = hits.length ? h0(hits) : 'none';
          var stored = null;
          try { stored = sessionStorage.getItem('vz_ref'); } catch (_) {}
          var ref = 'finder-' + match;
          cta.href = base + '#ref=' + encodeURIComponent(stored ? stored + '~' + ref : ref);
          if (window.umami && typeof window.umami.track === 'function') {
            try { window.umami.track('finder_used', { match: match }); } catch (_) {}
          }
        }
        function h0(hits) { return hits[0].d.u.split('/').filter(Boolean).pop(); }
        root.querySelector('form').addEventListener('submit', show);
        root.querySelectorAll('[data-example]').forEach(function (b) {
          b.addEventListener('click', function () { input.value = b.textContent; show(); });
        });
      })();"""


def finder(slug, tone="paper"):
    data = [{"u": rel(slug, s), "n": page_title(s)[0], "l": page_title(s)[1], "k": k} for s, k in FINDER.items()]
    blob = json.dumps(data).replace("</", "<\\/")
    chips = "".join(f'<button type="button" class="chip" data-example>{e(x)}</button>' for x in FINDER_EXAMPLES)
    return f"""<section class="section tone-{tone}" id="finder"><div class="wrap narrow">
  {section_head("Workflow finder", "What's taking your team's time?",
                "Describe the task in a few words. We'll point you to the closest thing we build. Nothing you type "
                "leaves your browser.", accent="your team's time?")}
  <form class="panel finder" role="search" aria-label="Workflow finder">
    <label for="finder-q-{slug.count('/')}" class="tag">The work you'd like off your plate</label>
    <div class="finder-row"><input id="finder-q-{slug.count('/')}" type="text" maxlength="200" autocomplete="off"
      placeholder="e.g. typing purchase orders from email into our ERP" />
      <button class="btn btn-ink" type="submit">Find it</button></div>
    <div class="chips"><span class="muted small">Try:</span>{chips}</div>
  </form>
  <div class="finder-out" hidden><div class="cards cards-uc finder-hits"></div>
    <p class="big" data-none hidden>We don't have a page for that yet, which doesn't mean we can't help.
    Tell us about it.</p>
    <div class="actions">{contact("finder", "Book a free discovery call").replace("<a ", "<a data-finder-cta ", 1)}
    <a class="btn btn-ghost" href="{rel(slug, CALC_SLUG)}">Estimate the hours it takes</a></div></div>
  <script type="application/json" id="finder-data">{blob}</script>
</div></section>
<script>
{FINDER_JS}
</script>"""


CALC_JS = """      (function () {
        var form = document.getElementById('calc');
        function num(name) { var v = parseFloat(form.elements[name].value); return isFinite(v) && v > 0 ? v : 0; }
        function fmt(n) { return Math.round(n).toLocaleString(); }
        var tracked = false;
        function run(ev) {
          if (ev) ev.preventDefault();
          var weekly = num('items') * num('minutes') / 60;
          var yearly = weekly * num('weeks');
          var back = yearly * num('share') / 100;
          var rate = num('rate');
          document.getElementById('share-out').textContent = num('share') + '%';
          document.getElementById('r-weekly').textContent = fmt(weekly);
          document.getElementById('r-yearly').textContent = fmt(yearly);
          document.getElementById('r-back').textContent = fmt(back);
          document.getElementById('r-weeks').textContent = (back / 37.5).toFixed(1);
          var money = document.getElementById('r-money-row');
          money.hidden = !rate;
          document.getElementById('r-money').textContent = fmt(back * rate);
          if (ev && ev.type === 'submit' && !tracked && window.umami && typeof window.umami.track === 'function') {
            tracked = true;
            try { window.umami.track('calculator_used', { bucket: back < 100 ? '<100' : back < 500 ? '100-500' : '500+' }); } catch (_) {}
          }
        }
        form.addEventListener('input', run);
        form.addEventListener('submit', run);
        run();
      })();"""


def build_calculator():
    slug = CALC_SLUG
    desc = ("Free calculator: estimate the hours a year one repetitive workflow takes your team, and how many an "
            "AI agent with human review could give back.")
    fields = [("items", "How many times does it happen a week?", "e.g. orders, quotes, documents or emails", 60, 1),
              ("minutes", "Minutes of handling each time", "reading, re-keying, checking, filing", 6, 1),
              ("weeks", "Working weeks a year", "", 48, 1),
              ("rate", "Loaded hourly cost of the person doing it (optional)", "wage plus overhead, any currency", "", 1)]
    inputs = "".join(
        f'<label class="field"><span><strong>{e(lab)}</strong>{f"<span class=muted> {e(hint)}</span>" if hint else ""}'
        f'</span><input type="number" name="{n}" min="0" step="{st}" inputmode="decimal" value="{v}" /></label>'
        for n, lab, hint, v, st in fields)
    faq = [("How is this calculated?",
            "Times per week × minutes each ÷ 60 gives weekly hours; × working weeks gives yearly hours; × the share "
            "you expect back gives the hours an agent could return. A 37.5-hour week converts hours to working weeks."),
           ("What share should I use?",
            "Start low. The agent prepares and a person still reviews, so the time that comes back is the reading "
            "and re-keying, not the checking. 30% is a cautious first guess; the Discovery Sprint measures the "
            "real figure on your own work.")] + FAQ_TOOLS
    main = f"""
{hero("How many hours could come back?", "A two-minute estimate of what one repetitive workflow costs your team "
      "each year, and how much of it an AI agent with human review could give back.", "calc", "Hours-back calculator",
      slug=slug, accent="come back?", task=("#calc", "Use the calculator"))}
<section class="section tone-lime" id="calc-wrap"><div class="wrap split calc-split">
  <form class="panel calc" id="calc">{inputs}
    <label class="field"><span><strong>Share of that time an agent could give back</strong>
      <span class="muted"> after your team reviews its work</span></span>
      <span class="range"><input type="range" name="share" min="0" max="90" step="5" value="30" />
      <output id="share-out">30%</output></span></label>
    <div class="actions"><button class="btn btn-ink" type="submit">Work it out</button></div>
    <noscript><p class="muted">Times per week × minutes ÷ 60 × working weeks × share = hours back a year.</p></noscript>
  </form>
  <div class="panel result calc-out" aria-live="polite">
    <p class="eyebrow">Your estimate</p>
    <dl class="stats">
      <div><dt>Hours a week on this today</dt><dd id="r-weekly">0</dd></div>
      <div><dt>Hours a year</dt><dd id="r-yearly">0</dd></div>
      <div><dt>Hours that could come back each year</dt><dd id="r-back">0</dd></div>
      <div><dt>That's about this many working weeks</dt><dd id="r-weeks">0</dd></div>
      <div id="r-money-row" hidden><dt>Worth, at your hourly cost</dt><dd id="r-money">0</dd></div>
    </dl>
    <p class="muted small">Your own numbers multiplied out: an estimate, not a quote or a promise.</p>
    <div class="actions">{contact("calc")}
      <a class="btn btn-ghost" href="{rel(slug, 'discovery-sprint/')}">How the sprint measures it</a></div>
  </div>
</div></section>
<section class="section"><div class="wrap">{faq_html(faq)}</div></section>
{cta_band("calc-band")}
<script>
{CALC_JS}
</script>"""
    app = {"@type": "WebApplication", "@id": url(slug) + "#app", "name": "Hours-back calculator",
           "url": url(slug), "applicationCategory": "BusinessApplication", "operatingSystem": "Any",
           "isAccessibleForFree": True, "description": desc, "publisher": {"@id": ORG_ID},
           "offers": {"@type": "Offer", "price": "0", "priceCurrency": "CAD"}}
    return page(slug, "Hours-Back Calculator for AI Automation", desc, main,
                ld=[app, faq_ld(faq)], ref="calc")


def build_tools():
    slug = TOOLS_SLUG
    desc = ("Free tools from VisionzLab for small businesses weighing AI: a workflow finder, an hours-back "
            "calculator and the 4S check. They run in your browser; no sign-up.")
    cards = [(CALC_SLUG, "Calculator", "Hours-back calculator",
              "Estimate what one repetitive workflow costs a year, and how much an agent could give back."),
             (MATURITY_SLUG, "Self-check", "The 4S check",
              "Eight yes-or-no questions place one workflow at Strategy, Solution, Scale or Sustain."),
             ("#finder", "Finder", "Workflow finder", "Describe a task in a few words and see the closest thing we build.")]
    html_cards = "".join(
        f'<a class="card" href="{h if h.startswith("#") else rel(slug, h)}"><span class="tag">{e(t)}</span>'
        f'<h3>{e(n)}</h3><p>{e(d)}</p><span class="arrow">→</span></a>' for h, t, n, d in cards)
    main = f"""
{hero("Free tools for deciding where AI fits", "No sign-up and nothing to install. Each one takes a couple of "
      "minutes and runs in your browser.", "tools", "Free tools", slug=slug, accent="where AI fits", tone="lime",
      task=("#tools", "Pick a tool"))}
<section class="section" id="tools"><div class="wrap">{section_head("Tools", "Three free tools", intro=(
    "A workflow finder, an hours-back calculator and the 4S check. Each runs in your browser, with no sign-up "
    "and nothing to install."), accent="free tools")}<div class="cards cards-uc">{html_cards}</div></div></section>
{finder(slug, tone="lime")}
<section class="section"><div class="wrap">{faq_html(FAQ_TOOLS)}</div></section>
{cta_band("tools-band")}"""
    return page(slug, "Free AI Tools for Small Businesses", desc, main, ld=[faq_ld(FAQ_TOOLS)], ref="tools")


def article_ld(g):
    return {"@type": "Article", "@id": url(g["slug"]) + "#article", "headline": g["title"],
            "description": g["description"], "url": url(g["slug"]), "mainEntityOfPage": url(g["slug"]),
            "datePublished": g.get("published", GUIDES_PUBLISHED),
            "dateModified": g.get("updated", g.get("published", GUIDES_PUBLISHED)), "inLanguage": "en",
            "author": {"@id": ORG_ID}, "publisher": {"@id": ORG_ID}, "image": f"{SITE}/public/og.jpg"}


def build_guide(g):
    slug = g["slug"]
    ref = "guide-" + slug.split("/")[1]
    body = []
    for head, paras, bullets in g["sections"]:
        ps = "".join(f"<p>{e(p)}</p>" for p in paras)
        cls = "ticks flags" if head.lower().startswith("red flag") else "ticks"
        ul = f'<ul class="{cls}">{"".join(f"<li>{e(b)}</li>" for b in bullets)}</ul>' if bullets else ""
        body.append(f"<h2>{e(head)}</h2>{ps}{ul}")
    others = [x for x in GUIDES if x["slug"] != slug]
    more = rows(slug, [(x["slug"], x["nav"], x["description"]) for x in others] +
                [(CALC_SLUG, "Hours-back calculator", "Estimate what one workflow costs a year, and what could come back.")])
    main = f"""
{hero(g["h1"], g["lead"], ref, g.get("eyebrow", "Guide"), slug=slug, accent=g["accent"], tone="lime")}
<section class="section"><div class="wrap narrow prose big guide">
  <p class="muted small">Published {g.get("published", GUIDES_PUBLISHED)} by {BRAND}{
      f' · Updated {g["updated"]}' if g.get("updated") else ""}</p>
  {"".join(body)}
</div></section>
<section class="section tone-paper"><div class="wrap">{faq_html(g["faq"])}</div></section>
<section class="section tone-lime"><div class="wrap">{section_head("Keep reading", "More guides and tools", accent="and tools")}{more}</div></section>
{cta_band(ref + "-band")}"""
    return page(slug, g["title"], g["description"], main, ld=[article_ld(g), faq_ld(g["faq"])], ref=ref,
                og_type="article")


def build_guides():
    slug = GUIDES_SLUG
    desc = ("Plain-English guides from VisionzLab for small and mid-sized businesses deciding where AI agents and "
            "automation fit, and how to buy them well.")
    items = [(g["slug"], g["nav"], g["description"]) for g in GUIDES]
    items += [(MATURITY_SLUG, "The 4S check", "Where is your business with AI? Eight questions, about two minutes."),
              ("instead-of-hiring/", "AI capacity instead of a hire", "When an AI engineering team beats adding headcount.")]
    main = f"""
{hero("Guides for putting AI to work", "Short answers to the questions owners ask us most, written so you can "
      "use them with or without us.", "guides", "Guides", slug=slug, accent="to work", tone="lime",
      task=("#library", "Browse the guides"))}
<section class="section" id="library"><div class="wrap">{section_head("Library", "All guides", intro=(
    "Each guide answers one buying question in plain English: what to ask, what it involves, and the red "
    "flags. No sign-up."), accent="guides")}{rows(slug, items)}</div></section>
{cta_band("guides-band")}"""
    return page(slug, "AI Automation Guides for Small Businesses", desc, main, ref="guides")


def build_privacy():
    slug = PRIVACY_SLUG
    desc = f"How the {BRAND} website handles the information you share with it: the enquiry form, analytics and email."
    main = f"""
{hero("Privacy", "What this website collects, why, and how to reach us about it.", "privacy", "Privacy notice",
      slug=slug, cta="Book a free discovery call")}
<section class="section"><div class="wrap narrow prose big">
  <p>{BRAND} is a brand of {LEGAL_NAME}, an Ontario corporation. This notice covers visionzlab.com. Work we do for
  a client is covered by the agreement for that engagement.</p>
  <h2>The enquiry form</h2>
  <p>When you book a call, the form collects the details you type in, plus the page or link you came from, so
  we know which part of the site was useful. The form is provided by HubSpot, which stores your submission for us
  and may set its own cookies; see <a class="link" href="https://legal.hubspot.com/privacy-policy" rel="noopener">HubSpot's
  privacy policy</a>. We use these details to reply to you and arrange the call, and we don't sell them.</p>
  <h2>Analytics</h2>
  <p>We count page views and button clicks with Umami, a privacy-focused analytics tool we host ourselves. It does
  not use cookies. The free tools on this site record only that they were used, never what you type into them.</p>
  <h2>Email</h2>
  <p>If you email us, we keep the conversation so we can reply and follow up.</p>
  <h2>Hosting</h2>
  <p>The site is served by GitHub Pages, which may log technical data such as IP addresses to run and protect the
  service. Fonts and images are served from this site, not from third parties.</p>
  <h2>Your choices</h2>
  <p>To see, correct or delete what we hold about you, email <a class="link" href="mailto:{EMAIL_GENERAL}">{EMAIL_GENERAL}</a>.</p>
  <p class="muted small">Last updated {GUIDES_PUBLISHED}.</p>
</div></section>"""
    return page(slug, "Privacy", desc, main, ref="privacy")


def build_data_trust():
    t, slug = DATA_TRUST, DATA_TRUST_SLUG
    blocks = []
    for i, (head, intro, items) in enumerate(t["sections"]):
        lis = "".join(f"<li><strong>{e(a)}.</strong> {e(b)}</li>" for a, b in items)
        p = f'<p class="big">{e(intro)}</p>' if intro else ""
        tone = " tone-lime" if i % 2 == 0 else ""
        blocks.append(f'<section class="section{tone}"><div class="wrap narrow prose big"><h2>{e(head)}</h2>{p}'
                      f'<ul class="ticks">{lis}</ul></div></section>')
    main = f"""
{hero(t["h1"], t["lead"], "trust", "Security and privacy", slug=slug, accent="your data")}
{"".join(blocks)}
<section class="section"><div class="wrap narrow prose big">
  <h2>The standards we follow</h2><p>{e(t["standards"])}</p>
  <h2>If something goes wrong</h2><p>{e(t["incident"])}</p>
  <h2>Ask us anything</h2><p>On request, we'll give you the list of providers that would handle your data, their
  audit reports, and a written description of how your system is set up. Email
  <a class="link" href="mailto:{EMAIL_GENERAL}">{EMAIL_GENERAL}</a>.</p>
  <p class="muted small">This page covers the AI systems we build for clients. For this website itself, see our
  <a class="link" href="{rel(slug, PRIVACY_SLUG)}">privacy notice</a>. Last updated 2026-11-04.</p>
</div></section>
<section class="section"><div class="wrap">{faq_html(t["faq"])}</div></section>
{cta_band("trust-band")}"""
    return page(slug, t["title"], t["description"], main, ld=[faq_ld(t["faq"])], ref="trust")


def build_llms(pages):
    lines = [f"# {BRAND}", "",
             "> AI studio helping small and mid-sized businesses in Canada and the US put AI agents to work: "
             "training, guided agent setup, custom AI development, managed AI employees, and AI engineering "
             "capacity instead of a new hire. Also an AI-assisted security review for small businesses.", "",
             f"{BRAND} (also written {', '.join(ALT_NAMES[:2])}) is based in Ontario, Canada, and serves "
             "Canada and the United States.", "",
             f"Who we serve: {WHO_WE_SERVE}", "", f"Pricing: {PRICING_SUMMARY}", "", "## Pages", ""]
    lines += [f"- [{t}]({url(s)}): {d}" for s, t, d in pages]
    lines += ["", "## Full text and feeds", "", f"- [Full text of every page]({SITE}/llms-full.txt)",
              f"- [Guides RSS feed]({url(GUIDES_SLUG)}feed.xml)"]
    lines += ["", "## Contact", "", f"- New business: {EMAIL_SALES}", f"- General: {EMAIL_GENERAL}",
              f"- Book a free discovery call: {CONTACT_URL}", "",
              f"{BRAND} is a brand of {LEGAL_NAME}, an Ontario corporation.", ""]
    return "\n".join(lines)


class _Text(html.parser.HTMLParser):
    """The readable text of a page's <main>, as light Markdown, for llms-full.txt."""
    SKIP = {"script", "style", "svg", "noscript", "template", "button", "select"}
    VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}
    PREFIX = {"h1": "# ", "h2": "## ", "h3": "### ", "h4": "#### ", "li": "- ", "summary": "Q: "}
    BLOCK = {"p", "li", "h1", "h2", "h3", "h4", "dt", "dd", "summary", "tr", "blockquote", "figcaption",
             "div", "label", "section", "article", "ul", "ol", "dl", "form", "header", "footer", "nav"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.out, self.buf, self.prefix = [], [], ""
        self.stack, self.skip_at = [], None  # open tags inside <main>; depth where a skipped subtree began

    def handle_starttag(self, tag, attrs):
        if tag == "main":
            self.stack = ["main"]
            return
        if not self.stack or tag in self.VOID:
            return
        self.stack.append(tag)
        a = dict(attrs)
        # aria-live regions are calculator outputs: placeholder zeros until someone uses the tool
        if self.skip_at is None and (tag in self.SKIP or a.get("aria-hidden") == "true" or "hidden" in a
                                     or "aria-live" in a):
            self.skip_at = len(self.stack)
        if self.skip_at is None and tag in self.BLOCK:
            self.flush()
            self.prefix = self.PREFIX.get(tag, "")

    def handle_endtag(self, tag):
        if not self.stack or tag not in self.stack:
            return
        while self.stack:  # pop to the matching tag (tolerates unclosed children)
            top = self.stack.pop()
            if self.skip_at is not None and len(self.stack) < self.skip_at:
                self.skip_at = None
            if top == tag:
                break
        if tag in self.BLOCK or tag == "main":
            self.flush()

    def handle_data(self, data):
        if self.stack and self.skip_at is None:
            self.buf.append(data)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)

    def updatepos(self, i, j):  # a tag boundary separates words ("calculator" + "Book"), never joins them
        if self.stack and self.skip_at is None and self.buf and not self.buf[-1].endswith(" "):
            self.buf.append(" ")
        return super().updatepos(i, j)

    def flush(self):
        text = re.sub(r" ([.,;:!?)])", r"\1", " ".join("".join(self.buf).split()))
        if text:
            self.out.append(self.prefix + text)
        self.buf, self.prefix = [], ""


def page_text(body):
    t = _Text()
    t.feed(body)
    t.flush()
    lines, prev = [], None
    for line in t.out:
        if line != prev:  # drop repeats such as a heading echoed by a visual label
            lines.append(line)
        prev = line
    return "\n\n".join(lines)


def build_llms_full(pages):
    """Every indexed page's readable text in one file, for answer engines that read llms-full.txt."""
    head = build_llms([]).split("## Pages")[0].rstrip()
    parts = [head, "", f"This file holds the full text of every page on {SITE}. The index is {SITE}/llms.txt.", ""]
    for slug, body, title, _ in pages:
        parts += [f"---\n\n# {title}\n\nURL: {url(slug)}", "", page_text(body), ""]
    return "\n".join(parts) + "\n"


def build_guides_feed():
    """RSS 2.0 feed of the guides, newest first."""
    def rfc822(d):
        return datetime.datetime.strptime(d, "%Y-%m-%d").strftime("%a, %d %b %Y 12:00:00 +0000")
    items = sorted(GUIDES, key=lambda g: g.get("published", GUIDES_PUBLISHED), reverse=True)
    rows = "".join(
        f"    <item>\n      <title>{e(g['title'])}</title>\n      <link>{url(g['slug'])}</link>\n"
        f"      <guid isPermaLink=\"true\">{url(g['slug'])}</guid>\n"
        f"      <pubDate>{rfc822(g.get('published', GUIDES_PUBLISHED))}</pubDate>\n"
        f"      <description>{e(g['description'])}</description>\n    </item>\n" for g in items)
    newest = rfc822(max(g.get("updated", g.get("published", GUIDES_PUBLISHED)) for g in GUIDES))
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">\n  <channel>\n'
            f"    <title>{BRAND} guides</title>\n    <link>{url(GUIDES_SLUG)}</link>\n"
            f'    <atom:link href="{url(GUIDES_SLUG)}feed.xml" rel="self" type="application/rss+xml" />\n'
            "    <description>Plain-English guides on where AI agents and automation fit in a small or "
            "mid-sized business.</description>\n    <language>en-ca</language>\n"
            f"    <lastBuildDate>{newest}</lastBuildDate>\n{rows}  </channel>\n</rss>\n")


OG_TEMPLATE = """<!doctype html><html><head><meta charset="utf-8"><style>
@font-face {{ font-family: Inter; src: url("{font}") format("woff2"); font-weight: 100 900; }}
* {{ box-sizing: border-box; margin: 0; }}
html, body {{ width: 1200px; height: 630px; overflow: hidden; }}
body {{ background: #fafaf7; color: #16052d; font-family: Inter, sans-serif; display: grid;
  grid-template-columns: 1fr 300px; gap: 56px; align-items: center; padding: 72px 80px;
  border-bottom: 16px solid #e1ff3f; }}
.eyebrow {{ display: inline-block; border: 3px solid #16052d; border-radius: 999px; padding: 8px 20px;
  font-size: 22px; font-weight: 700; letter-spacing: .12em; text-transform: uppercase; margin-bottom: 34px; }}
h1 {{ font-size: {size}px; line-height: 1.08; font-weight: 650; letter-spacing: -.025em; }}
.hl {{ background: #e1ff3f; padding: 0 .12em; box-decoration-break: clone; -webkit-box-decoration-break: clone; }}
.brand {{ margin-top: 40px; font-size: 26px; font-weight: 600; display: flex; align-items: center; gap: 12px; }}
.frame {{ width: 300px; height: 300px; background: #16052d; display: grid; place-items: center; }}
.frame g {{ stroke: #e1ff3f; }}
.frame svg {{ width: 190px; height: 190px; }}
</style></head><body>
<div><p class="eyebrow">{eyebrow}</p><h1>{title}</h1>
<p class="brand"><svg width="34" height="34" viewBox="0 0 100 100">{mark}</svg>visionzlab.com</p></div>
<div class="frame"><svg viewBox="0 0 100 100">{mark}</svg></div>
</body></html>"""
OG_MARK = ('<g fill="#E1FF3F" stroke="#16052D" stroke-width="3.5" stroke-linejoin="round">'
           '<path d="M38 27 Q49.22 48.78 71 60 Q49.22 71.22 38 93 Q26.78 71.22 5 60 Q26.78 48.78 38 27 Z"/>'
           '<path d="M79 9 Q84.1 18.9 94 24 Q84.1 29.1 79 39 Q73.9 29.1 64 24 Q73.9 18.9 79 9 Z"/></g>')
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"


def render_og_cards():
    """Render a 1200x630 PNG per page with headless Chrome, only for cards whose HTML changed.
    public/og/manifest.json maps each card to the hash of the HTML it was rendered from."""
    import hashlib
    import tempfile
    out_dir = ROOT / "public" / "og"
    out_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = out_dir / "manifest.json"
    manifest = json.loads(manifest_path.read_text()) if manifest_path.exists() else {}
    font = (ROOT / "public" / "fonts" / "inter-latin.woff2").as_uri()
    rendered = 0
    for name, (eyebrow, title) in sorted(OG_CARDS.items()):
        size = 76 if len(title) <= 40 else 64 if len(title) <= 62 else 54
        accent = title.split(" for ", 1)[1] if " for " in title else None
        shown = headline(title, accent) if accent and len(accent) <= 24 else e(title)
        doc = OG_TEMPLATE.format(font=font, eyebrow=e(eyebrow), title=shown, mark=OG_MARK, size=size)
        digest = hashlib.sha256(doc.encode()).hexdigest()[:16]
        target = out_dir / name
        if manifest.get(name) == digest and target.exists():
            continue
        if not pathlib.Path(CHROME).exists():
            raise SystemExit(f"OG card {name} needs rendering but Chrome is not at {CHROME}")
        with tempfile.TemporaryDirectory() as tmp:
            src = pathlib.Path(tmp) / "card.html"
            src.write_text(doc)
            subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--force-device-scale-factor=1",
                            "--window-size=1200,630", f"--screenshot={target}", src.as_uri()],
                           check=True, capture_output=True, timeout=60)
        manifest[name] = digest
        rendered += 1
    for stale in set(manifest) - set(OG_CARDS):
        (out_dir / stale).unlink(missing_ok=True)
        del manifest[stale]
    manifest_path.write_text(json.dumps(manifest, indent=1, sort_keys=True) + "\n")
    return rendered


def committed(path):
    """The file's text at HEAD, or None if git has no committed version of it."""
    res = subprocess.run(["git", "show", f"HEAD:{path}"], cwd=ROOT, capture_output=True, text=True)
    return res.stdout if res.returncode == 0 else None


def lastmods(pages):
    """Each page's lastmod: the committed sitemap's date if its HTML matches HEAD, otherwise today.
    <script> blocks are ignored, so a tracking or form-script change doesn't re-date every page."""
    prev = dict(re.findall(r"<loc>(.*?)</loc>\s*<lastmod>(.*?)</lastmod>", committed("sitemap.xml") or ""))
    strip = lambda h: re.sub(r"<script\b.*?</script>", "", h or "", flags=re.S)
    return {slug: prev.get(url(slug), TODAY) if strip(body) == strip(committed(f"{slug}index.html")) else TODAY
            for slug, body in pages}


def build_sitemap(dates):
    rows = "".join(f"  <url>\n    <loc>{url(s)}</loc>\n    <lastmod>{d}</lastmod>\n  </url>\n"
                   for s, d in dates.items())
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + rows + "</urlset>\n")


def build_redirect(from_slug, to_slug):
    target, here = url(to_slug), rel(from_slug, to_slug)
    return f"""<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <title>Moved | {BRAND}</title>
    <meta name="robots" content="noindex, follow" />
    <link rel="canonical" href="{target}" />
    <meta http-equiv="refresh" content="0; url={here}" />
    <script>location.replace({json.dumps(here)} + location.search + location.hash);</script>
  </head>
  <body><p>This page has moved to <a href="{here}">{target}</a>.</p></body>
</html>
"""


def main():
    global TRACKER_JS, CONTACT_URL
    check_questions()
    if HUBSPOT_FORM_ID:
        CONTACT_URL = url(BOOK_SLUG)
    TRACKER_JS = (TRACKER_JS.replace("__UMAMI_HOST__", UMAMI_HOST)
                  .replace("__UMAMI_ID__", UMAMI_SITE_ID or ""))
    out = [("", build_home(), "Home", ORG["description"]),
           ("services/", build_services(), "Services", "The five ways to work with us."),
           ("discovery-sprint/", build_sprint(), "Discovery Sprint", "The paid sprint most engagements start with."),
           (MATURITY_SLUG, build_maturity(), "The 4S check",
            "Where is your business with AI? Eight questions place one workflow at Strategy, Solution, Scale or "
            "Sustain.")]
    out += [(t["slug"], build_tier(i), t["title"], t["description"]) for i, t in enumerate(TIERS)]
    out += [(SECURITY["slug"], build_security(), SECURITY["title"], SECURITY["description"])]
    out += [("use-cases/", build_use_cases(), "AI Agent Use Cases", "Agents for operations, growth and finance teams.")]
    out += [(u["slug"], build_use_case(u), u["title"], u["description"]) for u in USE_CASES]
    out += [(p["slug"], build_play(p), p["title"], p["description"]) for p in PLAYS]
    out += [("about/", build_about(), "About", "Who we are and how we work.")]
    out += [(EXPERIENCE_SLUG, build_experience(), "Our team's experience",
             "What our team built before VisionzLab, and how we earn trust before we have case studies of our own.")]
    out += [(m["slug"], build_person(m), f"{m['name']}, {m['role']}", m["description"]) for m in TEAM]
    out += [(GUIDES_SLUG, build_guides(), "Guides", "Plain-English guides on where AI agents and automation fit.")]
    out += [(g["slug"], build_guide(g), g["title"], g["description"]) for g in GUIDES]
    out += [(TOOLS_SLUG, build_tools(), "Free tools", "Workflow finder, hours-back calculator and the 4S check.")]
    out += [(CALC_SLUG, build_calculator(), "Hours-back calculator",
             "Estimate how many hours a year one workflow takes, and how many an AI agent could give back.")]
    out += [(DATA_TRUST_SLUG, build_data_trust(), "Security and privacy",
             "How we protect client data in the AI systems we build: approved models, no training, people approve.")]
    out += [(PRIVACY_SLUG, build_privacy(), "Privacy", "What this website collects and why.")]
    if HUBSPOT_FORM_ID:
        out += [(BOOK_SLUG, build_book(), "Book a free discovery call", "Book a free discovery call.")]
    for slug, body, _, _ in out:
        path = ROOT / slug / "index.html"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(body)
    for old, new in REDIRECTS.items():
        path = ROOT / old / "index.html"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(build_redirect(old, new))
    (ROOT / "sitemap.xml").write_text(build_sitemap(lastmods([(s, b) for s, b, *_ in out])))
    (ROOT / "llms.txt").write_text(build_llms([(s, t, d) for s, _, t, d in out]))
    (ROOT / "llms-full.txt").write_text(build_llms_full(out))
    cards = render_og_cards()
    (ROOT / GUIDES_SLUG / "feed.xml").write_text(build_guides_feed())
    print(f"wrote {len(out)} pages, sitemap.xml, llms.txt, llms-full.txt, {GUIDES_SLUG}feed.xml; "
          f"{len(OG_CARDS)} social cards ({cards} re-rendered)")


if __name__ == "__main__":
    main()
