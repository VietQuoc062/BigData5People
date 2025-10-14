import csv
import time
import random
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (NoSuchWindowException, TimeoutException,
                                        StaleElementReferenceException, WebDriverException)
import json

url = "https://itviec.com/it-jobs"

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/140.0.0.0 Safari/537.36"
)
HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "en-US,en;q=0.9,vi;q=0.8",
    "Connection": "keep-alive",
    "Referer": "https://google.com/",
    "Upgrade-Insecure-Requests": "1",
    "DNT": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Pragma": "no-cache",
    "Cache-Control": "no-cache"
}

username = "your_email@gmail.com"
password = "your_password"

MAX_PAGES = 200
OUTPUT_CSV = "itviec_test.csv"

RETRY_CLICK = 3
WAIT_SHORT = 5
WAIT_LONG = 15

def temp_stop(a=1, b=2):
    time.sleep(random.uniform(a, b))

def auto_scroll(driver, steps=1, pause=2.0):
    for _ in range(steps):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(pause)


def safe_get_text(el):
    if not el:
        return ""
    try:
        return el.get_text(strip=True)
    except Exception:
        return ""


def safe_find_all(soup, name=None, class_=None):
    try:
        return soup.find_all(name, class_=class_)
    except Exception:
        return []


def wait_for_body(driver, timeout=WAIT_LONG):
    WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))


def refresh_web(driver, timeout=WAIT_LONG):
    old_source_len = len(driver.page_source)
    driver.refresh()
    # Wait until page length changes or timeout
    end = time.time() + timeout
    while time.time() < end:
        temp_stop(0.3, 0.6)
        new_len = len(driver.page_source)
        if new_len != old_source_len:
            break
    wait_for_body(driver, timeout=timeout)


def click_next_page(driver, target_page_num):
    attempt = 0
    while attempt < RETRY_CLICK:
        attempt += 1
        try:
            next_btn = WebDriverWait(driver, WAIT_SHORT).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "div.page.next > a[rel='next']"))
            )
        except TimeoutException:
            try:
                next_btn = WebDriverWait(driver, WAIT_SHORT).until(
                    EC.element_to_be_clickable((By.XPATH, f"//a[@href='/it-jobs?page={target_page_num}&query=&source=search_job']"))
                )
            except TimeoutException:
                print(f"[Pagination] Không tìm thấy nút next target={target_page_num} (attempt {attempt})")
                return False
        try:
            current_url = driver.current_url
            next_btn.click()
            temp_stop(0.8, 1.4)
            # Wait for URL change
            WebDriverWait(driver, WAIT_LONG).until(lambda d: d.current_url != current_url)
            refresh_web(driver)
            auto_scroll(driver, steps=1, pause=1.8)
            return True
        except (StaleElementReferenceException, TimeoutException, WebDriverException) as e:
            print(f"[Pagination] attempt {attempt} failed: {e}")
            temp_stop(1.0, 2.0)
            if attempt == RETRY_CLICK:
                return False


def extract_job_links(driver):
    links = set()
    soup = BeautifulSoup(driver.page_source, "html.parser")
    for script_tag in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(script_tag.string)
        except Exception:
            continue
        if isinstance(data, dict) and data.get("itemListElement"):
            for item in data.get("itemListElement", []):
                url = item.get("url")
                if url:
                    links.add(url)
    return links


def restart_driver():
    print("[Driver] Recreating driver after window loss...")
    new_options = Options()
    new_options.add_argument(f"user-agent={USER_AGENT}")
    new_options.add_argument("--disable-blink-features=AutomationControlled")
    new_options.add_argument("--disable-infobars")
    new_options.add_argument("--no-sandbox")
    new_options.add_argument("--disable-dev-shm-usage")
    new_options.add_argument("--lang=en-US,en")
    new_options.add_argument("--window-size=1920,1080")
    return webdriver.Chrome(options=new_options)

# ================== INIT DRIVER ==================
chrome_options = Options()
chrome_options.add_argument(f"user-agent={USER_AGENT}")
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_argument("--disable-infobars")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--lang=en-US,en")
chrome_options.add_argument("--window-size=1920,1080")
# chrome_options.add_argument("--headless=new")  # optional

driver = webdriver.Chrome(options=chrome_options)

try:
    # ================== LOGIN ==================
    driver.get("https://itviec.com/sign_in")
    wait_for_body(driver)

    WebDriverWait(driver, WAIT_LONG).until(EC.presence_of_element_located((By.ID, "user_email")))
    email_input = driver.find_element(By.ID, "user_email")
    password_input = driver.find_element(By.ID, "user_password")

    email_input.clear(); email_input.send_keys(username); temp_stop(1.2, 2.2)
    password_input.clear(); password_input.send_keys(password); temp_stop(1.0, 2.0)

    sign_in_btn = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
    sign_in_btn.click()

    wait_for_body(driver)
    time.sleep(120)  # tự xử lý captcha thủ công
    temp_stop(2, 3)

    # Navigate directly instead of opening new tab & closing old (prevents window loss)
    driver.get(url)
    wait_for_body(driver)
    auto_scroll(driver, steps=1, pause=1.5)

    # Collect all job links
    all_job_links = set()
    # page_count = 1

    # Collect from first page
    first_links = extract_job_links(driver)
    all_job_links.update(first_links)
    print(f"[Links] Page 1 collected {len(first_links)} links (total {len(all_job_links)})")

    for next_page in range(2, MAX_PAGES + 1):
        if not click_next_page(driver, next_page):
            print(f"[Pagination] Dừng tại trang {next_page-1}")
            break
        new_links = extract_job_links(driver)
        added = len(new_links - all_job_links)
        all_job_links.update(new_links)
        print(f"[Links] Page {next_page} added {added} new (total {len(all_job_links)})")
        temp_stop(1.5, 2.5)
        # page_count += 1
        # if page_count >= 3:  # limit for test
        #     break

    # Cào details từng job
    columns = [
        "Job name", "Company name", "Star", "Lương", "Skills", "Job Expertise", "Job Domain", "Address",
        "Work at", "Work days", "Company industry", "Company country", "Company size", "link"
    ]
    results = []

    #detail_limit = 4
    for idx, job_url in enumerate(list(all_job_links), start=1):
        try:
            driver.get(job_url)
            wait_for_body(driver)
            temp_stop(1.2, 2.0)
            soup = BeautifulSoup(driver.page_source, "html.parser")

            job_name = safe_get_text(soup.find("h1", class_="ipt-xl-6 text-it-black"))
            company_name = safe_get_text(soup.find("div", class_="employer-name"))
            star = safe_get_text(soup.find("div", class_="h4 ips-2 text-it-black"))

            salary = ""
            salary_div = soup.find_all("span", class_="ips-2 fw-500")
            if salary_div:
                span_salary = salary_div[0]
                if span_salary:
                    salary = safe_get_text(span_salary)
            if not salary:
                span_candidates = soup.find_all("span", class_="ips-2 fw-500")
                for sc in span_candidates:
                    txt = safe_get_text(sc)
                    if any(ch.isdigit() for ch in txt):  # contains numbers
                        salary = txt
                        break

            skills_str = ""
            skill_blocks = safe_find_all(soup, "div", "d-flex flex-wrap igap-2")
            if skill_blocks:
                skill_container = skill_blocks[0]
                skill_tags = skill_container.find_all("a", class_="text-reset itag itag-light itag-sm")
                skills = [safe_get_text(a) for a in skill_tags if safe_get_text(a)]
                skills_str = ",".join(skills)

            job_expertise = ""
            if not job_expertise:
                banner = soup.find("div", class_="imb-4 imb-xl-3 d-flex flex-column flex-xl-row igap-3 align-items-xl-baseline")
                if banner:
                    expertise_block = banner.find("div", class_="d-flex")
                    if expertise_block:
                        a = expertise_block.find("a", class_="text-reset itag itag-light itag-sm")
                        job_expertise = safe_get_text(a)

            job_domain_str = ""
            if len(skill_blocks) > 1:
                domain_tags = skill_blocks[1].find_all("div", class_="itag bg-light-grey itag-sm cursor-default")
                job_domain = [safe_get_text(d) for d in domain_tags if safe_get_text(d)]
                job_domain_str = ",".join(job_domain)

            address = ""
            addr_spans = safe_find_all(soup, "span", "normal-text text-rich-grey")
            if addr_spans:
                address = safe_get_text(addr_spans[0])
            work_at = safe_get_text(soup.find("span", class_="normal-text text-rich-grey ms-1"))

            work_days = ""
            cols = safe_find_all(soup, "div", "col text-end text-it-black")
            if len(cols) >= 4:
                work_days = safe_get_text(cols[3])
            company_industry = safe_get_text(soup.find("div", class_="col text-end text-it-black text-wrap-desktop"))
            company_country = safe_get_text(cols[2] if len(cols) > 2 else None)
            company_size = safe_get_text(cols[1] if len(cols) > 1 else None)

            results.append([
                job_name, company_name, star, salary, skills_str, job_expertise, job_domain_str,
                address, work_at, work_days, company_industry, company_country, company_size, job_url
            ])
            print(f"[Detail] ({idx}/{len(all_job_links)}) {job_name} - {company_name} | Salary='{salary}' | Expertise='{job_expertise}'")
            temp_stop(0.3, 1.6)
        except NoSuchWindowException:
            print("[Detail] Window closed unexpectedly. Attempting recovery.")
            try:
                driver.quit()
            except Exception:
                pass
            driver = restart_driver()
            driver.get(url)
            wait_for_body(driver)
            continue
        except Exception as e:
            print(f"[Detail] Lỗi khi lấy {job_url}: {e}")

    # Lưu vào CSV
    with open(OUTPUT_CSV, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(columns)
        writer.writerows(results)
    print(f"[CSV] Ghi {len(results)} dòng vào {OUTPUT_CSV}")

finally:
    try:
        driver.quit()
    except Exception:
        pass
