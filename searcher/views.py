from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException

def index(request):
    return render(request, 'searcher/index.html')

url = 'https://primoapac01.hosted.exlibrisgroup.com/primo-explore/search?query='
others = ',AND&pfilter=pfilter,exact,books,AND&vid=82SNU&mfacet=library,include,MAIN,1&lang=ko_KR&mode=advanced'


def make_driver():
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    options.add_argument('window-size=1920x1080')
    options.add_argument("disable-gpu")

    
    driver = webdriver.Chrome('/usr/bin/chromedriver', options = options)
    return driver


def searchTitle(target, driver):
    driver.get(url + 'title,contains,' + target + others)
    return getResults(driver)

def searchCreator(target, driver):
    driver.get(url + 'creator,contains,' + target + others)
    return getResults(driver)

def getResults(driver):
    results = {}
    try:
        elements = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".item-title"))
        )
        index = 0
        for e in elements:
            index += 1
            results[index] = e.text
        driver.quit()
        return results
    except TimeoutException as ex:
        print("Exception has been thrown. " + str(ex))
    finally:
        driver.quit()


@csrf_exempt
def search(request):
    if request.method == 'POST':
        req = json.loads(request.body)
        reqTitle = req["action"]["detailParams"]["title"]["value"]
        driver = make_driver()

        result = searchTitle(reqTitle, driver)
        # 일단 가져오는지 보게 첫 번째 것만...
        answer = result[1]
        print(answer)
        res = {
            "version": "2.0",
            "template": {
                "outputs": [
                    {
                        "simpleText": {
                            "text": answer 
                        }
                    }
                ]
            }
        }
        return JsonResponse(res)