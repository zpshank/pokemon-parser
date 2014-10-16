# coding=utf-8
__author__ = 'zackshank'
import sys
import urllib
import getopt
from bs4 import BeautifulSoup

#filter for moves
def is_move_or_header(tag):
    return (tag.has_attr('class') and tag.has_attr('colspan')
            and tag.get('class')[0] == 'fooevo'
            and (tag.get('colspan') == '9'
                 or tag.get('colspan') == '10')) \
        or (tag.has_attr('class') and tag.has_attr('rowspan') and tag.get('class')[0] == 'fooinfo' and tag.get('rowspan') == '2')

#Constants
LEVEL_UP_MOVES = 'LEVEL_UP_MOVES'
MACHINE_MOVES = 'MACHINE_MOVES'
EGG_MOVES = 'EGG_MOVES'
TUTOR_MOVES = 'TUTOR_MOVES'
TRANSFER_MOVES = 'TRANSFER_MOVES'


outputFile = ''
pokemonStart = 1
pokemonEnd = 719

# Get options
try:
    opts, args = getopt.getopt(sys.argv[1:], 'hs:f:o:')
except getopt.GetoptError:
    print 'python pokemon_parser.py -s <start_number> -f <finish_number> -o <outputfile>'
    sys.exit(2)
for opt, arg in opts:
    if opt == '-h':
        print 'python pokemon_parser.py -s <start number> -f <finish number> -o <outputfile>'
        sys.exit()
    elif opt in "-s":
        pokemonStart = arg
    elif opt in "-f":
        pokemonEnd = arg
    elif opt in "-o":
        outputFile = open(arg, 'w')


pokemonId = int(pokemonStart)
while pokemonId <= int(pokemonEnd):
    #Issue with Wormadam
    if pokemonId != 413:
        response = urllib.urlopen("http://www.serebii.net/pokedex-xy/{0:03d}.shtml".format(pokemonId))
        html = response.read()
        soup = BeautifulSoup(html)
        print('Writing: ' + soup.title.string)
        # soup.originalEncoding
        #for dextable in soup.find_all('table', class_='dextable'):
        #    print(dextable[0])
        moves = soup.find_all(is_move_or_header)
        section = ''
        moveIndex = 0
        sectionTitle = ''
        while moveIndex < len(moves):
            move = moves[moveIndex]
            #Check to see if in new section
            if move.get('class')[0] == 'fooevo':
                #if we are in a new section set the new section
                if 'X / Y Level Up' in unicode(move).encode('utf-8'):
                    sectionTitle = move.string
                    section = LEVEL_UP_MOVES
                elif 'HM Attacks' in unicode(move).encode('utf-8'):
                    sectionTitle = 'TM & HM Attacks'
                    section = MACHINE_MOVES
                elif 'Egg Moves' in unicode(move).encode('utf-8'):
                    sectionTitle = 'Egg Moves'
                    section = EGG_MOVES
                elif 'Move Tutor Attacks' in move:
                    sectionTitle = 'Move Tutor Attacks'
                    section = TUTOR_MOVES
                elif 'Transfer Only Moves' in unicode(move).encode('utf-8'):
                    sectionTitle = 'Transfer Only Moves'
                    section = TRANSFER_MOVES
                else:
                    section = 'None'
                moveIndex += 1
            #else continue with section operations
            else:
                if section == LEVEL_UP_MOVES:
                    if not 'Max Stats' in unicode(move.string).encode('utf-8'):
                        moveLevel = unicode(move.string).encode('utf-8')
                        if moveLevel == '—':
                            moveLevel = '0'
                        moveName = unicode(moves[moveIndex+1].a.string).encode('utf-8')
                        outputFile.write("{},Level {},{},{}\n".format(pokemonId, moveLevel, moveName, sectionTitle))
                        moveIndex += 2
                    else:
                        moveIndex += 1
                elif section == MACHINE_MOVES:
                    if not 'Max Stats' in unicode(move).encode('utf-8'):
                        moveMachine = unicode(move.string).encode('utf-8')
                        moveName = unicode(moves[moveIndex+1].a.string).encode('utf-8')
                        outputFile.write("{},{},{},{}\n".format(pokemonId, moveMachine, moveName, sectionTitle))
                        moveIndex += 2
                    else:
                        moveIndex += 1
                elif section == EGG_MOVES:
                    moveName = unicode(move.string).encode('utf-8')
                    outputFile.write("{},Egg,{},{}\n".format(pokemonId, moveName, sectionTitle))
                    moveIndex += 2
                elif section == TUTOR_MOVES:
                    moveName = unicode(move.string).encode('utf-8')
                    outputFile.write("{},Tutor,{},{}\n".format(pokemonId, moveName, sectionTitle))
                    moveIndex += 1
                elif section == TRANSFER_MOVES:
                    # Avoid Max Stats
                    if not 'Max Stats' in unicode(move).encode('utf-8'):
                        moveName = unicode(move.string).encode('utf-8')
                        moveTransfer = unicode(moves[moveIndex+1].string).encode('utf-8')
                        outputFile.write("{},Transfer ({}),{}, {}\n".format(pokemonId,moveTransfer, moveName, sectionTitle))
                    moveIndex += 2
                else:
                    moveIndex += 1

    pokemonId += 1

outputFile.close()
