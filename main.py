# coding=utf-8
import random
import logging
from weibo_crawler import WeiboCrawler
from multiprocessing.dummy import Pool as ThreadPool

def load_keywords(path='./keywords.txt'):
    keywords = []
    with open(path, 'r') as f:
        for line in f:
            keywords.append(line.strip())

    return keywords

def load_users(path='./passwd.txt'):
    '''
    load the validate users
    '''
    users = []
    with open(path, 'r') as f:
        for line in f:
            users.append(tuple(line.strip().split(None)))
    print(users)
    return users

def crawl(keywords):
    try:
        wc = WeiboCrawler(keywords, *random.choice(g_users))
        wc.crawl(50, comments = True)
    finally:
        wc.save()
    return True

def main():
    logging.basicConfig(filename='./weibo_crawler.log', filemode='w', level=logging.INFO)
    logging.info('Craler started..')
    pool = ThreadPool(len(g_keywords))
    results = pool.map(crawl, g_keywords)
    pool.close()
    pool.join()
    logging.info('Crawler finished.')

g_users = load_users()
g_keywords = load_keywords()


if __name__ == '__main__':
    main()
