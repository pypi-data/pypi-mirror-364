"""
Utility functions for preprocessing Indonesian text.
"""

from typing import List, Union

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

    return _get_text_cleaner().clean_html(text)


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


def replace_spell_corrector(text: str) -> str:
    """Mengganti kata gaul (slang) menjadi kata formal.

    Args:
        text: Teks yang mengandung kata slang

    Returns:
        Teks dengan kata formal

    Example:
        >>> from src.preprocessing import replace_spell_corrector
        >>> replace_spell_corrector("emg siapa yg nanya?")
        "memang siapa yang bertanya?"
    """
    if not text:
        return text

    # Menggunakan SpellCorrector yang sudah include slang normalization + spell correction
    return _get_spell_corrector().correct_sentence(text)


def replace_repeated_chars(text: str) -> str:
    """Mengatasi word elongation (karakter berulang).

    Args:
        text: Teks dengan karakter berulang

    Returns:
        Teks dengan karakter berulang dinormalisasi

    Example:
        >>> from src.preprocessing import replace_repeated_chars
        >>> replace_repeated_chars("kenapaaa?")
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

    return _get_text_cleaner().clean_mentions(text)


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

    return _get_text_cleaner().clean_hashtags(text)


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

    return _get_text_cleaner().clean_numbers(text)


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

    return _get_text_cleaner().clean_punctuation(text)


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

    return _get_text_cleaner().clean_extra_spaces(text)


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

    return _get_text_cleaner().clean_special_chars(text)


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

    return _get_text_cleaner().clean_whitespace(text)


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

    return _get_text_cleaner().to_lowercase(text)


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

    return _get_stemmer().stem(text)


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
    Pipeline sederhana untuk menjalankan beberapa fungsi preprocessing secara berurutan.

    Example:
        >>> from nahiarhdNLP.preprocessing import Pipeline, remove_html, remove_url, remove_mentions
        >>>
        >>> # Buat pipeline dengan functions
        >>> pipeline = Pipeline(remove_html, remove_url, remove_mentions)
        >>> result = pipeline.process("Hello <b>world</b> @user https://example.com")
        >>>
        >>> # Atau langsung pakai
        >>> pipeline = Pipeline(remove_url, replace_spell_corrector, to_lowercase)
        >>> result = pipeline.process("Halooo https://google.com gw lg nyari info")
    """

    def __init__(self, *functions):
        """
        Inisialisasi Pipeline dengan functions yang akan dijalankan berurutan.

        Args:
            *functions: Fungsi-fungsi preprocessing yang akan dijalankan secara berurutan
        """
        self.functions = functions

    def process(self, text: str):
        """
        Memproses teks menggunakan semua functions yang sudah di-set.

        Args:
            text: Teks yang akan diproses

        Returns:
            Teks yang sudah diproses oleh semua functions
        """
        if not text:
            return text

        result = text
        for func in self.functions:
            result = func(result)
        return result

    def __call__(self, text: str):
        """Memungkinkan pipeline dipanggil langsung seperti function."""
        return self.process(text)

    def __repr__(self) -> str:
        """String representation."""
        func_names = [func.__name__ for func in self.functions]
        return f"Pipeline({', '.join(func_names)})"


def pipeline(*functions):
    """
    Fungsi helper untuk membuat dan menjalankan pipeline sederhana.

    Args:
        *functions: Fungsi-fungsi preprocessing yang akan dijalankan berurutan

    Returns:
        Pipeline object yang bisa digunakan untuk memproses teks

    Example:
        >>> from nahiarhdNLP.preprocessing import pipeline, remove_url, remove_mentions, to_lowercase
        >>>
        >>> # Buat pipeline
        >>> my_pipeline = pipeline(remove_url, remove_mentions, to_lowercase)
        >>> result = my_pipeline.process("Hello @user https://example.com")
        >>>
        >>> # Atau langsung buat dan pakai
        >>> result = pipeline(remove_html, to_lowercase).process("Hello <b>World</b>")
    """
    return Pipeline(*functions)


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
    replace_repeated_chars: bool = True,
    replace_spell_corrector: bool = True,
    emoji_to_words: bool = False,
    words_to_emoji: bool = False,
    remove_stopwords: bool = False,
    stem_text: bool = False,
    tokenize: bool = False,
) -> Union[str, List[str]]:
    """
    Fungsi preprocess dengan parameter eksplisit untuk setiap step.
    Untuk backward compatibility dan kontrol detail.

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
        replace_repeated_chars: Normalisasi kata berulang
        replace_spell_corrector: Ganti kata slang dengan kata formal
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
        >>> result = preprocess("Halooo @user!", replace_spell_corrector=True)
        >>>
        >>> # Preprocess dengan tokenisasi
        >>> tokens = preprocess("Saya suka makan", tokenize=True)
    """
    # Import fungsi-fungsi yang dibutuhkan di dalam scope ini untuk menghindari circular import

    # Build functions list berdasarkan parameter
    functions = []

    # Import fungsi di module level sudah ada, jadi bisa langsung pakai
    if remove_html:
        functions.append(globals()["remove_html"])
    if remove_url:
        functions.append(globals()["remove_url"])
    if remove_mentions:
        functions.append(globals()["remove_mentions"])
    if remove_hashtags:
        functions.append(globals()["remove_hashtags"])
    if remove_numbers:
        functions.append(globals()["remove_numbers"])
    if remove_special_chars:
        functions.append(globals()["remove_special_chars"])
    if remove_whitespace:
        functions.append(globals()["remove_whitespace"])
    if remove_extra_spaces:
        functions.append(globals()["remove_extra_spaces"])
    if replace_repeated_chars:
        functions.append(globals()["replace_repeated_chars"])
    if emoji_to_words:
        functions.append(globals()["emoji_to_words"])
    if words_to_emoji:
        functions.append(globals()["words_to_emoji"])
    if replace_spell_corrector:
        functions.append(globals()["replace_spell_corrector"])
    if remove_punctuation:
        functions.append(globals()["remove_punctuation"])
    if to_lowercase:
        functions.append(globals()["to_lowercase"])
    if remove_stopwords:
        functions.append(globals()["remove_stopwords"])
    if stem_text:
        functions.append(globals()["stem_text"])
    if tokenize:
        functions.append(globals()["tokenize"])

    # Gunakan Pipeline baru untuk proses
    if functions:
        pipe = Pipeline(*functions)
        return pipe.process(text)
    else:
        return text
