import nltk
from nltk.corpus import wordnet as wn
import re
from nltk import word_tokenize, pos_tag, ne_chunk
from difflib import SequenceMatcher
from nltk.tokenize import RegexpTokenizer
import json


nltk.download('maxent_ne_chunker')
nltk.download('words')

product_pattern = r'\b(?:[Ss][Tt]-?(?:902|903|901|906|907)|ventouse|port|goblete|902|903|901|906|907)\b'
re_add_corpus_v = [r'\band\b', r'\bplus\b']
quantity_regex = r'\b[A-Za-z\d]+\b'
re_yes_corpus_v = [r'\by\b', r'\byes\b', r'\bok\b', r'\bokey\b', r"\bdid\b", r'\bwant\b', r'\bdo\b', r'affirmative', r'positive', r'exact', r'correct']
phone_regex = r'\b(?:\d{10}|\d{4} \d{2} \d{2} \d{2}|\d{3} \d{2} \d{2} \d{2}|\d{3} \d{8}|\d{12})\b'
re_not_corpus_v = [r'\bn\b', r'\bnot?\b', r"\bdidt\b", r"\bdidn'?t\b", r"\bdon'?t\b", r'negative', 'nope']
status_regex = r'\b(?:paid|not paid|yes paid|no paid|yes|no|not)\b'

action_select_keys_d = {'personal_info':  ['personal', 'edit', 'modify', 'profile'],
                        'help':           ['help'],
                        'record':         ['record', 'add', 'new', 'write', 'list', 'put'],
                        'stats':          ['stats', 'summary', 'statistics', 'results', 'status'],
                        'delete':         ['delete', 'erase', 'remove', 'reset', 'clear', 'clean'],
                        'cancel':         ['cancel', 'stop', 'quit', 'exit', 'back', 'return', 'select']}

numbers_1_9_d = {'one': 1,
                 'two': 2,
                 'three': 3,
                 'four': 4,
                 'five': 5,
                 'six': 6,
                 'seven': 7,
                 'eight': 8,
                 'nine': 9}

numbers_10_19_d = {'ten': 10,
                   'eleven': 11,
                   'twelve': 12,
                   'thirteen': 13,
                   'fourteen': 14,
                   'fifteen': 15,
                   'sixteen': 16,
                   'seventeen': 17,
                   'eighteen': 18,
                   'nineteen': 19}

numbers_20_90_d = {'twenty': 20,
                   'thirty': 30,
                   'forty': 40,
                   'fifty': 50,
                   'sixty': 60,
                   'seventy': 70,
                   'eighty': 80,
                   'ninety': 90}

original_products = ['ST-901', 'ST-902', 'ST-903', 'ST-907', 'P-30', 'ventouse car', 'ST-906', 'Port Goblete']


# Specify the path to your JSON file
json_file_path = 'D:\miniEcoomerce\server\data\cities.json'

# Load data from the JSON file
with open(json_file_path, 'r', encoding='utf-8') as file:
    data = json.load(file)

class SentenceParser:
    """ This class has the task of parsing sentences and retrieve relevant information """

    def __init__(self):
        return None


    def find_v(self, sentence, to_find_v):
        sentence = sentence.lower()
        found = False

        for w in to_find_v:
            if w in sentence:
                found = True
                break

        return found

    def yes_no_question(self, sentence):
        sentence = sentence.lower()

        f_yes = re.findall('|'.join(re_yes_corpus_v), sentence)
        f_not = re.findall('|'.join(re_not_corpus_v), sentence)

        to_ret = None
        if len(f_yes) > 0:
            to_ret = True
        if len(f_not) > 0:
            to_ret = False

        return to_ret

    def similar(self, a, b):
        return SequenceMatcher(None, a, b).ratio()

    def extract_product(self, sentence):
        match = re.search(product_pattern, sentence)

        if match:
            identified_product = match.group()

            # Calculate similarity scores with original products
            similarity_scores = {original_product: self.similar(identified_product.lower(), original_product.lower())
                                 for original_product in original_products}

            # Find the product with the maximum similarity score
            max_similarity_product = max(similarity_scores, key=similarity_scores.get)

            return max_similarity_product
        else:
            return None

    def postag(self, sentence):
        """ Make a postag of a sentence """
        # Ensure that the sentence is in lower case
        sentence = sentence.lower()

        # Tokenize
        tokens = nltk.word_tokenize(sentence)

        # POS tagging
        postag_v = nltk.pos_tag(tokens)
        return postag_v

    def find_name(self, sentence):
        """ Finds and returns a personal name in the sentence.
            If is not found, it return None"""
        name_v = []

        s_lower = sentence.lower()
        tokens_lower = nltk.word_tokenize(s_lower)

        present = None
        if 'is' in tokens_lower:
            present = 'is'

        if 'me' in tokens_lower:
            present = 'me'

        if 'am' in tokens_lower:
            present = 'am'

        pt_v = self.postag(sentence)
        jump = True
        if present is not None:
            for w, p in pt_v:
                if jump and w.lower() != present:
                    continue
                elif jump:
                    jump = False
                    continue

                if len(name_v) == 0 or 'NN' in p:
                    name_v.append(w)
                else:
                    break

        if len(name_v) == 0:
            if len(pt_v) == 1:
                name = pt_v[0][0]

                name_v.append(name)

            # First lets find "NNP"s
            for w, p in pt_v:
                if p == 'NNP':
                    name_v.append(w)

            if len(name_v) == 0:
                for w, p in pt_v:
                    if p == 'VBN':
                        name_v.append(w)

        if len(name_v) == 0:
            return None
        else:
            for i in range(len(name_v)):
                name_v[i] = name_v[i][0].upper() + name_v[i][1:].lower()

        return ' '.join(name_v)

    def parse_qte(self, sentence):
        """ Parses the quantity (qte) from the sentence using word-to-number conversion. """

        words = sentence.lower().split()

        # Process each word and convert to numbers
        parsed_qte = []
        for word in words:
            if word in numbers_1_9_d:
                parsed_qte.append(numbers_1_9_d[word])
            elif word in numbers_10_19_d:
                parsed_qte.append(numbers_10_19_d[word])
            elif word in numbers_20_90_d:
                parsed_qte.append(numbers_20_90_d[word])
            elif word.isdigit():
                parsed_qte.append(int(word))

        return parsed_qte[0]

    def parse_unit_price(self, unit_price_str):
        """ Parses unit price from a string with currency symbols and decimal values. """
        # Define currency symbols and their corresponding values (assuming dz and da)
        currency_symbols = {'$': 1, 'da': 1, 'dz': 1}

        # Remove non-alphanumeric characters and convert to lowercase
        cleaned_str = re.sub(r'[^a-zA-Z0-9.]', '', unit_price_str.lower())

        # Extract currency symbol (if present)
        currency_symbol = next((symbol for symbol in currency_symbols if symbol in cleaned_str), None)

        # Remove currency symbol from the string
        if currency_symbol:
            cleaned_str = cleaned_str.replace(currency_symbol, '')

        # Convert to float (considering .000 format)
        try:
            unit_price = float(cleaned_str)
        except ValueError:
            unit_price = None

        # Multiply by the currency value if a valid currency symbol is found
        if currency_symbol and currency_symbol in currency_symbols:
            unit_price *= currency_symbols[currency_symbol]

        return unit_price



    def find_phone_number(self, sentence):
        """ Finds and returns a phone number in the sentence. If not found, returns None. """

        # Find all occurrences of the phone number pattern in the sentence
        matches = re.findall(phone_regex, sentence)

        # If a match is found, return the phone number
        if matches:
            return matches
        else:
            return None

    import re
    import nltk
    from nltk import word_tokenize, pos_tag, ne_chunk
    from difflib import SequenceMatcher
    from nltk.tokenize import RegexpTokenizer

    nltk.download('maxent_ne_chunker')
    nltk.download('words')

    def find_client_information(self, sentence):
        """ Finds and returns client information (name, phone number, city) in the sentence.
        If not found, returns empty strings.

        Parameters:
        - sentence: Input sentence containing client information.
        - data: List of dictionaries containing city information.

        Returns:
        - Tuple containing  phone number, and city.
        """

        # Tokenize and tag words
        tokenizer = RegexpTokenizer(r'\w+')
        words = tokenizer.tokenize(sentence)
        client_info = []

        # Check for cities in the provided data and use similarities to find the best match
        max_score = 0
        best_match = ''
        for i in data:
            for k, v in i.items():
                for city in words:
                    similarity_score = SequenceMatcher(None, city.lower(), str(v).lower()).ratio()

                    if similarity_score > max_score:
                        max_score = similarity_score
                        best_match = i[k]

        # Find all occurrences of the phone number pattern in the sentence
        phone_matches = self.find_phone_number(sentence)
        # If matches are found, return the information, else return empty strings
        phone_number = phone_matches[0] if phone_matches else ''
        client_city = best_match
        client_info.append(phone_number)
        client_info.append(client_city)

        return client_info
    def find_payment_status(self, sentence):
        """ Finds and returns the payment status in the sentence. If not found, returns None. """

        # Find all occurrences of the payment status pattern in the sentence
        matches = re.findall(status_regex, sentence.lower())

        # If a match is found, return the payment status
        if matches:
            return matches[0]
        else:
            return None

    def intension_detector(self, sentence, just_cancel=False, sim_th=0.6):
        """Returns the intention of the sentence. If just_cancel is present, compares the sentence with the cancel intention."""

        pos_actions_v = []

        if (not just_cancel) and self.find_v(sentence, action_select_keys_d['personal_info']):
            pos_actions_v.append('personal_info')
        elif (not just_cancel) and self.find_v(sentence, action_select_keys_d['help']):
            pos_actions_v.append('help')
        elif (not just_cancel) and self.find_v(sentence, action_select_keys_d['record']):
            pos_actions_v.append('record')
        elif (not just_cancel) and self.find_v(sentence, action_select_keys_d['stats']):
            pos_actions_v.append('stats')
        elif (not just_cancel) and self.find_v(sentence, action_select_keys_d['delete']):
            pos_actions_v.append('delete')
        elif self.find_v(sentence, action_select_keys_d['cancel']):
            pos_actions_v.append('cancel')

        if (not just_cancel) and (len(pos_actions_v) > 1 or len(pos_actions_v) == 0):
            # If we are here, we need to disambiguate
            if len(pos_actions_v) == 0:
                pos_actions_v = list(action_select_keys_d.keys())

            actions_similarity_v = [0.0 for _ in pos_actions_v]

            tokens_v = word_tokenize(sentence)
            for i_a, action in enumerate(pos_actions_v):  # For each action
                for w in tokens_v:  # For each word in the sentence
                    w_ss_v = wn.synsets(w)

                    for a_w in action_select_keys_d[action]:  # For each keyword in the action
                        a_ss_v = wn.synsets(a_w)

                        # Compare the similarity between word and action synsets
                        for a_ss in a_ss_v:
                            for w_ss in w_ss_v:
                                d_sim = wn.path_similarity(w_ss, a_ss, simulate_root=False)
                                if d_sim is not None and d_sim > actions_similarity_v[i_a]:
                                    actions_similarity_v[i_a] = d_sim

            # Find the maximum similarity score
            sim_max = max(actions_similarity_v)

            if sim_max > sim_th:
                i_max = actions_similarity_v.index(sim_max)
                pos_actions_v = [pos_actions_v[i_max]]
            else:
                pos_actions_v = []

        # At this point, we must have 1 option or None
        assert len(pos_actions_v) <= 1, " - ERROR, intension_detector, more than 1 possible option"

        return pos_actions_v[0] if pos_actions_v else None


if __name__ == '__main__':

        sp = SentenceParser()

        sp = SentenceParser()
        q_v = ['I want to add a new record',
               'I just want to view my results',
               'I want to clean my data',
               'back',
               'delete',
               'i want to write a product',
               'give me the status']

        for q in q_v:
            a = sp.intension_detector(q, False)
            print(q)
            print(a)
            print('')
