import re

character = ['.',',',';',':','-,','...','?','!','(',')','[',']','{','}','<','>','"','/','\'','#','-','@']
emoticon = [':)',':]','=)',':-)',':(',':[','=(',':-(',':p',':P','=P',':-p',':-P',':D','=D',':-D',':o',':O',':-o',':-O',';)',';-)','8-)','B-)','^_^','-_-','>:o','>:O',':v',':3','8|','B|','8-|','B-|','>:(',':/',':\\',':-/',':-\\',':\'(','O:)',':*',':-*','<3','(y)','(Y)']

class Normalize():
    def remove_ascii(self, text):
        '''
            menghapus ASCII
        '''
        text = text.encode('ascii', 'ignore').decode('utf-8')
        return text

    def lower_text(self, text):
        '''
            normalisasi huruf besar ke kecil
        '''
        text = text.lower()
        return text

    def repeat_char_modify(self, text):
        '''
            mengubah character yang berulang menjadi satu char
        '''
        for i in range(len(character)):
            char_long = 5
            while char_long >= 2:
                char = character[i]*char_long
                text = text.replace(char, character[i])
                char_long -= 1
        return text

    def remove_elipsis(self, text):
        '''
            menghapus ellipsis
        '''
        text = text.replace('...', ' ...')
        text = text.replace(' ...','')
        return text

    def remove_newline(self, text):
        '''
            menghapus newline
        '''
        text = text.replace('\n', ' ')
        return text

    def remove_url(self, text):
        '''
            menghapus url
        '''
        text = re.sub(r"\s—\s", "", text)
        text = re.sub(r"http\S+", "", text)
        return text

    def remove_emoticons(self, text):
        '''
            menghapus emoticon
        '''
        return text

    def remove_hashtags_mentions(self, text):
        '''
            menghapus hastags dan mentions
        '''
        return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)"," ", text).split())
