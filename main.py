from distutils.log import debug
import bs4 as bs
import requests
import re
from wikipedia2vec import Wikipedia2Vec
from numpy import dot
from numpy.linalg import norm


initial_term = "chair"
pages_and_sizes = {}
budget = 8000
total_size = 0
pages_visited = []
links_list = []
# links_list.append(initial_term)
wiki2vec = Wikipedia2Vec.load("enwiki_20180420_win10_500d.pkl")
term_vector = wiki2vec.get_word_vector(initial_term)
distances = []
total_loss = 0
comulative_action_loss = 0
debug = False


def download_page(term):
    requested = requests.get("https://en.wikipedia.org/wiki/" + term)
    page = bs.BeautifulSoup(requested.text, "html.parser")
    return requested, page


def get_page_size(requested):
    return (len(requested.text)) / 1000


def get_links(page):
    links = page.findAll("a", attrs={"href": re.compile("^/wiki/")})
    global links_list
    link_list_local = []
    for link in links:
        if link.text:
            lk_low = link.text.lower()
            link_list_local.append(lk_low)
    return link_list_local


def get_terms_vect(link_list_local):
    link_vector = {}
    for link in link_list_local:
        try:
            # print(link)
            vector = wiki2vec.get_word_vector(link)
            link_vector[link] = vector
        except KeyError:
            log_debug(f"word {link} not found")
            link_title = link.title()
            try:
                vector = wiki2vec.get_entity_vector(link_title)
                link_vector[link] = vector
            except:
                log_debug(f"entity {link} not found")
                link_vector[link] = None
    return link_vector


def clean_vectors(link_vector):
    cleaned_link_vector = {}
    for key, value in link_vector.items():
        if value is not None:
            cleaned_link_vector[key] = value
    return cleaned_link_vector


def get_distance(link_vector):
    global distances
    total_sum = 0
    for ln, vector in link_vector.items():
        distances_keys = [i for _, i in distances]
        if ln not in pages_visited and ln not in distances_keys:
            dis = dot(term_vector, vector) / (norm(term_vector) * norm(vector))
            distances.append((dis, ln))
            total_sum += dis
    distances = sorted((distances), reverse=1)
    # dist1, dist2 = distances[0], distances[1]
    return distances, total_sum


def get_next_link():
    for distance, link in distances:
        if link not in pages_visited:
            return distance, link


def log_debug(message):
    if debug:
        print(message)


def get_total_loss(total_sum, len_links_page):
    global total_loss
    moment_loss = total_sum / len_links_page
    total_loss += moment_loss
    print(f"Total Loss = {total_loss}")
    return total_loss


def get_action_loss(distance):
    global comulative_action_loss
    last_link = pages_visited[-1]
    dist1 = 1
    for (x, y) in distances:
        if y == last_link:
            dist1 = x
    action_loss = 0
    action_loss += dist1 - distance
    comulative_action_loss += action_loss
    print(f"Action Loss = {action_loss}")
    print(f"Comulative Action Loss = {comulative_action_loss}")
    return action_loss, comulative_action_loss


def process_link(term):
    global total_size, pages_visited
    requested, page = download_page(term)
    # print(term)
    page_size = get_page_size(requested)
    total_size += page_size
    pages_visited.append(term)
    pages_and_sizes[term] = page_size
    next_links = get_links(page)
    link_vec = get_terms_vect(next_links)
    link_vec = clean_vectors(link_vec)
    distances, total_sum = get_distance(link_vec)
    get_total_loss(total_sum, len(link_vec.keys()))

    distance, link = get_next_link()
    get_action_loss(distance)
    return distance, link


def loop(initial_term):
    distance = 1
    next_link = initial_term
    while True and total_size < budget:
        print(f"Total size = {total_size} \n")
        print(next_link, distance)
        distance, next_link = process_link(next_link)


loop(initial_term)
