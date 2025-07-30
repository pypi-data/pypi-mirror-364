from balinese_nlp.textpreprocessor.lemmatization.LevenstheinDistance import Lemmatization
import re
from .utils import load_balinese_lemmatization_file, load_balinese_normalization_dict, load_balinese_stop_words
import unicodedata


class TextPreprocessor:
    # Initialize the data only once when the class is loaded
    # This prevents reloading the file for every function call
    _BALINESE_STOP_WORDS = None
    _BALINESE_NORMALIZE_DICT = None
    _BALINESE_VOCAB = None

    @classmethod
    def _initialize_data(cls):
        if cls._BALINESE_STOP_WORDS is None:
            cls._BALINESE_STOP_WORDS = load_balinese_stop_words()
        if cls._BALINESE_NORMALIZE_DICT is None:
            cls._BALINESE_NORMALIZE_DICT = load_balinese_normalization_dict()
        if cls._BALINESE_VOCAB is None:
            cls._BALINESE_VOCAB = load_balinese_lemmatization_file()

    def __init__(self):
        # Call the initialization method to load data if not already loaded
        TextPreprocessor._initialize_data()
        # Definisikan karakter yang dianggap sebagai bagian dari "kata"
        self.word_chars_set = r"[\w'-]"
        # Definisikan karakter tanda baca umum
        self.punc_chars_set = r"[.,!?;:()\[\]{}'\"“”‘’/]"

        # Kompilasi pola regex untuk tanda baca agar lebih efisien
        self.punc_pattern = re.compile(self.punc_chars_set, re.UNICODE)

        # Pola regex untuk menemukan tanda baca di akhir string (satu atau lebih)
        self.trailing_punc_pattern = re.compile(
            r'(' + self.punc_chars_set + r')+$', re.UNICODE)

        # Pola regex untuk menemukan tanda baca di awal string (satu atau lebih)
        self.leading_punc_pattern = re.compile(
            r'^(' + self.punc_chars_set + r'+)', re.UNICODE)

    def remove_emoji_pattern(self, input_text):
        """
        Remove emojis from the input text.

        Args:
            input_text (str): The text from which to remove emojis.

        Returns:
            str: The cleaned text without emojis.
        """
        # https://en.wikipedia.org/wiki/Unicode_block
        EMOJI_PATTERN = re.compile(
            "["
            "\U0001F1E0-\U0001F1FF"  # flags (iOS)
            "\U0001F300-\U0001F5FF"  # symbols & pictographs
            "\U0001F600-\U0001F64F"  # emoticons
            "\U0001F680-\U0001F6FF"  # transport & map symbols
            "\U0001F700-\U0001F77F"  # alchemical symbols
            "\U0001F780-\U0001F7FF"  # Geometric Shapes Extended
            "\U0001F800-\U0001F8FF"  # Supplemental Arrows-C
            "\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
            "\U0001FA00-\U0001FA6F"  # Chess Symbols
            "\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
            "\U00002702-\U000027B0"  # Dingbats
            "]+"
        )
        # Replace emojis with an empty string
        cleaned_text = EMOJI_PATTERN.sub('', input_text)
        return cleaned_text

    def remove_leading_trailing_whitespace(self, text):
        """
        used to remove leading and trailing whitespace (spaces, tabs, newlines) from a string.

        Args:
            input_text (str): The raw input text

        Returns:
            str: The cleaned text
        """
        return text.strip()

    # remove special characters in text such as tab, enter, \r
    def remove_tab_characters(self, text, tab_characters={
        '\\t': " ",
        '\\n': "",
        '\\u': " ",
        '\\': "",
        '\\r': "",
        '\\x': "",

    }):
        for tab, replaced_with in tab_characters.items():
            text = text.replace(tab, replaced_with)
        return text

    # case folding in text
    def case_folding(self, text):
        return text.lower()

    # add enter after period punctuation
    def add_enter_after_period_punctuation(self, text):
        text = text.replace('.', '.\\n')
        return text

    # word tokenization
    def balinese_word_tokenize(self, sentence):
        """
        Melakukan word tokenization pada kalimat berbahasa Bali.
        Menangani tanda baca, angka, singkatan, dan hipen/apostrof.

        Args:
            sentence (str): Sebuah string kalimat berbahasa Bali.

        Returns:
            list: Sebuah daftar token (kata-kata) dari kalimat.
        """
        if not isinstance(sentence, str):
            raise TypeError("Input must be a string.")
        if not sentence.strip():  # Return empty list if sentence is just whitespace
            return []

        # 1. Menangani hipen yang memisahkan suku kata di akhir baris (misalnya "Administra-tion")
        # Jika ada pola 'kata- spasi kata', gabungkan menjadi satu kata
        sentence = re.sub(r'(\w+)-\s+(\w+)', r'\1\2', sentence)

        # Definisikan karakter yang dianggap sebagai bagian dari "kata"
        # (huruf, angka, underscore, hipen, apostrof)
        word_chars_set = r"[\w'-]"

        # Definisikan karakter tanda baca yang bisa muncul berdiri sendiri atau melekat pada kata
        # Ini mencakup semua tanda baca umum yang Anda sebutkan
        punc_chars_set = r"[.,!?;:()\[\]{}'\"“”‘’/]"

        # 2. Pola Regular Expression untuk tokenisasi kata
        # Ini adalah pola yang lebih komprehensif:
        # - \w+ : Mencocokkan satu atau lebih karakter "kata" (huruf, angka, underscore). Ini menangkap kata-kata biasa dan angka.
        # - \- : Mencocokkan tanda hubung (-) literal. Penting untuk meng-escape karena '-' di dalam [] bisa berarti rentang.
        # - [.,!?;:()\[\]{}'"“”‘’/] : Mencocokkan tanda baca umum secara literal.
        # - (\s+) : Mencocokkan satu atau lebih spasi (ini akan dipisahkan sebagai token spasi jika kita tidak filter).
        #
        # Pendekatan yang lebih baik adalah mencocokkan *kata-kata* dan *tanda baca* secara terpisah.
        # Ini akan memastikan tanda baca selalu menjadi token terpisah.

        # Memisahkan tanda baca dari kata. Pola ini akan mencari:
        # a. Satu atau lebih karakter kata (huruf, angka, underscore)
        # b. Tanda baca yang tidak diikuti oleh tanda kutip (untuk menghindari pemisahan "kata." -> "kata", ".")
        # c. Tanda baca yang diikuti oleh tanda kutip
        # d. Angka atau singkatan seperti "N.I.C.A." atau "No. 1" yang mungkin memiliki titik di tengah.
        #    Kita akan mencoba mempertahankan pola ini sebagai satu token sebisa mungkin pada langkah selanjutnya.

        # Menangani singkatan seperti "N.I.C.A." atau "M."
        # Ide: pisahkan tanda baca secara eksplisit, kecuali untuk titik di tengah singkatan.
        # Pola yang lebih baik:
        # - Kata-kata biasa: \b\w+'?\w*\b (menangani apostrof seperti "Indonésiané")
        # - Singkatan yang mungkin memiliki titik: (?:[A-Z]\.)+ (e.g., N.I.C.A.)
        # - Angka (termasuk desimal): \d+(?:[.,]\d+)?
        # - Tanda baca tunggal: [.,!?;:()\[\]{}'"“”‘’/-] (tanda hubung sebagai token terpisah jika tidak terikat ke kata)

        # Pola yang lebih canggih:
        # 1. Kata-kata biasa (dengan atau tanpa apostrof): \b\w+(?:'\w+)?\b
        # 2. Angka (termasuk desimal/ribuan): \d+(?:[.,]\d+)?
        # 3. Singkatan dengan titik di tengah: (?:[A-Z]\.)+[A-Z]?
        # 4. Tanda baca: [^\s\w] (apapun yang bukan spasi atau karakter kata)

        # Menggabungkan pola dengan prioritas:
        # - Singkatan huruf kapital dengan titik (e.g., N.I.C.A.)
        # - Kata-kata yang mengandung apostrof (e.g., Indonésiané)
        # - Angka (termasuk desimal/ribuan)
        # - Kata-kata biasa
        # - Semua tanda baca lainnya
        token_pattern = re.compile(r"""
            # 1. Singkatan huruf kapital dengan titik (e.g., N.I.C.A., Mr.)
            (?:[A-Z]\.)+[A-Z]?

            # 2. Angka (termasuk desimal/ribuan)
            | \d+(?:[.,]\d+)?

            # 3. KATA yang mungkin memiliki HIPEN/APOSTROF internal DAN mungkin memiliki TANDA BACA di AKHIR
            # Ini adalah perubahan kunci untuk "uyeng-uyengan," atau "pianakne,"
            # Mencocokkan serangkaian karakter kata, diikuti secara opsional oleh nol atau lebih
            # karakter tanda baca dari punc_chars_set. Batas kata (\b) di akhir memastikan
            # bahwa itu tidak melintasi spasi atau batas kata lainnya.
            | \b""" + word_chars_set + r"""+(?:""" + punc_chars_set + r""")*\b

            # 4. Urutan tanda baca yang berdiri sendiri (misalnya "!!", ".?", "...", atau tanda kutip tunggal)
            # Ini akan mencocokkan satu atau lebih karakter dari punc_chars_set.
            # Penting: Pola ini harus ditempatkan SETELAH pola "kata dengan tanda baca di akhir"
            # agar pola kata mendapatkan prioritas lebih tinggi.
            | """ + punc_chars_set + r"""+

            # 5. Pola fallback untuk karakter non-spasi, non-kata, non-tanda-baca lainnya
            # (Misalnya simbol matematika, simbol mata uang, jika tidak termasuk dalam angka)
            | [^\s\w]

        """, re.VERBOSE | re.UNICODE)  # re.VERBOSE memungkinkan komentar dalam regex, re.UNICODE mendukung karakter Unicode

        raw_tokens = token_pattern.findall(sentence)

        final_tokens = []

        # Pola Regex untuk memisahkan tanda baca di AWAL token
        # Ini hanya akan berlaku untuk token yang dimulai dengan tanda baca diikuti oleh sesuatu yang lain
        # Contoh: "(kata" seharusnya menjadi "(" dan "kata"
        # Ini TIDAK akan memengaruhi "kata,", "kata.", atau "!!", karena pola utama sudah menanganinya.
        leading_punctuation_pattern = re.compile(
            r'^(' + punc_chars_set + r'+)(.*)', re.UNICODE)

        for token in raw_tokens:
            # Lewati jika token kosong setelah pemrosesan awal
            if not token.strip():
                continue

            # Periksa dan pisahkan tanda baca di AWAL token
            match_start = leading_punctuation_pattern.match(token)
            if match_start:
                # Tambahkan tanda baca di awal
                final_tokens.append(match_start.group(1))
                remaining_token = match_start.group(2)
                if remaining_token:  # Tambahkan sisa token jika tidak kosong
                    final_tokens.append(remaining_token)
            else:
                # Jika tidak ada tanda baca di awal, atau jika itu adalah kata-dengan-tanda-baca-di-akhir,
                # atau tanda baca murni, tambahkan token seperti adanya.
                final_tokens.append(token)

        # Saring string kosong yang mungkin dihasilkan
        return [t for t in final_tokens if t and not t.isspace()]

    # function to segment balinese paragraphs into sentences
    def balinese_sentences_segmentation(self, text):
        """
        Melakukan segmentasi kalimat pada teks berbahasa Bali.
        Menangani titik, tanda kutip dalam percakapan, tanda seru, dan tanda tanya sebagai pemisah.
        Memperhatikan variasi penulisan dalam teks pidato.
        """
        # 1. Pra-pemrosesan Teks: Ganti newline dengan spasi dan bersihkan spasi berlebih
        text = text.replace('\n', ' ').strip()
        # Ganti multiple spaces dengan single space
        text = re.sub(r'\s+', ' ', text)

        # 2. Pola Regular Expression yang Lebih Lanjut untuk Segmentasi Awal
        sentences = re.split(
            r'(?<=[.!?])\s+(?=[A-Z"])|(?<=["])(\s*)(?=[A-Z])', text)

        # Filter out None values that might arise from alternative splits in regex
        sentences = [s for s in sentences if s is not None]

        # 3. Pembersihan dan Penggabungan Kalimat yang Terpecah (terutama percakapan)
        cleaned_sentences = []
        i = 0
        while i < len(sentences):
            current_sentence = sentences[i].strip()
            if not current_sentence:  # Skip empty strings
                i += 1
                continue

            # Kasus a: Kalimat dimulai dengan tanda kutip pembuka dan kalimat sebelumnya tidak berakhir dengan tanda kutip
            # Ini menandakan kelanjutan percakapan yang mungkin terpisah di baris baru.
            if current_sentence.startswith(('"', '“', '‘')) and len(cleaned_sentences) > 0 and \
                    not cleaned_sentences[-1].endswith(('"', '”', '’', '.', '!', '?')):
                cleaned_sentences[-1] += " " + current_sentence
            # Kasus b: Kalimat sebelumnya adalah poin daftar (e.g., "a. ") dan kalimat sekarang adalah kelanjutannya.
            # Atau kasus judul/item daftar tanpa tanda baca akhir yang diikuti oleh teks.
            elif len(cleaned_sentences) > 0 and \
                (re.match(r'^[a-zA-Z]\.', cleaned_sentences[-1].strip()) or re.match(r'^-', cleaned_sentences[-1].strip())) and \
                    not (current_sentence[0].isupper() or current_sentence.startswith(('"', '“', '‘'))):
                cleaned_sentences[-1] += " " + current_sentence
            else:
                cleaned_sentences.append(current_sentence)
            i += 1

        # 4. Finalisasi: Penanganan Tanda Kutip Penutup dan Pembersihan Akhir
        # Ini mengatasi kasus di mana tanda kutip penutup tidak langsung diikuti oleh pemisah kuat.
        final_sentences = []
        temp_sentence = ""
        for s in cleaned_sentences:
            if temp_sentence:
                temp_sentence += " " + s
            else:
                temp_sentence = s

            # Kriteria untuk mengakhiri sebuah kalimat (terutama percakapan)
            # Jika berakhir dengan tanda kutip, anggap sebagai akhir percakapan.
            # Jika tidak ada tanda kutip, periksa tanda baca akhir kalimat standar.
            # Hindari memisahkan kalimat yang dimulai dengan kutipan tapi belum berakhir.
            # PERBAIKAN: Meng-escape tanda tanya (?) agar dibaca sebagai karakter literal
            if (re.search(r'[.!?"]$|!”$|.”$|\?’$', temp_sentence) and not (temp_sentence.startswith(('"', '“', '‘')) and not re.search(r'[.!?"]$|!”$|.”$|\?’$', temp_sentence))) or \
                    (not re.search(r'[.!?"]$|!”$|.”$|\?’$', temp_sentence) and not temp_sentence.startswith(('"', '“', '‘')) and (temp_sentence.endswith('.') or temp_sentence.endswith('!') or temp_sentence.endswith('?'))):
                final_sentences.append(temp_sentence.strip())
                temp_sentence = ""

        # Tambahkan sisa kalimat jika ada setelah loop
        if temp_sentence:
            final_sentences.append(temp_sentence.strip())

        # Bersihkan lagi dari string kosong yang mungkin tersisa
        final_sentences = [s for s in final_sentences if s]

        return final_sentences

    def convert_ascii_sentence(self, sentence):
        """
        Converts a sentence to contain only ASCII characters and ASCII punctuation.
        Non-ASCII characters (including accented letters) and non-ASCII punctuation
        are removed.

        Args:
            sentence: A string of sentence.

        Returns:
            A string with all non-ASCII characters and
            non-ASCII punctuation removed.
        """
        # Normalize the string to NFKD form (Compatibility Decomposition).
        # This separates base characters from their diacritical marks (accents, etc.).
        # For example, 'é' becomes 'e' followed by a combining acute accent.
        # This step is crucial for properly converting accented characters before encoding.
        normalized_sentence = unicodedata.normalize('NFKD', sentence)

        # Encode the normalized string to 'ascii' and then decode it back.
        # The 'ignore' error handler ensures that any character that cannot
        # be represented in ASCII (i.e., all non-ASCII characters, including
        # diacritics and non-ASCII punctuation) is simply dropped.
        ascii_only_sentence = normalized_sentence.encode(
            'ascii', 'ignore').decode('ascii')

        # Strip any leading or trailing whitespace that might result from
        # the removal of characters, ensuring clean sentence boundaries.
        cleaned_sentence = ascii_only_sentence.strip()

        return cleaned_sentence

    def remove_special_punctuation(self, text, special_punctuations={
        '–': '-',
        "…": " ",
        "..": ".",
        '„„': ""
    }):
        for special_punc, replaced_with in special_punctuations.items():
            text = text.replace(special_punc, replaced_with)
        return text

    # remove punctiation based on string.punctuation in text
    def remove_punctuation(self, text, exclude=None):
        """
        Removes punctuation from the given text, excluding specified characters.

        Args:
            text (str): The input string to preprocess.
            exclude (list, optional): A list of punctuation characters to *keep*.
                                      Defaults to an empty list.

        Returns:
            str: The text with specified punctuations removed.
        """
        if exclude is None:
            exclude = []

        # Define a comprehensive set of punctuation characters
        # Note: Some common Balinese punctuation or symbols might not be in this standard set,
        # so you might need to extend it based on your specific text data.
        string_punctuation = '''!"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~“”‘’'''

        # Create a mutable set from the punctuation string for easier manipulation
        punctuation_to_remove = set(string_punctuation)

        # Remove characters from the set that are in the exclude list
        for char_to_keep in exclude:
            punctuation_to_remove.discard(char_to_keep)

        # Create the translation table
        # str.maketrans maps each character in the first argument to None
        # if the third argument is provided, effectively deleting them.
        translator = str.maketrans("", "", "".join(punctuation_to_remove))

        # Apply the translation and strip leading/trailing whitespace
        cleaned_text = text.translate(translator).strip()

        return cleaned_text

    # remove multiple whitespace into single whitespace

    def remove_whitespace_multiple(self, text):
        return re.sub('\s+', ' ', text)

    # remove number in text 1 digit or more
    def remove_number(self, text):
        return re.sub(r"\d+", "", text)

    def remove_exclamation_words(self, text, exclamation_words=[
        'Prrrr.',
        'Brrr.',
        'biaaar',
        'Beh',
        'ri…ri…',
        'kwek…',
        'Ihhh…'
    ]):

        for seruan in exclamation_words:
            text = text.replace(seruan, '')
        return text

    def remove_person_entities_in_text(self, sentences, list_of_detected_character):
        for character in list_of_detected_character:
            sentences = sentences.replace(character, '')
        sentences = sentences.replace('  ', ' ').replace(' .', '.')
        return sentences.strip()

    def remove_stop_words(self, text):
        BALINESE_STOP_WORDS = TextPreprocessor._BALINESE_STOP_WORDS
        # remove stopwords process
        tokenize_text = self.balinese_word_tokenize(text)
        for idx, token in enumerate(tokenize_text):
            if token.lower() in BALINESE_STOP_WORDS:
                del tokenize_text[tokenize_text.index(token)]

        return " ".join(tokenize_text)

    def remove_parentheses(self, text):
        return re.sub(r'\([^)]*\)$', '', text)

    def remove_substring(self, text, substring):
        return text.replace(substring, '')

    def remove_urls_and_link(self, text, sub_patterns_to_remove=[
        'LINK:', 'LINK : ', 'Link :'
    ]):
        """
        Function to remove URLs and "LINK : " from a text
        """
        url_pattern = re.compile(r'https?://\S+|www\.\S+')
        text_without_urls = url_pattern.sub(r'', text)
        for sub_pattern_to_remove in sub_patterns_to_remove:
            text_without_urls = text_without_urls.replace(
                sub_pattern_to_remove, '')
        return text_without_urls

    def remove_non_ascii_punctuation(self, text):
        """
        Removes non-ASCII punctuation and symbols from a given text string,
        handling None values and empty strings.

        Args:
            text: The input text string.  Can be None or an empty string.

        Returns:
            The text string with non-ASCII punctuation removed, or an empty string
            if the input was None or an empty string.
        """
        if text is None:
            return ""  # Or any other appropriate default value
        text = str(text)  # Convert to string in case the value is not a string
        if not text:
            return ""
        # Remove non-ascii characters
        text = text.encode("ascii", "ignore").decode()
        # Remove non-ascii punctuation and symbols
        text = re.sub(r'[^\x00-\x7F]+', '', text)
        return text

    def normalize_words(self, text):
        # Balinese Normalize Words
        BALINESE_NORMALIZE_WORDS = TextPreprocessor._BALINESE_NORMALIZE_DICT['normalized']
        BALINESE_UNNORMALIZE_WORDS = TextPreprocessor._BALINESE_NORMALIZE_DICT['unnormalized']

        # normalize words process
        tokenize_text = self.balinese_word_tokenize(text)
        for idx, token in enumerate(tokenize_text):
            if token.lower() in BALINESE_UNNORMALIZE_WORDS:
                tokenize_text[tokenize_text.index(
                    token)] = BALINESE_NORMALIZE_WORDS[BALINESE_UNNORMALIZE_WORDS.index(token.lower())]

        return " ".join(tokenize_text)

    def lemmatize_text(self, text):
        BALINESE_VOCABS = TextPreprocessor._BALINESE_VOCAB
        lemmatized_tokens = [Lemmatization(BALINESE_VOCABS).lemmatization(
            token.strip()) for token in text.split(' ')]
        return ' '.join(lemmatized_tokens)

    def replace_substrings(self, text, substrings=None):
        """
        Function to all the substrings in text with empty ('')
        input:
        - text: Str
        - substrings: list

        return:
        - text without the substrings
        """
        if substrings is None:
            return text

        for substring in substrings:
            text = text.replace(substring, '')

        return text

    def remove_punctuation_from_token(self, token):
        """
        Menghapus semua tanda baca dari sebuah token string.

        Args:
            token (str): Sebuah token (kata) yang mungkin mengandung tanda baca.

        Returns:
            str: Token tanpa tanda baca.
        """
        return self.punc_pattern.sub('', token)

    def get_trailing_punctuation(self, token):
        """
        Mendapatkan tanda baca yang menempel di akhir sebuah token.

        Args:
            token (str): Sebuah token (kata) yang mungkin mengandung tanda baca di akhirnya.

        Returns:
            str: String yang berisi tanda baca di akhir token, atau string kosong jika tidak ada.
        """
        match = self.trailing_punc_pattern.search(token)
        if match:
            return match.group(0)
        return ""

    def split_token_and_trailing_punctuation(self, token_str):
        """
        Memisahkan sebuah token menjadi bagian kata dan tanda baca di akhir (jika ada).
        Contoh: 'uyeng-uyengan,' akan menjadi ['uyeng-uyengan', ',']

        Args:
            token_str (str): Sebuah string token.

        Returns:
            list: Daftar yang berisi [bagian_kata, tanda_baca_akhir] jika ada tanda baca
                  di akhir, atau [bagian_kata] jika tidak ada.
        """
        trailing_punc = self.get_trailing_punctuation(token_str)
        if trailing_punc:
            word_part = token_str[:-len(trailing_punc)]
            if not word_part and trailing_punc:  # Handle cases like '!' or '?' as standalone
                return [trailing_punc]
            return [word_part, trailing_punc]
        else:
            return [token_str]

    def split_token_by_punctuation(self, token_str):
        """
        Memisahkan sebuah token menjadi bagian tanda baca awal, kata, dan tanda baca akhir.

        Args:
            token_str (str): Sebuah string token.

        Returns:
            list: Daftar yang berisi bagian-bagian token yang sudah dipisahkan.
                  Contoh: ['(', 'kata', ')'], ['kata', '?'], ['"', 'teks', '!'], ['!'], ['kata']
        """
        result = []
        current_processing_str = token_str

        # 1. Ekstrak tanda baca awal
        match_leading = self.leading_punc_pattern.match(current_processing_str)
        leading_punc = ""
        if match_leading:
            leading_punc = match_leading.group(0)
            current_processing_str = current_processing_str[len(
                leading_punc):]  # Sisa string

        # 2. Ekstrak tanda baca akhir dari sisa string
        match_trailing = self.trailing_punc_pattern.search(
            current_processing_str)
        trailing_punc = ""
        word_part = ""
        if match_trailing:
            trailing_punc = match_trailing.group(0)
            # Bagian kata di tengah
            word_part = current_processing_str[:-len(trailing_punc)]
        else:
            # Jika tidak ada tanda baca akhir, seluruh sisa adalah kata
            word_part = current_processing_str

        # 3. Tambahkan bagian-bagian yang tidak kosong ke hasil
        if leading_punc:
            result.append(leading_punc)

        # Pastikan bagian kata tidak kosong (misal untuk input '()')
        if word_part:
            result.append(word_part)

        if trailing_punc:
            result.append(trailing_punc)

        # Jika hasilnya kosong (misalnya input adalah string kosong atau hanya spasi),
        # atau jika token asli hanya terdiri dari tanda baca yang sudah ditangani,
        # pastikan outputnya konsisten (misal '!' menjadi ['!'])
        if not result and token_str:
            # Ini akan menangani kasus di mana token_str murni tanda baca
            # dan belum ditambahkan ke result (seharusnya sudah ditangani oleh leading_punc)
            # Namun, ini sebagai fallback jika ada edge case yang terlewat
            return [token_str] if token_str.strip() else []

        return result
