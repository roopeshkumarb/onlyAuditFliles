# BRIEF FOR THE AUDITOR (read first)
You are asked to audit BLK-001 (a data-freshness watchdog for live-only market-data recorders), the 03-11-2026 power incident, and the remote-access plan. Read `01_REPORT_BLK001.md`, then check every claim against the numbered files. Answer the 7 questions in section 6 of the report, and for each file say: SUPPORTS / DOES NOT SUPPORT / CANNOT CHECK.
Context: retail NIFTY 50 intraday system; four broker feeds are recorded in parallel on two boxes (i5, i7/"j1800") because live ticks/depth cannot be fetched later. Times are IST (GMT+5:30). Nothing here places orders.
Please do NOT treat absence of data as zero. Mark UNKNOWN.
