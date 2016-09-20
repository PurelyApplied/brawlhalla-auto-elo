#!/usr/bin/env python3
'''Run while playing Brawlhalla, during opponent loading screen,
 to fetch and display ranked 1s elo.
 
 Written by Patrick "PurelyApplied" Rhomberg, 2016-09-01
'''

# Known issues:
# ImageGrab.grab() fails on non-primary monitors
 
from enum import Enum
try:
     import Image
except:
    from PIL import ImageGrab, Image

import requests
from bs4 import BeautifulSoup as BS
import win32gui
import pytesseract

SERVERS = Enum("server",
               ["us-e", "eu", "sea", "brz", "aus", "us-w", "any"])
LEGENDS = Enum("legend",
               ["Bodvar", "Cassidy", "Orion", "Lord Vraxx	",
                "Gnash", "Queen Nai", "Hattori",
                "Sir Roland", "Scarlet", "Thatch", "Ada",
                "Sentinel", "Lucien", "Teros",
                "Brynn", "Asuri", "Barraza", "Ember", "Azoth", "Koji", "Ulgrim",
                "Diana", "Jhala", "Kor", "Wu Shang", "Val"])




class LadderStanding:
    def __init__(self, rank, region, player, wins_loss, rating, peak):
        '''All are passed as strings.'''
        self.player = player
        self.rank = rank
        self.region = region
        #        self.tier = tier
        self.wins, self.loss = wins_loss.split("-")
        self.rating = rating
        self.peak = peak
        self.all = player, rank, region, self.wins, self.loss, rating, peak
        
    def __str__(self):
        return (
            "{}:\n  Rank:\t\t{}\n  Region:\t{}\n  "
            "Record:\t{}-{}\n  Elo (Peak):\t{} ({})".format(
                self.player, *self.all[1:]))

    def __repr__(self):
        return "<LadderStanding: {}>".format(self.player)
        
        
def main(server=SERVERS.any):
    player_list = screencap_players()
    for player in player_list:
        page = fetch_elo_page(player, server)
        ladder_entries = process_page(page)
    print("\n".join(str(e) for e in ladder_entries))


def process_page(page_request):
    soup = BS(page_request.text)
    contents = list(soup.strings)
    i = contents.index("Peak Rating") + 1
    ladder_entries = []
    block_size = 6
    while i + block_size - 1 < len(contents):
        ladder_entries.append(LadderStanding(*contents[i:i+block_size]))
        i += block_size
    return ladder_entries
    

def fetch_elo_page(player, server=SERVERS.any):
    url = r"http://www.brawlhalla.com/rankings/1v1/"
    if server != SERVERS.any:
        url += server.name + "/"
    url += "?p=" + player
    return requests.get(url)


def screencap_players():
     handle = win32gui.FindWindow(None, "Brawlhalla")
     bbox = win32gui.GetWindowRect(handle)
     win32gui.BringWindowtoTop(handle)
     img = ImageGrab.grab(get_window_box())
     return pytesseract.image_to_string(img)


def test():
    img = Image.open("test.jpg")
    text = pytesseract.image_to_string(img)
    word_list = [w.strip() for w in text.split("\n") if w.strip()]
    return word_list
