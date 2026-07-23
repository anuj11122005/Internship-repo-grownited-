import sqlite3
import pandas as pd
import os
import re

def execute_analytics():
    print("Executing Phase 2 SQL Analytics...")
    
    db_path = 'data/olist_clean.db'
    sql_script_path = 'scripts/09_sql_analytics.sql'
    output_path = 'outputs/sql_analytics_results.txt'
    
    if not os.path.exists(db_path):
        print(f"Error: Database {db_path} not found. Please run Phase 1 loading script first.")
        return
        
    if not os.path.exists(sql_script_path):
        print(f"Error: SQL script {sql_script_path} not found.")
        return
        
    os.makedirs('outputs', exist_ok=True)
    
    # Read and parse the SQL file
    with open(sql_script_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # Split queries by semicolon, keeping comments intact
    # We will use regex to find queries block by block
    queries = []
    
    # Simple parser: split by -- Q
    blocks = content.split('-- Q')
    for block in blocks[1:]: # Skip the header block
        # Restore the -- Q prefix
        block = '-- Q' + block
        
        # Extract comment
        comment_match = re.match(r'(-- Q\d+:.*?)\n', block)
        if comment_match:
            comment = comment_match.group(1).strip()
            # Extract SQL query
            sql = block[len(comment_match.group(0)):].strip()
            # Remove trailing semicolon for pandas
            if sql.endswith(';'):
                sql = sql[:-1]
                
            queries.append({"comment": comment, "sql": sql})

    print(f"Found {len(queries)} analytics queries to execute.")
    
    # Connect and execute
    with sqlite3.connect(db_path) as conn:
        with open(output_path, 'w', encoding='utf-8') as out_f:
            out_f.write("==================================================\n")
            out_f.write("       OLIST E-COMMERCE SQL ANALYTICS RESULTS     \n")
            out_f.write("==================================================\n\n")
            
            for q in queries:
                print(f"Executing: {q['comment']}")
                
                try:
                    df = pd.read_sql_query(q['sql'], conn)
                    
                    # Formatting for output
                    output_block = f"{q['comment']}\n{'-' * len(q['comment'])}\n"
                    
                    if df.empty:
                        output_block += "No results returned.\n\n"
                    else:
                        output_block += df.to_string(index=False) + "\n\n"
                        
                    out_f.write(output_block)
                    
                except Exception as e:
                    error_msg = f"{q['comment']}\n{'-' * len(q['comment'])}\nERROR executing query: {e}\n\n"
                    out_f.write(error_msg)
                    print(f"  -> ERROR: {e}")
                    
    print(f"\nSQL Analytics execution complete. Results saved to {output_path}")

if __name__ == "__main__":
    execute_analytics()
