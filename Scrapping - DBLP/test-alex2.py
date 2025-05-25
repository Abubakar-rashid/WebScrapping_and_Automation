import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time
import sys
import json
import re
from urllib.parse import quote
from concurrent.futures import ThreadPoolExecutor
from collections import defaultdict

class AffiliationExtractor:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        # Cache to avoid duplicate requests
        self.paper_cache = {}
        self.author_cache = {}
    
    def clean_title(self, title):
        """Clean paper title for API queries"""
        return re.sub(r'[^\w\s]', '', title).strip().lower()
    
    def get_semantic_scholar_paper(self, title, authors):
        """Query Semantic Scholar API for paper details"""
        clean_title = self.clean_title(title)
        cache_key = f"ss_{clean_title}"
        
        if cache_key in self.paper_cache:
            return self.paper_cache[cache_key]
        
        try:
            # Construct a query with both title and first author
            first_author = authors[0] if authors else ""
            query = f"{title} {first_author}"
            encoded_query = quote(query)
            
            url = f"https://api.semanticscholar.org/graph/v1/paper/search?query={encoded_query}&fields=title,authors,year,venue,openAccessPdf"
            
            response = self.session.get(url)
            if response.status_code == 200:
                data = response.json()
                # Find the best matching paper
                if 'data' in data and data['data']:
                    for paper in data['data']:
                        # Simple match: check if the paper title contains our search title
                        # or vice versa (for cases where our title contains extraneous info)
                        paper_title = paper.get('title', '').lower()
                        if paper_title in clean_title or clean_title in paper_title:
                            self.paper_cache[cache_key] = paper
                            return paper
            
            # If no paper found
            self.paper_cache[cache_key] = None
            return None
            
        except Exception as e:
            print(f"Error querying Semantic Scholar: {e}")
            # Cache the failure to avoid repeated failed requests
            self.paper_cache[cache_key] = None
            return None
    
    def get_openalex_paper(self, title, authors):
        """Query OpenAlex API for paper details"""
        clean_title = self.clean_title(title)
        cache_key = f"oa_{clean_title}"
        
        if cache_key in self.paper_cache:
            return self.paper_cache[cache_key]
        
        try:
            query = f'"{title}"'  # Exact title match
            encoded_query = quote(query)
            
            url = f"https://api.openalex.org/works?filter=title.search:{encoded_query}"
            response = self.session.get(url)
            
            if response.status_code == 200:
                data = response.json()
                if 'results' in data and data['results']:
                    for paper in data['results']:
                        paper_title = paper.get('title', '').lower()
                        if paper_title in clean_title or clean_title in paper_title:
                            self.paper_cache[cache_key] = paper
                            return paper
            
            self.paper_cache[cache_key] = None
            return None
            
        except Exception as e:
            print(f"Error querying OpenAlex: {e}")
            self.paper_cache[cache_key] = None
            return None
    
    def get_author_affiliations(self, title, authors):
        """Get author affiliations from both sources and combine results"""
        affiliations = defaultdict(list)
        
        # Try Semantic Scholar first
        ss_paper = self.get_semantic_scholar_paper(title, authors)
        if ss_paper and 'authors' in ss_paper:
            for author_data in ss_paper['authors']:
                name = author_data.get('name', '')
                if name and 'affiliations' in author_data and author_data['affiliations']:
                    for affiliation in author_data['affiliations']:
                        if affiliation and affiliation not in affiliations[name]:
                            affiliations[name].append(affiliation)
        
        # Also try OpenAlex
        oa_paper = self.get_openalex_paper(title, authors)
        if oa_paper and 'authorships' in oa_paper:
            for authorship in oa_paper['authorships']:
                if 'author' in authorship and 'display_name' in authorship['author']:
                    name = authorship['author']['display_name']
                    if 'institutions' in authorship and authorship['institutions']:
                        for institution in authorship['institutions']:
                            if 'display_name' in institution:
                                affiliation = institution['display_name']
                                if affiliation and affiliation not in affiliations[name]:
                                    affiliations[name].append(affiliation)
        
        # If we found affiliations, match them to our original authors using fuzzy matching
        result = {}
        for orig_author in authors:
            # Look for exact or similar matches
            for api_author, affs in affiliations.items():
                # Simple name matching (could be improved with fuzzy matching)
                if orig_author.lower() in api_author.lower() or api_author.lower() in orig_author.lower():
                    result[orig_author] = affs
                    break
            
            # If no match found, set empty list
            if orig_author not in result:
                result[orig_author] = []
                
        return result
''' you can input the amount of proceeding , conferences and papers through parameters in this '''



def scrape_dblp_with_affiliations(max_conferences=3, max_proceedings=2, max_papers=5):
    """Scrape DBLP and enrich with author affiliations"""
    # Setup Chrome
    options = Options()
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    # Uncomment for headless mode
    # options.add_argument("--headless")
    # options.add_argument("--disable-gpu")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    # Initialize affiliation extractor
    affiliation_extractor = AffiliationExtractor()
    
    all_papers = []
    
    try:
        # Start with the conferences index page
        driver.get("https://dblp.org/db/conf/index.html?prefix=A")
        wait = WebDriverWait(driver, 10)
        
        # Find conference links
        conference_links = driver.find_elements(By.CSS_SELECTOR, "div.hide-body ul li a")[:max_conferences]
        hrefs = [link.get_attribute('href') for link in conference_links]
        
        for conf_href in hrefs:
            print(f"\nVisiting conference: {conf_href}")
            driver.get(conf_href)
            
            # Find all proceedings entries
            proceedings_elements = driver.find_elements(By.CSS_SELECTOR, "li.entry.editor.toc")
            
            for proc_idx, proc in enumerate(proceedings_elements[:max_proceedings]):
                if proc_idx >= max_proceedings:
                    break
                    
                try:
                    # Find the [contents] link
                    contents_link = proc.find_element(By.CSS_SELECTOR, "a.toc-link")
                    proceedings_title = proc.find_element(By.CSS_SELECTOR, "span.title").text
                    print(f"  Found proceedings: {proceedings_title}")
                    
                    # Get contents URL
                    contents_url = contents_link.get_attribute('href')
                    print(f"  Opening contents: {contents_url}")
                    
                    # Open in new tab
                    driver.execute_script(f"window.open('{contents_url}');")
                    driver.switch_to.window(driver.window_handles[1])
                    
                    # Wait for the page to load
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "li.entry"))
                    )
                    
                    # Extract all papers
                    paper_elements = driver.find_elements(By.CSS_SELECTOR, "li.entry:not(.editor)")
                    
                    print(f"  Found {len(paper_elements)} papers")
                    
                    for paper_idx, paper in enumerate(paper_elements):
                        if paper_idx >= max_papers:
                            break
                            
                        try:
                            # Extract paper title
                            title_elem = paper.find_element(By.CSS_SELECTOR, "span.title")
                            title = title_elem.text
                            
                            # Extract authors
                            author_elems = paper.find_elements(By.CSS_SELECTOR, "span[itemprop='author'] span[itemprop='name']")
                            authors = [author.text for author in author_elems]
                            
                            # Get publication year if available
                            year = ""
                            try:
                                year_elem = paper.find_element(By.CSS_SELECTOR, "meta[itemprop='datePublished']")
                                year = year_elem.get_attribute('content')
                            except:
                                pass
                            
                            print(f"    Paper: {title}")
                            print(f"    Authors: {', '.join(authors)}")
                            
                            # Get author affiliations (this is the new part)
                            print("    Getting author affiliations...")
                            affiliations = affiliation_extractor.get_author_affiliations(title, authors)
                            
                            # Format affiliations for display
                            formatted_affiliations = {}
                            for author, affs in affiliations.items():
                                formatted_affiliations[author] = affs if affs else ["Not found"]
                                affiliation_str = ", ".join(affs) if affs else "Not found"
                                print(f"      {author}: {affiliation_str}")
                            
                            paper_data = {
                                'conference': conf_href,
                                'proceedings': proceedings_title,
                                'title': title,
                                'authors': authors,
                                'affiliations': formatted_affiliations,
                                'year': year
                            }
                            
                            all_papers.append(paper_data)
                            print("    " + "-" * 50)
                            
                        except Exception as e:
                            print(f"    Error extracting paper details: {str(e)}")
                    
                    # Close the proceedings tab and go back to conference page
                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])
                    
                except Exception as e:
                    print(f"  Error processing proceedings: {str(e)}")
        
        # Save results to CSV and JSON
        if all_papers:
            # For CSV, we need to flatten the nested affiliations structure
            csv_data = []
            for paper in all_papers:
                # Create a flattened copy of the paper data
                flat_paper = paper.copy()
                
                # Convert affiliations to string
                author_affiliation_strings = []
                for author, affs in paper['affiliations'].items():
                    affiliation_str = ", ".join(affs)
                    author_affiliation_strings.append(f"{author}: {affiliation_str}")
                
                flat_paper['affiliations'] = "; ".join(author_affiliation_strings)
                flat_paper['authors'] = ", ".join(paper['authors'])
                
                csv_data.append(flat_paper)
            
            # Save as CSV
            df = pd.DataFrame(csv_data)
            df.to_csv('dblp_papers_with_affiliations.csv', index=False, encoding='utf-8')
            
            # Save as JSON (preserves the nested structure better)
            with open('dblp_papers_with_affiliations.json', 'w', encoding='utf-8') as f:
                json.dump(all_papers, f, ensure_ascii=False, indent=2)
            
            print(f"\nSaved {len(all_papers)} papers to dblp_papers_with_affiliations.csv and .json")
        
    finally:
        # Always close the driver
        driver.quit()
    
    return all_papers

if __name__ == "__main__":
    # Configure output encoding for Windows systems
    sys.stdout.reconfigure(encoding='utf-8')
    
    # Call the main function (with limits for testing)
    # Change these numbers for your actual scraping run
    papers = scrape_dblp_with_affiliations(
        max_conferences=2,  # Number of conferences to scrape
        max_proceedings=2,  # Number of proceedings per conference
        max_papers=3        # Number of papers per proceedings
    )
    
    print(f"Total papers with affiliations scraped: {len(papers)}")