# AI-NTDRS Phase 2 Research Findings

**Project:** AI Network Threat Detection & Response System (AI-NTDRS)  
**Phase:** Research and technology selection  
**Status:** Provisional findings to guide implementation  
**Note:** This document records the research basis for dataset and model decisions. Final benchmarking results will be produced during implementation and evaluation.

---

## 1. Research Goal

The aim of this research phase is to identify a realistic, flow-based, academically defensible approach for detecting suspicious network behavior in an authorized educational network environment. The selected approach must balance:

- Detection quality.
- Explainability.
- Computational cost.
- Ease of deployment.
- Suitability for a final-year Computer Science project.

---

## 2. Key Findings

1. Flow-based datasets are the best fit for AI-NTDRS because the target system prioritizes privacy-preserving network metadata over packet payload inspection.
2. Classical machine-learning models remain the strongest first choice for this project because they are easier to explain, easier to evaluate, and easier to deploy than more complex deep-learning models.
3. CICIDS2017, UNSW-NB15, Bot-IoT, and TON_IoT are the strongest candidate datasets for the project because they are publicly available, security-focused, and widely used in research.
4. Isolation Forest is a strong baseline for anomaly detection in unlabeled or partially labeled flow data.
5. Random Forest and Gradient Boosting are strong candidates for supervised classification because they support interpretable feature importance and practical performance on tabular data.
6. SHAP or model-specific feature importance should be used for explanation, but the explanation layer must remain grounded in actual model inputs and outputs.

---

## 3. Dataset Survey

### 3.1 CICIDS2017

**Source:** Canadian Institute for Cybersecurity, University of New Brunswick  
**Type:** Labeled network-flow dataset derived from real packet captures  
**Why it is relevant:** It contains modern attacks and benign background traffic generated in a realistic testbed.

**Research observations:**
- The dataset includes more than 80 extracted flow features.
- It covers benign traffic and attacks such as brute force FTP, brute force SSH, DoS, DDoS, Heartbleed, web attacks, infiltration, botnet activity, and port scanning.
- The dataset is labeled and flow-oriented, which fits the proposed ingestion and preprocessing pipeline.
- It is well documented and widely cited.

**Strengths:**
- Good attack diversity.
- Strong academic recognition.
- Flow features align closely with the AI-NTDRS design.
- Suitable for supervised classification and benchmarking.

**Limitations:**
- Requires careful cleaning and class-balancing analysis.
- Some records and feature values may need preprocessing due to infinities, missing values, or label cleanup.
- It is a research dataset, not a perfect mirror of a live campus network.

### 3.2 UNSW-NB15

**Source:** UNSW Canberra cyber range research dataset  
**Type:** Labeled hybrid network dataset  
**Why it is relevant:** It is a recognized intrusion-detection benchmark with modern attack types and tabular flow features.

**Research observations:**
- The source page reports 2,540,044 total records.
- It contains 49 features.
- It includes nine attack families: Fuzzers, Analysis, Backdoors, DoS, Exploits, Generic, Reconnaissance, Shellcode, and Worms.
- The published split includes 175,341 training records and 82,332 testing records.

**Strengths:**
- Large enough for meaningful supervised benchmarking.
- Well documented and widely used.
- Balanced enough for model comparison experiments.
- Suitable for feature-importance and classification analysis.

**Limitations:**
- Some attack categories are broad and may require careful interpretation.
- The feature set is smaller than CICIDS2017 in terms of network-flow diversity.
- Real-world transferability still needs to be validated.

### 3.3 Bot-IoT

**Source:** UNSW Canberra cyber range dataset  
**Type:** Large-scale IoT/botnet dataset  
**Why it is relevant:** It is useful for stress-testing detection logic under high-volume attack traffic.

**Research observations:**
- The source page reports more than 72,000,000 records in the raw packet capture environment.
- The extracted CSV flow data is approximately 16.7 GB.
- A reduced 5% subset is also provided and contains about 3 million records.
- Attack types include DDoS, DoS, OS and service scan, keylogging, and data exfiltration.

**Strengths:**
- Excellent for high-volume anomaly and botnet behavior analysis.
- Provides a demanding benchmark for scalability.
- Good for showing how risk scoring handles bursty malicious traffic.

**Limitations:**
- Very large and computationally heavier than the other candidates.
- IoT-centric behavior is not identical to a university campus environment.
- May be better used as a secondary benchmark rather than the only dataset.

### 3.4 TON_IoT

**Source:** UNSW Canberra and related research outputs  
**Type:** Heterogeneous IoT, IIoT, Windows, Linux, and network telemetry dataset  
**Why it is relevant:** It supports a broader telemetry-driven security story and aligns with mixed-source monitoring.

**Research observations:**
- The project page describes raw datasets for IoT/IIoT sensors, network traffic, Linux telemetry, and Windows telemetry.
- Processed CSV datasets and train/test subsets are provided.
- Security events are grounded by timestamps and tagged IP addresses.
- The dataset is designed for evaluating AI-based security applications, including intrusion detection and threat intelligence.

**Strengths:**
- Rich multi-source telemetry.
- Suitable for demonstrating extensibility beyond pure flow data.
- Good fit for future work involving endpoint or hybrid monitoring.

**Limitations:**
- It is a family of datasets rather than a single simple table.
- Exact sub-dataset selection must be handled carefully.
- Requires more preprocessing coordination if used as the main benchmark.

### 3.5 NSL-KDD

**Source:** Legacy IDS benchmark  
**Type:** Classic labeled network intrusion dataset  
**Why it matters:** It is still useful as a historical baseline, but it is not the strongest primary choice for AI-NTDRS.

**Research observations:**
- It is older and less representative of current traffic patterns.
- It is useful for comparison in academic discussion but weaker as the main dataset.

**Strengths:**
- Commonly cited historical baseline.
- Simple to reference in literature review sections.

**Limitations:**
- Outdated compared with modern traffic and attack behavior.
- Less suitable as the main academic evaluation dataset for this project.

---

## 4. Provisional Dataset Strategy

### Recommended Primary Dataset

**CICIDS2017** is the best initial primary dataset for AI-NTDRS because it combines:

- Flow-based features.
- Modern attack categories.
- Realistic benign background traffic.
- Strong academic recognition.
- Good alignment with the project's educational-network use case.

### Recommended Secondary Benchmarks

- **UNSW-NB15** for broader supervised model comparison.
- **Bot-IoT** for high-volume attack and botnet-style stress testing.
- **TON_IoT** for heterogeneous telemetry and future extensibility.

### Practical Selection Logic

1. Use CICIDS2017 for the main evaluation narrative.
2. Compare the model against UNSW-NB15 where time permits.
3. Use Bot-IoT or TON_IoT for robustness and generalization discussion.
4. Keep NSL-KDD as a literature baseline only.

This gives the project both academic credibility and manageable implementation scope.

---

## 5. Algorithm Survey

### 5.1 Isolation Forest

**Role:** Primary anomaly detection baseline  
**Why it fits:**
- Works well on tabular flow data.
- Does not require labels.
- Efficient enough for an academic prototype.
- Easier to explain than deep anomaly detectors.

**Trade-off:**
- May not capture highly complex nonlinear behavior as well as advanced deep models.
- Still a strong baseline when explainability and deployment simplicity matter.

### 5.2 Random Forest

**Role:** Supervised classification baseline  
**Why it fits:**
- Robust on tabular cybersecurity features.
- Supports feature importance.
- Strong performance without heavy tuning.
- More interpretable than many alternatives.

**Trade-off:**
- Larger models may be less compact than linear methods.
- Feature importance is useful but not a complete explanation.

### 5.3 Gradient Boosting

**Role:** Candidate supervised classifier  
**Why it fits:**
- Often strong performance on structured data.
- Good for class-imbalanced and complex tabular patterns.
- Can outperform simpler baselines when tuned carefully.

**Trade-off:**
- More tuning effort than Random Forest.
- Some variants are less transparent to non-technical stakeholders.

### 5.4 One-Class SVM

**Role:** Possible anomaly baseline  
**Why it fits:**
- Useful in some one-class anomaly settings.

**Trade-off:**
- Can become expensive on larger datasets.
- Less practical for this project than Isolation Forest.

### 5.5 Autoencoder

**Role:** Advanced anomaly-detection option  
**Why it fits:**
- Can model reconstruction error for unusual behavior.

**Trade-off:**
- Harder to explain.
- More complex to train and validate.
- Not the best first choice for a final-year project unless implementation time is generous.

---

## 6. Selected Modeling Direction

### Recommended Baseline Design

- **Anomaly detection:** Isolation Forest.
- **Supervised classification:** Random Forest, with Gradient Boosting as a comparison candidate.
- **Explainability:** Feature importance plus SHAP where practical.

### Why this direction is appropriate

- It is technically credible.
- It matches the tabular nature of network-flow data.
- It is easier to defend academically than a black-box deep model.
- It supports both unlabeled anomaly detection and labeled classification.
- It can run in a manageable local or Docker-based environment.

---

## 7. Explainability Strategy

The system should never output a risk score without a reason.

### Recommended explanation layers

1. Global feature importance for overall model understanding.
2. Local explanation for each alert or device investigation.
3. Human-readable summary tied to observed inputs.

### Preferred techniques

- Tree-based feature importance.
- SHAP for local contribution analysis where feasible.
- Rule-based summary templates for the dashboard.

### Explanation rules

- Use actual model features only.
- Never invent causes that are not supported by the input data.
- Distinguish between observations, model inference, and recommended action.

---

## 8. Academic Justification

This research direction is appropriate for a final-year Computer Science project because it demonstrates:

- Network security concepts.
- Flow-based traffic analysis.
- Classical machine learning.
- Explainable AI.
- Risk prioritization.
- Human-in-the-loop response workflows.
- Secure software architecture.

It avoids unnecessary complexity while still producing a serious cybersecurity platform.

---

## 9. Recommended Next Implementation Inputs

Before coding begins, the project should define:

1. Final dataset choice and preprocessing rules.
2. Feature list for the first ML pipeline.
3. Initial risk-score weights and severity thresholds.
4. Database schema entities and relationships.
5. Authentication roles and permission matrix.
6. API contract for flow ingestion, alerts, devices, and reports.
7. Frontend information architecture for the SOC dashboard.

---

## 10. Conclusion

The research phase supports a practical and defensible design choice: use flow-based network datasets, classical tree-based ML models, and explainability methods that make security alerts understandable. CICIDS2017 should be the primary starting point, with UNSW-NB15, Bot-IoT, and TON_IoT used as secondary evaluation datasets or comparison sources. This gives AI-NTDRS a solid academic foundation without overcomplicating the implementation.
