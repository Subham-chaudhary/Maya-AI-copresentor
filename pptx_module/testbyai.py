import os
import json
import time
import sys
from datetime import datetime

# Try to import colorama for beautiful output, fallback if not present
try:
    from colorama import init, Fore, Style, Back
    init(autoreset=True)
    HAS_COLOR = True
except ImportError:
    HAS_COLOR = False
    class MockColor:
        def __getattr__(self, name): return ""
    Fore = Style = Back = MockColor()

# Import user modules
# NOTE: Ensure parser.py, controller.py, and create.py are in the same directory
try:
    from parser import PPTParser
    from controller import PPTController
    from create import PPTCreator
except ImportError as e:
    print(f"CRITICAL ERROR: Could not import your modules. {e}")
    sys.exit(1)

# --- Configuration ---
TEST_FILE_NAME = "test.pptx"
JSON_OUTPUT_NAME = "test.json"

# --- Styling and Logger Utilities ---
class TestRunner:
    def __init__(self):
        self.tests_run = 0
        self.tests_passed = 0
        self.tests_failed = 0
        self.start_time = time.time()
        self.step_count = 1

    def print_banner(self):
        print("\n" + Fore.CYAN + Style.BRIGHT + "="*60)
        print(Fore.CYAN + Style.BRIGHT + f"  PPT MODULE AUTOMATED TEST SUITE")
        print(Fore.CYAN + f"  Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(Fore.CYAN + Style.BRIGHT + "="*60 + "\n")

    def log_section(self, title):
        print(Fore.MAGENTA + Style.BRIGHT + f"\n[{self.step_count}] {title.upper()}")
        print(Fore.MAGENTA + "-"*60)
        self.step_count += 1

    def log_info(self, message):
        print(Fore.BLUE + "  ℹ " + Fore.WHITE + message)

    def log_success(self, message):
        print(Fore.GREEN + Style.BRIGHT + "  ✔ PASS: " + Fore.GREEN + message)
        self.tests_passed += 1
        self.tests_run += 1

    def log_fail(self, message, error=None):
        print(Fore.RED + Style.BRIGHT + "  ✘ FAIL: " + Fore.RED + message)
        if error:
            print(Fore.RED + f"    Error Details: {error}")
        self.tests_failed += 1
        self.tests_run += 1

    def countdown(self, seconds, message="Waiting"):
        """Displays a visual progress bar/countdown"""
        for i in range(seconds, 0, -1):
            sys.stdout.write(f"\r  ⏳ {message}... {i}s ")
            sys.stdout.flush()
            time.sleep(1)
        sys.stdout.write(f"\r  ✨ {message}... Done!   \n")

    def print_summary(self):
        duration = time.time() - self.start_time
        print("\n" + Fore.CYAN + Style.BRIGHT + "="*60)
        print(Fore.CYAN + Style.BRIGHT + "  TEST SUMMARY")
        print(Fore.CYAN + Style.BRIGHT + "="*60)
        
        print(f"  Total Steps: {self.tests_run}")
        
        # Color coding the final results
        if self.tests_failed == 0:
            status_color = Fore.GREEN
            status_text = "ALL SYSTEM GO"
        else:
            status_color = Fore.RED
            status_text = "ERRORS DETECTED"

        print(status_color + f"  Passed:      {self.tests_passed}")
        print(status_color + f"  Failed:      {self.tests_failed}")
        print(Fore.WHITE +   f"  Duration:    {duration:.2f} seconds")
        print(Fore.CYAN +    f"  Status:      " + status_color + Style.BRIGHT + status_text)
        print(Fore.CYAN + Style.BRIGHT + "="*60 + "\n")

# --- Helper for user input ---
def _get_user_choice(prompt):
    """
    Prompts the user for a 'y' or 'n' choice and returns the validated input.
    """
    while True:
        choice = input(Fore.YELLOW + Style.BRIGHT + f"\n  ❓ {prompt} (y/n): ").lower().strip()
        if choice in ['y', 'n']:
            return choice
        else:
            print(Fore.RED + "  Invalid input. Please enter 'y' or 'n'.")

# --- Main Test Execution ---

def main():
    runner = TestRunner()
    runner.print_banner()

    # Pre-check for existing files and user interaction
    files_to_check = [TEST_FILE_NAME, JSON_OUTPUT_NAME]
    existing_files = [f for f in files_to_check if os.path.exists(f)]

    skip_creation_test = False # Initialize flag

    if existing_files:
        runner.log_info(Fore.YELLOW + Style.BRIGHT + "Pre-existing test files detected:")
        for f in existing_files:
            runner.log_info(f"  - {f}")
        
        choice = _get_user_choice("Do you want to delete these files to ensure a clean test environment?")
        
        if choice == 'y':
            runner.log_info("Deleting pre-existing files...")
            for f in existing_files:
                try:
                    os.remove(f)
                    runner.log_info(f"  Deleted '{f}'.")
                except OSError as e:
                    runner.log_fail(f"Error deleting '{f}'. Cannot proceed cleanly.", e)
                    sys.exit(1) # Critical error, cannot proceed cleanly
            runner.log_info("Files deleted. Proceeding with full test suite.")
        else: # User chose 'n'
            runner.log_info(Fore.YELLOW + "User chose to keep existing files. Skipping the PPT creation test.")
            runner.log_info("Proceeding with parsing and controller tests using the existing files.")
            skip_creation_test = True

    # 1. PPT Creation Test
    if not skip_creation_test:
        runner.log_section("Testing PPT Creation")
        absolute_path = os.path.abspath(TEST_FILE_NAME)
        
        try:
            runner.log_info(f"Initializing PPTCreator with {TEST_FILE_NAME}...")
            creator = PPTCreator(TEST_FILE_NAME)
            creator.main()
            
            if os.path.exists(TEST_FILE_NAME):
                runner.log_success(f"File '{TEST_FILE_NAME}' created successfully.")
            else:
                runner.log_fail(f"File '{TEST_FILE_NAME}' was not found after creation.")
                return # Exit if creation fails
                
        except Exception as e:
            runner.log_fail("Exception during PPT Creation", e)
            return
    else:
        runner.log_section("PPT Creation Skipped")
        absolute_path = os.path.abspath(TEST_FILE_NAME) # Still need this for later steps
        runner.log_info(f"Using pre-existing file '{TEST_FILE_NAME}' for subsequent tests.")


    # 2. PPT Parsing Test
    runner.log_section("Testing PPT Parsing")
    
    try:
        runner.log_info(f"Initializing PPTParser on {absolute_path}...")
        parser = PPTParser(absolute_path)
        data = parser.parse()
        
        if data:
            runner.log_success("Data parsed successfully (Data is not empty).")
        else:
            runner.log_fail("Parser returned empty data.")

        # Save JSON
        json_filename = os.path.splitext(os.path.basename(TEST_FILE_NAME))[0] + ".json"
        with open(json_filename, "w") as outfile:
            json.dump(data, outfile, indent=4)
            
        if os.path.exists(json_filename):
            runner.log_success(f"Parsed data saved to '{json_filename}'.")
        else:
            runner.log_fail(f"Failed to save '{json_filename}'.")

    except Exception as e:
        runner.log_fail("Exception during Parsing", e)

    # 3. PPT Controller Test (Visual)
    runner.log_section("Testing PPT Controller (Visual Check)")
    runner.log_info("WARNING: Do not touch mouse/keyboard during this phase.")
    
    controller = None
    try:
        runner.log_info("Initializing Controller...")
        controller = PPTController()
        
        runner.log_info("Opening presentation...")
        controller.open_presentation(absolute_path)
        runner.log_success("Presentation opened.")
        
        runner.log_info("Starting Slideshow...")
        controller.start_show()
        runner.countdown(5, "Waiting for slideshow to load")
        runner.log_success("Slideshow started.")

        # Slide 2
        runner.log_info("Navigating to Next Slide (Slide 2)...")
        controller.next_slide()
        runner.countdown(2, "Holding Slide 2")
        runner.log_success("Transitioned to Slide 2.")

        # Slide 4
        runner.log_info("Jumping to Slide 4...")
        controller.goto_slide(4)
        runner.countdown(2, "Holding Slide 4")
        runner.log_success("Jumped to Slide 4.")

        # Previous (Slide 3)
        runner.log_info("Going to Previous Slide (Should be Slide 3)...")
        controller.previous_slide()
        runner.countdown(2, "Holding Slide 3")
        runner.log_success("Transitioned Back to Slide 3.")

        # Slide 5
        runner.log_info("Jumping to Slide 5...")
        controller.goto_slide(5)
        runner.countdown(2, "Holding Slide 5")
        runner.log_success("Jumped to Slide 5.")

        runner.log_info("Ending Show...")
        controller.end_show()
        runner.log_success("Show ended gracefully.")
        
        runner.log_info("Closing Application...")
        controller.close()
        runner.log_success("Application closed.")

    except Exception as e:
        runner.log_fail("Exception during Controller operations", e)
    
    # 4. Final Report
    runner.print_summary()

if __name__ == "__main__":
    main()