import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import os
from datetime import datetime

# URL of your status page
status_page_url = "https://lexisnexisinsproductstatus.statuspage.io/"

# The expected operational status
expected_status = "All Systems Operational"

# Directory to save screenshots
screenshot_dir = r"C:\Users\DesaHa01\OneDrive - Reed Elsevier Group ICO Reed Elsevier Inc\Desktop\Python_Test\Screenshot"
if not os.path.exists(screenshot_dir):
    os.makedirs(screenshot_dir)

# Function to check the current status from the page
def get_current_status():
    response = requests.get(status_page_url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find the status text (adjust the selector based on actual HTML structure)
    status_element = soup.find("span", class_="status font-large")  # Adjust the class name as needed
    if status_element:
        print(f"Status element found: {status_element.get_text().strip()}")
        return status_element.get_text().strip()
    else:
        print("Status element not found")
        return None

# Function to take a screenshot using Selenium
def take_screenshot():
    # Set up Selenium WebDriver (Chrome in this case)
    options = webdriver.ChromeOptions()
    options.headless = True  # Run in headless mode to not open a browser window
    options.add_argument("--log-level=3")  # Suppress logging
    options.add_argument("--disable-logging")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    try:
        # Open the status page in the browser
        driver.get(status_page_url)
        time.sleep(3)  # Wait for the page to load completely

        # Take a screenshot and save it with a timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        screenshot_path = os.path.join(screenshot_dir, f"status_change_{timestamp}.png")
        driver.save_screenshot(screenshot_path)
        print(f"Screenshot saved to: {screenshot_path}")
    finally:
        driver.quit()

# Main loop to monitor status page
def monitor_status():
    last_status = expected_status  # Initial status, expecting "All Systems Operational"
    
    while True:
        current_status = get_current_status()
        print(f"Current status: {current_status}")
        
        if current_status and current_status != last_status:
            print(f"Status changed! Expected: {last_status}, Found: {current_status}")
            take_screenshot()  # Take a screenshot when status changes
            last_status = current_status  # Update the last status
        
        # Wait before checking again (e.g., 5 minutes)
        time.sleep(300)

# Start monitoring the status page
monitor_status()
