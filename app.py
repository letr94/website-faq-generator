from flask import Flask, render_template, request, jsonify
from bs4 import BeautifulSoup
import requests
import openai
import os
import asyncio
import uuid
from asgiref.sync import async_to_sync
from playwright.async_api import async_playwright
from dotenv import load_dotenv
from urllib.parse import urljoin, urlparse

load_dotenv()

app = Flask(__name__)
openai.api_key = os.getenv('OPENAI_API_KEY')

# Ensure screenshots directory exists
SCREENSHOTS_DIR = os.path.join('static', 'screenshots')
os.makedirs(SCREENSHOTS_DIR, exist_ok=True)

def normalize_url(url):
    """Add protocol if missing and normalize the URL."""
    url = url.strip().lower()
    if not url:
        return None
        
    # Remove any whitespace and common prefixes
    url = url.replace(' ', '')
    for prefix in ['https://', 'http://', 'www.']:
        url = url.replace(prefix, '')
    
    return f'https://{url}'

async def try_url_with_protocols(url):
    """Try accessing URL with different protocols."""
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        
        # Set longer timeout and configure page
        page.set_default_timeout(60000)  # 60 seconds timeout
        await page.set_viewport_size({"width": 1280, "height": 800})
        
        # First try HTTPS
        try:
            https_url = f'https://{url}'
            response = await page.goto(https_url, wait_until='networkidle', timeout=60000)
            if response and response.ok:
                await browser.close()
                return https_url
        except Exception:
            pass
            
        # Then try HTTP
        try:
            http_url = f'http://{url}'
            response = await page.goto(http_url, wait_until='networkidle', timeout=60000)
            if response and response.ok:
                await browser.close()
                return http_url
        except Exception:
            pass
            
        await browser.close()
        return None

def is_same_domain(url1, url2):
    """Check if two URLs belong to the same domain."""
    return urlparse(url1).netloc == urlparse(url2).netloc

def is_common_page(url_lower):
    """Check if URL likely points to a common page type."""
    common_patterns = [
        'about', 'contact', 'product', 'service', 'feature',
        'pricing', 'team', 'faq', 'support', 'help'
    ]
    return any(pattern in url_lower for pattern in common_patterns)

async def find_common_pages(page, base_url):
    """Find common pages like About, Contact, Products etc."""
    links = await page.evaluate('''() => {
        return Array.from(document.querySelectorAll('a[href]')).map(a => a.href);
    }''')
    
    common_pages = set()
    base_domain = urlparse(base_url).netloc
    
    for link in links:
        try:
            if not is_same_domain(link, base_url):
                continue
                
            link_lower = link.lower()
            if is_common_page(link_lower):
                common_pages.add(link)
                
        except Exception:
            continue
    
    return list(common_pages)[:5]  # Limit to 5 pages to avoid overload

async def scrape_with_playwright(url):
    try:
        # Remove any protocol and normalize URL
        clean_url = url.replace('https://', '').replace('http://', '').replace('www.', '')
        working_url = await try_url_with_protocols(clean_url)
        
        if not working_url:
            return {'error': 'Could not access the website. Please check the URL and try again.'}
            
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            context = await browser.new_context(
                viewport={'width': 1280, 'height': 800},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            )
            page = await context.new_page()
            
            # Configure page settings
            page.set_default_timeout(60000)  # 60 seconds timeout
            await page.set_extra_http_headers({"Accept-Language": "en-US,en;q=0.9"})
            
            # Dictionary to store page data
            pages_data = {}
            
            # First, visit the main page
            try:
                await page.goto(working_url, wait_until='networkidle', timeout=60000)
                # Wait for common elements that might indicate page load
                await page.wait_for_selector('body', timeout=60000)
                # Additional wait for dynamic content
                await page.wait_for_timeout(3000)
                
                # Take screenshot of main page
                main_screenshot = f"{uuid.uuid4()}.png"
                main_screenshot_path = os.path.join(SCREENSHOTS_DIR, main_screenshot)
                await page.screenshot(path=main_screenshot_path, full_page=True)
                
                # Get main page content
                main_content = await page.content()
                pages_data['main'] = {
                    'url': working_url,
                    'content': main_content,
                    'screenshot': f'screenshots/{main_screenshot}'
                }
            except Exception as e:
                return {'error': f'Error accessing main page: {str(e)}'}
            
            # Find and visit common pages
            try:
                common_pages = await find_common_pages(page, working_url)
            except Exception:
                common_pages = []  # Continue with main page if finding common pages fails
            
            for page_url in common_pages:
                try:
                    await page.goto(page_url, wait_until='networkidle', timeout=60000)
                    await page.wait_for_selector('body', timeout=60000)
                    await page.wait_for_timeout(3000)
                    
                    # Take screenshot
                    page_screenshot = f"{uuid.uuid4()}.png"
                    page_screenshot_path = os.path.join(SCREENSHOTS_DIR, page_screenshot)
                    await page.screenshot(path=page_screenshot_path, full_page=True)
                    
                    # Get page content
                    page_content = await page.content()
                    
                    # Store page data
                    page_type = 'other'
                    url_lower = page_url.lower()
                    if 'about' in url_lower:
                        page_type = 'about'
                    elif 'contact' in url_lower:
                        page_type = 'contact'
                    elif 'product' in url_lower:
                        page_type = 'products'
                    
                    pages_data[page_type] = {
                        'url': page_url,
                        'content': page_content,
                        'screenshot': f'screenshots/{page_screenshot}'
                    }
                    
                except Exception as e:
                    print(f"Error scraping page {page_url}: {str(e)}")
                    continue
            
            await browser.close()
            
            if not pages_data:
                return {'error': 'Could not extract content from the website. Please try again or try a different URL.'}
            
            # Process all pages content
            all_text = ""
            screenshots = []
            
            for page_type, data in pages_data.items():
                try:
                    soup = BeautifulSoup(data['content'], 'html.parser')
                    text_elements = soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'div', 'span'])
                    text = f"\n=== {page_type.upper()} PAGE ===\n"
                    text += ' '.join([elem.get_text(strip=True) for elem in text_elements if elem.get_text(strip=True)])
                    all_text += text + "\n\n"
                    screenshots.append({
                        'type': page_type,
                        'url': data['url'],
                        'path': data['screenshot']
                    })
                except Exception as e:
                    print(f"Error processing {page_type} page: {str(e)}")
                    continue
            
            if not all_text.strip():
                return {'error': 'Could not extract readable content from the website. Please try a different URL.'}
            
            return {
                'text': all_text[:4000],  # Limit text to avoid token limits
                'screenshots': screenshots
            }
            
    except Exception as e:
        return {'error': f"Error accessing website: {str(e)}. Please check the URL and try again."}

def generate_faqs(content, custom_prompt=""):
    try:
        # Create a dynamic system message based on custom prompt
        if custom_prompt:
            system_message = f"You are a helpful assistant that generates FAQs based on website content. {custom_prompt}"
        else:
            system_message = "You are a helpful assistant that generates comprehensive FAQs based on multiple pages of a website. Include specific information from different pages (main, about, contact, products) when relevant."

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": f"Generate 8-10 relevant FAQ questions and answers based on this multi-page content. Make sure to cover different aspects of the website: {content}"}
            ]
        )
        return response.choices[0].message['content']
    except Exception as e:
        return str(e)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/generate-faq', methods=['POST'])
def generate_faq():
    data = request.json
    url = data.get('url', '').strip()

    if not url:
        return jsonify({'error': 'URL is required'}), 400
        
    custom_prompt = data.get('custom_prompt', '')
    
    try:
        # Run the async scraping function in a sync context
        result = async_to_sync(scrape_with_playwright)(url)
        
        if 'error' in result:
            return jsonify({'error': result['error']}), 400
            
        faqs = generate_faqs(result['text'], custom_prompt)
        return jsonify({
            'faqs': faqs,
            'screenshots': result['screenshots']
        })
    except Exception as e:
        return jsonify({'error': f'Error processing request: {str(e)}'}), 500

# Clean up old screenshots periodically (keep last 100)
def cleanup_screenshots():
    try:
        files = sorted(
            [os.path.join(SCREENSHOTS_DIR, f) for f in os.listdir(SCREENSHOTS_DIR)],
            key=os.path.getmtime
        )
        if len(files) > 100:
            for f in files[:-100]:
                os.remove(f)
    except Exception:
        pass  # Ignore cleanup errors

if __name__ == '__main__':
    app.run(debug=True)
