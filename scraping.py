# Import Pandas, Splinter and BeautifulSoup
import pandas as pd
import datetime as dt
from splinter import Browser
from bs4 import BeautifulSoup as soup
from webdriver_manager.chrome import ChromeDriverManager

def scrape_all(): #browser?
    # Initiate headless driver for deployment
    executable_path = {'executable_path': ChromeDriverManager().install()}
    browser = Browser('chrome', **executable_path, headless=True)

    news_title, news_paragraph = mars_news(browser)

    # Run all scraping functions and store results in a dictionary
    data = {
        "news_title": news_title,
        "news_paragraph": news_paragraph,
        "featured_image": featured_image(browser),
        "facts": mars_facts(),
        "hemispheres": mars_hemisphers(browser),
        "last_modified": dt.datetime.now()
    }
    # Stop webdriver and return data
    browser.quit()
    return data

# Scrape Mars News
def mars_news(browser):
    # Visit the mars nasa news site
    url = 'https://mars.nasa.gov/news/'
    browser.visit(url)

    # Optional delay for loading the page
    browser.is_element_present_by_css("ul.item_list li.slide", wait_time=1)

    # Convert the browser html to a soup object and then quit the browser
    html = browser.html
    news_soup = soup(html, 'html.parser')

    # Add try/except for error handling
    try:
        slide_elem = news_soup.select_one('div.list_text')
        # Use the parent element to find the first 'a' tag and save it as 'news_title'
        news_title = slide_elem.find('div', class_='content_title').get_text()
        # Use the parent element to find the paragraph text
        news_p = slide_elem.find('div', class_='article_teaser_body').get_text()
    except AttributeError:
        return None, None

    return news_title, news_p

# FEATURED IMAGES
def featured_image(browser):
    # Visit URL
    url = 'https://spaceimages-mars.com'
    browser.visit(url)

    # Find and click the full image button
    full_image_elem = browser.find_by_tag('button')[1]
    full_image_elem.click()

    # Parse the resulting html with soup
    html = browser.html
    img_soup = soup(html, 'html.parser')

    # Add try/except for error handling
    try:
        # Find the relative image url
        img_url_rel = img_soup.find('img', class_='fancybox-image').get('src')

    except AttributeError:
        return None

    # Use the base url to create an absolute url
    img_url = f'https://spaceimages-mars.com/{img_url_rel}'

    return img_url

# MARS FACTS
def mars_facts():
    # Add try/except for error handling
    try:
        # Use 'read_html' to scrape the facts table into a dataframe
        df = pd.read_html('https://galaxyfacts-mars.com')[0]

    except BaseException:
        return None

    # Assign columns and set index of dataframe
    df.columns=['Description', 'Mars', 'Earth']
    df.set_index('Description', inplace=True)

    # Convert dataframe into HTML format, add bootstrap
    return df.to_html(classes="table table-striped")

# D1: Scrape High-Resolution Mars’ Hemisphere Images and Titles
## Hemispheres
def mars_hemisphers(browser):
    # 1. Use browser to visit the URL 
    url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(url)

    # 2. Create a list to hold the images and titles.
    hemisphere_image_urls = []

    # Retrieve the image URLs and titles for each hemisphere
    for i in range(4):  # iterate through css/html tags with for loop
        # Find and click the relevant hemisphere page link.
        hemisphere_url = browser.find_by_tag("div.description a.itemLink.product-item")[i]
        hemisphere_url.click()
                
        # Parse the resulting html with soup.
        html = browser.html
        img_soup = soup(html, 'html.parser')
                
        # Look inside the <li /> tag for full image url.
        list_item = img_soup.find('li')
        img_url_rel = list_item.find('a')['href']
        # Look inside the <h2 /> tag for text with a class of 'title.'
        title_rel = img_soup.select_one('h2', class_='title').get_text()

        # Store title and img_url values.
        hemispheres = {"title": title_rel, "img_url": img_url_rel}

        # Append values to dictionary.
        hemisphere_image_urls.append(hemispheres)

        # go back to 'url.'
        browser.back()

    # Print the list that holds the dictionary of each image url and title.
    return hemisphere_image_urls

if __name__ == "__main__":
    # If running as script, print scraped data
    print(scrape_all())