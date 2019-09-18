
from fststr import fststr
import pywrapfst as fst
import os


class Lemmatizer():

    def __init__(self):
        # get the symbol table
        st = fststr.symbols_table_from_alphabet(fststr.EN_SYMB)
        return

    # build a pre processing FST that add <#> to the current string
    def buildpreProcessFST(self, curr_string):

        s = '0\n'
        for i in range(len(curr_string)):
            s+='{} {} {} {}\n'.format(i, i+1, curr_string[i], curr_string[i])
        s+='{} {} <epsilon> <#>\n{}\n'.format(len(curr_string), len(curr_string)+1, len(curr_string)+1)
        # print(s)
        st = fststr.symbols_table_from_alphabet(fststr.EN_SYMB)
        compiler = fst.Compiler(isymbols=st, osymbols=st, keep_isymbols=True, keep_osymbols=True)
        print(s, file=compiler)
        FSTpre = compiler.compile()

        return FSTpre

    # build a FST works for in_vocab_words, based on the dictionary file, for section 2.1
    def buildInVocabFST(self): 

        # initialize a FST1
        st = fststr.symbols_table_from_alphabet(fststr.EN_SYMB)
        compiler = fst.Compiler(isymbols=st, osymbols=st, keep_isymbols=True, keep_osymbols=True)
        inits1 = '0\n'
        print(inits1, file=compiler)
        initFST1 = compiler.compile()
        fststr.expand_other_symbols(initFST1)

        # read dictionary file
        dict_file = open('in_vocab_dictionary_verbs.txt', 'r')
        # read each line of the file
        dict_lines = dict_file.readlines()
        # build FST for each word
        for line in dict_lines:
            # make each line into a list, one list for one word, 
            # including its lemma form, surface form, and the form name
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
            s+='{} {} <#> <epsilon>\n'.format(len(lineList[1]),len(lineList[1])+1)
            s+='{} {} <epsilon> +Known\n{}\n'.format(len(lineList[1])+1,len(lineList[1])+2, len(lineList[1])+2)
            print(s)
            # now union current FST into the initFST1
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
        # compile txt files into FST, and union them into initFST2
        for f in morph_files:
            compiler = fst.Compiler(isymbols=st, osymbols=st, keep_isymbols=True, keep_osymbols=True)
            morph = open(f).read()
            print(morph, file=compiler)
            morph_FST = compiler.compile()
            fststr.expand_other_symbols(morph_FST)
            initFST2 = initFST2.union(morph_FST)

        # Run indivdual FST file, for debugging purposes:
        # compiler = fst.Compiler(isymbols=st, osymbols=st, keep_isymbols=True, keep_osymbols=True)
        # morph = open('FST_morph_ing.txt').read()
        # print(morph, file=compiler)
        # morph_FST = compiler.compile()
        # fststr.expand_other_symbols(morph_FST)
        # initFST2 = initFST2.union(morph_FST)

        return initFST2

    # build a FST that applies allomorphic rules, for section 2.3
    def buildAllomFST(self):

        # initialize a FST3
        st = fststr.symbols_table_from_alphabet(fststr.EN_SYMB)
        compiler = fst.Compiler(isymbols=st, osymbols=st, keep_isymbols=True, keep_osymbols=True)
        inits3 = '0\n'
        print(inits3, file=compiler)
        initFST3 = compiler.compile()
        fststr.expand_other_symbols(initFST3)

        # read allom FST txt files
        allom_files = [filename for filename in os.listdir('.') if filename.startswith("FST_allom_")]
        # print(allom_files)
        # compile txt files into FST, and union them into initFST3
        for f in allom_files:
            compiler = fst.Compiler(isymbols=st, osymbols=st, keep_isymbols=True, keep_osymbols=True)
            allom = open(f).read()
            print(allom, file=compiler)
            allom_FST = compiler.compile()
            fststr.expand_other_symbols(allom_FST)
            initFST3 = initFST3.union(allom_FST)

        # Run indivdual FST file, for debugging purposes:
        # compiler = fst.Compiler(isymbols=st, osymbols=st, keep_isymbols=True, keep_osymbols=True)
        # allom = open('FST_allom_EInsertion.txt').read()
        # print(allom, file=compiler)
        # allom_FST = compiler.compile()
        # fststr.expand_other_symbols(allom_FST)
        # initFST3 = initFST3.union(allom_FST)

        return initFST3

    # build a post processing FST, transform intermediate form to lemma+Guess
    def buildpostProcessFST(self):

        st = fststr.symbols_table_from_alphabet(fststr.EN_SYMB)
        compiler = fst.Compiler(isymbols=st, osymbols=st, keep_isymbols=True, keep_osymbols=True)
        post = open('FST_postprocess.txt').read()
        print(post, file=compiler)
        post_FST = compiler.compile()
        fststr.expand_other_symbols(post_FST)

        return post_FST

    def runPreProcessFST(self, input_str):
        FST_pre = self.buildpreProcessFST(input_str)
        return fststr.apply(input_str, FST_pre)

    def runtask1(self, input_str):
        FST_1 = self.buildInVocabFST()
        return fststr.apply(input_str, FST_1) 

    def runtask2(self, input_str):
        FST_2 = self.buildMorphFST()
        return fststr.apply(input_str, FST_2)

    def runtask3(self, input_str):
        FST_3 = self.buildAllomFST()
        return fststr.apply(input_str, FST_3)

    def runPostProcessFST(self, input_str):
        FST_post = self.buildpostProcessFST()
        return fststr.apply(input_str, FST_post)


    def lemmatize(self, input_str):
        # input ex. giving<#>
        # output ex. give+Known or give+Guess
        ##########################################
        return

    def delemmatize(self, input_lemma):
        # input ex. give+Guess
        # output ex. a set of ”give”, ”giving”, ”gived”, ”gives”, ”giveing”, ”giveen”, and ”giveed”
        ##########################################
        return



l = Lemmatizer()

######## TEST CASES ########
############################

# l.buildpreProcessFST('hello')

# preFST_test = 'hello'
# print("input: ", preFST_test)
# print("output: ", l.runPreProcessFST(preFST_test))


############################

# l.buildInVocabFST()

# lemma_test = 'aahing<#>'
# print("input: ", lemma_test)
# print("output: ", l.runtask1(lemma_test))

############################

# l.buildMorphFST()

### -s ###
# task2_test = 'as<#>'
# task2_test = 'asss<#>'
# task2_test = 'ss<#>'

### -ed, -en ###
# task2_test = 'sqed<#>'
# task2_test = 'sqeed<#>'
# task2_test = 'sqeeed<#>'
# task2_test = 'sqedk<#>'
# task2_test = 'seqed<#>'
# task2_test = 'seqemed<#>'
# task2_test = 'sqeded<#>'

### -ing ###
# task2_test = 'aing<#>'
# task2_test = 'aiking<#>'
# task2_test = 'ainking<#>'
# task2_test = 'aingk<#>'
# task2_test = 'aining<#>'
# task2_test = 'aiing<#>'
# task2_test = 'aiiing<#>'
# task2_test = 'aingg<#>'
# task2_test = 'ainging<#>'
# task2_test = 'iinnging<#>'
# task2_test = 'squigging<#>'
# print("input: ", task2_test)
# print("output: ", l.runtask2(task2_test))

############################

# l.buildAllomFST()

### e insertion ###
# task3_test = 'fox<^>s<#>'

### e deletion ###
# task3_test = 'make<^>ing<#>'

### k deletion ###

### y replacement ###
# task3_test = 'trie<^>s<#>'
# task3_test = 'triie<^>s<#>'
# task3_test = 'trieiee<^>s<#>'
# task3_test = 'tri<^>ed<#>'
# task3_test = 'triiii<^>ed<#>'
# task3_test = 'triiie<^>ed<#>'
# task3_test = 'iei<^>ed<#>'
# task3_test = 'triii<^>s<#>'
# task3_test = 'triiii<^>s<#>'
# task3_test = 'trieee<^>s<#>'

### consonants ###
# task3_test = 'squigg<^>ing<#>'
# task3_test = 'squikigg<^>ed<#>'
# task3_test = 'squikbcixx<^>ing<#>'
# print("input: ", task3_test)
# print("output: ", l.runtask3(task3_test))


############################

# l.buildpostProcessFST('fox<^>es<#>')

# postFST_test = 'run<^>ing<#>'
# print("input: ", postFST_test)
# print("output: ", l.runPostProcessFST(postFST_test))










