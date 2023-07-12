#Get Model #, Product ID, Manufacuter, Size, Material 1, 2 3? , Style, link, photo link.

import sys
import bs4
import time
import json
import logging
import time
import signal

from selenium import webdriver


startPage = None
endPage = None

driver = None



def handler(signum, frame):
    res = input("Ctrl-c was pressed. Do you really want to exit? y/n ")
    logger.warning('QUIT prompt entered')
    if res == 'y':
        logger.critical('Quiting Program')
        logger.critical("driver %s",driver)
        driver.close()
        driver.quit()
        sys.exit(0)



def mainWork():
    signal.signal(signal.SIGINT, handler)
    #CHANGE THIS filename

    #ogFileName = '1-5k'

    jsonFilename = f"start{startPage}-end{endPage}.txt"
    logFileName = f"start{startPage}-end{endPage}.log"


    logging.basicConfig(filename=logFileName,format = '%(asctime)s %(levelname)s %(message)s')
    logger=logging.getLogger()
    logger.setLevel(logging.DEBUG)


    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter = logging.Formatter('%(name)-12s %(asctime)s %(levelname)s %(message)s')
    # tell the handler to use this format
    console.setFormatter(formatter)
    # add the handler to the root logger
    logging.getLogger().addHandler(console)




    logger.info("Starting Firefox")

    #you are going to have to change the executable path, just download geckodriver and change the location to it
    #driver = webdriver.Firefox(executable_path=r'C:\Users\ericm\Downloads\geckodriver-v0.29.1-win64\geckodriver.exe')
    #driver.set_page_load_timeout(10)
    #driver.implicitly_wait(10)

    from bs4 import BeautifulSoup as soup

    #The base url just needs the = sign at the end for it to work
    baseURL = 'https://www.houzz.com/products/living-room-furniture/p/' # add by incraments of 36 start at 1





    logger.info("startPage: %s", startPage)
    logger.info("endPage: %s", endPage)
    logger.info('JSON OUTPUT FILE %s', jsonFilename)

    #change pages on reboots
    for x in range(startPage,endPage,36):

        driver = webdriver.Firefox(executable_path=r'C:\Users\ericm\Downloads\geckodriver-v0.29.1-win64\geckodriver.exe')
        driver.set_page_load_timeout(10)
        driver.implicitly_wait(5)

        mainPageLoadStartTime = time.time()


        furniture = []

        url = baseURL + str(x)
        
        #print(url)

        logger.info('PAGE URL %s: %s', x, url)
        
        try:
            driver.get(url)

            html = driver.page_source


            #page_soup = soup(html,"html.parser")
            page_soup = soup(html,"lxml")

            itemnum = 0

            container = page_soup.findAll("div",class_='hz-product-card hz-track-me hz-product-card--medium hz-br-container--three-grid hz-product-card__browse-redesign')
        
            logger.info('NUM PRODUCT CARDS FOUND %s', len(container))
        except:
            logger.info('NUM PRODUCT CARDS FOUND %s', len(container))
            logger.error('Load MAIN PAGE in __%s__ error TIME OUT',x)
            logger.error('SLEEPING FOR 1 MINUTE to AVOID MORE FAILURE')
            time.sleep(60) #wait a minute somethignn is wrong
            continue

        #driver.find_elements_by_class_name("hz-product-card hz-track-me hz-product-card--medium hz-br-container--three-grid hz-product-card__browse-redesign")

        #time.sleep(5)


        for contain in container:

            itemnum = itemnum + 1

            itemTotalNumber = itemnum + x #number for better logging and knowledge of area in pages very aprox changes

            itemPageLoadStartTime = time.time()

            try:
                item = contain.find('a')
                link = item.get('href')
            except:
                logger.error('no link in get')
                continue

            logger.info('itemTotalNumber %s', itemTotalNumber)

            logger.info('ITEM NUM: %s Link: %s', itemnum, link)

            if(link == None):
                logger.error('LINK NOT FOUND FOR ITEM')
                #print(item.prettify())
                #dont contintue
                continue







            #print('link is ', itemnum, ' ', link)

            #now we have product links for the page

            #print(itemnum)
            #if(itemnum > 10):
            #    break

            try:
                driver.get(link)
                html = driver.page_source
                driver.implicitly_wait(1)
            except:
                print('Load item error page=', x, 'link\n', link)
                logger.error('Load item error TIME OUT')
                continue

            page_soup = soup(html,"lxml")

            #click on the details of the item
            try:
                e =driver.find_element_by_xpath("/html/body/div[2]/div[4]/div/div[1]/div/div[1]/div[1]/div[2]/div/ul/li[2]/span")
                e.click()
            except:
                print('xpath not found error')
                logger.error('XPATH NOT FOUND FOR MORE DETAILS')
                continue

            #refersh soup after click?

            try:
                html = driver.page_source
                page_soup = soup(html,"lxml")
                price = page_soup.find('span',class_='pricing-info__price')
                price = price.text

                title = page_soup.find('span',class_='view-product-title')
                title = title.text

                if(title == None or price == None):
                    logger.error('Price or Title Not found')
                    continue

                try:
                    reviews = page_soup.find('span',class_='star-rating__review-text star-rating__review-text-link')
                    reviews = reviews.text
                except:
                    reviews = 0
                    logger.warning('no reviews for this item but it is ok')






            except:
                logger.error('PRICE NOT FOUND')
                continue


            #print(price.text)

            #priceValue = price.text
            #priceValue = priceValue.replace('$','')

            try:


                spec = []
                value = []


                spec.append('Price')
                value.append(price)

                spec.append('Title')
                value.append(title)

                spec.append('Reviews')
                value.append(reviews)



                logger.info('Price: %s', price)
                logger.info('Title: %s', title)
                logger.info('Reviews: %s', reviews)


                for item in page_soup.findAll('dt',class_='product-spec-item-label'):
                    spec.append(item.text)
                    #print(item.text)

                for item in page_soup.findAll('dd',class_='product-spec-item-value'):
                    value.append(item.text)
                    #print(item.text)

                details = dict(zip(spec,value))
                logger.debug('Details of item: %s', details)



               


                #Add furniture to details
                furniture.append(details) 
                #driver.close()
                progresMectric = itemTotalNumber / endPage
                logger.info('PROGRESS %s',progresMectric)

                itemLoadTime = time.time() - itemPageLoadStartTime

                logger.info('ITEM LOAD TIME %s',itemLoadTime)
            except:
                logger.error('SOMETHING WENT WRONG IN GETTING DETAILS')
                continue


        #At end of Page save all data into json



        logger.info('DUMPING to: %s PAGE: %s', jsonFilename, x)
        with open(jsonFilename,'a') as outfile:
            #data = json.load(outfile)
            #data.add(furniture)
            json.dump(furniture,outfile)
            furniture.clear()

        logger.info("DUMP COMPLETE")

        driver.close()

        totalPageTime = time.time() - mainPageLoadStartTime
        logger.info("PAGE LOAD TIME TOTAL %s", totalPageTime)
            

        time.sleep(5)

    driver.quit()
    print("DONE")
    logger.info("COMPLETE FROM %s to %s x is %s itemTotal is %s",startPage,endPage, x, itemTotalNumber)



if __name__ == '__main__':
    startPage = int(sys.argv[1])
    endPage = int(sys.argv[2])
    mainWork()
