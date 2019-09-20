
from fststr import fststr
import pywrapfst as fst
import os
from copy import deepcopy

class Lemmatizer():

    def __init__(self):
        # get the symbol table
        st = fststr.symbols_table_from_alphabet(fststr.EN_SYMB)
        return

    # build a pre processing FST that add <#> to the current string
    def buildpreProcessFST(self, curr_str):

        # print("entering buildpreProcessFST\n")

        s = '0\n'
        tracker = 0
        for i in range(len(curr_str)):
            if (curr_str[i] == '+') or (curr_str[i] == '<'):
                s+='{} {} <epsilon> {}\n'.format(tracker, tracker+1, curr_str[tracker:len(curr_str)])
                # tracker +=1
                break
            else:
                s+='{} {} {} {}\n'.format(tracker, tracker+1, curr_str[tracker], curr_str[tracker])
                tracker += 1

        s+='{} {} <epsilon> <#>\n{}\n'.format(tracker, tracker+1, tracker+1)
        # print(s)
        st = fststr.symbols_table_from_alphabet(fststr.EN_SYMB)
        compiler = fst.Compiler(isymbols=st, osymbols=st, keep_isymbols=True, keep_osymbols=True)
        print(s, file=compiler)
        FSTpre = compiler.compile()
        fststr.expand_other_symbols(FSTpre)

        return FSTpre

    def buildpreProcessFST_delemmatize(self):

        # initialize a FSTpre
        st = fststr.symbols_table_from_alphabet(fststr.EN_SYMB)
        compiler = fst.Compiler(isymbols=st, osymbols=st, keep_isymbols=True, keep_osymbols=True)
        initpres = '1\n'
        print(initpres, file=compiler)
        initFSTpre = compiler.compile()
        fststr.expand_other_symbols(initFSTpre)

        pre_files = [filename for filename in os.listdir('.') if filename.startswith("FST_pre_")]
        # print(pre_files)
        # compile txt files into FST, and union them into initFST2
        for f in pre_files:
            compiler = fst.Compiler(isymbols=st, osymbols=st, keep_isymbols=True, keep_osymbols=True)
            pre = open(f).read()
            print(pre, file=compiler)
            pre_FST = compiler.compile()
            fststr.expand_other_symbols(pre_FST)
            initFSTpre = initFSTpre.union(pre_FST)


        return initFSTpre

    # build a FST works for in_vocab_words, based on the dictionary file, for section 2.1
    def buildInVocabFST(self): 

        # print("entering buildInVocabFST\n")

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
            # print(s)
            # now union current FST into the initFST1
            compiler = fst.Compiler(isymbols=st, osymbols=st, keep_isymbols=True, keep_osymbols=True)
            print(s, file=compiler)
            currFST = compiler.compile()
            fststr.expand_other_symbols(currFST)
            initFST1 = initFST1.union(currFST)

        return initFST1

    # build a FST that separates out suffix -s, -ed, -en, -ing with morpheme boundaries, for section 2.2
    def buildMorphFST(self):

        # print("entering buildMorphFST\n")

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

        # print("entering buildAllomFST\n")

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
        # allom = open('FST_allom_EInsertion_shch.txt').read()
        # print(allom, file=compiler)
        # allom_FST = compiler.compile()
        # fststr.expand_other_symbols(allom_FST)
        # initFST3 = initFST3.union(allom_FST)

        return initFST3

    # build a post processing FST, transform intermediate form to lemma+Guess, don't forget the without <^> case!!
    def buildpostProcessFST(self, input_str):

        # print("entering buildpostProcessFST\n")

        # initialize a FSTpost
        st = fststr.symbols_table_from_alphabet(fststr.EN_SYMB)
        compiler = fst.Compiler(isymbols=st, osymbols=st, keep_isymbols=True, keep_osymbols=True)
        initposts = '0\n'
        print(initposts, file=compiler)
        initFSTpost = compiler.compile()
        fststr.expand_other_symbols(initFSTpost)

        # read post FST txt files
        post_files = [filename for filename in os.listdir('.') if filename.startswith("FST_post_")]
        # print(post_files)
        # compile txt files into FST, and union them into initFSTpost
        for f in post_files:
            compiler = fst.Compiler(isymbols=st, osymbols=st, keep_isymbols=True, keep_osymbols=True)
            post = open(f).read()
            print(post, file=compiler)
            post_FST = compiler.compile()
            fststr.expand_other_symbols(post_FST)
            initFSTpost = initFSTpost.union(post_FST)
            #print("checkpoint: ", fststr.apply(input_str, initFSTpost), '\n')

        # Run indivdual FST file, for debugging purposes:
        # compiler = fst.Compiler(isymbols=st, osymbols=st, keep_isymbols=True, keep_osymbols=True)
        # post = open('FST_post_withsign.txt').read()
        # print(post, file=compiler)
        # post_FST = compiler.compile()
        # fststr.expand_other_symbols(post_FST)
        # initFSTpost = initFSTpost.union(post_FST)


        # FST that take care of input is original form
        s = ''
        # loop through the character parts of the input
        tracker = 0
        for i in range(len(input_str)):
            if (input_str[i] == '+'):
                s+='{} {} <#> +Guess\n{}\n'.format(tracker, tracker+1, tracker+1)
                tracker += 1
                break
            else:
                s+='{} {} {} {}\n'.format(tracker, tracker+1, input_str[tracker], input_str[tracker])
                tracker += 1
        # take care of <#> in the end, change it to +Guess
        s+='{} {} <#> +Guess\n{}\n'.format(tracker, tracker+1, tracker+1)
        compiler = fst.Compiler(isymbols=st, osymbols=st, keep_isymbols=True, keep_osymbols=True)
        print(s, file=compiler)
        original_case_FST = compiler.compile()
        fststr.expand_other_symbols(original_case_FST)
        initFSTpost = initFSTpost.union(original_case_FST)

        # # Last FST, clear out any word ends with <#>, output words ends with +Guess and +Known
        compiler = fst.Compiler(isymbols=st, osymbols=st, keep_isymbols=True, keep_osymbols=True)
        clear = open('FST_finalclearance.txt').read()
        print(clear, file=compiler)
        clear_FST = compiler.compile()
        fststr.expand_other_symbols(clear_FST)
        lastFST = fst.compose(initFSTpost.arcsort(sort_type="olabel"), clear_FST.arcsort(sort_type="ilabel") )

        return lastFST

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

    def runtask23(self, input_str):
        FST_2 = self.buildMorphFST()
        FST_3 = self.buildAllomFST()
        FST_2_3 = fst.compose(FST_2.arcsort(sort_type="olabel"), FST_3.arcsort(sort_type="ilabel") )
        return fststr.apply(input_str, FST_2_3)

    def runPostProcessFST(self, input_str):
        FST_post = self.buildpostProcessFST()
        return fststr.apply(input_str, FST_post)


    def buildFinalFST(self, input_str):

        # print("entering buildFinalFST\n")

        FST_pre = self.buildpreProcessFST(input_str)
        # print("test pre inv ouput: ", fststr.apply('as<#>', deepcopy(FST_pre).invert()), '\n')
        FST_1 = self.buildInVocabFST()
        # print("test 1 inv ouput: ", fststr.apply('a+Guess', deepcopy(FST_1).invert()), '\n')
        FST_2 = self.buildMorphFST()
        # print("test 2 inv ouput: ", fststr.apply('a<^>s<#>', deepcopy(FST_2).invert()), '\n')
        FST_3 = self.buildAllomFST()
        # print("test 3 inv output: ", fststr.apply('as<#>', deepcopy(FST_3).invert()), '\n')
        FST_post = self.buildpostProcessFST(input_str)
        # print("test post inv output: ", fststr.apply('a+Guess', deepcopy(FST_post).invert()), '\n')
        # FST_pre_1 = fst.compose(FST_pre.arcsort(sort_type="olabel"), FST_1.arcsort(sort_type="ilabel") )
        
        FST_2_3 = fst.compose(FST_2.arcsort(sort_type="olabel"), FST_3.arcsort(sort_type="ilabel") )
        FST_23_post = fst.compose(FST_2_3.arcsort(sort_type="olabel"), FST_post.arcsort(sort_type="ilabel") )
        FST_whole = FST_1.union(FST_23_post)
        FST_final = fst.compose(FST_pre.arcsort(sort_type="olabel"), FST_whole.arcsort(sort_type="ilabel") )
        return FST_final


    def lemmatize(self, input_str):
        # input ex. giving<#>
        # output ex. give+Known or give+Guess
        ##########################################
        FST_final = self.buildFinalFST(input_str)
        return set(fststr.apply(input_str, FST_final))

    def delemmatize(self, input_str):
        # input ex. give+Guess
        # output ex. a set of ”give”, ”giving”, ”gived”, ”gives”, ”giveing”, ”giveen”, and ”giveed”
        ##########################################

        # invert post FST
        FST_post = self.buildpostProcessFST(input_str)
        FST_post_inv = deepcopy(FST_post).invert()

        # invert allom FST
        FST_3 = self.buildAllomFST()
        FST_3_inv = deepcopy(FST_3).invert()
        # print("test here 3 inv: ", fststr.apply('as<#>', FST_3_inv), '\n')
        FST_post_3_inv = fst.compose(FST_post_inv.arcsort(sort_type="olabel"), FST_3_inv.arcsort(sort_type="ilabel") )
        
        # invert morph FST
        FST_2 = self.buildMorphFST()
        FST_2_inv = deepcopy(FST_2).invert()
        # print("test here 2 inv: ", fststr.apply('aes<^><#>', FST_2_inv), '\n')
        FST_post3_2_inv = fst.compose(FST_post_3_inv.arcsort(sort_type="olabel"), FST_2_inv.arcsort(sort_type="ilabel") )
        
        # invert inVocab FST
        FST_1 = self.buildInVocabFST()
        FST_1_inv = deepcopy(FST_1).invert()
        # print("test here 1 inv: ", fststr.apply('a+Guess', FST_1_inv), '\n')
        FST_in_union_out_inv = FST_1_inv.union(FST_post3_2_inv)
        
        # preprocess FST for delemmatize
        FST_pre_inv = self.buildpreProcessFST_delemmatize()
        # print("test here pre inv: ", fststr.apply('aing<#>', FST_pre_inv), '\n')
        FST_unionInOut_pre = fst.compose(FST_in_union_out_inv.arcsort(sort_type="olabel"), FST_pre_inv.arcsort(sort_type="ilabel") )

        # FST_final = self.buildFinalFST(input_lemma)
        # FST_final_inverted = deepcopy(FST_final).invert()
        # print(FST_final_inverted.input_symbols())
        return set(fststr.apply(input_str, FST_unionInOut_pre))



l = Lemmatizer()

######## TEST CASES ########

############################

# l.buildpreProcessFST('hello')

# preFST_test = 'hello'
# print("input: ", preFST_test)
# print("output: ", l.runPreProcessFST(preFST_test))


############################

# l.buildInVocabFST()

# task1_test = 'aahing<#>'
# print("input: ", task1_test)
# print("output: ", l.runtask1(task1_test))

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
# task3_test = 'watch<^>s<#>'

### e deletion ###
# task3_test = 'make<^>ing<#>'

### k deletion ###
# task3_test = 'panick<^>ing<#>'
# task3_test = 'ckckckc<^>ed<#>'
# task3_test = 'cccck<^>ed<#>'

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

############################

# lemma_test = 'squigging'
# lemma_test = 'making'
# lemma_test = 'watches'
# lemma_test = 'ases'
# lemma_test = 'walk'
# print("input: ", lemma_test)
# print("output: ", l.lemmatize(lemma_test))

# print("\n\n")

# lemma_test2 = 'give+Guess'
# lemma_test2 = 'a+Guess'
# print("input: ", lemma_test2)
# print("output: ", l.delemmatize(lemma_test2))









