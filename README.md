# 💬 Lex Bot 🇨🇭

A simple Streamlit front-end for accessing Swiss legal documents.

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://chatbot-template.streamlit.app/)

## How to run it on your own machine

Run the app

   ```
   $ poetry run streamlit run scripts/bot.py
   ```

## Development

### Localization

Creating `messages.pot` file

```bash
xgettext -o resources/messages.pot src/*.py
```

Merging 

```bash
msgmerge --update resources/locale/de/LC_MESSAGES/messages.po resources/messages.pot
msgmerge --update resources/locale/en/LC_MESSAGES/messages.po resources/messages.pot
msgmerge --update resources/locale/fr/LC_MESSAGES/messages.po resources/messages.pot
msgmerge --update resources/locale/it/LC_MESSAGES/messages.po resources/messages.pot
```

Compiling translations to `.mo` from `.po`:

```bash
msgfmt resources/locale/de/LC_MESSAGES/messages.po -o resources/locale/de/LC_MESSAGES/messages.mo
msgfmt resources/locale/en/LC_MESSAGES/messages.po -o resources/locale/en/LC_MESSAGES/messages.mo
msgfmt resources/locale/fr/LC_MESSAGES/messages.po -o resources/locale/fr/LC_MESSAGES/messages.mo
msgfmt resources/locale/it/LC_MESSAGES/messages.po -o resources/locale/it/LC_MESSAGES/messages.mo
```
