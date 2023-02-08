# to run 
# scrapy crawl tmdb_spider -o movies.csv

import scrapy
import requests
from random import randint

def get_user_agent_list():
    API = 'efccdead-3091-423f-952d-49f98106bbc0'
    response = requests.get('http://headers.scrapeops.io/v1/user-agents?api_key=' + API)
    json_response = response.json()
    return json_response.get('result', [])

def get_random_user_agent(user_agent_list):
    random_index = randint(0, len(user_agent_list) - 1)
    return user_agent_list[random_index]

user_agent_list = get_user_agent_list()

class TmdbSpider(scrapy.Spider):
    name = 'tmdb_spider'

    def start_requests(self):
        '''
            Request the main page of the movie and navigate to the movie page.
        '''
        start_urls = ['https://www.themoviedb.org/tv/100088-the-last-of-us']
        headers = {'User-Agent': get_random_user_agent(user_agent_list)}
        for url in start_urls:
            yield scrapy.Request(url=url, headers=headers)


    def parse(self, response):
        '''
            Parse the movie page, and then navigate to the Cast & Crew page.
        '''
        next_page = response.css('p.new_button a').attrib['href']
        next_page = "https://www.themoviedb.org" + next_page
        headers = {'User-Agent': get_random_user_agent(user_agent_list)}
        yield scrapy.Request(next_page, callback = self.parse_full_credits,headers=headers)

    def parse_full_credits(self, response):
        '''
            Parse the Cast & Crew page, yield a scrapy.Request
            for the page of each actor listed on the page, and then navigate to the page of an actor.
        '''
        link = response.css("section.panel.pad ol[class='people credits '] div.info p[class!='character'] a::attr(href)").getall()
        headers = {'User-Agent': get_random_user_agent(user_agent_list)}
        for url in link:
            yield scrapy.Request(url = "https://www.themoviedb.org" + url, callback=self.parse_actor_page, headers=headers)
        

    def parse_actor_page(self, response):
        '''
            Parse the page of an actor, and output one such dictionary for each of the movies or TV shows
            on which that actor has worked. 
        '''
        actor_name = response.css("h2.title a::text").get()
        movie_or_TV_name = response.css("div.credits_list table.credit_group a.tooltip bdi::text").getall()
        for movie in movie_or_TV_name:
            yield {"actor" : actor_name, 
                    "movie_or_TV_name" : movie}
    