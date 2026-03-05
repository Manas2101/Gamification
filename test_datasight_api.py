#!/usr/bin/env python3
"""
Test script to debug DataSight API calls
"""
import requests
import config
from datetime import datetime
import urllib3

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def test_datasight_apis():
    """Test all DataSight API endpoints"""
    
    print("=" * 80)
    print("DATASIGHT API TEST")
    print("=" * 80)
    
    if not config.DATASIGHT_BEARER_TOKEN:
        print("❌ DATASIGHT_BEARER_TOKEN not configured!")
        return
    
    print(f"✅ Token configured: {config.DATASIGHT_BEARER_TOKEN[:20]}...")
    
    headers = {
        'accept': 'text/plain',
        'Authorization': f'Bearer {config.DATASIGHT_BEARER_TOKEN}'
    }
    
    base_url = "https://datasight.global.hsbc"
    
    # Test with a sample pod ID (using first pod from your database)
    pod_id = 5488
    from_date = "2025-09"
    to_date = "2025-10"
    
    print(f"\nTest Parameters:")
    print(f"  Pod ID: {pod_id}")
    print(f"  From: {from_date}")
    print(f"  To: {to_date}")
    
    # 1. Test MTTR
    print("\n" + "-" * 80)
    print("1. Testing MTTR API")
    print("-" * 80)
    mttr_params = {
        'from': from_date,
        'to': to_date,
        'teambookIds': pod_id,
        'teambookLevel': 5,
        'page': 1,
        'size': 50
    }
    
    try:
        mttr_url = f"{base_url}/incident/metric/mttr/by-group/teambook/metric"
        print(f"URL: {mttr_url}")
        print(f"Params: {mttr_params}")
        
        response = requests.get(mttr_url, headers=headers, params=mttr_params, verify=False)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {data}")
            if 'data' in data and len(data['data']) > 0:
                mttr_value = data['data'][0].get('mttr')
                print(f"✅ MTTR found: {mttr_value}")
            else:
                print("⚠️ No MTTR data in response")
        else:
            print(f"❌ Error: {response.text}")
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    # 2. Test LTTD
    print("\n" + "-" * 80)
    print("2. Testing LTTD API")
    print("-" * 80)
    lttd_params = {
        'from': from_date,
        'to': to_date,
        'teambookIds': pod_id,
        'teambookLevel': 5,
        'page': 1,
        'size': 50
    }
    
    try:
        lttd_url = f"{base_url}/releases/metric/lttd/teambook/metric"
        print(f"URL: {lttd_url}")
        print(f"Params: {lttd_params}")
        
        response = requests.get(lttd_url, headers=headers, params=lttd_params, verify=False)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {data}")
            if 'data' in data and len(data['data']) > 0:
                lttd_value = data['data'][0].get('lttd')
                print(f"✅ LTTD found: {lttd_value}")
            else:
                print("⚠️ No LTTD data in response")
        else:
            print(f"❌ Error: {response.text}")
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    # 3. Test Release Frequency
    print("\n" + "-" * 80)
    print("3. Testing Release Frequency API")
    print("-" * 80)
    rf_params = {
        'from': from_date,
        'to': to_date,
        'teambookIds': pod_id,
        'teambookLevel': 5,
        'page': 1,
        'size': 50
    }
    
    try:
        rf_url = f"{base_url}/releases/metric/release-frequency/teambook/metric"
        print(f"URL: {rf_url}")
        print(f"Params: {rf_params}")
        
        response = requests.get(rf_url, headers=headers, params=rf_params, verify=False)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {data}")
            if 'data' in data and len(data['data']) > 0:
                rf_value = data['data'][0].get('releases')
                print(f"✅ RF found: {rf_value}")
            else:
                print("⚠️ No RF data in response")
        else:
            print(f"❌ Error: {response.text}")
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    # 4. Test CFR
    print("\n" + "-" * 80)
    print("4. Testing CFR API")
    print("-" * 80)
    cfr_params = {
        'from': from_date,
        'to': to_date,
        'teambookIds': pod_id,
        'teambookLevel': 5,
        'page': 1,
        'size': 50
    }
    
    try:
        cfr_url = f"{base_url}/releases/metric/cfr/teambook/metric"
        print(f"URL: {cfr_url}")
        print(f"Params: {cfr_params}")
        
        response = requests.get(cfr_url, headers=headers, params=cfr_params, verify=False)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {data}")
            if 'data' in data and len(data['data']) > 0:
                cfr_value = data['data'][0].get('change_failure_rate')
                print(f"✅ CFR found: {cfr_value}")
            else:
                print("⚠️ No CFR data in response")
        else:
            print(f"❌ Error: {response.text}")
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    print("\n" + "=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    test_datasight_apis()
