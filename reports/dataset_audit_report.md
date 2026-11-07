# Dataset Audit Report: MobiURL-Guard

## 1. Executive Summary

| Attribute | Value |
| :--- | :--- |
| **Dataset Source** | `data\raw\dataset.csv` |
| **Total Records** | **116,600** |
| **Total Features / Columns** | **26** |
| **URL Column** | `url` |
| **Label Column** | `label` |
| **Total Missing Cells** | **14** |
| **Raw Duplicate URLs** | **1,369** (1.17%) |
| **Canonical URL Duplicates** | **2,317** (1.99%) |

---

## 2. Class Distribution and Label Representation

The dataset contains the following class distributions:

| Class Label | Count | Percentage | Assigned Meaning |
| :--- | :--- | :--- | :--- |
| `0` | 100,000 | 85.76% | Benign / Safe (0) |
| `1` | 16,600 | 14.24% | Malicious / Phishing (1) |

- **Balance Assessment:** Imbalanced.
- **Target Encoding:** Binary classification where `0` = Benign, `1` = Malicious URL.

---

## 3. URL Scheme Distribution

| Scheme | Count | Percentage |
| :--- | :--- | :--- |
| `https` | 50,271 | 43.11% |
| `http` | 66,329 | 56.89% |

---

## 4. Metadata and Context Availability

- **Timestamps Available:** `False` (No temporal sequence is embedded; temporal split requires synthetic drift partition or external validation).
- **DNS / WHOIS Records:** `False` (No external DNS/WHOIS records exist in raw dataset; offline detection is preserved).
- **HTML / DOM Payloads:** `False` (Content inspection not present; lexical, structural, entropy, and brand analysis form the core feature engine).
- **Message / SMS Context:** `False` (Message text is absent in base URL table; modular message context scoring engine implemented as an optional multimodal pipeline).

---

## 5. Feature Schema and Leakage Analysis

### Columns Present in Dataset
- `url` (missing: 0)
- `url_len` (missing: 0)
- `dom` (missing: 0)
- `dom_len` (missing: 0)
- `is_ip` (missing: 0)
- `tld` (missing: 14)
- `tld_len` (missing: 0)
- `subdom_cnt` (missing: 0)
- `letter_cnt` (missing: 0)
- `digit_cnt` (missing: 0)
- `special_cnt` (missing: 0)
- `eq_cnt` (missing: 0)
- `qm_cnt` (missing: 0)
- `amp_cnt` (missing: 0)
- `dot_cnt` (missing: 0)
- `dash_cnt` (missing: 0)
- `under_cnt` (missing: 0)
- `letter_ratio` (missing: 0)
- `digit_ratio` (missing: 0)
- `spec_ratio` (missing: 0)
- `is_https` (missing: 0)
- `slash_cnt` (missing: 0)
- `entropy` (missing: 0)
- `path_len` (missing: 0)
- `query_len` (missing: 0)
- `label` (missing: 0)

### Data Leakage Evaluation
- **Potential Leakage Columns Identified:** `None`
- The dataset features consist of pre-extracted lexical and structural properties (`url_len`, `dom_len`, `is_ip`, `tld_len`, `subdom_cnt`, `letter_cnt`, `digit_cnt`, `special_cnt`, `eq_cnt`, `qm_cnt`, `amp_cnt`, `dot_cnt`, `dash_cnt`, `under_cnt`, `letter_ratio`, `digit_ratio`, `spec_ratio`, `is_https`, `slash_cnt`, `entropy`, `path_len`, `query_len`).
- **Research Safeguard:** For the research pipeline and production mobile app, MobiURL-Guard extracts features directly from raw input URLs using an independent, rigorous feature extraction engine (`src/features/`), guaranteeing zero leakage and complete compatibility with unseen URLs and zero-day threats.

---

## 6. Preprocessing and Deduplication Protocol

1. **Missing Value Handling:** Impute or drop any corrupted records.
2. **Canonical Deduplication:** Remove exact canonical duplicates before cross-validation to prevent optimistic evaluation bias.
3. **Domain Disjoint Grouping:** Group URLs by registered domain (`dom`) to enable cross-domain zero-day evaluation protocols without domain leakage across train and test sets.
