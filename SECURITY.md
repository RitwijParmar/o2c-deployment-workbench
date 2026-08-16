# Security and financial-control boundaries

This repository is an implementation simulator built entirely from synthetic data. Do not load customer, banking, remittance, or personally identifiable information into the sample files or hosted dashboard.

The agent layer is advisory. It may classify an exception, summarize evidence, or recommend a queue action, but it cannot post cash, issue a refund, approve a write-off, change customer master data, or mutate an ERP. Those actions require a human-controlled downstream process.

To report a vulnerability, use GitHub's private vulnerability-reporting feature for this repository. Do not include real financial data, credentials, or account identifiers in the report.

Before adapting this simulator for a production environment, add authenticated source connectors, secret management, encryption, role-based access, segregation-of-duties controls, immutable audit retention, and organization-specific approval policies.
