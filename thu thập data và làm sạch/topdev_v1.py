import csv
import time
import random
from urllib.parse import urljoin
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException, ElementClickInterceptedException

def scroll_to_bottom(driver):
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

url = "https://topdev.vn/"

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/140.0.0.0 Safari/537.36"
)


MAX_PAGES = 200
OUTPUT_CSV = "topdev_test.csv"
chrome_options = Options()
chrome_options.add_argument(f"user-agent={USER_AGENT}")
# chrome_options.add_argument("--headless")
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option('useAutomationExtension', False)
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
driver = webdriver.Chrome(options=chrome_options)
driver.get(url)
time.sleep(random.uniform(2, 4))
# --- PHẦN ĐĂNG NHẬP sẽ dừng 80s để bạn đăng nhập thủ công ---
time.sleep(80)

driver.get("https://topdev.vn/jobs/search?job_categories_ids=2%2C3%2C4%2C5%2C6%2C7%2C8%2C9%2C10%2C11%2C12%2C13%2C67")
time.sleep(random.uniform(2, 4))

all_links = set()

scroll_to_bottom(driver)
time.sleep(2)

# mới vào trang đầu tiên, lấy tất cả link
soup = BeautifulSoup(driver.page_source, 'html.parser')
jobs = soup.find_all('a', class_='line-clamp-1 text-sm/[18px] font-semibold text-brand-500 md:line-clamp-1 md:text-base/[24px]')
for job in jobs:
    link = job.get('href')
    if link:
        full_link = urljoin(url, link)
        all_links.add(full_link)

print(f"Found {len(all_links)} job links.")

def safe_click_next(driver, timeout=10, max_retries=5):
    attempt = 0
    while attempt < max_retries:
        attempt += 1
        try:
            next_btn = WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "a[aria-label='Go to next page']"))
            )
            # Check disabled state (some sites add aria-disabled or class changes)
            aria_disabled = next_btn.get_attribute("aria-disabled")
            if aria_disabled == 'true':
                return False
            # Scroll into view
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", next_btn)
            time.sleep(0.3)
            try:
                next_btn.click()
            except (ElementClickInterceptedException, StaleElementReferenceException):
                # Retry by refreshing
                driver.execute_script("arguments[0].click();", next_btn)
            return True
        except TimeoutException:
            return False
        except StaleElementReferenceException:
            time.sleep(0.5)
        except ElementClickInterceptedException:
            time.sleep(0.5)
    return False

# nhấn nút next page
page_num = 1
while page_num < MAX_PAGES:
    page_num += 1
    # if page_num == 4:
    #     break
    existing_count = len(all_links)
    clicked = safe_click_next(driver)
    if not clicked:
        print(f"No more next button (page {page_num}). Stopping.")
        break
    time.sleep(random.uniform(2.0,4.0))
    scroll_to_bottom(driver)
    time.sleep(1.2)

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    jobs = soup.find_all('a', class_='line-clamp-1 text-sm/[18px] font-semibold text-brand-500 md:line-clamp-1 md:text-base/[24px]')
    new_links_found = 0
    for job in jobs:
        link = job.get('href')
        if link:
            full_link = urljoin(url, link)
            if full_link not in all_links:
                all_links.add(full_link)
                new_links_found += 1

    if new_links_found == 0:
        print(f"Page {page_num}: No new links. Assuming last page. Stopping.")
        break

    print(f"Page {page_num}: +{new_links_found} new links (total {len(all_links)}).")
    time.sleep(random.uniform(1, 2))

# Go to each job link and extract details
columns = ["Job name", "Company name", "Lương", "Skills", "Address", "Work days", "Level", "Kinh nghiệm", "Company size", "link"]

with open(OUTPUT_CSV, "w", newline="", encoding="utf-8-sig") as f:
    writer = csv.writer(f)
    writer.writerow(columns)

    for i, link in enumerate(all_links):
        print(f"\nScraping {i+1}/{len(all_links)}: {link}")
        # if i == 6:
        #     break
        try:
            driver.get(link)
            time.sleep(random.uniform(0.3, 1.3))
            
            job_soup = BeautifulSoup(driver.page_source, 'html.parser')

            job_name = job_soup.find('a', class_='text-brand-500 line-clamp-1 text-sm/[18px] font-semibold md:line-clamp-1 md:text-base/[24px]')
            job_name = job_name.text.strip() if job_name else "N/A"

            company_name_tag = job_soup.find('span', class_='text-brand-500 text-center text-sm/[18px] font-semibold md:line-clamp-2 md:text-2xl')
            company_name = company_name_tag.text.strip() if company_name_tag else "N/A"

            luong = job_soup.find_all('span', class_='text-brand-500 line-clamp-1 flex items-center gap-[6px] text-sm/[16px] font-semibold')[0]
            luong = luong.text.strip() if luong else "N/A"
            work_days = job_soup.find_all('span', class_='text-text-500 flex items-center gap-1 text-xs/[12px] font-medium md:text-sm')[2]
            work_days = work_days.text.strip() if work_days else "N/A"

            level = job_soup.find_all('span', class_='text-text-500 flex items-center gap-1 text-xs/[12px] font-medium md:text-sm')[1]
            level = level.text.strip() if level else "N/A"
            kinh_nghiem = job_soup.find_all('span', class_='text-text-500 flex items-center gap-1 text-xs/[12px] font-medium md:text-sm')[3]
            kinh_nghiem = kinh_nghiem.text.strip() if kinh_nghiem else "N/A"

            # Address
            address_tag = job_soup.find_all('span', class_='text-text-500 flex items-center gap-1 text-xs/[12px] font-medium md:text-sm')[0]
            address = address_tag.text.strip() if address_tag else "N/A"

            # Company Size
            company_size_tag = job_soup.find('div', class_='my-3 flex w-full flex-col items-center justify-between gap-1 md:gap-1')
            company_size = company_size_tag.text.strip() if company_size_tag else "N/A"

            # Skills
            skills_container = job_soup.find_all('div', class_='flex flex-wrap items-center gap-1')[0]
            skills = []
            if skills_container:
                skill_tags = skills_container.find_all('a')
                skills = [skill.text.strip() for skill in skill_tags]
            
            skills_str = ", ".join(skills) if skills else "N/A"

            print(f"Job name: {job_name} - Company: {company_name} - Salary: {luong} - Skills: {skills_str} - Address: {address} - Work days: {work_days} - Level: {level} - Experience: {kinh_nghiem} - Company size: {company_size} - Link: {link}")
            writer.writerow([job_name, company_name, luong, skills_str, address, work_days, level, kinh_nghiem, company_size, link])

        except Exception as e:
            print(f"Could not process {link}. Error: {e}")

driver.quit()
print(f"Data saved to {OUTPUT_CSV}")
