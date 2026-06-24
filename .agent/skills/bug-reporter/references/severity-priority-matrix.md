# Severity vs Priority Classification Matrix

To eliminate subjectivity in triage, enterprise teams must strictly distinguish between **Severity** (technical impact) and **Priority** (business urgency). 

---

## 1. Defining the Core Concepts

- **Severity (Technical Impact)**: Measures how severely a bug degrades system performance, data integrity, security, or functionality. Determined primarily by **QA and Engineering Leads**.
- **Priority (Business Urgency)**: Measures how quickly the business needs the bug resolved. Determined by **Product Managers (PMs), Business Stakeholders, and Release Management**.

> [!NOTE]
> Severity and Priority do not always match! 
> A minor visual typo on the home page has **Low Severity**, but if it is on the core corporate investor presentation page during an IPO, it receives **High Priority** for an immediate fix.

---

## 2. Objective Severity Classification (S1 - S4)

| Severity Level | Technical Definition | Examples |
| :--- | :--- | :--- |
| **P1 Blocker ** | Complete system outage, data corruption risk, security compromise (exploit), or total blockage of a core business workflow with no workaround. | - Database crash on login.<br>- API Gateway returning 500 for all search calls.<br>- Unencrypted user passwords visible in console logs. |
| **P2 Blocker ** | Total blockage of a core business workflow with no workaround. | - Database crash on login.<br>- API Gateway returning 500 for all search calls.<br>- Unencrypted user passwords visible in console logs. |
| **P3 Major** | A core business function is broken or degrades severely, but a reasonable technical workaround is available for users. | - Discount code button fails on Safari but works on Chrome/Firefox.<br>- Freelancer list filtering takes >10 seconds, violating SLA but still returns results. |
| **P4 Minor** | A non-critical feature is broken or fails. Visual or operational degradation that does not prevent user progression. | - Profile picture upload fails for GIF formats but works for JPG/PNG.<br>- Clear Filter button resets checkboxes but fails to reset location search text. |
| **P5 Trivial** | Visual issues, spacing errors, font discrepancies, layout misalignments, or simple spelling typos that carry zero functional impact. | - Apply Filters text is misspelled as 'Aply Filers'.<br>- Padding between list entries is 10px instead of 16px. |

---

## 3. Triage Mapping Matrix

Use this mapping tool to align technical findings with business prioritization:

```
                  +-------------------------------------------------------+
                  |                      SEVERITY                         |
                  +-----------------+-------------------+-----------------+
                  |  S1 (Blocker)   |    S2 (Major)     |   S3/S4 (Minor) |
+---+-------------+-----------------+-------------------+-----------------+
| P | P1 (Immediate) Total outage,  | Safety breach,    | Visually bad,   |
| R |             | revenue block   | exploit risk      | high visibility |
| I +-------------+-----------------+-------------------+-----------------+
| O | P2 (High)   | Workaround      | Core UI broken    | Minor broken    |
| R |             | exists but bad  | for major browsers| customer flows  |
| I +-------------+-----------------+-------------------+-----------------+
| T | P3/P4 (Med) | Backup systems  | Niche feature     | Typos, padding, |
| Y |             | active, internal| failures          | alignment       |
+---+-------------+-----------------+-------------------+-----------------+
```
