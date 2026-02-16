"""
Automated test script for logging and error handling.

This script tests:
1. Logger initialization
2. Log file creation
3. Error logging with stack traces
4. Error handler dialogs (simulated)
"""

import sys
import os
from pathlib import Path

# Add src to path
src_dir = Path(__file__).parent / "src"
sys.path.insert(0, str(src_dir))

from utils.logger import setup_logger, get_log_file_path
from utils.app_paths import get_logs_dir


def test_logger_initialization():
    """Test 1: Logger initialization"""
    print("=" * 60)
    print("TEST 1: Logger Initialization")
    print("=" * 60)
    
    try:
        logger = setup_logger("test_logger")
        print("✅ Logger created successfully")
        print(f"   Logger name: {logger.name}")
        print(f"   Log level: {logger.level}")
        print(f"   Handlers: {len(logger.handlers)}")
        return True
    except Exception as e:
        print(f"❌ Logger initialization failed: {e}")
        return False


def test_log_file_creation():
    """Test 2: Log file creation"""
    print("\n" + "=" * 60)
    print("TEST 2: Log File Creation")
    print("=" * 60)
    
    try:
        log_file = get_log_file_path()
        logs_dir = get_logs_dir()
        
        print(f"✅ Logs directory: {logs_dir}")
        print(f"✅ Log file path: {log_file}")
        
        if log_file.exists():
            print(f"✅ Log file exists")
            print(f"   Size: {log_file.stat().st_size} bytes")
        else:
            print(f"⚠️  Log file doesn't exist yet (will be created on first log)")
        
        return True
    except Exception as e:
        print(f"❌ Log file check failed: {e}")
        return False


def test_logging_levels():
    """Test 3: Different log levels"""
    print("\n" + "=" * 60)
    print("TEST 3: Logging Different Levels")
    print("=" * 60)
    
    try:
        logger = setup_logger("test_levels")
        
        # Test different log levels
        logger.debug("This is a DEBUG message")
        print("✅ DEBUG message logged")
        
        logger.info("This is an INFO message")
        print("✅ INFO message logged")
        
        logger.warning("This is a WARNING message")
        print("✅ WARNING message logged")
        
        logger.error("This is an ERROR message")
        print("✅ ERROR message logged")
        
        logger.critical("This is a CRITICAL message")
        print("✅ CRITICAL message logged")
        
        return True
    except Exception as e:
        print(f"❌ Logging levels test failed: {e}")
        return False


def test_exception_logging():
    """Test 4: Exception logging with stack trace"""
    print("\n" + "=" * 60)
    print("TEST 4: Exception Logging with Stack Trace")
    print("=" * 60)
    
    try:
        logger = setup_logger("test_exceptions")
        
        # Trigger an exception
        try:
            # This will cause a division by zero error
            result = 1 / 0
        except Exception as e:
            logger.error(f"Caught exception: {e}", exc_info=True)
            print("✅ Exception logged with stack trace")
        
        # Trigger another exception
        try:
            # This will cause a key error
            test_dict = {"key1": "value1"}
            value = test_dict["nonexistent_key"]
        except Exception as e:
            logger.error(f"Caught KeyError: {e}", exc_info=True)
            print("✅ KeyError logged with stack trace")
        
        return True
    except Exception as e:
        print(f"❌ Exception logging test failed: {e}")
        return False


def test_log_file_content():
    """Test 5: Verify log file content"""
    print("\n" + "=" * 60)
    print("TEST 5: Log File Content Verification")
    print("=" * 60)
    
    try:
        log_file = get_log_file_path()
        
        if not log_file.exists():
            print("❌ Log file doesn't exist")
            return False
        
        # Read last 20 lines
        with open(log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            last_lines = lines[-20:] if len(lines) > 20 else lines
        
        print(f"✅ Log file contains {len(lines)} lines")
        print(f"\nLast 10 log entries:")
        print("-" * 60)
        for line in last_lines[-10:]:
            print(line.rstrip())
        print("-" * 60)
        
        # Check for expected content
        content = ''.join(lines)
        checks = {
            "Timestamp": any("2026-" in line for line in lines),
            "Log levels": any("INFO" in content or "ERROR" in content),
            "Module names": any("test_" in content),
            "Stack traces": "Traceback" in content,
        }
        
        print(f"\nContent checks:")
        for check_name, passed in checks.items():
            status = "✅" if passed else "❌"
            print(f"  {status} {check_name}")
        
        return all(checks.values())
    except Exception as e:
        print(f"❌ Log file content check failed: {e}")
        return False


def test_error_handler_import():
    """Test 6: Error handler import"""
    print("\n" + "=" * 60)
    print("TEST 6: Error Handler Import")
    print("=" * 60)
    
    try:
        from utils.error_handler import show_error, show_info, show_warning
        print("✅ Error handler functions imported successfully")
        print("   - show_error")
        print("   - show_info")
        print("   - show_warning")
        return True
    except Exception as e:
        print(f"❌ Error handler import failed: {e}")
        return False


def run_all_tests():
    """Run all tests and report results"""
    print("\n" + "=" * 60)
    print("AUTOMATED LOGGING & ERROR HANDLING TESTS")
    print("=" * 60)
    print()
    
    tests = [
        ("Logger Initialization", test_logger_initialization),
        ("Log File Creation", test_log_file_creation),
        ("Logging Levels", test_logging_levels),
        ("Exception Logging", test_exception_logging),
        ("Log File Content", test_log_file_content),
        ("Error Handler Import", test_error_handler_import),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ Test '{test_name}' crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed!")
        print(f"\n📁 Log file location:")
        print(f"   {get_log_file_path()}")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    exit_code = run_all_tests()
    sys.exit(exit_code)
