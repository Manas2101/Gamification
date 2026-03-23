#!/usr/bin/env python3
"""
Debug script to test exact token and URL configuration
"""

import os
import requests
import urllib3

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def test_token_detailed():
    """Detailed token testing with exact reference code format"""
    
    print("=" * 80)
    print("GITHUB TOKEN DEBUG TEST")
    print("=" * 80)
    
    # Load token
    token = os.getenv('GITHUB_TOKEN', '')
    
    if not token:
        print("❌ GITHUB_TOKEN not set in environment")
        print("\nCheck:")
        print("  1. Is .env file in current directory?")
        print("  2. Did you export GITHUB_TOKEN in terminal?")
        print("  3. Run: echo $GITHUB_TOKEN")
        return
    
    print(f"\n✓ Token loaded")
    print(f"  Length: {len(token)}")
    print(f"  Preview: {token[:4]}...{token[-4:]}")
    print(f"  Starts with: {token[:4]}")
    
    # Check token format
    if not token.startswith('ghp_') and not token.startswith('gho_') and not token.startswith('github_pat_'):
        print(f"\n⚠️  WARNING: Token doesn't start with expected prefix (ghp_, gho_, github_pat_)")
        print(f"  Your token starts with: {token[:10]}")
    
    # Test with exact reference code format
    print("\n" + "=" * 80)
    print("TEST 1: Using Reference Code Format")
    print("=" * 80)
    
    base_url = "https://alm-github.systems.uk.hsbc/api/v3"
    test_org = "GCDU-Repository"
    test_repo = "gdt-mds-gcdu-101-acct-srch-pa"
    
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "dpi-gamification-hygiene-checker",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    
    print(f"\nBase URL: {base_url}")
    print(f"Testing repo: {test_org}/{test_repo}")
    print(f"\nHeaders:")
    for key, value in headers.items():
        if key == 'Authorization':
            print(f"  {key}: token {token[:4]}...{token[-4:]}")
        else:
            print(f"  {key}: {value}")
    
    # Test 1: Get repo info
    print(f"\n--- Test 1a: Get Repo Info ---")
    url = f"{base_url}/repos/{test_org}/{test_repo}"
    print(f"URL: {url}")
    
    try:
        resp = requests.get(url, headers=headers, verify=False, timeout=30)
        print(f"Status: {resp.status_code}")
        
        if resp.status_code == 200:
            data = resp.json()
            print(f"✓ SUCCESS!")
            print(f"  Repo name: {data.get('name')}")
            print(f"  Full name: {data.get('full_name')}")
            print(f"  Default branch: {data.get('default_branch')}")
            print(f"  Private: {data.get('private')}")
        elif resp.status_code == 401:
            print(f"❌ 401 UNAUTHORIZED")
            print(f"\nResponse headers:")
            for key, value in resp.headers.items():
                print(f"  {key}: {value}")
            print(f"\nResponse body:")
            print(f"  {resp.text}")
            
            print(f"\n🔍 Debugging steps:")
            print(f"  1. Verify token is from: https://alm-github.systems.uk.hsbc/settings/tokens")
            print(f"  2. Token must have 'repo' scope checked")
            print(f"  3. Token must not be expired")
            print(f"  4. Try regenerating token with same scopes")
            
        elif resp.status_code == 404:
            print(f"❌ 404 NOT FOUND")
            print(f"  Either:")
            print(f"    - Token is valid but repo doesn't exist")
            print(f"    - Token doesn't have access to this repo")
            print(f"    - Org/repo name is wrong")
        else:
            print(f"❌ Unexpected status: {resp.status_code}")
            print(f"Response: {resp.text}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    # Test 2: List branches
    print(f"\n--- Test 1b: List Branches ---")
    url = f"{base_url}/repos/{test_org}/{test_repo}/branches"
    print(f"URL: {url}")
    
    try:
        resp = requests.get(url, headers=headers, verify=False, timeout=30)
        print(f"Status: {resp.status_code}")
        
        if resp.status_code == 200:
            branches = resp.json()
            print(f"✓ SUCCESS! Found {len(branches)} branches")
            for branch in branches[:5]:
                print(f"  - {branch['name']}")
        else:
            print(f"❌ Failed: {resp.status_code}")
            print(f"Response: {resp.text[:200]}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    # Test 3: Test authenticated user endpoint
    print(f"\n--- Test 2: Get Authenticated User ---")
    url = f"{base_url}/user"
    print(f"URL: {url}")
    
    try:
        resp = requests.get(url, headers=headers, verify=False, timeout=30)
        print(f"Status: {resp.status_code}")
        
        if resp.status_code == 200:
            user = resp.json()
            print(f"✓ SUCCESS! Authenticated as:")
            print(f"  Login: {user.get('login')}")
            print(f"  Name: {user.get('name')}")
            print(f"  Email: {user.get('email')}")
        else:
            print(f"❌ Failed: {resp.status_code}")
            print(f"Response: {resp.text[:200]}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print("\nIf all tests failed with 401:")
    print("  → Token is invalid or doesn't have correct permissions")
    print("  → Generate new token from: https://alm-github.systems.uk.hsbc/settings/tokens")
    print("  → Required scopes: 'repo' (full control of private repositories)")
    print("\nIf repo test failed but user test passed:")
    print("  → Token is valid but doesn't have access to that specific repo")
    print("  → Check repo name/org is correct")
    print("\nIf all tests passed:")
    print("  → Token is working! Check your code's token loading logic")

if __name__ == "__main__":
    test_token_detailed()
