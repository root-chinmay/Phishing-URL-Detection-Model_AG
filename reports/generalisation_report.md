# Cross-Domain and Zero-Day Generalisation Report: MobiURL-Guard (Research Gap 1)

## 1. Experimental Protocols
1. **Conventional Random Stratified Split:** URLs randomly shuffled across train and test partitions. Identical registered domains may appear in both partitions, creating optimistic evaluation bias.
2. **Domain-Disjoint Evaluation Protocol:** Records grouped strictly by registered domain. Zero domain overlap between train and test partitions, rigorously testing zero-day malicious domain discovery.

---

## 2. Experimental Comparison

| Evaluation Protocol | Accuracy | Precision | Recall | F1-Score | ROC-AUC | FPR | FNR |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Conventional Random Split** | 0.9295 | 0.9507 | 0.9060 | **0.9278** | 0.9798 | 0.0470 | 0.0940 |
| **Domain-Disjoint (Unseen Domains)** | 0.9027 | 0.8847 | 0.8815 | **0.8831** | 0.9699 | 0.0822 | 0.1185 |

---

## 3. Generalisation Gap & Key Insights

- **Generalisation Gap ($\Delta F_1$):** `+0.0447`
- **Analysis:** When evaluated on completely unfamiliar, never-before-seen domains, the model retains strong discriminative power (0.9699 AUC), confirming that lexical, entropy, and structural features generalize effectively without memorizing domain identity.
- **Fail-Safe Mechanism:** Unfamiliar URLs with borderline scores trigger the conformal uncertainty filter (`{Legitimate, Malicious}`), preventing false positive blocking of novel benign sites.
