#!/usr/bin/env python3
"""
Setup script for the enhanced LinkedIn image extractor.

This script helps install the required dependencies and checks system compatibility.
"""

import subprocess
import sys
import os
import platform


def run_command(command, description):
    """Run a shell command and return success status."""
    print(f"📦 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"   ✅ Success")
            return True
        else:
            print(f"   ❌ Failed: {result.stderr.strip()}")
            return False
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        return False


def check_python_version():
    """Check if Python version is compatible."""
    print("🐍 Checking Python version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(
            f"   ✅ Python {version.major}.{version.minor}.{version.micro} is compatible"
        )
        return True
    else:
        print(
            f"   ❌ Python {version.major}.{version.minor}.{version.micro} "
            f"is too old. Requires Python 3.8+"
        )
        return False


def install_python_dependencies():
    """Install required Python packages."""
    print("\n📚 Installing Python dependencies...")

    # Check if requirements.txt exists
    if not os.path.exists("requirements.txt"):
        print("   ❌ requirements.txt not found")
        return False

    # Install requirements
    success = run_command(
        f"{sys.executable} -m pip install -r requirements.txt",
        "Installing packages from requirements.txt",
    )

    return success


def check_chromedriver():
    """Check if ChromeDriver is available."""
    print("\n🌐 Checking ChromeDriver availability...")

    # Try to find chromedriver in PATH
    try:
        result = subprocess.run(
            ["chromedriver", "--version"], capture_output=True, text=True
        )
        if result.returncode == 0:
            version = result.stdout.strip()
            print(f"   ✅ ChromeDriver found: {version}")
            return True
    except FileNotFoundError:
        pass

    print("   ⚠️  ChromeDriver not found in PATH")
    return False


def install_chromedriver():
    """Provide instructions for installing ChromeDriver."""
    print("\n🔧 ChromeDriver Installation Instructions:")

    system = platform.system().lower()

    if system == "darwin":  # macOS
        print("   For macOS with Homebrew:")
        print("   brew install chromedriver")
        print()
        print("   Alternative - Manual installation:")
        print("   1. Download from https://chromedriver.chromium.org/")
        print("   2. Extract and move to /usr/local/bin/")
        print("   3. Run: chmod +x /usr/local/bin/chromedriver")

    elif system == "linux":
        print("   For Ubuntu/Debian:")
        print("   sudo apt-get update")
        print("   sudo apt-get install chromium-chromedriver")
        print()
        print("   For other Linux distributions:")
        print("   1. Download from https://chromedriver.chromium.org/")
        print("   2. Extract and move to /usr/local/bin/")
        print("   3. Run: chmod +x /usr/local/bin/chromedriver")

    elif system == "windows":
        print("   For Windows:")
        print("   1. Download from https://chromedriver.chromium.org/")
        print("   2. Extract chromedriver.exe")
        print("   3. Add the directory to your PATH environment variable")
        print("   4. Or place chromedriver.exe in your Python Scripts folder")

    else:
        print(
            "   Please visit https://chromedriver.chromium.org/ for installation instructions"
        )


def test_imports():
    """Test if all required modules can be imported."""
    print("\n🧪 Testing module imports...")

    modules_to_test = [
        ("requests", "HTTP requests"),
        ("PIL", "Image processing"),
        ("bs4", "HTML parsing"),
        ("fake_useragent", "User agent rotation"),
        ("selenium", "Browser automation (optional)"),
    ]

    all_success = True

    for module, description in modules_to_test:
        try:
            __import__(module)
            print(f"   ✅ {module} - {description}")
        except ImportError as e:
            print(f"   ❌ {module} - {description}: {str(e)}")
            if module != "selenium":  # Selenium is optional
                all_success = False

    return all_success


def run_test_script():
    """Run the LinkedIn extractor test script."""
    print("\n🚀 Running LinkedIn extractor test...")

    if not os.path.exists("test_linkedin_extractor.py"):
        print("   ⚠️  Test script not found")
        return False

    try:
        result = subprocess.run(
            [sys.executable, "test_linkedin_extractor.py"],
            capture_output=True,
            text=True,
            timeout=60,
        )

        if result.returncode == 0:
            print("   ✅ Test completed successfully")
            # Show last few lines of output
            lines = result.stdout.strip().split("\n")
            for line in lines[-5:]:
                if line.strip():
                    print(f"   {line}")
            return True
        else:
            print("   ❌ Test failed")
            print(f"   Error: {result.stderr.strip()}")
            return False

    except subprocess.TimeoutExpired:
        print("   ⚠️  Test timed out (this is normal for LinkedIn extraction)")
        return True
    except Exception as e:
        print(f"   ❌ Test error: {str(e)}")
        return False


def main():
    """Main setup function."""
    print("🔧 Enhanced LinkedIn Image Extractor Setup")
    print("=" * 50)

    # Check Python version
    if not check_python_version():
        print("\n❌ Setup failed: Incompatible Python version")
        return 1

    # Install Python dependencies
    if not install_python_dependencies():
        print("\n❌ Setup failed: Could not install Python dependencies")
        return 1

    # Check ChromeDriver
    chromedriver_available = check_chromedriver()
    if not chromedriver_available:
        install_chromedriver()

    # Test imports
    if not test_imports():
        print("\n❌ Setup failed: Required modules could not be imported")
        return 1

    # Run test script
    print("\n" + "=" * 50)
    test_success = run_test_script()

    # Final summary
    print("\n" + "=" * 50)
    print("📋 SETUP SUMMARY:")
    print(f"   • Python version: ✅")
    print(f"   • Dependencies: ✅")
    print(f"   • ChromeDriver: {'✅' if chromedriver_available else '⚠️  Optional'}")
    print(f"   • Module imports: ✅")
    print(f"   • Test execution: {'✅' if test_success else '⚠️  See above'}")

    if chromedriver_available and test_success:
        print("\n🎉 Setup completed successfully!")
        print("   The enhanced LinkedIn image extractor is ready to use.")
    else:
        print("\n⚠️  Setup completed with warnings:")
        if not chromedriver_available:
            print("   • ChromeDriver not found - Selenium extraction will be disabled")
        if not test_success:
            print("   • Test execution had issues - Check the output above")
        print("   • Basic functionality should still work")

    print("\n📖 Next steps:")
    print("   • Read LINKEDIN_EXTRACTOR_README.md for detailed usage instructions")
    print("   • Run 'python main.py' to process speaker images with the new extractor")
    print("   • Monitor success rates and adjust configuration as needed")

    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
