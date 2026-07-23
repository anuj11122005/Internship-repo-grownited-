import os
import sqlite3
import pandas as pd
import re

def run_full_qa():
    print("Starting Comprehensive Final QA Check...\n")
    
    report_lines = []
    report_lines.append("="*50)
    report_lines.append("FINAL COMPREHENSIVE QA REPORT")
    report_lines.append("="*50 + "\n")
    
    total_checks = 0
    passes = 0
    warnings = 0
    fails = 0
    
    def log_result(status, msg, fix=None):
        nonlocal total_checks, passes, warnings, fails
        total_checks += 1
        if status == "PASS": passes += 1
        elif status == "WARNING": warnings += 1
        elif status == "FAIL": fails += 1
        
        line = f"[{status}] {msg}"
        if fix and status == "FAIL":
            line += f"\n    -> FIX NEEDED: {fix}"
        print(line)
        report_lines.append(line)

    # --- Phase 1: Database ---
    print("--- Phase 1: Database ---")
    report_lines.append("\n--- Phase 1: Database ---")
    db_path = 'data/olist_clean.db'
    if not os.path.exists(db_path):
        log_result("FAIL", "Database file not found.", "Run scripts/08_load_to_mysql.py")
    else:
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        
        # Check tables and row counts
        tables = ['customers', 'orders', 'order_items', 'products', 'sellers', 'payments', 'reviews']
        missing_tables = []
        for table in tables:
            c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,))
            if not c.fetchone():
                missing_tables.append(table)
        
        if missing_tables:
            log_result("FAIL", f"Missing tables in DB: {missing_tables}", "Fix scripts/07_mysql_schema.sql")
        else:
            log_result("PASS", "All 7 tables exist in the database.")
            
            # Row counts vs CSV
            mismatches = []
            for table in tables:
                csv_path = f'data/clean/{table}_clean.csv' if table != 'order_items' else 'data/clean/items_clean.csv'
                if os.path.exists(csv_path):
                    csv_count = len(pd.read_csv(csv_path))
                    c.execute(f"SELECT COUNT(*) FROM {table}")
                    db_count = c.fetchone()[0]
                    if csv_count != db_count:
                        mismatches.append(f"{table} (CSV: {csv_count}, DB: {db_count})")
            
            if mismatches:
                log_result("WARNING", f"Row count mismatches: {mismatches} (Allowed if dupes were dropped during PK constraints)")
            else:
                log_result("PASS", "Database row counts match CSVs perfectly.")
                
            # Foreign Keys
            fks_found = False
            for table in tables:
                c.execute(f"PRAGMA foreign_key_list({table})")
                if c.fetchall():
                    fks_found = True
                    break
            
            if fks_found:
                log_result("PASS", "Foreign key constraints are defined in the schema.")
            else:
                log_result("FAIL", "No foreign key constraints found.", "Add FK constraints to scripts/07_mysql_schema.sql")
                
        conn.close()
        
    # ER Diagram
    if os.path.exists('outputs/er_diagram.png'):
        log_result("PASS", "outputs/er_diagram.png exists.")
    else:
        log_result("WARNING", "outputs/er_diagram.png is missing.", "Run ER diagram script")

    # --- Phase 2: SQL Analytics ---
    print("\n--- Phase 2: SQL Analytics ---")
    report_lines.append("\n--- Phase 2: SQL Analytics ---")
    sql_script = 'scripts/09_sql_analytics.sql'
    if os.path.exists(sql_script):
        with open(sql_script, 'r', encoding='utf-8') as f:
            q_count = f.read().upper().count('SELECT ')
        if q_count >= 30:
            log_result("PASS", f"Found {q_count} queries in scripts/09_sql_analytics.sql")
        else:
            log_result("FAIL", f"Found only {q_count} queries. Expected >=30.", "Add more queries to scripts/09_sql_analytics.sql")
    
    sql_res = 'outputs/sql_analytics_results.txt'
    if os.path.exists(sql_res):
        with open(sql_res, 'r', encoding='utf-8') as f:
            content = f.read()
            if len(content) > 1000:
                log_result("PASS", "outputs/sql_analytics_results.txt is populated.")
            else:
                log_result("FAIL", "outputs/sql_analytics_results.txt is nearly empty.", "Run scripts/10_run_sql_analytics.py")
    else:
        log_result("FAIL", "outputs/sql_analytics_results.txt not found.", "Run scripts/10_run_sql_analytics.py")

    # --- Phase 3: Cleaning ---
    print("\n--- Phase 3: Cleaning ---")
    report_lines.append("\n--- Phase 3: Cleaning ---")
    master_features = 'data/clean/master_orders_features.csv'
    if os.path.exists(master_features):
        df = pd.read_csv(master_features, nrows=10)
        outlier_cols = ['is_price_outlier', 'is_freight_value_outlier', 'is_delivery_days_outlier']
        missing = [c for c in outlier_cols if c not in df.columns]
        if missing:
            log_result("FAIL", f"Missing outlier columns: {missing}", "Run scripts/11_outlier_detection.py")
        else:
            log_result("PASS", "Outlier flag columns exist in features table.")
    
    fig_dir = 'outputs/figures'
    if os.path.exists(fig_dir):
        if any('outlier' in f.lower() or 'boxplot' in f.lower() for f in os.listdir(fig_dir)):
            log_result("PASS", "Outlier box plots exist in outputs/figures/")
        else:
            log_result("FAIL", "Outlier box plots missing.", "Run visualizations script")

    # --- Phase 4: Feature Engineering ---
    print("\n--- Phase 4: Feature Engineering ---")
    report_lines.append("\n--- Phase 4: Feature Engineering ---")
    if os.path.exists(master_features):
        req_cols = ['revenue', 'approx_cost', 'approx_profit', 'approx_profit_margin', 
                    'order_month', 'order_quarter', 'order_year', 'is_weekend_order', 'high_value_customer']
        df_full = pd.read_csv(master_features)
        missing_cols = [c for c in req_cols if c not in df_full.columns]
        if missing_cols:
            log_result("FAIL", f"Missing engineered columns: {missing_cols}", "Run scripts/12_feature_engineering.py")
        else:
            log_result("PASS", "All required engineered features exist.")
            
            # Spot check formula
            sample = df_full.sample(5, random_state=42)
            calculated_profit = sample['revenue'] - sample['approx_cost']
            if (sample['approx_profit'].round(2) == calculated_profit.round(2)).all():
                log_result("PASS", "Spot-check: approx_profit mathematically matches revenue - approx_cost exactly.")
            else:
                log_result("FAIL", "Spot-check failed for approx_profit formula.", "Fix scripts/12_feature_engineering.py")

    # --- Phase 5: Visualizations ---
    print("\n--- Phase 5: Visualizations ---")
    report_lines.append("\n--- Phase 5: Visualizations ---")
    if os.path.exists(fig_dir):
        pngs = [f for f in os.listdir(fig_dir) if f.endswith('.png')]
        corrupted = [f for f in pngs if os.path.getsize(os.path.join(fig_dir, f)) < 1024]
        
        if len(pngs) >= 20:
            log_result("PASS", f"Found {len(pngs)} PNG files in outputs/figures/")
        else:
            log_result("FAIL", f"Found only {len(pngs)} PNG files. Expected >=20.", "Run scripts/13_visualizations.py")
            
        if corrupted:
            log_result("FAIL", f"Found corrupted/empty PNGs: {corrupted}", "Check visualizations script")
        else:
            log_result("PASS", "No 0-byte or corrupted PNGs found.")
            
        filenames = " ".join(pngs).lower()
        if 'heatmap' in filenames and 'boxplot' in filenames and 'scatter' in filenames and 'pair' in filenames:
            log_result("PASS", "Confirmed presence of heatmap, boxplot, scatter, and pair plot.")
        else:
            log_result("FAIL", "Missing required specific chart types.", "Ensure heatmap, boxplot, scatter, pair plots are generated")

    # --- Phase 6: Statistics ---
    print("\n--- Phase 6: Statistics ---")
    report_lines.append("\n--- Phase 6: Statistics ---")
    stat_file = 'outputs/statistics_summary.txt'
    if os.path.exists(stat_file):
        with open(stat_file, 'r', encoding='utf-8') as f:
            stat_text = f.read().lower()
        keywords = ['mean', 'median', 'mode', 'variance', 'std', 'q1', 'percentile', 'correlation', 'covariance']
        missing_keys = [k for k in keywords if k not in stat_text and k.replace('std', 'standard deviation') not in stat_text]
        if not missing_keys:
            log_result("PASS", "All statistical keywords found in summary.")
        else:
            log_result("FAIL", f"Missing statistical keywords: {missing_keys}", "Run scripts/14_statistics.py")
    else:
        log_result("FAIL", "statistics_summary.txt not found.", "Run scripts/14_statistics.py")

    # --- Phase 7 & 8: ML Model + Evaluation ---
    print("\n--- Phase 7 & 8: ML Model + Evaluation ---")
    report_lines.append("\n--- Phase 7 & 8: ML Model + Evaluation ---")
    ml_script = 'scripts/15_ml_model.py'
    if os.path.exists(ml_script):
        with open(ml_script, 'r', encoding='utf-8') as f:
            ml_code = f.read()
        if 'high_value_customer' in ml_code:
            log_result("PASS", "Classification model targets 'high_value_customer'.")
        else:
            log_result("FAIL", "Model does not seem to target high_value_customer.", "Update scripts/15_ml_model.py")
            
        if all(metric in ml_code for metric in ['accuracy', 'precision', 'recall', 'f1', 'confusion_matrix']):
            log_result("PASS", "Model script imports/reports all 5 required metrics.")
        else:
            log_result("FAIL", "Model script missing some required metric calculations.", "Update scripts/15_ml_model.py")
    else:
        log_result("FAIL", "scripts/15_ml_model.py not found.", "Build ML script")

    # --- Phase 9: Dashboard ---
    print("\n--- Phase 9: Dashboard ---")
    report_lines.append("\n--- Phase 9: Dashboard ---")
    dash_script = 'scripts/03_dashboard.py'
    if os.path.exists(dash_script):
        with open(dash_script, 'r', encoding='utf-8') as f:
            dash_code = f.read()
        kpis = ['Total Revenue', 'Total Approx. Profit', 'Total Customers', 'Total Orders']
        missing_kpis = [k for k in kpis if k not in dash_code]
        if not missing_kpis:
            log_result("PASS", "All 4 required KPIs present in dashboard code.")
        else:
            log_result("FAIL", f"Missing KPIs in dashboard: {missing_kpis}", "Update scripts/03_dashboard.py")
            
        if 'approximate' in dash_code.lower() or 'proxy' in dash_code.lower():
            log_result("PASS", "Profit KPI is labeled with an approximation caveat.")
        else:
            log_result("FAIL", "Profit KPI is missing 'approximate/proxy' caveat language.", "Update scripts/03_dashboard.py labels")
    else:
        log_result("FAIL", "scripts/03_dashboard.py not found.", "Build Dashboard script")

    # --- Business Insights ---
    print("\n--- Business Insights ---")
    report_lines.append("\n--- Business Insights ---")
    report_file = 'outputs/business_report.md'
    if os.path.exists(report_file):
        with open(report_file, 'r', encoding='utf-8') as f:
            report_text = f.read()
        
        # Extract Business Insights section
        if '## Business Insights' in report_text:
            insights_section = report_text.split('## Business Insights')[1]
            # Match numbered bullets like "1. **Title**" or just "1."
            bullets = re.findall(r"^\d+\.\s+(.*)$", insights_section, re.MULTILINE)
            if len(bullets) >= 15:
                log_result("PASS", f"Found {len(bullets)} business insight bullets.")
                
                # Check for digits in every bullet
                generic = []
                for idx, b in enumerate(bullets):
                    if not re.search(r"\d", b):
                        generic.append(idx+1)
                
                if generic:
                    log_result("FAIL", f"Bullets lack data grounding (no numbers): {generic}", "Update business_report.md insights to include specific metrics")
                else:
                    log_result("PASS", "All 15+ business insights are data-grounded with numbers.")
            else:
                log_result("FAIL", f"Found only {len(bullets)} business insight bullets. Expected 15.", "Run scripts/16_generate_insights.py")
        else:
            log_result("FAIL", "## Business Insights section missing in report.", "Run scripts/16_generate_insights.py")
            
    # --- Field Mapping Consistency ---
    print("\n--- Field Mapping Consistency ---")
    report_lines.append("\n--- Field Mapping Consistency ---")
    if os.path.exists(report_file):
        with open(report_file, 'r', encoding='utf-8') as f:
            report_text = f.read()
        if 'field_mapping_notes.md' in report_text or 'proxy' in report_text or 'approximation' in report_text.lower():
            log_result("PASS", "Field mapping context (proxy/approximations or notes link) found in business report.")
        else:
            log_result("FAIL", "field_mapping_notes.md context missing in business report.", "Add field mapping note to business_report.md")

    # --- SCORECARD ---
    scorecard = f"""
==================================================
FINAL QA SCORECARD
==================================================
Total Checks : {total_checks}
Passes       : {passes}
Warnings     : {warnings}
Failures     : {fails}
==================================================
"""
    print(scorecard)
    report_lines.append(scorecard)
    
    with open('outputs/final_qa_report.txt', 'w', encoding='utf-8') as f:
        f.write("\n".join(report_lines))
    print("Final QA report saved to outputs/final_qa_report.txt")

if __name__ == "__main__":
    run_full_qa()
