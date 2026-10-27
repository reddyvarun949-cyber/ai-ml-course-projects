"""Generate the synthetic product review dataset used in this project.

Run from the project root:  python data/generate_data.py
The output is data/product_reviews.csv. The seed is fixed, so everyone gets the same file.

How a review is made:
  1. pick a product category, a product and a TRUE sentiment (positive / neutral / negative),
  2. build the text from small phrase pools: opinions about the product's aspects (battery, fabric, taste ...),
     general opinions, negations ("not bad", "not worth it"), mixed reviews ("great screen but ..."),
     occasional sarcasm, Hinglish words, emojis and typos,
  3. pick a star rating that USUALLY agrees with the sentiment (people are not always consistent),
  4. add messiness: a few wrong labels (annotator mistakes), empty reviews and duplicate rows.

Nothing here is real customer data; it is invented for teaching.
"""
import os

import numpy as np
import pandas as pd

SEED = 42
N = 4000

# ---------------------------------------------------------------------------
# Phrase pools per category: products, positive aspects, negative aspects
# ---------------------------------------------------------------------------
CATEGORIES = {
    "electronics": {
        "products": ["phone", "earphones", "laptop", "smartwatch", "power bank", "bluetooth speaker", "charger",
                     "tablet", "headphones", "keyboard"],
        "pos": ["the battery lasts all day", "the screen is bright and sharp", "sound quality is excellent",
                "it charges really fast", "build quality feels premium", "setup took two minutes",
                "the camera takes lovely photos", "connects instantly to my phone", "bass is deep and clear",
                "very light and easy to carry", "the display is crisp", "keys feel nice to type on"],
        "neg": ["the battery dies fast", "the screen has dead pixels", "it heats up a lot", "stopped working after a week",
                "the sound crackles at high volume", "the charging port is loose", "bluetooth keeps disconnecting",
                "the camera is blurry", "it hangs every few minutes", "the cable broke in a month",
                "it takes forever to charge", "left earbud stopped working"],
        "neu_aspect": ["battery backup is average", "sound is fine for calls", "the screen is okay indoors",
                       "it charges at a normal speed", "build quality is plastic but fine"],
    },
    "clothing": {
        "products": ["t-shirt", "jeans", "kurta", "jacket", "saree", "shoes", "dress", "hoodie", "track pants", "shirt"],
        "pos": ["the fabric is soft and comfortable", "it fits perfectly", "the colour is exactly as shown",
                "the stitching is neat", "very comfortable to wear all day", "looks stylish",
                "the material feels premium", "got many compliments", "the size chart was accurate",
                "keeps me warm"],
        "neg": ["the size runs too small", "the colour faded after the first wash", "the fabric feels cheap",
                "the stitching came off", "it looks very different from the picture", "it shrank after one wash",
                "the zip broke on day one", "the sole came off", "it is too tight around the shoulders",
                "there was a hole in it"],
        "neu_aspect": ["the fabric is a bit thin", "the fit is slightly loose", "the colour is a little darker",
                       "the size is as per the chart", "material is average"],
    },
    "home": {
        "products": ["mixer grinder", "pressure cooker", "bedsheet", "curtains", "water bottle", "non-stick pan",
                     "table lamp", "storage box", "ceiling fan", "iron"],
        "pos": ["it works perfectly in my kitchen", "it is easy to clean", "it looks elegant in the living room",
                "sturdy and well made", "the motor is powerful", "keeps water cold for hours",
                "heats up quickly", "very silent while running", "the finish is beautiful", "saves a lot of time"],
        "neg": ["the coating started peeling", "the lid does not fit properly", "the motor makes a loud noise",
                "it arrived broken", "it leaks from the bottom", "the handle got loose", "it stopped heating",
                "the colour bled onto other clothes", "it rusted within a month", "smells of burning plastic"],
        "neu_aspect": ["it is a bit heavy", "the motor is slightly noisy", "the size is smaller than I thought",
                       "it takes some time to heat", "the finish is simple"],
    },
    "beauty": {
        "products": ["face wash", "moisturiser", "shampoo", "lipstick", "sunscreen", "perfume", "hair oil",
                     "body lotion", "kajal", "face serum"],
        "pos": ["my skin feels soft", "the fragrance lasts long", "no breakouts at all", "my hair feels smooth",
                "the shade is lovely", "it absorbs quickly", "my skin looks brighter", "it is gentle on skin",
                "reduced my hair fall", "the texture is light"],
        "neg": ["it caused itching and rashes", "the smell is too strong", "it made my skin oily",
                "it dried out my hair", "the seal was broken", "it gave me pimples", "the shade looks nothing like the photo",
                "it burns my eyes", "the fragrance fades in minutes", "it felt sticky"],
        "neu_aspect": ["the smell is mild", "it is a bit sticky", "the shade is slightly different",
                       "results take time", "the quantity is small"],
    },
    "grocery": {
        "products": ["basmati rice", "green tea", "peanut butter", "honey", "almonds", "coffee", "atta", "olive oil",
                     "masala", "dark chocolate"],
        "pos": ["it tastes fresh", "good quality grains", "great aroma", "it was well packed", "tastes just like homemade",
                "the almonds are big and crunchy", "rich flavour", "the expiry date was far away", "very pure taste",
                "my kids love it"],
        "neg": ["it tasted stale", "there were insects in it", "I received an expired product", "the packet was torn",
                "the taste is very bland", "it smells rancid", "the jar was leaking", "too much sugar added",
                "lumps everywhere", "half the packet was broken pieces"],
        "neu_aspect": ["the taste is mild", "the packet is smaller than expected", "the aroma is light",
                       "the grains are medium sized", "it is slightly sweet"],
    },
}

# ---------------------------------------------------------------------------
# General phrases that are not tied to a category
# ---------------------------------------------------------------------------
POS_GENERAL = ["Totally worth the money.", "Highly recommend it.", "Very happy with this purchase.",
               "Excellent product.", "Love it!", "Exceeded my expectations.", "Value for money.",
               "Delivery was super quick.", "Best purchase this year.", "Would buy again.", "Great quality.",
               "Superb!", "Amazing product.", "Perfect gift for my mother.", "Five stars from me.",
               "Really good.", "Awesome.", "Very good product, satisfied."]
POS_NEGATED = ["Not bad at all.", "No complaints so far.", "Can't complain for this price.", "Never had any issue.",
               "Not disappointed.", "Didn't expect it to be this good.", "Nothing to complain about.",
               "Not a single problem in three months."]
NEG_GENERAL = ["Waste of money.", "Very disappointed.", "Do not buy.", "Worst purchase ever.", "Returning it.",
               "Poor quality.", "Terrible.", "Complete waste.", "Customer care did not help at all.",
               "Regret buying this.", "Horrible experience.", "Cheap quality.", "Pathetic product.",
               "Avoid this seller."]
NEG_NEGATED = ["Not worth it.", "Not good.", "Not happy with the quality.", "Would not recommend.",
               "Doesn't work as described.", "Not as described.", "Not worth the price.", "Never buying again.",
               "Don't waste your money.", "Not what I ordered."]
NEU_GENERAL = ["It's okay.", "Average product.", "Does the job.", "Nothing special.", "As expected.",
               "Decent for the price.", "Okay okay product.", "Neither good nor bad.", "Fine for basic use.",
               "Not great, not terrible.", "Received the item.", "It is what it is.", "Packaging was standard.",
               "Could be better.", "Works, but nothing to write home about.", "Fair enough for the price.",
               "Mixed feelings about this one.", "Satisfactory.", "Just average."]
SARCASM = ["Wow, stopped working in two days. Amazing quality {e}", "Great, just great. Another broken {p}.",
           "Loved waiting three weeks for a damaged box.", "Brilliant, the {p} died the day the return window closed.",
           "Fantastic, exactly what I wanted... a {p} that does not turn on.",
           "Oh sure, 'premium quality'. Fell apart in a week."]
HINGLISH = {
    "positive": ["Bahut accha product.", "Paisa vasool!", "Ekdum mast.", "Zabardast quality.", "Bahut badhiya."],
    "negative": ["Bekaar product.", "Bakwas quality.", "Paisa barbaad.", "Bilkul ghatiya.", "Bekaar hai, mat lena."],
    "neutral": ["Theek hai.", "Chalega.", "Thik thak hai.", "Theek thaak hai, kuch khaas nahi."],
}
EMOJIS = {"positive": ["😍", "👍", "😊", "❤️", "🔥"], "negative": ["😡", "👎", "😞", "🤬", "💔"],
          "neutral": ["😐", "🤷", "🙂"]}
CONNECT = [" but ", ", but ", " however ", ". Only issue is ", " although "]


def add_typos(text, rng, rate=0.06):
    """Swap two neighbouring letters or drop a letter in a few words (people type fast on phones)."""
    words = text.split(" ")
    for i, w in enumerate(words):
        if len(w) > 3 and w.isalpha() and rng.random() < rate:
            j = rng.integers(1, len(w) - 1)
            if rng.random() < 0.5:
                w = w[:j - 1] + w[j] + w[j - 1] + w[j + 1:]       # swap
            else:
                w = w[:j] + w[j + 1:]                             # drop
            words[i] = w
    return " ".join(words)


def cap(s):
    return s[0].upper() + s[1:] if s else s


def make_review(sentiment, cat, rng):
    """Build one review text for the given TRUE sentiment and category."""
    info = CATEGORIES[cat]
    product = rng.choice(info["products"])
    pick = lambda pool: pool[rng.integers(len(pool))]  # noqa: E731
    parts = []
    r = rng.random()

    if sentiment == "positive":
        if r < 0.03:                                  # Hinglish-only
            parts = [pick(HINGLISH["positive"])]
        elif r < 0.55:                                # aspect + general
            parts = [cap(pick(info["pos"])) + ".", pick(POS_GENERAL)]
            if rng.random() < 0.35:
                extra = cap(pick(info["pos"])) + "."
                if extra != parts[0]:                 # avoid saying the same thing twice
                    parts.insert(1, extra)
        elif r < 0.72:                                # negated positive: "not bad", "no complaints"
            parts = [pick(POS_NEGATED), cap(pick(info["pos"])) + "."]
        elif r < 0.80:                                # mostly positive with a small complaint
            parts = [cap(pick(info["pos"])) + pick(CONNECT) + pick(info["neu_aspect"]) + ".", pick(POS_GENERAL)]
        elif r < 0.88:                                # mixed, but the writer is happy overall (hard case)
            parts = [cap(pick(info["neg"])) + pick(CONNECT) + pick(info["pos"]) + "."]
            if rng.random() < 0.5:
                parts.append(pick(NEU_GENERAL + POS_NEGATED))
        else:                                         # short
            parts = [pick(POS_GENERAL) if rng.random() < 0.6 else f"Good {product}."]
    elif sentiment == "negative":
        if r < 0.03:
            parts = [pick(HINGLISH["negative"])]
        elif r < 0.07:                                # sarcasm: positive words, negative meaning
            parts = [pick(SARCASM).format(p=product, e="🙄")]
        elif r < 0.52:
            parts = [cap(pick(info["neg"])) + ".", pick(NEG_GENERAL)]
            if rng.random() < 0.3:
                extra = cap(pick(info["neg"])) + "."
                if extra != parts[0]:                 # avoid saying the same thing twice
                    parts.insert(1, extra)
        elif r < 0.75:                                # negated: "not worth it", "would not recommend"
            parts = [cap(pick(info["neg"])) + ".", pick(NEG_NEGATED)]
        elif r < 0.80:                                # mild complaint written in "neutral" words (hard case)
            parts = [pick(NEU_GENERAL), cap(pick(info["neg"])) + "."]
        elif r < 0.87:                                # looked nice at first, then failed
            parts = [cap(pick(info["pos"])) + pick(CONNECT) + pick(info["neg"]) + ".", pick(NEG_NEGATED + NEG_GENERAL)]
        else:
            parts = [pick(NEG_GENERAL + NEG_NEGATED) if rng.random() < 0.6 else f"Bad {product}."]
    else:  # neutral
        if r < 0.05:
            parts = [pick(HINGLISH["neutral"])]
        elif r < 0.35:
            parts = [pick(NEU_GENERAL), cap(pick(info["neu_aspect"])) + "."]
        elif r < 0.42:                                # "not bad" style but only lukewarm (hard case)
            parts = [pick(POS_NEGATED), cap(pick(info["neu_aspect"])) + "."]
        elif r < 0.70:                                # genuinely mixed: one good thing, one bad thing
            if rng.random() < 0.5:
                parts = [cap(pick(info["pos"])) + pick(CONNECT) + pick(info["neg"]) + "."]
            else:
                parts = [cap(pick(info["neg"])) + pick(CONNECT) + pick(info["pos"]) + "."]
            if rng.random() < 0.5:
                parts.append(pick(NEU_GENERAL))
        elif r < 0.85:
            parts = [f"The {product} is okay.", cap(pick(info["neu_aspect"])) + "."]
        else:
            parts = [pick(NEU_GENERAL)]

    # sometimes mention the product name, Hinglish word or an emoji
    if rng.random() < 0.25:
        parts.insert(0, f"Bought this {product} last month.")
    if rng.random() < 0.06 and sentiment in HINGLISH:
        parts.append(pick(HINGLISH[sentiment]))
    text = " ".join(parts)
    if rng.random() < 0.15:
        text += " " + pick(EMOJIS[sentiment])
    if rng.random() < 0.18:
        text = add_typos(text, rng)
    if rng.random() < 0.08:
        text = text.upper() if rng.random() < 0.3 else text.lower()
    if rng.random() < 0.05:
        text = text.replace("good", "gooood").replace("bad", "baaad").replace("love", "loveee")
    return text


RATING_GIVEN_SENTIMENT = {          # P(rating = 1..5 | sentiment): people are not perfectly consistent
    "positive": [0.0, 0.01, 0.05, 0.35, 0.59],
    "neutral": [0.03, 0.17, 0.60, 0.18, 0.02],
    "negative": [0.58, 0.34, 0.07, 0.01, 0.0],
}


def make_dataset(n=N, seed=SEED):
    rng = np.random.default_rng(seed)
    cats = rng.choice(list(CATEGORIES), size=n, p=[0.28, 0.22, 0.2, 0.15, 0.15])
    sentiments = rng.choice(["positive", "neutral", "negative"], size=n, p=[0.5, 0.2, 0.3])
    texts = [make_review(s, c, rng) for s, c in zip(sentiments, cats)]
    ratings = [int(rng.choice([1, 2, 3, 4, 5], p=RATING_GIVEN_SENTIMENT[s])) for s in sentiments]

    # Label noise: annotators disagree on ~6% of reviews (the label is changed, the text is not)
    labels = sentiments.copy()
    noisy = rng.random(n) < 0.06
    for i in np.where(noisy)[0]:
        labels[i] = rng.choice([s for s in ["positive", "neutral", "negative"] if s != labels[i]])

    start = np.datetime64("2024-01-01")
    dates = start + rng.integers(0, 730, n).astype("timedelta64[D]")
    df = pd.DataFrame({
        "review_id": [f"R{i:05d}" for i in range(1, n + 1)],
        "product_category": cats,
        "review_text": texts,
        "rating": ratings,
        "verified_purchase": rng.random(n) < 0.8,
        "review_date": pd.to_datetime(dates).strftime("%Y-%m-%d"),
        "sentiment": labels,
    })

    # Messiness: empty / whitespace-only reviews (customer gave stars but no text)
    empty_idx = rng.choice(n, size=35, replace=False)
    df.loc[empty_idx, "review_text"] = rng.choice(["", " ", "   "], size=35)
    df.loc[empty_idx[:15], "review_text"] = np.nan
    # Duplicate rows (the same review exported twice)
    dupes = df.sample(60, random_state=seed)
    df = pd.concat([df, dupes], ignore_index=True)
    df = df.sample(frac=1, random_state=seed).reset_index(drop=True)
    return df


if __name__ == "__main__":
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "product_reviews.csv")
    data = make_dataset()
    data.to_csv(out, index=False)
    print(f"Wrote {len(data)} rows to {out}")
    print(data["sentiment"].value_counts().to_string())
