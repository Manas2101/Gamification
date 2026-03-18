"""
Test script to verify YAML registry integration with DataSight API
Tests the complete flow: YAML → Registry Loader → API Integration → Database
"""

import logging
import os
from datetime import datetime
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_registry_loader():
    """Test 1: Verify YAML registry loader works"""
    print("\n" + "="*60)
    print("TEST 1: Registry Loader")
    print("="*60)
    
    from registry_loader import RegistryLoader
    
    loader = RegistryLoader()
    apps = loader.load_all()
    
    print(f"✅ Loaded {len(apps)} apps from registry")
    
    for app in apps:
        print(f"\n  App: {app.app_name} (EIM: {app.eim})")
        print(f"    TeamBook Pods: {app.teambook_pods}")
        print(f"    TeamBook Level: {app.teambook_level}")
        print(f"    Stack: {app.stack}, Tier: {app.tier}")
        print(f"    CI: {app.ci_automated}, CD: {app.cd_automated}")
        print(f"    Rollback: {app.automated_rollback}, Zero-touch: {app.zero_touch_deployment}")
    
    return len(apps) > 0

def test_api_integration():
    """Test 2: Verify API integration (requires valid token)"""
    print("\n" + "="*60)
    print("TEST 2: API Integration")
    print("="*60)
    
    # Load token from environment
    from config import DATASIGHT_BEARER_TOKEN
    
    if not DATASIGHT_BEARER_TOKEN:
        print("⚠️  DATASIGHT_BEARER_TOKEN not configured in .env")
        print("   Skipping API test (configure token to test API calls)")
        return False
    
    from api_integration import MetricsCollector
    
    collector = MetricsCollector(DATASIGHT_BEARER_TOKEN)
    
    # Try to fetch metrics for current month
    week_date = datetime.now()
    
    print(f"  Attempting to fetch metrics for week: {week_date.strftime('%Y-%m-%d')}")
    
    try:
        metrics = collector.collect_weekly_metrics(week_date)
        print(f"✅ Successfully fetched metrics for {len(metrics)} apps")
        
        if metrics:
            sample = metrics[0]
            print(f"\n  Sample metrics for {sample.get('app_name', sample.get('pod_name'))}:")
            print(f"    RF: {sample.get('rf')}")
            print(f"    LTTD: {sample.get('lttd')}")
            print(f"    MTTR: {sample.get('mttr')}")
            print(f"    CFR: {sample.get('cfr')}")
        
        return True
    except Exception as e:
        print(f"❌ API call failed: {e}")
        return False

def test_database_storage():
    """Test 3: Verify database storage works"""
    print("\n" + "="*60)
    print("TEST 3: Database Storage")
    print("="*60)
    
    from database import MetricsDatabase
    
    # Use test database
    test_db_path = "test_metrics.db"
    
    # Clean up old test db
    if Path(test_db_path).exists():
        os.remove(test_db_path)
    
    db = MetricsDatabase(test_db_path)
    
    # Insert test pod
    db.upsert_pod(
        pod_id=9594666,
        pod_name="RDH",
        stack="java-spring",
        business_unit="Default",
        tier=2
    )
    
    # Insert test metrics
    test_metrics = {
        'pod_id': 9594666,
        'week_date': datetime.now(),
        'week_start': datetime.now(),
        'rf': 150,
        'lttd': 2.5,
        'ltdd_measurable': 0.95,
        'cfr': 0.08,
        'mttr': 1.2,
        'priv_access': 1,
        'ci': True,
        'cd': True,
        'iac': False,
        'rollback': True,
        'self_service': False,
        'cfr_reported': True,
        'automation_audited': True,
        'critical_data_present': True,
        'rf_score': 25,
        'flow_score': 20,
        'cfr_score': 4,
        'mttr_score': 4,
        'priv_score': 2,
        'automation_score': 15,
        'stability_score': 10,
        'dpi': 70,
        'data_quality_flags': ''
    }
    
    db.insert_weekly_metrics(test_metrics)
    
    # Verify retrieval
    latest = db.get_latest_metrics()
    
    if len(latest) > 0:
        print(f"✅ Successfully stored and retrieved metrics")
        print(f"   Pods in database: {len(latest)}")
        print(f"   Sample: {latest.iloc[0]['Team']} - DPI: {latest.iloc[0]['DPI']}")
        
        # Cleanup
        os.remove(test_db_path)
        return True
    else:
        print("❌ Failed to retrieve metrics from database")
        return False

def test_complete_flow():
    """Test 4: Complete end-to-end flow (requires valid token)"""
    print("\n" + "="*60)
    print("TEST 4: Complete Integration Flow")
    print("="*60)
    
    from config import DATASIGHT_BEARER_TOKEN
    
    if not DATASIGHT_BEARER_TOKEN:
        print("⚠️  DATASIGHT_BEARER_TOKEN not configured")
        print("   Skipping complete flow test")
        return False
    
    from data_fetcher import DataFetcher
    
    # Use test database
    test_db_path = "test_complete.db"
    
    # Clean up old test db
    if Path(test_db_path).exists():
        os.remove(test_db_path)
    
    try:
        fetcher = DataFetcher(DATASIGHT_BEARER_TOKEN, db_path=test_db_path)
        
        print("  Fetching current week data...")
        fetcher.refresh_current_week()
        
        # Get results
        latest = fetcher.get_latest_dashboard_data()
        
        print(f"✅ Complete flow successful!")
        print(f"   Apps processed: {len(latest)}")
        
        if len(latest) > 0:
            print(f"\n  Sample results:")
            for idx, row in latest.head(3).iterrows():
                print(f"    {row['Team']}: DPI={row['DPI']:.1f}, RF={row['RF']}, LTDD={row['LTDD']}")
        
        # Cleanup
        os.remove(test_db_path)
        return True
        
    except Exception as e:
        print(f"❌ Complete flow failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("YAML REGISTRY INTEGRATION TEST SUITE")
    print("="*60)
    
    results = {
        'Registry Loader': test_registry_loader(),
        'API Integration': test_api_integration(),
        'Database Storage': test_database_storage(),
        'Complete Flow': test_complete_flow()
    }
    
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {test_name}: {status}")
    
    total = len(results)
    passed = sum(results.values())
    
    print(f"\n  Total: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Integration is working correctly.")
    else:
        print("\n⚠️  Some tests failed. Check the output above for details.")

if __name__ == "__main__":
    main()
