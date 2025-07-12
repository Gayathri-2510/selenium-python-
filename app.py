from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import csv
from datetime import datetime

options = Options()
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--no-sandbox")
driver = webdriver.Chrome(options=options)
try:
    url = "https://sourcing.alibaba.com/rfq/rfq_search_list.htm?country=AE&recently=Y&tracelog=newest"
    driver.get(url)
    time.sleep(3)  
    rfq_data = driver.execute_script(
        "return window.PAGE_DATA && window.PAGE_DATA.index && window.PAGE_DATA.index.data ? window.PAGE_DATA.index.data : [];"
    )

    if not rfq_data:
        print("No RFQ data found.")
    else:
        print(f"Found {len(rfq_data)} RFQ entries.")

    buyer_img_elements = driver.find_elements(By.TAG_NAME, 'img')
    buyer_image_urls = [img.get_attribute('src') for img in buyer_img_elements if img.get_attribute('src')]
    print(f"Found {len(buyer_image_urls)} buyer images.")
    filename = f"RFQ_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    headers = [
        "RFQ ID",
        "Title",
        "Buyer Name",
        "Buyer Images",
        "Inquiry Time",
        "Quotes Left",
        "Country",
        "Quantity Required",
        "Email Confirmed",
        "Experience",
        "Complete Chat",
        "Typical Replies",
        "Interactive",
        "Inquiry URL",
        "Inquiry Date",
        "Scraping Date"
    ]

    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        writer.writeheader()
        quote_elements = driver.find_elements(By.CLASS_NAME, 'brh-rfq-item__quote-left')
        react_divs = driver.find_elements(By.CLASS_NAME, 'next-tag-body')
        for index, item in enumerate(rfq_data):
            quotes_left = ''
            if index < len(quote_elements):
                span = quote_elements[index].find_element(By.TAG_NAME, 'span')
                quotes_left = span.text

            experienced_buyer = "No"
            if index < len(react_divs):
                react_div = react_divs[index]
                visible_text = react_div.text.strip()
                if "Experienced buyer" in visible_text:
                    experienced_buyer = "Yes"

            typically_replies = "No"
            if index < len(react_divs):
                react_div = react_divs[index]
                visible_text = react_div.text.strip()
                if "Typically replies" in visible_text:
                    typically_replies = "Yes"

            interactive_user = "No"
            if index < len(react_divs):
                react_div = react_divs[index]
                visible_text = react_div.text.strip()
                if "Interactive user" in visible_text:
                    interactive_user = "Yes"

            complete_chat = "No"

            buyer_img_url = buyer_image_urls[0] if buyer_image_urls else ''

            email_confirmed = "No"
            if index < len(react_divs):
                react_text = react_divs[index].text
                if "Email Confirmed" in react_text:
                    email_confirmed = "Yes"

            writer.writerow({
                "RFQ ID": item.get('rfqId', ''),
                "Title": item.get('subject', ''),
                "Buyer Name": item.get('buyerName', ''),
                "Buyer Images": buyer_img_url,
                "Inquiry Time": item.get('openTimeStr', ''),
                "Quotes Left": quotes_left,
                "Country": item.get('country', ''),
                "Quantity Required": item.get('quantity', ''),
                "Email Confirmed": email_confirmed,
                "Experience": experienced_buyer,
                "Complete Chat": "No", 
                "Typical Replies": typically_replies,
                "Interactive": interactive_user,
                "Inquiry URL": item.get('quoteUrl', ''),
                "Inquiry Date": datetime.now().strftime('%d-%m-%Y'),
                "Scraping Date": datetime.now().strftime('%d-%m-%Y')
            })

    print(f"Data saved to {filename}")

except Exception as e:
    print("An error occurred:", e)

finally:
    driver.quit()