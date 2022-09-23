import crawl_lib
import crawl_page
import os
import json
import asyncio
import csv
import boto3
import pandas as pd
from datetime import datetime
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


def load_ads(aws_access_key_id, aws_secret_access_key, ads_s3_path):
    ads_s3_path = ads_s3_path.split('/')
    bucket = ads_s3_path[2]
    key = '/'.join(ads_s3_path[3:])
    s3 = boto3.client("s3", aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)
    s3.download_file(Bucket=bucket, Key=key, Filename="ads.csv")
    # read csv to dict
    return pd.read_csv("ads.csv").to_dict(orient = "records")


async def find_post_from_ads(ADS=None):
    ads = load_ads(
        os.environ['AWS_ACCESS_KEY_ID'],
        os.environ['AWS_SECRET_ACCESS_KEY'],
        os.environ['ADS_S3_PATH']
    ) if ADS is None else json.loads(ADS)
    posts = []
    print('============================ ADS ==================================')
    print(ads)
    print('==============================================================')
    for ad in ads:
        post = await find_post(ad['ad_id'], ad['page_id'])
        print("{:<30} {:<30}".format(post['ad_id'], post['status']))

        if post['post_id'] is not None:
            ad['post_id'] = post['post_id']
            ad['page_id'] = post['page_id']
            posts.append(ad)

    # upload posts to s3
    posts_df = pd.DataFrame(posts)
    s3_output_path = f's3://ihz-sl/ad-posts/input-ads/posts_{datetime.now().strftime("%Y%m%d%H%M%S")}.csv'
    posts_df.to_csv(s3_output_path, storage_options={'key': os.environ['AWS_ACCESS_KEY_ID'], 'secret': os.environ['AWS_SECRET_ACCESS_KEY']})

    # output the result to XCOM airflow
    with open('./airflow/xcom/return.json', 'w') as f:
        json.dump({'s3_output_path': s3_output_path}, f)


if __name__ == '__main__':
    asyncio.run(find_post_from_ads())
