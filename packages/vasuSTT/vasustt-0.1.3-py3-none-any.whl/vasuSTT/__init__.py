import time
from selenium import webdriver  # pip install selenium
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait

from selenium.webdriver.support import expected_conditions as EC

options = Options()
options.add_argument('--use-fake-ui-for-media-stream')
options.add_argument('--headless')


# Website details
website_path = "https://rtstt-nethytech.netlify.app/"

# Configure Chrome options
chrome_options = Options()
chrome_options.add_argument("--use-fake-ui-for-media-stream")
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3")
chrome_options.add_argument("--headless=new")

# Initialize WebDriver
driver = webdriver.Chrome(options=chrome_options)
wait = WebDriverWait(driver, 10)

def stream(content: str):
    """Display streaming text without repeating."""
    print(f"\033[96m\rUser Speaking: \033[93m{content}", flush=True)

def get_text():
    """Get the recognized text from the website."""
    try:
        return driver.find_element(By.ID, "output").get_attribute('value')
    except Exception as e:
        print(f"Error getting text: {e}")
        return ""

def main() -> str:
    """Main function to process speech-to-text."""
    try:
        driver.get(website_path)
        wait.until(EC.presence_of_element_located((By.ID, "startButton")))

        # Start the speech recognition
        start_button = driver.find_element(By.ID, "startButton")
        start_button.click()
        print("Listening...", flush=True)

        last_text = ""
        stable_text = ""

        while True:
            current_text = get_text()
            last_text = current_text

            # Check if the recognized text has stabilized
            if current_text != stable_text:
                stable_text = current_text

            # Check if the recognition has stopped
            if start_button.text == "Start":
                break

            time.sleep(0.5)

        return stable_text
    except Exception as e:
        print(f"Error in main function: {e}")
        return ""

def listen():
    """Continuously listen for user input and handle the speech recognition."""
    try:
        while True:
            result = main()
            if result and len(result) != 0:
                print(f'you said:- "{result}"\n')
                with open("input.txt", "w", encoding="utf-8") as f:
                    f.write(result)
    except KeyboardInterrupt:
        print("\nListening interrupted.")
        return ""

listen()