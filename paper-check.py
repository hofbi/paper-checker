#!/bin/python
#
# Quick & dirty python script to check a paper for common English mistakes


# Feature Wishlist:
# - detection of american or british english
# - detection Titles and consistent style (capital or not)  .
# - detection of I/We 
# - detection of grammar errors with be/was/were   DONE
# - detection of plural errors "a cars"          DONE
# - check "to" + passive
# - check "to small, to large"                  DONE
# - check confused verb/noun: the/a + verb
# - check for unnecessary terms: "it is clear", "and so on"  DONE
# - check vague quantifiers such as  "very", "most", "many" "a large number"
# - check Figure in capital
# - check for inconsistent terms:  block chain, blockchain, block-chain, chain of blocks

# - check adposition at the end
# - check noun cluster


# if im präsens → 2. teil in future; if im perfekt → 2. teil in präsens
# If $\Delta t$ is passed as argument, the time dependence is made obvious for the caller. 
# If someone looks over the code later, subprograms that depend on time will be easy to spot.



# not found:  
# ... by but ... => comma or mistake
# is spend => is spent
# paranthesis => parantheses
# ... consensus based ... consensus-based (always -based?)


# Statistics: http://textalyser.net/index.php?lang=en#analysis



# Settings
#===========================================

ANALYZE_SENTENCE = False   # analyze sentence structure, experimental
CFG_INTERACTIVE = False   # ask for action after each error
CFG_PRINT_INPUT = False   # print the intput after pre-processing
MAX_WORDS_PER_SENT = 50

# consistency settings
OXFORD_COMMA=True                 # is oxford comma used?
CAPITAL_HEADINGS=True             # are headings written in capital?
AMERICAN_ENGLISH=True             # If False: British English


OUTPUT_FILENAME = "correction.txt"



# import
#===========================================
from collections import Counter


# own functions
from lib.nlp import *
from lib.stripper import *
from pos.POS_en import *    # part of speech lists


if ANALYZE_SENTENCE:
    from pos.tagger import *


# global state variables
outputLines = []
wasCorrectionMade = False





# checking regex
# ==========================================================
# rePrep = r'(?:about|all|as|at|after|by|between|from|for|in|into|of|on|over|per|that|than|through|towards|under|unless|upon|with|without)'
# reAdpos = rePrep
# reDeterminer = r'(?:all|a|an|another|any|both|each|either|every|half|la|less|many|more|most|much|neither|no|our|several|some|such|that|the|these|this|those|which)'
# reAux = r'(?:can|cannot|could|may|might|must|shall|should|will|would)'
# reSubConjunction = r'(?:as|after|although|as \w\w+ as|because|before|but|even|how|if|in order to|once|since|so that|that|though|unless|until|when|where|whether|why)'
# reAdv = r'\w\w+ly'


reIntroductoryPhrase = r'(Actually|As a result|Additionally|Afterwards|Consequently|However|Finally|First|Furthermore|Therefore|Third(?:ly)?|For example|For (?:this|that) reason|Generally|In general|In fact|In (?:18|19|20)\d\d|In the past|Instead(?! of)|On the other hand|Nevertheless|Nowadays|On the contrary|Recently|Second(?:ly)?|What is more)\s+[a-z]\w+'


reDoublePreposition = r'\s+('+rePrep+')\s+'+rePrep+'\s+'
reDoubleDeterminer = r'\s+('+reDeterminer+')\s+\w+\s+'+reDeterminer+'\s+'

reDoubledParantheses = r'\([^)]\(|\([^)]\)\s*\('

# wrong! depends if used as adjective
reHyphen = r'(anti ?i\w\w+|non ?n\w\w+|class wide|worst case|run time|real time|(?:high|low) level|safety critical|open source|problem solving|right handed|one ?half)'





wrongCharacters = [
    (r'\s(-)\s', '–'),
    (r'(„)', '“'),
    (r'(")\w+', '“'),
    (r'\w+(?:\.|!|?)?(")', '”'),
]







# word lists
# ==========================================================




lstAcronyms = [ 'AC', 'ACM', 'CPU', 'DDR', 'FPGA', 'FSM', 'GNU', 'GPS', 'GUI', 'HF', 'HTML', 'IEEE', 'LED', 'OS', 'PC', 'PCB', 'PDF', 'USB', 'RAM', 'RF', 'ROM', 'VR', 'URL', 'WIFI' ]







# improvement suggestions
# ==========================================================


redundantPhrases = [
    ('all of the', 'all'),
    ('and so on', 'etc.'),
    ('in the case that', 'in case'),
    ('it is clear', ''),
    ('over the time', 'over time'),
    ('sufficient enough', 'sufficient'),
    ('due to the fact that', 'because'),
]



reWrongCombinations = [
 ('last change', 'last chance'),
 ('object orientated', 'object oriented'),
 ('pulse with', 'pulse width'),
 ('time point', 'point in time'),
 ('could of', 'could have'),
 ('de-factor', 'de-facto'),
 ('network package', 'network packet'),
 ('software packet', 'software package'),
]


confusedVerbNoun = [
    ('affect', 'effect'),
    ('ascend', 'ascent'),
    ('build', 'built'),
    ('constrain', 'constraint'),
    ('descend', 'descent'),
    ('live', 'life'),
    ('practice', 'practise'),
    ('prove', 'proof'),
    ('set up', 'setup'),
    ('save', 'safe'),
    ('shut down', 'shutdown'),

]



nonScientific = [
    ('ass', 'as'), 
    ('airs', 'air'), 
    ('angel', 'angle'),
    ('adepts?', 'adapt'),
    ('butt', 'but'),
    ('fir', 'for'),
    ('fife', 'five'),
    ('fuck', ''),
    ('botch', 'both'),
    ('bloody', 'blood'),
    ('altar', 'alter'),
    ('boar', 'board'),
    ('bough', 'bought'),
    ('breech', 'breach'),
    ('bye', 'by'),
    ('canvass', 'canvas'),
    ('coarse', 'course'),
    ('curse', 'course'),
    ('compliment', 'complement'),
    ('discreet', 'discrete'),
    ('decent', 'descend'),   # both?
    ('duel', 'dual'),
    ('exorcise', 'exercise'),
    ('hight', 'height'),
    ('palate', 'palette'),
    ('par', 'part'),
    ('planing', 'planning'),
    ('poop', 'pop'),
    ('principal', 'principle'),
    ('stationery', 'stationary'),
    ('realty', 'reality'),
    ('rite', 'write'),
    ('rise', 'raise'),
    ('shit', 'shift'),
    ('slut', 'slot'),
    ('sown', 'shown'),
    ('stale', 'stable'),
    ('sing', 'sign'),
    ('temper', 'tamper'),
    ('theses', 'these'),
    ('thou', 'you'),
    ('thee', 'you'),
    ('thy', 'your'),
    ('thine', 'your'),
    ('untrue', 'false'),
    ('woks?', 'work'),
    ('withing', 'within'),
    ('ye', 'you'),

    ]




lstInformalWords = [
    ('Also,?', 'Furthermore,'),
    ('[Aa]nyways?', 'nevertheless'),
    ('a couple of', 'several'),
    ('a bit', 'slightly'),
    ('a little bit', 'slightly'),
    #('about '+reNum, 'approximately'),
    ('all right', 'acceptable'),
    ('bad', 'negative'),
    ('big', 'major'),
    ('bug', 'fault'),
    ('But', 'However,'),
    ('cheap', 'inexpensive'),
    ('classical', 'conventional'),
    ('cool', 'great'),
    ('deal with', 'manage'),
    ('easy', 'simple'),
    ('enough', 'sufficient'),
    ('fat', 'heavy'),
    ('good', 'positive'),
    ('kinds', 'types'),
    ('kind of', 'rather'),
    ('like(?! to)', 'such as'),
    ('sort of', 'rather'),
    ('heaps of', 'many'),
    ('huge', 'large'),
    ('nice', 'attractive'),
    ('normal', 'general'),  # conventional
    ('places?', 'location'),
    ('plenty', 'many'),
    ('pretty', 'rather'),
    ('rotations', 'evolutions'),
    ('So', 'Therefore,'),
    ('speed', 'velocity'),
    ('silly', 'inappropriate'),
    ('stuff', 'things'),
    ('stupid', 'inappropriate'),
    ('then', 'subsequently'),
    ('things?', 'object'),
    ('though', 'although'),
    ('wonderful', 'great'),
    ('quite', 'rather'),
    ('whole', 'entire'),
    ('wrong', 'incorrect'),
    ('Well,?', ''),
    ('[Yy]ou', 'one'),
    ('[Yy]our', 'one\'s'),

    # wane, ousted ?
]


lstVague = ('many', 'most', 'some', 'a large number', 'several', 'often', 'a lot', 'few', 'very')


britishAmerican = [
    ('aeroplane', 'airplane'),
    ('aluminium', 'aluminum'),
    ('analyse', 'analyze'),
    ('analogue', 'analog'),
    ('catalogue', 'catalog'),
    ('defence', 'defense'),
    ('licence', 'license'),
    ('centre', 'center'),
    ('fibre', 'fiber'),
    ('behaviour', 'behavior'),
    ('colour', 'color'),
    ('flavour', 'flavor'),
    #(r'\w\wl')
]



synonyms = [ 
    ('show', 'illustrate', 'demonstrate'),
    ('calculate', 'determine'),
    ('analyze', 'evaluate', 'investigate'),
    ('precise', 'concise')
]








# helper functions
######################################################################################

def bold( string ):
    return '\033[1m'+string+'\033[0m'

def red( string ):
    return '\033[91m'+string+'\033[0m'

def green( string ):
    return '\033[32m'+string+'\033[0m'

def setTitle( title ):
    return ''


def readInputFile( fileName ):
    ext = fileName.lower().split('.')[-1]
    inFileHandler = open(fileName,'rb')

    if ext == "pdf":
        import os, subprocess
        SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
        args = ["/usr/bin/pdftotext", '-enc', 'UTF-8', "{}/{}".format(SCRIPT_DIR, fileName), '-']
        res = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        text = res.stdout.decode('utf-8')
        text = re.sub(r'(?<=\n)\w\w?(?=\n)', '', text)

    elif ext in ["txt", "tex", "md"]:     
        text = inFileHandler.read().decode("utf-8")
        inFileHandler.close()

    else:
        raise ValueError("unknown extension: "+ext)

    return text



def writeOutputFile( fileName, text ):
    reply = ''
    while( reply == '' ):
        reply = input("Should the output file "+fileName+" be written? [y/n]")
    if(reply == "y"):
        with open(fileName, "w+") as f:
            f.write(text)


G_issues = ''
def logIssue( ln, msg, match ):
    global G_issues
    G_issues += "Line " + str(ln) + ": " + msg + "("+match+")\n"


def askAction( ln, msg, match, replace):
    print ( bold("Line " + str(ln)) + ": " + msg)
    num_n = match.count('\n')
    outcopy = outputLines[ln-1:ln+num_n]
    replacestr = green("⇒\""+replace+"\"") if (replace != '') else ''
    print (''.join(outcopy).replace(match, red('"'+match+'"') + replacestr) )

    ignoreall = False
    if not CFG_INTERACTIVE: return False
    global wasCorrectionMade
    reply = input("What should we do? (Enter: nothing, r: repair, i:ignore all, q:quit) : ")
    if(reply == "r"):
        if(replace != ''): 
            outputLines[ln-1] = outputLines[ln-1].replace(match, replace, 1)
            wasCorrectionMade = True
    elif(reply == "i"):
        ignoreall = True
    elif(reply == "q"):
        if(wasCorrectionMade):
            writeOutputFile( OUTPUT_FILENAME, '\n'.join(outputLines) )
        sys.exit(0)

    return ignoreall


def findRegEx( regex, text ):
    matches = []
    regex = regex + r'|(\n)'
    line_num = 1
    line_start = 0
    for mo in re.finditer(regex, text):
        if mo.group(mo.lastindex) == '\n':
            line_start = mo.end()
            line_num += 1
        else:
            column = mo.start() - line_start
            matches.append( (line_num, column, mo) )    
            if ('\n' in mo.group(0)): line_num += mo.group(0).count('\n')
    return matches







# features
######################################################################################

def checkDoubledWords(text ):
    matches = findRegEx(r"\s(\w+)\s+\1\s", text)
    for match in matches:
        askAction( match[0], "Found doubled word:", match[2].group(0), " "+match[2].group(1)+" ")

    reTheDet = '(:?[Aa]n?|[Aa]nother|[Aa]ny|[Mm]y|[Oo]ur|[Mm]any|[Nn]o|[Ss]ome|[Tt]he|[Tt]heir|[Tt]his|[Tt]hese|[Tt]hose)'
    matches = findRegEx(r'\s+'+reTheDet+'\s+('+reTheDet+')\s', text)
    for match in matches:
        replace = match[2].group(0).replace(match[2].group(1)+" ", '', 1)
        askAction( match[0], "Found doubled determiner:", match[2].group(0), replace)   

    matches = findRegEx(r'\s+'+reAdpos+'\s+('+reAdpos+')\s', text)
    for match in matches:
        replace = match[2].group(0).replace(match[2].group(1)+" ", '', 1)
        askAction( match[0], "Found doubled adposition:", match[2].group(0), replace)   


def checkAnA( text ):
    # find wrong a
    matches = findRegEx("\s+(a) (?:[AaOoIi]|[Ee][^u]|[Uu][^sn]|[Uu]n[^i]|[Uu]nin|8[- ])\w+\s+" , text )
    matches += findRegEx("\s+(a) (?:[AEFHILMNORSX][A-Z\d]{2,3})\s+" , text )   #3-4 letter acronyms
    for match in matches:
        replace = match[2].group(0).replace(" a ", " an ", 1)
        askAction( match[0], "Possibly misuse of \"a\", could be \"an\": ", match[2].group(0), replace)

    matches = findRegEx(r"\s+(an) [„“”]?(?:[^AaOoEeIiUu\\„“”][a-z]|[^AEFHILMNORSX„“”][^a-z]|[Uu]s|[Uu]ni)\w*\s+" , text )
    for match in matches:
        replace = match[2].group(0).replace(" an ", " a ", 1)
        askAction( match[0], "Possibly misuse of \"an\", could be \"a\": ", match[2].group(0), replace)


def checkToo( text ):
    matches = findRegEx("\s+to\s(:?much|few|low|high|large|big|long|short|small|strong|weak)\s" , text )
    for match in matches:
        replace = match[2].group(0).replace("to", "too", 1)
        askAction( match[0], "Possibly \"too\" instead of \"to\": ", match[2].group(0), replace)


def checkThan( text ):
    matches = findRegEx("\s+(:?more|less|lower|higher|better|worse|larger|bigger|longer|shorter|smaller|stronger)(?: \w\w\w\w+)?(?: \w\w\w\w+)? then " , text )
    matches += findRegEx("\s+(:?rather|further) then " , text )
    for match in matches:
        replace = match[2].group(0).replace("then", "than", 1)
        askAction( match[0], "Possibly misuse of \"then\", could be \"than\": ", match[2].group(0), replace)


def checkCommas( text ):
    matches = findRegEx( reIntroductoryPhrase , text )  # r'\.\s+'+
    for match in matches:
        replace = match[2].group(0).replace( match[2].group(1), match[2].group(1)+",", 1)
        askAction( match[0], "Possibly missing comma after introductory phrase: ", match[2].group(0), replace)

    matches = findRegEx( r'\w+, ('+reSubConjunction+r')\s+\w+' , text )
    for match in matches:
        replace = match[2].group(0).replace( ", "+match[2].group(1), " "+match[2].group(1), 1)
        askAction( match[0], "Possibly no comma before subordinate conjunction: ", match[2].group(0), replace)


def checkWrongAuxiliary( text ):
    matches = findRegEx( r'\s(are|be|been|am|is|was|were|have|has|had)(:?\s\w\w\w+)?\s+(?:be|am|is|was|were|have|has|could|will)\s' , text )
    matches+= findRegEx( r'\s'+reAux+r'\s+(are|been|am|is|was|were|has|had)', text)
    for match in matches:
        replace = match[2].group(0).replace( match[2].group(1)+' ', '', 1)
        askAction( match[0], "Wrong verb structure: ", match[2].group(0), replace)




def checkOxfordComma( text, isUsed ):
    if(isUsed):
        matches = findRegEx( r'\w+,\s+(\w+)\s+and\s+', text )
    else:
        matches = findRegEx( r'\w+,\s+(\w+,)\s+and\s+', text )
    for match in matches:   
        askAction( match[0], "Possibly inconsistent Oxford Comma: ", match[2].group(0), '')


def checkWrongPerson( text ):
    matches = findRegEx( r'\s(?:[Hh]e|[Ss]he|[Ii]t|[Oo]ne|[Tt]his)(:?\salso|\sonly|\s\w\w\w+ly)?\s(have|do|were)\s' , text )
    matches += findRegEx( r'\s(?:[Yy]ou|[We]e|[Tt]hey)(:?\salso|\sonly|\s\w\w\w+ly)?(?:is|has|does|was)\s' , text )
    for match in matches:
        askAction( match[0], "Probably wrong person", match[2].group(0), '')


def checkPlural( text ):
    matches = findRegEx(r"\s+(?:[Aa]n?|[Aa]nother|[Ee]ach)\s+(\w+[^uis'’]s)\s+" , text )
    for match in matches:
        replace = match[2].group(0).replace(match[2].group(1), match[2].group(1)[:-1], 1)
        askAction( match[0], "Possibly wrong plural: ", match[2].group(0), replace)






def checkSimplePast( text ):
    matches = findRegEx( r'\s(?:did) \w\w+ed ' , text )
    for match in matches:
        askAction( match[0], "Probably wrong past", match[2].group(0), '')




def checkNumbers( text ):
    matches = findRegEx( r'\w+ (\d) \w+' , text )
    for match in matches:
        replace = match[2].group(0).replace( match[2].group(1), lstNum[int(match[2].group(1))], 1)
        askAction( match[0], "Number embedded in text, should probably be written as word: ", match[2].group(0), replace)

    matches = findRegEx( r'\w+ (\d\d\d\d\d(?:\.\d+)) \w+' , text )
    for match in matches:
        askAction( match[0], "Large number, you could use a thousand separator: ", match[2].group(0), '')



def checkInformal( text ):
    lstShortForms = [ (r'\w+(n\'t)\s+', 'not'), (r'\w+(\'re)\s+', 'are'), (r'\w+(\'ve)\s+', 'have'), (r'\w+(\'ll)\s+', 'will') ]
    for i, words in enumerate(lstShortForms):
        matches = findRegEx( words[0] , text )
        for match in matches:
            replace = match[2].group(0).replace( match[2].group(1), " "+words[1], 1)
            askAction( match[0], "Short forms are informal: ", match[2].group(0), replace)

    for i, words in enumerate(lstInformalWords):
        matches = findRegEx( r'\W+('+words[0]+')\W+' , text )
        for match in matches:
            replace = match[2].group(0).replace( match[2].group(1), words[1], 1)
            askAction( match[0], "Informal word, could be substituted: ", match[2].group(0), replace)


def checkNonScientific( text ):
    lines = text.split('\n')
    for i, words in enumerate(nonScientific):
        matches = findRegEx( r'\W+('+words[0]+')\W+' , text )
        for match in matches:
            replace = match[2].group(0).replace( match[2].group(1), words[1], 1)
            askAction( match[0], "Probably wrong word in scientific context:" , match[2].group(0), replace) 




def checkVerbPrepositions( text ):
    for verbprep in lstVerbPreposition:
        #matches = findRegEx( r'\W+('+verbprep[0]+')\s+((?!'+verbprep[1]+')\w{2,3})\W+' , text )    # invinitive is most likely a noun!
        verbpl = plural(verbprep[0])
        matches = findRegEx( r'\W+(\w+)\s+('+verbpl+')\s+((?!'+verbprep[1]+')\w{2,3})\W+' , text )
        verpt = past(verbprep[0])
        matches += findRegEx( r'\W+(\w+)\s+('+verpt+')\s+((?!'+verbprep[1]+')\w{2,3})\W+' , text )
        for match in matches:
            if match[2].group(1) not in lstDeterminer and match[2].group(3) in lstAdpos:
                print 
                replace = match[2].group(0).replace( match[2].group(3), verbprep[1], 1)
                askAction( match[0], "Possibly wrong preposition: ", match[2].group(0), replace)



def checkHyphen( text ):
    matches = findRegEx( reHyphen , text )
    for match in matches:
        replace= str(match[2].group(0)).replace(" ", "-")
        askAction( match[0], "Possibly missing hyphen: ", match[2].group(0), replace)

    matches = findRegEx( "\w+(-)\w\w\w+ing" , text )
    for match in matches:
        replace= str(match[2].group(0)).replace("-", " ")
        askAction( match[0], "Probably no hyphen of gerund combination: ", match[2].group(0), replace)      


def checkCapitalPeriod( text ):
    matches = findRegEx( "\w\w\w+(?:\.|!)\s+([a-z]\w+)" , text )
    for match in matches:
        replace = match[2].group(0).replace( match[2].group(1), match[2].group(1).capitalize(), 1)
        askAction( match[0], "Possibly missing capital letter after period: ", match[2].group(0), replace)  






def checkPairs( text ):
    matches = findRegEx( r'\w+\s+(\([^)]+(:?\.\s+[A-Z]))' , text ) # non closing
    matches += findRegEx( r'(\w+\s*\([^)]+\(\s*\w+|\w+\s*\)\s*\(\s*\w+)' , text ) # nested or subsequent parentheses
    #matches += findRegEx( r'(\w\w+\(\w)' , text ) # no space before 
    # @todo: check that the line is not code : no +-/= in the same line
    for match in matches:
        askAction( match[0], "Possibly problem with parentheses: ", match[2].group(0), '')

    matches = findRegEx( r'\s+(“[^”]+“|”\s*“)' , text ) # nested or subsequent “”
    matches += findRegEx( r'\s+(‘[^’]+‘|’\s*‘)' , text ) # nested or subsequent “”
    for match in matches:
        askAction( match[0], "Possibly problem with quotes: ", match[2].group(0), '')
    



def checkAbbreviations( text ):
    foundAbbreviations=lstAcronyms
    matches = findRegEx( r'\s+([A-Z][A-Z])\s+' , text )
    for match in matches:
        if( match[2].group(1) not in foundAbbreviations ):
            askAction( match[0], "Found two character acronym, could be written in full words", match[2].group(0), '')
            foundAbbreviations.append(match[2].group(1))

    matches = findRegEx( r'\s+([A-Z][A-Z][A-Z][A-Z]?[A-Z]?)\s+(?!\(|“)' , text )
    for match in matches:
        if( '('+match[2].group(1)+')' not in text and match[2].group(1) not in foundAbbreviations ):
            askAction( match[0], "Found acronym that was probably never introduced", match[2].group(0), '')
            foundAbbreviations.append(match[2].group(1))




def checkVague( text ):
    """ find some, very, often """
    reVague = '('+'|'.join(lstVague)+')'
    matches = findRegEx( r'\s+'+reVague+r'\s+', text )
    for match in matches:
        askAction( match[0], "Found vague formulation. Can you be more specific?", match[2].group(0), '')




def checkSplitInfinitve( text ):
    matches = findRegEx( r'\sto ('+reAdv+') (\w{4,})' , text )
    for match in matches:
        if match[2].group(2) not in lstDeterminer+lstAdpos+lstConjunction+lstAdv:
            replace = 'to '+match[2].group(2)+' '+match[2].group(1)
            askAction( match[0], "An adverb probably splits an infinitive expression", match[2].group(0), replace)



def checkEndPreposition( text ):
    matches = findRegEx( r'\s+('+rePrep+r')\s+[.!?]' , text )
    for match in matches:
        logIssue( match[0], "Style: Avoid prepositions at the end of sentences", match[2].group(0) )






## Analyze Sentences
##########################

# check length: > 50 words is too long


def checkSentences( text ):
    sentences = split2sentences( text )
    for sentence in sentences:  
        words = split2words( sentence )
        # check length
        if len(words) > MAX_WORDS_PER_SENT: print(bold('Sentence too long ')+'({} words): '.format(len(words))+sentence[:MAX_WORDS_PER_SENT]+'...')




## Analyze TeX
# - check itemize starts with capital/lowercase consistent, headings consistent
# - check that each section has at least 2 subsections etc.
# - check that itemize has dots
# - check number of references and how often cited
# - check label/ref, centering in figure, tables with @{} consistence, check SI units 
# - check caption has period, analyze abstract, 
# - check figures referenced in text  DONE
##########################


def analyzeTeX( text ):
    print("\n\nTeX Analysis:")
    print('----------------------------------------------------')
    text = re.sub(r'(?<!\\)\%.*?\n', r'\n', text)     # remove comments
    # checkTeXheadings( text )
    checkTeXreferences( text )
    checkTeXmath( text )
    print('----------------------------------------------------\n\n')



def checkTeXheadings( text ):
    lstTeXHeading = ['title', 'chapter', 'section', 'subsection', 'subsubsection', 'paragraph']
    for heading in lstTeXHeading:
        matches = findRegEx(r'\\'+heading+r'\{([^}]*?)\}',  text)
        for match in matches:
            words = split2words(match[2].group(1))
            for word in words:
                if len(word) > 3 and word[0].islower() and word not in lstAdpos+lstDet+lstConjunction:
                    #askAction( match[0], "Lowercase letter in heading:" , word, word.capitalize())
                    print("Lowercase letter in heading: ", match[2].group(1))
                    break




def checkTeXreferences( text ):
    refs = {}
    matches = re.findall(r'\\cite\{([^}]+)\}', text)
    for match in matches:
        refs[match] = refs[match] + 1 if match in refs.keys() else 1
    print("found {} references and {} citations.".format( len(refs.keys()), len(matches) ))

    matches = re.findall(r'\\label\{([^}]+)\}', text)
    for match in matches:
        if re.search(r'ref\{\s*'+re.escape(match)+r'\s*\}', text) == None:
            print(" * WARN: unused label: {}".format(match))

    matches = findRegEx(r'\\caption\{([^}]+)\}\s*\n', text)
    for match in matches:
        if match[2].group(1)[-1] != '.':
            print(" * WARN: caption missing period (line {})".format(match[0]))



def checkTeXmath( text ):
    reFunction = r'(sin|cos|tan|log|min|max|exp)'
    matches = findRegEx(r'\\begin\{equation\}\s*\n\s*([^$]+?)\s*\n\s*\\end\{equation\}', text)
    # matched = findRegEx(r'\s\$(\S[^$]+\S)\$\s', text)
    for match in matches:
        #print(match[2].group(1))
        fun = re.search(r'(?:\s|[\(\)\*])'+reFunction, match[2].group(1))
        if fun != None:
            print(" * WARN: use \"\\{}\" instead of \"{}\". (Equation ln. {})".format(fun.group(1), fun.group(1), match[0]) )







## Statistics
##########################
G_stats = {}
G_words = {}



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
    print('      Words: {} ({} unique)     '.format(G_stats['words'], G_stats['unique_words']) )
    print('             characters: {} .. {} ({:.2f} avg.)'.format(G_stats['word_length_min'], G_stats['word_length_max'], G_stats['word_length_avg']) )
    # print('             syllables:  {} .. {} ({:.2f} avg.)'.format(G_stats['syl_per_word_min'], G_stats['syl_per_word_max'], G_stats['syl_per_word_avg']) )
    print('                                ')
    print('  Sentences: {}                 '.format(G_stats['sentences']) )
    print('             words: {} .. {} ({:.2f} avg.)'.format(G_stats['words_per_sent_min'], G_stats['words_per_sent_max'], G_stats['words_per_sent_avg']) )
    print("----------------------------------------------------\n")

    # number of POS: nouns, verbs, etc.
    print('Most frequent words: '+str(G_stats['common_words']))

    statsReferences( text )




# main parsing function
######################################################################################

def parseFile( fileName ):
    fileBaseName, ext = os.path.splitext(fileName)

    text = readInputFile( fileName )

    # process TeX
    if fileName.endswith('.tex'):
        analyzeTeX( text )  
        text = stripTeX( text, True )


    global outputLines
    outputLines = text.splitlines(True)

    if CFG_PRINT_INPUT:
        for idx, line in enumerate(outputLines):
            print("#{}: {}".format(idx, line), end='')
        

    # show stats
    showStats(text)


    # reliable, critical checks
    print('\n\nCritical Mistakes:\n---------------------')
    checkDoubledWords( text )   # no false alarms, no missed errors
    checkAnA(text)              # almost no false alarms
    checkWrongPerson( text )
    checkPlural( text )
    checkThan(text)             # quite good
    checkToo(text)             
    checkWrongAuxiliary( text )


    # working checks
    print('\n\nNormal Mistakes:\n---------------------')
    # checkVerbPrepositions( text )
    # checkCapitalPeriod( text )
    checkNonScientific( text )  # few false alarms
    checkHyphen( text )     # few false alarms
    checkCommas( text )     # many false alarms


    # experimental
    print('\n\nImprovements:\n---------------------')
    checkVague( text )
    checkSplitInfinitve( text )
    checkNumbers( text )    # reliable
    checkAbbreviations( text )
    checkPairs( text )   # many false alarms
    checkInformal(text)


    #regex finiter: https://docs.python.org/3/library/re.html#writing-a-tokenizer
    if ANALYZE_SENTENCE:
        checkSentences( text )



    if(wasCorrectionMade):
        writeOutputFile( OUTPUT_FILENAME, '\n'.join(outputLines) )


# Main Program
#############################################
import fileinput
import sys
import os
import re


# check arguments
args = sys.argv[1:]
if len(args) == 0:
    print("Usage: python paper-check.py FILE")
    sys.exit(0)

for arg in args:
    parseFile(arg)
    sys.exit(0)