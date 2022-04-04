from distutils.log import debug
import bs4 as bs
import requests
import re
from wikipedia2vec import Wikipedia2Vec
from numpy import dot
from numpy.linalg import norm
import numpy as np
import matplotlib.pyplot as plt
import json


# crawler
initial_term = "hair"
pages_and_sizes = {}
budget = 20000
total_size = 0
pages_visited = []
links_list = []
wiki2vec = Wikipedia2Vec.load("enwiki_20180420_win10_500d.pkl")
term_vector = wiki2vec.get_word_vector(initial_term)
distances = []
debug = False

# cmab
num_arms = 10
min_distance_to_reward = 0.3
regret = 0.0
regrets = [0.0]
eps = 0.4
init_proba = 1.0
estimates = [init_proba] * num_arms
counts = [0] * num_arms
actions = []


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
    for ln, vector in link_vector.items():
        distances_keys = [i[1] for i in distances]
        if ln not in pages_visited and ln not in distances_keys:
            dis = dot(term_vector, vector) / (norm(term_vector) * norm(vector))
            distances.append([dis, ln])
    distances = sorted(distances)
    distances = add_bins_to_distances()
    return distances


def add_bins_to_distances():
    # makes the distances discrete
    global distances
    count_distances = len(distances)
    bin_size = count_distances // num_arms
    current_bin = 0

    for i, d in enumerate(distances):
        if len(d) == 2:
            d.append(current_bin)
        else:
            d[2] = current_bin
        if (i + 1) % bin_size == 0:
            if current_bin >= num_arms:
                current_bin = num_arms - 1
            else:
                current_bin += 1
    return distances


def generate_reward(term):
    distance = [i[0] for i in distances if i[1] == term]
    if distance[0] >= min_distance_to_reward:
        return 1
    return 0


def update_regret(term):
    global regret, regrets
    best_distance = max([i[0] for i in distances])
    distance = [i[0] for i in distances if i[1] == term]
    regret += best_distance - distance[0]
    regrets.append(regret)


def log_debug(message):
    if debug:
        print(message)
        return message


def print_link(link, action, reward):
    dict_to_print = {
        link: {
            "distance": str([i[0] for i in distances if i[1] == link]),
            "size": pages_and_sizes[link],
            "total_size": str(total_size),
            "regret": str(regret),
            "action": str(action),
            "reward": str(reward),
            "counts": str(counts),
            "estimates": str(estimates),
        }
    }

    print(
        json.dumps(dict_to_print, indent=2)
        .replace("{", "")
        .replace("}", "")
        .replace('\n  "', "")
        .replace('"\n  \n', "\n")
        .replace('"', "")
        .replace(",", "")
    )


def process_link(term):
    global total_size, pages_visited
    requested, page = download_page(term)
    page_size = get_page_size(requested)

    if total_size + page_size > budget:
        return False

    total_size += page_size
    pages_visited.append(term)
    pages_and_sizes[term] = page_size
    next_links = get_links(page)
    link_vec = get_terms_vect(next_links)
    link_vec = clean_vectors(link_vec)
    get_distance(link_vec)
    return True


def find_term_in_bin(num_bin):
    # find the next action:
    term = ""
    terms_in_bin = [i[1] for i in distances if i[2] == num_bin]
    while not term:
        index_term = np.random.randint(0, len(terms_in_bin))
        if terms_in_bin[index_term] not in pages_visited:
            term = terms_in_bin[index_term]
    return term


def run_one_step():
    global estimates
    if np.random.random() < eps or not any(estimates):
        i = np.random.randint(0, num_arms)
    else:
        i = max(range(num_arms), key=lambda x: estimates[x])

    next_term = find_term_in_bin(i)
    if process_link(next_term):
        r = generate_reward(next_term)
        estimates[i] += 1.0 / (counts[i] + 1) * (r - estimates[i])
        return i, next_term, r
    return None, None, None


def plot_budgets():
    sizes = list(pages_and_sizes.values())

    f_budgets = plt.figure("Budget Sizes")
    plt.title("Budget Sizes")
    plt.xlabel("Download")
    plt.ylabel("Page Size")
    plt.step(np.arange(len(sizes)), sizes)

    f_budgets_cumsum = plt.figure("Budget Cumulative Sum")
    plt.title("Budget Cumulative Sum")
    plt.xlabel("Download")
    plt.ylabel("Cumulative Sum")
    sizes_cumsum = np.cumsum(sizes)
    plt.step(np.arange(len(sizes_cumsum)), sizes_cumsum)

    f_chosen_actions = plt.figure("Chosen Actions")
    plt.title("Chosen Actions")
    plt.xlabel("Times action chosen")
    plt.ylabel("Action Bin")
    plt.bar(np.arange(len(counts)), counts)

    plt.show()


def loop(initial_term):
    global counts, actions
    # run the first time
    process_link(initial_term)
    processed_term = initial_term

    while processed_term is not None:
        prev_link = processed_term
        action, processed_term, reward = run_one_step()
        if processed_term is not None:
            print_link(prev_link, action, reward)
            counts[action] += 1
            actions.append(action)
            update_regret(processed_term)


if __name__ == "__main__":
    loop(initial_term)
    plot_budgets()
    print("")
