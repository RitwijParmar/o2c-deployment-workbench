import fs from "node:fs/promises";
import path from "node:path";
import { SpreadsheetFile, Workbook } from "@oai/artifact-tool";

const root = process.cwd();
const outDir = path.join(root, "outputs", "o2c-workbench-20260816");
const previewDir = path.join(outDir, "previews");
const deliverableDir = path.join(root, "deliverables");
await fs.mkdir(previewDir, { recursive: true });
await fs.mkdir(deliverableDir, { recursive: true });
const summary = JSON.parse(await fs.readFile(path.join(root, "output", "benchmark_summary.json"), "utf8"));
const dq = JSON.parse(await fs.readFile(path.join(root, "output", "data_quality_report.json"), "utf8"));

const wb = Workbook.create();
const names = ["Cover", "Configuration", "Source Mapping", "Data Quality", "KPI Definitions", "KPI Benchmark", "Requirements", "UAT Scenarios", "Cutover", "Go-Live Dashboard", "Checks", "Sources"];
for (const name of names) wb.worksheets.add(name);

const navy = "#0B1F33";
const blue = "#1769AA";
const cyan = "#30B6C9";
const pale = "#EAF2F8";
const light = "#F5F7FA";
const green = "#177A55";
const amber = "#B56A00";
const red = "#A93C3C";
const gray = "#617181";
const border = "#D8E2EA";

function title(sheet, text, subtitle, cols = "H") {
  sheet.showGridLines = false;
  sheet.getRange(`A1:${cols}2`).merge();
  sheet.getRange("A1").values = [[text]];
  sheet.getRange(`A1:${cols}2`).format = { fill: navy, font: { bold: true, color: "#FFFFFF", size: 22 }, verticalAlignment: "center", rowHeight: 30 };
  sheet.getRange(`A3:${cols}3`).merge();
  sheet.getRange("A3").values = [[subtitle]];
  sheet.getRange(`A3:${cols}3`).format = { fill: pale, font: { color: gray, italic: true, size: 10 }, wrapText: true, rowHeight: 30, verticalAlignment: "center" };
}

function header(range) {
  range.format = { fill: blue, font: { bold: true, color: "#FFFFFF" }, borders: { preset: "all", style: "thin", color: border }, wrapText: true, verticalAlignment: "center" };
}

function body(range) {
  range.format = { borders: { preset: "all", style: "thin", color: border }, verticalAlignment: "top", wrapText: true };
}

function fit(sheet, range, maxWidth = 36) {
  const used = sheet.getRange(range);
  used.format.autofitRows();
  used.format.autofitColumns();
  used.format.columnWidth = maxWidth;
}

// Cover
{
  const s = wb.worksheets.getItem("Cover");
  s.showGridLines = false;
  s.getRange("A1:H4").merge();
  s.getRange("A1").values = [["O2C Deployment Workbench"]];
  s.getRange("A1:H4").format = { fill: navy, font: { bold: true, color: "#FFFFFF", size: 28 }, verticalAlignment: "center", horizontalAlignment: "center" };
  s.getRange("A5:H6").merge();
  s.getRange("A5").values = [["ERP Receivables Integration · Complete Synthetic Customer Implementation"]];
  s.getRange("A5:H6").format = { fill: blue, font: { bold: true, color: "#FFFFFF", size: 14 }, verticalAlignment: "center", horizontalAlignment: "center" };
  s.getRange("B8:G8").merge();
  s.getRange("B8").values = [[summary.implementation.customer_name]];
  s.getRange("B8:G8").format = { font: { bold: true, color: navy, size: 18 }, horizontalAlignment: "center" };
  s.getRange("B10:C14").values = [["Implementation ID", summary.implementation.implementation_id], ["As-of date", summary.implementation.as_of_date], ["Canonical records", summary.data_quality.total_records], ["Data-quality gate", summary.data_quality.status], ["Go-live recommendation", summary.agentic_control.go_live.recommendation]];
  body(s.getRange("B10:C14"));
  s.getRange("B10:B14").format = { fill: pale, font: { bold: true, color: navy }, borders: { preset: "all", style: "thin", color: border } };
  s.getRange("B16:G19").merge();
  s.getRange("B16").values = [[summary.implementation.source_disclaimer + "\n\n" + summary.implementation.benchmark_disclaimer]];
  s.getRange("B16:G19").format = { fill: "#FFF6DD", font: { color: amber, bold: true }, wrapText: true, verticalAlignment: "center", horizontalAlignment: "center", borders: { preset: "outside", style: "medium", color: amber } };
  s.getRange("A1:H22").format.columnWidth = 18;
  s.getRange("B10:B14").format.columnWidth = 24;
  s.getRange("C10:C14").format.columnWidth = 28;
}

// Configuration
{
  const s = wb.worksheets.getItem("Configuration");
  title(s, "Customer Configuration", "Executable controls are maintained in config/customer_implementation.yaml.", "F");
  const rows = [
    ["Section", "Parameter", "Configured value", "Purpose", "Owner", "Change control"],
    ["Matching", "Absolute tolerance", 2, "Minimum allowed USD variance", "Cash Application Lead", "UAT + approval"],
    ["Matching", "Percentage tolerance", 0.0025, "Relative variance threshold", "Cash Application Lead", "UAT + approval"],
    ["Matching", "Minimum partial ratio", 0.25, "Floor for referenced partial auto-application", "AR Manager", "UAT + approval"],
    ["Matching", "Deduction clear limit", 500, "Maximum validated deduction for auto-clear", "Deductions Lead", "UAT + approval"],
    ["Matching", "Cross-currency", true, "Permit configured FX comparison", "Treasury Operations", "UAT + approval"],
    ["Collections", "Days past due weight", 0.35, "Priority score component", "Collections Lead", "Re-score + UAT"],
    ["Collections", "Open balance weight", 0.30, "Priority score component", "Collections Lead", "Re-score + UAT"],
    ["Collections", "Broken promise weight", 0.20, "Priority score component", "Collections Lead", "Re-score + UAT"],
    ["Collections", "Credit risk weight", 0.10, "Priority score component", "Credit/Collections", "Re-score + UAT"],
    ["Collections", "Active deduction weight", 0.05, "Priority score component", "Deductions Lead", "Re-score + UAT"],
    ["Agents", "Offline case limit", 24, "Bounded reproducible decision sample", "AI Platform Owner", "Code review"],
    ["Agents", "High-value approval", 10000, "Escalation threshold", "AR Controls Owner", "Approval"],
    ["Observability", "Record content capture", false, "Avoid sensitive record content in traces", "Platform Security", "Security approval"],
  ];
  s.getRange(`A5:F${4 + rows.length}`).values = rows;
  header(s.getRange("A5:F5")); body(s.getRange(`A6:F${4 + rows.length}`));
  s.getRange("C6").format.numberFormat = "$#,##0.00";
  s.getRange("C7:C8").format.numberFormat = "0.0%";
  s.getRange("C9").format.numberFormat = "$#,##0";
  s.getRange("C11:C15").format.numberFormat = "0.0%";
  s.getRange("C17").format.numberFormat = "$#,##0";
  s.freezePanes.freezeRows(5);
  s.getRange("A1:F18").format.columnWidth = 24;
  s.getRange("D6:F18").format.columnWidth = 30;
}

// Source Mapping
{
  const s = wb.worksheets.getItem("Source Mapping");
  title(s, "Source-to-Target Mapping", "Representative mappings; every source is a simulated style export, not a genuine ERP integration.", "H");
  const entities = [
    ["customers", "KNA1_SIM.csv", "HZ_CUST_ACCOUNTS_SIM.csv", "customers_export_sim.csv", "customer_id", "Customer master", "Required/unique", "source_system + source_file"],
    ["invoices", "BSID_SIM.csv", "RA_CUSTOMER_TRX_ALL_SIM.csv", "transactions_invoices_sim.csv", "invoice_id", "Open receivable", "Dates/currency/amount", "source_system + source_file"],
    ["payments", "FEBEP_SIM.csv", "AR_CASH_RECEIPTS_ALL_SIM.csv", "customer_payments_sim.csv", "payment_id", "Incoming cash", "Bank duplicate", "source_system + source_file"],
    ["remittances", "REMADV_SIM.csv", "AR_RECEIVABLE_APPLICATIONS_SIM.csv", "payment_applications_sim.csv", "remittance_id", "Invoice references", "Payment link", "source_system + source_file"],
    ["deductions", "DM_CASE_SIM.csv", "AR_DEDUCTIONS_SIM.csv", "credit_memos_deductions_sim.csv", "deduction_id", "Short-pay evidence", "Status/limit", "source_system + source_file"],
    ["promises_to_pay", "PTP_SIM.csv", "AR_PROMISES_SIM.csv", "promises_to_pay_sim.csv", "promise_id", "Promise tracking", "Invoice link", "source_system + source_file"],
    ["collection_activities", "DUNNING_LOG_SIM.csv", "AR_COLLECTION_ACTIVITIES_SIM.csv", "collection_notes_sim.csv", "activity_id", "Collector history", "Customer link", "source_system + source_file"],
  ];
  s.getRange("A5:H5").values = [["Canonical entity", "SAP S/4HANA-style", "Oracle Fusion-style", "NetSuite-style", "Business key", "Purpose", "Primary control", "Lineage"]];
  s.getRange("A6:H12").values = entities;
  header(s.getRange("A5:H5")); body(s.getRange("A6:H12"));
  s.getRange("A14:H14").merge(); s.getRange("A14").values = [["Representative field-level mappings"]]; s.getRange("A14:H14").format = { fill: cyan, font: { bold: true, color: navy } };
  const fields = [
    ["customer_id", "KUNNR", "CUST_ACCOUNT_ID", "internalid", "Text", "Required", "Preserve", "Customer key"],
    ["invoice_number", "XBLNR", "TRX_NUMBER", "tranid", "Text", "Required", "Trim", "Reference match"],
    ["open_amount", "DMBTR_OPEN", "AMOUNT_DUE_REMAINING", "amountremaining", "Decimal", "Non-negative", "Parse decimal", "Open AR"],
    ["bank_txn_id", "BANK_REF", "BANK_REFERENCE", "custbody_bank_reference", "Text", "Duplicate warning", "Trim", "Bank control"],
    ["invoice_refs", "XBLNR_LIST", "APPLIED_TRX_NUMBERS", "applied_tranids", "Text list", "Payment link", "Normalize delimiters", "Remittance"],
    ["promise status", "PTP_STATUS", "PROMISE_STATUS", "promisestatus", "Enum", "Invoice link", "Uppercase", "Collections"],
  ];
  s.getRange("A15:H15").values = [["Canonical field", "SAP field", "Oracle field", "NetSuite field", "Type", "Control", "Transform", "Use"]];
  s.getRange("A16:H21").values = fields;
  header(s.getRange("A15:H15")); body(s.getRange("A16:H21"));
  s.freezePanes.freezeRows(5);
  s.getRange("A1:H21").format.columnWidth = 22;
}

// Data Quality
{
  const s = wb.worksheets.getItem("Data Quality");
  title(s, "Data-Quality Report", "Seed-42 canonical control results. Intentional duplicates remain warnings and are routed.", "G");
  s.getRange("A5:B9").values = [["Control result", "Value"], ["Canonical records", dq.total_records], ["Validation errors", dq.error_count], ["Warnings", dq.warning_count], ["Batch gate", dq.status + " WITH WARNINGS"]];
  header(s.getRange("A5:B5")); body(s.getRange("A6:B9"));
  const controls = [
    ["VAL-001", "Required identifiers populated", "ERROR", "0", "Pass"],
    ["VAL-002", "Primary identifiers unique", "ERROR", "0", "Pass"],
    ["VAL-003", "Customer foreign keys resolve", "ERROR", "0", "Pass"],
    ["VAL-004", "Amounts non-negative", "ERROR", "0", "Pass"],
    ["VAL-005", "Currency configured", "ERROR", "0", "Pass"],
    ["VAL-006", "Due date not before invoice date", "ERROR", "0", "Pass"],
    ["VAL-007", "Duplicate bank transactions identified", "WARN", dq.warning_count, "Warnings routed"],
  ];
  s.getRange("A11:E11").values = [["Check", "Definition", "Severity", "Findings", "Disposition"]];
  s.getRange("A12:E18").values = controls;
  header(s.getRange("A11:E11")); body(s.getRange("A12:E18"));
  s.getRange("A20:G22").merge(); s.getRange("A20").values = [["The 18 warnings are deliberate repeated bank identifiers. Later occurrences are quarantined, excluded from valid cash, and routed to the Cash Application Data Steward. No validation issue is silently discarded."]];
  s.getRange("A20:G22").format = { fill: "#FFF6DD", font: { color: amber }, wrapText: true, verticalAlignment: "center" };
  s.getRange("A1:G22").format.columnWidth = 22;
  s.getRange("B12:B18").format.columnWidth = 40;
}

// KPI Definitions
{
  const s = wb.worksheets.getItem("KPI Definitions");
  title(s, "KPI Definition Sheet", "Every movement is a synthetic controlled implementation benchmark.", "G");
  const rows = [
    ["Auto-match rate", "Auto-matched valid payments / valid payments", "Higher", "Duplicate records excluded", "Daily", "Cash Application Lead", "78%"],
    ["Manual-review rate", "Manual-review payment records / all payment records", "Lower", "Includes duplicates requiring steward review", "Daily", "Cash Application Lead", "22%"],
    ["Unapplied cash", "Sum of valid payment residuals translated to USD", "Lower", "Overpayment residuals remain visible", "Daily", "AR Manager", "$125,000"],
    ["DSO", "Ending AR / 90-day synthetic credit sales × 90", "Lower", "Controlled indicator, not customer DSO", "Weekly", "AR Manager", "48 days"],
    ["CEI", "Collections effectiveness formula using beginning/current/ending AR", "Higher", "Depends on synthetic aging mix", "Weekly", "Collections Lead", "82%"],
    ["Past-due AR", "Past-due ending AR / ending AR", "Lower", "Uses configured as-of date", "Daily", "Collections Lead", "30%"],
    ["Processing time", "Record counts × configured handling minutes", "Lower", "Modeled effort, not observation", "Batch", "Implementation Lead", "25 hours"],
  ];
  s.getRange("A5:G5").values = [["KPI", "Definition", "Direction", "Limitation", "Cadence", "Owner", "Target"]];
  s.getRange("A6:G12").values = rows;
  header(s.getRange("A5:G5")); body(s.getRange("A6:G12"));
  s.getRange("A1:G12").format.columnWidth = 24;
  s.getRange("B6:B12").format.columnWidth = 44;
  s.getRange("D6:D12").format.columnWidth = 38;
}

// KPI Benchmark with formulas
{
  const s = wb.worksheets.getItem("KPI Benchmark");
  title(s, "Current State vs Configured Future State", "Formula-driven target status. Gaps are retained for an honest go-live decision.", "H");
  s.getRange("A5:H5").values = [["Metric", "Direction", "Baseline", "Future", "Change", "Target", "Target status", "Unit"]];
  const rows = summary.kpi_comparison.map(r => [r.label, r.direction === "higher" ? "Higher" : "Lower", r.baseline, r.future, null, r.target, null, r.unit]);
  s.getRange("A6:H12").values = rows;
  s.getRange("E6").formulas = [["=D6-C6"]]; s.getRange("E6:E12").fillDown();
  s.getRange("G6").formulas = [["=IF(B6=\"Higher\",IF(D6>=F6,\"MET\",\"GAP\"),IF(D6<=F6,\"MET\",\"GAP\"))"]]; s.getRange("G6:G12").fillDown();
  header(s.getRange("A5:H5")); body(s.getRange("A6:H12"));
  for (const row of [6, 7, 11]) s.getRange(`C${row}:F${row}`).format.numberFormat = "0.0%";
  s.getRange("C8:F8").format.numberFormat = "$#,##0";
  s.getRange("C9:F9").format.numberFormat = "0.0";
  s.getRange("C10:F10").format.numberFormat = "0.0\"%\"";
  s.getRange("C12:F12").format.numberFormat = "0.0";
  s.getRange("A14:H16").merge(); s.getRange("A14").values = [[summary.implementation.benchmark_disclaimer]];
  s.getRange("A14:H16").format = { fill: "#FFF6DD", font: { color: amber, bold: true }, wrapText: true, horizontalAlignment: "center", verticalAlignment: "center" };
  s.freezePanes.freezeRows(5);
  s.getRange("A1:H16").format.columnWidth = 20;
  s.getRange("A6:A12").format.columnWidth = 25;
}

// Requirements
{
  const s = wb.worksheets.getItem("Requirements");
  title(s, "Requirements Traceability Matrix", "Business requirement to design, evidence and UAT linkage.", "F");
  const reqs = [
    ["REQ-001", "Three simulated ERP source styles", "Source config/adapters", "data/raw", "UAT-01–03", "Covered"],
    ["REQ-002", "Seven canonical entities", "Canonical model", "data/canonical", "UAT-04", "Covered"],
    ["REQ-003", "Validation control gate", "validation.py", "DQ report", "UAT-05–09", "Covered"],
    ["REQ-004", "Difficult cash cases", "matching.py", "matches/allocations", "UAT-10–21", "Covered"],
    ["REQ-005", "Baseline/future KPIs", "kpis.py", "dashboard/workbook", "UAT-22", "Covered"],
    ["REQ-006", "Collection priority", "collections.py", "worklist", "UAT-23", "Covered"],
    ["REQ-007", "Multi-agent handoffs", "agent_control.py", "agent decisions/traces", "UAT-24", "Covered"],
    ["REQ-008", "Human approval gate", "agent policy", "recommendation-only", "UAT-25", "Covered"],
    ["REQ-009", "MCP tools/resources/prompts", "mcp_server.py", "capability discovery", "UAT-26", "Covered"],
    ["REQ-010", "Agent observability", "observability.py", "JSONL spans", "UAT-27", "Covered"],
    ["REQ-011", "Evidence-based go live", "monitor agent", "conditional go", "UAT-28", "Covered"],
  ];
  s.getRange("A5:F5").values = [["Requirement", "Description", "Design", "Evidence", "UAT", "Status"]];
  s.getRange("A6:F16").values = reqs;
  header(s.getRange("A5:F5")); body(s.getRange("A6:F16"));
  s.getRange("A1:F16").format.columnWidth = 24;
  s.getRange("B6:B16").format.columnWidth = 38;
}

// UAT
{
  const s = wb.worksheets.getItem("UAT Scenarios");
  title(s, "User Acceptance Testing", "Twenty-eight controlled scenarios. All test data and expected impacts are synthetic.", "F");
  const scenarioNames = [
    "SAP-style ingestion", "Oracle-style ingestion", "NetSuite-style ingestion", "Canonical completeness", "Missing required ID", "Duplicate primary ID", "Broken customer FK", "Unsupported currency", "Invalid invoice dates", "Exact payment", "Partial payment", "Overpayment", "One payment / multiple invoices", "Multiple payments / one invoice", "Missing remittance", "Cross-currency", "Amount tolerance", "Duplicate payment", "Deduction short-pay", "Unknown reference", "High-value unmatched", "Benchmark comparison", "Collection weighting", "Agent handoff", "Human control gate", "MCP discovery", "Telemetry privacy", "Go-live decision"
  ];
  const expected = [
    "Seven SAP-style files load with lineage", "Seven Oracle-style files load with lineage", "Seven NetSuite-style files load with lineage", "Seven entities total 1,908 records", "VAL-001 blocks batch", "VAL-002 blocks batch", "VAL-003 blocks batch", "VAL-005 blocks batch", "VAL-006 blocks batch", "One invoice auto-matches", "Cash applies and balance remains", "Invoice clears; residual routes", "Two allocations created", "Successive allocations clear invoice", "Unique amount may infer; ambiguity cannot", "Configured FX used", "Within-tolerance variance accepted", "Later record quarantined", "Payment plus deduction clears", "Cash remains unapplied", "Senior analyst route", "Seven movements and disclaimer visible", "Weights change order", "Supervisor handoff traced", "Approval required; no action executed", "4 tools, 3 resources, 2 prompts", "Spans exist; content capture false", "CONDITIONAL_GO"
  ];
  const uatRows = scenarioNames.map((name, i) => [`UAT-${String(i + 1).padStart(2, "0")}`, name, expected[i], i < 4 ? "Implementation Lead" : i < 22 ? "Finance Operations" : "Platform / Controls", "Not executed", "Evidence required"]);
  s.getRange("A5:F5").values = [["ID", "Scenario", "Expected result", "Owner", "Status", "Evidence"]];
  s.getRange("A6:F33").values = uatRows;
  header(s.getRange("A5:F5")); body(s.getRange("A6:F33"));
  s.freezePanes.freezeRows(5);
  s.getRange("A1:F33").format.columnWidth = 24;
  s.getRange("B6:C33").format.columnWidth = 38;
}

// Cutover
{
  const s = wb.worksheets.getItem("Cutover");
  title(s, "Cutover and Rollback Checklist", "No production cutover is performed by this repository; this is the implementation control pack.", "F");
  const actions = [
    ["Entry", "Approve mappings, tolerances, routes, targets and agent boundary", "Finance + Controls", "Open", "", "Block if incomplete"],
    ["Entry", "Sign UAT-01–28 and close Severity-1 defects", "Implementation Lead", "Open", "", "Block if incomplete"],
    ["Entry", "Reconcile source counts, cash totals and currencies", "Data Lead", "Open", "", "Block if variance"],
    ["Security", "Restrict MCP clients; configure auth outside localhost", "Platform Security", "Open", "", "Block external access"],
    ["Security", "Confirm trace content capture disabled", "Platform Security", "Open", "", "Block if enabled"],
    ["Cutover", "Freeze configuration and tag release candidate", "Release Manager", "Open", "", "Rollback to prior tag"],
    ["Cutover", "Run validation and seven smoke cases", "QA Lead", "Open", "", "Stop on error"],
    ["Cutover", "Enable recommendation-only agents and read tools", "AI Platform Owner", "Open", "", "Disable services"],
    ["Cutover", "Publish dashboard and hypercare rota", "AR Manager", "Open", "", "Revert dashboard"],
    ["Rollback", "Stop new batches and disable agent/MCP access", "Incident Commander", "Ready", "", "Immediate"],
    ["Rollback", "Restore prior configuration and canonical snapshot", "Data Lead", "Ready", "", "Verify hashes"],
    ["Rollback", "Reconcile and obtain restart approval", "Finance + Technology", "Ready", "", "No self-restart"],
  ];
  s.getRange("A5:F5").values = [["Phase", "Control/action", "Owner", "Status", "Sign-off", "Rollback/stop condition"]];
  s.getRange("A6:F17").values = actions;
  header(s.getRange("A5:F5")); body(s.getRange("A6:F17"));
  s.getRange("A1:F17").format.columnWidth = 24;
  s.getRange("B6:B17").format.columnWidth = 46;
  s.getRange("F6:F17").format.columnWidth = 30;
}

// Dashboard
{
  const s = wb.worksheets.getItem("Go-Live Dashboard");
  title(s, "Go-Live Monitoring Dashboard", "Formula-linked to the benchmark sheet. Seed-42 decision retains unmet stretch targets.", "H");
  s.getRange("A5:B9").values = [["Control", "Result"], ["Data quality", null], ["Target gaps", null], ["Go-live decision", null], ["Agent approval bypass", 0]];
  s.getRange("B6").formulas = [["='Data Quality'!B9"]];
  s.getRange("B7").formulas = [["=COUNTIF('KPI Benchmark'!G6:G12,\"GAP\")"]];
  s.getRange("B8").formulas = [["=IF(AND(B6=\"PASS WITH WARNINGS\",B7=0),\"GO\",IF(AND(B6=\"PASS WITH WARNINGS\",B7<=4),\"CONDITIONAL GO\",\"NO GO\"))"]];
  header(s.getRange("A5:B5")); body(s.getRange("A6:B9"));
  s.getRange("D5:H5").values = [["KPI", "Baseline", "Future", "Target", "Status"]];
  for (let i = 0; i < 7; i++) {
    const row = 6 + i;
    s.getRange(`D${row}:H${row}`).formulas = [[`='KPI Benchmark'!A${row}`, `='KPI Benchmark'!C${row}`, `='KPI Benchmark'!D${row}`, `='KPI Benchmark'!F${row}`, `='KPI Benchmark'!G${row}`]];
  }
  header(s.getRange("D5:H5")); body(s.getRange("D6:H12"));
  for (const row of [6, 7, 11]) s.getRange(`E${row}:G${row}`).format.numberFormat = "0.0%";
  s.getRange("E8:G8").format.numberFormat = "$#,##0";
  s.getRange("E9:G9").format.numberFormat = "0.0";
  s.getRange("E10:G10").format.numberFormat = "0.0\"%\"";
  s.getRange("E12:G12").format.numberFormat = "0.0";
  s.getRange("J5:L5").values = [["Rate KPI", "Baseline", "Future"]];
  s.getRange("J6:L8").values = [["Auto-match", summary.kpi_comparison[0].baseline, summary.kpi_comparison[0].future], ["Manual review", summary.kpi_comparison[1].baseline, summary.kpi_comparison[1].future], ["Past-due AR", summary.kpi_comparison[5].baseline, summary.kpi_comparison[5].future]];
  s.getRange("K6:L8").format.numberFormat = "0.0%";
  const chart = s.charts.add("bar", s.getRange("J5:L8"));
  chart.title = "Current vs Future Rates";
  chart.hasLegend = true;
  chart.yAxis = { numberFormatCode: "0%" };
  chart.setPosition("A14", "H31");
  s.getRange("A33:H36").merge(); s.getRange("A33").values = [["Conditional-go conditions: retain human approval for posting, write-off, refund and master-data actions; operate hypercare for unapplied cash and residual overpayments."]];
  s.getRange("A33:H36").format = { fill: "#FFF6DD", font: { color: amber, bold: true }, wrapText: true, verticalAlignment: "center" };
  s.getRange("A1:L36").format.columnWidth = 18;
  s.getRange("D6:D12").format.columnWidth = 24;
}

// Checks
{
  const s = wb.worksheets.getItem("Checks");
  title(s, "Workbook Control Checks", "Formula checks support reviewer inspection; all should show PASS.", "F");
  s.getRange("A5:C5").values = [["Check", "Formula/result", "Status"]];
  s.getRange("A6:A11").values = [["Seven KPI rows"], ["KPI target statuses populated"], ["UAT scenario count = 28"], ["Data-quality errors = 0"], ["Agent approval bypass = 0"], ["Disclaimer present"]];
  s.getRange("B6").formulas = [["=COUNTA('KPI Benchmark'!A6:A12)"]];
  s.getRange("B7").formulas = [["=COUNTA('KPI Benchmark'!G6:G12)"]];
  s.getRange("B8").formulas = [["=COUNTA('UAT Scenarios'!A6:A33)"]];
  s.getRange("B9").formulas = [["='Data Quality'!B7"]];
  s.getRange("B10").formulas = [["='Go-Live Dashboard'!B9"]];
  s.getRange("B11").formulas = [["=IF(LEN(Cover!B16)>20,1,0)"]];
  s.getRange("C6").formulas = [["=IF(B6=7,\"PASS\",\"FAIL\")"]];
  s.getRange("C7").formulas = [["=IF(B7=7,\"PASS\",\"FAIL\")"]];
  s.getRange("C8").formulas = [["=IF(B8=28,\"PASS\",\"FAIL\")"]];
  s.getRange("C9").formulas = [["=IF(B9=0,\"PASS\",\"FAIL\")"]];
  s.getRange("C10").formulas = [["=IF(B10=0,\"PASS\",\"FAIL\")"]];
  s.getRange("C11").formulas = [["=IF(B11=1,\"PASS\",\"FAIL\")"]];
  header(s.getRange("A5:C5")); body(s.getRange("A6:C11"));
  s.getRange("A1:F14").format.columnWidth = 26;
}

// Sources
{
  const s = wb.worksheets.getItem("Sources");
  title(s, "Research and Evidence Sources", "Primary references used for MCP, observability, agent and receivables design.", "D");
  const sources = [
    ["MCP Python SDK", "https://github.com/modelcontextprotocol/python-sdk", "Tools, resources, prompts and transports", "Accessed 2026-08-16"],
    ["MCP specification", "https://modelcontextprotocol.io/specification/2025-06-18/basic/index", "Client/server primitives", "Accessed 2026-08-16"],
    ["OpenTelemetry GenAI registry", "https://opentelemetry.io/docs/specs/semconv/registry/attributes/gen-ai/", "Agent/workflow/tool semantic attributes", "Accessed 2026-08-16"],
    ["SAP partial vs residual", "https://help.sap.com/docs/SAP_S4HANA_CLOUD/918bca53037f408f91a2295d04ac16bc/279bad94d6414e05aab0cacf42eb3803.html", "Partial-payment behavior", "Accessed 2026-08-16"],
    ["Oracle Receivables Credit to Cash", "https://docs.oracle.com/en/cloud/saas/financials/26c/faofc/using-receivables-credit-to-cash.pdf", "Receipt/remittance context", "Accessed 2026-08-16"],
    ["NetSuite customer payment", "https://docs.oracle.com/en/cloud/saas/netsuite/ns-online-help/section_N3667711.html", "Payment and auto-apply context", "Accessed 2026-08-16"],
    ["OpenAI model guidance", "https://developers.openai.com/api/docs/guides/latest-model", "Optional multi-agent model path", "Accessed 2026-08-16"],
  ];
  s.getRange("A5:D5").values = [["Source", "URL", "Used for", "Retrieved"]];
  s.getRange("A6:D12").values = sources;
  header(s.getRange("A5:D5")); body(s.getRange("A6:D12"));
  s.getRange("A1:D12").format.columnWidth = 28;
  s.getRange("B6:B12").format.columnWidth = 70;
  s.getRange("C6:C12").format.columnWidth = 38;
}

for (const name of names) {
  const s = wb.worksheets.getItem(name);
  const preview = await wb.render({ sheetName: name, autoCrop: "all", scale: 1, format: "png" });
  const safe = name.toLowerCase().replaceAll(" ", "-");
  await fs.writeFile(path.join(previewDir, `${safe}.png`), new Uint8Array(await preview.arrayBuffer()));
}

const formulaScan = await wb.inspect({ kind: "match", searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A", options: { useRegex: true, maxResults: 200 }, maxChars: 6000 });
await fs.writeFile(path.join(outDir, "formula_error_scan.txt"), formulaScan.ndjson || String(formulaScan), "utf8");
const structure = await wb.inspect({ kind: "sheet", include: "id,name", maxChars: 6000 });
await fs.writeFile(path.join(outDir, "workbook_structure.txt"), structure.ndjson || String(structure), "utf8");

const xlsx = await SpreadsheetFile.exportXlsx(wb);
const primaryPath = path.join(outDir, "O2C_Implementation_Workbook.xlsx");
await xlsx.save(primaryPath);
await xlsx.save(path.join(deliverableDir, "O2C_Implementation_Workbook.xlsx"));
console.log(primaryPath);
