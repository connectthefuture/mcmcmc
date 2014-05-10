import nltk
import random
import string
import json
from flask import Flask

app = Flask(__name__)

class MCMCMC(object):

    def __init__(self, n = 3, rhyme_level = 2):
        self.n = n
        self.chains = { }
        self.chains_backwards = { }
        self.words = set()
        self.rhyme_cache = { }
        self.rhyme_level = rhyme_level
        
    def rhyme(self, inp, level):
        try:
            return self.rhyme_cache[self.syllable_map[inp]]
        except KeyError:
            return []

    def build_rhyme_cache(self):
        level = self.rhyme_level
        cache = { }
        entries = nltk.corpus.cmudict.entries()
        syllables = [(word, syl) for word, syl in entries if word in self.words]
        syllable_map = {word : tuple(syllable[-level:]) for word, syllable in syllables}
        for (word, syllable) in syllables:
            try:
                cache[tuple(syllable[-level:])].add(word)
            except KeyError:
                cache[tuple(syllable[-level:])] = set((word,))
        self.rhyme_cache = cache
        self.syllable_map = syllable_map
        
    def get_sets(self, text):
        if len(text) < self.n:
            return
          
        for i in range(len(text) - self.n):
            yield [text[i + x] for x in range(self.n)]
 
        
    def update_chains(self, text):
        self.update_forward_chain(text)
        self.update_backwards_chain(text)
        self.build_rhyme_cache()
        
    def update_backwards_chain(self, text):
        split = text.split()[::-1]
        for x in self.get_sets(split):
            try:
                self.chains_backwards[tuple(x[:-1])].append(x[-1])
            except KeyError:
                self.chains_backwards[tuple(x[:-1])] = [x[-1]]

    def update_forward_chain(self, text):
        split = text.split()
        for x in self.get_sets(split):
            self.words.add(x[-1])
            try:
                self.chains[tuple(x[:-1])].append(x[-1])
            except KeyError:
                self.chains[tuple(x[:-1])] = [x[-1]]
        
    def generate_line(self, line_length, backwards = False, start_word = None):
        if not backwards:
            chains = self.chains
        else:
            chains = self.chains_backwards
        
        if start_word:
            current_phrase = random.choice([x for x in chains.keys() if x[0] == start_word])
        else:
            current_phrase = random.choice(chains.keys())
        words = list(current_phrase)
        for i in range(0, line_length - self.n + 1):
            try:
                next_word = random.choice(chains[current_phrase])
            except KeyError:
                break
            
            words.append(next_word)
            current_phrase = current_phrase[1:] + (next_word,)

        if backwards:
            return ' '.join(words[::-1])
        return ' '.join(words)
        
def load_rap():
    a = json.load(open("scrubbed_lyrics.json", "r"))
    all_lyrics = []
    for x in a:
        all_lyrics.append(x["lyrics"])
    return '\n'.join(all_lyrics)
             
mcmcmc = MCMCMC(3)
all_lyrics =  load_rap()
mcmcmc.update_chains(all_lyrics)

def generate_stanza(line_length, rhyme_level, num_couplets):
    lines = []
    for i in range(num_couplets):
        done = False
        while not done:
            line_1 = mcmcmc.generate_line(line_length)
            rhymes = list(mcmcmc.rhyme(line_1.split()[-1], rhyme_level))
            if (len(rhymes) == 0):
                continue
            line_2 = mcmcmc.generate_line(line_length, True, random.choice(rhymes))
            done = True
        lines.append(line_1.capitalize())
        lines.append(line_2.capitalize())
    return lines
   
@app.route("/")
def home():
    stanzas = [generate_stanza(7, 2, 3) for x in range(3)]
    chorus = [generate_stanza(7, 2, 2)]
    return "<br/><br/>".join(["<br/>".join(x) for x in stanzas + chorus])
    
    
if __name__ == "__main__":
    app.run()

