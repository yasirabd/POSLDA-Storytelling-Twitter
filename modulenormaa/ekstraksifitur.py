def ekstraksifitur():
    #================= Case Folding =================#
    data()
    komentar = []
    for v in kms_komen.values():
        komentar.append(v[2])
    komentar = [item.lower() for item in komentar]

    #================= Tokenizing =================#
    lstkata2 = []
    tokenizer = RegexpTokenizer(r'\w+|\$[\d\.]+')
    for item in komentar:
        lstkata = (tokenizer.tokenize(item))
        lstkata2.append(lstkata)

    #================= Normalisasi =================#
    fin = open("kamus/kamus.txt", encoding="utf8")
    kms_kata = fin.readlines()
    kms_kata = [item.rstrip('\n') for item in kms_kata]
    fin.close()

    i = 0
    lstkalimatbr = []
    lstdokumenbr = []
    for kalimat in lstkata2:
        lstkalimatbr = []
        for kata in kalimat:
            per_kata = {}
            for kamus in kms_kata:
                result = distance.get_jaro_distance(repr(kata), repr(kamus), winkler=True, scaling=0.1)
                per_kata.update({i: (result, kata, kamus)})
                i = i + 1
            maxi = max(per_kata.items(), key=operator.itemgetter(1))
            lstkalimatbr.append(maxi[1][2])
        lstdokumenbr.append(lstkalimatbr)

    #================= kamus stopwords ==================#
    fin = open("kamus/stopWords.txt", encoding="utf8")
    stop_words = fin.readlines()
    stop_words = [item.rstrip('\n') for item in stop_words]
    fin.close()

    wordfildok = []
    wordfilkal = []
    for t in lstdokumenbr:
        wordfilkal = []
        for w in t:
            if w not in stop_words:
                wordfilkal.append(w)
        wordfildok.append(wordfilkal)

    #================= stemming =================#
    factory = StemmerFactory()
    stemmer = factory.create_stemmer()

    lstkalimatstem = []
    lstdokumenstem = []
    for t in wordfildok:
        lstkalimatstem = []
        for w in t:
            hasil_stem = []
            hasil_stem = stemmer.stem(w)
            lstkalimatstem.append(hasil_stem)
        lstdokumenstem.append(lstkalimatstem)

    #================= sentiment lexicon =================#
    fin = open("kamus/sen_lexfull.txt", encoding="utf8")
    sen_lex = fin.readlines()
    sen_lex = [item.rstrip('\n') for item in sen_lex]
    fin.close()

    #================= representasi ekstraksi fitur occurence =================#
    global dict_all
    dict_all = {}
    dokexkal = []
    dok_all = []
    i = 0
    for word in lstdokumenstem:
        dokexdok = []
        dokexkal = []
        for wordsen in sen_lex:
            if (wordsen in word):
                dokexkal.append(wordsen)
        dokexdok.append(kms_komen[i][1])
        dokexdok.append(kms_komen[i][0])
        dokexdok.append(dokexkal)
        dict_all.update({i: dokexdok})
        i = i + 1
    #================= eksport csv preprocessing occurence =================#
    test = "data/bow_pre_occurence.csv"
    with open(test, "w", encoding='utf8', errors='ignore') as output:
        writer = csv.writer(output, lineterminator='\n')
        for value in dict_all.values():
            writer.writerows([value])

    #================= representasi ekstraksi fitur frekuensi =================#
    global dict_all_fek
    dict_all_fek = {}
    dokexkal_fek = []
    dok_all_fek = []
    i = 0
    for word in lstdokumenstem:
        dokexdok_fek = []
        dokexkal_fek = []
        for wordsen in sen_lex:
            j = 0
            if (wordsen in word):
                j = word.count(wordsen)
                k = 0
                while (k < j):
                    k = k + 1
                    dokexkal_fek.append(wordsen)
        dokexdok_fek.append(kms_komen[i][1])
        dokexdok_fek.append(kms_komen[i][0])
        dokexdok_fek.append(dokexkal_fek)
        dict_all_fek.update({i:dokexdok_fek})
        i=i+1
    #================= eksport csv preprocessing frekuensi =================#
    test_fek = "data/bow_pre_frekuensi.csv"
    with open(test_fek, "w", encoding='utf8', errors='ignore') as output:
        writer = csv.writer(output, lineterminator='\n')
        for value in dict_all_fek.values():
            writer.writerows([value])

    #========================= Return Variable =========================#
    return render_template(
        'ekstraksifitur.html', sen_lex = sen_lex, dict_all = dict_all, dict_all_fek = dict_all_fek)