
from fststr import fststr
import pywrapfst as fst
import os

# Third try with git, to avoid password

class Lemmatizer():

    def __init__(self):
        # get the symbol table ready
        st = fststr.symbols_table_from_alphabet(fststr.EN_SYMB)
        return

    # build a FST works for in_vocab_words in section 2.1, based on the dictionary file
    def buildInVocabFST(self): 
        # read dictionary file
        dict_file = open('in_vocab_dictionary_verbs.txt', 'r')
        # read each line of the file
        dict_lines = dict_file.readlines()

        # initialize a FST1
        st = fststr.symbols_table_from_alphabet(fststr.EN_SYMB)
        compiler = fst.Compiler(isymbols=st, osymbols=st, keep_isymbols=True, keep_osymbols=True)
        inits1 = '0\n'
        print(inits1, file=compiler)
        initFST1 = compiler.compile()
        fststr.expand_other_symbols(initFST1)


        for line in dict_lines:
            # make each line into a list of three 
            line = line.strip()
            line = line.rstrip(',')
            lineList = line.split(',')
            # print(lineList)
            # now build and update FST base on each line
            s = ''
            for i in range(len(lineList[1])):
                try:
                    s+='{} {} {} {}\n'.format(i,i+1,lineList[1][i],lineList[0][i])
                except:
                    s+='{} {} {} <epsilon>\n'.format(i,i+1,lineList[1][i])
            s+='{} {} <epsilon> +Known\n{}\n'.format(len(lineList[1]),len(lineList[1])+1, len(lineList[1])+1)
            # print(s)
            # now union current FST into the myFST
            compiler = fst.Compiler(isymbols=st, osymbols=st, keep_isymbols=True, keep_osymbols=True)
            print(s, file=compiler)
            currFST = compiler.compile()
            initFST1 = initFST1.union(currFST)

        return initFST1

    # build a FST that separates out suffix -s, -ed, -en, -ing with morpheme boundaries, for section 2.2
    def buildMorphFST(self):
        # initialize a FST2
        st = fststr.symbols_table_from_alphabet(fststr.EN_SYMB)
        compiler = fst.Compiler(isymbols=st, osymbols=st, keep_isymbols=True, keep_osymbols=True)
        inits2 = '0\n'
        print(inits2, file=compiler)
        initFST2 = compiler.compile()
        fststr.expand_other_symbols(initFST2)

        # read morph FST txt files
        morph_files = [filename for filename in os.listdir('.') if filename.startswith("FST_morph_")]
        # print(morph_files)
        for f in morph_files:
            compiler = fst.Compiler(isymbols=st, osymbols=st, keep_isymbols=True, keep_osymbols=True)
            morph = open(f).read()
            print(morph, file=compiler)
            morph_FST = compiler.compile()
            initFST2 = initFST2.union(morph_FST)

        return initFST2


    def runtask1(self, input_str1):
        FST_1 = self.buildInVocabFST()
        return fststr.apply(input_str, FST_1) 


    def runtask2(self, input_str):
        FST_2 = self.buildMorphFST()
        return fststr.apply(input_str, FST_2)


    def lemmatize(self, input_str):
        # input ex. giving<#>
        # output ex. give+Known or give+Guess
        ##########################################

        # myFST should eventually consist of: 
        #   txt myFSTs for out_vocab_words in section 2.2 and 2.3,
        #   FST generated by buildInVocabFST for section 2.1,
        #   union them together
        FST_1 = self.buildInVocabFST()
        return fststr.apply(input_str, FST_1) 

    def delemmatize(self, input_lemma):
        # input ex. give+Guess
        # output ex. a set of ”give”, ”giving”, ”gived”, ”gives”, ”giveing”, ”giveen”, and ”giveed”
        ##########################################
        return



l = Lemmatizer()
############################

#l.buildInVocabFST()

# lemma_test = 'aahing'
# print("input: ", lemma_test)
# print("output: ", l.lemmatize(lemma_test))

############################

#l.buildMorphFST()

# task2_test = 'squiggs<#>'
# print("input: ", task2_test)
# print("output: ", l.runtask2(task2_test))



























