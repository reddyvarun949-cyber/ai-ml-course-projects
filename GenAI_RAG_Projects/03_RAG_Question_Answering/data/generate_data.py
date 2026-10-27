"""Generate the employee handbook and the evaluation questions used in this project.

Run from the project root:  python data/generate_data.py

Outputs
    data/handbook/*.md          10 policy documents of the fictional company "Sunrise Tech Pvt Ltd"
    data/eval_questions.csv     32 test questions with the expected source document and key fact

Everything here is invented for teaching. Names, e-mail addresses and numbers do not belong to any real company.
The text is fixed (no randomness), so every student gets exactly the same files. A little realistic messiness is
added on purpose: Windows line endings in one file, trailing spaces and extra blank lines in another, and a
"Last updated" line at the top of some documents. The loader in backend/rag/loader.py cleans this up.
"""
import csv
import os

HERE = os.path.dirname(os.path.abspath(__file__))
HANDBOOK_DIR = os.path.join(HERE, "handbook")

DOCS = {}

DOCS["leave_policy.md"] = """
# Leave Policy

Last updated: 1 January 2026. Applies to all permanent employees of Sunrise Tech Pvt Ltd.

## Leave year

The leave year runs from 1 January to 31 December. Leave balances are shown in the SunPeople HR portal.

## Earned leave

Every employee gets 18 days of earned leave per year. Earned leave is credited at 1.5 days per month.
Unused earned leave can be carried forward to the next year up to a maximum of 30 days. Any balance above 30 days
lapses on 31 December. At the end of the year you may encash up to 10 days of earned leave at your basic salary.

## Casual leave

You get 8 days of casual leave per year for short personal needs. Casual leave can be taken for at most 3 consecutive
days and cannot be carried forward to the next year.

## Sick leave

You get 10 days of sick leave per year. A medical certificate from a registered doctor is required when sick leave is
taken for more than 2 consecutive days. Unused sick leave cannot be encashed.

## Maternity and paternity leave

Women employees are entitled to 26 weeks of paid maternity leave. Fathers get 10 working days of paid paternity leave,
which must be taken within 3 months of the child's birth or adoption.

## How to apply for leave

Apply for leave in SunPeople. Planned leave of 3 days or more must be applied for at least 7 days in advance.
Your manager should approve or reject the request within 2 working days. Leave without pay is allowed for a maximum of
30 days per year and needs approval from the HR head.
"""

DOCS["work_from_home.md"] = """
# Work From Home and Hybrid Work Policy

## Hybrid work pattern

Employees in hybrid roles may work from home for up to 2 days per week. Tuesday and Thursday are core office days,
and everyone in a hybrid role must be in the office on those days. Work-from-home days must be requested in SunPeople
by Friday of the previous week.

## Core working hours

When working from home you must be online and reachable between 11:00 AM and 4:00 PM IST (core hours). Keep your
status on the chat tool up to date.

## Allowances

Hybrid employees receive an internet allowance of ₹1,500 per month, paid with the monthly salary. A one-time home
office setup reimbursement of up to ₹5,000 is available for a chair or desk; submit the bill within 60 days of purchase.

## Fully remote work

Fully remote work is an exception and needs approval from a Vice President. Fully remote arrangements are reviewed
every 6 months.

## Working from another location

You may work from another Indian city for up to 15 days per year with your manager's approval. Working from outside
India is not allowed because of tax and data protection rules.
"""

DOCS["travel_expense.md"] = """
# Travel and Expense Reimbursement Policy

## Booking travel

All business travel is booked through the travel desk (travel@sunrisetech.example). Flights must be requested at
least 10 days before the travel date. Flights are booked in economy class. Business class is allowed only for flights
longer than 6 hours and only for employees in Band 5 and above.

## Hotel limits per night

| City category | Examples | Hotel limit per night |
|---|---|---|
| Metro | Mumbai, Delhi, Bengaluru | ₹6,000 |
| Tier-2 | Pune, Jaipur, Kochi | ₹4,000 |
| Other cities | all other places | ₹2,500 |

## Daily allowance

The daily allowance (per diem) for meals is ₹1,200 per day on domestic trips and USD 60 per day on international trips.
Alcohol is never reimbursed.

## Local travel

Local cab fares are reimbursed at actuals up to ₹1,000 per day. If you use your own car for official work you can
claim ₹12 per km.

## Submitting expense claims

Submit expense claims in SunPeople within 30 days of the end of the trip. Attach receipts for every expense above ₹500.
Claims submitted after 30 days need approval from the finance controller. Approved claims are paid within 15 working
days.
"""

DOCS["it_security.md"] = """
# IT Security and Password Policy

Last updated: 15 March 2026.

## Passwords

Passwords must be at least 12 characters long and include upper-case letters, lower-case letters, a number and a symbol.
You must change your password every 90 days. Your last 5 passwords cannot be reused. Never share your password, not even
with the IT helpdesk.

## Multi-factor authentication

Multi-factor authentication (MFA) is mandatory for e-mail and VPN. Use the SunAuth app on your phone to approve sign-ins.

## Devices and networks

Laptops lock automatically after 5 minutes of inactivity; lock your screen whenever you leave your desk. USB storage
devices such as pen drives are blocked on company laptops. Install software only from the Company Portal. On public or
guest Wi-Fi, for example in hotels, airports or at a client site, always connect through the company VPN.

## Reporting incidents

Report a lost or stolen laptop or phone to the IT helpdesk (extension 4357) within 2 hours. Forward suspicious e-mails
to security@sunrisetech.example or use the Report Phish button.

## Data handling

Do not upload confidential company or client data to public AI tools or personal cloud storage.
"""

DOCS["code_of_conduct.md"] = """
# Code of Conduct

## Our values

We act with integrity, treat every colleague with respect and protect the information our clients trust us with.

## Gifts and hospitality

You may accept gifts from vendors or clients worth up to ₹2,000. Gifts above ₹2,000 must be declared to the compliance
team within 7 days, and cash gifts must always be refused.

## Conflict of interest

Declare any conflict of interest to the compliance team as soon as it arises and in the annual declaration due by
30 April each year. Outside paid work (moonlighting) needs written approval from HR before you start.

## Harassment

Sunrise Tech has zero tolerance for harassment. Complaints of sexual harassment are handled by the Internal Committee
(IC), which can be reached at ic@sunrisetech.example. A complaint should be filed within 3 months of the incident.

## Social media

Do not share confidential information on social media. Only the corporate communications team may speak on behalf of
the company.

## Breaking the code

Violations of this code may lead to disciplinary action, up to and including termination of employment.
"""

DOCS["health_insurance.md"] = """
# Health Insurance Benefits

## Group medical insurance

All employees are covered by group medical insurance with a sum insured of ₹5,00,000 per family per year. The family
covers the employee, spouse and up to 2 children. Insurance is administered by CarePlus TPA.

## Adding parents

Employees can add their parents for a premium of ₹9,000 per parent per year, deducted from salary. Parents get a
separate cover of ₹3,00,000 per year.

## Enrolment

Enrol yourself and your family within 30 days of joining. A newborn child must be added within 30 days of birth.

## Hospitalisation

Cashless treatment is available at network hospitals. For planned hospitalisation, request pre-authorisation at least
48 hours in advance. For emergency hospitalisation, inform CarePlus TPA within 24 hours of admission. Room rent is
capped at ₹10,000 per day.

## What is covered

Maternity expenses are covered up to ₹75,000 within the sum insured. OPD consultations and dental treatment are not
covered. Employees aged 35 and above get a free annual health check-up.
"""

DOCS["onboarding.md"] = """
# Onboarding Guide for New Joiners

## Your first day

Report at 9:30 AM to the reception at Sunrise Tech Park, Pune. Bring your PAN card, Aadhaar card, educational
certificates, relieving letter from your previous employer, 2 passport-size photos and a cancelled cheque. Your laptop
is issued by IT on day 1, and your ID card is ready within 3 working days.

## Your first month

A buddy is assigned to help you for the first 30 days. Complete the mandatory information security and POSH
(prevention of sexual harassment) trainings within your first 14 days.

## Probation and notice period

The probation period is 6 months. During probation the notice period is 15 days. After confirmation the notice period
is 60 days.

## Salary

Salary is paid on the last working day of each month. If you join after the 20th of a month, that month's salary is
paid together with the next month's salary.
"""

DOCS["performance_review.md"] = """
# Performance Review Process

## Review calendar

Performance is reviewed once a year in April, with a mid-year check-in in October. Submit your self-assessment in
SunPeople by 10 April. Goals for the new year must be set by 15 May.

## Rating scale

Ratings use a 1 to 5 scale: 5 = Outstanding, 4 = Exceeds expectations, 3 = Meets expectations,
2 = Partially meets expectations, 1 = Below expectations.

## Increments and bonus

Salary increments take effect from 1 July. The annual performance bonus is paid in July. The bonus multiplier is 150%
of target for rating 5, 120% for rating 4, 100% for rating 3, 50% for rating 2 and 0% for rating 1.

## Promotions

You are eligible for promotion after at least 18 months in your current band, with a rating of 4 or 5 in the latest
review.

## Performance improvement plan

An employee rated 1, or rated 2 in two consecutive reviews, is placed on a 90-day performance improvement plan (PIP).
"""

DOCS["holidays_2026.md"] = """
# Holiday List 2026 (Pune and Bengaluru offices)

## Fixed holidays

| Date | Day | Holiday |
|---|---|---|
| 1 January | Thursday | New Year's Day |
| 26 January | Monday | Republic Day |
| 4 March | Wednesday | Holi |
| 3 April | Friday | Good Friday |
| 1 May | Friday | Maharashtra Day / Labour Day |
| 15 August | Saturday | Independence Day |
| 14 September | Monday | Ganesh Chaturthi |
| 2 October | Friday | Gandhi Jayanti |
| 20 October | Tuesday | Dussehra |
| 9 November | Monday | Diwali |
| 10 November | Tuesday | Diwali (Balipratipada) |
| 25 December | Friday | Christmas |

## Floating holidays

Each employee may choose 2 floating holidays from this list: Makar Sankranti (14 January), Eid al-Fitr (20 March),
Raksha Bandhan (28 August) and Guru Nanak Jayanti (24 November). Select your floating holidays in SunPeople by
31 January.

## Holidays on weekends and holiday work

When a holiday falls on a Saturday or Sunday, no replacement day off is given. If your manager asks you to work on a
holiday, you get a compensatory day off, which must be taken within 30 days.
"""

DOCS["grievance_process.md"] = """
# Grievance Redressal Process

## Step 1: Talk to your manager

Most concerns can be solved quickly by talking to your manager first.

## Step 2: Raise a formal grievance

If the issue is not solved, raise a formal grievance using the Grievance form in SunPeople or by e-mail to
grievance@sunrisetech.example. HR acknowledges the grievance within 2 working days and aims to resolve it within
15 working days.

## Step 3: Appeal

If you are not satisfied with the decision, you can appeal to the Grievance Committee within 10 working days of
receiving the decision. The committee gives its final decision within 30 days.

## Anonymous reporting and protection

You can report concerns anonymously through the ethics hotline (extension 7788). Sunrise Tech does not tolerate
retaliation against anyone who raises a concern in good faith. Sexual harassment complaints go to the Internal
Committee described in the Code of Conduct.
"""

# question_id, question, type, expected_docs (";" separated), expected_facts (";" separated)
QUESTIONS = [
    ("Q01", "How many earned leave days do I get per year?", "direct", "leave_policy", "18 days"),
    ("Q02", "Can I carry forward unused earned leave? What is the limit?", "direct", "leave_policy", "30 days"),
    ("Q03", "When do I need a medical certificate for sick leave?", "direct", "leave_policy",
     "more than 2 consecutive days"),
    ("Q04", "How long is paternity leave?", "direct", "leave_policy", "10 working days"),
    ("Q05", "How many days a week can I work from home?", "direct", "work_from_home", "2 days per week"),
    ("Q06", "What is the internet allowance for hybrid employees?", "direct", "work_from_home", "₹1,500"),
    ("Q07", "Which days do I have to come to the office?", "paraphrase", "work_from_home", "Tuesday and Thursday"),
    ("Q08", "What is the hotel limit per night in Mumbai?", "direct", "travel_expense", "₹6,000"),
    ("Q09", "How much money do I get for food each day on a domestic trip?", "paraphrase", "travel_expense",
     "₹1,200"),
    ("Q10", "How soon after a trip must I submit my expense claim?", "direct", "travel_expense", "30 days"),
    ("Q11", "Who is allowed to fly business class?", "direct", "travel_expense", "Band 5"),
    ("Q12", "What is the minimum password length?", "direct", "it_security", "12 characters"),
    ("Q13", "I lost my laptop. Whom should I tell and how quickly?", "direct", "it_security", "2 hours"),
    ("Q14", "Can I copy files to a pen drive on my office laptop?", "paraphrase", "it_security", "blocked"),
    ("Q15", "What is the maximum value of a gift I can accept from a vendor?", "direct", "code_of_conduct", "₹2,000"),
    ("Q16", "Do I need permission to do freelance work on weekends?", "paraphrase", "code_of_conduct",
     "written approval from HR"),
    ("Q17", "What is the sum insured under the health insurance?", "direct", "health_insurance", "₹5,00,000"),
    ("Q18", "Can I add my parents to the medical insurance and what does it cost?", "direct", "health_insurance",
     "₹9,000"),
    ("Q19", "What documents should I bring on my first day?", "direct", "onboarding", "PAN card"),
    ("Q20", "How long is the probation period?", "direct", "onboarding", "6 months"),
    ("Q21", "If I resign after confirmation, how many days must I serve?", "paraphrase", "onboarding", "60 days"),
    ("Q22", "When is the self-assessment due?", "direct", "performance_review", "10 April"),
    ("Q23", "How long do I have to stay in my band before I can be promoted?", "direct", "performance_review",
     "18 months"),
    ("Q24", "Is 2 October a holiday?", "direct", "holidays_2026", "Gandhi Jayanti"),
    ("Q25", "How many floating holidays can I choose?", "direct", "holidays_2026", "2 floating holidays"),
    ("Q26", "How long does HR take to resolve a formal grievance?", "direct", "grievance_process",
     "15 working days"),
    ("Q27", "I am a new joiner. How long is my probation and by when must I enrol in health insurance?",
     "multi_doc", "onboarding;health_insurance", "6 months;30 days of joining"),
    ("Q28", "I am travelling to Delhi for a client visit. What is my hotel limit, and how should I use the hotel Wi-Fi?",
     "multi_doc", "travel_expense;it_security", "₹6,000;VPN"),
    ("Q29", "Does Sunrise Tech offer employee stock options (ESOP)?", "unanswerable", "", ""),
    ("Q30", "What is on the cafeteria lunch menu today?", "unanswerable", "", ""),
    ("Q31", "How much is the Diwali bonus?", "unanswerable", "", ""),
    ("Q32", "Who is the CEO of Sunrise Tech?", "unanswerable", "", ""),
]
# Q33 and beyond are left for the students' own experiments.
QUESTIONS += [
    ("Q33", "Can I bring my pet dog to the office?", "unanswerable", "", ""),
]


def write_handbook():
    os.makedirs(HANDBOOK_DIR, exist_ok=True)
    for old in os.listdir(HANDBOOK_DIR):              # start clean so removed documents do not linger
        if old.endswith(".md"):
            os.remove(os.path.join(HANDBOOK_DIR, old))
    for name, text in DOCS.items():
        text = text.strip() + "\n"
        newline = "\n"
        if name == "travel_expense.md":                # messiness: Windows line endings
            newline = "\r\n"
        if name == "health_insurance.md":              # messiness: trailing spaces and extra blank lines
            text = text.replace(".\n", ".   \n").replace("\n## ", "\n\n\n## ")
        with open(os.path.join(HANDBOOK_DIR, name), "w", encoding="utf-8", newline=newline) as f:
            f.write(text)


def write_questions():
    path = os.path.join(HERE, "eval_questions.csv")
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["question_id", "question", "question_type", "expected_docs", "expected_facts"])
        w.writerows(QUESTIONS)
    return path


if __name__ == "__main__":
    write_handbook()
    path = write_questions()
    print(f"Wrote {len(DOCS)} handbook documents to {HANDBOOK_DIR}")
    print(f"Wrote {len(QUESTIONS)} evaluation questions to {path}")
