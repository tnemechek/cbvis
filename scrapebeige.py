import requests
from bs4 import BeautifulSoup
import os


beigeurl = 'https://www.federalreserve.gov/monetarypolicy/publications/beige-book-default.htm'
wdir = os.getcwd().replace('\\', '/')


def pollReleases(url=beigeurl, fdir='BeigeBook', dotext='.pdf'):
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')
    links_all = soup.find_all('a', href=True)
    links_tgt = [link['href'] for link in links_all if fdir in link['href'] and link['href'].endswith(dotext)]
    if links_tgt:
        return ['https://www.federalreserve.gov' + l for l in links_tgt]
    else:
        raise Exception(f'no links to "{fdir}" {dotext} files found at\n{url}')


def fname_from_url(url):
    return url.rsplit('/')[-1]


def path_from_fname(fname):
    return os.path.abspath(fname).replace('\\', '/').replace(fname, f'{fname.split("_")[0]}/{fname}')


def checkExisting(fdir='BeigeBook', dotext='.pdf'):
    fnames = os.listdir(f'{wdir}/{fdir}')
    if not dotext:
        return fnames
    else:
        return  [fname for fname in fnames if fname.endswith(dotext)]


def getFpaths(fdir='BeigeBook', dotext='.pdf'):
    fnames_existing = checkExisting(fdir, dotext)
    fpaths_existing = [path_from_fname(fname) for fname in fnames_existing]
    fpaths_existing.sort(reverse=True)
    return fpaths_existing


def getNew(
        links=None,
        fdir='BeigeBook',
        dotext='.pdf'
        ):

    if not links:
        links = pollReleases(url=beigeurl, fdir='BeigeBook', dotext='.pdf')

    fnames = [fname_from_url(link) for link in links]
    fnames_new = [fname for fname in fnames if fname not in checkExisting(fdir)]
    links_new = [links[fnames.index(fname)] for fname in fnames_new]

    fpaths_new = []
    for link, fname in zip(links_new, fnames_new):
        r = requests.get(link)
        fpath = f'{wdir}/{fdir}/{fname}'
        fpaths_new.append(fpath)
        with open(fpath, 'wb') as f: f.write(r.content)
        print(f'downloaded file: {link} --> \n{fpath}')
    return fpaths_new
    # return [path_from_fname(fname) for fname in checkExisting(fdir=fdir, dotext=dotext)]