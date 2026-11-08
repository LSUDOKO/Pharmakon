# Presenter shots for the Pharmakon film

Five short pieces to camera, about 1.5 minutes in total. In four of them your voice replaces narrator lines, so the film grows only by the intro (about 12 s, ending near 8:35).
The narrator still carries the explanation over the graphics. You carry the moments that need a person: who built this, why it matters, the honest result, and the limits.

| # | Where in the film | Replaces narrator line | Look on screen | Length |
|---|---|---|---|---|
| P1 | Right after the torn-paper title, before "Meet Eleni" | nothing (new) | full frame + name lower third | ~12 s |
| P2 | Motivation scene ("This matters…") | s04_a + first sentence of s05_a | full frame, then shrinks into a corner circle as the pipeline graphic builds | ~22 s |
| P3 | Start of the live demo | s08_a "Here is Eleni using it." | full frame, torn-paper wipe into the browser | ~5 s |
| P4 | Results: the time-machine result | s10_e | full frame, the backtest chart beside you | ~22 s |
| P5 | Limits and next steps | s11_b + s11_c | full frame, ends on a torn-paper wipe into the closing Eleni line | ~30 s |

Read the lines at a calm pace. Small rewording is fine, but keep every number and the safety sentence exactly as written. The film's captions are made from what you actually say.

---

## P1 — Intro (new, after the title)

> Hi, I'm [your name], [one line: e.g. "a developer from …" / "and this is our team, …"].
> Before I show you what we built, let me introduce someone it's for.

The film then cuts to "Meet Eleni…".

## P2 — Why it matters (replaces s04_a, opens s05_a)

> Why does this matter? Plants have given medicine some of its most important drugs, and the Greek tradition is one of the best documented anywhere.
> Yet almost none of it has ever become a hypothesis anyone can actually test.
> So we built Pharmakon.

The narrator continues: "It reads the Greek, works out which plant each name means…"

## P3 — Into the demo (replaces s08_a)

> Let me show you. Here's Eleni using it.

## P4 — The honest result (replaces s10_e)

> Now the result we didn't expect. We asked: does two thousand years of history predict what science studies next?
> It doesn't. Research popularity does. And in two thousand and five, adding history even made the ranking worse.
> We report that exactly as we would report a success.

## P5 — Limits and what's next (replaces s11_b and s11_c)

> We're clear about the limits. Expert judgement is not ground truth. A search hit is only a proxy for evidence. And our audits still need human experts.
> Everything here is a research hypothesis, never medical advice.
> Next: expert audits, richer plant descriptions, more Byzantine authors, and a lab partner to test the top leads.
> If that's you, we'd love to hear from you.

The narrator closes the film: "Eleni started with six hundred names…"

---

## How to record

- **Framing:** landscape 16:9, 1080p or 4K, 30 fps. Camera at eye level, about an arm and a half away, head and shoulders. Leave a little space on one side; P2 and P4 put graphics beside you.
- **Background:** dark and plain (a dark wall or curtain, a few metres behind you). The film is black and deep green, so a bright or busy room will jump out.
- **Light:** one soft light (a window or lamp through a sheet) at 45° in front of you. No light behind you, and no overhead light alone.
- **Clothes:** solid dark or muted colours. No white, no fine stripes, no logos.
- **Sound:** this matters most. Use a lavalier or your phone's mic about 20 cm from your mouth, in a quiet room with soft furnishings and fans off. Record a separate phone voice memo as a backup if you can.
- **Delivery:** look into the lens, not at the screen. Stay silent for 2 s before you speak and 2 s after you finish. Do 2–3 takes of each piece and keep the best.
- **Files:** name them `P1.mp4` … `P5.mp4` (take numbers are fine: `P4_take2.mp4`) and put them in `video/film/public/presenter/`.

## What happens after you record

1. The best take is trimmed and the audio cleaned: noise reduction, levels matched to the narrator, and the same −14 LUFS master.
2. Your video gets a light grade toward the film's deep green and black, with a little grain, so it sits inside the brand rather than looking like a webcam.
3. Captions come from your real words (whisper word timing) in the same style as the rest of the film.
4. Each shot gets a torn-paper wipe in and out and a lower third in Outfit (name and role in P1, short labels after that).
5. The timing is regenerated so music ducking and cuts follow your takes, the film is re-rendered, and the `.srt` file and thumbnail are updated.

---

## As built (8 Nov 2026)

- **Takes used:** `video/film/public/presenter/p1–p5.mp4`, 854×480 phone footage. They are cut and cleaned by `video/make_presenter.py`, which writes `video/vo/presenter.json`; `make_timing.py` merges that file.
- **Audio:** each take is cleaned with a high-pass filter, FFT denoise, a gentle gate, compression, de-essing and a limiter. It is then levelled to the narrator at −18.8 LUFS. The noise floor between phrases falls from about −58 dB to about −70 dB.
- **Picture:** the footage is shown as a graded card rather than full frame, because it is phone video in a bright room. The card is cropped to the face, pulled toward black and verdigris, grained, and drawn in with a verdigris rule.
  - P1 and P3 are their own short scenes, with kinetic type on the left and the card on the right.
  - In P2, P4 and P5 the narrated scene shrinks to a screen on the left while the card stands on the right. The scene keeps animating, cued to Arpit's real word timing from whisper.
- **Changes from the plan:**
  - P2 ends before "so we built Pharmakon", because the narrator says that line.
  - P3 uses only "Let me show you." The narrator's "Here is Eleni using it" is kept, so the demo's frame-exact edit is unchanged.
- **Captions:** they follow Arpit's actual words, with mis-hearings corrected (Arpit, Hamirpur, tradition, predict, descriptions).
- **Outro credit:** "Built by Arpit · B.Tech Computer Science, NIT Hamirpur".
