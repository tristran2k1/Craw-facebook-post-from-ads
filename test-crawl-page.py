import asyncio
from ntpath import join
from playwright.async_api import async_playwright
from datetime import datetime
from utils import parse_datetime, clean_text, remove_substring, check_element_exist, count_element_exist

async def find_post_url(url_company, max_scroll_time=2):

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
        is_found_pinned_post = False
        num_of_scroll = 0
        post_date = None

        while (num_of_scroll < max_scroll_time):
            
            # scroll down and check end of page
            await page.wait_for_timeout(4000)
            num_of_scroll = num_of_scroll + 1
            await page.keyboard.press("End")
            
            # each status/post is a container, include: create date + post_url, describe(content), media(photo, video) ...
            # => select each container and process

            # check if any posts exist in the page
            post_containers = page.locator("div.story_body_container")
            num_of_containers = await post_containers.count()
            if index_container == num_of_containers:
                print(f'Not found any posts in the page, it might page cannot be loaded. {index_container}')
                result = {'status':'POST_NOT_FOUND', 'url': None}
                return result

            print(num_of_containers)
            while index_container < num_of_containers:
                print(index_container)
                container_nth = post_containers.nth(index_container)
                # get create date
                if await count_element_exist(container_nth,'abbr') > 1:
                    index_container=index_container+2
                    continue

                created_date_locator = container_nth.locator('abbr')
                create_date = await created_date_locator.inner_text()
                # TODO: avoid using try except to branching
                # if check_element_exist(container_nth,"div._5rgt._5nk5._5msi > div") == Fals
                if await count_element_exist(container_nth, "div._5rgt._5nk5._5msi > div") == 0:
                    print('no content')
                    index_container = index_container+1
                    continue
                post_content_locator = container_nth.locator("div._5rgt._5nk5._5msi > div")
                post_content = await post_content_locator.all_inner_texts()
                print(post_content)
                post_content = post_content[0]
                    

                index_container=index_container+1
                
                print(create_date)
                print(post_content)
                # crawl content + clean content: remove emoji, '... More', \n 
                # post_content = remove_substring(post_content, removeText='… More')
                # post_content = clean_text(post_content)

                # ad_content = remove_substring(ad_content, removeText='… More')
                # ad_content = clean_text(ad_content)

                # compare content
                # if ad_content.find(post_content) != -1:
                #     # get url
                #     post_url_locator = created_date_locator.locator('..')
                #     post_url = await post_url_locator.get_attribute('href')
                #     result = {'status':'SUCCESS', 'url': post_url}
                #     return result
            
                # formalize datetime
                # post_date = parse_datetime(create_date)

            # check by top-down
            # diff_date = datetime.now() - post_date

            # if the ads are taken from a post
            # the post can be found 60 days before the ads are created
            # maybe it's a pinned post -> except
            # TODO: use scoll instead
            # if diff_date.days >= 60:
            #     if is_found_pinned_post:
            #         print('Not found post in 60 days from now')
            #         result = {'status':'POST_NOT_FOUND', 'url': None}
            #         return result

            #     is_found_pinned_post = True

            

url = 'https://m.facebook.com/profile.php?eav=AfbzeZeiZgAbkGuyeh6dXvpzNEccWTol7LJtu6VwOMnHLIfhVLlTsAV6nCnJ7dCYCWI&paipv=0&mds=%2Fedit%2Fpost%2Fdialog%2F%3Fcid%3DS%253A_I100076556389520%253A175712118324000%253A175712118324000%26ct%3D2%26nodeID%3Du_a_4z_8J%26redir%3D%252Fstory_chevron_menu%252F%253Fis_menu_registered%253Dfalse%26loc%3Dtimeline%26eav%3DAfYCRByHmE9KUHdR3uh9csLSX5pUNYS2Wcp18VceFaDct3YBu-FQTu1pEuNAoY0Gsjo%26paipv%3D0&mdf=1'
asyncio.run(find_post_url(url))
print('done')