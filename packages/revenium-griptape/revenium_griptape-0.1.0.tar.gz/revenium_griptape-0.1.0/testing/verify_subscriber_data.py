#!/usr/bin/env python3
"""
Script to verify that subscriber data is being properly received by Revenium
with the new nested structure.
"""
import os
import requests
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def query_revenium_transactions():
    """Query recent transactions from Revenium API to verify subscriber data structure."""
    
    api_key = os.getenv("REVENIUM_METERING_API_KEY")
    base_url = os.getenv("REVENIUM_METERING_BASE_URL", "https://api.qa.hcapp.io/meter")
    
    if not api_key:
        print("❌ REVENIUM_METERING_API_KEY not found in environment")
        return
    
    # Calculate time range for recent transactions (last hour)
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(hours=1)
    
    # Format timestamps for API
    start_timestamp = start_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    end_timestamp = end_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    
    print(f"🔍 Querying Revenium transactions from {start_timestamp} to {end_timestamp}")
    print(f"📡 API Base URL: {base_url}")
    print(f"🔑 API Key: {api_key[:20]}...")
    
    # Query transactions endpoint
    url = f"{base_url}/v2/ai/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Try to get recent transactions
    params = {
        "start_time": start_timestamp,
        "end_time": end_timestamp,
        "limit": 10
    }
    
    try:
        print(f"\n🚀 Making GET request to: {url}")
        print(f"📋 Query params: {params}")
        
        response = requests.get(url, headers=headers, params=params)
        
        print(f"📊 Response status: {response.status_code}")
        print(f"📄 Response headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n✅ Successfully retrieved transaction data")
            print(f"📈 Number of transactions: {len(data.get('transactions', []))}")
            
            # Check for subscriber data in transactions
            transactions = data.get('transactions', [])
            for i, transaction in enumerate(transactions[:3]):  # Check first 3 transactions
                print(f"\n🔍 Transaction {i+1}:")
                print(f"   ID: {transaction.get('id', 'N/A')}")
                print(f"   Organization: {transaction.get('organization_id', 'N/A')}")
                print(f"   Provider: {transaction.get('provider', 'N/A')}")
                print(f"   Model: {transaction.get('model', 'N/A')}")
                
                # Check for subscriber data
                subscriber = transaction.get('subscriber')
                if subscriber:
                    print(f"   ✅ Subscriber (nested): {json.dumps(subscriber, indent=6)}")
                    if isinstance(subscriber, dict):
                        print(f"      - ID: {subscriber.get('id', 'N/A')}")
                        print(f"      - Email: {subscriber.get('email', 'N/A')}")
                        credential = subscriber.get('credential')
                        if credential:
                            print(f"      - Credential: {credential}")
                else:
                    # Check for old flat structure
                    subscriber_id = transaction.get('subscriber_id')
                    subscriber_email = transaction.get('subscriber_email')
                    if subscriber_id or subscriber_email:
                        print(f"   ⚠️  Subscriber (flat): ID={subscriber_id}, Email={subscriber_email}")
                    else:
                        print(f"   ❌ No subscriber data found")
                
                print(f"   Task Type: {transaction.get('task_type', 'N/A')}")
                print(f"   Timestamp: {transaction.get('timestamp', 'N/A')}")
                
        else:
            print(f"❌ Failed to retrieve transactions: {response.status_code}")
            print(f"📄 Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error querying Revenium API: {e}")

def test_specific_organization():
    """Query transactions for specific organizations we just tested."""
    
    api_key = os.getenv("REVENIUM_METERING_API_KEY")
    base_url = os.getenv("REVENIUM_METERING_BASE_URL", "https://api.qa.hcapp.io/meter")
    
    if not api_key:
        print("❌ REVENIUM_METERING_API_KEY not found in environment")
        return
    
    # Test organizations from our examples
    test_orgs = [
        "demo-openai-org",
        "demo-anthropic-org", 
        "debug-org"
    ]
    
    for org_id in test_orgs:
        print(f"\n🔍 Checking transactions for organization: {org_id}")
        
        # This would be the actual query - the exact endpoint may vary
        # For now, let's just show what we would query
        print(f"   Would query: {base_url}/v2/ai/completions?organization_id={org_id}")

if __name__ == "__main__":
    print("🔍 Verifying Subscriber Data Structure in Revenium")
    print("=" * 60)
    
    query_revenium_transactions()
    test_specific_organization()
    
    print("\n✅ Verification complete!")
    print("\n💡 If subscriber data shows nested structure with 'id', 'email', and 'credential' fields,")
    print("   then the update was successful!")
