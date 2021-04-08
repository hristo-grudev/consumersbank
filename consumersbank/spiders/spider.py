import json

import scrapy

from scrapy.loader import ItemLoader

from ..items import ConsumersbankItem
from itemloaders.processors import TakeFirst


class ConsumersbankSpider(scrapy.Spider):
	name = 'consumersbank'
	start_urls = ['https://www.consumers.bank/DesktopModules/EasyDNNNews/getnewsdata.ashx?language=en-US&portalid=0&tabid=106&moduleid=764&pageTitle=Our%20Press%20Releases%20%7C%20Consumers%20National%20Bank&numberOfPostsperPage=999999&startingArticle=1']

	def parse(self, response):
		data = json.loads(response.text)
		raw_data = scrapy.Selector(text=data['content'])
		post_links = raw_data.xpath('//article')
		for post in post_links:
			url = post.xpath('.//div[@class="edn_readMoreButtonWrapper"]/a/@href').get()
			date = post.xpath('.//time/text()').get()
			yield response.follow(url, self.parse_post, cb_kwargs={'date': date})

	def parse_post(self, response, date):
		if 'pdf' in response.url:
			return
		title = response.xpath('//h1[@class="edn_articleTitle"]/text()').get()
		description = response.xpath('//article//text()[normalize-space() and not(ancestor::h1)]').getall()
		description = [p.strip() for p in description if '{' not in p]
		description = ' '.join(description).strip()

		item = ItemLoader(item=ConsumersbankItem(), response=response)
		item.default_output_processor = TakeFirst()
		item.add_value('title', title)
		item.add_value('description', description)
		item.add_value('date', date)

		return item.load_item()
