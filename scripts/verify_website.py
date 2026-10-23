"""Buildless-site asset, bilingual content and repository-link validation."""
import json
from html.parser import HTMLParser
from urllib.parse import urlparse
from common import ROOT

class Page(HTMLParser):
    def __init__(self):super().__init__();self.links=[];self.assets=[];self.bilingual=0
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if 'data-zh' in a:assert a.get('data-en');self.bilingual+=1
        if tag=='a':self.links.append(a.get('href',''))
        if tag in ('script','img') and a.get('src'):self.assets.append(a['src'])
        if tag=='link' and a.get('href'):self.assets.append(a['href'])

def main():
    root=ROOT/'website/dist';page=Page();page.feed((root/'index.html').read_text())
    for path in page.assets:assert (root/path).is_file(),path
    prefix='https://github.com/wZuck/Unextended/'
    repo_links=[]
    for href in page.links:
        if href.startswith('#'):continue
        assert urlparse(href).scheme=='https',href
        if href.startswith(prefix):
            path=href[len(prefix):].split('/',2)
            if path[0] in ('blob','tree'):
                assert path[1]=='main' and (ROOT/path[2]).exists(),href
                repo_links.append(path[2])
    assert page.bilingual>=25 and len(page.assets)>=4
    report={'local_assets':page.assets,'bilingual_elements':page.bilingual,'repository_links':repo_links,
            'static_checks_passed':True,'browser_checks':'Language toggle and responsive iframe QA; see website-qa.json',
            'hosting_audience':'owner-private'}
    (ROOT/'reports/website-check.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))

if __name__=='__main__':main()
