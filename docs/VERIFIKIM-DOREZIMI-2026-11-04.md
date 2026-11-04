# Verifikim i dorëzimit Meta — 04.11.2026 17:2x

**Burimi (jo derivati):** API-i i platformës Cerebral Valley, i lexuar me sesionin Clerk të Klloshës
(Chromium CDP :18800), vetëm GET — asnjë shkrim, asnjë PATCH.

```
GET https://api.cerebralvalley.ai/v1/event/meta-ai-developer-hackathon/hackathon/submissions/user
→ 200  {"detail": "User hackathon submissions retrieved successfully", "submissions": [ ... ]}
```

## Dorëzimi

| Fushë | Vlerë |
|---|---|
| id | `cbd0a66f-368b-4699-97a1-db81ca4aa92d` |
| ekip | Halimi (teamNumber 2), anëtar: Arber Arifi / arifi.arber@gmail.com |
| krijuar | 2026-10-26 17:17:51 |
| aplikimi i eventit | `status: approved`, waiver i nënshkruar |

## Fushat e formularit (11)

| Fusha | Lloji | Kërkuar | Vlera | Ndryshuar |
|---|---|---|---|---|
| Which track are you submitting to? | select | po | Indie Developer Track | 26.10 |
| Which problem statement did you build towards? | select | po | Build for Your World | 26.10 |
| Project Description | text | po | plotësuar | 28.10 08:26 |
| Public GitHub Repository | url | po | github.com/arifiarber-sYn/halim-fatura-agent | 26.10 |
| 3-Minute Demo Video | url | po | `.../demo-halimi-en-v3.mp4` (jsDelivr) | **03.11 19:26** |
| Use of Meta products | text | po | plotësuar (Muse Wonder 1.0, reasoning_effort=minimal) | 28.10 08:26 |
| Why are Meta's models important | text | po | plotësuar | 28.10 08:26 |
| Feedback on partner technologies | short_text | jo | plotësuar | 28.10 08:26 |
| Likely to build with Meta Model API | select | po | Very likely | 03.11 19:26 |
| Overall opinion of Meta Model API | select | po | Very favorable | 03.11 19:26 |
| Marketing permission (Meta/CV publish) | checkbox | **jo** | false | 26.10 |

**Të gjitha fushat e detyrueshme janë plotësuar.** Checkbox-i i fundit është opsional
(leje marketingu) — mbetet `false` me vetëdije, nuk bllokon.

## Pse faqja /submit duket «closed»

`cv_submit_check.py` raportoi `status: closed, fushat: 0` në 14:17, 16:17 dhe 17:16
(para 14:17: `open, 4 fusha`). Shkaku: rruga `/hackathon/submit` ridrejton te faqja e
eventit kur përdoruesi **ka tashmë një dorëzim** — jo sepse afati u mbyll. Afati i shpallur
në faqe: **Oct 26, 6:00 PM – Nov 5, 3:00 AM (GMT+1)**.

Kjo është e njëjta klasë defekti e shënuar më 04.11 (L-378): *leximi i pamjes së formularit
në vend të burimit (API)*.

## Rreziku i mbetur

Asnjë veprim nuk kërkohet nga Kllosha për dorëzimin. Mbetet vetëm vlerësimi i jurisë.
