#!/usr/bin/env python3
"""
Test script to verify GitHub token authentication
"""

import os
import requests
import urllib3

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def test_github_token():
    """Test GitHub token against both public and internal GitHub instances"""
    
    # Load token from environment
    token = os.getenv('GITHUB_TOKEN', '')
    
    if not token:
        print("❌ ERROR: GITHUB_TOKEN environment variable is not set")
        print("\nTo set it:")
        print("  export GITHUB_TOKEN='your_token_here'")
        print("\nOr add to .env file:")
        print("  GITHUB_TOKEN=your_token_here")
        return False
    
    print(f"✓ GitHub token found (length: {len(token)})")
    print(f"  Preview: {token[:4]}...{token[-4:] if len(token) > 8 else '***'}\n")
    
    # Test headers
    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    
    # Test 1: Public GitHub (if accessible)
    print("=" * 60)
    print("Test 1: Public GitHub API")
    print("=" * 60)
    try:
        response = requests.get(
            'https://api.github.com/user',
            headers=headers,
            timeout=10,
            verify=False
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            user_data = response.json()
            print(f"✓ SUCCESS: Authenticated as {user_data.get('login', 'unknown')}")
        elif response.status_code == 401:
            print(f"❌ FAILED: 401 Unauthorized")
            print(f"Response: {response.text}")
        else:
            print(f"⚠ Unexpected status: {response.text}")
    except Exception as e:
        print(f"⚠ Error: {e}")
    
    print()
    
    # Test 2: Internal HSBC GitHub Enterprise
    print("=" * 60)
    print("Test 2: Internal HSBC GitHub Enterprise")
    print("=" * 60)
    
    # Test with a known repo from GCDU YAML
    test_repo = "GCDU-Repository/gdt-mds-gcdu-101-acct-srch-pa"
    api_url = f"https://alm-github.systems.uk.hsbc/api/v3/repos/{test_repo}"
    
    print(f"Testing repo: {test_repo}")
    print(f"API URL: {api_url}\n")
    
    try:
        response = requests.get(
            api_url,
            headers=headers,
            timeout=10,
            verify=False
        )
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            repo_data = response.json()
            print(f"✓ SUCCESS: Repo found")
            print(f"  Name: {repo_data.get('name', 'unknown')}")
            print(f"  Full name: {repo_data.get('full_name', 'unknown')}")
            print(f"  Default branch: {repo_data.get('default_branch', 'unknown')}")
            
            # Test branches endpoint
            print(f"\nTesting branches endpoint...")
            branches_resp = requests.get(
                f"{api_url}/branches",
                headers=headers,
                timeout=10,
                verify=False
            )
            print(f"Branches status: {branches_resp.status_code}")
            if branches_resp.status_code == 200:
                branches = branches_resp.json()
                print(f"✓ Found {len(branches)} branches")
                for branch in branches[:3]:
                    print(f"  - {branch['name']}")
            else:
                print(f"❌ Branches failed: {branches_resp.text}")
                
        elif response.status_code == 401:
            print(f"❌ FAILED: 401 Unauthorized")
            print(f"\nPossible issues:")
            print(f"  1. Token is for public GitHub, not internal HSBC instance")
            print(f"  2. Token doesn't have 'repo' scope")
            print(f"  3. Token is expired or invalid")
            print(f"\nResponse: {response.text}")
            
        elif response.status_code == 404:
            print(f"⚠ Repository not found (404)")
            print(f"  This might mean:")
            print(f"  - Token is valid but repo doesn't exist")
            print(f"  - Token doesn't have access to this repo")
            print(f"  - Repo path is incorrect")
            
        else:
            print(f"⚠ Unexpected status: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"⚠ Error: {e}")
    
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    print("\nIf you see 401 errors:")
    print("1. Make sure you're using a token from: https://alm-github.systems.uk.hsbc/settings/tokens")
    print("2. Token must have 'repo' scope (full control of private repositories)")
    print("3. Token must be for the INTERNAL GitHub instance, not public GitHub")
    print("\nTo generate a new token:")
    print("  1. Go to: https://alm-github.systems.uk.hsbc/settings/tokens")
    print("  2. Click 'Generate new token'")
    print("  3. Select 'repo' scope")
    print("  4. Copy the token and set it in .env file")

if __name__ == "__main__":
    test_github_token()
