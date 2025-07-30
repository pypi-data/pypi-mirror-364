#!/usr/bin/env python3
"""
AI Job Portal Demo
Takes natural language job postings and automatically creates AI agents to solve the problem
"""

import os
import sys
import json
import requests
from pathlib import Path
from memra import Agent, Department, LLM, ExecutionEngine

def analyze_job_posting(job_description):
    """Use LLM to analyze job posting and determine required agents and workflow"""
    print("🤖 Analyzing job posting with AI...")
    
    # Use Hugging Face API to analyze the job posting
    hf_api_key = os.getenv("HUGGINGFACE_API_KEY")
    if not hf_api_key:
        print("❌ HUGGINGFACE_API_KEY not found in environment")
        return None
    
    # Create prompt for job analysis
    analysis_prompt = f"""
    Analyze this job posting and determine what AI agents are needed to solve the problem.
    
    Job Posting:
    {job_description}
    
    Please provide a JSON response with the following structure:
    {{
        "problem_type": "string describing the type of problem",
        "required_agents": [
            {{
                "role": "agent role name",
                "job": "detailed job description",
                "tools": ["list", "of", "required", "tools"],
                "sops": ["list", "of", "standard", "operating", "procedures"]
            }}
        ],
        "workflow_order": ["list", "of", "agent", "roles", "in", "execution", "order"],
        "data_requirements": {{
            "source_tables": ["list", "of", "source", "table", "names"],
            "target_tables": ["list", "of", "target", "table", "names"],
            "transformations": ["list", "of", "required", "data", "transformations"]
        }}
    }}
    
    Focus on creating a realistic data engineering workflow that demonstrates the problem and solution.
    """
    
    try:
        # Call Hugging Face API
        headers = {"Authorization": f"Bearer {hf_api_key}"}
        payload = {
            "inputs": analysis_prompt,
            "parameters": {
                "max_new_tokens": 1000,
                "temperature": 0.1,
                "return_full_text": False
            }
        }
        
        response = requests.post(
            "https://api-inference.huggingface.co/models/meta-llama/Llama-2-70b-chat-hf",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            # Extract the generated text and parse as JSON
            generated_text = result[0]["generated_text"]
            
            # Try to extract JSON from the response
            try:
                # Find JSON in the response
                start_idx = generated_text.find("{")
                end_idx = generated_text.rfind("}") + 1
                json_str = generated_text[start_idx:end_idx]
                analysis = json.loads(json_str)
                print("✅ Job analysis completed successfully")
                return analysis
            except json.JSONDecodeError:
                print("⚠️ Could not parse LLM response as JSON, using fallback")
                return create_fallback_analysis(job_description)
        else:
            print(f"❌ Hugging Face API error: {response.status_code}")
            return create_fallback_analysis(job_description)
            
    except Exception as e:
        print(f"❌ Error calling Hugging Face API: {e}")
        return create_fallback_analysis(job_description)

def create_fallback_analysis(job_description):
    """Create a fallback analysis if LLM fails"""
    print("🔄 Using fallback analysis...")
    
    # Simple keyword-based analysis
    job_lower = job_description.lower()
    
    if "medallion" in job_lower or "bronze" in job_lower or "silver" in job_lower or "gold" in job_lower:
        return {
            "problem_type": "medallion_architecture_data_pipeline",
            "required_agents": [
                {
                    "role": "Data Engineer",
                    "job": "Setup database tables and orchestrate data transformation pipeline",
                    "tools": ["SQLExecutor"],
                    "sops": ["Create source and target tables", "Design data schema", "Coordinate pipeline execution"]
                },
                {
                    "role": "Bronze Layer Specialist",
                    "job": "Process raw data and create bronze layer tables",
                    "tools": ["SQLExecutor"],
                    "sops": ["Extract raw data", "Apply basic validation", "Store in bronze layer"]
                },
                {
                    "role": "Silver Layer Specialist", 
                    "job": "Transform bronze data into silver layer with business logic",
                    "tools": ["SQLExecutor"],
                    "sops": ["Apply data transformations", "Implement business rules", "Create silver layer"]
                },
                {
                    "role": "Gold Layer Specialist",
                    "job": "Create final gold layer with aggregated and modeled data",
                    "tools": ["SQLExecutor"],
                    "sops": ["Aggregate data", "Create data models", "Generate final gold layer"]
                }
            ],
            "workflow_order": ["Data Engineer", "Bronze Layer Specialist", "Silver Layer Specialist", "Gold Layer Specialist"],
            "data_requirements": {
                "source_tables": ["raw_sales_data"],
                "target_tables": ["bronze_sales", "silver_sales", "gold_sales_summary"],
                "transformations": ["data_cleansing", "aggregation", "business_logic_application"]
            }
        }
    else:
        # Default data engineering workflow
        return {
            "problem_type": "data_engineering_pipeline",
            "required_agents": [
                {
                    "role": "Data Engineer",
                    "job": "Setup database tables and orchestrate data transformation pipeline",
                    "tools": ["SQLExecutor"],
                    "sops": ["Create source and target tables", "Design data schema", "Coordinate pipeline execution"]
                },
                {
                    "role": "Data Transformation Specialist",
                    "job": "Transform and clean data according to business requirements",
                    "tools": ["SQLExecutor"],
                    "sops": ["Apply data transformations", "Clean and validate data", "Implement business logic"]
                },
                {
                    "role": "Data Quality Analyst",
                    "job": "Validate data quality and ensure accuracy",
                    "tools": ["SQLExecutor"],
                    "sops": ["Verify data completeness", "Check data accuracy", "Generate quality reports"]
                }
            ],
            "workflow_order": ["Data Engineer", "Data Transformation Specialist", "Data Quality Analyst"],
            "data_requirements": {
                "source_tables": ["source_data"],
                "target_tables": ["target_data"],
                "transformations": ["data_cleansing", "format_standardization", "quality_validation"]
            }
        }

def create_agents_from_analysis(analysis):
    """Create Agent objects from the LLM analysis"""
    print("👥 Creating AI agents based on analysis...")
    
    agents = []
    for agent_spec in analysis["required_agents"]:
        # Create LLM for this agent
        agent_llm = LLM(model="llama-3.2-11b-vision-preview", temperature=0.1)
        
        # Create Agent object
        agent = Agent(
            role=agent_spec["role"],
            job=agent_spec["job"],
            llm=agent_llm,
            sops=agent_spec["sops"],
            systems=["PostgreSQL", "MCPBridge"],
            tools=[{"name": tool, "hosted_by": "mcp"} for tool in agent_spec["tools"]],
            input_keys=["source_data", "target_schema"],
            output_key=f"{agent_spec['role'].lower().replace(' ', '_')}_results"
        )
        agents.append(agent)
        print(f"✅ Created agent: {agent_spec['role']}")
    
    return agents

def create_department_from_analysis(analysis, agents):
    """Create Department object from the LLM analysis"""
    print("🏢 Creating AI department...")
    
    department = Department(
        name=f"AI Team for {analysis['problem_type'].replace('_', ' ').title()}",
        mission=f"Solve the data engineering problem: {analysis['problem_type']}",
        agents=agents,
        workflow_order=analysis["workflow_order"],
        dependencies=["PostgreSQL", "MCPBridge"],
        execution_policy={
            "retry_on_fail": True,
            "max_retries": 3,
            "halt_on_validation_error": False,
            "timeout_seconds": 300
        },
        context={
            "problem_type": analysis["problem_type"],
            "data_requirements": analysis["data_requirements"]
        }
    )
    
    print("✅ AI department created successfully")
    return department

def setup_demo_data(analysis):
    """Setup demo data based on the analysis"""
    print("🗄️ Setting up demo data...")
    
    mcp_url = "http://localhost:8081"
    
    # Create source table
    create_source_sql = """
    CREATE TABLE IF NOT EXISTS source_data (
        id SERIAL PRIMARY KEY,
        customer_name VARCHAR(100),
        product_name VARCHAR(100),
        quantity INTEGER,
        unit_price DECIMAL(10,2),
        order_date DATE,
        region VARCHAR(50),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    
    # Insert sample data
    insert_data_sql = """
    INSERT INTO source_data (customer_name, product_name, quantity, unit_price, order_date, region) VALUES
    ('John Smith', 'Laptop', 1, 1200.00, '2024-01-15', 'North'),
    ('Sarah Johnson', 'Mouse', 2, 25.50, '2024-01-16', 'South'),
    ('Mike Davis', 'Keyboard', 1, 75.00, '2024-01-17', 'East'),
    ('Lisa Wilson', 'Monitor', 1, 300.00, '2024-01-18', 'West'),
    ('David Brown', 'Headphones', 3, 45.00, '2024-01-19', 'North');
    """
    
    # Create target table
    create_target_sql = """
    CREATE TABLE IF NOT EXISTS target_data (
        id SERIAL PRIMARY KEY,
        customer_name VARCHAR(100),
        product_name VARCHAR(100),
        total_amount DECIMAL(10,2),
        order_date DATE,
        region VARCHAR(50),
        processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    
    sql_statements = [create_source_sql, insert_data_sql, create_target_sql]
    
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
    
    print("✅ Demo data setup complete")

def execute_workflow(department):
    """Execute the generated workflow"""
    print("🚀 Executing AI workflow...")
    
    try:
        # Create execution engine
        execution_engine = ExecutionEngine()
        
        # Execute the department
        result = execution_engine.execute(department)
        
        print("✅ Workflow execution completed")
        return result
        
    except Exception as e:
        print(f"❌ Error executing workflow: {e}")
        return None

def show_results():
    """Show the results of the workflow"""
    print("\n📊 Workflow Results:")
    print("-" * 50)
    
    mcp_url = "http://localhost:8081"
    
    # Show source data
    print("\n📥 Source Data:")
    try:
        response = requests.post(f"{mcp_url}/execute_tool", json={
            "tool_name": "SQLExecutor",
            "params": {"sql_query": "SELECT * FROM source_data ORDER BY id LIMIT 5;"}
        }, headers={
            "X-Bridge-Secret": "test-secret-for-development",
            "Content-Type": "application/json"
        }, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success") and result.get("results", {}).get("data"):
                data = result["results"]["data"]
                for row in data:
                    print(f"  {row}")
        else:
            print("  ❌ Could not fetch source data")
    except Exception as e:
        print(f"  ❌ Error fetching source data: {e}")
    
    # Show target data
    print("\n📤 Target Data:")
    try:
        response = requests.post(f"{mcp_url}/execute_tool", json={
            "tool_name": "SQLExecutor",
            "params": {"sql_query": "SELECT * FROM target_data ORDER BY id LIMIT 5;"}
        }, headers={
            "X-Bridge-Secret": "test-secret-for-development",
            "Content-Type": "application/json"
        }, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success") and result.get("results", {}).get("data"):
                data = result["results"]["data"]
                for row in data:
                    print(f"  {row}")
        else:
            print("  ❌ Could not fetch target data")
    except Exception as e:
        print(f"  ❌ Error fetching target data: {e}")

def cleanup_demo_tables():
    """Clean up demo tables"""
    print("🧹 Cleaning up demo tables...")
    
    cleanup_sql = """
    DROP TABLE IF EXISTS target_data CASCADE;
    DROP TABLE IF EXISTS source_data CASCADE;
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

def main():
    """Main function to run the AI Job Portal demo"""
    
    # The job posting from the user
    job_posting = """
    We're looking for a data engineer to build a simple demo that mirrors a common enterprise workflow—specifically, connecting a source table to a target table with appropriate data transformations and cleansing. Ideally, the demo should showcase data flowing through a Medallion architecture (bronze → silver → gold), but we're also open to alternate workflows that are representative of tasks performed by data stewards, analysts, or scientists. The goal is to clearly illustrate how structured data is processed and modeled in a realistic scenario.
    """
    
    print("=" * 80)
    print("🤖 AI JOB PORTAL DEMO")
    print("=" * 80)
    print()
    print("📋 JOB POSTING:")
    print(job_posting)
    print()
    print("=" * 80)
    print()
    
    try:
        # Step 1: Analyze the job posting
        analysis = analyze_job_posting(job_posting)
        if not analysis:
            print("❌ Failed to analyze job posting")
            return False
        
        print(f"🎯 Problem Type: {analysis['problem_type']}")
        print(f"👥 Required Agents: {len(analysis['required_agents'])}")
        print(f"🔄 Workflow Steps: {len(analysis['workflow_order'])}")
        print()
        
        # Step 2: Create agents
        agents = create_agents_from_analysis(analysis)
        
        # Step 3: Create department
        department = create_department_from_analysis(analysis, agents)
        
        # Step 4: Setup demo data
        cleanup_demo_tables()  # Clean up any existing data
        setup_demo_data(analysis)
        
        # Step 5: Execute workflow
        result = execute_workflow(department)
        
        # Step 6: Show results
        show_results()
        
        # Display final summary
        print("\n" + "=" * 80)
        print("🎉 AI JOB PORTAL WORKFLOW COMPLETED!")
        print("=" * 80)
        print()
        print("📊 SUMMARY:")
        print(f"   • Job Posted: {analysis['problem_type']}")
        print(f"   • AI Team Created: {len(agents)} agents")
        print(f"   • Workflow Executed: {len(analysis['workflow_order'])} steps")
        print("   • Result: Automated data engineering solution")
        print()
        print("🔍 NEXT STEPS:")
        print("   • Check database: docker exec -it memra-ops_postgres_1 psql -U postgres -d local_workflow")
        print("   • View source: SELECT * FROM source_data;")
        print("   • View target: SELECT * FROM target_data;")
        print()
        print("🧹 CLEANUP:")
        print("   • Run cleanup: python memra/demos/ai_job_portal/cleanup_demo.py")
        print("=" * 80)
        
        return True
        
    except Exception as e:
        print(f"❌ Error in AI Job Portal workflow: {e}")
        return False

if __name__ == "__main__":
    main() 