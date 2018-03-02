from pybo import *

input_string = ' ཤི་བཀྲ་ཤིས་  tr བདེ་་ལེ གས། བཀྲ་ཤིས་བདེ་ལེགས་ཀཀ'
test2 = 'བཀྲ་ཤིས་'
t = 'དཀོན་མཆོག་'
test = 'ཀཀ་ཀཀ་ཞེས་བྱ་བ། ངེད་རྣམས་ནི་མཐོ་གོ་གནས་དང་། འབྱོར་ལྡན། མིང་གྲགས་ཡོད་མཁན་དེ་འདྲ་ནམ་ཡང་མིན་ལ། ' \
       'ཅི་ཞིག་ཤེས་ཁུལ་གྱིས་ཚོགས་པ་འདི་གཉེར་བ་ཞིག་ཀྱང་གཏན་ནས་མིན། ཚན་རྩལ་གྱི་རྦ་རླབས་དྲག་ཏུ་འཕྱོ་ལྡིང་བྱེད་' \
       'པའི་དུས་སྐབས་འདིར་ང་ཚོས་སྔ་ས་ནས་རང་གི་སྐད་ཡིག་དང་རིག་གཞུང་ལ་དུང་བ་ཞིག་ན་གཞོན་ཚོར་བསྐྲུན་མ་ཐུབ་པ་དང་། ' \
       'བདག་གཅེས་ལ་འབད་མ་ནུས་ཚེ་ཡོད་ཚད་མིང་ཙམ་ཞིག་ཏུ་གྱུར་ཚར་རྗེས་ངལ་བ་ཇི་ཙམ་བརྟེན་ཡང་སྙིང་པོ་ལོན་རྒྱུ་དཀའ་བས་ད་' \
       'ལྟ་མ་སྔ་མ་ཕྱིས་བའི་དུས་ཚིགས་གལ་ཆེན་ཞིག་ཏུ་བརྩིས་ནས་ང་ཚོས་འདི་ལྟར་རང་ནུས་ལ་དཔགས་པའི་སྐད་ཡིག་རིག་གཞུང་དང་' \
       'འབྲེལ་བའི་བྱེད་སྒོ་སྤེལ་མུས་ཡིན།'

bs = BoSyl()  # used to affix particles
trie = PyBoTrie(bs, profile='POS')  # loads or builds a trie
tok = Tokenizer(trie)

for i in [input_string, test2, t, test]:
    pre_processed = PyBoTextChunks(i)
    words = tok.tokenize(pre_processed)

    tagged = ['"{}"/{}'.format(w.content, w.tag) for w in words]
    print(', '.join(tagged))
