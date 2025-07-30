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
    replace_slang, replace_word_elongation, correct_spelling,
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
    replace_slang, replace_word_elongation, correct_spelling,
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
# Output: "kunjungi sekarang!"

# Menghapus mentions (@username)
mention_text = "Halo @user123 dan @admin apa kabar?"
clean_result = remove_mentions(mention_text)
print(clean_result)
# Output: "Halo dan apa kabar?"

# Menghapus hashtags (#tag)
hashtag_text = "Hari ini #senin #libur #weekend"
clean_result = remove_hashtags(hashtag_text)
print(clean_result)
# Output: "Hari ini"

# ✨ FUNGSI NORMALISASI DAN KOREKSI

# Normalisasi slang (menggunakan SpellCorrector)
slang_text = "emg siapa yg nanya?"
normal_text = replace_slang(slang_text)
print(normal_text)
# Output: "memang siapa yang bertanya?"

# Mengatasi perpanjangan kata (word elongation)
elongation_text = "kenapaaa bangettt???"
clean_result = replace_word_elongation(elongation_text)
print(clean_result)
# Output: "kenapa banget??"

# Koreksi ejaan
spell_text = "saya mencri informsi pnting"
corrected = correct_spelling(spell_text)
print(corrected)
# Output: "saya mencuri informasi penting"

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
# Output: "suka makan nasi goreng"

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

Pipeline memungkinkan Anda menjalankan beberapa fungsi preprocessing sekaligus dengan konfigurasi yang fleksibel.

```python
from nahiarhdNLP.preprocessing import Pipeline, pipeline, preprocess

# 🏗️ MENGGUNAKAN KELAS PIPELINE

# Buat pipeline dengan konfigurasi default
pipe = Pipeline()
result = pipe.process("Halooo @user https://example.com gw lg nyari info 😀")
print(result)

# Buat pipeline dengan konfigurasi custom
config = {
    'remove_html': True,
    'remove_url': True,
    'remove_mentions': True,
    'remove_hashtags': True,
    'normalize_slang': True,
    'correct_spelling': True,
    'remove_stopwords': True,
    'stem_text': False,
    'to_lowercase': True,
    'tokenize': False
}

pipe = Pipeline(config)
messy_text = "gw lg mencri informsi pnting @user #trending https://example.com"
result = pipe.process(messy_text)
print(result)

# Update konfigurasi pipeline
pipe.update_config({'tokenize': True, 'remove_stopwords': False})
tokens = pipe.process("Saya suka makan nasi goreng")
print(tokens)

# Lihat konfigurasi aktif
print("Konfigurasi:", pipe.get_config())
print("Steps aktif:", pipe.get_enabled_steps())

# Reset ke konfigurasi default
pipe.reset_config()

# 🚀 FUNGSI PIPELINE (SIMPLE)

# Gunakan konfigurasi default
result = pipeline("Halooo @user https://example.com gw lg nyari info 😀")
print(result)

# Gunakan konfigurasi custom
config = {
    'remove_url': True,
    'normalize_slang': True,
    'to_lowercase': True,
    'remove_mentions': True
}
result = pipeline("Gw lg browsing https://google.com @admin", config)
print(result)

# Dengan tokenisasi
config = {'normalize_slang': True, 'tokenize': True}
tokens = pipeline("gw suka makan nasi", config)
print(tokens)

# ⚙️ FUNGSI PREPROCESS (DETAIL CONTROL)

# Preprocess dengan parameter eksplisit
result = preprocess(
    "Halooo @user123 #trending https://example.com gw lg nyari info 😀!!!",
    remove_url=True,
    remove_mentions=True,
    remove_hashtags=True,
    remove_punctuation=True,
    normalize_slang=True,
    correct_spelling=True,
    to_lowercase=True,
    remove_stopwords=True
)
print(result)

# Preprocess dengan tokenisasi
tokens = preprocess(
    "Saya suka makan nasi goreng pedas",
    remove_stopwords=True,
    tokenize=True
)
print(tokens)

# Preprocess minimal (hanya cleaning dasar)
result = preprocess(
    "Halooo @user!!! 123",
    remove_mentions=True,
    remove_numbers=True,
    remove_punctuation=True,
    replace_word_elongation=True,
    to_lowercase=True,
    # Nonaktifkan normalisasi advanced
    normalize_slang=False,
    correct_spelling=False,
    remove_stopwords=False
)
print(result)
```

#### 📋 Konfigurasi Pipeline Available

```python
# Semua opsi konfigurasi yang tersedia
available_options = {
    # Basic cleaning
    'remove_html': True,           # Hapus HTML tags
    'remove_url': True,            # Hapus URL
    'remove_mentions': True,       # Hapus @mentions
    'remove_hashtags': True,       # Hapus #hashtags
    'remove_numbers': False,       # Hapus angka
    'remove_punctuation': False,   # Hapus tanda baca
    'remove_special_chars': True,  # Hapus karakter khusus
    'remove_whitespace': True,     # Hapus whitespace berlebih
    'remove_extra_spaces': True,   # Hapus spasi berlebih

    # Text normalization
    'to_lowercase': True,          # Ubah ke huruf kecil
    'replace_word_elongation': True, # Normalisasi kata berulang (halooo -> halo)
    'normalize_slang': True,       # Normalisasi slang (gw -> saya)
    'correct_spelling': True,      # Koreksi ejaan

    # Emoji handling
    'emoji_to_words': False,       # Ubah emoji ke kata
    'words_to_emoji': False,       # Ubah kata ke emoji

    # Linguistic processing
    'remove_stopwords': False,     # Hapus stopwords
    'stem_text': False,           # Lakukan stemming

    # Tokenization
    'tokenize': False,            # Tokenisasi (return list)
}
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

1. **Untuk preprocessing sekaligus**: Gunakan `Pipeline`, `pipeline()`, atau `preprocess()`
2. **Untuk kontrol penuh**: Gunakan kelas individual (`TextCleaner`, `SpellCorrector`, dll)
3. **Untuk spell correction + slang**: Gunakan `SpellCorrector` yang menggabungkan kedua fitur
4. **Untuk stemming**: Install Sastrawi terlebih dahulu: `pip install Sastrawi`
5. **Untuk load dataset**: Gunakan `DatasetLoader` dari `nahiarhdNLP.datasets`
6. **Untuk inisialisasi kelas**: Panggil `_load_data()` untuk kelas yang memerlukan dataset
7. **Untuk kustomisasi pipeline**: Gunakan kelas `Pipeline` dengan konfigurasi dictionary
8. **Untuk penggunaan sederhana**: Gunakan fungsi `pipeline()` atau `preprocess()`

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

```
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
│   └── utils.py            # Fungsi utility individual
└── demo.py                 # File demo penggunaan
```

## 🆕 Changelog Versi 1.2.0

- ✅ **[BARU]** Penambahan fitur **Pipeline** untuk preprocessing sekaligus
- ✅ **[BARU]** Kelas `Pipeline` dengan konfigurasi fleksibel
- ✅ **[BARU]** Fungsi `pipeline()` untuk penggunaan sederhana
- ✅ **[BARU]** Fungsi `preprocess()` dengan parameter eksplisit
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

Raihan Hidayatullah Djunaedi (raihanhd.dev@gmail.com)

---

Untuk contoh penggunaan lengkap, lihat file `demo.py` di repository ini.
