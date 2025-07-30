# ✅ Selenium ka use jo ki kisi bhi site ko automate karne me help karta hai

from selenium import webdriver
from selenium.webdriver.common.by import By  # ID, Class, XPath se element locate karne ke liye
from selenium.webdriver.support.ui import WebDriverWait  # kisi element ka wait karne ke liye
from selenium.webdriver.support import expected_conditions as EC  # clickable ya visible hone ka wait karne ke liye
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager  # driver auto-install ke liye
from os import getcwd  # current directory ka path lene ke liye

# ✅ Chrome ke options configure kar rahe hai
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--use-fake-ui-for-media-stream")  # Mic permissions ko bypass karne ke liye
chrome_options.add_argument("--headless=new")  # Browser background me chalega, visible nahi hoga

# ✅ Chrome driver start ho raha hai (auto-install ho jaayega agar pehli baar run kar rahe ho)
driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=chrome_options
)

# ✅ Local HTML file ko open kar rahe ho
website = "https://voicetotextbyaapthi.vercel.app/"
driver.get(website)

# ✅ Output ko save karne ke liye file ka path
rec_file = f"{getcwd()}\\input.txt"

# ✅ Speech-to-text output sunne ka main function
def listen():
    try:
        # Wait for the button to be clickable and then click
        start_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.ID, 'startButton'))
        )
        start_button.click()
        print("Listening...")

        output_text = ""  # Purana output yaad rakhne ke liye

        while True:
            # Output element jab ready ho tab uska text read karo
            output_element = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.ID, 'output'))
            )
            current_text = output_element.text.strip()

            # Agar naya output mila hai, tabhi file me write karo
            if current_text != output_text and current_text:
                output_text = current_text
                with open(rec_file, "w") as file:
                    file.write(output_text.lower())
                print("USER:", output_text)

    except KeyboardInterrupt:
        print("\n⛔ Stopped by user.")
    except Exception as e:
        print("⚠️ Error:", e)

# ✅ Start listening
listen()
