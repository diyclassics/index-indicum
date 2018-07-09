from lxml import html
import math

BASE_URL = 'http://dlib.nyu.edu/awdl/isaw/isaw-papers/'
PAPERS_URLS = [f'{BASE_URL}{i}' for i in range(1,14)]

total_text_page = ""
number_doc_containing = {}

tf_idf = {}
wordcount = {}
total_word = {}
for i, url in enumerate(PAPERS_URLS, 1):
    with open("data/papers/isaw-papers-%s.xhtml" % (i), "r") as paper:
        html_page = html.parse(paper)
        work_cited = html_page.xpath('//p[@class="work_cited"]')
        for work in work_cited :
            work.getparent().remove(work)
        text_page = html_page.xpath("//body//text()")
        print(text_page)
    # To eliminate duplicates, remember to split by punctuation, and use case demiliters.
    total_word[str(i)] = 0
    wordcount [str(i)] = {}
    tf_idf[str(i)] = {}

    for words in text_page :
        for word in words.lower().split():
            word = word.replace(".", "")
            word = word.replace(",", "")
            word = word.replace(":", "")
            word = word.replace("\"", "")
            word = word.replace("!", "")
            word = word.replace("â€œ", "")
            word = word.replace("â€˜", "")
            word = word.replace("*", "")

            if word not in wordcount[str(i)]:
                wordcount[str(i)][word] = 1
                if word in number_doc_containing.keys() :
                    number_doc_containing[word] += 1
                else :
                    number_doc_containing[word] = 1

            else:
                wordcount[str(i)][word] += 1
        total_word[str(i)] += 1

for i, url in enumerate(PAPERS_URLS, 1):
    for  word, number in wordcount[str(i)].items() :
        tf = wordcount[str(i)][word]/total_word[str(i)]

        tf_idf[str(i)][word] =  tf * math.log(i/number_doc_containing[word])
    tf_idf[str(i)] = sorted(tf_idf[str(i)].items(), key=lambda x: x[1])
    tf_idf[str(i)] = tf_idf[str(i)][-10:]

