"""Education and training providers: admissions, student services and curriculum.

Rules for this file: no student health, disability or accommodation information anywhere; admission, grade, credit
and curriculum decisions stay with the admissions officer, faculty, registrar or program chair. Rules quoted are
the college's own policies, never the law.
"""
from mk import (D, F, Tbl, Draft, upload, inbox, process, review, X, exceptions, compare, approve, R, write,
                Sec, Chart, report, QA, ask, case)

INDUSTRY = dict(name="Education and training providers", brand="Acme College", order=108,
                blurb="Colleges, career schools and training providers. Staff and faculty make every decision.")

CASES = [
    # 1 ------------------------------------------------------------------------------------------
    case("edu-admissions-docs", "Admissions document check",
         "Application forms, transcripts and language test reports arrive for the January intake. The assistant checks "
         "each file against the program's requirements, flags anything missing, unreadable or expiring and drafts the "
         "follow-up. The admissions officer decides.",
         ("Applications, transcripts and test reports", "Checks each file against program requirements, drafts follow-ups",
          "Decides every admission and sends every follow-up", "A completeness list per applicant"),
         area="Admissions", persona=("Nadia Fontaine", "Admissions officer"), unit="Applications checked",
         docs=[
             D("Application 26-3104 - Jonah Whitlock.pdf", "pdf", meta="Portal PDF · 4 pages · Mon 08:10",
               label="Jonah Whitlock · 26-3104", sub="Application + transcript · complete",
               body="ACME COLLEGE · APPLICATION FOR ADMISSION\nApplication no. [[26-3104|Application]]\nApplicant: [[Jonah Whitlock|Applicant]]\n"
                    "Program: [[Electrical Engineering Technician (diploma)|Program]]\nIntake: [[January 2027|Intake]]\n\n"
                    "Attached: secondary school transcript, Lakeview Secondary\n  Diploma granted: June 2026\n"
                    "  Grade 12 English ........ [[78|Grade 12 English]]\n  Grade 12 Math ........... [[81|Grade 12 Math]]\n\n"
                    "Application fee: [[paid 14 Nov 2026|Fee]]",
               fields=[F("Application", "26-3104", "Portal header"), F("Applicant", "Jonah Whitlock", "Page 1"),
                       F("Program", "Electrical Engineering Technician · diploma", "Page 1"), F("Intake", "January 2027 (classes start 11 Jan)", "Page 1"),
                       F("Grade 12 English", "78 (needs 60)", "Transcript, page 3", 0.98), F("Grade 12 Math", "81 (needs 60)", "Transcript, page 3", 0.98),
                       F("Fee", "Paid 14 Nov 2026", "Payment record")],
               table=Tbl("Program requirements", ["Requirement", "On file", "Result"],
                         ["Secondary school diploma", "Granted June 2026", "Met", "ok"],
                         ["Grade 12 English, 60 or higher", "78", "Met", "ok"],
                         ["Grade 12 Math, 60 or higher", "81", "Met", "ok"],
                         ["Application fee", "Paid", "Met", "ok"]),
               notes="Every requirement is on file and met. The file is ready for the admissions officer's decision.",
               yes="Mark complete"),
             D("Transcript - Elise Marchetti.pdf", "scan", meta="Scan · 2 pages · Mon 09:02",
               label="Elise Marchetti · 26-3117", sub="Transcript scan · mark unreadable",
               body="NORTHFIELD DISTRICT SECONDARY SCHOOL\nStudent: [[Elise Marchetti|Applicant]]\nDiploma granted: [[June 2025|Diploma]]\n\n"
                    "Grade 12 English ........ [[71|Grade 12 English]]\nGrade 12 Math ........... [[▒8|Grade 12 Math]]  (first digit smudged)\n"
                    "Grade 12 Accounting ..... 74\n\nCopy uploaded by applicant. Not an official copy.",
               fields=[F("Applicant", "Elise Marchetti · application 26-3117", "Name + portal upload", 0.97),
                       F("Program", "Business Administration · January 2027", "Application record"),
                       F("Diploma", "Granted June 2025", "Page 1", 0.96), F("Grade 12 English", "71 (needs 60)", "Page 1", 0.95),
                       F("Grade 12 Math", "?_8: first digit unreadable (58 or 68 would change the result)", "Page 1, smudged", 0.3)],
               table=Tbl("Program requirements", ["Requirement", "On file", "Result"],
                         ["Secondary school diploma", "Granted June 2025", "Met", "ok"],
                         ["Grade 12 English, 60 or higher", "71", "Met", "ok"],
                         ["Grade 12 Math, 60 or higher", "Unreadable", "Can't tell", "check"],
                         ["Application fee", "Paid 9 Nov 2026", "Met", "ok"]),
               flags=["The math mark is left blank, not guessed. Anything from 08 to 98 fits the scan.",
                      "An official transcript sent by the school would settle it."],
               draft=Draft("Hi Elise,\n\nThanks for applying to Business Administration for January. The copy of your transcript we received is "
                           "hard to read where it shows your [[Grade 12 Math]] mark. Could you ask your school to send us an official transcript, "
                           "or upload a clearer copy to the applicant portal?\n\nAdmissions, Acme College",
                           label="Follow-up to applicant", to="Elise Marchetti", subject="One item to finish your application",
                           alt=["Hi Elise,\n\nWe're nearly done with your application. The [[Grade 12 Math]] mark on your transcript copy is smudged. "
                                "A clearer copy in the portal, or an official transcript from your school, is all we need.\n\nAdmissions, Acme College"]),
               yes="Send follow-up"),
             D("Language test report - Rowan Kessler.pdf", "pdf", meta="Test report PDF · Mon 09:40",
               label="Rowan Kessler · 26-3122", sub="Test report · expires before start",
               body="ENGLISH LANGUAGE TEST · SCORE REPORT\nCandidate: [[Rowan Kessler|Applicant]]\nTest date: [[3 Dec 2024|Test date]]\n\n"
                    "Overall ........ [[64|Overall score]]\nReading ........ 66\nWriting ........ [[58|Writing score]]\nListening ...... 65\nSpeaking ....... 63\n\n"
                    "Test on the college's approved list.",
               fields=[F("Applicant", "Rowan Kessler · application 26-3122", "Name + portal upload", 0.98),
                       F("Program", "Computer Programming · January 2027", "Application record"),
                       F("Test date", "3 Dec 2024", "Report header", 0.99), F("Overall score", "64 (needs 60)", "Report", 0.99),
                       F("Writing score", "58 (needs 55)", "Report", 0.99),
                       F("Valid until", "3 Dec 2026: two years, your admissions policy", "Calculated from test date")],
               table=Tbl("Program requirements", ["Requirement", "On file", "Result"],
                         ["Secondary school diploma", "Transcript received 2 Nov", "Met", "ok"],
                         ["Grade 12 English, 60 or higher", "66", "Met", "ok"],
                         ["Grade 12 Math, 60 or higher", "70", "Met", "ok"],
                         ["Language test score", "Overall 64, writing 58", "Met", "ok"],
                         ["Test valid on the start date", "Ends 3 Dec 2026; classes start 11 Jan 2027", "Expires first", "bad"]),
               flags=[("bad", "The scores meet the requirement, but your policy needs the test to be valid on the first day of classes. It ends five weeks before."),
                      ("info", "Whether an exception applies is the admissions officer's call. The assistant only shows the dates.")],
               draft=Draft("Hi Rowan,\n\nThanks for your application to Computer Programming. Your language test scores meet the program requirement, "
                           "but the result is valid until [[3 December 2026]], before classes start on 11 January. "
                           "We'll be in touch about your options shortly.\n\nAdmissions, Acme College",
                           label="Follow-up to applicant", to="Rowan Kessler", subject="Your language test date"),
               yes="Send follow-up"),
             D("Re: my application - Hannah Lindgren.eml", "email", from_="hannah.lindgren@mailbox.example", to="admissions@acme-college.example",
               subject="Re: missing documents, application 26-3129", meta="Email · 2 attachments · Mon 10:15",
               label="Hannah Lindgren · 26-3129", sub="Email · transfer credit pending",
               body="Hello,\n\nAttached is my Grade 12 transcript for application [[26-3129|Application]] ([[Accounting diploma|Program]], January).\n\n"
                    "I'd also like [[transfer credit for two courses|Transfer credit]] I took at Northbay Community College. "
                    "I've asked them to send my transcript but it hasn't gone out yet.\n\nThanks,\nHannah Lindgren\n\n"
                    "Attachment: transcript.pdf  (Grade 12 English [[69|Grade 12 English]], Grade 12 Math [[64|Grade 12 Math]])",
               fields=[F("Application", "26-3129", "Subject and body"), F("Program", "Accounting · diploma · January 2027", "Application record"),
                       F("Grade 12 English", "69 (needs 60)", "Attached transcript", 0.96), F("Grade 12 Math", "64 (needs 60)", "Attached transcript", 0.96),
                       F("Transfer credit", "?Two courses, not named; college transcript not received", "Email text", 0.4)],
               table=Tbl("Program requirements", ["Requirement", "On file", "Result"],
                         ["Secondary school diploma", "Granted June 2026", "Met", "ok"],
                         ["Grade 12 English, 60 or higher", "69", "Met", "ok"],
                         ["Grade 12 Math, 60 or higher", "64", "Met", "ok"],
                         ["College transcript (transfer credit only)", "Not received", "Waiting", "check"]),
               flags=["Admission requirements are all met. Transfer credit waits on the college transcript.",
                      ("info", "The registrar's office decides transfer credit, not admissions or the assistant.")],
               draft=Draft("Hi Hannah,\n\nThanks, we have your Grade 12 transcript and your application is now complete for admission review. "
                           "Transfer credit is assessed separately by the registrar's office once [[Northbay Community College sends your transcript]] "
                           "and you tell us which two courses you'd like considered.\n\nAdmissions, Acme College",
                           label="Reply to applicant", to="Hannah Lindgren", subject="Re: missing documents, application 26-3129"),
               yes="Send reply"),
         ],
         stages=[
             upload("Applications arrive", "From the applicant portal and the admissions inbox. Use the samples, or drop a file to see what happens."),
             process([("Reading forms, transcripts and test reports", "Portal PDFs, scans and email attachments"),
                      ("Matching each document to its application", "Application number, then name"),
                      ("Checking program requirements", "Diploma, required courses and marks, language test"),
                      ("Checking dates", "Document validity against the 11 January start"),
                      ("Drafting follow-ups", "Nothing is sent")],
                     log=[("26-3104: all four requirements met", "g", 2), ("26-3117: math mark unreadable on the scan", "y", 2),
                          ("26-3122: test valid to 3 Dec 2026, start is 11 Jan 2027", "y", 3)]),
             review("Review each file", "The document on the left, the requirement check and any follow-up on the right.",
                    yes="Mark complete", reasons=["Ask the applicant", "Wrong application matched", "Needs the registrar", "I'll check this one myself"]),
             compare(Tbl("Completeness list · January 2027 intake", ["Application", "Applicant", "Program", "Missing or expiring", "Follow-up"],
                         ["26-3104", "Jonah Whitlock", "Electrical Engineering Technician", "—", "—", "ok"],
                         ["26-3117", "Elise Marchetti", "Business Administration", "Grade 12 Math mark unreadable", "Drafted", "check"],
                         ["26-3122", "Rowan Kessler", "Computer Programming", "Language test ends before start", "Drafted", "bad"],
                         ["26-3129", "Hannah Lindgren", "Accounting", "College transcript (transfer credit only)", "Drafted", "check"]),
                     "Completeness list", "One row per application. Filter by status."),
             write("Student information system (test copy)", [
                 R("Application 26-3104 · Jonah Whitlock", [("Checklist", "Complete"), ("Next", "Admission decision"), ("Owner", "Nadia Fontaine")], "Ready for decision"),
                 R("Application 26-3117 · Elise Marchetti", [("Waiting on", "Official transcript"), ("Follow-up", "Sent by Nadia")], "Waiting on applicant", "check"),
                 R("Application 26-3122 · Rowan Kessler", [("Issue", "Test valid to 3 Dec 2026"), ("Owner", "Admissions officer")], "On hold", "bad"),
                 R("Application 26-3129 · Hannah Lindgren", [("Checklist", "Complete for admission"), ("Transfer credit", "Passed to the registrar")], "Ready for decision", "info")],
                 sub="Checklist statuses only. Admission decisions are entered by the admissions officer.", cta="Save checklists"),
             report("Admissions completeness · January 2027 intake", [
                 Sec("What came in", p="Four files on Monday: two portal applications, one transcript scan and one applicant email. Seventeen requirement checks in all."),
                 Sec("Where each one stands", table=Tbl(None, ["Application", "Program", "Status", "Waiting on"],
                                                         ["26-3104 · Whitlock", "Electrical Engineering Technician", "Complete", "Admission decision"],
                                                         ["26-3117 · Marchetti", "Business Administration", "Waiting", "Official transcript"],
                                                         ["26-3122 · Kessler", "Computer Programming", "On hold", "Admissions officer: test date"],
                                                         ["26-3129 · Lindgren", "Accounting", "Complete", "Admission decision; registrar for credit"])),
                 Sec("Requirement checks by result", chart=Chart("Checks", ["Met", "Unclear or waiting", "Expires before start"], [14, 2, 1],
                                                                 tones=["ok", "check", "bad"])),
                 Sec("Follow-ups", list=["Admissions officer to decide on the 26-3122 test date before the next offer round.",
                                         "Registrar's office to pick up the 26-3129 transfer credit request when the college transcript arrives."])],
                 title="Intake report", subtitle="Admissions · invented data",
                 kpis=[(4, "Applications"), (2, "Complete", "ok"), (1, "Waiting on applicant", "check"), (1, "On hold", "bad")],
                 sources=["Applicant portal uploads, Mon", "Admissions inbox, Mon", "Program requirements table, January 2027 intake"],
                 format="Intake report"),
         ],
         next=["Applications and documents are picked up from the applicant portal and the admissions inbox as they arrive.",
               "Program requirements and document-validity rules come from a table your admissions team keeps.",
               "The admissions officer makes every admission decision and sends every follow-up.",
               "Transfer credit stays with the registrar's office."],
         tags=["admissions", "transcripts", "applications", "college", "completeness", "follow-up"]),

    # 2 ------------------------------------------------------------------------------------------
    case("edu-student-inbox", "Student services inbox",
         "Students write in about fees, timetables and transcripts. The assistant sorts each message, answers routine "
         "questions from the college's published policies and routes the rest to the right office. Staff approve and "
         "send every reply.",
         ("Student emails about fees, schedules and records", "Sorts, answers from policy with a citation, routes the rest",
          "Reads, edits and sends every reply", "Answered or routed messages, logged on the student file"),
         area="Student services", persona=("Tess Holloway", "Student services lead"), unit="Messages handled",
         docs=[
             D("Payment plan question.eml", "email", from_="sienna.ward@students.acme-college.example", to="studentservices@acme-college.example",
               subject="Can I split my winter fees?", meta="Email · Mon 08:05", label="Sienna Ward · fees", sub="Email · routine",
               body="Hi,\n\nIs it possible to pay my [[winter term fees|Topic]] in two parts instead of all at once?\n\n"
                    "Thanks,\nSienna Ward\nStudent ID [[2601487|Student]]",
               fields=[F("Type", "Fees: payment plan", "Message text"), F("Student", "Sienna Ward · 2601487", "Student ID, college email", 0.99),
                       F("Winter fees posted", "$2,140.00", "Student account"), F("Answer from", "Fee policy FP-3, section 2", "Policy library"),
                       F("Route to", "Student accounts (copy)", "Routing rule 1: fees")],
               table=Tbl("Checks", ["Check", "Result"], ["Student found", "Active, Business Administration, term 2", "ok"],
                         ["Eligible for a plan", "No balance owing from earlier terms", "ok"], ["Policy answer found", "FP-3, section 2", "ok"]),
               draft=Draft("Hi Sienna,\n\nYes. Under our fee policy you can pay winter fees in two instalments: half by [[4 January 2027]] and the rest by "
                           "[[1 February 2027]]. Please choose the payment plan option in the student portal by 15 December.\n\n"
                           "Student Services, Acme College",
                           label="Draft reply", to="Sienna Ward",
                           alt=["Hi Sienna,\n\nGood news: a two-part payment plan is available for winter. The first half is due [[4 January 2027]] "
                                "and the second [[1 February 2027]]. You can sign up in the student portal until 15 December.\n\nStudent Services, Acme College"]),
               yes="Send reply"),
             D("Timetable clash.eml", "email", from_="jprice.home@mailbox.example", to="studentservices@acme-college.example",
               subject="Two classes at the same time", meta="Email · Mon 08:47", label="Jordan Price · timetable", sub="Email · identity to confirm",
               body="Hello,\n\nMy winter timetable has [[ACC-1101 section 02|Course A]] and [[BUS-1150 section 01|Course B]] both on Tuesdays at 10:00. "
                    "What should I do?\n\nJordan Price",
               fields=[F("Type", "Timetable: clash", "Message text"),
                       F("Student", "?Jordan Price: two active students with this name (2600931, 2602215)", "Personal email, not on file", 0.45),
                       F("Course A", "ACC-1101-02 · Tue 10:00", "Winter timetable"), F("Course B", "BUS-1150-01 · Tue 10:00", "Winter timetable"),
                       F("Other sections", "BUS-1150-03 · Thu 13:00 · 4 seats open at 08:50", "Winter timetable", 0.85),
                       F("Route to", "Student services", "Routing rule 3: timetables")],
               table=Tbl("Checks", ["Check", "Result"], ["Clash confirmed", "Both sections meet Tue 10:00", "ok"],
                         ["Student identified", "Two records match the name", "check"], ["Open section", "BUS-1150-03 has seats", "ok"]),
               flags=["The email came from a personal address. Nothing from the student record goes in the reply until the student confirms their ID.",
                      "Seat counts change through the day. The reply says seats were open, not that one is held."],
               draft=Draft("Hi Jordan,\n\nThanks for flagging the clash. Section 03 of BUS-1150 meets on [[Thursdays at 13:00]] and had seats open this morning. "
                           "You can switch sections yourself in the student portal. If you'd like us to help, please reply from your college email "
                           "or include your [[student ID]].\n\nStudent Services, Acme College",
                           label="Draft reply", to="Jordan Price"),
               yes="Send reply"),
             D("Official transcript request.eml", "email", from_="m.okafor-reyes@students.acme-college.example", to="studentservices@acme-college.example",
               subject="Official transcript to another college", meta="Email · Mon 09:20", label="Malik Okafor-Reyes · transcript", sub="Email · hold on account",
               body="Hi,\n\nCould you send an [[official transcript|Topic]] to Ridgeview Polytechnic? I'm applying for their degree program and "
                    "the deadline is [[15 December|Deadline]].\n\nThanks,\nMalik Okafor-Reyes, ID [[2598840|Student]]",
               fields=[F("Type", "Records: official transcript", "Message text"), F("Student", "Malik Okafor-Reyes · 2598840", "Student ID, college email", 0.99),
                       F("Deadline", "15 Dec 2026", "Message text"), F("Answer from", "Records policy RP-1: requests, fees, holds", "Policy library"),
                       F("Route to", "Registrar's office (copy)", "Routing rule 5: transcripts")],
               table=Tbl("Checks", ["Check", "Result"], ["Student found", "Graduated June 2026, Accounting", "ok"],
                         ["Holds on account", "Library fine, $40.00", "bad"], ["Transcript fee", "$15.00, paid at request", "info"]),
               flags=[("bad", "Your records policy withholds official transcripts while a hold is on the account. The reply explains how to clear it."),
                      "Removing or waiving a hold is the registrar's decision."],
               draft=Draft("Hi Malik,\n\nThanks for your request. Before we can send an official transcript, a [[$40.00 library fine]] on your account needs to be cleared. "
                           "Once it's paid, request the transcript in the student portal ($15.00) and choose Ridgeview Polytechnic as the recipient. "
                           "Requests usually go out within five business days, so there's time before 15 December.\n\nStudent Services, Acme College",
                           label="Draft reply", to="Malik Okafor-Reyes"),
               yes="Send reply"),
             D("Final mark question - MKT-2204.eml", "email", from_="ava.lindqvist@students.acme-college.example", to="studentservices@acme-college.example",
               subject="My final project mark looks wrong", meta="Email · Mon 10:02", label="Ava Lindqvist · grade question", sub="Email · route to faculty",
               body="Hello,\n\nIn [[MKT-2204|Course]] my rubric shows [[42/50|Rubric mark]] for the final project, but the gradebook shows [[32/50|Gradebook mark]]. "
                    "I think it was entered wrong. Who do I talk to?\n\nAva Lindqvist, 2603312",
               fields=[F("Type", "Grades: possible entry error", "Message text"), F("Student", "Ava Lindqvist · 2603312", "Student ID, college email", 0.99),
                       F("Course", "MKT-2204 · Digital Marketing, fall", "Course list"), F("Rubric mark", "42/50 (student's copy)", "Message text"),
                       F("Gradebook mark", "32/50", "Message text"), F("Route to", "Course faculty, copy program coordinator", "Routing rule 8: grades")],
               table=Tbl("Checks", ["Check", "Result"], ["Grade questions", "Faculty only, per academic policy AP-2", "info"],
                         ["Grade appeal window", "10 business days from posting; mark posted Fri", "ok"]),
               flags=[("info", "The assistant doesn't look at or change marks. It routes the question and drafts an acknowledgement only.")],
               draft=Draft("Hi Ava,\n\nThanks for letting us know. We've passed your question about the MKT-2204 final project mark to your "
                           "[[instructor and program coordinator]], who handle grade questions. They'll reply directly. Raising it now keeps you within "
                           "the 10-business-day window under the academic policy.\n\nStudent Services, Acme College",
                           label="Acknowledgement", to="Ava Lindqvist"),
               yes="Route and acknowledge"),
         ],
         stages=[
             inbox("Student services inbox", "Messages arrive", "Email to studentservices@ from students and applicants."),
             process([("Reading each message", "Email body and attachments"), ("Sorting by type", "Fees, timetables, records, grades"),
                      ("Identifying the student", "College email or student ID; personal emails are not trusted"),
                      ("Finding the policy answer", "Published fee, records and academic policies"),
                      ("Routing and drafting", "Nothing is sent")],
                     title="Sorting and drafting",
                     log=[("Jordan Price: two student records, ID needed", "y", 2), ("2598840: library hold blocks official transcripts", "y", 3),
                          ("MKT-2204 grade question routed to faculty", "g", 4)]),
             review("Review and reply", "The message on the left, the policy answer or routing on the right.",
                    yes="Send reply", reasons=["Needs a different office", "Policy answer is wrong", "Student must confirm identity", "I'll answer this myself"]),
             ask([QA("Can a student on a payment plan register for spring?", "Yes, as long as both winter instalments are paid on time. A missed instalment puts a hold on registration until it is paid.",
                     "Fee policy FP-3, section 2", "Fee policy FP-3, section 5"),
                  QA("How long do official transcripts take?", "Up to five business days after the request is paid, if there are no holds on the account.",
                     "Records policy RP-1, section 3"),
                  QA("Can we change a student's grade if they show us the rubric?", "No. Only the course faculty can change a grade; student services routes the question.",
                     "Academic policy AP-2, section 1")],
                 "Ask the policy library", "Staff ask; answers come only from the college's own policies, with the section cited."),
             write("Student information system (test copy)", [
                 R("Contact note · Sienna Ward · 2601487", [("Topic", "Payment plan"), ("Reply", "Sent by staff")], "Logged"),
                 R("Contact note · Jordan Price · ID to confirm", [("Topic", "Timetable clash"), ("Waiting on", "Student ID")], "Logged, waiting", "check"),
                 R("Contact note · Malik Okafor-Reyes · 2598840", [("Topic", "Official transcript"), ("Blocked by", "Library hold")], "Logged", "bad"),
                 R("Referral · Ava Lindqvist · MKT-2204", [("To", "Course faculty, program coordinator"), ("Opened", "Mon 10:02")], "Routed", "info")],
                 sub="Each message is logged on the student's file with the reply a person sent.", cta="Save contact notes"),
             report("Student services inbox · Monday", [
                 Sec("What came in", p="Four student emails: one about fees, one about a timetable, one about records and one about a grade."),
                 Sec("Where each one stands", table=Tbl(None, ["Student", "Topic", "Outcome", "Waiting on"],
                                                         ["Sienna Ward", "Payment plan", "Answered from FP-3", "—"],
                                                         ["Jordan Price", "Timetable clash", "Answered in general terms", "Student ID"],
                                                         ["Malik Okafor-Reyes", "Official transcript", "Hold explained", "Fine to be paid"],
                                                         ["Ava Lindqvist", "Final mark", "Routed to faculty", "Instructor"])),
                 Sec("Messages by outcome", chart=Chart("Messages", ["Answered from policy", "Needs student action", "Routed to faculty"], [1, 2, 1],
                                                         tones=["ok", "check", "info"]))],
                 title="Inbox summary", subtitle="Student services · invented data",
                 kpis=[(4, "Messages"), (3, "Replies drafted"), (1, "Routed to faculty", "info"), (1, "Hold on account", "bad")],
                 sources=["Fee policy FP-3", "Records policy RP-1", "Academic policy AP-2"]),
         ],
         next=["Messages are read from the student services inbox as they arrive.",
               "Answers come only from your published policies, each with its section cited.",
               "Staff read, edit and send every reply; grades, holds and credit stay with their offices.",
               "Students writing from personal email are asked to confirm their ID before anything from their file is shared."],
         tags=["student services", "inbox", "fees", "transcripts", "timetable", "college"]),

    # 3 ------------------------------------------------------------------------------------------
    case("edu-course-outline", "Course outline and accreditation map",
         "Revised course outlines come in for the program review. The assistant maps each course outcome to the program's "
         "learning outcomes, checks assessment weights and reading lists, and flags gaps against your quality framework. "
         "The program chair approves the map.",
         ("Course outlines and program learning outcomes", "Maps course outcomes to program outcomes, flags gaps and outdated items",
          "Settles every unclear mapping and approves the report", "A mapping report for the quality office"),
         area="Curriculum and quality", persona=("Colin Mercer", "Program chair, Business Administration"), unit="Outlines mapped",
         docs=[
             D("Program outcomes and 2023 map.xlsx", "sheet", meta="Spreadsheet · quality office · June 2023",
               label="Program outcomes · 2023 map", sub="Reference · 6 outcomes",
               rows=[["Outcome", "Program learning outcome", "Courses (2023 map)"],
                     ["[[PLO1|PLO1]]", "Explain how business functions work together", "BUS-1101, BUS-2210"],
                     ["[[PLO2|PLO2]]", "Communicate business information clearly", "BUS-1101, COM-1120"],
                     ["[[PLO3|PLO3]]", "Analyse financial information to support decisions", "ACC-1101, ACC-2150"],
                     ["[[PLO4|PLO4]]", "Use digital tools to analyse and present data", "CIS-1105, BUS-2210"],
                     ["[[PLO5|PLO5]]", "Work effectively in teams", "BUS-1101, BUS-2330"],
                     ["[[PLO6|PLO6]]", "Apply ethical and sustainable practice", "BUS-1101, BUS-2330"]],
               body="Business Administration diploma · last full map [[June 2023|Last map]]",
               fields=[F("Program", "Business Administration · diploma", "Sheet title"), F("Outcomes", "6 program learning outcomes", "Rows 2-7"),
                       F("Last map", "June 2023", "Sheet title"), F("In this review", "BUS-1101, BUS-2210, BUS-2330", "Review request")],
               flags=["Your quality framework asks for a full map every three years. The last one is from June 2023, so this review is due."],
               notes="Reference for the mapping. Each program outcome must be assessed at an advanced level in at least one second-year course, per your quality framework.",
               yes="Use as reference"),
             D("BUS-1101 Introduction to Business - outline.pdf", "pdf", meta="PDF · 5 pages · revised Oct 2026",
               label="BUS-1101 · Introduction to Business", sub="Year 1 · maps cleanly",
               body="BUS-1101 INTRODUCTION TO BUSINESS · Fall 2026\n\nCourse learning outcomes\n"
                    "1. [[Describe the main functions of a business and how they connect|CLO1]]\n2. [[Write a short business report for a manager|CLO2]]\n"
                    "3. [[Present a business case as part of a team|CLO3]]\n4. [[Identify ethical issues in a business case|CLO4]]\n\n"
                    "Assessment: Report 30% · Team presentation 30% · Quizzes 20% · Final test 20%\n"
                    "Required text: [[Business Today, 6th edition, 2023|Required text]]",
               fields=[F("CLO1", "PLO1 · introduced", "Outcome 1", 0.95), F("CLO2", "PLO2 · introduced", "Outcome 2", 0.96),
                       F("CLO3", "PLO5 · introduced", "Outcome 3", 0.94), F("CLO4", "PLO6 · introduced", "Outcome 4", 0.93),
                       F("Required text", "2023 edition", "Page 4")],
               table=Tbl("Checks", ["Check", "Result"], ["Every course outcome maps to a program outcome", "4 of 4", "ok"],
                         ["Assessment weights", "Add to 100%", "ok"], ["Required text", "Within 8 years, your review rule", "ok"]),
               notes="All four outcomes map at the introductory level. No changes needed.", yes="Accept mapping"),
             D("BUS-2210 Operations Management - outline.pdf", "pdf", meta="PDF · 6 pages · revised Oct 2026",
               label="BUS-2210 · Operations Management", sub="Year 2 · one unclear, old text",
               body="BUS-2210 OPERATIONS MANAGEMENT · Winter 2027\n\nCourse learning outcomes\n"
                    "1. [[Map a business process and find its bottleneck|CLO1]]\n2. [[Build a spreadsheet model to plan inventory and its cost|CLO2]]\n"
                    "3. [[Measure quality with simple control charts|CLO3]]\n\n"
                    "Assessment: Process map project 35% · Inventory model 25% · Midterm 20% · Final 20%\n"
                    "Required text: [[Operations Essentials, 3rd edition, 2014|Required text]]",
               fields=[F("CLO1", "PLO1 · advanced", "Outcome 1", 0.93),
                       F("CLO2", "?PLO4 (digital tools) or PLO3 (financial analysis)", "Outcome 2 fits both", 0.5),
                       F("CLO3", "PLO4 · advanced", "Outcome 3", 0.9), F("Required text", "2014 edition", "Page 5", 0.98)],
               table=Tbl("Checks", ["Check", "Result"], ["Every course outcome maps to a program outcome", "2 of 3 clear", "check"],
                         ["Assessment weights", "Add to 100%", "ok"], ["Required text", "12 years old; your rule flags over 8", "check"]),
               flags=["CLO2 could support either PLO3 or PLO4. Only faculty know what the inventory rubric grades, so it is left unmapped.",
                      "The required text is from 2014. A newer edition may exist; faculty confirm."]),
             D("BUS-2330 Digital Marketing - revised outline.docx", "docx", meta="Word · draft from faculty · Nov 2026",
               label="BUS-2330 · Digital Marketing", sub="Year 2 · weights and a gap",
               body="BUS-2330 DIGITAL MARKETING · Winter 2027 (revised draft)\n\nCourse learning outcomes\n"
                    "1. [[Plan a digital campaign for a small business|CLO1]]\n2. [[Measure campaign results with web analytics|CLO2]]\n"
                    "3. [[Pitch a campaign plan to a client panel as a team|CLO3]]\n"
                    "(2023 outcome 4, \"Evaluate marketing practices against ethical and privacy standards\", removed)\n\n"
                    "Assessment: Campaign plan 40% · Analytics report 25% · Team pitch 25% · Participation 15%  = [[105%|Weights]]\n"
                    "Required text: Digital Marketing Practice, 2025",
               fields=[F("CLO1", "PLO1 · advanced", "Outcome 1", 0.92), F("CLO2", "PLO4 · advanced", "Outcome 2", 0.94),
                       F("CLO3", "PLO5 · advanced", "Outcome 3", 0.93), F("Weights", "105%", "Assessment table", 0.99),
                       F("Removed outcome", "Ethics and privacy (was PLO6)", "Compared with the 2023 outline")],
               table=Tbl("Checks", ["Check", "Result"], ["Every course outcome maps to a program outcome", "3 of 3", "ok"],
                         ["Assessment weights", "Add to 105%", "bad"], ["Required text", "2025 edition", "ok"],
                         ["PLO6 at an advanced level", "This was the only year-2 course for PLO6", "bad"]),
               flags=[("bad", "Weights add to 105%. The assistant doesn't change an outline; faculty fix it."),
                      ("bad", "Removing the ethics outcome leaves PLO6 with no second-year course. Your framework needs one.")],
               draft=Draft("Hi Ines,\n\nThanks for the revised BUS-2330 outline. Two things before it goes to the committee:\n\n"
                           "- The assessment weights add to [[105%]].\n- The ethics and privacy outcome from 2023 is gone. It was the only year-2 course "
                           "covering program outcome 6, so the program chair would like to talk about where that outcome now sits.\n\nColin",
                           label="Note to faculty", to="Ines Varga", subject="BUS-2330 outline: two items"),
               yes="Send to faculty"),
         ],
         stages=[
             upload("Outlines arrive", "Revised outlines from faculty and the program's outcomes sheet from the quality office."),
             process([("Reading outlines", "Outcomes, assessments, required texts"), ("Comparing with the 2023 outlines", "What was added or removed"),
                      ("Mapping course outcomes", "Each course outcome to a program outcome and level"),
                      ("Checking your quality rules", "Weights, text age, advanced coverage of every program outcome"),
                      ("Marking what it isn't sure of", "Unclear mappings are left for faculty")],
                     log=[("BUS-2210 CLO2: fits PLO3 and PLO4, left unmapped", "y", 2), ("BUS-2330 weights add to 105%", "y", 3),
                          ("PLO6: no year-2 course after the BUS-2330 change", "y", 3)]),
             review("Review each outline", "The outline on the left, the mapping and checks on the right.",
                    yes="Accept mapping", reasons=["Mapping is wrong", "Faculty to revise the outline", "Needs the curriculum committee", "I'll map this one myself"]),
             compare(Tbl("Curriculum map · after this review", ["Program outcome", "Courses mapped", "Advanced level", "Change since 2023"],
                         ["PLO1 · Business functions", "BUS-1101, BUS-2210, BUS-2330", "Yes", "BUS-2330 added", "ok"],
                         ["PLO2 · Communication", "BUS-1101 (COM-1120 not in this review)", "Yes, COM-1120", "None", "ok"],
                         ["PLO3 · Financial analysis", "ACC courses not in this review", "Yes, ACC-2150", "BUS-2210 CLO2 unclear", "check"],
                         ["PLO4 · Digital tools", "BUS-2210, BUS-2330", "Yes", "BUS-2330 added", "ok"],
                         ["PLO5 · Teamwork", "BUS-1101, BUS-2330", "Yes", "None", "ok"],
                         ["PLO6 · Ethics and sustainability", "BUS-1101 only", "No", "BUS-2330 dropped its ethics outcome", "bad"]),
                     "Curriculum map", "One row per program outcome. Filter to see the gaps."),
             exceptions([
                 X("PLO6 has no advanced-level course", "After the BUS-2330 revision, ethics and sustainability is only introduced in BUS-1101.",
                   ["Ask BUS-2330 faculty to restore an ethics outcome", "Add an ethics outcome to BUS-2210", "Take it to the curriculum committee"],
                   rec=2, tone="bad", why="Moving an outcome between courses affects two faculty members; the committee usually settles that."),
                 X("BUS-2210 inventory model: PLO3 or PLO4?", "CLO2 builds a spreadsheet model that also costs the inventory.",
                   ["Map to PLO4", "Map to PLO3", "Map to both"], why="Only faculty know what the rubric grades. The assistant leaves it to them."),
                 X("BUS-2210 required text from 2014", "Your review rule flags required texts older than eight years.",
                   ["Ask faculty for a current edition", "Keep it: faculty confirm it's still right", "Note it for the next review"], rec=0),
                 X("BUS-2330 weights add to 105%", "Campaign plan 40, analytics 25, pitch 25, participation 15.",
                   ["Return to faculty to fix", "Hold the outline until the committee meets"], rec=0, tone="bad",
                   why="Weights are set by faculty; the assistant never edits an outline."),
             ], "Gaps and fixes", "Each item needs the chair's decision. The assistant suggests; you choose."),
             report("Course outline mapping · Business Administration · 2026 review", [
                 Sec("Summary", p="Three revised outlines were mapped against the six program learning outcomes. Nine of ten course outcomes map clearly; one is left for faculty."),
                 Sec("Curriculum map", table=Tbl(None, ["Program outcome", "Courses in this review", "Advanced level"],
                                                 ["PLO1", "BUS-1101, BUS-2210, BUS-2330", "Yes"], ["PLO2", "BUS-1101", "Yes (COM-1120)"],
                                                 ["PLO3", "None in this review", "Yes (ACC-2150)"], ["PLO4", "BUS-2210, BUS-2330", "Yes"],
                                                 ["PLO5", "BUS-1101, BUS-2330", "Yes"], ["PLO6", "BUS-1101", "No: gap"])),
                 Sec("Course outcomes per program outcome", chart=Chart("Course outcomes (this review)", ["PLO1", "PLO2", "PLO3", "PLO4", "PLO5", "PLO6", "Unclear"],
                                                                         [3, 1, 0, 2, 2, 1, 1], tones=["ok", "ok", "check", "ok", "ok", "bad", "check"])),
                 Sec("Outline fixes with faculty", list=["BUS-2330: assessment weights add to 105%.", "BUS-2210: required text from 2014.",
                                                        "BUS-2210: faculty to say whether CLO2 supports PLO3 or PLO4."]),
                 Sec("Decision for the chair", list=["Where PLO6 is assessed at an advanced level from Winter 2027."])],
                 title="Mapping report", subtitle="Curriculum and quality · invented data",
                 kpis=[(3, "Outlines"), (10, "Course outcomes"), (9, "Mapped", "ok"), (1, "Unclear", "check"), (1, "Program gap", "bad")],
                 sources=["Program outcomes and 2023 map, quality office", "BUS-1101 outline, Oct 2026", "BUS-2210 outline, Oct 2026",
                          "BUS-2330 revised outline, Nov 2026", "Quality framework: coverage and text-age rules"],
                 format="Mapping report"),
             approve("Send the mapping report to the quality office?", "Chair approval",
                     summary=[("Outlines", "3 mapped"), ("Open items", "1 unclear mapping, 2 outline fixes"), ("Program gap", "PLO6, for the committee")],
                     checks=["I settled or assigned every unclear mapping", "Faculty have the outline fixes", "The PLO6 gap is listed, not hidden"],
                     yes="Approve report"),
         ],
         next=["Outlines are collected from the curriculum folder as faculty submit them.",
               "Program outcomes and your quality rules come from the quality office's own sheet.",
               "Faculty own their outlines; the assistant never edits one.",
               "The program chair approves every map before it goes to the quality office or a review panel."],
         tags=["curriculum", "course outline", "learning outcomes", "accreditation", "program review", "college"]),
]
