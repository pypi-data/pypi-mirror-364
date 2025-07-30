# nahiarhdNLP - Indonesian Natural Language Processing Library

Library Indonesian Natural Language Processing dengan fitur preprocessing teks, normalisasi slang, konversi emoji, koreksi ejaan, dan berbagai fungsi text processing lainnya.

## 🚀 Instalasi

```bash
pip install nahiarhdNLP
```

## 📦 Import Library

```python
# Import functions dari preprocessing
from nahiarhdNLP.preprocessing import (
    # Fungsi pembersihan dasar
    remove_html, remove_url, remove_mentions, remove_hashtags,
    remove_numbers, remove_punctuation, remove_extra_spaces,
    remove_special_chars, remove_whitespace, to_lowercase,
    # Fungsi normalisasi dan koreksi
    replace_spell_corrector, replace_repeated_chars,
    # Fungsi emoji
    emoji_to_words, words_to_emoji,
    # Fungsi linguistic
    remove_stopwords, stem_text, tokenize,
    # Fungsi pipeline
    pipeline, preprocess
)

# Import kelas untuk penggunaan advanced
from nahiarhdNLP.preprocessing import (
    TextCleaner, SpellCorrector, StopwordRemover,
    Stemmer, EmojiConverter, Tokenizer, Pipeline
)

# Import dataset loader
from nahiarhdNLP.datasets import DatasetLoader
```

## 📋 Contoh Penggunaan

### 1. 🧹 TextCleaner - Membersihkan Teks

```python
from nahiarhdNLP.preprocessing import TextCleaner

cleaner = TextCleaner()

# Membersihkan URL
url_text = "kunjungi https://google.com sekarang!"
clean_result = cleaner.clean_urls(url_text)
print(clean_result)
# Output: "kunjungi  sekarang!"

# Membersihkan mentions
mention_text = "Halo @user123 apa kabar?"
clean_result = cleaner.clean_mentions(mention_text)
print(clean_result)
# Output: "Halo  apa kabar?"
```

### 2. ✏️ SpellCorrector - Koreksi Ejaan & Normalisasi Slang

```python
from nahiarhdNLP.preprocessing import SpellCorrector

spell = SpellCorrector()

# Koreksi kata salah eja
word = "mencri"
corrected = spell.correct_word(word)
print(corrected)
# Output: "mencuri"

# Koreksi kalimat lengkap (termasuk normalisasi slang)
sentence = "gw lg mencri informsi"
corrected = spell.correct_sentence(sentence)
print(corrected)
# Output: "saya lagi mencuri informasi"
```

### 3. 🚫 StopwordRemover - Menghapus Stopwords

```python
from nahiarhdNLP.preprocessing import StopwordRemover

stopword = StopwordRemover()
stopword._load_data()  # Load dataset stopwords

# Menghapus stopwords
text = "saya suka makan nasi goreng"
result = stopword.remove_stopwords(text)
print(result)
# Output: "suka makan nasi goreng"

# Cek apakah kata adalah stopword
is_stop = stopword.is_stopword("adalah")
print(is_stop)  # True
```

### 4. 😀 EmojiConverter - Konversi Emoji

```python
from nahiarhdNLP.preprocessing import EmojiConverter

emoji = EmojiConverter()
emoji._load_data()  # Load dataset emoji

# Emoji ke teks
emoji_text = "😀 😂 😍"
text_result = emoji.emoji_to_text_convert(emoji_text)
print(text_result)

# Teks ke emoji
text = "wajah_gembira"
emoji_result = emoji.text_to_emoji_convert(text)
print(emoji_result)
```

### 5. 🔪 Tokenizer - Tokenisasi

```python
from nahiarhdNLP.preprocessing import Tokenizer

tokenizer = Tokenizer()

# Tokenisasi teks
text = "ini contoh tokenisasi"
tokens = tokenizer.tokenize(text)
print(tokens)
# Output: ['ini', 'contoh', 'tokenisasi']
```

### 6. 🌿 Stemmer - Stemming

```python
from nahiarhdNLP.preprocessing import Stemmer

try:
    stemmer = Stemmer()
    text = "bermain-main dengan senang"
    result = stemmer.stem(text)
    print(result)
    # Output: "main main dengan senang"
except ImportError:
    print("Install Sastrawi dengan: pip install Sastrawi")
```

### 7. 🛠️ Fungsi Individual

```python
from nahiarhdNLP.preprocessing import (
    remove_html, remove_url, remove_mentions, remove_hashtags,
    remove_numbers, remove_punctuation, remove_extra_spaces,
    remove_special_chars, remove_whitespace, to_lowercase,
    replace_spell_corrector, replace_repeated_chars,
    emoji_to_words, words_to_emoji, remove_stopwords,
    stem_text, tokenize
)

# 🧹 FUNGSI PEMBERSIHAN DASAR

# Menghapus HTML tags
html_text = "website <a href='https://google.com'>google</a>"
clean_result = remove_html(html_text)
print(clean_result)
# Output: "website google"

# Menghapus URL
url_text = "kunjungi https://google.com sekarang!"
clean_result = remove_url(url_text)
print(clean_result)
# Output: "kunjungi  sekarang!"

# Menghapus mentions (@username)
mention_text = "Halo @user123 dan @admin apa kabar?"
clean_result = remove_mentions(mention_text)
print(clean_result)
# Output: "Halo  dan  apa kabar?"

# Menghapus hashtags (#tag)
hashtag_text = "Hari ini #senin #libur #weekend"
clean_result = remove_hashtags(hashtag_text)
print(clean_result)
# Output: "Hari ini   "

# ✨ FUNGSI NORMALISASI DAN KOREKSI

# Normalisasi slang dan koreksi ejaan (menggunakan SpellCorrector)
slang_text = "emg siapa yg nanya?"
normal_text = replace_spell_corrector(slang_text)
print(normal_text)
# Output: "memang siapa yang bertanya?"

# Mengatasi perpanjangan kata (word elongation)
elongation_text = "kenapaaa bangettt???"
clean_result = replace_repeated_chars(elongation_text)
print(clean_result)
# Output: "kenapa banget???"

# Koreksi ejaan kompleks
spell_text = "saya mencri informsi pnting"
corrected = replace_spell_corrector(spell_text)
print(corrected)
# Output: "saya mencari informasi penting"

# 😀 FUNGSI EMOJI

# Konversi emoji ke kata
emoji_text = "😀 😂 😍"
text_result = emoji_to_words(emoji_text)
print(text_result)

# Konversi kata ke emoji
text_to_emoji = "wajah_gembira wajah_sedih"
emoji_result = words_to_emoji(text_to_emoji)
print(emoji_result)

# 🔬 FUNGSI LINGUISTIC

# Menghapus stopwords
stopword_text = "saya sangat suka sekali makan nasi goreng"
clean_result = remove_stopwords(stopword_text)
print(clean_result)
# Output: "  suka  makan nasi goreng"

# Stemming teks (memerlukan Sastrawi)
try:
    stem_text_input = "bermain-main dengan gembira"
    stemmed = stem_text(stem_text_input)
    print(stemmed)
    # Output: "main main dengan gembira"
except ImportError:
    print("Install Sastrawi: pip install Sastrawi")

# Tokenisasi teks
tokenize_text = "Saya suka makan nasi goreng"
tokens = tokenize(tokenize_text)
print(tokens)
# Output: ['Saya', 'suka', 'makan', 'nasi', 'goreng']
```

### 8. 🔀 Pipeline - Preprocessing Sekaligus

Pipeline yang super simple - langsung pass functions yang mau dipakai!

```python
from nahiarhdNLP.preprocessing import Pipeline, remove_html, remove_url, remove_mentions, to_lowercase

# 🚀 CARA PAKAI YANG SIMPLE

# Langsung pass functions yang mau dipakai
pipeline = Pipeline(remove_html, remove_url, remove_mentions)
result = pipeline.process("Hello <b>world</b> @user https://example.com")
print(result)
# Output: "Hello world  "

# Bebas pilih functions sesuai kebutuhan
pipeline = Pipeline(remove_url, replace_spell_corrector, to_lowercase)
result = pipeline.process("Halooo https://google.com gw lg nyari info")
print(result)

# Pipeline bisa dipanggil langsung seperti function
result = pipeline("Test text lainnya")
print(result)

# Contoh lain - untuk social media text
social_pipeline = Pipeline(
    remove_mentions,
    remove_hashtags,
    remove_url,
    replace_spell_corrector,
    to_lowercase
)
result = social_pipeline.process("Halooo @user #trending https://example.com gw lg nyari info")
print(result)

# Untuk cleaning basic
basic_pipeline = Pipeline(remove_html, remove_extra_spaces, to_lowercase)
result = basic_pipeline.process("Hello <b>World</b>   !")
print(result)

# Tokenisasi juga bisa langsung
token_pipeline = Pipeline(remove_url, to_lowercase, tokenize)
tokens = token_pipeline.process("Hello https://google.com World")
print(tokens)  # ['hello', 'world']

# 🎯 FUNGSI PIPELINE HELPER

# Buat pipeline dengan helper function
from nahiarhdNLP.preprocessing import pipeline

my_pipeline = pipeline(remove_url, remove_mentions, to_lowercase)
result = my_pipeline.process("Hello @user https://example.com")
print(result)

# Atau langsung chain
result = pipeline(remove_html, to_lowercase).process("Hello <b>World</b>")
print(result)
```

#### 🎯 Kenapa Pipeline Ini Lebih Baik?

- ✅ **Super Simple** - No config dictionary, langsung pass functions!
- ✅ **Flexible** - Bebas pilih functions apa aja sesuai kebutuhan
- ✅ **Clean Code** - Cuma 30 baris, gak ada kompleksitas berlebih
- ✅ **To The Point** - Exactly what you need, nothing more
- ✅ **Easy to Read** - `Pipeline(remove_url, to_lowercase)` langsung jelas

#### 📝 Available Functions untuk Pipeline

```python
# Basic cleaning
remove_html, remove_url, remove_mentions, remove_hashtags,
remove_numbers, remove_punctuation, remove_special_chars,
remove_whitespace, remove_extra_spaces

# Text transformation
to_lowercase, replace_repeated_chars, replace_spell_corrector

# Emoji handling
emoji_to_words, words_to_emoji

# Linguistic processing
remove_stopwords, stem_text, tokenize
```

### 9. 📊 Dataset Loader

```python
from nahiarhdNLP.datasets import DatasetLoader

loader = DatasetLoader()

# Load stopwords dari CSV lokal
stopwords = loader.load_stopwords_dataset()
print(f"Jumlah stopwords: {len(stopwords)}")

# Load slang dictionary dari CSV lokal
slang_dict = loader.load_slang_dataset()
print(f"Jumlah slang: {len(slang_dict)}")

# Load emoji dictionary dari CSV lokal
emoji_dict = loader.load_emoji_dataset()
print(f"Jumlah emoji: {len(emoji_dict)}")

# Load wordlist dari JSON lokal
wordlist = loader.load_wordlist_dataset()
print(f"Jumlah kata: {len(wordlist)}")
```

> **Catatan:** Semua dataset (stopword, slang, emoji, wordlist) di-load langsung dari file CSV/JSON di folder `nahiarhdNLP/datasets/`. Tidak ada proses download dari external source.

## 🚨 Error Handling

```python
try:
    from nahiarhdNLP.preprocessing import SpellCorrector
    spell = SpellCorrector()
    result = spell.correct_sentence("test")
except ImportError:
    print("Package nahiarhdNLP belum terinstall")
    print("Install dengan: pip install nahiarhdNLP")
except Exception as e:
    print(f"Error: {e}")
```

## 💡 Tips Penggunaan

1. **Untuk preprocessing simple**: Gunakan `Pipeline(function1, function2, ...)` - langsung pass functions!
2. **Untuk kontrol detail**: Gunakan `preprocess()` dengan parameter boolean
3. **Untuk kontrol penuh**: Gunakan kelas individual (`TextCleaner`, `SpellCorrector`, dll)
4. **Untuk spell correction + slang**: Gunakan `SpellCorrector` yang menggabungkan kedua fitur
5. **Untuk stemming**: Install Sastrawi terlebih dahulu: `pip install Sastrawi`
6. **Untuk load dataset**: Gunakan `DatasetLoader` dari `nahiarhdNLP.datasets`
7. **Untuk inisialisasi kelas**: Panggil `_load_data()` untuk kelas yang memerlukan dataset
8. **Pipeline design**: `Pipeline(remove_url, to_lowercase)` lebih jelas daripada config dictionary
9. **Function chaining**: Pipeline bisa dipanggil seperti function dengan `pipeline("text")`

## ⚡ Performance & Dataset

nahiarhdNLP menggunakan **dataset lokal** yang sudah disediakan:

- **Stopwords**: File `stop_word.csv` (788 kata)
- **Slang Dictionary**: File `slang.csv` (15,675 pasangan)
- **Emoji Mapping**: File `emoji.csv` (3,530 emoji)
- **Wordlist**: File `wordlist.json` (kamus kata Indonesia)
- **KBBI Dictionary**: File `kata_dasar_kbbi.csv` (28,527 kata)
- **Kamus Tambahan**: File `kamus.txt` (30,871 kata)

Semua dataset tersimpan di folder `nahiarhdNLP/datasets/` dan diakses melalui `DatasetLoader`.

## 📦 Dependencies

Package ini membutuhkan:

- `pandas` - untuk load dan proses dataset CSV/JSON
- `Sastrawi` - untuk stemming (opsional)
- `rich` - untuk output formatting di demo (opsional)

## 🔧 Struktur Modul

````markdown
```text
nahiarhdNLP/
├── datasets/
│   ├── loaders.py          # DatasetLoader class
│   ├── emoji.csv           # Dataset emoji (3,530 entries)
│   ├── slang.csv           # Dataset slang (15,675 entries)
│   ├── stop_word.csv       # Dataset stopwords (788 entries)
│   ├── wordlist.json       # Dataset wordlist
│   ├── kata_dasar_kbbi.csv # Dataset KBBI (28,527 entries)
│   └── kamus.txt           # Dataset kamus tambahan (30,871 entries)
├── preprocessing/
│   ├── cleaning/
│   │   └── text_cleaner.py # TextCleaner class
│   ├── linguistic/
│   │   ├── stemmer.py      # Stemmer class
│   │   └── stopwords.py    # StopwordRemover class
│   ├── normalization/
│   │   ├── emoji.py        # EmojiConverter class
│   │   └── spell_corrector.py # SpellCorrector class
│   ├── tokenization/
│   │   └── tokenizer.py    # Tokenizer class
│   └── utils.py            # Fungsi utility individual & Pipeline
└── demo.py                 # File demo penggunaan
```
````

````markdown
## 🆕 Changelog Versi 1.3.0

- 🚀 **[MAJOR]** Pipeline sekarang super simple - langsung pass functions sebagai arguments!
- ✅ **[PERBAIKAN]** Tidak ada lagi config dictionary yang kompleks
- ✅ **[PERBAIKAN]** Pipeline cuma 30 baris kode - clean dan to the point
- ✅ **[BARU]** Pipeline bisa dipanggil langsung seperti function: `pipeline("text")`
- ✅ **[BARU]** Helper function `pipeline()` untuk membuat Pipeline dengan mudah
- ✅ **[PERBAIKAN]** Fungsi `preprocess()` tetap ada untuk backward compatibility
- ✅ **[PERBAIKAN]** Documentation dan contoh yang lebih jelas dan praktis
- ✅ **[PERBAIKAN]** Nama fungsi diperbaiki: `replace_spell_corrector` (menggabungkan slang + koreksi ejaan)
- ✅ **[PERBAIKAN]** Nama fungsi diperbaiki: `replace_repeated_chars` (mengatasi word elongation)
- ✅ Menggabungkan spell correction dan slang normalization dalam `SpellCorrector`
- ✅ Semua dataset menggunakan file lokal (CSV/JSON)
- ✅ Struktur yang lebih terorganisir dengan pemisahan kelas dan fungsi
- ✅ Penambahan `DatasetLoader` untuk manajemen dataset terpusat
- ✅ Dataset lengkap dengan 6 file berbeda (emoji, slang, stopwords, wordlist, KBBI, kamus)
- ❌ Menghapus dependency pada external APIs atau downloads

## 🐛 Troubleshooting

**Error saat import dataset:**

```python
# Pastikan memanggil _load_data() untuk kelas yang memerlukan dataset
stopword = StopwordRemover()
stopword._load_data()  # Penting!
```
````

**Error Sastrawi tidak ditemukan:**

```bash
pip install Sastrawi
```

**Error pandas tidak ditemukan:**

```bash
pip install pandas
```

## 📄 License

MIT License

## 👨‍💻 Author

Raihan Hidayatullah Djunaedi [raihanhd.dev@gmail.com](mailto:raihanhd.dev@gmail.com)

---

Untuk contoh penggunaan lengkap, lihat file `demo.py` di repository ini.
