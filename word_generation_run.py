from generators.words_generator import generate_random_word
from grammar.mathscript_grammar import *

print(" ".join(map(str, generate_random_word(script, 0))))
