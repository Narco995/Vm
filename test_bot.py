"""
Comprehensive test script for the Telegram AI Bot
Tests all modules, services, and database functionality
"""
import sys
import os
import asyncio
import importlib

# Test results storage
test_results = {
    "passed": [],
    "failed": [],
    "warnings": []
}

def test_module_import(module_name, display_name=None):
    """Test if a module can be imported"""
    display_name = display_name or module_name
    try:
        importlib.import_module(module_name)
        test_results["passed"].append(f"✅ Import: {display_name}")
        return True
    except Exception as e:
        test_results["failed"].append(f"❌ Import: {display_name} - {str(e)[:50]}")
        return False

def test_config():
    """Test configuration loading"""
    print("\n" + "="*50)
    print("📋 Testing Configuration")
    print("="*50)
    
    try:
        from config import (
            TELEGRAM_BOT_TOKEN, OPENAI_API_KEY, GPT_MODEL,
            DATABASE_PATH, MAX_MEMORY_MESSAGES
        )
        DEBUG = os.getenv('DEBUG', 'false').lower() == 'true'
        print(f"  TELEGRAM_BOT_TOKEN: {'Set' if TELEGRAM_BOT_TOKEN else 'Not Set'}")
        print(f"  OPENAI_API_KEY: {'Set' if OPENAI_API_KEY else 'Not Set'}")
        print(f"  GPT_MODEL: {GPT_MODEL}")
        print(f"  DATABASE_PATH: {DATABASE_PATH}")
        print(f"  MAX_MEMORY_MESSAGES: {MAX_MEMORY_MESSAGES}")
        print(f"  DEBUG: {DEBUG}")
        test_results["passed"].append("✅ Config: All settings loaded")
        return True
    except Exception as e:
        test_results["failed"].append(f"❌ Config: {str(e)}")
        return False

async def test_database():
    """Test database initialization"""
    print("\n" + "="*50)
    print("🗄️ Testing Database")
    print("="*50)
    
    try:
        from database.db_manager import DBManager
        db = DBManager()
        await db.init_db()
        print("  Database initialized successfully")
        
        # Test basic operations
        test_user_id = 12345
        test_message = "Test message for database"
        
        # Test adding message
        await db.add_message(test_user_id, "user", test_message)
        print("  ✅ Add message: Success")
        
        # Test getting history
        history = await db.get_conversation_history(test_user_id, limit=5)
        print(f"  ✅ Get history: {len(history)} messages retrieved")
        
        # Test saving memory
        await db.add_memory_note(test_user_id, "Test memory note")
        print("  ✅ Save memory: Success")
        
        # Test getting memories
        memories = await db.get_memory_notes(test_user_id)
        print(f"  ✅ Get memories: {len(memories)} memories retrieved")
        
        test_results["passed"].append("✅ Database: All operations working")
        return True
    except Exception as e:
        test_results["failed"].append(f"❌ Database: {str(e)}")
        return False

def test_handlers():
    """Test all handler modules"""
    print("\n" + "="*50)
    print("🎯 Testing Handlers")
    print("="*50)
    
    handlers = [
        ("bot.handlers.command_handler", "Command Handler"),
        ("bot.handlers.message_handler", "Message Handler"),
        ("bot.handlers.voice_handler", "Voice Handler"),
        ("bot.handlers.image_handler", "Image Handler"),
        ("bot.handlers.file_handler", "File Handler"),
        ("bot.handlers.callback_handler", "Callback Handler"),
    ]
    
    for module, name in handlers:
        test_module_import(module, name)

def test_services():
    """Test all service modules"""
    print("\n" + "="*50)
    print("⚙️ Testing Services")
    print("="*50)
    
    services = [
        ("bot.services.ai_service", "AI Service"),
        ("bot.services.pdf_service", "PDF Service"),
        ("bot.services.document_service", "Document Service"),
        ("bot.services.code_service", "Code Service"),
        ("bot.services.research_service", "Research Service"),
        ("bot.services.data_service", "Data Service"),
        ("bot.services.automation_service", "Automation Service"),
        ("bot.services.file_service", "File Service"),
    ]
    
    for module, name in services:
        test_module_import(module, name)

def test_utils():
    """Test utility modules"""
    print("\n" + "="*50)
    print("🔧 Testing Utils")
    print("="*50)
    
    test_module_import("bot.utils.formatters", "Formatters")

def test_web_dashboard():
    """Test web dashboard module"""
    print("\n" + "="*50)
    print("🌐 Testing Web Dashboard")
    print("="*50)
    
    test_module_import("web_dashboard", "Web Dashboard")

def test_main():
    """Test main.py can be imported"""
    print("\n" + "="*50)
    print("🚀 Testing Main Application")
    print("="*50)
    
    # Don't actually run main, just test import
    test_module_import("config", "Config")
    test_module_import("database.db_manager", "DB Manager")

async def run_all_tests():
    """Run all tests"""
    print("\n" + "╔" + "═"*48 + "╗")
    print("║" + " "*10 + "🤖 BOT COMPREHENSIVE TEST SUITE" + " "*10 + "║")
    print("╚" + "═"*48 + "╝")
    
    # Test core dependencies
    print("\n" + "="*50)
    print("📦 Testing Core Dependencies")
    print("="*50)
    
    core_deps = [
        "telegram", "openai", "mistralai", "fpdf", "docx",
        "pdfplumber", "pandas", "apscheduler", "aiohttp",
        "bs4", "dotenv", "aiosqlite", "PIL", "openpyxl", "httpx"
    ]
    
    for dep in core_deps:
        test_module_import(dep, dep.upper())
    
    # Run all tests
    test_config()
    await test_database()
    test_handlers()
    test_services()
    test_utils()
    test_web_dashboard()
    
    # Print summary
    print("\n" + "╔" + "═"*48 + "╗")
    print("║" + " "*15 + "📊 TEST SUMMARY" + " "*17 + "║")
    print("╚" + "═"*48 + "╝")
    
    print(f"\n✅ Passed: {len(test_results['passed'])}")
    print(f"❌ Failed: {len(test_results['failed'])}")
    print(f"⚠️  Warnings: {len(test_results['warnings'])}")
    
    if test_results["failed"]:
        print("\n❌ Failed Tests:")
        for fail in test_results["failed"]:
            print(f"  {fail}")
    
    if test_results["warnings"]:
        print("\n⚠️  Warnings:")
        for warn in test_results["warnings"]:
            print(f"  {warn}")
    
    # Calculate success rate
    total = len(test_results["passed"]) + len(test_results["failed"])
    if total > 0:
        success_rate = (len(test_results["passed"]) / total) * 100
        print(f"\n📈 Success Rate: {success_rate:.1f}%")
    
    return len(test_results["failed"]) == 0

if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)