"""
Utility functions for preprocessing Indonesian text.
"""

import re
from typing import Any, Dict, List, Optional, Union

# Import kelas-kelas yang sudah ada
from .cleaning.text_cleaner import TextCleaner
from .linguistic.stemmer import Stemmer
from .linguistic.stopwords import StopwordRemover
from .normalization.emoji import EmojiConverter
from .normalization.spell_corrector import SpellCorrector
from .tokenization.tokenizer import Tokenizer

# Inisialisasi instance global untuk fungsi-fungsi utility (lazy loading)
_text_cleaner = None
_stopword_remover = None
_emoji_converter = None
_spell_corrector = None
_stemmer = None
_tokenizer = None


def _get_text_cleaner():
    global _text_cleaner
    if _text_cleaner is None:
        _text_cleaner = TextCleaner()
    return _text_cleaner


def _get_stopword_remover():
    global _stopword_remover
    if _stopword_remover is None:
        _stopword_remover = StopwordRemover()
        _stopword_remover._load_data()
    return _stopword_remover


def _get_emoji_converter():
    global _emoji_converter
    if _emoji_converter is None:
        _emoji_converter = EmojiConverter()
        _emoji_converter._load_data()
    return _emoji_converter


def _get_spell_corrector():
    global _spell_corrector
    if _spell_corrector is None:
        _spell_corrector = SpellCorrector()
    return _spell_corrector


def _get_stemmer():
    global _stemmer
    if _stemmer is None:
        _stemmer = Stemmer()
    return _stemmer


def _get_tokenizer():
    global _tokenizer
    if _tokenizer is None:
        _tokenizer = Tokenizer()
    return _tokenizer


def remove_html(text: str) -> str:
    """Menghapus HTML tags dari teks.

    Args:
        text: Teks yang mengandung HTML tags

    Returns:
        Teks tanpa HTML tags

    Example:
        >>> from src.preprocessing import remove_html
        >>> remove_html("website <a href='https://google.com'>google</a>")
        "website google"
    """
    if not text:
        return text

    # Pattern untuk menghapus HTML tags
    html_pattern = r"<[^>]+>"
    result = re.sub(html_pattern, "", text)

    # Bersihkan spasi berlebih
    result = re.sub(r"\s+", " ", result).strip()

    return result


def remove_url(text: str) -> str:
    """Menghapus URL dari teks.

    Args:
        text: Teks yang mengandung URL

    Returns:
        Teks tanpa URL

    Example:
        >>> from src.preprocessing import remove_url
        >>> remove_url("retrieved from https://gist.github.com/gruber/8891611")
        "retrieved from "
    """
    if not text:
        return text

    return _get_text_cleaner().clean_urls(text)


def remove_stopwords(text: str) -> str:
    """Menghapus stopwords dari teks.

    Args:
        text: Teks yang mengandung stopwords

    Returns:
        Teks tanpa stopwords

    Example:
        >>> from src.preprocessing import remove_stopwords
        >>> remove_stopwords("siapa yang suruh makan?!!")
        "  suruh makan?!!"
    """
    if not text:
        return text

    return _get_stopword_remover().remove_stopwords(text)


def replace_slang(text: str) -> str:
    """Mengganti kata gaul (slang) menjadi kata formal.

    Args:
        text: Teks yang mengandung kata slang

    Returns:
        Teks dengan kata formal

    Example:
        >>> from src.preprocessing import replace_slang
        >>> replace_slang("emg siapa yg nanya?")
        "memang siapa yang bertanya?"
    """
    if not text:
        return text

    # Menggunakan SpellCorrector yang sudah include slang normalization + spell correction
    return _get_spell_corrector().correct_sentence(text)


def replace_word_elongation(text: str) -> str:
    """Mengatasi word elongation (karakter berulang).

    Args:
        text: Teks dengan karakter berulang

    Returns:
        Teks dengan karakter berulang dinormalisasi

    Example:
        >>> from src.preprocessing import replace_word_elongation
        >>> replace_word_elongation("kenapaaa?")
        "kenapa?"
    """
    if not text:
        return text

    return _get_text_cleaner().clean_repeated_chars(text)


def remove_mentions(text: str) -> str:
    """Menghapus mentions (@username) dari teks.

    Args:
        text: Teks yang mengandung mentions

    Returns:
        Teks tanpa mentions

    Example:
        >>> from src.preprocessing import remove_mentions
        >>> remove_mentions("Halo @user123 apa kabar?")
        "Halo  apa kabar?"
    """
    if not text:
        return text

    # Pattern untuk mentions
    mention_pattern = r"@\w+"
    result = re.sub(mention_pattern, "", text)

    # Bersihkan spasi berlebih
    result = re.sub(r"\s+", " ", result).strip()

    return result


def remove_hashtags(text: str) -> str:
    """Menghapus hashtags (#tag) dari teks.

    Args:
        text: Teks yang mengandung hashtags

    Returns:
        Teks tanpa hashtags

    Example:
        >>> from src.preprocessing import remove_hashtags
        >>> remove_hashtags("Hari ini #senin #libur")
        "Hari ini  "
    """
    if not text:
        return text

    # Pattern untuk hashtags
    hashtag_pattern = r"#\w+"
    result = re.sub(hashtag_pattern, "", text)

    # Bersihkan spasi berlebih
    result = re.sub(r"\s+", " ", result).strip()

    return result


def remove_numbers(text: str) -> str:
    """Menghapus angka dari teks.

    Args:
        text: Teks yang mengandung angka

    Returns:
        Teks tanpa angka

    Example:
        >>> from src.preprocessing import remove_numbers
        >>> remove_numbers("Saya berumur 25 tahun")
        "Saya berumur  tahun"
    """
    if not text:
        return text

    # Pattern untuk numbers
    number_pattern = r"\d+"
    result = re.sub(number_pattern, "", text)

    # Bersihkan spasi berlebih
    result = re.sub(r"\s+", " ", result).strip()

    return result


def remove_punctuation(text: str) -> str:
    """Menghapus tanda baca dari teks.

    Args:
        text: Teks yang mengandung tanda baca

    Returns:
        Teks tanpa tanda baca

    Example:
        >>> from src.preprocessing import remove_punctuation
        >>> remove_punctuation("Halo, apa kabar?!")
        "Halo apa kabar"
    """
    if not text:
        return text

    # Pattern untuk punctuation
    punctuation_pattern = r"[^\w\s]"
    result = re.sub(punctuation_pattern, "", text)

    # Bersihkan spasi berlebih
    result = re.sub(r"\s+", " ", result).strip()

    return result


def remove_extra_spaces(text: str) -> str:
    """Menghapus spasi berlebih dari teks.

    Args:
        text: Teks dengan spasi berlebih

    Returns:
        Teks dengan spasi normal

    Example:
        >>> from src.preprocessing import remove_extra_spaces
        >>> remove_extra_spaces("Halo    dunia   !")
        "Halo dunia !"
    """
    if not text:
        return text

    # Replace multiple spaces with single space
    result = re.sub(r"\s+", " ", text)
    return result.strip()


def remove_special_chars(text: str) -> str:
    """Menghapus karakter khusus yang bukan alfanumerik atau spasi.

    Args:
        text: Teks dengan karakter khusus

    Returns:
        Teks tanpa karakter khusus

    Example:
        >>> from src.preprocessing import remove_special_chars
        >>> remove_special_chars("Halo @#$%^&*() dunia!")
        "Halo  dunia!"
    """
    if not text:
        return text

    # Keep alphanumeric, spaces, and common punctuation
    special_pattern = r'[^\w\s.,!?;:()"\'-]'
    result = re.sub(special_pattern, "", text)

    # Bersihkan spasi berlebih
    result = re.sub(r"\s+", " ", result).strip()

    return result


def remove_whitespace(text: str) -> str:
    """Membersihkan karakter whitespace (tab, newline, dll).

    Args:
        text: Teks dengan karakter whitespace

    Returns:
        Teks dengan whitespace dibersihkan

    Example:
        >>> from src.preprocessing import remove_whitespace
        >>> remove_whitespace("Halo\\n\\tdunia\\r")
        "Halo dunia"
    """
    if not text:
        return text

    # Replace tabs, newlines, etc. with spaces
    result = re.sub(r"\t", " ", text)
    result = re.sub(r"\n", " ", text)
    result = re.sub(r"\r", " ", text)

    # Bersihkan spasi berlebih
    result = re.sub(r"\s+", " ", result).strip()

    return result


def to_lowercase(text: str) -> str:
    """Mengubah teks menjadi huruf kecil.

    Args:
        text: Teks yang akan diubah

    Returns:
        Teks dalam huruf kecil

    Example:
        >>> from src.preprocessing import to_lowercase
        >>> to_lowercase("HALO Dunia")
        "halo dunia"
    """
    if not text:
        return text

    return text.lower()


def emoji_to_words(text: str) -> str:
    """Mengubah emoji menjadi kata-kata bahasa Indonesia.

    Args:
        text: Teks yang mengandung emoji

    Returns:
        Teks dengan emoji diubah menjadi kata

    Example:
        >>> from src.preprocessing import emoji_to_words
        >>> emoji_to_words("emoji 😀😁")
        "emoji wajah_gembira wajah_menyeringai"
    """
    if not text:
        return text

    return _get_emoji_converter().emoji_to_text_convert(text)


def words_to_emoji(text: str) -> str:
    """Mengubah kata-kata menjadi emoji.

    Args:
        text: Teks yang mengandung nama emoji dalam bahasa Indonesia

    Returns:
        Teks dengan kata diubah menjadi emoji

    Example:
        >>> from src.preprocessing import words_to_emoji
        >>> words_to_emoji("emoji wajah_gembira")
        "emoji 😀"
    """
    if not text:
        return text

    return _get_emoji_converter().text_to_emoji_convert(text)


def correct_spelling(text: str) -> str:
    """Mengoreksi ejaan kata dalam teks.

    Args:
        text: Teks yang mungkin mengandung kata salah eja

    Returns:
        Teks dengan ejaan dikoreksi

    Example:
        >>> from src.preprocessing import correct_spelling
        >>> correct_spelling("sya suka mkn nasi")
        "saya suka makan nasi"
    """
    if not text:
        return text

    return _get_spell_corrector().correct_sentence(text)


def stem_text(text: str) -> str:
    """Melakukan stemming pada teks.

    Args:
        text: Teks yang akan di-stem

    Returns:
        Teks yang sudah di-stem

    Example:
        >>> from src.preprocessing import stem_text
        >>> stem_text("bermain-main dengan senang")
        "main main dengan senang"
    """
    if not text:
        return text

    global _stemmer
    if _stemmer is None:
        _stemmer = Stemmer()

    return _stemmer.stem(text)


def tokenize(text: str) -> List[str]:
    """Memecah teks menjadi token.

    Args:
        text: Teks yang akan dipecah

    Returns:
        List token

    Example:
        >>> from src.preprocessing import tokenize
        >>> tokenize("Saya suka makan nasi")
        ["Saya", "suka", "makan", "nasi"]
    """
    if not text:
        return []

    return _get_tokenizer().tokenize(text)


class Pipeline:
    """
    Pipeline untuk menjalankan beberapa preprocessing steps secara berurutan.

    Pipeline ini memungkinkan Anda untuk mengkonfigurasi dan menjalankan
    berbagai fungsi preprocessing dalam urutan yang diinginkan.

    Example:
        >>> from nahiarhdNLP.preprocessing import Pipeline
        >>>
        >>> # Buat pipeline dengan konfigurasi default
        >>> pipeline = Pipeline()
        >>> result = pipeline.process("Halooo @user https://example.com 😀")
        >>>
        >>> # Buat pipeline dengan konfigurasi custom
        >>> config = {
        >>>     'remove_html': True,
        >>>     'remove_url': True,
        >>>     'remove_mentions': True,
        >>>     'remove_hashtags': False,
        >>>     'normalize_slang': True,
        >>>     'correct_spelling': True,
        >>>     'remove_stopwords': True,
        >>>     'stem_text': False,
        >>>     'to_lowercase': True
        >>> }
        >>> pipeline = Pipeline(config)
        >>> result = pipeline.process("gw lg mencri informsi pnting @user")
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Inisialisasi Pipeline dengan konfigurasi.

        Args:
            config: Dictionary konfigurasi untuk mengaktifkan/nonaktifkan steps.
                   Jika None, akan menggunakan konfigurasi default.
        """
        # Konfigurasi default
        self.default_config = {
            # Basic cleaning
            "remove_html": True,
            "remove_url": True,
            "remove_mentions": True,
            "remove_hashtags": True,
            "remove_numbers": False,
            "remove_punctuation": False,
            "remove_special_chars": True,
            "remove_whitespace": True,
            "remove_extra_spaces": True,
            # Text normalization
            "to_lowercase": True,
            "replace_word_elongation": True,
            "normalize_slang": True,
            "correct_spelling": True,
            # Emoji handling
            "emoji_to_words": False,
            "words_to_emoji": False,
            # Linguistic processing
            "remove_stopwords": False,
            "stem_text": False,
            # Tokenization
            "tokenize": False,
        }

        # Gunakan config yang diberikan, atau default
        self.config = config if config is not None else self.default_config.copy()

        # Urutan eksekusi yang logis
        self.execution_order = [
            "remove_html",
            "remove_url",
            "remove_mentions",
            "remove_hashtags",
            "remove_numbers",
            "remove_special_chars",
            "remove_whitespace",
            "remove_extra_spaces",
            "replace_word_elongation",
            "emoji_to_words",
            "words_to_emoji",
            "normalize_slang",
            "correct_spelling",
            "remove_punctuation",
            "to_lowercase",
            "remove_stopwords",
            "stem_text",
            "tokenize",
        ]

        # Inisialisasi instance global untuk performa yang baik
        self._instances = {}

    def _get_instance(self, instance_type: str):
        """Get atau buat instance untuk processor tertentu."""
        if instance_type not in self._instances:
            if instance_type == "text_cleaner":
                self._instances[instance_type] = TextCleaner()
            elif instance_type == "stopword_remover":
                instance = StopwordRemover()
                instance._load_data()
                self._instances[instance_type] = instance
            elif instance_type == "emoji_converter":
                instance = EmojiConverter()
                instance._load_data()
                self._instances[instance_type] = instance
            elif instance_type == "spell_corrector":
                self._instances[instance_type] = SpellCorrector()
            elif instance_type == "stemmer":
                self._instances[instance_type] = Stemmer()
            elif instance_type == "tokenizer":
                self._instances[instance_type] = Tokenizer()

        return self._instances[instance_type]

    def process(self, text: str) -> Union[str, List[str]]:
        """
        Memproses teks menggunakan pipeline yang dikonfigurasi.

        Args:
            text: Teks yang akan diproses

        Returns:
            Teks yang sudah diproses, atau list token jika tokenize=True
        """
        if not text:
            return text

        result = text

        # Jalankan setiap step sesuai urutan
        for step in self.execution_order:
            if not self.config.get(step, False):
                continue

            # Basic cleaning steps
            if step == "remove_html":
                result = remove_html(result)
            elif step == "remove_url":
                result = remove_url(result)
            elif step == "remove_mentions":
                result = remove_mentions(result)
            elif step == "remove_hashtags":
                result = remove_hashtags(result)
            elif step == "remove_numbers":
                result = remove_numbers(result)
            elif step == "remove_punctuation":
                result = remove_punctuation(result)
            elif step == "remove_special_chars":
                result = remove_special_chars(result)
            elif step == "remove_whitespace":
                result = remove_whitespace(result)
            elif step == "remove_extra_spaces":
                result = remove_extra_spaces(result)

            # Text normalization
            elif step == "to_lowercase":
                result = to_lowercase(result)
            elif step == "replace_word_elongation":
                result = replace_word_elongation(result)
            elif step == "normalize_slang":
                result = replace_slang(result)
            elif step == "correct_spelling":
                result = correct_spelling(result)

            # Emoji handling
            elif step == "emoji_to_words":
                result = emoji_to_words(result)
            elif step == "words_to_emoji":
                result = words_to_emoji(result)

            # Linguistic processing
            elif step == "remove_stopwords":
                result = remove_stopwords(result)
            elif step == "stem_text":
                result = stem_text(result)

            # Tokenization (akan mengembalikan list)
            elif step == "tokenize":
                return tokenize(result)

        return result

    def update_config(self, new_config: Dict[str, Any]):
        """
        Update konfigurasi pipeline.

        Args:
            new_config: Dictionary dengan konfigurasi baru
        """
        self.config.update(new_config)

    def reset_config(self):
        """Reset konfigurasi ke default."""
        self.config = self.default_config.copy()

    def get_config(self) -> Dict[str, Any]:
        """Get konfigurasi saat ini."""
        return self.config.copy()

    def get_enabled_steps(self) -> List[str]:
        """Get list step yang aktif."""
        return [step for step in self.execution_order if self.config.get(step, False)]


def pipeline(
    text: str, config: Optional[Dict[str, Any]] = None
) -> Union[str, List[str]]:
    """
    Fungsi helper untuk memproses teks menggunakan pipeline.

    Args:
        text: Teks yang akan diproses
        config: Konfigurasi pipeline (opsional)

    Returns:
        Teks yang sudah diproses

    Example:
        >>> from nahiarhdNLP.preprocessing import pipeline
        >>>
        >>> # Gunakan konfigurasi default
        >>> result = pipeline("Halooo @user https://example.com 😀")
        >>>
        >>> # Gunakan konfigurasi custom
        >>> config = {'remove_url': True, 'normalize_slang': True, 'to_lowercase': True}
        >>> result = pipeline("gw lg browsing https://google.com", config)
    """
    processor = Pipeline(config)
    return processor.process(text)


def preprocess(
    text: str,
    remove_html: bool = True,
    remove_url: bool = True,
    remove_mentions: bool = True,
    remove_hashtags: bool = True,
    remove_numbers: bool = False,
    remove_punctuation: bool = False,
    remove_special_chars: bool = True,
    remove_whitespace: bool = True,
    remove_extra_spaces: bool = True,
    to_lowercase: bool = True,
    replace_word_elongation: bool = True,
    normalize_slang: bool = True,
    correct_spelling: bool = True,
    emoji_to_words: bool = False,
    words_to_emoji: bool = False,
    remove_stopwords: bool = False,
    stem_text: bool = False,
    tokenize: bool = False,
) -> Union[str, List[str]]:
    """
    Fungsi preprocess dengan parameter eksplisit untuk setiap step.

    Args:
        text: Teks yang akan diproses
        remove_html: Hapus HTML tags
        remove_url: Hapus URL
        remove_mentions: Hapus mentions (@user)
        remove_hashtags: Hapus hashtags (#tag)
        remove_numbers: Hapus angka
        remove_punctuation: Hapus tanda baca
        remove_special_chars: Hapus karakter khusus
        remove_whitespace: Hapus whitespace berlebih
        remove_extra_spaces: Hapus spasi berlebih
        to_lowercase: Ubah ke huruf kecil
        replace_word_elongation: Normalisasi kata berulang
        normalize_slang: Normalisasi kata slang
        correct_spelling: Koreksi ejaan
        emoji_to_words: Ubah emoji ke kata
        words_to_emoji: Ubah kata ke emoji
        remove_stopwords: Hapus stopwords
        stem_text: Lakukan stemming
        tokenize: Tokenisasi (return list)

    Returns:
        Teks yang sudah diproses atau list token

    Example:
        >>> from nahiarhdNLP.preprocessing import preprocess
        >>>
        >>> # Preprocess basic
        >>> result = preprocess("Halooo @user!", normalize_slang=True)
        >>>
        >>> # Preprocess dengan tokenisasi
        >>> tokens = preprocess("Saya suka makan", tokenize=True)
    """
    config = {
        "remove_html": remove_html,
        "remove_url": remove_url,
        "remove_mentions": remove_mentions,
        "remove_hashtags": remove_hashtags,
        "remove_numbers": remove_numbers,
        "remove_punctuation": remove_punctuation,
        "remove_special_chars": remove_special_chars,
        "remove_whitespace": remove_whitespace,
        "remove_extra_spaces": remove_extra_spaces,
        "to_lowercase": to_lowercase,
        "replace_word_elongation": replace_word_elongation,
        "normalize_slang": normalize_slang,
        "correct_spelling": correct_spelling,
        "emoji_to_words": emoji_to_words,
        "words_to_emoji": words_to_emoji,
        "remove_stopwords": remove_stopwords,
        "stem_text": stem_text,
        "tokenize": tokenize,
    }

    return pipeline(text, config)
