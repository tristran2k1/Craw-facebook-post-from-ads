from ntpath import join
from playwright.async_api import async_playwright
from src.utils import clean_text, remove_substring, count_element_exist

async def find_post_url(url_company, ad_content, max_scroll_time=2):

    async with async_playwright() as p:
        user_data_dir = "./user_data_dir"                                                
        browser = await p.chromium.launch_persistent_context(user_data_dir, headless=True, slow_mo=50, args=['--start-maximized'])                                                    
        page = await browser.new_page()

        # wait until no new network requests are made for 500 ms
        await page.goto(url_company, wait_until="networkidle")

        # check already logged in 
        if await count_element_exist(page, '#mobile_login_bar') != 0:
            result = {'status':'LOGIN_FAILED', 'url': None}
            return result

        # initial value
        index_container = 0
        num_of_scroll = 0

        while (num_of_scroll < max_scroll_time):
            
            # scroll down and check end of page
            await page.wait_for_timeout(4000)
            num_of_scroll = num_of_scroll + 1
            await page.keyboard.press("End")
            
            # each status/post is a container, include: created date + post_url, describe(content), media(photo, video) ...
            # => select each container and process

            # check if any posts exist in the page
            post_containers = page.locator("div.story_body_container")
            num_of_containers = await post_containers.count()
            if index_container == num_of_containers:
                print(f'Not found any posts in the page, it might page cannot be loaded. {index_container}')
                result = {'status':'POST_NOT_FOUND', 'url': None}
                return result

            while index_container < num_of_containers:
                container_nth = post_containers.nth(index_container)

                # check is a shared post
                num_of_subpost_in_post = await count_element_exist(container_nth,'abbr')
                if num_of_subpost_in_post > 1:
                    index_container = index_container + num_of_subpost_in_post
                    continue

                index_container = index_container + 1
                
                # get created date
                created_date_locator = container_nth.locator('abbr')
                # created_date = await created_date_locator.inner_text()

                # if post have no content
                if await count_element_exist(container_nth, "div._5rgt._5nk5._5msi > div") == 0:
                    continue
                
                post_content_locator = container_nth.locator("div._5rgt._5nk5._5msi > div")
                post_content = await post_content_locator.all_inner_texts()
                post_content = post_content[0]
 
                # crawl content + clean content: remove emoji, '... More', \n 
                post_content = remove_substring(post_content, removeText='… More')
                post_content = clean_text(post_content)

                ad_content = remove_substring(ad_content, removeText='… More')
                ad_content = clean_text(ad_content)

                # compare content
                if ad_content.find(post_content) != -1:
                    # get url
                    post_url_locator = created_date_locator.locator('..')
                    post_url = await post_url_locator.get_attribute('href')
                    result = {'status':'SUCCESS', 'url': post_url}
                    return result
