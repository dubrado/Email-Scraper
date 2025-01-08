import requests
from bs4 import BeautifulSoup
import re
import time  # Added for delay between requests

def get_profile_links(soup):
    """
    Extract profile URLs from the faculty listing page.
    Modify the selector based on the specific website structure.
    """
    profile_links = []
    # Look for all 'a' tags that might be profile links
    for link in soup.find_all('a'):
        href = link.get('href', '')
        # Modify this condition based on the URL pattern of profile pages
        if '/people/' in href or '/profile/' in href or '/faculty/' in href:
            # Convert relative URLs to absolute URLs if necessary
            if href.startswith('/'):
                href = f"https://www.cs.stanford.edu{href}"
            profile_links.append(href)
    
    return list(set(profile_links))  # Remove duplicates

def scrape_faculty_emails(url):
    """
    Scrapes faculty emails from a given university webpage and its profile pages
    """
    try:
        # Send GET request to the main faculty page
        print(f"Attempting to fetch main page: {url}...")
        response = requests.get(url)
        response.raise_for_status()
        
        print(f"Successfully fetched main page (status code: {response.status_code})")
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Get all profile links
        profile_links = get_profile_links(soup)
        print(f"Found {len(profile_links)} profile links to process")
        
        # Email pattern
        email_pattern = r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}'
        emails = set()  # Using set to avoid duplicates
        
        # Visit each profile page
        for profile_url in profile_links:
            try:
                print(f"Fetching profile: {profile_url}")
                # Add a small delay to be polite to the server
                time.sleep(1)
                
                profile_response = requests.get(profile_url)
                profile_response.raise_for_status()
                profile_soup = BeautifulSoup(profile_response.text, 'html.parser')
                
                # Search for emails in text
                for text in profile_soup.stripped_strings:
                    found_emails = re.findall(email_pattern, text)
                    emails.update(found_emails)
                
                # Search for mailto links
                for link in profile_soup.find_all('a'):
                    href = link.get('href')
                    if href and 'mailto:' in href:
                        email = href.replace('mailto:', '').strip()
                        if re.match(email_pattern, email):
                            emails.add(email)
                            
            except Exception as e:
                print(f"Error processing profile {profile_url}: {e}")
                continue
        
        print(f"Found {len(emails)} unique email addresses")
        
        # Format emails for email client
        formatted_emails = '; '.join(sorted(emails))
        return formatted_emails
        
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

if __name__ == "__main__":
    # Example usage - replace with actual university CS/AI department URL
    url = "https://www2.eecs.berkeley.edu/Faculty/Lists/CS/faculty.html"
    print("Starting email scraper...")
    emails = scrape_faculty_emails(url)
    
    if emails:
        print("\nCopy and paste these emails into your email client:")
        print(emails)
    else:
        print("\nNo emails were found or an error occurred.")
