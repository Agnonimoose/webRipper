import requests
from bs4 import BeautifulSoup as bs
from urllib.parse import urljoin

import os, morecontext, pathlib, minifier


class ripper:
    def __init__(self, url):
        self._url = url
        self._session = requests.Session()
        self._session.headers["User-Agent"] = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36"
        self._immies = [".apng", ".gif", ".ico", ".cur", ".jpg", ".jpeg", ".jfif",
                           ".pjpeg", ".pjp", ".png", ".svg"]

        self._jsFiles = {}
        self._cssFiles = {}
        self._imageFiles = {}

    def rip(self, url=None, minify=False):
        """Rip assets from webpage

            - url(str): url to page, if not the initiated url
            - minify(bool): choose whether or not to minify the assets

        """

        if url:
            self._url = url

        self._html = self._session.get(self._url).content.decode()
        if minify == True:
            self._html = minifier.html_minify(self._html)
        self._page = bs(self._html, "html.parser")

        for script in self._page.find_all("script"):
            if script.attrs.get("src"):
                script_url = urljoin(url, script.attrs.get("src"))
                if script_url.endswith(".js"):
                    if (minify == True) and ('min' not in script.attrs.get("src").split('.')):
                        tmpScripts= minifier.js_minify(requests.get(script_url).content.decode())
                        tmpScriptName = os.path.basename(script_url).split('/')[-1].split('.')[0] + ".min.js"
                        self._jsFiles[tmpScriptName] = tmpScripts
                    else:
                        self._jsFiles[os.path.basename(script_url).split('/')[-1]] = requests.get(script_url).content.decode()

        for link in self._page.find_all("link"):
            if link.attrs.get("href"):
                link_url = urljoin(url, link.attrs.get("href"))
                if link_url.endswith(".css"):
                    if (minify == True) and ('min' not in link.attrs.get("href").split('.')):
                        tmpCss = minifier.css_minify(requests.get(link_url).content.decode())
                        tmpCssName = os.path.basename(link_url).split('/')[-1].split('.')[0] + ".min.css"
                        self._cssFiles[tmpCssName] = tmpCss
                    else:
                        self._cssFiles[os.path.basename(link_url).split('/')[-1]] = requests.get(link_url).content.decode()

                elif pathlib.Path(link_url).suffix in self._immies:
                    self._imageFiles[os.path.basename(link_url).split('/')[-1]] = requests.get(link_url).content



    def write(self, dir=".", minify=False):
        """Write the web assets to a given directory

            - dir(str): path to write assets to
            - minify(bool): choose whether or not to minify the assets

        """
        with morecontext.dirchanged(dir):
            if "assets" not in os.listdir():
                os.mkdir("assets")
            with morecontext.dirchanged('assets'):
                if "js" not in os.listdir():
                    os.mkdir("js")
                with morecontext.dirchanged('js'):
                    for js in self._jsFiles:
                        with open(js, "w") as opened:
                            if (minify == True) and ('min' not in js.split('.')):
                                self._jsFiles[js] = minifier.js_minify(self._jsFiles[js])
                            opened.write(self._jsFiles[js])
                            opened.close()

                if "css" not in os.listdir():
                    os.mkdir("css")
                with morecontext.dirchanged('css'):
                    for css in self._cssFiles:
                        with open(css, "w") as opened:
                            if (minify == True) and ('min' not in css.split('.')):
                                self._cssFiles[css] = minifier.css_minify(self._cssFiles[css])
                            opened.write(self._cssFiles[css])
                            opened.close()

                if "img" not in os.listdir():
                    os.mkdir("img")
                with morecontext.dirchanged('img'):
                    for img in self._imageFiles:
                        with open(img, "wb") as opened:
                            opened.write(self._imageFiles[img])
                            opened.close()

                with open("page.html", "w") as opened:
                    if minify == True:
                        self._html = minifier.html_minify(self._html)
                    opened.write(self._html)
                    opened.close()



