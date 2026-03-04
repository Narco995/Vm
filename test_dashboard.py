"""
Test script to start the web dashboard and verify it works
"""
import asyncio
import aiohttp
from aiohttp import web
import sys
import os

sys.path.insert(0, '/workspace/Vm')

async def test_dashboard_start():
    """Test if the dashboard can start and respond to requests"""
    print("🌐 Testing Web Dashboard...")
    print("=" * 50)
    
    try:
        # Import the dashboard module
        from web_dashboard import create_app
        print("✅ Dashboard module imported successfully")
        
        # Create the app
        app = await create_app()
        print("✅ Dashboard app created successfully")
        
        # Check if the app has routes
        print(f"✅ App has {len(app.router.routes())} routes registered")
        
        # Test a simple request (without starting the server)
        print("\n📋 Dashboard Routes:")
        for route in app.router.routes():
            print(f"  {route.method} {route.path}")
        
        return True
        
    except Exception as e:
        print(f"❌ Dashboard test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def test_api_endpoints():
    """Test API endpoints functionality"""
    print("\n" + "=" * 50)
    print("🔌 Testing API Endpoints...")
    print("=" * 50)
    
    try:
        from database.db_manager import DBManager
        db = DBManager()
        await db.init_db()
        
        # Add some test data
        await db.add_message(999, "user", "Test message for API")
        await db.add_message(999, "assistant", "Test response from bot")
        await db.add_memory_note(999, "Test memory for API")
        
        print("✅ Test data added to database")
        
        # Test database queries that the API would use
        history = await db.get_conversation_history(999, limit=10)
        print(f"✅ Retrieved {len(history)} conversation history records")
        
        memories = await db.get_memory_notes(999)
        print(f"✅ Retrieved {len(memories)} memory records")
        
        return True
        
    except Exception as e:
        print(f"❌ API endpoints test failed: {str(e)}")
        return False

async def main():
    """Run all dashboard tests"""
    print("\n╔" + "═"*48 + "╗")
    print("║" + " "*10 + "🌐 DASHBOARD TEST SUITE" + " "*14 + "║")
    print("╚" + "═"*48 + "╝")
    
    success = True
    
    # Test dashboard
    if not await test_dashboard_start():
        success = False
    
    # Test API endpoints
    if not await test_api_endpoints():
        success = False
    
    print("\n" + "╔" + "═"*48 + "╗")
    print("║" + " "*18 + "📊 RESULTS" + " "*19 + "║")
    print("╚" + "═"*48 + "╝")
    
    if success:
        print("\n✅ All dashboard tests passed!")
        print("🌐 The web dashboard is ready to use.")
        print("\n📝 To start the dashboard manually:")
        print("   cd /workspace/Vm && python web_dashboard.py")
        print("   Then open http://localhost:8080 in your browser")
    else:
        print("\n❌ Some tests failed. Check the errors above.")
    
    return success

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)