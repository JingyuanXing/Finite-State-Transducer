
from lemmatizer import Lemmatizer


lem = Lemmatizer()

lemma_test = 'giving'
delamma_test = 'give+Guess'
lem.lemmatize(lemma_test)
lem.delemmatize(delamma_test)
# any fststr.apply(lemma_test, compiler.compile())