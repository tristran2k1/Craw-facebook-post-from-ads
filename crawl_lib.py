from playwright.async_api import async_playwright
from utils import logs_error, count_element_exist

# view example in ./example/num_of_ads-found.png
def get_num_of_ads(num_of_ads_text):
    num_of_ads = num_of_ads_text[1:].split(' ')
    return int(num_of_ads[0])

async def scrape_ad_content(url):
    async with async_playwright() as p:
        user_data_dir = "./user_data_dir"                     
        browser = await p.chromium.launch_persistent_context(user_data_dir, headless=True, args=['--start-maximized'])                                                            
        page = await browser.new_page()
        await page.goto(url, wait_until="load")

        # page.set_default_timeout(3000)
        # check if ads is existed
        try:
            # print(f'url: {url}')
            num_of_ads_text = await page.locator(".j1p9ls3c.gxngx1o2.mogvahtc.i6uybxyu.qc5lal2y.nnmaouwa.igjjae4c.aeinzg81").inner_text()

            # view example in ./example/num_of_ads-not_found.png
            if '~' not in num_of_ads_text:
                return None

            # use num_of_ads to find possible text
            # func: get_num_of_ads => return exactly how many ads was found, datatype : int
            # if there are more than one ads -> get the first one, else get it
            num_of_content = await count_element_exist(page, "._7jyr._a25-")
            return await page.locator("._7jyr._a25-").inner_text() if num_of_content == 1 else await page.locator("._7jyr._a25- >> nth=0").inner_text()

        except Exception as e:
            print(e)
            return await logs_error(page)