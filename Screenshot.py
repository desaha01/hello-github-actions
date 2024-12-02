import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from email.mime.text import MIMEText
from io import BytesIO

# URL of your status page.
status_page_url = "https://lexisnexisprogressive.statuspage.io/"

# The expected operational status
expected_status = "All11 Systems Operational"

# Email configuration
smtp_server = "appmail.risk.regn.net"  # Replace with your SMTP server
smtp_port = 25  # Replace with your SMTP port
recipient_email = "harsh.desai@lexisnexisrisk.com"  # Replace with the recipient's email
sender_email = "harsh.desai@lexisnexisrisk.com"  # Replace with your email

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

# Function to take a screenshot using Selenium and return it as a binary stream
def take_screenshot():
    # Set up Selenium WebDriver (Chrome in this case)
    options = webdriver.ChromeOptions()
    options.headless = True  # Run in headless mode to not open a browser window
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-logging")
    options.add_argument("--log-level=3")  # Suppress logging
    options.add_argument("--remote-debugging-port=9222")  # Enable remote debugging
    options.add_argument("--headless")  # Ensure headless mode is enabled
    options.add_argument("--disable-software-rasterizer")  # Disable software rasterizer

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    try:
        # Open the status page in the browser
        driver.get(status_page_url)
        driver.implicitly_wait(3)  # Wait for the page to load completely

        # Take a screenshot and return it as a binary stream
        screenshot = driver.get_screenshot_as_png()
        print("Screenshot captured")
        return screenshot
    finally:
        driver.quit()

# Function to send an email with the screenshot using smtplib
def send_email(screenshot):
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = "Status Page Alert"

    body = "The status page has changed. Please find the screenshot attached."
    msg.attach(MIMEText(body, 'plain'))

    part = MIMEBase('application', 'octet-stream')
    part.set_payload(screenshot)
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', 'attachment; filename="status_change.png"')
    msg.attach(part)

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        text = msg.as_string()
        server.sendmail(sender_email, recipient_email, text)
        server.quit()
        print(f"Email sent to {recipient_email}")
    except Exception as e:
        print(f"Failed to send email: {e}")

# Main function to check status and send email if status has changed
def main():
    current_status = get_current_status()
    print(f"Current status: {current_status}")
    
    if current_status != expected_status:
        print(f"Status changed! Expected: {expected_status}, Found: {current_status}")
        screenshot = take_screenshot()  # Take a screenshot when status changes
        if screenshot:
            send_email(screenshot)  # Send the screenshot via email

# Run the main function
main()
