READ_ME.txt
===========

Bahasa Indonesia Symbolic Parser

Created by:
# Joice
# Faculty of Computer Science
# University of Indonesia
# 2002

Library Call Number:
- Bachelor Thesis: SK-0487(Source Code SK-65)
  http://lontar.cs.ui.ac.id/Lontar/opac/themes/ng/detail.jsp?id=4655&lokasi=lokal
- Bachelor Thesis Sofcopy and Source: Source Code SK-65(SK-487)
  http://lontar.cs.ui.ac.id/Lontar/opac/themes/ng/detail.jsp?id=19697&lokasi=lokal


Bahasa Indonesia Symbolic Parser is a parser is a tool that will create a parse tree structures
for Indonesian sentences. Developed by defining Context-Free Grammar (CFG) Rules for Bahasa Indonesia 
grammar, complete with a simple lexicon of words in Bahasa Indonesia, and run on PCPATR application,
available at "http://www.sil.org/pcpatr/".


Symbolic Parser package consists of:
====================================
1. A PCPATR application that also available at "http://www.sil.org/pcpatr/".
   - pcpatr32.exe
2. Indonesian grammar source file.
   - grammarumum.grm
3. Indonesian lexicon source file.
   - lexgab.lex
4. Indonesian sentences examples.
   - ilmiahtak.sen
   - ilmiahurai.sen
   - mediatak.sen
   - mediaurai.sen
   - resmitak.sen
   - resmiurai.sen
   - tambahan_hiburan.sen
   - tambahan_ilmiah.sen
5. A guide of the package.
   - READ_ME.txt
   


Source file description:
========================
1. .sen
   File that consists of sentences that you want to parse. One row consists of one sentence to parse.
   Below this is an example for two sentences in two rows:
     pihaknya sudah menyiapkan pesawat kepresidenan secara prima
     kepala daerah kabupaten disebut bupati
2. .log
   The output file of the parsing process for a sentence input file (.sen) regarding the loaded grammar
   (.grm) and lexicon (.lex).
3. .lex
   Lexicon of the language with tag '\w' for the word, '\c' for the category, and '\f' for the subcategory
   separated in different rows.
   For example:
   \w menyiapkan
   \c Vtran
   \f <subcat> = ekatransitif
4. .grm
   File that define a grammar for a language in a context free grammar rules format



How to Run:
===========
1. Run pcpatr32.exe, available on this package or you can download it at "http://www.sil.org/pcpatr/".
2. Go to your working directory (directory consisting all the source files).
3. Type "set feature all" on the command prompt and push 'Enter' to turns on features display mode and
   displays the feature structures for all nodes of the tree.
4. Type "set tree on" on the command prompt and push 'Enter' to turns on the parse tree.
5. Type "set timing on" on the command prompt and push 'Enter' to turn on timing mode.
You can refer PCPATR reference manual on "http://www.sil.org/pcpatr/manual/pcpatr.html" for a complete
setting manual for step 3-5
6. Type "l g grammarumum.grm" on the command prompt and push 'Enter' to load the grammar.
7. Type "l l lexgab.lex" on the command prompt and push 'Enter' to load the lexicon.
8. Type "file parse [input_file.sen] [output_file.log]"on the command prompt and push 'Enter' to load 
   the input file and create/replace the output file.
