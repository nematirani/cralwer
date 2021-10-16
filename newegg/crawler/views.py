from django.shortcuts import render
import requests
from django.http import JsonResponse
import bs4
from django.conf import Settings
from crawler import models



# Create your views here.
class Crawler:
    def __init__(self,url,method='GET'):
        self.url = url
        self.method = method
        self._response = None

    @property
    def content(self):
        return self._response.content if self._response else None

    def send(self):
        self._response = requests.request(self.method, self.url)

    def to_bs4(self):
        return bs4.BeautifulSoup(self.content, features='lxml') if self.content else None

    def build_url(self):
        raise NotImplementedError

class NeweggCrawler(Crawler):
    def __init__(self,code):
        self.code = code
        super().__init__(self.build_url())
    
    def build_url(self):
        return '{base_url}/p/{code}'.format(base_url='https://www.newegg.com', code=self.code)

class Element:  
    def __init__(self,dom):
        self.dom = dom

    def parse(self):
        raise NotImplementedError 

class TitleElement(Element):
    def parse(self):
        return self.dom.body.find('h1', class_='product-title').text

class PriceElement(Element):
    def parse(self):
        return self.dom.body.find('li', class_='price-current').text



class Parser:
    def __init__(self,dom):
        self.dom = dom
    
    def _get_element(self):
        return [(attr, getattr(self, attr)) for attr in self.Meta.attrs]

    def get_results(self):
        result = {}
        for attr,el in self._get_element():
            result[attr] = el(self.dom).parse()
        return result

class NeweggParser(Parser):
    title = TitleElement
    price = PriceElement

    class Meta:
        attrs = ('title','price')
        


def newegg(request, code):
    crawler = NeweggCrawler(code)
    crawler.send()
    dom = crawler.to_bs4()
    parser = NeweggParser(dom)
    result = parser.get_results()
     

    product = models.Product(title=result['title'], price=result['price'])
    product.save()




    return JsonResponse(result)
