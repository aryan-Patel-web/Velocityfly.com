"""
Diagnostic Script to Test UnifiedDatabaseManager Attributes
Save this as: diagnostic_test.py
Run: python diagnostic_test.py
"""

def test_database_manager():
    print("=" * 60)
    print("🔍 DIAGNOSTIC TEST FOR UnifiedDatabaseManager")
    print("=" * 60)
    
    try:
        # Import the database manager
        print("\n📦 Attempting to import YTdatabase...")
        from YTdatabase import UnifiedDatabaseManager, get_database_manager
        
        print("✅ Successfully imported UnifiedDatabaseManager")
        
        # Create instance
        print("📦 Creating UnifiedDatabaseManager instance...")
        manager = UnifiedDatabaseManager()
        print("✅ Successfully created UnifiedDatabaseManager instance")
        
        # Check for methods
        methods_to_check = [
            'save_scrape_url',
            'get_scrape_url',
            'delete_scrape_url',
            'update_scrape_progress',
            'get_next_unprocessed_product',
            'get_automation_posts_count',
            'log_automation_post'
        ]
        
        print("\n📋 Checking for required methods:\n")
        
        all_methods_exist = True
        missing_methods = []
        
        for method_name in methods_to_check:
            has_method = hasattr(manager, method_name)
            status = "✅ EXISTS" if has_method else "❌ MISSING"
            print(f"   {status}: {method_name}")
            
            if not has_method:
                all_methods_exist = False
                missing_methods.append(method_name)
        
        print("\n" + "=" * 60)
        
        if all_methods_exist:
            print("✅ ALL METHODS EXIST - Database manager is correct!")
            print("=" * 60)
            
            # Test get_database_manager function
            print("\n🧪 Testing get_database_manager() function...")
            global_manager = get_database_manager()
            if hasattr(global_manager, 'save_scrape_url'):
                print("✅ Global instance also has the methods!")
            else:
                print("❌ Global instance is missing methods!")
            
            print("\n" + "=" * 60)
            print("✅ DIAGNOSTIC COMPLETE - Everything looks good!")
            print("=" * 60)
            print("\n💡 Your YTdatabase.py file is correct.")
            print("   If you're still getting errors, the issue is:")
            print("   1. Server cache - restart your server completely")
            print("   2. Wrong import location in your app")
            
            return True
        else:
            print("❌ SOME METHODS ARE MISSING!")
            print("=" * 60)
            print(f"\n❌ Missing methods: {', '.join(missing_methods)}")
            print("\n🔧 SOLUTION:")
            print("   1. Your YTdatabase.py file is NOT updated correctly")
            print("   2. Make sure you replaced the ENTIRE file content")
            print("   3. Check if UnifiedDatabaseManager class has these methods")
            print("   4. Look for this section in YTdatabase.py:")
            print("      # PRODUCT URL QUEUE MANAGEMENT (Delegate to YouTube manager)")
            print("   5. Re-run this test after fixing")
            return False
            
    except ImportError as e:
        print(f"\n❌ IMPORT ERROR: {e}")
        print("\n🔧 SOLUTION:")
        print("   1. Make sure YTdatabase.py is in the current directory")
        print("   2. Check if the file name is exactly 'YTdatabase.py' (case-sensitive)")
        print("   3. Try running: dir YTdatabase.py  (to verify file exists)")
        return False
        
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        print(f"   Error type: {type(e).__name__}")
        import traceback
        print("\n📋 Full error trace:")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    import sys
    import os
    
    print(f"📁 Current directory: {os.getcwd()}")
    print(f"🐍 Python version: {sys.version}")
    print(f"📂 Python path: {sys.executable}\n")
    
    # Check if YTdatabase.py exists
    if os.path.exists("YTdatabase.py"):
        print("✅ YTdatabase.py found in current directory\n")
    else:
        print("❌ YTdatabase.py NOT FOUND in current directory!")
        print("   Please navigate to the directory containing YTdatabase.py")
        print("   Or copy this diagnostic_test.py to that directory\n")
        sys.exit(1)
    
    success = test_database_manager()
    
    if success:
        print("\n🎉 TEST PASSED!")
        sys.exit(0)
    else:
        print("\n❌ TEST FAILED - Please fix the issues above")
        sys.exit(1)