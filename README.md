weibo-keywords-crawler
======================

微博搜索爬虫，提供搜索关键字，爬取关键字相关内容的微博和评论信息。


### 更新说明
*  *使用手动输入验证码的方式。目前爬虫有两处需要验证码：1，登陆时。2，搜索过于频繁时。爬虫当需要填写验证码的时候，会自动下载验证码并且使用本机默认的图像查看工具载入验证码，窗口会自动弹出。这时，只要根据终端的提示输入验证码即可。*

### 运行环境和相关依赖
* Python3.0+
* weibo sdk package:[https://pypi.python.org/pypi/weibo/0.1.2](https://pypi.python.org/pypi/weibo/0.1.2) (用来使用官方API获取评论内容，若只对微博内容感兴趣，可忽略)
* selenium
* phantomJS:[http://phantomjs.org/](http://phantomjs.org/) (用来模拟浏览器抓取微博，必须放置再系统PATH中)

#### 安装依赖
* `pip install -r requirements.txt -i http://pypi.v2ex.com/simple`
* 安装phantomJS, 并且添加到系统PATH中。

### 使用方法
* 配置`keyowords.txt`: 添加需要查询的关键字, 每行一个，如果是多关键词查询，每行用空格分开即可。
* 配置`passwd.txt`: 配置爬虫所需要的用户名和密码，每行一个，用户名和密码用空格分开。
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

### 注意事项
* 该类只提供一次关键词的搜索，如果系统并行进行关键词的搜索，则需要自己编写多线程/进程的程序。
