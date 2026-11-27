# Brave New World News Feed

A daily news briefing in Spanish, with a 1984-style look. It covers the UK, Spain and the world in 8 sections, with the 5 most important stories of the day in each. Every story is checked against other sources and gets a stamp that says how solid it is.

**▶ Open it:** https://dcalabuig7.github.io/Vibe%20Coding%20Projects/05-brave-new-world/

**Languages:** [Español](https://dcalabuig7.github.io/Vibe%20Coding%20Projects/05-brave-new-world/) · [English](https://dcalabuig7.github.io/Vibe%20Coding%20Projects/05-brave-new-world/en/) · [Português](https://dcalabuig7.github.io/Vibe%20Coding%20Projects/05-brave-new-world/pt/) · [中文](https://dcalabuig7.github.io/Vibe%20Coding%20Projects/05-brave-new-world/zh/)

## What it does

- **8 sections, 5 stories each:** UK, Spain, International, Economy and markets, Technology, Science and health, Culture, Sport.
- **A verification stamp on every story:**
  - **Verificado:** two or more independent sources, or an official one.
  - **Parcial:** the core is confirmed, some details are not.
  - **Fuente única:** only one source.
  - **Contradictorio:** the sources disagree.
- **Who said it:** each source has a one-line profile (country, owner, type) and, where one exists, its political leaning from AllSides or Media Bias Fact Check.
- **Short card, full file:** the main page shows a short summary. Open a story to see why it matters, a chart, key terms explained in plain words, key facts and all the sources.
- **"El día en 60 segundos":** the day in five sentences, with a "listen" button.
- **Search:** finds stories in today's edition. If a topic isn't there, it offers live searches on Google News, Bing, BBC and Reuters.
- **Blind spots:** flags stories where all the rated sources lean the same way.
- **"Mi lectura":** follow topics and see what you have read. This is saved only in your browser.
- **4 languages:** Spanish, English, Portuguese and Chinese. Pick one in the menu at the top right. The buttons and all 40 stories are translated, not machine translated on the fly.
- **iPhone widget:** live headlines by section on your home screen (see below).

## How to run it

- **In the browser:** open the link above. Nothing to install.
- **Offline:** download the repository and double-click `index.html`.

The chatbot ("Terminal de consulta") and the editions saved for other days only work when the page is opened inside Claude. Here, outside Claude, it shows the edition included in the page (6 November 2026). New daily editions are written in Spanish only; the translations cover this edition.

## Files

| File | What it is |
|------|------------|
| `index.html` | The whole newspaper in Spanish, in one page: layout, styles, code and today's stories. |
| `en/`, `pt/`, `zh/` | The same newspaper in English, Portuguese and Chinese. |
| `assets/logo.webp` | The logo. |
| `data/edition-2026-11-06.json` | The day's stories, with sources, stamps and charts. |
| `data/edition-2026-11-06-en.json` (and `-pt`, `-zh`) | The same stories, translated. |
| `tools/strings_es.json`, `tools/tr/*.tsv` | Every piece of story text in Spanish, and its translation into each language. |
| `tools/ui_i18n.py` | The translations of the buttons and labels. |
| `tools/build_i18n.py` | Builds the 4 language versions. |
| `tools/template.html` | The page without stories. The stories get poured into it. |
| `tools/*.py` | Python scripts that built the edition file. |
| `widget/BraveNewWorld-widget.js` | The iPhone widget for the Scriptable app. |

## How it works (the simple version)

Think of it as a **printing press**:

1. **The news (`data/*.json`)** is the ink. Each story is a small record: title, summary, stamp, sources, chart.
2. **The template (`tools/template.html`)** is the empty page with a hole marked `__SEED__`.
3. **Printing** pours the news into that hole. It does it four times, once per language, swapping the Spanish texts for their translations:

   ```
   python3 tools/build_i18n.py . data/edition-2026-11-06.json
   ```

   That writes `index.html` (Spanish) and `en/`, `pt/` and `zh/`.
4. **In the browser**, the page's JavaScript reads the stories and draws the cards, charts, filters and search.

## iPhone widget

1. Install **Scriptable** (free) from the App Store.
2. In Scriptable, tap **+**, paste the contents of `widget/BraveNewWorld-widget.js`, name it **Brave New World** and tap **Done**.
3. Add a large Scriptable widget to your home screen, long-press it, tap **Edit Widget** and choose the **Brave New World** script.
4. Optional: in **Parameter**, write a section (for example `Cultura`) to see only that section.

The widget shows live headlines from El País and the BBC. These headlines are **not** verified. Tap a headline to read it, or tap the edge of the widget to open a list of all 8 sections.

## What I learned

- How to keep **data apart from design**: the same template can print any day's edition.
- How to **verify information honestly**: never invent a source, and say clearly when something has only one source or the sources disagree.
- How to draw **simple charts** (bars, timelines, steps) with plain HTML and CSS.
- How to make a **sticky header**, live **search** and **filters** with JavaScript.
- How to make a page **readable on a phone** with media queries.
- How to build an **iPhone widget** with Scriptable that reads RSS feeds.
- How to make a site **multilingual**: keep every text in one place, translate it once, and build one page per language.
