from jutil import *


def main():
    top = f_read('../top.html').replace('</p></body></html>','')
    pages = ['index', 'most_wanted', 'log_games', 'bounties', 'black_market']
    for page in pages:
        des = '../{page}.html'
        bot_split = '<div id="bot">'
        bot = bot_split + f_read(des).split(bot_split)[1]
        f_write(des, rsf('~top\n~bot'))
    

if __name__ == '__main__':
    main()