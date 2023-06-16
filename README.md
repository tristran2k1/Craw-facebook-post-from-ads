## About
This is a small project, collecting raw data:
- Input: ads from facebook (facebook ads library)
- Process: from ads -> post content -> search for posts on facebook (if any)
- Output: post id
  
Goal: find potential customers in the real estate field from posts that run ads.

## Note
* *User data dir
* Cookies
* Windows
* Google Chrome

## Prerequisite
* Already login into your facebook, set Facebook's language is 'English' 
* Shut down chrome browser before run task

## Step
+ crawl_on_lib.py : crawl ads post from library
+ crawl_on_page.py : find post and extract post on fanpage

## How to run
Run `main.py`

## Input
- 2 lists: page list (url), ad list (url)
- Add in `find_ad_post.py`

## Output
- `list_ad_post.csv` with 3 fields: Ads url, Page url, Post url

