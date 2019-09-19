
import re
from collections import Counter


from lib.nlp import *
from pos.POS_en import *


## Statistics
##########################
G_stats = {}
G_words = {}


lstVague = ('a large number', 'a lot', 'few', 'many', 'most', 'some', 'really', 'several', 'often', 'very', 'quite')




def statsReferences( text ):
    refs = []
    matches = re.findall( r'\[(\d\d?)\]\.', text )
    for match in matches:
        refs.append(match[0])
    print("References: ")
    print(refs)




def calcStats( text ):
    # todo: sentences, sentence lengths, words, cohesion, text difficulty

    text = text.strip()

    global G_stats
    # init
    G_stats['words'] = 0
    G_stats['letters_all'] = len(text)
    G_stats['characters_no_white'] = len(re.sub(r'\s+', '', text))
    G_stats['characters_words'] = 0
    G_stats['unique_words'] = 0
    G_stats['word_length_min'] = 1000
    G_stats['word_length_avg'] = 0
    G_stats['word_length_max'] = 0
    G_stats['vague_words'] = 0
    G_stats['syl_per_word_min'] = 1000
    G_stats['syl_per_word_max'] = 0
    G_stats['syl_per_word_avg'] = 0
    G_stats['words_per_sent_min'] = 1000
    G_stats['words_per_sent_max'] = 0
    G_stats['words_per_sent_avg'] = 0


    sentences = split2sentences( text )

    G_stats['sentences'] = len(sentences)

    all_words = []
    for sentence in sentences:
        words = split2words( sentence )
        if len(words) < G_stats['words_per_sent_min']: 
            G_stats['words_per_sent_min'] = len(words)
            G_stats['shortest_sent'] = sentence
        if len(words) > G_stats['words_per_sent_max']: 
            G_stats['words_per_sent_max'] = len(words)
            G_stats['longest_sent'] = sentence
        G_stats['words_per_sent_avg'] += len(words)/len(sentences)
        all_words += words


    # look at words
    for word in all_words:
        # #print(word+': '+str(syllables(word)))
        # syls = syllables(word)
        # if( syls < G_stats['syl_per_word_min'] ): 
        #   G_stats['syl_per_word_min'] = syllables(word)
        # if( syls > G_stats['syl_per_word_max'] ): 
        #   G_stats['syl_per_word_max'] = syllables(word)
        #   #G_stats['most_syls'] = word
        # G_stats['syl_per_word_avg'] += (syllables(word) / len(all_words))

        if word in lstVague: G_stats['vague_words'] += 1
        
        G_stats['characters_words'] += len(word)
        
        if len(word) < G_stats['word_length_min']: G_stats['word_length_min'] = len(word)
        if len(word) > G_stats['word_length_max']: G_stats['word_length_max'] = len(word)
        G_stats['word_length_avg'] += (len(word) / len(all_words))
        
        if len(word) > 5:
            pass


    G_stats['words'] = len(all_words)
    G_stats['unique_words'] = len(set(all_words))
    long_words = [ x.lower() for x in all_words if len(x) > 5]
    word_count = Counter(long_words)
    G_stats['common_words'] = word_count.most_common(6)



# todo: print table, color values (good/bad)
# metric, avg±dev, [min,max], good range
def showStats( text ):
    global G_stats
    calcStats(text)

    print("Text Statisics:")
    print('----------------------------------------------------')
    print(' Characters: {} (incl. spaces)  '.format(G_stats['letters_all']))
    print('             {} (excl. spaces)  '.format(G_stats['characters_no_white']))
    print('             {} (only words)    '.format(G_stats['characters_words']))
    print('                                ')
    print('      Words: {} (total)          '.format(G_stats['words']) )
    print('             {} (unique, {} %)'.format(G_stats['unique_words'], round(100*G_stats['unique_words']/G_stats['words'])) )
    print('             chars per word: {} .. {} ({:.2f} avg.)'.format(G_stats['word_length_min'], G_stats['word_length_max'], G_stats['word_length_avg']) )
    # print('             syllables:  {} .. {} ({:.2f} avg.)'.format(G_stats['syl_per_word_min'], G_stats['syl_per_word_max'], G_stats['syl_per_word_avg']) )
    print('                                ')
    print('  Sentences: {}                 '.format(G_stats['sentences']) )
    print('             words per sent: {} .. {} ({:.2f} avg.)'.format(G_stats['words_per_sent_min'], G_stats['words_per_sent_max'], G_stats['words_per_sent_avg']) )
    print("----------------------------------------------------\n")

    print("Vague words: {}".format(G_stats['vague_words']))

    # number of POS: nouns, verbs, etc.
    print('Most frequent words: '+str(G_stats['common_words']))

    statsReferences( text )

