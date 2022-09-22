import crawl_lib
import crawl_page
import os
import json
import asyncio
from utils import FACEBOOK_CONVERTER

async def find_post(ad_id, page_id):
    ad_url = f'https://www.facebook.com/ads/library/?id={ad_id}'
    page_url = f'https://m.facebook.com/{page_id}'
    converted_page_id = FACEBOOK_CONVERTER.url_to_uid(page_url) # due to the input might be name
    result = {'ad_id': ad_id, 'page_id': converted_page_id, 'post_id': None, 'status': None}
    
    ad_content = await crawl_lib.scrape_ad_content(ad_url)

    if ad_content == None :
        result['status'] = 'ADS_NOT_FOUND'
        return result

    # scroll_num should <= 3, default = 2, per scroll = 15 posts
    post_url = await crawl_page.find_post_url(page_url, ad_content)

    if post_url['status'] == 'POST_NOT_FOUND':
        result['status'] = 'POST_NOT_FOUND'
        
    elif post_url['status'] == 'LOGIN_FAILED':
        result['status'] = 'LOGIN_FAILED'
        
    else: # if post_url['status'] == 'SUCCESS'
        _post_url = "https://www.facebook.com" + post_url['url']
        post_id =  FACEBOOK_CONVERTER.url_to_uid(_post_url)
        result['status'] = 'SUCCESS'       
        result['post_id'] = post_id       
    
    return result
        
async def find_post_from_ads(ADS=None):
    # ADS='[{"page_id":"100075993189667","ad_id":"1519947688358047"},{"page_id":"The-Landmark-Swanlake-Residences-Căn-Hộ-Khoáng-Nóng-Tại-Gia-101992878866213","ad_id":"1190205358138570"}]'
    ads = json.loads(os.environ['ADS']) if ADS is None else json.loads(ADS)       
    posts = []

    for ad in ads:
        post = await find_post(ad['ad_id'], ad['page_id'])
        print("{:<30} {:<30}".format(post['ad_id'], post['status']))

        if post['post_id'] is not None:
            posts.append(post)

    # output the result to XCOM airflow
    with open('./airflow/xcom/return.json', 'w') as f:
        json.dump(posts, f)    

if __name__ == '__main__':
    asyncio.run(find_post_from_ads())
