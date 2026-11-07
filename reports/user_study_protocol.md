# User Study & Usability Research Protocol: MobiURL-Guard

## 1. Study Objective
The objective of this controlled human-subject study is to evaluate whether providing **calibrated probability estimates, conformal uncertainty sets, and local XAI explanations** assists mobile users in making more accurate and confident security decisions when encountering deceptive URLs compared to binary indicators.

---

## 2. Experimental Design

### A. Study Paradigm
- **Design:** Between-subjects controlled experiment with $N = 100$ participants randomly allocated into 5 treatment arms ($n = 20$ each).
- **Task:** Participants evaluate 20 simulated mobile interaction cards (10 benign, 10 phishing) simulating SMS, WhatsApp, and browser notification prompts.

### B. Treatment Arms
1. **Condition 1 (Control / Binary):** Red/Green badge only ("Safe" vs "Dangerous").
2. **Condition 2 (Uncalibrated Point Score):** Raw uncalibrated percentage score (e.g., standard ML classifier output).
3. **Condition 3 (Calibrated Risk Meter):** Platt-calibrated malicious risk % (0% to 100%) and estimated benign probability.
4. **Condition 4 (Conformal Uncertainty):** Set-valued conformal prediction (`{Legitimate}`, `{Malicious}`, or `{Uncertain / Insufficient Evidence}`).
5. **Condition 5 (MobiURL-Guard Full Framework):** Calibrated risk % + Conformal set + Top-3 Explainable AI directional factors.

---

## 3. Quantitative Evaluation Metrics

1. **User Decision Accuracy:** Percentage of correct click/block decisions across phishing and benign links.
2. **False Positive Adherence:** Rate at which benign links are unnecessarily blocked due to excessive user panic.
3. **Decision Latency:** Measured response time (in seconds) per scenario.
4. **Perceived Confidence:** 5-point Likert scale (1 = "Completely unsure", 5 = "Completely confident").
5. **Cognitive Load:** Measured via the standardized NASA-TLX (Task Load Index) multi-dimensional assessment.
6. **Usability Score:** Measured via the standardized 10-item System Usability Scale (SUS).

---

## 4. Usability Questionnaire (Post-Task SUS Assessment)

| Item # | Standard SUS Statement | Scale (1-5) |
| :--- | :--- | :--- |
| **Q1** | I think that I would like to use this URL protection tool frequently on my smartphone. | Strongly Disagree (1) - Strongly Agree (5) |
| **Q2** | I found the threat assessment interface unnecessarily complex. | Strongly Disagree (1) - Strongly Agree (5) |
| **Q3** | I thought the system was easy to use. | Strongly Disagree (1) - Strongly Agree (5) |
| **Q4** | I think that I would need the assistance of a technical person to be able to understand the risk score. | Strongly Disagree (1) - Strongly Agree (5) |
| **Q5** | I found the explanatory reasons for why a URL is risky well integrated. | Strongly Disagree (1) - Strongly Agree (5) |
| **Q6** | I thought there was too much inconsistency in the risk ratings. | Strongly Disagree (1) - Strongly Agree (5) |
| **Q7** | I would imagine that most smartphone users would learn to interpret this risk score very quickly. | Strongly Disagree (1) - Strongly Agree (5) |
| **Q8** | I found the uncertainty warning ("Unable to determine reliably") helpful when evaluating unfamiliar links. | Strongly Disagree (1) - Strongly Agree (5) |
| **Q9** | I felt very confident using the tool to make browsing decisions. | Strongly Disagree (1) - Strongly Agree (5) |
| **Q10**| I needed to learn a lot of cybersecurity terminology before I could understand the explanations. | Strongly Disagree (1) - Strongly Agree (5) |

---

## 5. Statistical Hypothesis Testing
- **Hypothesis 1 ($H_1$):** Participants in Condition 5 (Full MobiURL-Guard) will demonstrate statistically significant higher decision accuracy than Condition 1 (Binary) via one-way ANOVA and Tukey's HSD ($p < 0.01$).
- **Hypothesis 2 ($H_2$):** Condition 4 and Condition 5 will exhibit significantly lower cognitive load on zero-day/ambiguous tasks due to explicit conformal uncertainty fail-safe indicators ($p < 0.05$).

---

## 6. Ethical Safeguards and IRB Compliance
- **Zero Real Credential Harvesting:** All phishing stimuli execute within isolated sandboxed `.test` domains (RFC 2606) with zero backend credential logging.
- **Informed Consent:** Explicit consent obtained prior to task commencement with full debriefing upon completion.
