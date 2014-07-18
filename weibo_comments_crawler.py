# coding=utf-8

class WeiboCommentsCrawler():
    '''
    A spider which is used to crawl all comments given a weibo item
    '''

    def __init__(self, client, weibo_mid):
        '''
        client: the weibo api client
        weibo_mid: the specific weibo whose comments would be crawled
        '''
        self.client = client
        self.weibo_id = weibo_mid

    def crawl(self):
        c = self.client
        results = []
        page = 1
        while True:
            comments = c.get('comments/show', id=int(self.weibo_id), count = 200, page = page)
            # print(comments)
            # print(type(comments))
            if type(comments) is dict:
                if len(comments['comments']) == 0:
                    break
                results.extend(comments['comments'])
                page += 1
            else:
                break

        # print('comments number', len(results))
        return results

    def save(self):
        pass

if __name__ == '__main__':
    pass
