"""Hotels and hospitality: group and event enquiries, guest review responses, and night audit exceptions.

Rules for this file: invented guests, groups and properties only; no review site, travel agency or hotel chain is
named. The assistant never quotes a rate, posts a response or adjusts a folio: the sales manager, the GM and the
night auditor do. Serious guest issues are about billing, security or noise, never illness or injury.
"""
from mk import (D, F, Tbl, Draft, upload, inbox, process, review, X, exceptions, compare, draft, approve, R, write,
                Sec, Chart, report, case)

INDUSTRY = dict(name="Hotels and hospitality", brand="Acme Hotels", order=103,
                blurb="Group sales, guest reviews and the night audit. Your team sets rates, replies and signs off.")

CASES = [
    case("hotel-group-rfp", "Group and event enquiries",
         "Wedding, association and corporate enquiries arrive by email, RFP form and phone. The assistant pulls out the "
         "dates, room block, meeting space and food and drink needs, checks availability and drafts the proposal with "
         "the rates left blank. The sales manager sets the rates and sends it.",
         ("Group and event enquiries by email, RFP form or phone", "Extracts dates, rooms and space, checks availability, drafts the proposal",
          "Sets every rate and concession and sends the proposal", "A proposal ready to send and the enquiry logged"),
         area="Group sales", persona=("Imogen Farrow", "Group sales manager"), unit="Enquiries handled",
         docs=[
             D("Wedding block - Amari and Lindgren.eml", "email", from_="jules.amari@lumenpost.example", to="groups@acme-hotels.example",
               subject="Wedding weekend, June 2027", meta="Email · Mon 23 Nov 10:14", label="Amari and Lindgren wedding", sub="Email · 50 room nights · clean",
               body="Hello,\n\nWe're getting married on [[Saturday 12 June 2027|Event date]] and would love to hold the reception at your hotel.\n\n"
                    "- About [[140 guests|Guests]] for dinner and dancing\n- Ceremony outside if possible, [[about 30 minutes before dinner|Ceremony]]\n"
                    "- A block of [[25 rooms for Friday and Saturday night|Room block]] for family\n\nCould you send us options and pricing?\n\nThanks so much,\nJules Amari",
               fields=[F("Event date", "Sat 12 June 2027", "Email text", 0.98), F("Guests", "140 for dinner and dancing", "Email text", 0.95),
                       F("Ceremony", "Outdoor, before dinner", "Email text", 0.9),
                       F("Room block", "25 rooms · Fri 11 and Sat 12 June · 50 room nights", "Email text"),
                       F("Space", "Harbour Ballroom (seats 180 banquet) + terrace", "Function diary")],
               table=Tbl("Availability", ["Item", "Asked", "Open"],
                         ["Rooms Fri 11 June", "25", "96", "ok"], ["Rooms Sat 12 June", "25", "71", "ok"],
                         ["Harbour Ballroom Sat", "140 banquet", "Open", "ok"], ["Terrace Sat afternoon", "Ceremony", "Open, rain plan: Bayview Room", "ok"]),
               draft=Draft("Dear Jules,\n\nCongratulations, and thank you for thinking of us. Saturday 12 June 2027 is open, and the Harbour Ballroom seats your 140 guests "
                           "with room for a dance floor. The ceremony can be on the terrace, with the Bayview Room held as a rain plan.\n\n"
                           "For your family we can hold 25 rooms on Friday and Saturday night at a group rate of [[rate set by the sales manager]].\n\n"
                           "I'd love to show you the space. Would a visit next week suit you?\n\nImogen Farrow\nGroup sales",
                           label="Proposal email", to="Jules Amari", subject="Your wedding weekend, 11 to 13 June 2027"),
               notes="Everything asked for is open. The rate and any food and drink minimum are for the sales manager to set.", yes="Approve proposal draft"),
             D("RFP - Prairie Apiarists Association.pdf", "pdf", meta="RFP form · 3 pages · Mon 23 Nov", label="Prairie Apiarists Association", sub="RFP · 145 room nights · peak short",
               body="PRAIRIE APIARISTS ASSOCIATION · ANNUAL CONFERENCE 2027 · REQUEST FOR PROPOSAL\n\n"
                    "Dates: arrive [[Wed 21 April|Arrival]], depart [[Sat 24 April 2027|Departure]]\n"
                    "Rooms: Wed [[40]] · Thu [[60|Peak night]] · Fri [[45]]\n"
                    "General session: [[180 theatre style|Main room]] Thu and Fri\nBreakouts: [[2 rooms for 40|Breakouts]]\nExhibits: 12 tables\n"
                    "Meals: breakfast x 3, lunch x 2, banquet Fri\n\n"
                    "Concessions requested: [[1 complimentary room per 20 sold; meeting space at no charge; 10% attrition|Concessions]]\n"
                    "Proposals due: [[Fri 4 Dec 2026|Due]]",
               fields=[F("Arrival", "Wed 21 April 2027", "Page 1"), F("Departure", "Sat 24 April 2027", "Page 1"),
                       F("Peak night", "Thu 22 April · 60 rooms", "Page 1"), F("Main room", "180 theatre, Thu and Fri", "Page 2"),
                       F("Breakouts", "2 rooms for 40", "Page 2"), F("Concessions", "Comp rooms, free meeting space, 10% attrition", "Page 3"),
                       F("Due", "Fri 4 Dec 2026", "Page 1")],
               table=Tbl("Availability", ["Item", "Asked", "Open"],
                         ["Rooms Wed 21 April", "40", "88", "ok"], ["Rooms Thu 22 April", "60", "48", "bad"],
                         ["Rooms Fri 23 April", "45", "74", "ok"], ["Harbour Ballroom Thu and Fri", "180 theatre", "Open", "ok"],
                         ["Two breakout rooms", "40 each", "Open", "ok"], ["Concessions", "3 asked", "Sales manager decides", "check"]),
               flags=[("bad", "Thursday 22 April is 12 rooms short: another group holds a tentative block of 30 that night. Its option date is Mon 30 Nov."),
                      ("info", "Concessions and the food and drink minimum are the sales manager's call. The draft leaves them open.")],
               yes="Approve proposal draft"),
             D("Sales kickoff - Tidewell Analytics.eml", "email", from_="events@tidewell-analytics.example", to="groups@acme-hotels.example",
               subject="Sales kickoff in February", meta="Email · Tue 24 Nov 09:02", label="Tidewell Analytics kickoff", sub="Email · dates unclear",
               body="Hi there,\n\nWe're planning our sales kickoff for [[the second or third week of February|Dates]]. Roughly:\n\n"
                    "- [[40 rooms for 2 nights|Room block]]\n- One meeting room for [[45, classroom style|Meeting room]]\n- Breakfast and lunch both days; dinner we'll do offsite\n\n"
                    "Can you tell us which week works better and send a quote?\n\nNadia Kerrigan\nTidewell Analytics",
               fields=[F("Dates", "?Week of 8 Feb or week of 15 Feb 2027; nights not given", "Email text", 0.4),
                       F("Room block", "40 rooms x 2 nights · 80 room nights", "Email text"),
                       F("Meeting room", "45 classroom", "Email text"), F("Meals", "Breakfast and lunch x 2", "Email text")],
               table=Tbl("Availability", ["Item", "Week of 8 Feb", "Week of 15 Feb"],
                         ["Rooms, Tue and Wed nights", "62 and 70 open", "22 and 25 open", "check"],
                         ["Meeting room for 45", "Lighthouse Room open", "Lighthouse Room open", "ok"]),
               flags=["The week of 15 Feb has a citywide trade show; only 22 rooms are open on Tuesday. The draft offers the week of 8 Feb first and asks which nights."],
               draft=Draft("Hi Nadia,\n\nThanks for thinking of us for your kickoff. The [[week of 8 February]] works best on our side: we can hold 40 rooms on "
                           "Tuesday and Wednesday nights and the Lighthouse Room for 45 classroom style. The following week is busier in the city.\n\n"
                           "Which two nights would you like? I'll send a full proposal as soon as I know.\n\nImogen",
                           label="Reply to client", to="Nadia Kerrigan"),
               yes="Approve proposal draft"),
             D("Call note - Pinewick Minor Hockey.txt", "call", meta="Call · Tue 24 Nov 15:30", label="Pinewick Minor Hockey", sub="Call · rate below floor",
               body="Call from Dale Pruett, team manager, Pinewick Minor Hockey.\nTournament weekend: [[Fri 4 to Sun 6 Dec 2026|Dates]]\n"
                    "Rooms: [[18 rooms, 2 nights|Room block]], mostly two queen beds\nAsked for: [[$99 a night, breakfast included|Rate asked]]\n"
                    "Said another hotel offered $109. Wants an answer by Thursday.",
               fields=[F("Dates", "Fri 4 to Sun 6 Dec 2026", "Call note"), F("Room block", "18 rooms x 2 nights · 36 room nights, two-queen", "Call note"),
                       F("Rate asked", "$99 with breakfast", "Call note"), F("Group floor that weekend", "$149, set by revenue management", "Rate plan")],
               table=Tbl("Checks", ["Check", "Asked", "On file"],
                         ["Two-queen rooms Fri and Sat", "18", "31 and 27 open", "ok"],
                         ["Rate", "$99 with breakfast", "Group floor $149", "bad"]),
               flags=[("bad", "The rate asked is $50 below the group floor for that weekend. The assistant does not answer on rate; the sales manager decides with revenue management."),
                      "The competing $109 offer is what the caller said. It isn't checked."],
               draft=Draft("Hi Dale,\n\nThanks for the call. We have 18 two-queen rooms open for 4 to 6 December. I'm confirming the [[group rate]] with our revenue team "
                           "and will call you back before Thursday.\n\nImogen", label="Holding reply", to="Dale Pruett"),
               yes="Approve proposal draft"),
         ],
         stages=[
             inbox("Group sales inbox and call notes", "Enquiries arrive", "Emails, RFP forms and notes from calls to the sales line.", cta="Check for new enquiries"),
             process([("Reading each enquiry", "Emails, RFP forms, call notes"),
                      ("Pulling out the needs", "Dates, room pattern, meeting space, meals, concessions"),
                      ("Checking availability", "Rooms by night, function diary, competing holds"),
                      ("Drafting proposals and replies", "Rates left blank for the sales manager")],
                     log=[("Prairie Apiarists: Thu 22 April short by 12 rooms (tentative hold G-2291)", "y", 2),
                          ("Tidewell: week of 15 Feb overlaps a citywide trade show", "y", 2),
                          ("Pinewick Minor Hockey: rate asked below the group floor", "y", 2),
                          ("Amari and Lindgren: all rooms and space open", "g", 2)]),
             review("Review each enquiry", "Source on the left, the needs and availability on the right. Rates are never filled in by the assistant.",
                    yes="Approve proposal draft", reasons=["Need more from the client", "Dates don't work", "Revenue manager decides", "I'll write this one myself"]),
             compare(Tbl("Enquiries against availability", ["Enquiry", "Dates", "Room nights", "Peak asked", "Peak open"],
                         ["Amari and Lindgren wedding", "11 to 13 June 2027", "50", "25", "71", "ok"],
                         ["Prairie Apiarists Association", "21 to 24 April 2027", "145", "60", "48", "bad"],
                         ["Tidewell Analytics", "Week of 8 or 15 Feb 2027", "80", "40", "22 to 70", "check"],
                         ["Pinewick Minor Hockey", "4 to 6 Dec 2026", "36", "18", "27", "check"]),
                     "Availability", "Filter by status. Red means the hotel can't hold what was asked as things stand."),
             draft("Dear Members of the Conference Committee,\n\nThank you for inviting us to propose for your 2027 annual conference.\n\n"
                   "Dates: Wednesday 21 to Saturday 24 April 2027.\nRooms: we can hold 40 rooms on Wednesday and 45 on Friday. On Thursday we can hold "
                   "[[48 rooms today, and up to 60 if a current option is released on 30 November]].\n"
                   "Meeting space: the Harbour Ballroom for 180 theatre style on Thursday and Friday, two breakout rooms for 40, and space for 12 exhibit tables.\n"
                   "Meals: breakfast three days, lunch two days and a Friday banquet, menus attached.\n\n"
                   "Group rate: [[set by the sales manager]]\nFood and drink minimum: [[set by the sales manager]]\nConcessions: [[as agreed by the sales manager]]\n\n"
                   "We'll hold this proposal until your decision date.\n\nImogen Farrow\nGroup sales manager",
                   "Proposal draft", "The full proposal for the association. Rates, the minimum and concessions are left for the sales manager.",
                   to="Conference committee, Prairie Apiarists Association", subject="Proposal: 2027 annual conference, 21 to 24 April"),
             write("Sales and catering system (test copy)", [
                 R("Prospect · Amari and Lindgren wedding", [("Dates", "11 to 13 June 2027"), ("Rooms", "25 x 2"), ("Space", "Ballroom, terrace"), ("Hold", "as set by Imogen")], "Saved"),
                 R("Prospect · Prairie Apiarists Association", [("Room nights", "145"), ("Proposal due", "Fri 4 Dec"), ("Note", "Thu 22 April short by 12")], "Saved", "check"),
                 R("Prospect · Tidewell Analytics", [("Dates", "waiting on client"), ("Room nights", "80")], "Saved, waiting", "check"),
                 R("Task · Pinewick Minor Hockey", [("Action", "Rate decision with revenue team"), ("Due", "Thu 26 Nov")], "Task created", "info")],
                 sub="Enquiries are logged with no space held unless the sales manager chose to hold it.", cta="Save to the sales system"),
             report("Group enquiries · week of 23 Nov", [
                 Sec("What came in", p="Four enquiries: two emails, one RFP form and one phone call. 311 room nights asked for in total."),
                 Sec("Room nights asked, by enquiry", chart=Chart("Room nights", ["Prairie Apiarists", "Tidewell", "Amari and Lindgren", "Pinewick Hockey"],
                                                                  [145, 80, 50, 36], tones=["check", "check", "ok", "check"])),
                 Sec("Where each one stands", table=Tbl(None, ["Enquiry", "Room nights", "Status", "Waiting on"],
                                                         ["Amari and Lindgren wedding", "50", "Proposal ready", "Sales manager's rate"],
                                                         ["Prairie Apiarists Association", "145", "Proposal drafted", "Option date 30 Nov; rate and concessions"],
                                                         ["Tidewell Analytics", "80", "Replied", "Client's choice of nights"],
                                                         ["Pinewick Minor Hockey", "36", "Holding reply", "Rate decision by Thursday"])),
                 Sec("Follow-ups", list=["Check the G-2291 option on Mon 30 Nov before the association proposal goes out.",
                                         "Call Dale Pruett back before Thursday with the rate the revenue team agrees."])],
                 title="Weekly enquiries", subtitle="Group sales · invented data",
                 kpis=[(4, "Enquiries"), (311, "Room nights asked"), (1, "Ready to send", "ok"), (1, "Short on a peak night", "bad")], format="Weekly summary"),
         ],
         next=["Enquiries are picked up from the group sales inbox, the RFP forms and the call log as they arrive.",
               "Availability comes from your room inventory and function diary, read only.",
               "The sales manager sets every rate, minimum and concession, and sends every proposal.",
               "Holds are placed in your sales system only when the sales manager says so."],
         tags=["group sales", "rfp", "wedding", "room block", "meeting space", "proposal"]),

    case("hotel-guest-reviews", "Guest review responses and themes",
         "Online reviews and post-stay survey comments come in every day. The assistant sorts them by theme, drafts a "
         "response for each one and sends anything serious, like a security or billing problem, to the GM first. "
         "The GM approves every response before it is posted.",
         ("Online reviews and post-stay survey comments", "Sorts by theme, drafts responses, flags serious issues",
          "Approves every response and decides on serious issues", "Responses ready to post and a weekly theme report"),
         area="Guest experience", persona=("Tomasz Brennan", "General manager"), unit="Reviews handled",
         docs=[
             D("Review site A - 5 stars - breakfast.html", "web", meta="Review · 5 of 5 · Mon 23 Nov", label="5 stars · breakfast and front desk", sub="Review · positive",
               body="★★★★★  \"Felt looked after\"\nStayed two nights for a conference. [[Breakfast was excellent|Theme 1]], especially the fresh fruit and the eggs to order. "
                    "[[Mariela at the front desk|Staff named]] sorted out an early check-in for us without any fuss. Would stay again.\n\nPosted by: Conference traveller, Ottawa",
               fields=[F("Rating", "5 of 5", "Review header"), F("Theme 1", "Breakfast", "Review text"), F("Theme 2", "Front desk service", "Review text"),
                       F("Staff named", "Mariela, front desk", "Review text, staff list")],
               table=Tbl("Checks", ["Check", "Result"], ["Serious issue", "None", "ok"], ["Staff mention", "Passed to HR for recognition", "ok"]),
               draft=Draft("Thank you for staying with us and for such kind words. We're glad breakfast hit the spot, and I've passed your thanks on to "
                           "[[Mariela]] and the front desk team. We hope to welcome you back.\n\nTomasz Brennan, General manager",
                           label="Public response"),
               notes="Positive review. The draft follows your response guide: thank, name what they liked, invite back.", yes="Approve response"),
             D("Review site B - 2 stars - noise.html", "web", meta="Review · 2 of 5 · Sun 22 Nov", label="2 stars · noise from a party", sub="Review · noise",
               body="★★☆☆☆  \"No sleep on Saturday\"\nA [[wedding party on our floor was loud until 1:30 am|Theme 1]]. "
                    "I [[called the front desk twice|What they did]] and nothing changed. Room was clean and comfortable otherwise. "
                    "Stayed [[Saturday 21 November|Stay date]].",
               fields=[F("Rating", "2 of 5", "Review header"), F("Theme 1", "Noise", "Review text"), F("Stay date", "Sat 21 Nov", "Review text", 0.95),
                       F("What they did", "Called the front desk twice", "Review text"),
                       F("Front desk log", "Two noise calls logged at 00:40 and 01:10, 4th floor; security visited at 01:20", "Duty log, Sat night", 0.9)],
               table=Tbl("Checks", ["Check", "Result"], ["Serious issue", "No", "ok"],
                         ["Matches the duty log", "Yes, two calls logged", "ok"], ["Response time to the calls", "40 minutes to a security visit", "check"]),
               flags=["The duty log shows the calls but a 40-minute gap before security went up. The GM may want to look at that before replying."],
               draft=Draft("Thank you for telling us, and I'm sorry your Saturday night was so disrupted. You shouldn't have had to call twice. "
                           "We're [[reviewing how we handle noise calls overnight]] with our team. We'd welcome the chance to give you a quieter stay next time.\n\n"
                           "Tomasz Brennan, General manager", label="Public response"),
               yes="Approve response"),
             D("Post-stay survey - parking charge.txt", "note", meta="Survey · score 3 of 10 · Mon 23 Nov", label="Survey · charged twice for parking", sub="Survey · billing",
               body="POST-STAY SURVEY · comment box\nLikely to recommend: 3 of 10\n\n\"[[We were charged for parking twice|Theme 1]], [[$28 two times for one night|Amount]]. "
                    "The front desk said it would be fixed at checkout but it's still on my card statement.\"\n\nGuest: [[R. Haldane|Guest]] · stay Tue 17 Nov",
               fields=[F("Theme 1", "Billing: duplicate parking charge", "Survey comment"), F("Amount", "$28.00 charged twice", "Survey comment"),
                       F("Guest", "R. Haldane", "Survey record"),
                       F("Folio", "?F-883102 or F-883117: two stays under this name that week", "Property management system", 0.4)],
               table=Tbl("Checks", ["Check", "Result"],
                         ["Serious issue", "Yes: billing", "bad"], ["Folio found", "Two possible folios", "check"]),
               flags=[("bad", "A possible double charge goes to the front office manager before any reply. The response must not promise a refund until the folio is checked."),
                      ("info", "Survey comments are answered privately by email, not posted.")],
               draft=Draft("Dear R. Haldane,\n\nThank you for your survey and I'm sorry about the parking charge. Our front office manager is checking your folio today "
                           "and will [[email you directly with what she finds]].\n\nTomasz Brennan, General manager",
                           label="Private reply", to="R. Haldane"),
               yes="Approve response"),
             D("Review site A - 1 star - door.html", "web", meta="Review · 1 of 5 · Tue 24 Nov", label="1 star · door didn't latch", sub="Review · security",
               body="★☆☆☆☆  \"Didn't feel safe\"\nThe [[door to our room didn't close properly|Theme 1]]. You had to pull it hard or the latch didn't catch. "
                    "We were on the [[second floor, near the ice machine|Room]]. Reported it at checkout. Not good enough.",
               fields=[F("Rating", "1 of 5", "Review header"), F("Theme 1", "Security: door latch", "Review text"),
                       F("Room", "?214 or 216 (both next to the ice machine)", "Review text, floor plan", 0.4),
                       F("Checkout report", "?Not found in the front desk log", "Front desk log, last 14 days", 0.3)],
               table=Tbl("Checks", ["Check", "Result"],
                         ["Serious issue", "Yes: room security", "bad"], ["Open work order on 214 or 216", "None", "check"]),
               flags=[("bad", "A door that doesn't latch is sent to the GM and engineering now. The response waits until engineering has checked both rooms."),
                      "The guest says they reported it at checkout, but there's no entry in the log. The draft doesn't argue the point."],
               draft=Draft("Thank you for raising this, and I'm sorry. A door that doesn't close properly is not acceptable. Our engineering team has "
                           "[[checked the doors on that part of the second floor]], and I'd like to hear more: please contact me directly at the hotel.\n\n"
                           "Tomasz Brennan, General manager", label="Public response, after engineering checks"),
               yes="Approve response"),
             D("Review site C - 3 stars - pool.html", "web", meta="Review · 3 of 5 · Tue 24 Nov", label="3 stars · pool closed, slow check-in", sub="Review · mixed",
               body="★★★☆☆  \"Fine, but\"\nRoom was nice and the bed was comfortable. The [[pool was closed with no notice|Theme 1]] and the "
                    "[[check-in line took 25 minutes|Theme 2]] on Friday evening. Staff were friendly when we got to the desk.",
               fields=[F("Rating", "3 of 5", "Review header"), F("Theme 1", "Amenities: pool closed", "Review text"),
                       F("Theme 2", "Check-in wait", "Review text"),
                       F("Pool status", "Closed Fri 20 Nov for planned maintenance; notice on the booking page from Wed 18 Nov", "Maintenance calendar", 0.85)],
               table=Tbl("Checks", ["Check", "Result"], ["Serious issue", "No", "ok"],
                         ["Guests told about the pool", "Booking page only, no pre-arrival email", "check"]),
               draft=Draft("Thank you for your review. I'm sorry the pool was closed during your stay: it was planned maintenance, and we should have told you before you arrived. "
                           "We're also looking at [[staffing at the desk on Friday evenings]]. Glad you enjoyed the room, and we hope to see you again.\n\n"
                           "Tomasz Brennan, General manager", label="Public response"),
               yes="Approve response"),
         ],
         stages=[
             inbox("Review sites and post-stay survey", "Reviews arrive", "New reviews from three review sites and the comment box of your post-stay survey.", cta="Check for new reviews"),
             process([("Reading each review and comment", "Rating, text, stay date"),
                      ("Sorting by theme", "Your theme list: service, food, noise, billing, security, amenities, check-in"),
                      ("Checking the logs", "Duty log, front desk log, maintenance calendar, folios"),
                      ("Flagging serious issues to the GM", "Security and billing first"),
                      ("Drafting responses", "From your response guide. Nothing is posted")],
                     log=[("Door latch review: room 214 or 216, no work order open", "y", 3),
                          ("Parking charge: two possible folios for R. Haldane", "y", 2),
                          ("Noise review matches two calls in the duty log", "g", 2)]),
             review("Approve each response", "The review on the left, the theme, checks and draft on the right. Edit the draft as you like.",
                    yes="Approve response", reasons=["Wait for engineering or front office", "Tone isn't right", "Don't respond to this one", "I'll write this one myself"]),
             exceptions([
                 X("Door latch, second floor", "1-star review says the room door didn't latch. Room 214 or 216; no work order on either.",
                   ["Engineering checks both doors today", "Take both rooms out of order until checked", "Check 214 and 216 at next turnover"], rec=0, tone="bad",
                   why="It's a security issue. The response is held until engineering reports back."),
                 X("Parking charged twice", "Survey comment: $28.00 charged twice. Two folios could match.",
                   ["Front office manager checks both folios", "Refund $28.00 now", "Ask the guest for the card statement"], rec=0, tone="bad",
                   why="Folio adjustments are made by the front office manager after checking the charges."),
                 X("Noise calls answered slowly", "Two noise calls Saturday night, 40 minutes before security went up.",
                   ["Review with the night manager", "No action beyond the response"], rec=0,
                   why="The duty log supports the guest's account."),
             ], "Serious issues", "Sent to the GM before any response goes out. The GM chooses what happens."),
             write("Property management system (test copy)", [
                 R("Work order WO-4418 · rooms 214 and 216", [("Issue", "Door latch, from a guest review"), ("Assigned", "Engineering"), ("Priority", "as set by the GM")], "Work order created", "check"),
                 R("Folio query · R. Haldane", [("Folios", "F-883102, F-883117"), ("Owner", "Front office manager")], "Task created", "info"),
                 R("Responses · 3 reviews", [("Status", "Approved by the GM"), ("Posting", "by the GM's team")], "Ready to post"),
                 R("Responses · door review and survey reply", [("Status", "Held until checks are done")], "Held", "bad")],
                 sub="Work orders and tasks are created as the GM decided. Responses are posted by your team.", cta="Save to the system"),
             report("Guest feedback themes · week of 23 Nov", [
                 Sec("What came in", p="Five pieces of feedback: four online reviews and one survey comment. Ratings: one 5, one 3, one 2 and one 1 out of 5; the survey score was 3 of 10."),
                 Sec("Mentions by theme", chart=Chart("Mentions", ["Front desk and staff", "Breakfast", "Noise", "Billing", "Room security", "Pool", "Check-in wait"],
                                                     [2, 1, 1, 1, 1, 1, 1], tones=["ok", "ok", "check", "bad", "bad", "check", "check"])),
                 Sec("Serious issues", table=Tbl(None, ["Issue", "Source", "Owner", "Status"],
                                                 ["Door didn't latch, room 214 or 216", "1-star review", "Engineering", "Work order open"],
                                                 ["Parking charged twice", "Survey comment", "Front office manager", "Folio check"])),
                 Sec("For the GM", list=["Noise calls: 40 minutes from the second call to a security visit on Saturday.",
                                         "Pool closures: guests are told on the booking page but not by pre-arrival email."])],
                 title="Theme report", subtitle="Guest experience · invented data",
                 kpis=[(5, "Reviews and comments"), (3, "Responses ready", "ok"), (2, "Serious issues", "bad")],
                 sources=["Review sites A, B and C, 22 to 24 Nov", "Post-stay survey, Mon 23 Nov", "Duty log, Sat 21 Nov", "Maintenance calendar"],
                 format="Weekly theme report"),
         ],
         next=["Reviews are collected from the sites you use and your survey tool every morning.",
               "Responses follow your own response guide and tone.",
               "The GM approves every response; your team posts it.",
               "Security and billing issues go to the GM and the right department before any reply."],
         tags=["guest reviews", "reputation", "survey", "responses", "hotel"]),

    case("hotel-night-audit", "Night audit exceptions",
         "At the end of the day the property system exports the in-house list, no-shows and cashier totals. The "
         "assistant checks rate codes, comps, no-show charges and cashier variances against your policies and lists "
         "the exceptions. The night auditor resolves each one and the controller signs off.",
         ("Folio, rate, no-show and cashier exports", "Checks rates, comps, no-shows and tills against your policies",
          "The night auditor resolves exceptions; the controller signs off", "An exception list and the audit summary"),
         area="Accounting", persona=("Anika Sorensen", "Night auditor"), unit="Items checked",
         docs=[
             D("In-house rate check - Tue 24 Nov.csv", "sheet", meta="PMS export · 03:05 · 5 of 148 rooms flagged or sampled", label="Rate check · in-house rooms", sub="Rates · 2 issues",
               body="In-house guests, night of Tue 24 Nov 2026 · rooms with special rate codes",
               rows=[["Room", "Guest", "Rate code", "Rate", "Expected"],
                     ["304", "Halberd, J.", "BAR", "$189.00", "$189.00"],
                     ["312", "Pellegrino, S.", "[[CORP-NWX|Room 312 code]]", "$152.00", "$152.00"],
                     ["508", "Thornbury, K.", "COMP", "$0.00", "Comp code CA-1127"],
                     ["611", "Delacourt, M.", "[[COMP|Room 611 code]]", "$0.00", "[[No comp code|Room 611 approval]]"],
                     ["702", "Rasmussen, A.", "[[GRP-OAKR|Room 702 code]]", "$139.00", "[[$149.00 group contract|Room 702 rate]]"]],
               fields=[F("Room 312 code", "CORP-NWX · company profile not linked", "Rate code table", 0.7),
                       F("Room 611 code", "COMP", "Folio"), F("Room 611 approval", "None found in the comp log", "Comp and allowance log"),
                       F("Room 702 code", "GRP-OAKR · Oakreach Curling Club block", "Group block"),
                       F("Room 702 rate", "$139.00 posted; contract says $149.00", "Group contract G-2280")],
               table=Tbl("Rate checks", ["Room", "Check", "Result"],
                         ["304", "BAR rate matches", "Yes", "ok"], ["312", "Corporate rate needs a linked company", "Not linked", "check"],
                         ["508", "Comp has an approval code", "CA-1127", "ok"], ["611", "Comp has an approval code", "None", "bad"],
                         ["702", "Group rate matches the contract", "$10.00 under", "bad"]),
               flags=[("bad", "Room 611 is on a $0.00 comp with no approval in the comp log. Your policy needs a manager's code for every comp."),
                      ("bad", "Room 702 posted $139.00; the group contract rate is $149.00. Possibly keyed from last year's contract.")],
               yes="Clear item"),
             D("No-show list - Tue 24 Nov.csv", "sheet", meta="PMS export · 03:10 · 3 reservations", label="No-shows · 3 reservations", sub="No-shows · 1 unclear",
               rows=[["Reservation", "Guest", "Held by", "Rate", "Cancellation"],
                     ["R-77120", "Ingram, P.", "Card on file", "$189.00", "None"],
                     ["[[R-77134|Agency booking]]", "Sokolov, D.", "Travel agency deposit", "$172.00", "None"],
                     ["[[R-77141|Late cancel]]", "Bellweather, C.", "Card on file", "$189.00", "[[Phone, \"around 6 pm\"|Cancel time]]"]],
               fields=[F("R-77120", "Card on file, no cancellation: one night's charge under your policy", "Row 1, policy"),
                       F("Agency booking", "R-77134 · deposit held by the agency", "Row 2"),
                       F("Late cancel", "R-77141 · Bellweather, C.", "Row 3"),
                       F("Cancel time", "?\"Around 6 pm\"; cut-off is 18:00 on the day of arrival", "Reservation note, no time stamp", 0.35)],
               table=Tbl("No-show checks", ["Reservation", "Your policy", "Proposed"],
                         ["R-77120", "Charge one night", "$189.00 plus taxes", "ok"],
                         ["R-77134", "Agency bookings: front office manager decides", "Hold", "check"],
                         ["R-77141", "Charge if cancelled after 18:00", "Can't tell", "check"]),
               flags=["The Bellweather cancellation has no time stamp, only \"around 6 pm\" in the note. The assistant doesn't decide which side of the cut-off it falls."],
               yes="Clear item"),
             D("Cashier report - Tue 24 Nov.pdf", "pdf", meta="PDF · 1 page · 4 tills", label="Cashier report · 4 tills", sub="Tills · 1 over tolerance",
               body="CASHIER BALANCING · TUESDAY 24 NOVEMBER 2026\n\n"
                    "Front desk till 1 · AM shift   expected $612.00   counted $612.00   variance $0.00\n"
                    "Front desk till 2 · PM shift   expected $1,048.50  counted [[$1,006.00|Till 2 counted]]  variance [[-$42.50|Till 2 variance]]\n"
                    "Restaurant till R1 · lunch    expected $884.25   counted $889.25   variance +$5.00\n"
                    "Restaurant till R2 · dinner   expected $1,312.80  counted $1,312.80  variance $0.00\n\n"
                    "Tolerance per till: [[$10.00|Tolerance]]",
               fields=[F("Till 2 counted", "$1,006.00 against $1,048.50 expected", "Line 2"), F("Till 2 variance", "-$42.50", "Line 2"),
                       F("Tolerance", "$10.00 per till", "Footer, cash policy")],
               table=Tbl("Till checks", ["Till", "Variance", "Tolerance"],
                         ["Front desk 1 · AM", "$0.00", "$10.00", "ok"], ["Front desk 2 · PM", "-$42.50", "$10.00", "bad"],
                         ["Restaurant R1 · lunch", "+$5.00", "$10.00", "ok"], ["Restaurant R2 · dinner", "$0.00", "$10.00", "ok"]),
               flags=[("bad", "Till 2 on the PM shift is $42.50 short, over the $10.00 tolerance. It goes to the controller with the shift's paid-outs list."),
                      ("info", "Variances are reported by till and shift. Any follow-up with staff is the controller's.")],
               yes="Clear item"),
             D("Comp and allowance log - Tue 24 Nov.txt", "note", meta="Log · 2 entries", label="Comp and allowance log", sub="Log · clean",
               body="COMP AND ALLOWANCE LOG\n\n1. Room [[508|Comp room]] · complimentary night · reason: service recovery, prior stay · approved by GM · code [[CA-1127|Comp code]]\n"
                    "2. Room [[304|Allowance room]] · [[$45.00 room service credit|Allowance]] · reason: late room service order · approved by duty manager · code AL-3390",
               fields=[F("Comp room", "508", "Entry 1"), F("Comp code", "CA-1127, GM", "Entry 1"),
                       F("Allowance room", "304", "Entry 2"), F("Allowance", "$45.00 room service credit, code AL-3390", "Entry 2")],
               table=Tbl("Log checks", ["Entry", "Check", "Result"],
                         ["508 comp", "Approval code and approver", "Present", "ok"], ["304 allowance", "Approval code and posted to folio", "Present, posted", "ok"]),
               notes="Both entries have an approver and a code and match the folios. Nothing to resolve.", yes="Clear item"),
         ],
         stages=[
             upload("End-of-day exports", "The property system's in-house, no-show and cashier exports, plus the comp log. Use the samples, or drop a file to see what happens.",
                    cta="Load tonight's exports"),
             process([("Reading the exports", "Rate check, no-shows, cashier report, comp log"),
                      ("Checking rate codes", "Rate plans, corporate profiles, group contracts"),
                      ("Checking comps and allowances", "Every one needs an approval code"),
                      ("Checking no-shows", "Hold type and cancellation time against your policy"),
                      ("Balancing tills", "Each till against its tolerance")],
                     log=[("Room 611: comp with no approval code", "y", 2), ("Room 702: $139.00 against $149.00 contract", "y", 1),
                          ("Till 2 PM: -$42.50, tolerance $10.00", "y", 4), ("Comp log: 2 entries, both approved", "g", 2)]),
             review("Work through each file", "Each export with its checks. Clear it, or send it back with a reason.",
                    yes="Clear item", reasons=["Front office manager decides", "Controller decides", "Export looks wrong: rerun", "I'll fix this in the PMS myself"]),
             exceptions([
                 X("Room 611: comp with no approval", "$0.00 rate on COMP with nothing in the comp log.",
                   ["Leave for the GM to approve in the morning", "Post the BAR rate of $189.00", "Ask the front desk who set it"], rec=0, tone="bad",
                   why="Only a manager can approve a comp. The auditor doesn't change it overnight."),
                 X("Room 702: group rate $10.00 under contract", "GRP-OAKR posted at $139.00; contract G-2280 says $149.00.",
                   ["Correct to $149.00 tonight", "Leave and flag to group sales"], rec=0, tone="bad",
                   why="The contract is on file and signed. Correcting before the guest's folio prints avoids a dispute later."),
                 X("R-77141: cancelled \"around 6 pm\"", "No time stamp. The cut-off is 18:00.",
                   ["Don't charge", "Charge one night, $189.00 plus taxes", "Leave for the front office manager"], rec=2,
                   why="The note can't settle which side of 18:00 the call was."),
                 X("R-77134: agency booking no-show", "Deposit is held by the travel agency.",
                   ["Leave for the front office manager", "Bill the agency one night"], rec=0,
                   why="Your policy sends agency no-shows to the front office manager."),
                 X("Till 2 PM: $42.50 short", "Over the $10.00 tolerance.",
                   ["Report to the controller with the paid-outs list", "Recount the till first"], rec=1, tone="bad",
                   why="A recount rules out a counting slip before it goes to the controller."),
             ], "Exceptions", "The night auditor resolves each one. The assistant suggests; the auditor chooses."),
             approve("Close the day and send the audit pack to the controller?", "Close the day",
                     summary=[("Business date", "Tue 24 Nov 2026"), ("Items checked", "4 files, 14 lines"), ("Exceptions", "5"), ("Left for managers", "as chosen by Anika")],
                     checks=["Every exception has a decision or an owner", "No comp was approved by the night auditor", "Till variances are by till and shift only"],
                     yes="Close day"),
             report("Night audit summary · Tue 24 Nov 2026", [
                 Sec("The day", kpis=[[148, "Rooms occupied of 212"], ["69.8%", "Occupancy"], ["$24,013", "Room revenue"], [2, "Complimentary rooms"]]),
                 Sec("Exceptions by type", chart=Chart("Exceptions", ["Rate code", "Comp", "No-show", "Till"], [1, 1, 2, 1], tones=["bad", "bad", "check", "bad"])),
                 Sec("Exceptions and decisions", table=Tbl(None, ["Item", "Issue", "Decision", "Owner"],
                                                           ["Room 611", "Comp with no approval", "as decided by the auditor", "GM"],
                                                           ["Room 702", "$10.00 under group contract", "as decided by the auditor", "Night auditor"],
                                                           ["R-77141", "Cancel time unclear", "as decided by the auditor", "Front office manager"],
                                                           ["R-77134", "Agency no-show", "as decided by the auditor", "Front office manager"],
                                                           ["Till 2 PM", "-$42.50", "as decided by the auditor", "Controller"])),
                 Sec("For the controller", list=["Sign off the day once the room 611 comp is approved or reversed.",
                                                 "Room 312's corporate rate needs its company profile linked by sales."])],
                 title="Audit summary", subtitle="Night audit · invented data",
                 kpis=[(14, "Lines checked"), (8, "Passed", "ok"), (1, "Follow-up", "check"), (5, "Exceptions", "bad")],
                 sources=["PMS in-house export 03:05", "PMS no-show export 03:10", "Cashier report, 4 tills", "Comp and allowance log"],
                 format="Night audit summary"),
         ],
         next=["Exports are pulled from your property system at the end of each business day.",
               "Rate plans, contracts, comp rules and till tolerances come from your own policies.",
               "The night auditor resolves every exception; comps and refunds stay with managers.",
               "The controller signs off each day before it is final."],
         tags=["night audit", "folio", "no-show", "cashier", "comps", "hotel accounting"]),
]
