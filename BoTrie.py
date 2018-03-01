from BoSylUtils import BoSyl
import time
import os
import pickle

# inspired from https://gist.github.com/nickstanisha/733c134a0171a00f66d4
# and https://github.com/eroux/tibetan-phonetics-py


class Node:
    def __init__(self, label=None, leaf=False, data=None):
        self.label = label
        self.leaf = leaf
        self.data = data
        self.children = dict()

    def add_child(self, key, leaf=False):
        if not isinstance(key, Node):
            self.children[key] = Node(key, leaf)
        else:
            self.children[key.leaf] = key

    def can_walk(self):
        return self.children != dict()

    def is_match(self):
        return self.leaf

    def __getitem__(self, key):
        return self.children[key]


class Trie:
    def __init__(self):
        self.head = Node()

    def __getitem__(self, key):
        return self.head.children[key]

    def add(self, word, data=None):
        current_node = self.head
        word_finished = True

        i = 0
        for i in range(len(word)):
            if word[i] in current_node.children:
                current_node = current_node.children[word[i]]
            else:
                word_finished = False
                break

        if not word_finished:
            while i < len(word):
                current_node.add_child(word[i])
                current_node = current_node.children[word[i]]
                i += 1

        current_node.leaf = True
        if data:
            current_node.data = data

    def walk(self, char, current_node=None):
        if not current_node:
            current_node = self.head

        if char in current_node.children:
            next_node = current_node[char]
        else:
            next_node = None

        return next_node

    def has_word(self, word):
        if word == '':
            return False
        elif not word:
            raise ValueError('Trie.has_word requires a not-Null string')

        # Start at the top
        current_node = self.head
        exists = True
        for letter in word:
            if letter in current_node.children:
                current_node = current_node.children[letter]
            else:
                exists = False
                break

        # Still need to check if we just reached a word like 't'
        # that isn't actually a full word in our dictionary
        if exists:
            if not current_node.leaf:
                exists = False
        if exists:
            return {'exists': exists, 'data': current_node.data}
        else:
            return {'exists': exists}

    def deactivate_words(self, word_list):
        """
        if the word is not in the trie, it will silently loop over the letters
        and move on to the next word.
        :param word_list: list of words to deactivate
        """
        for word in word_list:
            current_node = self.head
            for letter in word:
                if letter in current_node.children:
                    current_node = current_node.children[letter]
                else:
                    current_node = None
                    # and pass the remaining letters to move on to next word

            if current_node:
                current_node.leaf = False


class PyBoTrie(Trie):
    def __init__(self, profile='pytib'):
        Trie.__init__(self)
        self.bt = BoSyl()
        self.TSEK = '་'
        self.COMMENT = '#'
        self.profile = profile
        self.pickled_file = profile + '_trie.pickled'
        self.load_or_build_trie()

    def load_or_build_trie(self):
        if not os.path.exists(self.pickled_file):
            self.build_trie()
        else:
            self.load_trie()

    def load_trie(self):
        print('Loading Trie...')
        start = time.time()
        with open(self.pickled_file, 'rb') as f:
            self.head = pickle.load(f)
        end = time.time()
        print('Time:', end - start)

    def rebuild_trie(self):
        self.head = Node()
        self.build_trie()

    def build_trie(self):
        """
        """
        print('building Trie...', end=' ')
        start = time.time()
        files = {1: 'ancient.txt',
                 2: 'exceptions.txt',
                 3: 'uncompound_lexicon.txt',
                 4: 'Tibetan.DICT',
                 5: 'tsikchen.txt',
                 6: 'oral_corpus_0.txt',
                 7: 'oral_corpus_1.txt',
                 8: 'oral_corpus_2.txt',
                 9: 'oral_corpus_3.txt',
                 10: 'recordings_4.txt'}
        tests = {1: 'test.txt'}
        profiles = {
                    'pytib': [files[1], files[2], files[3], files[5], 'particles.txt'],
                    'POS': [files[1], files[2], files[3], files[5], 'particles.txt', files[4]],
                    'empty': [],
                    'test': [tests[1]]
                    }

        if self.profile == 'test':
            for f in profiles[self.profile]:
                full_path = os.path.join(os.path.split(__file__)[0], 'resources', 'tests', f)
                self.__add_one_file(full_path)
            return

        for f in profiles[self.profile]:
            full_path = os.path.join(os.path.split(__file__)[0], 'resources', 'trie', f)
            self.__add_one_file(full_path)

        with open(self.pickled_file, 'wb') as f:
            pickle.dump(self.head, f, pickle.HIGHEST_PROTOCOL)
        end = time.time()
        print('Time:', end - start)

    def __add_one_file(self, folder):
        """
        files can have comments starting with #
        spaces and empty lines are trimmed
        a single space(breaks if more than one), a comma or a tab can be used as separators
        :param folder:
        """
        with open(folder, 'r') as g:
            for line in g.read().split('\n'):
                if self.COMMENT in line:
                    comment_idx = line.index(self.COMMENT)
                    line = line[:comment_idx]

                line = line.strip()

                if line:
                    if '\t' in line:
                        word, pos = line.split('\t')
                    elif ',' in line:
                        word, pos = line.split(',')
                    elif ' ' in line:
                        if line.count(' ') > 1:
                            break
                        word, pos = line.split(' ')
                    else:
                        word, pos = line, 'XXX'

                    self.inflect_n_add(word, pos)

    def inflect_n_add(self, word, pos):
        """
        Add to the trie all the affixed versions of the word
        :param word: a word without ending tsek
        :param pos: initial POS
        """
        if word.endswith(self.TSEK):
            word = word[:-1]

        beginning, last_syl = self.split_at_last_syl(word)

        if self.bt.is_affixable(last_syl):
            affixed = self.bt.get_all_affixed(last_syl)
            for a in affixed:
                data = '{}_{}_{}_{}'.format(pos, a[1]['POS'], a[1]['len'], a[1]['aa'])
                self.add(beginning+a[0]+self.TSEK, data)
        self.add(word+self.TSEK, '{}___'.format(pos))

    def split_at_last_syl(self, word):
        if word.count(self.TSEK) >= 1:
            tsek_idx = word.rindex(self.TSEK)
            return word[:tsek_idx+1], word[tsek_idx+1:]
        else:
            return '', word


if __name__ == '__main__':
    """ Example use """
    bt = PyBoTrie('POS')
    print('གྲུབ་མཐའ་', bt.has_word('གྲུབ་མཐའ་'))
    print('གྲུབ་མཐའི་', bt.has_word('གྲུབ་མཐའི་'))
    print('ཟས་', bt.has_word('ཟས་'))

    trie = Trie()
    words = 'hello goo good goodbye help gerald gold tea ted team to too tom stan standard money'
    for w in words.split():
        trie.add(w)
    print("'goodbye':", trie.has_word('goodbye'))
