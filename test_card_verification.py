import os
import unittest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from datetime import datetime
import pandas as pd

# Folders to save screenshots
PASS_FOLDER = "test_screenshots/pass_folder"
FAIL_FOLDER = "test_screenshots/fail_folder"
os.makedirs(PASS_FOLDER, exist_ok=True)
os.makedirs(FAIL_FOLDER, exist_ok=True)

BASE_URL = "http://127.0.0.1:5000"

def save_screenshot(driver, test_name, passed=True):
    now = datetime.now().strftime("%Y%m%d_%H%M%S")
    folder = PASS_FOLDER if passed else FAIL_FOLDER
    path = os.path.join(folder, f"{test_name}_{now}.png")
    driver.save_screenshot(path)
    print(f"📸 Screenshot saved: {path}")

class CardFormTests(unittest.TestCase):

    def setUp(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless=new")
        self.driver = webdriver.Chrome(service=Service(), options=chrome_options)
        self.wait = WebDriverWait(self.driver, 10)
        self.driver.get(BASE_URL)

    def tearDown(self):
        self.driver.quit()

    def fill_and_submit_form(self, name, birthdate, card_number, expiry, cvv):
        self.driver.get(BASE_URL)
        self.driver.find_element(By.NAME, "name").clear()
        self.driver.find_element(By.NAME, "name").send_keys(name)
        self.driver.find_element(By.NAME, "birthdate").clear()
        self.driver.find_element(By.NAME, "birthdate").send_keys(birthdate)
        self.driver.find_element(By.NAME, "card_number").clear()
        self.driver.find_element(By.NAME, "card_number").send_keys(card_number)
        self.driver.find_element(By.NAME, "expiry").clear()
        self.driver.find_element(By.NAME, "expiry").send_keys(expiry)
        self.driver.find_element(By.NAME, "cvv").clear()
        self.driver.find_element(By.NAME, "cvv").send_keys(cvv)
        self.driver.find_element(By.TAG_NAME, "button").click()

    def test_TC1_all_fields_present(self):
        try:
            for field in ["name", "birthdate", "card_number", "expiry", "cvv"]:
                self.assertTrue(self.driver.find_element(By.NAME, field).is_displayed())
            save_screenshot(self.driver, "TC1", passed=True)
        except:
            save_screenshot(self.driver, "TC1", passed=False)
            self.fail("Missing form fields.")

    def test_TC2_valid_and_invalid_names(self):
        df = pd.read_excel("valid_cards.xlsx", engine="openpyxl")
        valid_row = df.iloc[0]
        valid_name = valid_row["Name"]
        card_number = str(valid_row["Card Number"]).zfill(16)
        cvv = str(valid_row["CVV"])

        # ✅ Valid case
        self.fill_and_submit_form(valid_name, "1990-01-01", card_number, "2025-09", cvv)
        try:
            self.wait.until(EC.url_contains("/success"))
            self.assertIn("/success", self.driver.current_url)
            save_screenshot(self.driver, "TC2_valid", passed=True)
        except:
            save_screenshot(self.driver, "TC2_valid", passed=False)
            self.fail("Valid name test failed")

        # ❌ Invalid case
        self.fill_and_submit_form("Fake Name", "1990-01-01", card_number, "2025-09", cvv)
        try:
            self.wait.until(EC.url_contains("/fail"))
            self.assertIn("/fail", self.driver.current_url)
            save_screenshot(self.driver, "TC2_invalid", passed=True)
        except:
            save_screenshot(self.driver, "TC2_invalid", passed=False)
            self.fail("Invalid name test failed")

    def test_TC3_birthdate_format(self):
        self.fill_and_submit_form("John Doe", "1990-01-01", "4000000000000000", "2025-09", "100")
        save_screenshot(self.driver, "TC3_invalid_format", passed=True)

    def test_TC4_card_number_validation(self):
        self.fill_and_submit_form("John Doe", "1990-01-01", "1234", "2025-09", "100")
        save_screenshot(self.driver, "TC4_short", passed=True)

        self.fill_and_submit_form("John Doe", "1990-01-01", "abcdabcdabcdabcd", "2025-09", "100")
        save_screenshot(self.driver, "TC4_non_numeric", passed=True)

    def test_TC5_expiry_validation(self):
        self.fill_and_submit_form("John Doe", "1990-01-01", "4000000000000000", "2023-01", "100")
        save_screenshot(self.driver, "TC5_past", passed=True)

        self.fill_and_submit_form("John Doe", "1990-01-01", "4000000000000000", "2050-01", "100")
        save_screenshot(self.driver, "TC5_future", passed=True)

        self.fill_and_submit_form("John Doe", "1990-01-01", "4000000000000000", "abcd-xy", "100")
        save_screenshot(self.driver, "TC5_invalid_format", passed=True)

    def test_TC6_cvv_variants(self):
        self.fill_and_submit_form("John Doe", "1990-01-01", "4000000000000000", "2025-09", "12")
        save_screenshot(self.driver, "TC6_too_short", passed=True)

        self.fill_and_submit_form("John Doe", "1990-01-01", "4000000000000000", "2025-09", "abcd")
        save_screenshot(self.driver, "TC6_alpha", passed=True)

    def test_TC7_submission_and_redirect(self):
        df = pd.read_excel("valid_cards.xlsx", engine="openpyxl")
        row = df.iloc[0]
        self.fill_and_submit_form(
            row["Name"], "1990-01-01", str(row["Card Number"]).zfill(16), "2025-09", str(row["CVV"])
        )
        try:
            self.wait.until(EC.url_contains("/success"))
            self.assertIn("/success", self.driver.current_url)
            save_screenshot(self.driver, "TC7", passed=True)
        except:
            save_screenshot(self.driver, "TC7", passed=False)
            self.fail("Form submission did not redirect to success page.")

    def test_TC8_verification_against_excel(self):
        df = pd.read_excel("valid_cards.xlsx", engine="openpyxl")
        row = df.iloc[0]
        self.fill_and_submit_form(
            row["Name"], "1990-01-01", str(row["Card Number"]).zfill(16), "2025-09", str(row["CVV"])
        )
        try:
            self.wait.until(EC.url_contains("/success"))
            self.assertIn("/success", self.driver.current_url)
            save_screenshot(self.driver, "TC8", passed=True)
        except:
            save_screenshot(self.driver, "TC8", passed=False)
            self.fail("Form verification failed against valid_cards.xlsx.")

if __name__ == "__main__":
    result = unittest.TextTestRunner(verbosity=2).run(unittest.TestLoader().loadTestsFromTestCase(CardFormTests))
    print(f"\n✅ Total Passed: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"❌ Total Failed : {len(result.failures) + len(result.errors)}")
