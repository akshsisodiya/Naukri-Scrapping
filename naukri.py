import pyppeteer
from threading import Thread
import asyncio
import time


class Naukri:
    def __init__(self):
        self.base_url = 'https://www.naukri.com/'
        self.url = None
        self.browser = None
        self.home = None
        self.pages = []
        self.art_limit = 20
        self.results = None

    # setup browser and home page
    async def setup(self):
        self.browser = await pyppeteer.launch(headless=False, args=['--disable-notifications'])
        print('browser launched')
        self.home = await self.browser.newPage()
        print('setup done')

    # load jobs page
    async def loadjobs(self, article, count):
        try:
            await self.home.click('div .list article:nth-child({})'.format(count))
        except:
            await article.click()
        print('clicked', count)
        pages = await self.browser.pages()
        await pages[1].bringToFront()

    # load home page
    async def loadhome(self, url, pagination='1'):
        self.url = self.base_url+url+f'-jobs-{pagination}'
        await self.home.goto(self.url)
        print('home loaded')

        await self.home.waitForSelector("div .list", {'timeout': 10000, 'visible': False})
        print('list loaded')

    # click on all jobs
    async def clickjobs(self):
        articles = await self.home.querySelectorAll("div .list article")
        print('articles loaded', len(articles))

        for i, article in enumerate(articles[:self.art_limit]):
            await self.loadjobs(article, i+1)

    # get links of all jobs
    async def getlinks(self):
        pages = await self.browser.pages()
        print(len(pages))

        with open('links.txt', 'a') as f:
            for page in pages[2:]:
                f.write(page.url+'\n')
                await page.close()

    # fetch skills from all jobs
    async def fetchSkills(self):
        pages = await self.browser.pages()
        with open('skills.txt', 'a') as f:
            for page in pages[2:]:
                chips = await page.querySelectorAll('a .chip')
                for chip in chips:
                    skill = await page.evaluate('(element) => element.textContent', chip)
                    f.write(skill+',')

    # close all pages except home page
    async def closepages(self):
        pages = await self.browser.pages()
        for page in pages[2:]:
            await page.close()

    async def fetchhtml(self):
        pages = await self.browser.pages()
        for page in pages[2:]:
            html = await page.content()
            slug = page.url.split('/')[3].split('?')[0]
            with open(f'html/{slug}.txt', 'w') as f:
                f.write(html)

    async def countresults(self):
        await self.home.waitForSelector('#root > div.search-result-container > div > div > section.listContainer.fleft > div.sortAndH1Cont > div.h1-wrapper > span', {'timeout': 10000, 'visible': True})
        count_string = await self.home.querySelector('#root > div.search-result-container > div > div > section.listContainer.fleft > div.sortAndH1Cont > div.h1-wrapper > span')
        JSHandle = await count_string.getProperty('textContent')
        rawstring = JSHandle.toString()
        result_count = int(rawstring.split(' ')[4])
        print(result_count)
        self.results = result_count//20 - 1

    # run all functions
    async def run(self, urls):
        await self.setup()
        for url in urls:
            await self.loadhome(url)
            await self.countresults()
            await self.clickjobs()
            await self.fetchhtml()
            await self.fetchSkills()
            await self.closepages()

            for i in range(self.results):
                await self.loadhome(url, pagination=str(i + 2))
                await self.clickjobs()
                await self.fetchhtml()
                await self.fetchSkills()
                await self.closepages()

        await self.browser.close()
