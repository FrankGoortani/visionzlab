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

# Illustrations (generated in the site's isometric line-art style). Missing files fall back to computer.webp.
ART = {
    "hero": ("public/art/hero-agents.webp", 1200, 800),
    "sprint": ("public/art/sprint.webp", 900, 900),
    "lab": ("public/art/lab.webp", 900, 900),
    "teach": ("public/art/tier-teach.webp", 900, 900),
    "setup": ("public/art/tier-setup.webp", 900, 900),
    "build": ("public/art/tier-build.webp", 900, 900),
    "employee": ("public/art/tier-employee.webp", 900, 900),
    "team": ("public/art/tier-team.webp", 900, 900),
}
EMAIL_GENERAL = "frank@visionzlab.com"
EMAIL_SALES = "asal@visionzlab.com"

ORG_ID = f"{SITE}/#organization"
ORG = {
    "@type": "ProfessionalService",
    "@id": ORG_ID,
    "name": BRAND,
    "url": f"{SITE}/",
    "logo": f"{SITE}/public/logo.png",
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
        "slug": "services/ai-training/", "art": "teach",
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
        "slug": "services/ai-agent-setup/", "art": "setup",
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
        "slug": "services/ai-development/", "art": "build",
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
        "slug": "services/ai-employee/", "art": "employee",
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
        "slug": "services/ai-team/", "art": "team",
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
        "slug": "for/small-business/", "art": "teach",
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
        "slug": "for/accountants-bookkeepers/", "art": "employee",
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
        "slug": "for/distributors-manufacturers/", "art": "build",
        "nav": "Distributors & Manufacturers",
        "title": "AI Quote and Order Automation for Distributors and Manufacturers",
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
        "slug": "for/insurance-brokers/", "art": "employee",
        "nav": "Insurance Brokers",
        "title": "AI Automation for Commercial and P&C Insurance Brokers",
        "description": "AI agents for commercial and property & casualty brokerages and MGAs: submission intake, "
                       "certificate requests, renewal preparation and claims intake, with brokers in control.",
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
        "slug": "for/mortgage-brokers/", "art": "setup",
        "nav": "Mortgage Brokers",
        "title": "AI Automation for Mortgage Brokers and Agents",
        "description": "AI tools for mortgage brokerages and agents: renewal tracking and outreach, document "
                       "collection, lead follow-up and being found in AI search, in more than one language.",
        "lead": "Never miss a renewal, chase fewer documents, and follow up with every lead — without more admin.",
        "body": [
            "Renewals are the business you already earned, and they are easy to lose when maturity dates live in "
            "a spreadsheet. Document collection and lead follow-up take the rest of the week.",
            "We set up tools that track every maturity date and prompt timely outreach, send clients a clear "
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
        "slug": "instead-of-hiring/", "art": "team",
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
        "slug": "use-cases/quote-rfq-intake/",
        "nav": "Quote & RFQ Intake",
        "title": "AI Quote and RFQ Intake Agent",
        "description": "An AI agent that reads incoming requests for quote, matches items to your catalogue and "
                       "pricing, and drafts the quote for your team to approve.",
        "lead": "An AI agent that reads every RFQ, matches it to your catalogue and drafts the quote, for your team to approve.",
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
        "nav": "Inbox Triage",
        "title": "AI Shared Inbox Triage and Reply Drafting Agent",
        "description": "An AI agent that sorts a shared inbox, routes each message to the right person and drafts "
                       "replies, so nothing waits and nothing is missed.",
        "lead": "An AI agent that sorts your shared inbox, routes every message and drafts the reply.",
        "for": "Teams working out of a shared inbox — sales, service, orders, claims or admin — where messages wait or get missed.",
        "does": [
            "Reads every incoming message and its attachments",
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
        "nav": "Renewals & Follow-up",
        "title": "AI Renewal Tracking and Client Follow-up Agent",
        "description": "An AI agent that tracks renewal and maturity dates, prepares timely outreach and follows "
                       "up with leads and clients, so no renewal or enquiry slips.",
        "lead": "An AI agent that tracks every renewal date and follows up with every lead, so nothing slips.",
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


def art(slug, key, alt="", eager=False):
    path, w, h = ART[key]
    if not (ROOT / path).exists():
        path, w, h = "public/computer.webp", 640, 540
    load = 'fetchpriority="high"' if eager else 'loading="lazy"'
    return f'<img src="{rel(slug, path)}" alt="{e(alt)}" width="{w}" height="{h}" {load} decoding="async" />'


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
    <meta property="og:image" content="{SITE}/public/og.jpg" />
    <meta name="twitter:card" content="summary_large_image" />
    <meta name="twitter:title" content="{e(full_title)}" />
    <meta name="twitter:description" content="{e(description)}" />
    <meta name="twitter:image" content="{SITE}/public/og.jpg" />
    <link rel="icon" type="image/svg+xml" href="data:image/svg+xml,%3Csvg%20xmlns%3D%22http%3A//www.w3.org/2000/svg%22%20viewBox%3D%220%200%20100%20100%22%3E%3Cg%20fill%3D%22%23E1FF3F%22%20stroke%3D%22%2316052D%22%20stroke-width%3D%223.5%22%20stroke-linejoin%3D%22round%22%3E%3Cpath%20d%3D%22M38%2027%20Q49.22%2048.78%2071%2060%20Q49.22%2071.22%2038%2093%20Q26.78%2071.22%205%2060%20Q26.78%2048.78%2038%2027%20Z%22/%3E%3Cpath%20d%3D%22M79%209%20Q84.1%2018.9%2094%2024%20Q84.1%2029.1%2079%2039%20Q73.9%2029.1%2064%2024%20Q73.9%2018.9%2079%209%20Z%22/%3E%3C/g%3E%3C/svg%3E" />
    <link rel="apple-touch-icon" href="{SITE}/public/logo.png" />
    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
    <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" />
    <link rel="stylesheet" href="{css}" />
    <script type="application/ld+json">{json.dumps({"@context": "https://schema.org", "@graph": graph}, indent=None)}</script>
  </head>
  <body>
    <header class="top">
      <div class="wrap top-in">
        <a class="brand" href="{rel(slug, '')}"><svg class="mark" viewBox="0 0 100 100" aria-hidden="true"><g fill="#E1FF3F" stroke="#16052D" stroke-width="3.5" stroke-linejoin="round"><path d="M38 27 Q49.22 48.78 71 60 Q49.22 71.22 38 93 Q26.78 71.22 5 60 Q26.78 48.78 38 27 Z"/><path d="M79 9 Q84.1 18.9 94 24 Q84.1 29.1 79 39 Q73.9 29.1 64 24 Q73.9 18.9 79 9 Z"/></g></svg>{BRAND}</a>
        <nav class="nav">{nav_html}{contact(ref + '-nav', 'Book a call', 'btn btn-sm')}</nav>
      </div>
    </header>
    <main>
{main}
    </main>
    <footer class="foot">
      <div class="wrap foot-in">
        <div><a class="brand" href="{rel(slug, '')}"><svg class="mark" viewBox="0 0 100 100" aria-hidden="true"><g fill="#E1FF3F" stroke="#16052D" stroke-width="3.5" stroke-linejoin="round"><path d="M38 27 Q49.22 48.78 71 60 Q49.22 71.22 38 93 Q26.78 71.22 5 60 Q26.78 48.78 38 27 Z"/><path d="M79 9 Q84.1 18.9 94 24 Q84.1 29.1 79 39 Q73.9 29.1 64 24 Q73.9 18.9 79 9 Z"/></g></svg>{BRAND}</a>
          <p class="muted">AI agents and automation for small and mid-sized businesses.<br />
          Based in Ontario, Canada · serving Canada and the US.</p></div>
        <div><h4>Services</h4><ul>{foot_tiers}<li><a href="{rel(slug, 'discovery-sprint/')}">Discovery Sprint</a></li>
          <li><a href="{rel(slug, MATURITY_SLUG)}">The 4S check</a></li></ul></div>
        <div><h4>Use cases</h4><ul>{foot_uses}</ul></div>
        <div><h4>Who we help</h4><ul>{foot_plays}</ul></div>
        <div><h4>Company</h4><ul><li><a href="{rel(slug, 'about/')}">About</a></li>
          <li><a href="{rel(slug, ASAL['slug'])}">Business Development</a></li>
          <li><a href="mailto:{EMAIL_SALES}">{EMAIL_SALES}</a></li>
          <li><a href="mailto:{EMAIL_GENERAL}">{EMAIL_GENERAL}</a></li></ul></div>
      </div>
      <div class="legal"><div class="wrap muted">© {datetime.date.today().year} {LEGAL_NAME} · {BRAND} is a brand of
        {LEGAL_NAME}, an Ontario corporation.</div></div>
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


def hero(h1, lead, ref, eyebrow=None, cta="Book a free discovery session", slug="", img=None, alt="",
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


def stats():
    items = [("5", "ways to work with us, from training to a full team"),
             ("2–4", "weeks for a discovery sprint, prototype included"),
             ("1", "point of contact from first call to delivery"),
             ("CA + US", "clients across Canada and the United States")]
    cells = "".join(f'<div class="stat"><strong>{e(a)}</strong><span>{e(b)}</span></div>' for a, b in items)
    return f'<section class="stats"><div class="wrap stats-in">{cells}</div></section>'


def cta_band(ref):
    return (f'<section class="band"><div class="wrap band-in"><div><h2>Not sure where to <span class="hl">start?</span></h2>'
            f'<p>Book a free discovery session. We\'ll look at your work together and tell you plainly '
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
{hero("AI that takes work off your team's plate.",
      "We help small and mid-sized businesses put AI agents to work — from teaching your team to build "
      "their own, to building and running an AI employee for you.", "home", "AI agents & automation",
      img="hero", alt="Isometric illustration of an AI agent handling documents, email, calendar and reports",
      accent="off your team's plate.", second=("services/", "See the five services"))}
{stats()}
<section class="section tone-lime"><div class="wrap split">
  <div class="frame frame-paper">{art(slug, "sprint", "Isometric illustration of a laptop prototype, a roadmap and a checklist")}</div>
  <div><p class="eyebrow">Start here</p><h2>The Discovery <span class="hl">Sprint</span></h2>
  <p class="big">A short, paid sprint on one of your workflows. In 2–4 weeks you get a working prototype, a costed
  build plan and a clear go/no-go — before you commit to anything bigger.</p>
  <div class="actions"><a class="btn btn-ink" href="discovery-sprint/">How the sprint works →</a></div></div>
</div></section>
<section class="section"><div class="wrap">
  {section_head("Five ways to work with us", "Do it yourself, do it together, or let us do it.",
                "Start wherever fits. Most clients begin small and move up as they see results.", accent="let us do it.")}
  {ladder(slug)}
</div></section>
<section class="section tone-lime"><div class="wrap">
  {section_head("Use cases", "Agents for operations, growth and finance teams.", accent="finance teams.")}
  {use_case_cards(slug, only=[u["slug"] for u in USE_CASES[:8]])}
  <p class="more"><a class="link" href="use-cases/">All use cases →</a></p>
</div></section>
<section class="section"><div class="wrap">
  {section_head("Who we help", "Built for businesses without an AI team.", accent="without an AI team.")}
  {rows(slug, [(p["slug"], p["nav"], p["lead"]) for p in PLAYS])}
</div></section>
<section class="section tone-lime"><div class="wrap">
  {section_head("The 4S check", "Where is your business with AI?",
                "Four stages, eight yes-or-no questions, about two minutes. Find the one step that moves you forward.",
                accent="with AI?")}
  {stage_cards(slug)}
  <p class="more"><a class="link" href="{MATURITY_SLUG}#check">Take the 4S check →</a></p>
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
      "Pick the level of help that fits — and change it as you go.", "services", "Services", slug=slug,
      accent="work with us")}
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
        nxt = f'<p class="more"><a class="link" href="{rel(slug, n["slug"])}">Need more? See {e(n["nav"])} →</a></p>'
    ref = slug.split("/")[1]
    main = f"""
{hero(t["title"], t["lead"], ref, f'Service 0{i + 1} · {t["tier"]}', slug=slug, img=t["art"],
      alt=f'Isometric illustration for {t["nav"]}')}
<section class="section tone-lime"><div class="wrap split">
  <div class="panel"><h2>Who it's for</h2><p class="big">{e(t["for"])}</p><h2>What you get</h2><ul class="ticks">{get}</ul>{nxt}</div>
  <div class="panel"><h2>How it works</h2><ol class="steps">{how}</ol></div>
</div></section>
<section class="section"><div class="wrap">{faq_html(t["faq"])}</div></section>
<section class="section tone-lime"><div class="wrap">{section_head("All services", "Five ways to work with us", accent="work with us")}{ladder(slug, highlight=slug)}</div></section>
{cta_band(ref + "-band")}"""
    return page(slug, t["title"], t["description"], main,
                ld=[service_ld(slug, t["title"], t["description"]), faq_ld(t["faq"])], ref=ref)


def build_play(p):
    slug = p["slug"]
    body = "".join(f"<p>{e(x)}</p>" for x in p["body"])
    uses = ""
    if p.get("uses"):
        assert set(p["uses"]) <= {u["slug"] for u in USE_CASES}, f'unknown use case in {slug}: {p["uses"]}'
        uses = (f'<section class="section tone-lime"><div class="wrap">'
                f'{section_head("Use cases", "What we usually build first", accent="build first")}'
                f'{use_case_cards(slug, only=p["uses"])}</div></section>')
    main = f"""
{hero(p["title"], p["lead"], p["ref"], "Who we help", slug=slug, img=p["art"], alt=f'Isometric illustration for {p["nav"]}')}
<section class="section tone-lime"><div class="wrap narrow prose big">{body}</div></section>
<section class="section"><div class="wrap">{section_head("Where to start", "Where clients usually start", accent="usually start")}{ladder(slug, only=p["tiers"])}
<p class="more"><a class="link" href="{rel(slug, 'services/')}">See all five services →</a></p></div></section>
{uses}
{cta_band(p["ref"] + "-band")}"""
    return page(slug, p["title"], p["description"], main, ref=p["ref"])


def use_case_cards(slug, exclude=None, only=None):
    cards = "".join(
        f'<a class="card" href="{rel(slug, u["slug"])}"><span class="tag">Use case</span>'
        f'<h3>{e(u["nav"])}</h3><p>{e(u["lead"])}</p><span class="arrow">→</span></a>'
        for u in USE_CASES if u["slug"] != exclude and (only is None or u["slug"] in only))
    return f'<div class="cards cards-uc">{cards}</div>'


def build_use_cases():
    slug = "use-cases/"
    desc = ("AI agents for operations, sales and finance teams: quote and RFQ intake, order entry, document "
            "intake, inbox triage, renewals, market intelligence, prospect research, planning and financial reporting.")
    main = f"""
{hero("AI agents for operations, growth and finance teams", "Agents that do the reading, re-keying, tracking "
      "and reporting — so your people can spend their time on the decisions.", "use-cases",
      "Use cases", slug=slug, tone="lime")}
<section class="section"><div class="wrap">{use_case_cards(slug)}
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
<section class="section"><div class="wrap">{faq_html(u["faq"])}</div></section>
<section class="section tone-lime"><div class="wrap">{section_head("More", "More use cases", accent="use cases")}{use_case_cards(slug, exclude=slug)}</div></section>
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
      "and a clear go/no-go — before you commit to anything bigger.", "sprint", "Start here", slug=slug,
      img="sprint", alt="Isometric illustration of a laptop prototype, a roadmap and a checklist", accent="Sprint",
      second=(MATURITY_SLUG, "Not sure? Take the 4S check"))}
<section class="section tone-lime"><div class="wrap split">
  <div class="panel"><h2>What you walk away with</h2><ul class="ticks">
    <li>A working prototype on your own process</li><li>A costed, phased build plan</li>
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
            "Strategy, Solution, Scale or Sustain, and show the one step that moves you forward.")
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
<div class="cards cards-uc">{cards}</div></div></section>
<section class="section tone-lime"><div class="wrap split">
  <div><h2>Where we work</h2><p class="big">We're based in Ontario, Canada, and work with clients across Canada and
  the United States, online or on site.</p></div>
  <div><h2>Who you'll talk to</h2><p class="big">Every engagement starts with our business development lead.</p>
  <div class="actions"><a class="btn btn-ink" href="{rel(slug, ASAL['slug'])}">Meet our VP of Business Development →</a></div></div>
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
<section class="hero tone-paper"><div class="wrap hero-split person">
  <div class="hero-copy">
    <p class="eyebrow">{e(role)}</p>
    <h1>{e(name)}</h1>
    <p class="lead">Asal leads business development at {BRAND}. She is the first person most clients speak to,
    and stays their point of contact from the first conversation through delivery and beyond.</p>
    <p class="big">She works with owners and leadership teams to find where AI can take real work off their people —
    and is just as quick to say when it can't. Her job is to make sure every engagement starts at the
    right size, with a clear outcome both sides can measure.</p>
    <div class="actions">{contact('asal', 'Book a conversation with Asal')}
      <a class="btn btn-ghost" href="mailto:{EMAIL_SALES}">{EMAIL_SALES}</a></div>
  </div>
  <div class="frame frame-photo"><picture><source srcset="{rel(slug, 'public/team/asal.webp')}" type="image/webp" />
  <img src="{rel(slug, 'public/team/asal.jpg')}" alt="{e(name)}, {e(role)} at {BRAND}" width="720" height="900" fetchpriority="high" /></picture></div>
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
           ("discovery-sprint/", build_sprint(), "Discovery Sprint", "The paid sprint most engagements start with."),
           (MATURITY_SLUG, build_maturity(), "The 4S check",
            "Where is your business with AI? Eight questions place one workflow at Strategy, Solution, Scale or "
            "Sustain.")]
    out += [(t["slug"], build_tier(i), t["title"], t["description"]) for i, t in enumerate(TIERS)]
    out += [("use-cases/", build_use_cases(), "AI Agent Use Cases", "Agents for operations, growth and finance teams.")]
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
