import pronouncing as pn
import re, os

'''SYLLABLE KEY: 
    -   emphasized syllable
    u   unemphasized syllable
    x   any syllable
    U   either - or uu
    /   line break
    |   word break
    :   Repeat the pattern'''


global meters, enabled

METERS = [
    ("iambic-pentameter", "u-u-u-u-u-:"),
    ("iambic-pentameter", "-uu-u-u-u-:"),
    ("dactylic-hexameter", "-U-U-U-U-uu-x:"),
    ("hendecasyllabic", "x--uu-u-u-x:"),
    ("hendecasyllabic", "-x-uu-u-u-x:"),
    ("haiku", "xxxxx/xxxxxxx/xxxxx"),
    ("elegiac-couplet", "-U-U-U-U-uu-x/-U-U-|-uu-uu-:"),
    ("trochaic-tetrameter", '-u-u-u-u:'),
    ]

enabled = {
    "iambic-pentameter":True,
    "dactylic-hexameter":False,
    "hendecasyllabic":True,
    "haiku":False,
    "elegiac-couplet":True,
    "trochaic-tetrameter":False,
}

MODIFICATIONS = {"traveller":['-uu', '-u'], "@":['u', '-'], "&":['u', '-'], "%":['u-'], "hexameter":['--uu', 'u-uu'], "pentameter":['u-uu', '-u-u'],"catullus":['u-u'],
    "providence":['-uu', '-u-'], "fountains":['-u', '--'], "indolent":['-uu', '-u-'], "toil":['-', '-u'], '/':['u', '-'], '+':['u', '-'], '-':['-u'], "myself":['--', 'u-'] }

DESCRIPTION = {"iambic-pentameter":"`u-u-u-u-u-` or `-uu-u-u-u-`. Shakespeare's meter, and the most common English meter.",
"dactylic_hexameter":"`-U-U-U-U-uu-x`, where each `U` represents either `uu` or `-`, and `x` can be either `-` or `u`, your choice. Vergil's meter, and a common one in Latin epic poetry. Not very common in English.",
"hendecasyllabic":"`---uu-u-u-x`, where `x` represents either `-` or `u`. Catullus's meter, commonly used for somewhat lighthearted poetry in Latin. Not very common in English. At most one of the first two syllables is allowed to be short.",
"haiku":"Look it up, chief.",
"elegiac-couplet":"A mournful meter, coming in pairs: the first line is dactylic-hexameter, and the second is `-U-U-|-uu-uu-` where `|` represents a division between two words.",
"trochaic-tetrameter":"`-u-u-u-u`. A meter sometimes used by Shakespeare for spells and witchery."}

EXAMPLES = {"iambic-pentameter":"""_The world was all before them: where to choose
Their place of rest, and Providence their guide._
--_Paradise Lost_, by John Milton.""",
"Dactylic_hexameter":"""_In the hexameter rises the fountain's silvery column._
--"The Ovidian Elegiac Metre" by Samuel Taylor Coleridge""",
"hendecasyllabic":"""_O you chorus of indolent reviewers,
Irresponsible, indolent reviewers,
Look, I come to the test, a tiny poem
All composed in a metre of Catullus_
---"For Once Then Something" by Alfred Tennyson""",
"haiku":"""_An old silent pond
A frog jumps into the pond—
Splash! Silence again._
--"The old pond" by Matsuo Basho""",
"elegiac-couplet":"""_In the hexameter rises the fountain's silvery column,
In the pentameter aye falling in melody back._
--"The Ovidian Elegiac Metre" by Samuel Taylor Coleridge""",
"trochaic-tetrameter":"""_Double, double, toil and trouble;
Fire burn and cauldron bubble_
--_Macbeth_ by William Shakespeare"""}

MAX_LENGTH = 25


def getPatterns(word):
    try:
        return MODIFICATIONS[word.lower()]
    except:
        pass

    while word[-1].upper()==word[-1].lower():
        word = word[:-1]

    # Handle numbers
    n=None
    try:
        n=float(word)
    except:
        pass
    if n != None:
        raise Exception("Numbers aren't handled yet: "+word)

    # Handle words with dots in them
    if word.endswith('.com') or word.endswith('.org') or word.endswith('.net') or word.endswith('.edu'):
        res = getPatterns[word[:-4]]
        return [r + '--' for r in res]
    if word.endswith('.us'):
        res = getPatterns[word[:-3]]
        return [r + 'uu' for r in res]
    if word.endswith('.eu') or word.endswith('.au'):
        res = getPatterns[word[:-3]]
        return [r + '--' for r in res]
    

    phones = pn.phones_for_word(word)
    if len(phones) == 0:
        if(word.endswith('\'s')):
            try:
                return getPatterns(word[:-2]+'s')
            except:
                return getPatterns(word[:-2])
        raise Exception("Encountered unknown word "+word)
    results = []
    for p in phones:
        stresses = pn.stresses(p)
        if len(stresses) == 1:
            if '-' not in results: results.append('-')
            if 'u' not in results: results.append('u')
            continue
        line = ""
        for letter in stresses:
            if letter == '0':
                line+= 'u' 
            else:
                line += '-'
        if line not in results:
            results.append(line)
    return results

class ScanNode: # A state machine indicating a certain way to scan a passage.
    def __init__(self):
        self.possibleIndices = list(range(len(meters)))
        self.meterIndex = [0]*len(meters)
        self.breaks = []
        for i in range(len(meters)):
            self.breaks.append([])

    def copy(self):
        r = ScanNode()
        r.possibleIndices = self.possibleIndices[:]
        r.meterIndex = self.meterIndex[:]
        for i in range(len(meters)):
            r.breaks[i] = self.breaks[i][:]
        return r

    def scanPattern(self, pattern, wordIndex):
        remove = []
        for i in self.possibleIndices:
            start = True
            for letter in pattern:
                # Process special characters
                if self.meterIndex[i] >= len(meters[i][1]):
                    remove.append(i)
                    break # Failed the U test

                if type(self.meterIndex[i]) == int:
                    if meters[i][1][self.meterIndex[i]] == ":": # repeat the meter
                        if start:
                            self.meterIndex[i] = 0
                            self.breaks[i].append(wordIndex)
                        else:
                            remove.append(i)
                            break # line break occurred in middle of word
                    if meters[i][1][self.meterIndex[i]] == "/":
                        if start:
                            self.meterIndex[i]+= 1
                            self.breaks[i].append(wordIndex)
                        else:
                            remove.append(i)
                            break # line break occurred in middle of word
                    if meters[i][1][self.meterIndex[i]] == "|":
                        if start:
                            self.meterIndex[i] += 1
                        else:
                            remove.append(i)
                            break # word break occurred in middle of word

                start = False
                # Start matching to the meter
                if type(self.meterIndex[i]) == float:
                    if letter == 'u':
                        self.meterIndex[i] = int(self.meterIndex[i]) + 1
                        continue
                    else:
                        remove.append(i)
                        break # Failed the U test
                if letter == meters[i][1][self.meterIndex[i]]:
                    self.meterIndex[i] += 1
                    continue
                if meters[i][1][self.meterIndex[i]] == 'x':
                    self.meterIndex[i] += 1
                    continue
                if meters[i][1][self.meterIndex[i]] == 'U':
                    if letter == '-':
                        self.meterIndex[i] += 1
                        continue
                    else:
                        self.meterIndex[i] += 0.5
                        continue
                remove.append(i)
                break # Did not match

        for i in remove:
            self.possibleIndices.remove(i)

        if len(self.possibleIndices) == 0:
            return False
        return True

    def assertEnd(self):
        index = 0
        while index < len(self.possibleIndices):
            i =self.possibleIndices[index]
            if self.meterIndex[i] >= len(meters[i][1]): # If I'm out of meter
                index+=1
                continue
            if type(self.meterIndex[i]) == float: # If I'm in the middle of a U
                del self.possibleIndices[index]
                continue
            for letter in meters[i][1][self.meterIndex[i]:]:
                if letter in ['-', 'u', 'x', 'U']: # Part of the meter remains:
                    del self.possibleIndices[index]
                    index-=1
                    break
            index+=1
        if len(self.possibleIndices) == 0:
            return False
        else:
            return True
   

def fitToMeter(text):
    maxNumNodes = 0
    words = re.split(' |\n', text)
    
    for i in range(len(words)):
        if len(words[i]) > MAX_LENGTH:
            raise Exception ("Word too long")
    
        # Strip end punctuation
        while words[i][-1].upper()==words[i][-1].lower() and words[i][-1] not in ['.', ',', '!', '?', ':', ';', '-']:
            words[i] = words[i][:-1]
        while words[i][0].upper()==words[i][0].lower():
            words[i] = words[i][1:]

        # Throw in other cases
        existsNonLetter = False
        for letter in words[i]:
            if letter.upper() == letter.lower() and letter != "'":
                existsNonLetter = True
            else:
                if existsNonLetter:
                    raise Exception("Word contains inner punctuation: "+words[i])

    patterns = []
    i = 0
    while i < len(words):
        if words[i] == "":
            del words[i]
            continue
        p = getPatterns(words[i])
        patterns.append(p)
        i+=1

    nodes = [[ScanNode(), 0, 0]] # Format: node, word to start on, pattern index under question
    while len(nodes) > 0:
        killNode = False
        for i in range(nodes[0][1], len(words)):
            if killNode:
                break
            maxNumNodes = max(maxNumNodes, len(nodes))

            if len(patterns[i]) - 1 > nodes[0][2]: # When there are multiple possible pronunciations and this word has not been encountered
                nodes.append([nodes[0][0].copy(), i, nodes[0][2] + 1])# Save the next path for later
            if nodes[0][0].scanPattern(patterns[i][nodes[0][2]], i):
                nodes[0][2] = 0 # From now on, use the first possible translation and save the rest for later.
            else:
                killNode = True
                break

        if not killNode: # The entire thing was successfully translated!
            if nodes[0][0].assertEnd(): # Check that the node is at the end of the meter line
                
                index = nodes[0][0].possibleIndices[0]
                text = ""
                for i in range(len(words)):
                    if i in nodes[0][0].breaks[index]:
                        text += '\n'
                    text += words[i] + ' '
                return meters[index][0], text[:-1]
        del nodes[0]
    return None, None


def makeMeters():
    global meters
    meters=METERS
    meters = []
    for name, meter in METERS:
        if enabled[name]:
            meters.append((name, meter))

def loadEnabled():
    global enabled
    if not os.path.exists("enabled.txt"):
        return
    f = open('enabled.txt', 'r')
    for line in f.read().split('\n'):
        if line == '': continue
        name, value = line.split(':')
        enabled[name] = (True if value == 't' else False)

def saveEnabled():
    f = open('enabled.txt', 'w')
    for k, v in enabled.items():
        f.write(k+':'+('t' if v else 'f')+'\n')


def init():
    loadEnabled()
    makeMeters()
    
    print("Initialization completed")

if __name__ == "__main__":
    init()
    print(getPatterns("myself"))
    print(fitToMeter('''i don't quite know myself, i'd love to see'''))