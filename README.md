## pyinfo

This is a little script that can get announcements from any website you want and send it to you as an email. You can launch it with `launchctl` on mac and make it send the email for you every day so that you will not miss any important message.

## Usage

1. Create a `config.yaml` or use the template. The file location can be specified in `runner.py`
    ``` bash
    cp config_template.yaml config.yaml
    ```
2. Setup `config.yaml`.
3. Write you own `Queryer` in `custom_queryer.py`. Here is the template.
    ``` python 
    class ExampleQueryer(Queryer):
    def __init__(self):
        super().__init__("Website", "http://example.com/message", 2)

    @retry_on_network_problem()
    def get_one_page_infos(self, url):
        logger.debug('website is querying "{}"...'.format(url))
        resp = requests.get(url)
        content = resp.content.decode()
        root = html.fromstring(content)  # type: html.HtmlElement
        ul = root.find(".//ul[@class='wp_article_list']")  # type: html.HtmlElement
        for li in ul.getchildren():  # type: html.HtmlElement
            text = li.find(".//a").text
            href = li.find(".//a").attrib['href']  # type: str
            time = self.format_datetime(li.find(".//span[@class='Article_PublishDate']").text, "%Y-%m-%d")
            self.infos.append(Info(text, href, time))
        return root

    def next_page_url(self, page):  # return the next page url
        self.page_num += 1
        return self.url.replace('list', 'list{}'.format(self.page_num))
    ```
4. In the `runner.py`:
    ``` python
    # init first
    init(config = 'PATH_TO_PROJECT/config.yaml')
    start([ExampleQueryer()])   # use instances, not classes
    ```
    
4. Run the `runner.py`.

**Attention: if you want to use it with `launchctl`, you'd better use absolute path for all file location configurations.**



