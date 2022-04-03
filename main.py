from dis import dis
from operator import index
import sre_parse
from turtle import clear
import bs4 as bs
import requests
import re
import numpy as np
from wikipedia2vec import Wikipedia2Vec
from numpy import dot
from numpy.linalg import norm
import pandas as pd


initial_term = "car"
url_size = {}
budget = 12000
page_sizes = 0
pages_visited = []
pages_visited.append(initial_term)
links_list = []
links_list.append(initial_term)
wiki2vec = Wikipedia2Vec.load("enwiki_20180420_win10_500d.pkl")
term_vector = wiki2vec.get_word_vector(initial_term)
# term = "car"
# 
# def scrap_cos(term,n_terms):


def donwload_page(term):
    requested = requests.get('https://en.wikipedia.org/wiki/'+term)
    page = bs.BeautifulSoup(requested.text,'html.parser')
    # pg_size = res.headers.get('Content-Length')
    #size_kb = float(pg_size)/1024
    return term,requested,page


def page_size(term, requested):
    global url_size
    # for term in 
    pg_size = (len(requested.text))/1000
    url_size[term] = pg_size
    return url_size

    
def get_links(page):
    links = page.findAll("a", attrs={'href': re.compile("^/wiki/")})
    global links_list
    link_list_local = []
    for link in links:
        if link.text:
            lk_low = link.text.lower()
            link_list_local.append(lk_low)
    return link_list_local


def get_terms_vect(link_list_local):
    link_vector = []
    for link in link_list_local:
        try:
            # print(link)
            x = wiki2vec.get_word_vector(link)
            link_vector.append((link, x))
        except:
            pass
        try:
            x = wiki2vec.get_entity_vector(link)
            link_vector.append((link, x))
        except:
            continue
    return link_vector


def get_distance(link_vector, n_terms):
    cos_dist = []
    for ln, vector in link_vector:
        dis = dot(term_vector, vector)/(norm(term_vector)*norm(vector))
        cos_dist.append((dis,ln))
    data = sorted(set(cos_dist))
    big_cos = data[-n_terms:] 
    
    # for x, y in big_cos:
    #     url_size[y] = x 
    return big_cos

def loop(term):
    global page_sizes
    term, requested, page = donwload_page(term)
    # print(term)
    dic = page_size(term, requested)
    for item, value in dic.items():
        # if page_sizes + value >= 2000:
        #     break

        page_sizes += value
        pages_visited.append(item)
    link_local = get_links(page)
    link_vec = get_terms_vect(link_local)
    # dist = get_distance(link_vec[1], link_vec[0], 3)
    dis = get_distance(link_vec, 3)
    dis1 = sorted(dis, reverse=1)
    print(dis1)
    for x, y in dis1:
        if y not in links_list:
            links_list.append(y)
    # return links_list
    # print(dis)
    # print(url_size)

# while page_sizes < budget:
#     print(page_sizes)
loop(initial_term)
for link in links_list:
    if link not in pages_visited and page_sizes < budget:
        print(page_sizes)
        loop(link)
        print(link)
        pages_visited.append(link)
    


print(url_size)


# term_blue = scrap_cos("blue", 3)
# # print(term_blue)

# terms = {}
# terms["blue"] = term_blue
# # print(terms["blue"])

# first_level_list = []
# second_level_list = []
# for term in terms["blue"]:
#     print(term)
#     # second_level_list = []
#     try:
#         first_level_tree = scrap_cos((term[1].lower()), 3)
#         first_level_list.append(first_level_tree)
#     except KeyError as e:
#         print(e)
#     # terms["blue"] = ["term"][1] : [first_level_tree]
#     for term2 in first_level_tree:
#         try:
#             second_level_tree = scrap_cos((term2[1].lower()), 3)
#             second_level_list.append(second_level_tree)
#         # terms["blue"]["each"]["first_level_tree"] = [second_level_tree]
#         except KeyError as e:
#             print(e)
# print(terms)
# print(first_level_list)
# print(second_level_list)
# print(url_size)

