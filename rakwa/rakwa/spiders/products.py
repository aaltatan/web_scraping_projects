import scrapy
from scrapy.http import Response
import logging

logging.basicConfig(
    filemode="a",
    filename="logger.log",
    format="[%(asctime)s] %(levelname)s | %(name)s => %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    encoding="utf-8",
    level=logging.INFO,
)


def cf_decode_email(encodedString):
    r = int(encodedString[:2], 16)
    email = "".join(
        [
            chr(int(encodedString[i : i + 2], 16) ^ r)
            for i in range(2, len(encodedString), 2)
        ]
    )
    return email


class ProductsSpider(scrapy.Spider):
    name = "products"
    allowed_domains = ["www.rakwa.com"]
    start_urls = [
        f"https://www.rakwa.com/categories?page={idx}" for idx in range(1, 1099)
    ]

    def parse(self, res: Response):
        response: scrapy.Selector = res
        links = response.css(".listing__item > a::attr(href)").getall()
        for link in links:
            yield res.follow(url=link, callback=self.parse_item)

    def parse_item(self, res: Response):
        response: scrapy.Selector = res

        name = response.css(".listing__hero__text h2::text").get()

        categories = response.css(".primary-btn-listing-categories *::text").getall()
        categories = ", ".join(
            [cat.replace("\n", "").strip() for cat in categories if cat != "\n"]
        )

        description = [
            p.replace("\n", "")
            for p in response.css(".listing__details__about *::text").getall()
            if p != "\n"
        ]
        description = "\n".join(description)

        contact = {}

        if response.css(".fa.fa-envelope ~ a::attr(href)"):
            enc_email = (
                response.css(".fa.fa-envelope ~ a::attr(href)").get().split("#")[-1]
            )
            contact["email"] = cf_decode_email(enc_email)

        contact_lis = response.css(".listing__sidebar__contact__text li")
        for li in contact_lis:
            key = li.css("span::attr(class)").get()
            if not li.css("a"):
                contact[key] = {
                    "details": " ".join(li.css("*::text").getall()).strip(),
                }
            else:
                contact[key] = {
                    "details": " ".join(li.css("*::text").getall()).strip(),
                    "link": li.css("a::attr(href)").get().strip(),
                }

        social_media = {}
        if response.css(".listing__sidebar__contact__social"):
            selector = ".listing__sidebar__contact__social a i::attr(class)"
            keys = response.css(selector).getall()
            selector = ".listing__sidebar__contact__social a::attr(href)"
            values = response.css(selector).getall()
            for key, value in zip(keys, values):
                social_media[key] = value

        working_hours = response.css(".listing__sidebar__working__hours")
        time = working_hours.css(".row:first-child .alert *::text").getall()
        time = " ".join(time).strip()
        table = working_hours.css(".row:last-child > div > .row")
        working_week_times = ""
        for row in table:
            day = row.css(".col-3 span::text").get()
            hours = row.css(".col-9 .row .col-12 span::text").get()
            working_week_times += f"{day}: {hours}\n"

        comments = []
        comments_container = response.css(".listing__details__review li .media-body")
        for c in comments_container:
            comment = {
                "commenter": c.css("h5::text").get().strip(),
                "body": c.css(".media-body-comment-body::text").get(),
            }
            comments.append(comment)

        google_map_link = (
             response
             .css('.listing__details__map__btn::attr(href)')
             .get('')
        )

        yield {
            "name": name,
            "categories": categories,
            "description": description,
            "contact": contact,
            "social_media": social_media,
            "working_week_times": working_week_times,
            "google_map_link": google_map_link,
            "comments": comments,
            "comments_count": len(comments),
            "link": res.url,
        }
