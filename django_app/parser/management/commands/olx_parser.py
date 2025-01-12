import asyncio
import json
import logging
import os
import random
import time

from asgiref.sync import sync_to_async
from django.core.management import BaseCommand
from playwright.async_api import async_playwright

from parser.models import OLXAd


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        while True:
            asyncio.run(self.olx_ad_parser())
            time.sleep(60)

    async def olx_ad_parser(self):

        async with async_playwright() as p:
            try:
                browser = await p.chromium.launch(headless=False)
                context = await browser.new_context()

                try:
                    await self.load_cookies(context)
                except FileNotFoundError:
                    pass

                page = await context.new_page()

                for i in range(1, 6):
                    if i == 1:
                        await page.goto("https://www.olx.ua/uk/list/")

                    else:
                        await page.goto(f"https://www.olx.ua/uk/list/?page={i}")

                    await page.wait_for_load_state("domcontentloaded")

                    await self.human_scroll_page(page)

                    all_links = await self.get_ad_links(page)

                    for link in all_links:
                        logging.log(logging.INFO, f"Link is being processed: {link}")
                        try:
                            information_about_ad = {}
                            await page.goto(link)

                            await page.wait_for_load_state("domcontentloaded")

                            await self.human_scroll_page(page)

                            imgs_list = await self.get_ad_images(page)
                            information_about_ad['images'] = imgs_list

                            date_published = await self.get_date_published(page)
                            information_about_ad['date_published'] = date_published

                            title = page.locator("[class='css-1kc83jo']")
                            if await title.count() > 0:
                                title = await title.text_content()
                                information_about_ad['title'] = title

                            try:
                                price, log_mess = await self.get_ad_price(page)
                                information_about_ad['price'] = price
                                logging.log(logging.INFO, log_mess)
                            except Exception as e:
                                logging.log(logging.INFO, f"Price error: {e}")

                            tags_list = await self.get_ad_tags(page)
                            information_about_ad['tags'] = "\n".join(tags_list)

                            describe = await page.locator("[class='css-1o924a9']").text_content()
                            information_about_ad['describe'] = describe

                            phone_number = await self.get_seller_phone_number(page)
                            information_about_ad['phone_number'] = phone_number
                            await page.wait_for_timeout(5000)

                            id_locator = await page.locator("[class='css-12hdxwj']").text_content()
                            id_advertisement = id_locator.split(": ")[-1]
                            information_about_ad['id_advertisement'] = id_advertisement
                            logging.log(logging.INFO, "Id found successfully")

                            number_of_views = await self.get_number_of_views_ad(page)
                            information_about_ad['number_of_views'] = number_of_views

                            name_seller = await page.locator("[class='css-1lcz6o7']").nth(1).text_content()
                            information_about_ad['name_seller'] = name_seller
                            logging.log(logging.INFO, "Name seller found successfully")

                            rating = await self.get_ad_rating(page)
                            information_about_ad['rating'] = rating

                            register_date_seller = await page.locator("[class='css-23d1vy']").nth(1).text_content()
                            information_about_ad['register_date_seller'] = register_date_seller
                            logging.log(logging.INFO, "Register date seller found successfully")

                            last_online_seller = await self.get_last_online_seller(page)
                            information_about_ad['last_online_seller'] = last_online_seller

                            region = await page.locator("[class='css-wefbef']").text_content()
                            information_about_ad['region'] = region

                            try:
                                await self.save_cookies(context)
                            except FileNotFoundError:
                                os.mkdir("parser/cookies")

                            exists_advertisement = await sync_to_async(
                                OLXAd.objects.filter(id_advertisement=id_advertisement).exists)()
                            if not exists_advertisement:
                                try:
                                    await OLXAd.objects.acreate(**information_about_ad)
                                except Exception as e:
                                    logging.log(logging.INFO, f"Error saving object: {e}")

                        except Exception as e:
                            logging.log(logging.INFO, f"Error: {e}")

            finally:
                await browser.close()

    @staticmethod
    async def load_cookies(context):
        with open("parser/cookies/cookies.txt", "r") as f:
            cookies = json.load(f)
            await context.add_cookies(cookies)

    @staticmethod
    async def save_cookies(context):
        with open("parser/cookies/cookies.txt", "w") as f:
            cookies = await context.cookies()
            f.write(json.dumps(cookies))

    @staticmethod
    async def get_ad_links(page):

        list_all_elements = await page.locator('[class="css-l9drzq"]').all()
        all_ad_links = []

        for element in list_all_elements:
            start_link = 'https://m.olx.ua/'
            end_link = await element.locator('a').nth(0).get_attribute("href")
            link = start_link + end_link
            all_ad_links.append(link)

        return all_ad_links

    @staticmethod
    async def get_ad_images(page):
        imgs_list = []
        all_div_imgs = await page.locator("[class='swiper-zoom-container']").all()
        for img in all_div_imgs:
            imgs_list.append(await img.locator("img").get_attribute("src"))
            logging.log(logging.INFO, "Image found successfully")
        return "\n".join(imgs_list)

    @staticmethod
    async def get_date_published(page):
        try:
            date_published_locator = page.locator("[class='css-1ycin']")
            if await date_published_locator.count() > 0:
                date_published = await date_published_locator.text_content()
                logging.log(logging.INFO, "Date published found successfully")
            else:
                date_published = ""
                logging.log(logging.INFO, f"Date published not found successfully")

            return date_published

        except Exception as e:
            logging.log(logging.INFO, f"Error: {e}")

    @staticmethod
    async def get_ad_price(page, price=0):
        price_locator = page.locator("[class='css-90xrc0']")
        if await price_locator.count() > 0:
            log_mess = "Price found successfully"
            price = await price_locator.text_content()
        else:
            log_mess = "Price not found"

        return price, log_mess

    @staticmethod
    async def get_ad_tags(page):
        tags_locator = page.locator("[class='css-rn93um']")
        tags_list = []
        for d in await tags_locator.all():
            list_with_li = [await data.text_content() for data in await d.locator("li").all()]
            list_with_div = [await data.text_content() for data in await d.locator("div").all()]
            tags_list = list_with_li + list_with_div
            logging.log(logging.INFO, "Tags found successfully")

        return tags_list

    @staticmethod
    async def get_seller_phone_number(page):
        if await page.locator("[class='css-10ghwn2']").count() == 0 and await page.locator("[class='css-1vgbwlu']").count() != 0:
            await page.locator("[class='css-72jcbl']").click()
            await page.wait_for_timeout(1000)
            phone_number_locator = await page.locator("[class='css-1dvqodz']").all()
            phone_number = "\n".join([await number.text_content() for number in phone_number_locator])

            logging.log(logging.INFO, "Phone number found successfully")
        else:
            logging.log(logging.INFO, "Phone number not found")
            phone_number = ""
            await page.locator("[class='css-12hdxwj']").click()
            await page.wait_for_timeout(1000)
        return phone_number

    @staticmethod
    async def get_number_of_views_ad(page):

        spectators_locator = page.locator("[class='css-42xwsi']")
        if await spectators_locator.count() > 0:
            spectators = await spectators_locator.text_content()
            spectators = int(spectators.split(": ")[-1])

            logging.log(logging.INFO, "Number of views found successfully")

        else:
            spectators = None

        return spectators

    @staticmethod
    async def get_ad_rating(page):

        rating_locator = page.locator("[class='css-1t8hkrx']")
        if await rating_locator.count() > 0:
            rating = await rating_locator.nth(0).text_content()
            logging.log(logging.INFO, "Rating found successfully")
        else:
            rating = "Ще не має рейтингу"
            logging.log(logging.INFO, "Rating not found")

        return rating

    @staticmethod
    async def get_last_online_seller(page):
        last_online_seller_locator = page.locator("[class='css-1p85e15']").nth(1)
        if await last_online_seller_locator.count() > 0:
            last_online_seller = await last_online_seller_locator.text_content()
            logging.log(logging.INFO, "Last online seller found successfully")
        else:
            last_online_seller = await page.locator("[class='css-1bbl8pa']").nth(1).text_content()
            logging.log(logging.INFO, "Last online seller found successfully")

        return last_online_seller

    @staticmethod
    async def human_scroll_page(page):
        for _ in range(5):
            await page.mouse.wheel(200, 400)
            await asyncio.sleep(random.uniform(1, 3))
