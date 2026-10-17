# Putting the new Astrabeam homepage into Squarespace

The design lives in this repo; Squarespace shows it through three Code Blocks plus
one native Form Block. Videos, images, styles and scripts load from
`https://tarunkumarnyu.github.io/astrabeam-site/`, so **don't delete or rename the
GitHub repo**.

Requires the **Core** plan or higher (code injection and JavaScript in code blocks).

## 1. Create a hidden page
1. **Pages** → **+** (next to "Not Linked") → **Blank Page**.
2. Name it `Home (new)`. In its settings, set the URL slug to `/home-new`.
3. Visitors can't reach it from the menu; you can preview it at `astrabeam.com/home-new`.

## 2. Page header code
1. Hover the page → ⚙ **Settings** → **Advanced** → **Page Header Code Injection**.
2. Paste all of `1-page-header-code-injection.html`. Save.

This loads the fonts, styles and scripts, hides Squarespace's own header/footer on
this page only, and styles the contact form.

## 3. Main content
1. Edit the page. Delete any placeholder blocks.
2. **Add Section** → blank section. In the section's ✎ **Format**: smallest height,
   full content width.
3. **Add Block** → **Code**. Set the mode to **HTML**. Paste all of
   `2-code-block-main.html`.
4. Stretch the code block across the **full width** of the section grid.
   Leave "Display Source" off.

## 4. Contact section
1. Add another blank section below.
2. Left half: a **Code** block (HTML) with `3-code-block-contact.html`.
3. Right half: a **Form** block. Fields, in order:
   - **Name** (required)
   - **Email** labeled *Work email* (required)
   - **Text** labeled *Company*
   - **Dropdown** labeled *Industry*: Drones & UAVs, Search & Rescue, Mining,
     Agriculture, Defense, Research, Other
   - **Text area** labeled *What are you building?* (required)
4. Form → **Storage** → **Email**: `info@astrabeam.com`.
5. **Post-submit message**: *Thanks, we'll be in touch soon.*
6. Button label: **Send**.

## 5. Footer
Add a last blank section with a **Code** block (HTML): `4-code-block-footer.html`.

## 6. Privacy page
Create another page under Not Linked with the slug `/privacy` and paste the text of
`5-privacy-page.txt` into a normal Text block. (The footer links to `/privacy`.)

## 7. Check before going live
- Preview `astrabeam.com/home-new` on desktop and on a phone.
- If anything looks off (spacing, a Squarespace style leaking in), send a screenshot:
  fixes go into the header code, nothing else changes.
- Confirm permissions: the four testimonial companies, the executive advisors, and
  team members whose photos appear.

## 8. Go live
1. Pages → hover **Home (new)** → ⚙ → **Set as Homepage**, and drag it into the main
   navigation if your theme needs it there.
2. Move the old homepage to **Not Linked** as a backup. Switching back is the same
   step in reverse.

## Updating later
- Text or layout changed → in the repo run `python3 tools/build_squarespace_kit.py`,
  then re-paste `2-code-block-main.html` (and 3/4 if they changed).
- Styles or scripts changed → run `python3 tools/version_assets.py`, rebuild the kit,
  push to GitHub, then re-paste `1-page-header-code-injection.html` (its version
  numbers make browsers fetch the new files).
- New video or images → push them to GitHub; they're live in about 10 minutes.
