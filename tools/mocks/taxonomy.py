"""Browse facets and hub-page copy for visionzlab.com/use-cases/.

These hub pages are indexed, branded marketing pages, so every intro follows the copy rules:
plain description of the work and where an AI agent helps, a person approves every decision,
no claims of results, savings, accuracy or speed, no names of people, companies or products,
no legal or clinical work, and regulated advice stays with the licensed person.

FUNCTIONS, SKILLS and TASKS map a facet id to its display name and intro.
INDUSTRY_SEO maps each industry id (a module in cases/) to its title audience and intro.
MAP assigns every case slug to 1-2 functions, 2-4 skills and 1-3 tasks.
Plain data, standard library only.
"""

FUNCTIONS = {
    "finance": dict(
        name="Finance and accounting",
        intro="Finance teams spend their days moving numbers between invoices, statements and the ledger. "
              "An AI agent reads the paperwork, matches it to orders and payments, suggests coding and drafts the "
              "entries, then lists anything that doesn't tie. Your controller or bookkeeper approves every posting, "
              "payment and adjustment before it reaches the books."),
    "sales": dict(
        name="Sales and quoting",
        intro="Quoting and order work starts with messy requests: emails, PDFs, spreadsheets and phone notes. An AI "
              "agent pulls out what the customer asked for, matches it to your catalogue and price rules, and prepares "
              "a first version of the quote or proposal with gaps called out. A salesperson sets every price, date and "
              "discount and decides what goes out."),
    "service": dict(
        name="Customer service",
        intro="Customer messages arrive through inboxes, portals, chat and the phone, and each one needs the right "
              "owner and a sensible reply. An AI agent logs and sorts them, finds the order or account behind each one "
              "and drafts a response from your policies. Service staff own every customer conversation and decide each "
              "refund, credit or exception."),
    "operations": dict(
        name="Operations and fulfilment",
        intro="Fulfilment runs on paperwork that has to agree: orders, receiving counts, delivery tickets, schedules "
              "and work orders. An AI agent checks each document against the others and your rules, prepares the "
              "next record and holds anything that doesn't line up. Supervisors and dispatchers release the work, "
              "book the jobs and settle each exception."),
    "purchasing": dict(
        name="Purchasing and suppliers",
        intro="Buying well means comparing supplier quotes, price files and certificates that never arrive in the "
              "same format. An AI agent puts them on a common basis, drafts purchase orders and supplier chases, and "
              "tracks what is late or expiring. Buyers choose the supplier, set quantities and approve every order "
              "and request that leaves the building."),
    "compliance": dict(
        name="Compliance, quality and risk",
        intro="Quality and compliance work is mostly careful checking: is the file complete, does the record match "
              "the rule, has anything expired? An AI agent runs those checks against your own checklists and "
              "policies, cites where each finding came from and marks what it can't confirm. Your quality, "
              "compliance or risk lead judges each finding and signs off."),
    "people": dict(
        name="HR, staffing and payroll",
        intro="Staffing and HR teams handle timesheets, onboarding packets, certificates and a steady stream of policy "
              "questions. An AI agent checks hours and paperwork against your rules, tracks expiry dates, handles "
              "routine handbook questions with the relevant passage and prepares the payroll batch with exceptions "
              "listed. HR and payroll staff approve each batch, file and reminder, and every hiring decision stays with "
              "them."),
    "marketing": dict(
        name="Marketing and communications",
        intro="Marketing teams turn briefs, listings and product details into copy, campaign reports and "
              "announcements. An AI agent drafts from your templates and brand rules, checks each request is "
              "complete, and pulls campaign numbers into one report with anomalies flagged. Your marketers edit the "
              "words, decide the message and approve everything before it is published or sent."),
    "leadership": dict(
        name="Leadership and reporting",
        intro="Leaders need a clear weekly or monthly picture without someone rebuilding it by hand. An AI agent "
              "gathers figures from your systems, lays out results against goals and budget, and writes a plain summary "
              "that marks any number it couldn't verify. The owners of each figure check it, and leadership decides "
              "what the results mean and what happens next."),
    "it": dict(
        name="IT and security",
        intro="IT and security teams answer tickets, reconcile licences and fill in long security questionnaires. An AI "
              "agent sorts tickets by the response times you have agreed, compares licence bills with the people and "
              "devices actually using them and prepares questionnaire responses from policies you have approved, citing "
              "each one. Technicians and the security lead confirm each answer, change and priority before anything is "
              "sent."),
}

SKILLS = {
    "extract": dict(
        name="Reading and extracting documents",
        intro="Invoices, forms, scans and emails hold the fields your systems need, buried in different layouts. "
              "The agent reads each document, pulls out those fields, links every value back to where it appears on "
              "the page and marks anything it is unsure of. A person fills in or confirms the uncertain values "
              "before a record is created."),
    "match": dict(
        name="Matching and reconciliation",
        intro="Matching work compares one set of records with another: invoices with orders and receipts, payments "
              "with open items, statements with the ledger. The agent lines them up, explains every difference it "
              "finds and proposes how each could be resolved. Your team decides which differences are acceptable and "
              "approves every posting or correction."),
    "check": dict(
        name="Checking against your rules",
        intro="Many reviews are a checklist applied the same way every time. The agent tests each file or record "
              "against the rules you write down, such as required documents, dates, limits and thresholds, and shows "
              "the evidence behind every pass or flag. The reviewer who owns the rule makes the final call on "
              "anything flagged."),
    "triage": dict(
        name="Sorting and routing",
        intro="Shared queues fill with requests that belong to different people and carry different urgency. The "
              "agent reads each item, tags its type and priority using your rules, links related messages and sends "
              "it to the right owner with a suggested next step. Staff can change any routing, and nothing is "
              "answered or closed without them."),
    "draft": dict(
        name="Drafting replies and documents",
        intro="Replies, reminders, quotes, notices and first drafts of reports take time to write from scratch. The "
              "agent writes them from your templates, past examples and the facts in the file, and lists anything it "
              "had to leave open. Someone on your team edits each draft and decides whether and when it is sent."),
    "report": dict(
        name="Building reports",
        intro="Recurring reports mean pulling the same figures from several places, laying them out and explaining what "
              "moved. The agent assembles tables and charts, works out variances against plan or last period and writes "
              "first-draft notes on the biggest movements, each tied to its source. Nobody else sees the report until "
              "the person responsible for it has reviewed the numbers and the wording."),
    "research": dict(
        name="Research and monitoring",
        intro="Keeping an eye on competitors, prospects, suppliers or shipments means checking many sources again "
              "and again. The agent watches the sources you name, notices what changed and writes a short summary "
              "where every point links back to where it was found. Your team reads the summary and decides what "
              "deserves action."),
    "answer": dict(
        name="Answering questions from your documents",
        intro="Staff and customers ask questions that your manuals, policies and past answers already cover. The agent "
              "replies in plain language from the documents you approve, cites the page or passage behind each reply "
              "and says so plainly when nothing approved covers the question. Whoever owns each document decides how "
              "such gaps get filled, and nothing new is treated as policy until they sign it off."),
    "schedule": dict(
        name="Scheduling and reminders",
        intro="Renewal dates, expiries, condition deadlines and service visits are easy to miss when they live in "
              "many files. The agent reads the dates out of the documents, builds a calendar of what is due and "
              "drafts the reminders ahead of time. A person confirms each date and approves every reminder before it "
              "goes out."),
    "forecast": dict(
        name="Forecasting and planning",
        intro="Planning questions need numbers pulled together from orders, stock, receivables and schedules. The "
              "agent rolls the forecast forward, runs the scenarios you ask for and shows every assumption with its "
              "source, marking the ones that are estimates. The planner or finance lead owns the assumptions and "
              "decides what to do about any gap it shows."),
}

TASKS = {
    "invoices": dict(
        name="Invoices and bills",
        intro="Invoices arrive from suppliers by email and post, and your own invoices have to be built from job "
              "records, contracts and usage. The agent reads, matches and codes incoming bills and drafts outgoing "
              "ones from the source records, flagging any line that doesn't agree. Accounts payable and billing "
              "staff approve every invoice and every payment."),
    "purchase-orders": dict(
        name="Purchase orders",
        intro="Purchase orders sit at the centre of buying and receiving, and every invoice and delivery should "
              "trace back to one. The agent drafts orders from reorder needs, compares invoices and customer POs "
              "with what was agreed, and lists late or short deliveries. Buyers approve each order and decide how to "
              "handle every mismatch."),
    "quotes": dict(
        name="Quotes and RFQs",
        intro="Requests for quote come in as drawings, emails, spreadsheets and photos, often with something "
              "missing. The agent pulls out the items and specifications, finds similar past work, applies your "
              "price book or rate card and drafts the quote with its open questions. An estimator or salesperson "
              "sets the final price and lead time."),
    "contracts": dict(
        name="Contracts and leases",
        intro="Contracts and leases carry the dates, rates, allowances and recovery rules that billing and "
              "operations rely on. The agent reads those terms into a summary and a calendar of key dates, and points "
              "out where an amendment and the original seem to disagree. The contract owner confirms each term, and "
              "interpreting any clause stays with your team."),
    "timesheets": dict(
        name="Timesheets and hours",
        intro="Hours come in as portal exports, spreadsheets, punch reports and photos of paper sheets. The agent "
              "checks each entry against schedules, rates and approvals, flags overtime and missing punches, and "
              "prepares payroll and billing lines from the approved hours. Payroll staff and managers settle each "
              "exception and approve the batch."),
    "receipts": dict(
        name="Receipts and expenses",
        intro="Receipts turn up as phone photos, email attachments and paper in an envelope. The agent reads each "
              "one, matches it to a bank or card line, suggests a category from your rules and points out purchases "
              "outside policy. A bookkeeper confirms the categories and decides what to ask about before anything is "
              "posted."),
    "shared-inbox": dict(
        name="Shared inbox and enquiries",
        intro="A shared inbox mixes questions, requests, complaints and documents, and some of them are urgent. The "
              "agent logs each message, works out what it is and who owns it, routes it and prepares a suggested reply "
              "from your templates and the customer's history. Your team reviews each draft before it is sent, so no "
              "message leaves the inbox on its own."),
    "applications": dict(
        name="Applications and forms",
        intro="Applications, enrolments and account-opening forms stall when a page, signature or supporting "
              "document is missing. The agent checks each file against the requirement list, compares names, dates "
              "and figures across documents and drafts the request for whatever is missing. The person responsible "
              "for the file decides when it is complete and makes every approval decision."),
    "claims": dict(
        name="Claims and disputes",
        intro="Warranty claims, customer deductions, billing disputes and complaints to suppliers all need the evidence "
              "gathered and the story told clearly. The agent pulls together the repair order, delivery proof, contract "
              "terms, inspection result or field notes behind each item, compares them with what is being claimed and "
              "drafts the submission or request. The licensed or authorised person decides every claim, deduction and "
              "settlement."),
    "renewals": dict(
        name="Renewals and follow-up",
        intro="Renewals, chases and follow-ups slip when the dates live in a book of business, a spreadsheet or "
              "someone's memory. The agent builds a list of what is coming due or overdue, checks consent before any "
              "outreach and drafts each reminder or follow-up with what the other side needs to send. Your staff decide "
              "who is contacted, and where the work is regulated, advice comes only from the licensed person."),
    "statements": dict(
        name="Statements and reconciliations",
        intro="Statements and reconciliations compare what someone else says happened with what your books show. The "
              "agent compares each statement, remittance or settlement with your ledger line by line, lists missing "
              "items, duplicates and rate differences and drafts a query to the other party for each one. Finance "
              "decides every adjustment and sends any query."),
    "shipping": dict(
        name="Shipping and delivery documents",
        intro="Bills of lading, packing lists, delivery tickets, proofs of delivery and manifests all have to agree "
              "with the order and with each other. The agent reads them, compares quantities, weights and "
              "references, and keeps a list of what is short, damaged or still missing. Shipping and receiving leads "
              "confirm counts and send every notice."),
    "returns": dict(
        name="Returns and credits",
        intro="Returns, recalls and credits depend on finding the original order or lot and applying the right "
              "policy. The agent matches each request or notice to the order, invoice or stock on hand, checks it "
              "against your return rules and drafts the RMA, credit request or pull list. Staff approve every return, "
              "refund and credit claim."),
    "product-data": dict(
        name="Product and price data",
        intro="Product records and price files change constantly as suppliers send new sheets and costs move. The "
              "agent reads vendor files and engineering changes, builds draft item records, compares new costs with "
              "current prices against your margin targets and lists missing attributes. Merchandisers and pricing "
              "managers set every price and approve each record before import."),
    "certificates": dict(
        name="Certificates, permits and expiries",
        intro="Certificates, permits, licences and ID documents all expire, and a lapse can stop a job, placement or "
              "shipment. The agent reads the scope and expiry date of each document, keeps a register, compares it with "
              "upcoming work and drafts a request for the replacement well before the date. The compliance owner "
              "accepts each document and decides what happens when one lapses."),
    "proposals": dict(
        name="Proposals, grants and tenders",
        intro="Tenders, grant calls and RFPs come with mandatory requirements, scoring criteria and deadlines that are "
              "easy to miss. The agent lists every requirement against your evidence, drafts sections from past "
              "proposals and approved material, and marks where each figure came from. Someone senior on your team "
              "makes the go or no-go call, sets the price and signs what is submitted."),
    "month-end": dict(
        name="Month-end close and reporting",
        intro="Month-end and year-end close means chasing open tasks, explaining movements and building the same "
              "pack again. The agent tracks the close checklist, finds account movements above your threshold, "
              "drafts explanations from the documents behind them and fills the report template. The controller "
              "reviews every explanation and signs off the close."),
    "collections": dict(
        name="Payments and collections",
        intro="Cash comes in through bank feeds, cheques, cards and remittance emails that rarely match invoices one "
              "to one. The agent matches payments and gifts to open items, proposes postings, researches short "
              "payments and drafts reminders in a tone that fits each account's history. Receivables staff approve "
              "every posting and decide who is chased."),
    "work-orders": dict(
        name="Work orders and scheduling",
        intro="Service requests, maintenance calls and production demand all end up as work orders on someone's "
              "schedule. The agent identifies the asset or job, suggests urgency, a slot and a technician or "
              "machine, and drafts the work order and the customer update. Dispatchers and planners confirm every "
              "booking and approve the schedule."),
    # Added: the four largest clusters of cases that none of the base tasks described honestly.
    "orders": dict(
        name="Customer orders",
        intro="Customer orders arrive through email, portals, online stores, EDI files and the odd handwritten list. "
              "The agent enters each order, checks price, stock, credit, address and cut-off times against your "
              "records, and puts anything that doesn't fit on hold with the reason attached. Order desk staff release "
              "each order and resolve every hold."),
    "policies": dict(
        name="Policies, manuals and standards",
        intro="Policies, manuals, procedures and external standards hold answers people need every day, but they "
              "are long and scattered. The agent answers questions from the approved versions with the passage "
              "cited, maps documents against the standards you follow and finds every procedure affected by a "
              "change. Document owners approve each change and every new answer."),
    "report-packs": dict(
        name="Management and client reports",
        intro="Weekly briefs, monthly packs and quarterly reviews pull from the same sources each time. The agent "
              "gathers the figures, compares them with plan, peers or last period, writes a draft narrative and links "
              "every number to where it came from. The report owner edits that narrative, checks the figures and "
              "decides who receives it."),
    "campaigns": dict(
        name="Campaigns, listings and leads",
        intro="Listings, promotions, rollout memos and local lead lists all start from details scattered across "
              "forms, photos and public sources. The agent drafts copy and storyboards from your templates, checks "
              "each piece against your advertising rules and builds sourced lists of prospects. Your marketing team "
              "edits and approves every piece and decides whom to contact."),
}

INDUSTRY_SEO = {
    "core": dict(
        audience="small and mid-sized businesses",
        intro="Most businesses share the same paperwork: quotes, orders, invoices, a busy inbox and the monthly "
              "report. An AI agent reads what arrives, checks it against your records and drafts the next step, from "
              "a quote to a variance commentary. Your team approves every price, reply and number, and the agent "
              "marks what it isn't sure of."),
    "knowledge": dict(
        audience="growing teams",
        intro="As a team grows, the same questions reach the same few people. An AI agent answers from your "
              "approved policies, manuals and training material, cites the source for every answer and logs the "
              "questions the documents don't cover. Page owners review those gaps and approve each new answer before "
              "it becomes part of the library."),
    "finance_ops": dict(
        audience="finance teams",
        intro="Payables, receivables, billing, payroll prep and cash forecasting all depend on documents that have "
              "to agree. An AI agent matches invoices, payments and statements, drafts bills and reminders and rolls "
              "the forecast forward, listing every exception with its evidence. Controllers and clerks approve each "
              "posting, payment and adjustment."),
    "accounting": dict(
        audience="accounting and bookkeeping firms",
        intro="Firms spend busy season collecting documents, reconciling accounts and building client packs. An AI "
              "agent files and reads what clients upload, matches receipts to bank lines, applies your review rules "
              "to trial balances and drafts reminders for what is missing. The accountant applies professional "
              "judgment, answers every tax question and signs off the work."),
    "insurance": dict(
        audience="insurance and mortgage brokerages",
        intro="Brokerage desks juggle carrier notices, applications, renewals, certificates and commission "
              "statements. An AI agent reads each document, keeps pending lists and renewal calendars, checks files "
              "for completeness and drafts the paperwork and outreach. All insurance and mortgage advice comes from "
              "the licensed broker, advisor or agent, who approves everything sent."),
    "manufacturing": dict(
        audience="manufacturers and machine shops",
        intro="Job shops and fabricators live on RFQs, customer POs, work orders and shipping paperwork. An AI agent "
              "reads drawings and requests, finds similar past jobs, checks POs against quotes and assembles "
              "certificates of conformance and packing lists. Estimators set prices and lead times, planners approve "
              "the schedule and quality signs every shipment."),
    "distribution": dict(
        audience="distributors and wholesalers",
        intro="Distributors handle supplier price files, rebate remittances, online orders and returns in volume. "
              "An AI agent compares new costs with your margin targets, reconciles rebates against program terms, "
              "carries online orders through to labels and matches return requests to the original order. Buyers, "
              "finance and service staff approve every price, payout and RMA."),
    "professional": dict(
        audience="consultants and supply chain teams",
        intro="Planners and consultants produce exception lists, monthly packs, status reports, data clean-ups and "
              "proposals under deadline. An AI agent sorts planning exceptions, drafts the S&OP pack and weekly "
              "status from your logs, finds duplicate master records and drafts proposal sections from past work. "
              "Practice leads and planners edit, price and own every deliverable."),
    "real_estate": dict(
        audience="real estate brokerages",
        intro="Brokerages run on listing paperwork, condition dates, deal packages, marketing requests and a busy "
              "front desk. An AI agent drafts listing entries, tracks every condition deadline, checks deal files "
              "against your checklist and drafts marketing pieces from approved templates. Agents and the broker of "
              "record review each item, and they submit, sign and advise."),
    "field_service": dict(
        audience="trades and field service companies",
        intro="Service, construction and trucking offices handle repair quotes, dispatch, permits, subcontractor "
              "certificates, RFIs and load paperwork. An AI agent prices from your price book, proposes slots and "
              "routes, tracks expiry dates and keeps the RFI log current. The office, the dispatcher and the project "
              "manager confirm each booking, price and response."),
    "food": dict(
        audience="café and restaurant groups",
        intro="Head office for a café or restaurant group handles supplier invoices, ordering, franchise royalties, "
              "store audits and the weekly numbers. An AI agent matches invoices to deliveries, drafts orders against "
              "par levels, recomputes royalties and writes each café's weekly brief. Purchasing, finance and area "
              "managers approve every order, adjustment and message."),
    "public_sector": dict(
        audience="public-sector bid teams",
        intro="Bid teams face long tenders with addenda, mandatory requirements and strict scoring, and public "
              "offices review drawings against detailed checklists. An AI agent builds the compliance matrix and "
              "question list, or checks each drawing sheet against the review checklist with sheet references. The "
              "bid lead decides whether to bid and signs; the plans examiner issues every finding."),
    "logistics_3pl": dict(
        audience="3PL warehouses",
        intro="Third-party warehouses reconcile inbound trailers against ASNs, bill storage and handling from rate "
              "cards and release orders before carrier cut-offs. An AI agent matches counts, builds invoice lines "
              "from activity logs and checks addresses, stock and service levels before each wave. Warehouse leads "
              "confirm counts, set missing rates and release every order."),
    "freight_customs": dict(
        audience="freight forwarders and customs brokers",
        intro="Forwarders and customs brokers deal with incomplete quote requests, commercial invoices, packing "
              "lists and constant carrier updates. An AI agent pulls out shipment details, lists what's missing, "
              "cross-checks entry documents and tracks milestones against promised dates. Forwarders set every rate, "
              "and the licensed customs broker classifies each line and files the entry."),
    "retail": dict(
        audience="retailers and online stores",
        intro="Retail teams set up products from vendor sheets, answer order and return questions and review store "
              "performance every week. An AI agent builds draft product records, finds the order behind each "
              "customer message and drafts the weekly store pack with variances. Merchandisers price, service staff "
              "approve refunds and district managers decide actions."),
    "hospitality": dict(
        audience="hotels and resorts",
        intro="Hotels field group enquiries, read guest reviews every day and close each night with an audit. An AI "
              "agent pulls dates, room blocks and space needs from enquiries, sorts reviews by theme with draft "
              "responses and checks rate codes, comps and cashier totals. Sales managers set rates, managers approve "
              "replies and the controller signs off the audit."),
    "auto_dealers": dict(
        audience="automotive dealerships",
        intro="Dealerships need complete deal jackets before funding, clean warranty claims from repair orders and "
              "a steady flow of trade-ins ready for sale. An AI agent checks every document in the jacket, drafts "
              "warranty claims with labour operations and builds the reconditioning summary and listing draft. F&I, "
              "service and used-vehicle managers submit, price and decide."),
    "property_mgmt": dict(
        audience="property management companies",
        intro="Property managers handle maintenance requests at all hours, long commercial leases and the year-end "
              "recovery calculation. An AI agent sorts requests by urgency and drafts work orders, abstracts rent "
              "steps and critical dates from leases, and drafts each tenant's recovery statement. The property "
              "manager dispatches, approves spending and signs off every statement."),
    "agriculture": dict(
        audience="farm co-ops and agribusinesses",
        intro="Co-ops and agribusinesses settle grain deliveries, take crop-input orders in every form and answer "
              "buyers' traceability requests. An AI agent matches scale tickets to contracts, enters orders with "
              "stock and credit checks, and traces a lot back to fields and spray records. The grain manager, "
              "agronomist and food safety lead make each decision."),
    "fuel_distribution": dict(
        audience="fuel and propane distributors",
        intro="Fuel and propane distributors price delivery tickets, plan routes from tank monitors and prepare "
              "monthly tax workpapers. An AI agent prices each delivery from contract or posted prices, estimates "
              "when tanks reach the reorder point and checks every exempt sale for a certificate. Billing, dispatch "
              "and the controller approve invoices, routes and returns."),
    "education": dict(
        audience="colleges and training providers",
        intro="Colleges and training providers check admissions files, answer student questions and review course "
              "outlines against program outcomes. An AI agent compares each applicant's file with program "
              "requirements, answers routine questions from published policies with a citation and maps course "
              "outcomes for review. Admissions staff, student services and faculty make every decision."),
    "nonprofit": dict(
        audience="charities and non-profits",
        intro="Charities write grant applications, process gifts and report back to funders, often with a small "
              "team. An AI agent drafts application sections from program data, matches gifts to donors under your "
              "receipting policy and compiles impact figures into the funder's template with sources. Staff and the "
              "board review every figure, receipt and submission."),
    "staffing": dict(
        audience="staffing and recruitment agencies",
        intro="Agencies compare resumes with job orders, turn approved timesheets into payroll and invoices and "
              "keep worker documents current. An AI agent lists the evidence and gaps for each resume, checks hours "
              "against rates and approvals and tracks certificate expiries against placements. Recruiters, payroll "
              "and compliance staff decide every shortlist, batch and placement."),
    "agencies": dict(
        audience="marketing and creative agencies",
        intro="Agencies turn client emails and kickoff calls into briefs, build monthly campaign reports and bill "
              "retainers. An AI agent drafts the structured brief and open questions, assembles campaign numbers "
              "with first-draft commentary and tracks hours against each retainer. The account team owns every "
              "client conversation, overage decision and invoice."),
    "pharmacy": dict(
        audience="pharmacy back offices",
        intro="A pharmacy's back office matches wholesaler invoices to receiving counts, acts on recall and "
              "shortage notices and prices front-store promotions. An AI agent tracks credits owed, matches recalled "
              "lots to stock at each store and builds price changes and shelf tags. Pharmacy staff approve payments, "
              "pull lists and every price, and the work stays in the back office."),
    "med_device": dict(
        audience="medical device manufacturers",
        intro="Device makers run supplier corrective actions, document change orders and distributor orders with "
              "lot traceability. An AI agent drafts supplier requests and tracks responses, finds every procedure a "
              "change touches and assigns lots to orders by your rules. Quality and regulatory staff assess each "
              "change, judge every response and release orders."),
    "lending": dict(
        audience="credit unions and lenders",
        intro="Lenders spread borrower financial statements, refresh member identification files and test "
              "covenants every quarter. An AI agent spreads statements into your credit template, finds expired or "
              "missing items in member files and checks each covenant against the loan agreement. The analyst writes "
              "the recommendation, compliance rules on escalations and the credit committee decides."),
    "wealth": dict(
        audience="wealth and financial planning firms",
        intro="Advisory practices prepare for client reviews, write up meetings and process new account paperwork. "
              "An AI agent lists what changed since the last meeting, drafts the file note and follow-up from what "
              "was said and checks forms for missing signatures or mismatched details. All advice comes from the "
              "licensed advisor, and operations approves every account."),
    "msp": dict(
        audience="IT managed service providers",
        intro="Managed service providers triage tickets and alerts, reconcile monthly licence bills and prepare "
              "quarterly reviews. An AI agent sets priority from your service levels, matches licences to active "
              "users and client billing and drafts the review pack from ticket and patch data. Technicians, account "
              "managers and the vCIO confirm each priority, billing change and recommendation."),
    "saas": dict(
        audience="software and SaaS companies",
        intro="Software companies answer security questionnaires, work support queues and watch accounts "
              "approaching renewal. An AI agent drafts questionnaire answers from your approved library with "
              "sources, tags ticket area and severity with draft replies and gathers renewal risk evidence. The "
              "security lead, support agents and customer success managers approve every answer and plan."),
    "environmental": dict(
        audience="environmental and waste firms",
        intro="Waste and environmental firms reconcile manifests with scale tickets, bill route services and "
              "report against their permits each year. An AI agent matches the three documents per load, prices "
              "extras from each contract and assembles the permit report with readings flagged against limits. The "
              "people who sign manifests, invoices and reports make every decision."),
    "beverage": dict(
        audience="breweries and beverage producers",
        intro="Beverage producers normalise distributor depletion reports, keep excise and production records and "
              "check labels before print. An AI agent converts each report to case equivalents and maps accounts, "
              "reconciles brewing, packaging and removals, and checks labels against your compliance checklist. The "
              "sales, finance and compliance leads confirm, file and approve."),
}


def _m(fn, skills, tasks):
    return dict(fn=fn, skills=skills, tasks=tasks)


MAP = {
    # accounting
    "acct-document-intake": _m(["finance", "service"], ["extract", "triage", "draft"], ["receipts", "statements"]),
    "acct-tb-analysis": _m(["finance"], ["check", "report", "draft"], ["month-end"]),
    "acct-vouching": _m(["finance", "compliance"], ["match", "extract"], ["invoices", "month-end"]),
    "acct-flexible-reporting": _m(["finance"], ["report", "match", "draft"], ["report-packs", "month-end"]),
    "bk-reconciliation-prep": _m(["finance"], ["match", "extract"], ["receipts", "statements", "month-end"]),
    "acct-year-end-chase": _m(["finance", "service"], ["check", "draft", "schedule"], ["renewals"]),
    # agencies
    "agency-brief-intake": _m(["marketing", "sales"], ["extract", "draft"], ["campaigns"]),
    "agency-campaign-report": _m(["marketing"], ["report", "draft"], ["report-packs", "campaigns"]),
    "agency-timesheet-billing": _m(["finance"], ["match", "check", "draft"], ["timesheets", "invoices", "contracts"]),
    # agriculture
    "ag-grain-tickets": _m(["purchasing", "finance"], ["match", "extract"], ["contracts", "statements", "shipping"]),
    "ag-input-orders": _m(["sales", "operations"], ["extract", "check", "triage"], ["orders"]),
    "ag-traceability-pack": _m(["compliance", "operations"], ["match", "check", "report"], ["shipping"]),
    # auto_dealers
    "auto-deal-jacket": _m(["finance", "compliance"], ["check", "match", "extract"], ["applications", "contracts"]),
    "auto-warranty-claims": _m(["service", "finance"], ["extract", "draft", "check"], ["claims"]),
    "auto-used-appraisal": _m(["sales", "operations"], ["extract", "draft"], ["product-data", "campaigns"]),
    # beverage
    "bev-distributor-depletions": _m(["sales", "leadership"], ["extract", "match", "report"], ["report-packs"]),
    "bev-excise-workpapers": _m(["finance", "compliance"], ["match", "check", "report"], ["month-end"]),
    "bev-label-approval": _m(["marketing", "compliance"], ["check", "draft"], ["campaigns", "policies"]),
    # core
    "quote-rfq-intake": _m(["sales"], ["extract", "match", "draft"], ["quotes"]),
    "document-intake": _m(["finance", "operations"], ["extract", "check"], ["invoices", "shipping", "applications"]),
    "market-intelligence": _m(["leadership", "marketing"], ["research", "report", "answer"], ["report-packs"]),
    "order-entry": _m(["sales", "operations"], ["extract", "check", "triage"], ["orders", "purchase-orders", "returns"]),
    "inbox-triage": _m(["service"], ["triage", "draft", "schedule"], ["shared-inbox"]),
    "renewals-follow-up": _m(["sales", "service"], ["schedule", "draft", "check"], ["renewals"]),
    "prospect-research": _m(["sales"], ["research", "report", "draft"], ["campaigns"]),
    "planning-okrs": _m(["leadership"], ["forecast", "report"], ["report-packs"]),
    "financial-reporting": _m(["finance", "leadership"], ["report", "match", "draft"], ["month-end", "report-packs"]),
    # distribution
    "dist-price-update": _m(["purchasing", "sales"], ["match", "check", "extract"], ["product-data"]),
    "dist-buying-group-remit": _m(["finance"], ["match", "check", "report"], ["statements", "collections"]),
    "ecom-order-to-label": _m(["operations"], ["check", "extract"], ["orders", "shipping"]),
    "dist-returns-intake": _m(["service"], ["match", "check", "draft", "triage"], ["returns", "shared-inbox"]),
    # education
    "edu-admissions-docs": _m(["service", "compliance"], ["check", "extract", "draft"], ["applications"]),
    "edu-student-inbox": _m(["service"], ["triage", "answer", "draft"], ["shared-inbox", "policies"]),
    "edu-course-outline": _m(["compliance"], ["match", "check", "report"], ["policies", "report-packs"]),
    # environmental
    "env-manifests": _m(["compliance", "operations"], ["match", "check", "extract"], ["shipping", "statements"]),
    "env-route-billing": _m(["finance"], ["extract", "match"], ["invoices", "contracts", "claims"]),
    "env-compliance-report": _m(["compliance"], ["report", "check", "extract"], ["certificates"]),
    # field_service
    "svc-repair-quote": _m(["sales", "service"], ["extract", "draft"], ["quotes", "work-orders"]),
    "ops-dispatch-booking": _m(["operations"], ["schedule", "triage", "draft"], ["work-orders", "invoices"]),
    "tl-rate-load-docs": _m(["sales", "operations"], ["extract", "draft"], ["quotes", "shipping"]),
    "con-doc-control": _m(["compliance", "operations"], ["extract", "check", "schedule"], ["certificates", "contracts"]),
    "con-rfi-submittal-log": _m(["operations"], ["triage", "schedule", "draft"], ["shared-inbox"]),
    "svc-maintenance-contracts": _m(["sales", "service"], ["extract", "schedule", "draft"], ["renewals", "contracts"]),
    # finance_ops
    "ap-three-way-match": _m(["finance", "purchasing"], ["match", "extract"], ["invoices", "purchase-orders"]),
    "ar-cash-application": _m(["finance"], ["match", "extract"], ["collections"]),
    "ar-collections": _m(["finance"], ["draft", "schedule"], ["collections"]),
    "ar-deductions": _m(["finance", "sales"], ["match", "check", "draft"], ["claims", "collections"]),
    "ar-invoice-audit": _m(["finance"], ["check", "match"], ["invoices", "returns"]),
    "ap-vendor-statement": _m(["finance"], ["match", "check", "draft"], ["statements", "invoices"]),
    "ap-job-cost-coding": _m(["finance", "operations"], ["match", "extract", "triage"], ["invoices"]),
    "pay-payroll-prep": _m(["people", "finance"], ["check", "extract"], ["timesheets"]),
    "ap-supplier-settlement": _m(["purchasing", "finance"], ["extract", "match", "draft"], ["statements"]),
    "bill-job-card": _m(["finance"], ["extract", "check", "draft"], ["invoices", "work-orders"]),
    "bill-contract-usage": _m(["finance"], ["extract", "match"], ["invoices", "contracts"]),
    "bill-freight-pod": _m(["finance", "operations"], ["match", "extract"], ["invoices", "shipping"]),
    "bill-progress": _m(["finance"], ["extract", "check", "draft"], ["invoices", "contracts"]),
    "sales-data-entry": _m(["sales", "operations"], ["extract", "check", "report"], ["orders", "report-packs"]),
    "fin-13wk-cash": _m(["finance", "leadership"], ["forecast", "report", "answer"], ["report-packs"]),
    # food
    "food-invoice-match": _m(["finance", "purchasing"], ["match", "extract"], ["invoices", "purchase-orders"]),
    "food-off-spec": _m(["purchasing", "compliance"], ["check", "match", "draft"], ["receipts"]),
    "food-rfq-compare": _m(["purchasing"], ["extract", "match"], ["quotes"]),
    "food-import-landed": _m(["purchasing", "finance"], ["extract", "match"], ["shipping", "invoices"]),
    "food-supplier-certs": _m(["compliance", "purchasing"], ["extract", "schedule", "draft"], ["certificates"]),
    "food-labour-esa": _m(["people", "operations"], ["check", "report"], ["timesheets"]),
    "food-repair-triage": _m(["operations"], ["triage", "extract", "draft", "schedule"], ["work-orders"]),
    "food-royalty-recompute": _m(["finance"], ["check", "match", "report"], ["statements", "invoices"]),
    "food-weekly-brief": _m(["leadership", "operations"], ["report", "draft"], ["report-packs"]),
    "food-audit-summary": _m(["compliance", "operations"], ["extract", "match", "report"], ["report-packs"]),
    "food-menu-engineering": _m(["leadership", "marketing"], ["research", "report", "answer"], ["product-data"]),
    "food-scenario": _m(["finance", "leadership"], ["forecast", "report", "answer"], ["report-packs"]),
    "food-mgmt-pack": _m(["finance", "leadership"], ["report", "draft"], ["month-end", "report-packs"]),
    "food-close-variance": _m(["finance"], ["match", "report", "draft"], ["month-end"]),
    "food-hst-checks": _m(["finance", "compliance"], ["check", "extract"], ["invoices"]),
    "food-catering-intake": _m(["sales", "operations"], ["extract", "draft", "schedule"], ["orders", "quotes"]),
    "food-branch-ordering": _m(["purchasing", "operations"], ["forecast", "draft", "schedule"], ["purchase-orders"]),
    "food-warehouse-replenish": _m(["purchasing"], ["forecast", "draft"], ["purchase-orders"]),
    "food-catering-leads": _m(["sales", "marketing"], ["research", "report"], ["campaigns"]),
    "food-franchisee-comms": _m(["marketing"], ["draft", "answer"], ["campaigns"]),
    "food-new-hire-paperwork": _m(["people"], ["check", "extract", "schedule"], ["certificates", "applications"]),
    "food-capex-register": _m(["finance"], ["extract", "report"], ["invoices"]),
    # freight_customs
    "ff-quote-request": _m(["sales"], ["extract", "check", "draft"], ["quotes"]),
    "cb-entry-prep": _m(["operations", "compliance"], ["extract", "match"], ["shipping", "invoices"]),
    "ff-shipment-tracking": _m(["operations", "service"], ["research", "draft", "schedule"], ["shipping"]),
    # fuel_distribution
    "fuel-delivery-tickets": _m(["finance"], ["extract", "check", "draft"], ["invoices", "shipping"]),
    "fuel-tank-monitoring": _m(["operations"], ["forecast", "schedule", "check"], ["work-orders"]),
    "fuel-tax-returns": _m(["finance", "compliance"], ["check", "report"], ["month-end", "certificates"]),
    # hospitality
    "hotel-group-rfp": _m(["sales"], ["extract", "check", "draft"], ["proposals", "quotes"]),
    "hotel-guest-reviews": _m(["service", "marketing"], ["triage", "draft", "report"], ["shared-inbox"]),
    "hotel-night-audit": _m(["finance"], ["check", "report"], ["statements"]),
    # insurance (insurance and mortgage brokerage)
    "ins-pending-requirements": _m(["operations", "service"], ["match", "draft", "triage"], ["applications", "renewals"]),
    "ins-file-completeness": _m(["compliance"], ["check", "match"], ["applications"]),
    "ins-edocs-desk": _m(["service"], ["extract", "triage", "draft"], ["shared-inbox"]),
    "ins-submission-package": _m(["sales"], ["extract", "check"], ["renewals", "applications"]),
    "ins-adjuster-report": _m(["operations"], ["extract", "draft"], ["claims"]),
    "ins-benefits-renewal": _m(["sales", "service"], ["extract", "report"], ["renewals"]),
    "ins-commission-recon": _m(["finance"], ["match", "check"], ["statements"]),
    "ins-inforce-change": _m(["service"], ["extract", "check", "draft"], ["applications"]),
    "ins-policy-check": _m(["compliance", "service"], ["match", "check", "report"], ["renewals"]),
    "ins-policy-change-intake": _m(["operations", "service"], ["extract", "check", "triage"], ["applications", "shared-inbox"]),
    "ins-coi-requests": _m(["service"], ["draft", "check"], ["certificates", "shared-inbox"]),
    "ins-group-enrolment": _m(["operations"], ["extract", "check"], ["applications"]),
    "ins-bordereaux": _m(["finance", "compliance"], ["extract", "check", "report"], ["statements"]),
    "ins-uw-triage": _m(["operations"], ["triage", "check", "extract"], ["applications"]),
    "ins-renewal-remarketing": _m(["sales"], ["match", "schedule", "draft"], ["renewals"]),
    "mtg-doc-checklist": _m(["service"], ["check", "draft"], ["applications", "renewals"]),
    "mtg-renewals": _m(["sales"], ["schedule", "draft", "check"], ["renewals"]),
    # knowledge
    "company-brain": _m(["people", "operations"], ["answer", "check"], ["policies"]),
    "staff-questions-onboarding": _m(["people"], ["answer", "check"], ["policies"]),
    # lending
    "lend-commercial-spreading": _m(["finance", "compliance"], ["extract", "check", "report"], ["statements", "applications"]),
    "lend-kyc-refresh": _m(["compliance", "service"], ["check", "draft", "schedule"], ["certificates", "applications"]),
    "lend-covenant-monitoring": _m(["compliance", "finance"], ["check", "report", "schedule"], ["contracts", "statements"]),
    # logistics_3pl
    "3pl-receiving-asn": _m(["operations"], ["match", "extract", "draft"], ["shipping"]),
    "3pl-billing-storage": _m(["finance"], ["extract", "match"], ["invoices"]),
    "3pl-order-exceptions": _m(["operations", "service"], ["check", "triage"], ["orders", "shipping"]),
    # manufacturing
    "mfg-rfq-first-pass": _m(["sales"], ["extract", "match", "draft"], ["quotes"]),
    "mfg-fit-check": _m(["sales"], ["check", "triage"], ["quotes"]),
    "mfg-similar-jobs": _m(["sales"], ["research", "match", "answer"], ["quotes"]),
    "mfg-po-check": _m(["sales", "operations"], ["match", "check"], ["purchase-orders", "quotes", "orders"]),
    "mfg-shipment-pack": _m(["operations", "compliance"], ["extract", "check", "draft"], ["shipping", "certificates"]),
    "mfg-submittal-pack": _m(["sales", "compliance"], ["match", "check"], ["product-data"]),
    "mfg-work-orders": _m(["operations"], ["schedule", "forecast"], ["work-orders", "orders"]),
    "mfg-engineering-release": _m(["operations"], ["extract", "check", "match"], ["product-data"]),
    "mfg-po-expedite": _m(["purchasing"], ["draft", "schedule"], ["purchase-orders", "renewals"]),
    "mfg-network-front-door": _m(["sales"], ["triage", "extract", "draft"], ["quotes", "shared-inbox"]),
    "mfg-plating-quote": _m(["sales"], ["extract", "draft"], ["quotes"]),
    # med_device
    "md-supplier-capa": _m(["compliance", "purchasing"], ["draft", "schedule", "triage"], ["claims"]),
    "md-doc-change": _m(["compliance"], ["match", "check", "draft"], ["policies"]),
    "md-distributor-orders": _m(["operations", "sales"], ["extract", "check", "answer"], ["orders", "purchase-orders"]),
    # msp
    "msp-ticket-triage": _m(["it", "service"], ["triage", "answer"], ["shared-inbox"]),
    "msp-licence-recon": _m(["finance", "it"], ["match", "check"], ["invoices", "statements"]),
    "msp-qbr-report": _m(["leadership", "it"], ["report", "draft"], ["report-packs"]),
    # nonprofit
    "np-grant-application": _m(["leadership"], ["draft", "check", "extract"], ["proposals"]),
    "np-donation-receipts": _m(["finance"], ["match", "check", "draft"], ["collections"]),
    "np-impact-report": _m(["leadership"], ["report", "extract"], ["report-packs", "proposals"]),
    # pharmacy (back office)
    "pharm-wholesaler-invoices": _m(["finance", "purchasing"], ["match", "draft"], ["invoices", "returns"]),
    "pharm-recall-notices": _m(["compliance", "operations"], ["match", "triage", "draft"], ["returns"]),
    "pharm-front-store-pricing": _m(["marketing", "sales"], ["check", "extract"], ["product-data", "campaigns"]),
    # professional
    "scm-exception-triage": _m(["operations", "purchasing"], ["triage", "draft", "forecast"], ["purchase-orders"]),
    "scm-sop-pack": _m(["leadership", "operations"], ["report", "forecast"], ["report-packs"]),
    "consult-data-cleanup": _m(["operations", "it"], ["match", "check"], ["product-data"]),
    "consult-status-reports": _m(["leadership"], ["report", "draft"], ["report-packs"]),
    "prof-proposal-draft": _m(["sales"], ["draft", "check", "extract"], ["proposals"]),
    # property_mgmt
    "pm-maintenance-requests": _m(["operations", "service"], ["triage", "draft"], ["work-orders", "shared-inbox"]),
    "pm-lease-abstract": _m(["operations", "finance"], ["extract", "schedule"], ["contracts"]),
    "pm-cam-reconciliation": _m(["finance"], ["match", "check", "draft"], ["statements", "contracts", "month-end"]),
    # public_sector
    "rfp-intake": _m(["sales", "compliance"], ["extract", "check", "draft"], ["proposals"]),
    "gov-drawing-review": _m(["compliance"], ["check", "draft"], ["applications", "certificates"]),
    # real_estate
    "re-listing-draft": _m(["sales", "operations"], ["extract", "draft", "schedule"], ["campaigns", "applications"]),
    "re-status-watch": _m(["operations"], ["extract", "schedule", "draft"], ["contracts"]),
    "re-deal-check": _m(["compliance"], ["check", "extract"], ["contracts", "applications"]),
    "re-design-request": _m(["marketing"], ["check", "draft", "triage"], ["campaigns"]),
    "re-tool-register": _m(["compliance", "it"], ["check", "draft"], ["policies"]),
    "re-training-video-search": _m(["people"], ["answer", "extract"], ["policies"]),
    "re-listing-video": _m(["marketing"], ["draft", "extract"], ["campaigns"]),
    "re-commission-statement": _m(["finance"], ["draft", "match"], ["statements", "invoices"]),
    "re-agent-onboarding": _m(["people", "leadership"], ["check", "report", "schedule"], ["applications", "report-packs"]),
    "re-front-desk": _m(["service"], ["triage", "schedule"], ["shared-inbox"]),
    "re-pm-report-rollup": _m(["leadership"], ["report", "check"], ["report-packs"]),
    # retail
    "retail-vendor-onboarding": _m(["purchasing"], ["extract", "check"], ["product-data"]),
    "retail-customer-service": _m(["service"], ["triage", "draft", "check"], ["returns", "shared-inbox"]),
    "retail-store-reports": _m(["leadership", "operations"], ["report", "draft"], ["report-packs"]),
    # saas
    "saas-security-questionnaire": _m(["it", "sales"], ["answer", "draft"], ["proposals", "policies"]),
    "saas-support-triage": _m(["service"], ["triage", "draft"], ["shared-inbox"]),
    "saas-renewal-risk": _m(["sales", "service"], ["research", "report", "forecast"], ["renewals"]),
    # staffing
    "staff-resume-shortlist": _m(["people"], ["match", "check"], ["applications"]),
    "staff-timesheets": _m(["people", "finance"], ["check", "match"], ["timesheets", "invoices"]),
    "staff-compliance-docs": _m(["compliance", "people"], ["extract", "schedule", "check"], ["certificates"]),
    # wealth
    "wealth-review-prep": _m(["service"], ["extract", "report"], ["report-packs"]),
    "wealth-meeting-notes": _m(["service"], ["draft", "extract"], ["renewals"]),
    "wealth-account-opening": _m(["operations", "compliance"], ["check", "extract"], ["applications"]),
}
