**Glassdoor Company Information Scraper**

**Overview:**
This Python script is designed to scrape company information from Glassdoor, including details such as company overview, interview experience, and popular careers. It utilizes Selenium for web scraping and BeautifulSoup for HTML parsing.

**Requirements:**
- Python 3.x
- Selenium
- BeautifulSoup
- Chrome WebDriver

**Setup:**
1. Install Python if not already installed.
2. Install required Python packages using pip:
   ```
   pip install selenium beautifulsoup4
   ```
3. Download Chrome WebDriver and place it in the system path or update the `webdriver.Chrome()` line in the script to point to its location.

**Usage:**
1. Run the script using Python:
   ```
   python company_scraper.py
   ```
2. The script will iterate through multiple pages of Glassdoor's company listings, extracting information for each company found.

**Main Functions:**
1. `extract_information_overview(soup, information_list=[]):`
   - This function extracts overview information about a company from the provided HTML soup.
    - It finds and parses relevant HTML elements to gather data such as company name, rating, details, branches, size, industry, etc.
    - Extracted information is stored in a dictionary and appended to the information_list.

2. `extract_interviews(soup, information_list):`
   - This function extracts interview-related information about a company from the provided HTML soup.
    - It finds and parses interview experience and difficulty data from specific HTML elements.
    - Extracted information includes interview experience (positive, negative, neutral) with percentages and difficulty level.
    - The extracted data is appended to the first element of the information_list as a dictionary.

3. `extract_career(soup, information_list):`
   - This function extracts popular career information related to a company from the provided HTML soup.
    - It finds and parses HTML elements to extract popular career options within the company.
    - Extracted career options are stored as a list and appended to the first element of the information_list dictionary.

4. `save_to_csv(information_list, filename):`
   - SThis function saves the extracted company information to a CSV file.
    - It defines fieldnames for the CSV file based on the data structure.
    - If the CSV file doesn't exist, it writes headers based on the fieldnames.
    - It then writes the extracted information from the information_list to the CSV file.

**Disclaimer:**
- This script is intended for educational purposes only.
- Make sure to respect Glassdoor's terms of service and use this script responsibly.
