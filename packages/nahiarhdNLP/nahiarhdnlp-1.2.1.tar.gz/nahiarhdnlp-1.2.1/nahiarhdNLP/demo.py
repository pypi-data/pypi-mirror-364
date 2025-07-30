from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from nahiarhdNLP.preprocessing import (
    EmojiConverter,
    Pipeline,
    SpellCorrector,
    Stemmer,
    StopwordRemover,
    TextCleaner,
    Tokenizer,
    correct_spelling,
    emoji_to_words,
    pipeline,
    preprocess,
    remove_extra_spaces,
    remove_hashtags,
    remove_html,
    remove_mentions,
    remove_numbers,
    remove_punctuation,
    remove_special_chars,
    remove_stopwords,
    remove_url,
    remove_whitespace,
    replace_slang,
    replace_word_elongation,
    stem_text,
    to_lowercase,
    tokenize,
    words_to_emoji,
)


def demo_functions(console):
    console.print(Panel.fit("[bold blue]Demo Fungsi Utility[/bold blue]", style="blue"))
    tests = [
        ("remove_html", "website <a href='https://google.com'>google</a>", remove_html),
        ("remove_url", "kunjungi https://google.com sekarang!", remove_url),
        ("remove_mentions", "Halo @user123 apa kabar?", remove_mentions),
        ("remove_hashtags", "Hari ini #senin #libur #weekend", remove_hashtags),
        ("remove_numbers", "Saya berumur 25 tahun dan punya 3 anak", remove_numbers),
        (
            "remove_punctuation",
            "Halo, apa kabar?! Semoga sehat selalu...",
            remove_punctuation,
        ),
        ("remove_extra_spaces", "Halo    dunia   yang    indah", remove_extra_spaces),
        ("remove_special_chars", "Halo @#$%^&*() dunia!!!", remove_special_chars),
        ("remove_whitespace", "Halo\n\tdunia\r\nyang indah", remove_whitespace),
        ("to_lowercase", "HALO Dunia Yang INDAH", to_lowercase),
        ("replace_word_elongation", "kenapaaa???", replace_word_elongation),
        ("replace_slang", "emg siapa yg nanya?", replace_slang),
        ("remove_stopwords", "siapa yang suruh makan?!!", remove_stopwords),
        ("emoji_to_words", "emoji 😀😁", emoji_to_words),
        ("words_to_emoji", "emoji wajah_gembira", words_to_emoji),
        ("correct_spelling", "sya suka mkn nasi", correct_spelling),
        ("stem_text", "bermain-main dengan senang", stem_text),
        ("tokenize", "Saya suka makan nasi", lambda t: str(tokenize(t))),
    ]
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Fungsi")
    table.add_column("Input")
    table.add_column("Output")
    for name, text, func in tests:
        try:
            output = func(text)
        except Exception as e:
            output = f"[red]Error: {e}[/red]"
        table.add_row(name, text, str(output))
    console.print(table)


def demo_class(console):
    console.print(
        Panel.fit(
            "[bold yellow]Demo Class-based (TextCleaner, StopwordRemover, EmojiConverter, SpellCorrector, Stemmer, Tokenizer)[/bold yellow]",
            style="yellow",
        )
    )
    # TextCleaner
    cleaner = TextCleaner()
    url_text = "kunjungi https://google.com sekarang!"
    mention_text = "Halo @user123 apa kabar?"
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Class")
    table.add_column("Fitur")
    table.add_column("Input")
    table.add_column("Output")
    table.add_row("TextCleaner", "clean_urls", url_text, cleaner.clean_urls(url_text))
    table.add_row(
        "TextCleaner",
        "clean_mentions",
        mention_text,
        cleaner.clean_mentions(mention_text),
    )
    # StopwordRemover
    stopword = StopwordRemover()
    stopword._load_data()
    text = "saya suka makan nasi goreng"
    table.add_row(
        "StopwordRemover", "remove_stopwords", text, stopword.remove_stopwords(text)
    )
    # EmojiConverter
    emoji = EmojiConverter()
    emoji._load_data()
    emoji_text = "😀 😂 😍"
    table.add_row(
        "EmojiConverter",
        "emoji_to_text_convert",
        emoji_text,
        emoji.emoji_to_text_convert(emoji_text),
    )
    text3 = "wajah_gembira"
    table.add_row(
        "EmojiConverter",
        "text_to_emoji_convert",
        text3,
        emoji.text_to_emoji_convert(text3),
    )
    # SpellCorrector (now handles both spell correction and slang normalization)
    try:
        spell = SpellCorrector()
        spell_text = "sya suka mkn nasi"
        table.add_row(
            "SpellCorrector",
            "correct_sentence",
            spell_text,
            spell.correct_sentence(spell_text),
        )
        # Test slang normalization capability
        slang_text = "gw lg di rmh"
        table.add_row(
            "SpellCorrector",
            "slang_normalization",
            slang_text,
            spell.correct_sentence(slang_text),
        )
    except Exception as e:
        table.add_row(
            "SpellCorrector", "correct_sentence", "-", f"[red]Error: {e}[/red]"
        )
    # Stemmer
    try:
        stemmer = Stemmer()
        stem_text_in = "bermain-main dengan senang"
        table.add_row("Stemmer", "stem", stem_text_in, stemmer.stem(stem_text_in))
    except Exception as e:
        table.add_row("Stemmer", "stem", "-", f"[red]Error: {e}[/red]")
    # Tokenizer
    tokenizer = Tokenizer()
    token_text = "Saya suka makan nasi"
    table.add_row(
        "Tokenizer", "tokenize", token_text, str(tokenizer.tokenize(token_text))
    )
    console.print(table)


def demo_pipeline(console):
    """Demo fitur Pipeline untuk preprocessing sekaligus."""
    console.print(
        Panel.fit(
            "[bold green]🔀 Demo Pipeline - Preprocessing Sekaligus[/bold green]",
            style="green",
        )
    )

    # Sample messy text untuk testing
    messy_text = "Halooo @user123 #trending https://example.com gw lg nyari info pnting 😀!!! 123"

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Metode")
    table.add_column("Konfigurasi/Parameter")
    table.add_column("Input")
    table.add_column("Output")

    # 1. Demo Kelas Pipeline - Default Config
    try:
        pipe_default = Pipeline()
        result1 = pipe_default.process(messy_text)
        table.add_row(
            "Pipeline (default)",
            "Konfigurasi default",
            messy_text[:50] + "...",
            str(result1),
        )
    except Exception as e:
        table.add_row(
            "Pipeline (default)",
            "Konfigurasi default",
            messy_text[:50] + "...",
            f"[red]Error: {e}[/red]",
        )

    # 2. Demo Kelas Pipeline - Custom Config
    try:
        custom_config = {
            "remove_url": True,
            "remove_mentions": True,
            "remove_hashtags": True,
            "remove_numbers": True,
            "normalize_slang": True,
            "correct_spelling": True,
            "to_lowercase": True,
            "remove_punctuation": True,
        }
        pipe_custom = Pipeline(custom_config)
        result2 = pipe_custom.process(messy_text)
        table.add_row(
            "Pipeline (custom)",
            "URL, mentions, hashtags, numbers, slang, spelling, lowercase, punctuation",
            messy_text[:50] + "...",
            str(result2),
        )
    except Exception as e:
        table.add_row(
            "Pipeline (custom)",
            "Custom config",
            messy_text[:50] + "...",
            f"[red]Error: {e}[/red]",
        )

    # 3. Demo Pipeline dengan tokenisasi
    try:
        tokenize_config = {
            "remove_url": True,
            "remove_mentions": True,
            "normalize_slang": True,
            "to_lowercase": True,
            "tokenize": True,
        }
        pipe_token = Pipeline(tokenize_config)
        result3 = pipe_token.process("gw suka makan nasi @user")
        table.add_row(
            "Pipeline (tokenize)",
            "URL, mentions, slang, lowercase + tokenize",
            "gw suka makan nasi @user",
            str(result3),
        )
    except Exception as e:
        table.add_row(
            "Pipeline (tokenize)",
            "With tokenization",
            "gw suka makan nasi @user",
            f"[red]Error: {e}[/red]",
        )

    # 4. Demo fungsi pipeline()
    try:
        simple_config = {
            "remove_url": True,
            "normalize_slang": True,
            "to_lowercase": True,
        }
        result4 = pipeline("Gw lg browsing https://google.com", simple_config)
        table.add_row(
            "pipeline() function",
            "URL, slang, lowercase",
            "Gw lg browsing https://google.com",
            str(result4),
        )
    except Exception as e:
        table.add_row(
            "pipeline() function",
            "Simple config",
            "Gw lg browsing https://google.com",
            f"[red]Error: {e}[/red]",
        )

    # 5. Demo fungsi preprocess()
    try:
        result5 = preprocess(
            "Halooo @user!!! 123",
            remove_mentions=True,
            remove_numbers=True,
            remove_punctuation=True,
            replace_word_elongation=True,
            to_lowercase=True,
            normalize_slang=False,
            correct_spelling=False,
        )
        table.add_row(
            "preprocess() function",
            "mentions, numbers, punctuation, elongation, lowercase",
            "Halooo @user!!! 123",
            str(result5),
        )
    except Exception as e:
        table.add_row(
            "preprocess() function",
            "Explicit parameters",
            "Halooo @user!!! 123",
            f"[red]Error: {e}[/red]",
        )

    console.print(table)

    # Demo advanced pipeline features
    console.print("\n[bold cyan]🔧 Advanced Pipeline Features:[/bold cyan]")

    try:
        pipe_advanced = Pipeline()

        # Show current config
        config_table = Table(show_header=True, header_style="bold cyan")
        config_table.add_column("Feature")
        config_table.add_column("Status")

        config_table.add_row(
            "Current Config", str(len(pipe_advanced.get_config())) + " options"
        )
        config_table.add_row(
            "Enabled Steps", str(len(pipe_advanced.get_enabled_steps())) + " steps"
        )
        config_table.add_row(
            "Available Steps", str(pipe_advanced.get_enabled_steps()[:5]) + "..."
        )

        # Update config demonstration
        pipe_advanced.update_config({"tokenize": True, "remove_stopwords": True})
        config_table.add_row("After Update", "tokenize & remove_stopwords enabled")

        console.print(config_table)

    except Exception as e:
        console.print(f"[red]Error in advanced features: {e}[/red]")


def main():
    console = Console()
    console.print(
        Text("🇮🇩 [bold blue]nahiarhdNLP Demo Lengkap[/bold blue]", style="bold blue")
    )
    console.print(Text("Demonstrasi SEMUA Fungsi & Class Library", style="italic"))
    console.print("=" * 80)
    demo_functions(console)
    console.print("\n" + "=" * 80)
    demo_class(console)
    console.print("\n" + "=" * 80)
    demo_pipeline(console)
    console.print("\n" + "=" * 80)
    console.print(
        Panel.fit(
            "[bold green]🎉 Selesai! Semua fitur utama sudah didemokan.\n"
            "Termasuk fitur BARU: Pipeline untuk preprocessing sekaligus![/bold green]",
            style="bold green",
        )
    )


if __name__ == "__main__":
    main()
