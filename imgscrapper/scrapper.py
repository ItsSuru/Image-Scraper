import os
import time
import requests
from selenium import webdriver


def fetch_image_urls(query: str, max_links_to_fetch: int, wd: webdriver, sleep_between_interactions: int = 1):
    def scroll_to_end(wd): #just reading for now, will not execute, called somewhere else
        wd.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(sleep_between_interactions)

        # build the google query

    search_url = "https://www.google.com/search?safe=off&site=&tbm=isch&source=hp&q={q}&oq={q}&gs_l=img"

    # 'https://www.google.com/search?safe=off&site=&tbm=isch&source=hp&q=Dog&oq=Dog&gs_l=img'
    # load the page
    # q = term want to search
    wd.get(search_url.format(q=query)) # searching the above url here....

    image_urls = set()
    image_count = 0
    results_start = 0
    while image_count < max_links_to_fetch: # max links to fetch = no of img
        scroll_to_end(wd) # scroll down the page

        # get all image thumbnail results
        thumbnail_results = wd.find_elements_by_css_selector("img.Q4LuWd") # manual tag to find
        number_results = len(thumbnail_results)

        print(f"Found: {number_results} search results. Extracting links from {results_start}:{number_results}")

        for img in thumbnail_results[results_start:number_results]:
            # try to click every thumbnail such that we can get the real image behind it
            try:
                img.click()
                time.sleep(sleep_between_interactions)
            except Exception:
                continue

            # extract image urls
            actual_images = wd.find_elements_by_css_selector('img.n3VNCb')
            for actual_image in actual_images:
                # checking for src and http
                if actual_image.get_attribute('src') and 'http' in actual_image.get_attribute('src'):
                    image_urls.add(actual_image.get_attribute('src'))

            image_count = len(image_urls) # counting img for limit

            if len(image_urls) >= max_links_to_fetch:
                print(f"Found: {len(image_urls)} image links, done!")
                break
        else:
            print("Found:", len(image_urls), "image links, looking for more ...")
            time.sleep(30)
            return
            load_more_button = wd.find_element_by_css_selector(".mye4qd")
            if load_more_button:
                wd.execute_script("document.querySelector('.mye4qd').click();")

        # move the result startpoint further down
        results_start = len(thumbnail_results)

    return image_urls


def persist_image(folder_path:str,url:str, counter): # and here same persist function download the img
    try:
        image_content = requests.get(url).content

    except Exception as e:
        print(f"ERROR - Could not download {url} - {e}")

    try: # downloading and giving name to img
        f = open(os.path.join(folder_path, 'jpg' + "_" + str(counter) + ".jpg"), 'wb')
        f.write(image_content)
        f.close()
        print(f"SUCCESS - saved {url} - as {folder_path}")
    except Exception as e:
        print(f"ERROR - Could not save {url} - {e}")


def search_and_download(search_term: str, driver_path: str, target_path='./images', number_images=10):
    target_folder = os.path.join(target_path, '_'.join(search_term.lower().split(' ')))

    if not os.path.exists(target_folder): # checks whether that folder already existed or not(if yes then it will skip it)
        os.makedirs(target_folder)

    #this will open the browser for you
    with webdriver.Chrome(executable_path=driver_path) as wd:
        # res is holding the url's of img
        res = fetch_image_urls(search_term, number_images, wd=wd, sleep_between_interactions=0.5)

    counter = 0
    for elem in res: # trying to pass those url's to persist_imgage function
        persist_image(target_folder, elem, counter)
        counter += 1

DRIVER_PATH = './chromedriver' # downloaded chromedriver
search_term = 'Dog' #image want to download
# num of images you can pass it from here  by default it's 10 if you are not passing
number_images = 10
search_and_download(search_term=search_term, driver_path=DRIVER_PATH)