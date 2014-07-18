weibo-keywords-crawler
======================

微博搜索爬虫，提供搜索关键字，爬取关键字相关内容的微博和评论信息。


### 更新说明
*  *使用手动输入验证码的方式。目前爬虫有两处需要验证码：1，登陆时。2，搜索过于频繁时。爬虫当需要填写验证码的时候，会自动下载验证码并且使用本机默认的图像查看工具载入验证码，窗口会自动弹出。这时，只要根据终端的提示输入验证码即可。爬虫将会继续*
* 增加OAuth2.0 微博评论的爬取。

### 问题反馈
在[https://github.com/KeithYue/weibo-keywords-crawler/issues] (https://github.com/KeithYue/weibo-keywords-crawler/issues) 下面开一个Issue, assign 给我。

### 运行环境和相关依赖
* Python3.4
* weibo sdk package:[https://pypi.python.org/pypi/weibo/0.1.2](https://pypi.python.org/pypi/weibo/0.1.2) (用来使用官方API获取评论内容，若只对微博内容感兴趣，可忽略)
* selenium
* phantomJS:[http://phantomjs.org/](http://phantomjs.org/) (用来模拟浏览器抓取微博，必须放置再系统PATH中)

#### 安装依赖
* `pip install -r requirements.txt -i http://pypi.v2ex.com/simple`
* 安装phantomJS, 并且添加到系统PATH中。

### 使用方法
1. `git clone https://github.com/KeithYue/weibo-keywords-crawler.git`.
2. `cd weibo-keywords-crawler`
3. 配置`keyowords.txt`: 添加需要查询的关键字, 每行一个，如果是多关键词查询，每行用空格分开即可。
4. 配置`passwd.txt`: 配置爬虫所需要的用户名和密码，每行一个，用户名和密码用空格分开。
5. 运行`python main.py`: 启动爬虫，结果将存入`result`文件夹中。
6. 爬虫日志会放在`./weibo_crawler.log`中，若需要动态查看爬虫行为：'tail -f ./weibo_crawler.log'
 
主要提供了WeiboCrawler类，用来进行微博搜索。

    
    from weibo_crawler import WeiboCrawler

    def main():
        wc = WeiboCrawler('大数据', 'buaakeith@163.com', '5805880') # 三个参数：关键词（可以用空格分开），爬虫使用的用户名，爬虫使用的密码
        wc.crawl(page_count=1, comments = True) # page_count:获取结果的总页数, 默认为1，最高为50。comments:是否抓取评论数据，默认为False
        wc.save() # 存储结果
        return

    if __name__ == '__main__':
        main()

### 运行Demo
`python main.py`。结果将存入resutls文件夹。

### 数据格式
* 一条微博一个文件，存放在`.txt`文件中，`utf-8`编码，数据格式为`json`
 

    {
      "repost_count": 11,
      "user_profile": "http://weibo.com/linewow",
      "keywords": [
        "hkust"
      ],
      "comment_count": 2,
      "source_url": "http://weibo.com/1473473362/y2hsl74ca",
      "text": "【名校之旅】Hong Kong University of Science and Technology (HKUST) is the top 40 universities in the world in 2011. （Website：http://t.cn/aooAzL）香港科技大学，2011年世界大学排名前40.",
      "screen_name": "线话英语",
      "source": "微博 weibo.com",
      "created_at": {
        "$date": 1327431857000
      },
      "mid": "3405437611684426",
      "like_count": 0
    }

### 注意事项
* 该类只提供一次关键词的搜索，如果系统并行进行关键词的搜索，则需要自己编写多线程/进程的程序。
* 由于目前不支持机器自动识别验证码，所以需要验证码时程序会自动载入并且使用图片查看工具进行显示，所以目前爬虫不能在没有GUI界面的server上运行。
* 由于搜索结果最多有五十页，每页最多20条微博，所以对于每个关键词，每次执行最多只能获取1000条微博。
