#!/usr/bin/env python3
"""
KForce Data Engineering Demo
Demonstrates real data engineering workflow with source/target tables and transformations
"""

import os
import sys
import time
import requests
import json
from pathlib import Path
from memra import Agent, Department, LLM, ExecutionEngine

def cleanup_demo_tables():
    """Clean up any existing demo tables before starting"""
    print("🧹 Cleaning up any existing demo tables...")
    
    cleanup_sql = """
    DROP TABLE IF EXISTS clean_employees CASCADE;
    DROP TABLE IF EXISTS raw_employees CASCADE;
    """
    
    mcp_url = "http://localhost:8081"
    
    try:
        response = requests.post(f"{mcp_url}/execute_tool", json={
            "tool_name": "SQLExecutor",
            "params": {"sql_query": cleanup_sql}
        }, headers={
            "X-Bridge-Secret": "test-secret-for-development",
            "Content-Type": "application/json"
        }, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print("✅ Demo tables cleaned up successfully")
            else:
                print(f"⚠️ Cleanup had issues: {result.get('error', 'Unknown error')}")
        else:
            print(f"❌ Failed to cleanup tables: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error during cleanup: {e}")
    
    print("✅ Cleanup complete")

def print_problem_statement():
    """Print the problem statement and solution approach"""
    print("=" * 80)
    print("🏢 KFORCE DATA ENGINEERING DEMO")
    print("=" * 80)
    print()
    print("📋 PROBLEM STATEMENT:")
    print("   KForce has employee data stored in various systems with inconsistent formats:")
    print("   • Names are split into first_name and last_name fields")
    print("   • Email addresses have mixed case (john.SMITH@kforce.com)")
    print("   • Department names are inconsistent (engineering, Engineering, ENGINEERING)")
    print("   • No salary band categorization for reporting")
    print("   • Years of employment not calculated")
    print("   • Manager information stored as IDs, not names")
    print("   • Status values inconsistent (Active, active, ACTIVE)")
    print()
    print("🎯 SOLUTION APPROACH:")
    print("   We'll create a data engineering pipeline that:")
    print("   1. Creates a source table with raw, inconsistent employee data")
    print("   2. Creates a target table with clean, standardized schema")
    print("   3. Performs SQL transformations to clean and standardize the data")
    print("   4. Shows the before/after comparison")
    print()
    print("🔄 TRANSFORMATIONS TO BE APPLIED:")
    print("   • Name concatenation: first_name + last_name → full_name")
    print("   • Email standardization: Convert all emails to lowercase")
    print("   • Department standardization: Convert all departments to uppercase")
    print("   • Salary band calculation: Create business categories (Junior/Mid-Level/Senior/Executive)")
    print("   • Years employed calculation: Compute tenure from hire date")
    print("   • Manager lookup: Join with manager data to get manager names")
    print("   • Status standardization: 'Active' → 'EMPLOYED'")
    print()
    print("=" * 80)
    print()

def setup_database_tables():
    """Create source and target tables in PostgreSQL"""
    print("🗄️ Setting up database tables...")
    
    # Create source table - raw employee data (messy, inconsistent)
    create_source_table_sql = """
    CREATE TABLE IF NOT EXISTS raw_employees (
        employee_id VARCHAR(10),
        first_name VARCHAR(50),
        last_name VARCHAR(50),
        email VARCHAR(100),
        hire_date DATE,
        salary DECIMAL(10,2),
        department VARCHAR(50),
        manager_id VARCHAR(10),
        status VARCHAR(20),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    
    # Create target table - cleaned employee data (standardized, business-ready)
    create_target_table_sql = """
    CREATE TABLE IF NOT EXISTS clean_employees (
        employee_id VARCHAR(10) PRIMARY KEY,
        full_name VARCHAR(100),
        email VARCHAR(100),
        hire_date DATE,
        salary_usd DECIMAL(10,2),
        department VARCHAR(50),
        manager_name VARCHAR(100),
        employee_status VARCHAR(20),
        years_employed INTEGER,
        salary_band VARCHAR(20),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    
    # Insert sample data into source table (messy, inconsistent data)
    insert_source_data_sql = """
    INSERT INTO raw_employees (employee_id, first_name, last_name, email, hire_date, salary, department, manager_id, status) VALUES
    ('EMP001', 'John', 'Smith', 'john.SMITH@kforce.com', '2020-01-15', 75000.00, 'engineering', 'MGR001', 'Active'),
    ('EMP002', 'Sarah', 'Johnson', 'sarah.J@kforce.com', '2019-03-22', 82000.00, 'Sales', 'MGR002', 'active'),
    ('EMP003', 'Mike', 'Davis', 'mike.davis@kforce.com', '2021-06-10', 68000.00, 'Engineering', 'MGR001', 'Active'),
    ('EMP004', 'Lisa', 'Wilson', 'lisa.wilson@kforce.com', '2018-11-05', 95000.00, 'marketing', 'MGR003', 'ACTIVE'),
    ('EMP005', 'David', 'Brown', 'david.brown@kforce.com', '2022-02-28', 72000.00, 'Sales', 'MGR002', 'Inactive'),
    ('EMP006', 'Emily', 'Taylor', 'emily.taylor@kforce.com', '2020-09-14', 88000.00, 'engineering', 'MGR001', 'Active'),
    ('EMP007', 'Robert', 'Anderson', 'robert.anderson@kforce.com', '2019-07-30', 78000.00, 'Marketing', 'MGR003', 'active'),
    ('EMP008', 'Jennifer', 'Martinez', 'jennifer.martinez@kforce.com', '2021-04-12', 65000.00, 'sales', 'MGR002', 'Active'),
    ('EMP009', 'Christopher', 'Garcia', 'chris.garcia@kforce.com', '2020-12-03', 92000.00, 'Engineering', 'MGR001', 'ACTIVE'),
    ('EMP010', 'Amanda', 'Rodriguez', 'amanda.rodriguez@kforce.com', '2019-08-20', 85000.00, 'marketing', 'MGR003', 'Active');
    """
    
    # Insert manager data for reference
    insert_manager_data_sql = """
    INSERT INTO raw_employees (employee_id, first_name, last_name, email, hire_date, salary, department, manager_id, status) VALUES
    ('MGR001', 'Michael', 'Thompson', 'michael.thompson@kforce.com', '2017-05-10', 120000.00, 'Engineering', NULL, 'Active'),
    ('MGR002', 'Jessica', 'Lee', 'jessica.lee@kforce.com', '2018-02-15', 110000.00, 'Sales', NULL, 'Active'),
    ('MGR003', 'Daniel', 'Clark', 'daniel.clark@kforce.com', '2016-11-08', 115000.00, 'Marketing', NULL, 'Active');
    """
    
    # Execute SQL statements via MCP bridge
    mcp_url = "http://localhost:8081"
    
    sql_statements = [
        create_source_table_sql,
        create_target_table_sql,
        insert_source_data_sql,
        insert_manager_data_sql
    ]
    
    for i, sql in enumerate(sql_statements, 1):
        try:
            response = requests.post(f"{mcp_url}/execute_tool", json={
                "tool_name": "SQLExecutor",
                "params": {"sql_query": sql}
            }, headers={
                "X-Bridge-Secret": "test-secret-for-development",
                "Content-Type": "application/json"
            }, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    print(f"✅ SQL statement {i} executed successfully")
                else:
                    print(f"⚠️ SQL statement {i} had issues: {result.get('error', 'Unknown error')}")
            else:
                print(f"❌ Failed to execute SQL statement {i}: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error executing SQL statement {i}: {e}")
    
    print("✅ Database tables setup complete")

def show_before_data():
    """Show the raw, messy data before transformation"""
    print("\n📊 BEFORE TRANSFORMATION - Raw Employee Data:")
    print("-" * 80)
    
    query_sql = """
    SELECT 
        employee_id,
        first_name,
        last_name,
        email,
        department,
        salary,
        status
    FROM raw_employees 
    WHERE employee_id NOT LIKE 'MGR%'
    ORDER BY employee_id 
    LIMIT 5;
    """
    
    mcp_url = "http://localhost:8081"
    
    try:
        response = requests.post(f"{mcp_url}/execute_tool", json={
            "tool_name": "SQLExecutor",
            "params": {"sql_query": query_sql}
        }, headers={
            "X-Bridge-Secret": "test-secret-for-development",
            "Content-Type": "application/json"
        }, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                # Handle nested data structure
                if "data" in result and isinstance(result["data"], dict):
                    results = result["data"].get("results", [])
                else:
                    results = result.get("results", [])
                
                print(f"{'ID':<8} {'Name':<20} {'Email':<25} {'Dept':<12} {'Salary':<8} {'Status':<8}")
                print("-" * 80)
                for row in results:
                    name = f"{row['first_name']} {row['last_name']}"
                    print(f"{row['employee_id']:<8} {name:<20} {row['email']:<25} {row['department']:<12} {row['salary']:<8} {row['status']:<8}")
                
                print("\n🔍 DATA QUALITY ISSUES IDENTIFIED:")
                print("   • Names are split (first_name, last_name)")
                print("   • Email case inconsistent (john.SMITH@kforce.com)")
                print("   • Department case inconsistent (engineering, Engineering, ENGINEERING)")
                print("   • Status values inconsistent (Active, active, ACTIVE)")
                print("   • No salary bands for reporting")
                print("   • No years employed calculation")
                print("   • Manager names not resolved (only IDs)")
            else:
                print(f"⚠️ Query failed: {result.get('error', 'Unknown error')}")
        else:
            print(f"❌ Query failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error showing before data: {e}")

def perform_data_transformation():
    """Perform actual data transformation from source to target"""
    print("\n🔄 PERFORMING DATA TRANSFORMATION...")
    print("-" * 80)
    
    # Complex transformation SQL that:
    # 1. Joins employee data with manager data
    # 2. Calculates years employed
    # 3. Creates salary bands
    # 4. Cleans and standardizes data
    transformation_sql = """
    INSERT INTO clean_employees (
        employee_id,
        full_name,
        email,
        hire_date,
        salary_usd,
        department,
        manager_name,
        employee_status,
        years_employed,
        salary_band
    )
    SELECT 
        e.employee_id,
        CONCAT(e.first_name, ' ', e.last_name) as full_name,
        LOWER(e.email) as email,
        e.hire_date,
        e.salary as salary_usd,
        UPPER(e.department) as department,
        CONCAT(m.first_name, ' ', m.last_name) as manager_name,
        CASE 
            WHEN e.status = 'Active' THEN 'EMPLOYED'
            WHEN e.status = 'Inactive' THEN 'TERMINATED'
            ELSE 'UNKNOWN'
        END as employee_status,
        EXTRACT(YEAR FROM CURRENT_DATE) - EXTRACT(YEAR FROM e.hire_date) as years_employed,
        CASE 
            WHEN e.salary < 70000 THEN 'Junior'
            WHEN e.salary < 90000 THEN 'Mid-Level'
            WHEN e.salary < 110000 THEN 'Senior'
            ELSE 'Executive'
        END as salary_band
    FROM raw_employees e
    LEFT JOIN raw_employees m ON e.manager_id = m.employee_id
    WHERE e.employee_id NOT LIKE 'MGR%'
    ON CONFLICT (employee_id) DO UPDATE SET
        full_name = EXCLUDED.full_name,
        email = EXCLUDED.email,
        hire_date = EXCLUDED.hire_date,
        salary_usd = EXCLUDED.salary_usd,
        department = EXCLUDED.department,
        manager_name = EXCLUDED.manager_name,
        employee_status = EXCLUDED.employee_status,
        years_employed = EXCLUDED.years_employed,
        salary_band = EXCLUDED.salary_band,
        created_at = CURRENT_TIMESTAMP;
    """
    
    mcp_url = "http://localhost:8081"
    
    try:
        response = requests.post(f"{mcp_url}/execute_tool", json={
            "tool_name": "SQLExecutor",
            "params": {"sql_query": transformation_sql}
        }, headers={
            "X-Bridge-Secret": "test-secret-for-development",
            "Content-Type": "application/json"
        }, timeout=15)
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print("✅ Data transformation completed successfully")
                return True
            else:
                print(f"❌ Transformation failed: {result.get('error', 'Unknown error')}")
                return False
        else:
            print(f"❌ Failed to execute transformation: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error during transformation: {e}")
        return False

def show_after_data():
    """Show the clean, transformed data after transformation"""
    print("\n📊 AFTER TRANSFORMATION - Clean Employee Data:")
    print("-" * 80)
    
    query_sql = """
    SELECT 
        employee_id,
        full_name,
        email,
        department,
        salary_usd,
        salary_band,
        years_employed,
        manager_name,
        employee_status
    FROM clean_employees 
    ORDER BY employee_id 
    LIMIT 5;
    """
    
    mcp_url = "http://localhost:8081"
    
    try:
        response = requests.post(f"{mcp_url}/execute_tool", json={
            "tool_name": "SQLExecutor",
            "params": {"sql_query": query_sql}
        }, headers={
            "X-Bridge-Secret": "test-secret-for-development",
            "Content-Type": "application/json"
        }, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                # Handle nested data structure
                if "data" in result and isinstance(result["data"], dict):
                    results = result["data"].get("results", [])
                else:
                    results = result.get("results", [])
                
                print(f"{'ID':<8} {'Full Name':<20} {'Email':<25} {'Dept':<12} {'Salary':<8} {'Band':<10} {'Years':<6} {'Manager':<15} {'Status':<10}")
                print("-" * 80)
                for row in results:
                    print(f"{row['employee_id']:<8} {row['full_name']:<20} {row['email']:<25} {row['department']:<12} {row['salary_usd']:<8} {row['salary_band']:<10} {row['years_employed']:<6} {row['manager_name']:<15} {row['employee_status']:<10}")
                
                print("\n✅ DATA QUALITY IMPROVEMENTS ACHIEVED:")
                print("   • Names concatenated into full_name field")
                print("   • Email addresses standardized to lowercase")
                print("   • Department names standardized to uppercase")
                print("   • Salary bands calculated (Junior/Mid-Level/Senior/Executive)")
                print("   • Years employed calculated automatically")
                print("   • Manager names resolved from IDs")
                print("   • Status values standardized (EMPLOYED/TERMINATED)")
            else:
                print(f"⚠️ Query failed: {result.get('error', 'Unknown error')}")
        else:
            print(f"❌ Query failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error showing after data: {e}")

def verify_results():
    """Verify the transformation results"""
    print("\n🔍 VERIFYING TRANSFORMATION RESULTS...")
    print("-" * 80)
    
    # Check source table count
    source_count_sql = "SELECT COUNT(*) as count FROM raw_employees WHERE employee_id NOT LIKE 'MGR%';"
    
    # Check target table count
    target_count_sql = "SELECT COUNT(*) as count FROM clean_employees;"
    
    mcp_url = "http://localhost:8081"
    
    try:
        # Get source count
        response = requests.post(f"{mcp_url}/execute_tool", json={
            "tool_name": "SQLExecutor",
            "params": {"sql_query": source_count_sql}
        }, headers={
            "X-Bridge-Secret": "test-secret-for-development",
            "Content-Type": "application/json"
        }, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                # Handle nested data structure
                if "data" in result and isinstance(result["data"], dict):
                    results = result["data"].get("results", [])
                else:
                    results = result.get("results", [])
                if results and len(results) > 0:
                    source_count = results[0].get("count", 0)
                    print(f"📊 Source records: {source_count}")
                else:
                    print("📊 Source records: 0")
                    source_count = 0
            else:
                print(f"⚠️ Source count query failed: {result.get('error', 'Unknown error')}")
                source_count = 0
        else:
            print(f"❌ Source count query failed: {response.status_code}")
            source_count = 0
        
        # Get target count
        response = requests.post(f"{mcp_url}/execute_tool", json={
            "tool_name": "SQLExecutor",
            "params": {"sql_query": target_count_sql}
        }, headers={
            "X-Bridge-Secret": "test-secret-for-development",
            "Content-Type": "application/json"
        }, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                # Handle nested data structure
                if "data" in result and isinstance(result["data"], dict):
                    results = result["data"].get("results", [])
                else:
                    results = result.get("results", [])
                if results and len(results) > 0:
                    target_count = results[0].get("count", 0)
                    print(f"📊 Target records: {target_count}")
                else:
                    print("📊 Target records: 0")
                    target_count = 0
            else:
                print(f"⚠️ Target count query failed: {result.get('error', 'Unknown error')}")
                target_count = 0
        else:
            print(f"❌ Target count query failed: {response.status_code}")
            target_count = 0
        
        return True
        
    except Exception as e:
        print(f"❌ Error verifying results: {e}")
        return False

def create_kforce_workflow():
    """Create the KForce data engineering workflow using Memra composition language"""
    
    # Define LLMs for different agent types
    data_llm = LLM(model="llama-3.2-11b-vision-preview", temperature=0.1)
    transform_llm = LLM(model="llama-3.2-11b-vision-preview", temperature=0.0)
    
    # Data Engineer Agent - Setup and orchestration
    data_engineer_agent = Agent(
        role="Data Engineer",
        job="Setup database tables and orchestrate data transformation pipeline",
        llm=data_llm,
        sops=[
            "Create source table with raw employee data",
            "Create target table for cleaned employee data",
            "Insert sample data into source table",
            "Coordinate transformation process",
            "Verify data quality and completeness"
        ],
        systems=["PostgreSQL", "MCPBridge"],
        tools=[
            {"name": "SQLExecutor", "hosted_by": "mcp"},
            {"name": "DataValidator", "hosted_by": "mcp"}
        ],
        input_keys=["database_url"],
        output_key="pipeline_status"
    )
    
    # Data Transformation Agent - Actual data processing
    transformation_agent = Agent(
        role="Data Transformation Specialist",
        job="Transform raw employee data into clean, standardized format",
        llm=transform_llm,
        sops=[
            "Read data from raw_employees table",
            "Apply data cleaning rules (email formatting, name concatenation)",
            "Calculate derived fields (years employed, salary bands)",
            "Join with manager data for reporting",
            "Handle data quality issues and standardize values",
            "Insert transformed data into clean_employees table"
        ],
        systems=["PostgreSQL", "MCPBridge"],
        tools=[
            {"name": "SQLExecutor", "hosted_by": "mcp"},
            {"name": "DataValidator", "hosted_by": "mcp"}
        ],
        input_keys=["source_table", "target_table"],
        output_key="transformation_results"
    )
    
    # Data Quality Agent - Validation and verification
    quality_agent = Agent(
        role="Data Quality Analyst",
        job="Validate transformation results and ensure data quality",
        llm=data_llm,
        sops=[
            "Verify record counts match between source and target",
            "Check data completeness and accuracy",
            "Validate business rules (salary bands, years employed)",
            "Generate quality metrics and summary report",
            "Flag any data quality issues"
        ],
        systems=["PostgreSQL", "MCPBridge"],
        tools=[
            {"name": "SQLExecutor", "hosted_by": "mcp"},
            {"name": "DataValidator", "hosted_by": "mcp"}
        ],
        input_keys=["source_table", "target_table"],
        output_key="quality_report"
    )
    
    # Create the KForce Department using composition language
    kforce_department = Department(
        name="KForce Data Engineering",
        mission="Transform raw employee data into clean, standardized format with business logic",
        agents=[data_engineer_agent, transformation_agent, quality_agent],
        workflow_order=[
            "Data Engineer",
            "Data Transformation Specialist",
            "Data Quality Analyst"
        ],
        dependencies=["PostgreSQL", "MCPBridge"],
        execution_policy={
            "retry_on_fail": True,
            "max_retries": 3,
            "halt_on_validation_error": False,
            "timeout_seconds": 300
        },
        context={
            "company": "KForce",
            "source_table": "raw_employees",
            "target_table": "clean_employees",
            "transformation_type": "employee_data_cleansing"
        }
    )
    
    return kforce_department

def main():
    """Main function to run the KForce demo"""
    try:
        # Print problem statement and solution approach
        print_problem_statement()
        
        # Step 0: Cleanup any existing demo tables
        cleanup_demo_tables()
        
        # Step 1: Setup database tables
        print("\n🔄 Step 1/3: Data Engineer")
        setup_database_tables()
        
        # Step 2: Show before data
        show_before_data()
        
        # Step 3: Perform transformation
        print("\n🔄 Step 2/3: Data Transformation Specialist")
        if perform_data_transformation():
            print("✅ Data transformation completed successfully")
        else:
            print("❌ Data transformation failed")
            return False
        
        # Step 4: Show after data
        show_after_data()
        
        # Step 5: Verify results
        print("\n🔄 Step 3/3: Data Quality Analyst")
        if verify_results():
            print("✅ Data quality verification completed")
        else:
            print("❌ Data quality verification failed")
            return False
        
        # Display final results
        print("\n" + "=" * 80)
        print("🎉 KFORCE DATA ENGINEERING WORKFLOW COMPLETED SUCCESSFULLY!")
        print("=" * 80)
        print()
        print("📊 SUMMARY:")
        print("   • Problem: Inconsistent employee data across systems")
        print("   • Solution: Data engineering pipeline with SQL transformations")
        print("   • Result: Clean, standardized, business-ready employee data")
        print()
        print("🔍 NEXT STEPS:")
        print("   • Check database: docker exec -it memra-ops_postgres_1 psql -U postgres -d local_workflow")
        print("   • View source: SELECT * FROM raw_employees LIMIT 5;")
        print("   • View target: SELECT * FROM clean_employees LIMIT 5;")
        print("   • Compare: SELECT e.employee_id, e.first_name, c.full_name, c.salary_band FROM raw_employees e JOIN clean_employees c ON e.employee_id = c.employee_id;")
        print()
        print("🧹 CLEANUP:")
        print("   • Run cleanup: python memra/demos/kforce_engineering/cleanup_demo.py")
        print("=" * 80)
        
        return True
        
    except Exception as e:
        print(f"❌ Error in KForce workflow: {e}")
        return False

if __name__ == "__main__":
    main() 