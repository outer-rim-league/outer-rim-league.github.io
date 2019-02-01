from jutil import *


def main():
    src = '../top.html'
    print rsf('\nReading ~src\n')
    top = f_read(src).replace('</p></body></html>', '')
    pages = ['index', 'most_wanted', 'log_games', 'bounties', 'black_market']
    for page in pages:
        des = '../{page}.html'
        bot_split = '<div id="bot">'
        bot = bot_split + f_read(des).split(bot_split)[1]
        print rsf('Writing ~des')
        f_write(des, top + '\n' + bot)
    

if __name__ == '__main__':
    main()