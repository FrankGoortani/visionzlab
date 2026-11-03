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
import re
import subprocess

ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE = "https://visionzlab.com"
BRAND = "VisionzLab"
TODAY = datetime.date.today().isoformat()

# Contact and analytics endpoints. Both are personal-account hostnames for now;
# swap them here once brand-neutral replacements exist.
CONTACT_URL = "https://frankgoortani.typeform.com/to/VaoYV6iJ"
UMAMI_HOST = "https://goortani.synology.me:3100"
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
}
EMAIL_GENERAL = "hello@visionzlab.com"  # alias on frank@ (Workspace, 2026-11-01): no extra mailbox
EMAIL_FRANK = "frank@visionzlab.com"
EMAIL_SALES = "asal@visionzlab.com"

# Brand search: "visionzlab" is one word that Google readily "corrects" to "vision lab". These spellings tell it
# (WebSite + Organization alternateName) that the variants all mean this site, so a brand query resolves here.
ALT_NAMES = ["Visionz Lab", "VisionZ Lab", "VisionzLab AI", "visionzlab.com"]
# Official profiles of the company itself (not of people). Add each one here once it is confirmed to be ours:
# the LinkedIn company page, then @visionzlabs on YouTube/Instagram/TikTok/Facebook when they exist.
SAME_AS = ["https://www.linkedin.com/company/visionzlab-ai/"]  # confirmed ours 2026-10-31 (Asal listed, website field set)

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
                   "Document intake automation", "Order entry automation", "AI workflow design"],
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
        "title": "Managed AI Employee for Your Business",
        "description": "We build an AI employee for a defined role — bookkeeping, intake, reporting, follow-ups — "
                       "and keep it working for a monthly fee.",
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
        "ref": "play-industrial",
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
]

# Workflow finder (homepage and /tools/): words a visitor might type, mapped to the page that answers them.
FINDER = {
    "use-cases/quote-rfq-intake/": ["quote", "rfq", "estimate", "pricing", "price list", "tender", "bid"],
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


def contact(ref, label="Request a free discovery session", cls="btn"):
    external = '' if CONTACT_URL.startswith(SITE) else ' target="_blank" rel="noopener"'
    return (f'<a class="{cls}" href="{CONTACT_URL}#ref={e(ref)}" data-contact data-ref="{e(ref)}" '
            f'data-umami-event="contact_click" data-umami-event-location="{e(ref)}"{external}>{e(label)}</a>')


def faq_html(faq):
    items = "".join(f"<details><summary>{e(q)}</summary><p>{e(a)}</p></details>" for q, a in faq)
    return f'<section class="section"><h2>Questions</h2><div class="faq">{items}</div></section>'


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
            f'<span class="num">0{i + 1}</span><span class="tag">{e(t["tier"])}</span>'
            f'<div class="thumb">{art(slug, t["art"])}</div>'
            f'<h3>{e(t["nav"])}</h3><p>{e(t["lead"])}</p><span class="arrow">→</span></a>')
    return f'<div class="cards cards-tiers">{"".join(cards)}</div>'


def page(slug, title, description, main, ld=None, ref="site", image="public/og.jpg", og_type="website"):
    canonical = url(slug)
    full_title = f"{title} | {BRAND}" if slug else f"{BRAND} | {title}"
    nav = [("services/", "Services"), ("use-cases/", "Use Cases"), ("discovery-sprint/", "Discovery Sprint"),
           ("experience/", "Experience"), ("about/", "About")]
    nav_html = "".join(f'<a href="{rel(slug, s)}">{e(n)}</a>' for s, n in nav)
    foot_tiers = "".join(f'<li><a href="{rel(slug, t["slug"])}">{e(t["nav"])}</a></li>' for t in TIERS)
    foot_plays = "".join(f'<li><a href="{rel(slug, p["slug"])}">{e(p["nav"])}</a></li>' for p in PLAYS)
    foot_team = "".join(f'<li><a href="{rel(slug, m["slug"])}">{e(m["name"])}</a></li>' for m in TEAM)
    foot_guides = "".join(f'<li><a href="{rel(slug, g["slug"])}">{e(g["nav"])}</a></li>' for g in GUIDES)
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
        <nav class="nav" aria-label="Main navigation">{nav_html}{contact(ref + '-nav', 'Request a call', 'btn btn-sm')}</nav>
        <details class="mobile-menu"><summary>Menu</summary>
          <nav aria-label="Mobile navigation">{nav_html}{contact(ref + '-nav', 'Request a call', 'btn btn-sm')}</nav>
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
        <div><h2>Services</h2><ul>{foot_tiers}<li><a href="{rel(slug, 'discovery-sprint/')}">Discovery Sprint</a></li>
          <li><a href="{rel(slug, MATURITY_SLUG)}">The 4S check</a></li></ul></div>
        <div><h2>Use cases</h2><ul>{foot_uses}</ul></div>
        <div><h2>Who we help</h2><ul>{foot_plays}</ul></div>
        <div><h2>Resources</h2><ul><li><a href="{rel(slug, GUIDES_SLUG)}">Guides</a></li>
          {foot_guides}<li><a href="{rel(slug, TOOLS_SLUG)}">Free tools</a></li>
          <li><a href="{rel(slug, CALC_SLUG)}">Hours-back calculator</a></li></ul></div>
        <div><h2>Company</h2><ul><li><a href="{rel(slug, 'about/')}">About</a></li>
          <li><a href="{rel(slug, EXPERIENCE_SLUG)}">Our experience</a></li>
          {foot_team}
          <li><a href="{SAME_AS[0]}" rel="noopener">LinkedIn</a></li>
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


def hero(h1, lead, ref, eyebrow=None, cta="Request a free discovery session", slug="", img=None, alt="",
         accent=None, tone="paper", second=None):
    eb = f'<p class="eyebrow">{e(eyebrow)}</p>' if eyebrow else ""
    sec = f'<a class="btn btn-ghost" href="{rel(slug, second[0])}">{e(second[1])}</a>' if second else ""
    visual = f'<div class="frame">{art(slug, img, alt, eager=True)}</div>' if img else ""
    cls = "hero-split" if img else "hero-solo"
    return (f'<section class="hero tone-{tone}"><div class="wrap {cls}"><div class="hero-copy">{eb}'
            f'<h1>{headline(h1, accent)}</h1><p class="lead">{e(lead)}</p>'
            f'<div class="actions">{contact(ref, cta)}{sec}</div></div>{visual}</div></section>')


def section_head(eyebrow, title, intro=None, accent=None):
    i = f'<p class="intro">{e(intro)}</p>' if intro else ""
    return f'<div class="sec-head"><p class="eyebrow">{e(eyebrow)}</p><h2>{headline(title, accent)}</h2>{i}</div>'


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
            f'<div class="clients-heading"><p>Our team’s experience before VisionzLab</p>'
            f'<a class="link" href="{rel(slug, EXPERIENCE_SLUG)}">Explore that experience →</a></div>'
            f'<ul class="client-logos">{li}</ul></div></section>')


def cta_band(ref):
    return (f'<section class="band"><div class="wrap band-in"><div><h2>Not sure where to <span class="hl">start?</span></h2>'
            f'<p>Request a free discovery session. We\'ll look at your work together and tell you plainly '
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
      accent="off your team's plate.", second=("experience/", "Explore our experience"))}
{clients()}
</div>
{finder(slug)}

<section class="section tone-lime"><div class="wrap split">
  <div class="frame frame-paper">{art(slug, "sprint", "Isometric illustration of a laptop prototype, a roadmap and a checklist")}</div>
  <div><p class="eyebrow">Start here</p><h2>The Discovery <span class="hl">Sprint</span></h2>
  <p class="big">A short, paid sprint on one of your workflows. In 2–4 weeks you get a working prototype, a costed
  build plan and a clear go/no-go — before you commit to anything bigger.</p>
  <div class="actions"><a class="btn btn-ink" href="discovery-sprint/">How the sprint works →</a></div></div>
</div></section>
<section class="section tone-paper"><div class="wrap">
  {section_head("Use cases", "Start with one practical workflow.", accent="practical workflow.")}
  {use_case_cards(slug, only=["use-cases/quote-rfq-intake/", "use-cases/order-entry/", "use-cases/document-intake/"])}
  <p class="more"><a class="link" href="use-cases/">All use cases →</a></p>
</div></section>
<section class="section tone-lime"><div class="wrap">
  {section_head("Who we help", "Built for businesses without an AI team.", accent="without an AI team.")}
  {rows(slug, [(p["slug"], p["nav"], p["lead"]) for p in PLAYS])}
</div></section>
<section class="section tone-paper"><div class="wrap split">
  <div><h2>Choose the help that fits</h2><p class="big">Learn with us, build alongside us, or have us build and
  maintain your workflow. Start with one defined task and review the results before expanding.</p>
  <a class="link" href="services/">Compare the five services →</a></div>
  <div><h2>Not sure where to begin?</h2><p class="big">The 4S check is a short self-assessment to help you reflect
  on your next step with AI. Eight questions, about two minutes.</p>
  <a class="link" href="{MATURITY_SLUG}#check">Take the 4S check →</a></div>
</div></section>
<section class="section tone-lime"><div class="wrap split">
  <div><p class="eyebrow">About {BRAND}</p><h2>An AI studio for businesses <span class="hl">without an AI team</span></h2></div>
  <div><p class="big">{BRAND} is an AI studio based in Ontario, Canada, working with small and mid-sized businesses
  across Canada and the US. We teach teams to run their own agents, build agents with them, or build and run them
  for you, always with your people approving the decisions that matter.</p>
  <div class="actions"><a class="btn btn-ink" href="about/">About {BRAND} →</a>
  <a class="btn btn-ghost" href="{GUIDES_SLUG}">Read our guides</a></div></div>
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
<section class="section tone-lime"><div class="wrap split">
  <div>{section_head("Pricing", "How pricing works", intro=PRICING_SUMMARY, accent="pricing")}</div>
  <div class="panel"><ul class="ticks"><li><strong>Discovery session:</strong> free, with a short memo afterwards</li>
  <li><strong>Discovery Sprint:</strong> a fixed fee agreed before it starts</li>{"".join(
      f'<li><strong>{e(t["nav"])}:</strong> {e(t["priced"][0].lower() + t["priced"][1:].rstrip("."))}</li>' for t in TIERS)}</ul></div>
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


def check_questions():
    """Every use case and industry page leads with the question a buyer would type into an AI engine.
    _analytics/scripts/prompts-from-site.py reads it back from FAQPage to keep the answer-share probe in sync."""
    for x in USE_CASES + PLAYS:
        q, a = x.get("question") or (None, None)
        assert q and q.endswith("?") and len(q) > 25 and a, f'{x["slug"]}: add "question": (buyer question, answer)'


def build_play(p):
    slug = p["slug"]
    body = "".join(f"<p>{e(x)}</p>" for x in p["body"])
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
<section class="section tone-lime"><div class="wrap narrow prose big">{body}</div>{moments}</section>
<section class="section"><div class="wrap">{section_head("Where to start", "A recommended starting point", accent="starting point")}{ladder(slug, only=p["tiers"])}
<p class="more"><a class="link" href="{rel(slug, 'services/')}">See all five services →</a></p></div></section>
{uses}
<section class="section"><div class="wrap">{faq_html([p["question"]] + p.get("faq", []))}</div></section>
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
      "Use cases", slug=slug, tone="lime")}
<section class="section"><div class="wrap">{section_head("Use cases", f"{len(USE_CASES)} workflows we build agents for", intro=(
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
<section class="section"><div class="wrap split">
  <div><h2>Who it's for</h2><p class="big">{e(u["for"])}</p><h2>What the agent does</h2><ul class="ticks">{does}</ul></div>
  <div class="panel panel-lime"><h2>What stays with your people</h2><p class="big">{e(u["people"])}</p></div>
</div></section>
<section class="section tone-lime"><div class="wrap">{section_head("How to get it", "Pick the level of help that fits", accent="that fits")}{ladder(slug, only=u["tiers"])}</div></section>
<section class="section"><div class="wrap">{faq_html([u["question"]] + u["faq"])}</div></section>
<section class="section tone-lime"><div class="wrap">{section_head("More", "More use cases", accent="use cases")}{use_case_cards(slug, exclude=slug)}</div></section>
{cta_band(ref + "-band")}"""
    return page(slug, u["title"], u["description"], main,
                ld=[service_ld(slug, u["title"], u["description"]), faq_ld([u["question"]] + u["faq"])], ref=ref)


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
      accent="with AI?", second=(slug + "#check", "Take the check"))}
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
  {section_head("Before VisionzLab", "Experience behind the work", "Four examples from roles our founder held before "
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
    <div class="actions">{contact(ref, f"Request a conversation with {m['first']}")}
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
        document.addEventListener('hs-form-event:on-submission:success', function () {
          var shown = false;
          // After the request goes in, show the appointment calendar so the visitor can book a time at once.
          // The iframe only loads now, so visitors who never submit don't load Google Calendar.
          var box = document.getElementById('pick-a-time');
          if (box && box.hidden) {
            var frame = box.querySelector('iframe');
            frame.src = frame.getAttribute('data-src');
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
    desc = ("Request a free discovery session with VisionzLab. Tell us a little about your business and "
            "we'll find a time to talk.")
    js = BOOK_JS.replace("__REGION__", HUBSPOT_REGION).replace("__PORTAL__", HUBSPOT_PORTAL_ID)
    if BOOKING_CALENDAR_URL:
        book_next = ("Send the form, then pick a time from the calendar that appears, and the session is booked. "
                     "If none of the times suit you, we'll reply within one business day to find one.")
        calendar = f"""
<section class="tone-paper book-time" id="pick-a-time" hidden><div class="wrap">
  <h2>Thanks. Now pick a time.</h2>
  <p class="lead">Choose a slot and the session is booked: the invitation and video link arrive by email.
  If none of these times suit you, skip this step and we'll reply within one business day.</p>
  <iframe class="book-calendar" title="Pick a time for your discovery session" data-src="{BOOKING_CALENDAR_URL}"
    loading="lazy"></iframe>
  <p class="muted small">Calendar not showing? <a class="link" href="{BOOKING_CALENDAR_URL.split('?')[0]}"
    target="_blank" rel="noopener">Open it in a new tab</a>.</p>
</div></section>"""
    else:
        book_next = ("Send a request and we'll reply within one business day to arrange a time. "
                     "This form does not reserve an appointment.")
        calendar = ""
    main = f"""
<section class="hero tone-paper"><div class="wrap hero-split">
  <div class="hero-copy">
    <p class="eyebrow">Free discovery session</p>
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
    return page(slug, "Request a discovery session", desc, main, ref="book")


def page_title(slug):
    """Short name and lead for any finder target, from the content that owns it."""
    for u in USE_CASES:
        if u["slug"] == slug:
            return u["nav"], u["lead"]
    for t in TIERS:
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
    <div class="actions">{contact("finder", "Request a call about this").replace("<a ", "<a data-finder-cta ", 1)}
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
      slug=slug, accent="come back?", second=(slug + "#calc", "Use the calculator"))}
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
    <div class="actions">{contact("calc", "Check it on your real work")}
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
      "minutes and runs in your browser.", "tools", "Free tools", slug=slug, accent="where AI fits", tone="lime")}
<section class="section"><div class="wrap">{section_head("Tools", "Three free tools", intro=(
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
        ul = f'<ul class="ticks">{"".join(f"<li>{e(b)}</li>" for b in bullets)}</ul>' if bullets else ""
        body.append(f"<h2>{e(head)}</h2>{ps}{ul}")
    others = [x for x in GUIDES if x["slug"] != slug]
    more = rows(slug, [(x["slug"], x["nav"], x["description"]) for x in others] +
                [(CALC_SLUG, "Hours-back calculator", "Estimate what one workflow costs a year, and what could come back.")])
    main = f"""
{hero(g["h1"], g["lead"], ref, "Guide", slug=slug, accent=g["accent"], tone="lime")}
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
      "use them with or without us.", "guides", "Guides", slug=slug, accent="to work", tone="lime")}
<section class="section"><div class="wrap">{section_head("Library", "All guides", intro=(
    "Each guide answers one buying question in plain English: what to ask, what it involves, and the red "
    "flags. No sign-up."), accent="guides")}{rows(slug, items)}</div></section>
{cta_band("guides-band")}"""
    return page(slug, "AI Automation Guides for Small Businesses", desc, main, ref="guides")


def build_privacy():
    slug = PRIVACY_SLUG
    desc = f"How the {BRAND} website handles the information you share with it: the enquiry form, analytics and email."
    main = f"""
{hero("Privacy", "What this website collects, why, and how to reach us about it.", "privacy", "Privacy notice",
      slug=slug, cta="Request a call")}
<section class="section"><div class="wrap narrow prose big">
  <p>{BRAND} is a brand of {LEGAL_NAME}, an Ontario corporation. This notice covers visionzlab.com. Work we do for
  a client is covered by the agreement for that engagement.</p>
  <h2>The enquiry form</h2>
  <p>When you request a call, the form collects the details you type in, plus the page or link you came from, so
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


def build_llms(pages):
    lines = [f"# {BRAND}", "",
             "> AI studio helping small and mid-sized businesses in Canada and the US put AI agents to work: "
             "training, guided agent setup, custom AI development, managed AI employees, and AI engineering "
             "capacity instead of a new hire.", "",
             f"{BRAND} (also written {', '.join(ALT_NAMES[:2])}) is based in Ontario, Canada, and serves "
             "Canada and the United States.", "",
             f"Who we serve: {WHO_WE_SERVE}", "", f"Pricing: {PRICING_SUMMARY}", "", "## Pages", ""]
    lines += [f"- [{t}]({url(s)}): {d}" for s, t, d in pages]
    lines += ["", "## Contact", "", f"- New business: {EMAIL_SALES}", f"- General: {EMAIL_GENERAL}",
              f"- Request a discovery session: {CONTACT_URL}", "",
              f"{BRAND} is a brand of {LEGAL_NAME}, an Ontario corporation.", ""]
    return "\n".join(lines)


def committed(path):
    """The file's text at HEAD, or None if git has no committed version of it."""
    res = subprocess.run(["git", "show", f"HEAD:{path}"], cwd=ROOT, capture_output=True, text=True)
    return res.stdout if res.returncode == 0 else None


def lastmods(pages):
    """Each page's lastmod: the committed sitemap's date if its HTML matches HEAD, otherwise today."""
    prev = dict(re.findall(r"<loc>(.*?)</loc>\s*<lastmod>(.*?)</lastmod>", committed("sitemap.xml") or ""))
    return {slug: prev.get(url(slug), TODAY) if body == committed(f"{slug}index.html") else TODAY
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
    out += [(PRIVACY_SLUG, build_privacy(), "Privacy", "What this website collects and why.")]
    if HUBSPOT_FORM_ID:
        out += [(BOOK_SLUG, build_book(), "Request a discovery session", "Request a free discovery session.")]
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
    print(f"wrote {len(out)} pages, sitemap.xml, llms.txt")


if __name__ == "__main__":
    main()
