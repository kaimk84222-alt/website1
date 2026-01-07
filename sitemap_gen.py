import os
import random
import string
import datetime

def get_domain_from_cname():
    """Reads the domain name from the CNAME file."""
    try:
        with open('CNAME', 'r') as f:
            return f.read().strip()
    except FileNotFoundError:
        # Fallback if CNAME is missing, though we expect it to exist
        print("Warning: CNAME file not found. Please ensure it exists.")
        return "example.com"

def get_all_html_files():
    """Finds all HTML files in the repository, excluding common directories."""
    html_files = []
    for root, dirs, files in os.walk('.'):
        # Skip hidden directories like .git
        if '.git' in dirs:
            dirs.remove('.git')
        
        for file in files:
            if file.endswith('.html'):
                # Clean the path to be a URL-friendly path
                full_path = os.path.join(root, file).replace('./', '')
                # If it's index.html, we usually just want the directory path
                if full_path.endswith('index.html'):
                    url_path = full_path[:-10]
                else:
                    url_path = full_path
                html_files.append(url_path)
    return html_files

def generate_random_name(length=8):
    """Generates a random string for sitemap filenames."""
    letters = string.ascii_lowercase + string.digits
    return ''.join(random.choice(letters) for i in range(length))

def create_sitemap_chunk(urls, domain, filename):
    """Creates a single sitemap file for a list of URLs."""
    content = '<?xml version="1.0" encoding="UTF-8"?>\n'
    content += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    for url in urls:
        full_url = f"https://{domain}/{url}"
        content += f'  <url>\n    <loc>{full_url}</loc>\n    <lastmod>{today}</lastmod>\n    <priority>0.8</priority>\n  </url>\n'
    
    content += '</urlset>'
    with open(filename, 'w') as f:
        f.write(content)

def create_main_index(sitemap_files, domain):
    """Creates the main sitemap.xml index file."""
    content = '<?xml version="1.0" encoding="UTF-8"?>\n'
    content += '<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    
    for sm in sitemap_files:
        content += f'  <sitemap>\n    <loc>https://{domain}/{sm}</loc>\n  </sitemap>\n'
    
    content += '</sitemapindex>'
    with open('sitemap.xml', 'w') as f:
        f.write(content)

def create_robots_txt(domain):
    """Creates a robots.txt file pointing to the main sitemap."""
    content = "User-agent: *\nAllow: /\n"
    content += f"\nSitemap: https://{domain}/sitemap.xml"
    with open('robots.txt', 'w') as f:
        f.write(content)

def main():
    domain = get_domain_from_cname()
    all_urls = get_all_html_files()
    
    # Configuration: Max URLs per sitemap
    MAX_URLS = 2000
    
    # Split URLs into chunks
    chunks = [all_urls[i:i + MAX_URLS] for i in range(0, len(all_urls), MAX_URLS)]
    
    sitemap_filenames = []
    for i, chunk in enumerate(chunks):
        rand_name = f"sitemap_{generate_random_name()}.xml"
        create_sitemap_chunk(chunk, domain, rand_name)
        sitemap_filenames.append(rand_name)
        print(f"Generated: {rand_name} with {len(chunk)} links.")

    # Generate main index
    create_main_index(sitemap_filenames, domain)
    print("Generated: sitemap.xml (Index)")

    # Generate robots.txt
    create_robots_txt(domain)
    print("Generated: robots.txt")

if __name__ == "__main__":
    main()
