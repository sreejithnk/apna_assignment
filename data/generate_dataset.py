import json
import random
import re

# -----------------------------
# CONFIG
# -----------------------------
OUTPUT_FILE = "train_v2.jsonl"
N_SAMPLES = 500
SEED = 42

random.seed(SEED)

INSTRUCTION = (
    "Extract intent and slots. Output strict JSON. "
    "Also return normalized_text where Hindi is Devanagari and English is Latin."
)

# -----------------------------
# HINDI NORMALIZATION LEXICON
# -----------------------------
HINDI_MAP = {
    "bhai": "भाई",
    "yaar": "यार",
    "haan": "हाँ",
    "arre": "अरे",
    "accha": "अच्छा",
    "theek": "ठीक",
    "bas": "बस",
    "kal": "कल",
    "parso": "परसो",
    "aaj": "आज",
    "subah": "सुबह",
    "shaam": "शाम",
    "jaldi": "जल्दी",
    "thoda": "थोड़ा",
    "yaad": "याद",
    "dila": "दिला",
    "dena": "देना",
    "kar": "कर",
    "karo": "करो",
    "do": "दो",
    "rakh": "रख",
    "lo": "लो",
    "nahi": "नहीं",
    "ka": "का",
    "ki": "की",
    "ke": "के",
    "pe": "पर",
    "aage": "आगे",
    "kuch": "कुछ",
    "din": "दिन",
    "liye": "लिए",
    "me": "में",
    "kya": "क्या",
    "hain": "हैं",
    "mujhe": "मुझे",
    "kab": "कब",
    "sakte": "सकते",
    "baje": "बजे",
    "wali": "वाली",
    "ho": "हो",
    "sakti": "सकती",
    "yeh": "यह",
    "galat": "गलत",
    "ek": "एक",
    "baar": "बार",
    "na": "ना",
    "pakka": "पक्का",
    "se": "से",
    "hai": "है",
    "aaya": "आया"
}

# -----------------------------
# SEMANTIC FRAMES
# -----------------------------
FRAMES = [
    {
        "intent": "set_reminder",
        "slots": {"time": "कल सुबह", "task": "call"},
        "type": "reminder"
    },
    {
        "intent": "reschedule_meeting",
        "slots": {"original_time": "कल", "new_time": "Friday 4pm"},
        "type": "reschedule"
    },
    {
        "intent": "query_charges",
        "slots": {"amount": "1.25 lakh", "institution": "HDFC"},
        "type": "finance"
    },
    {
        "intent": "schedule_meeting",
        "slots": {"time": "कल", "requires_clarification": True},
        "type": "ambiguous"
    },
    {
        "intent": "cancel_meeting",
        "slots": {"meeting": "team sync", "reason": "urgent work"},
        "type": "cancel"
    },
    {
        "intent": "request_callback",
        "slots": {"time": "आज शाम", "priority": "high"},
        "type": "callback"
    },
    {
        "intent": "billing_inquiry",
        "slots": {"amount": "5000", "description": "subscription"},
        "type": "billing"
    },
    {
        "intent": "confirm_appointment",
        "slots": {"date": "परसो", "time": "2pm"},
        "type": "confirmation"
    }
]

# -----------------------------
# SURFACE REALIZATIONS
# -----------------------------
REALIZATIONS = {
    "reminder": [
        "bhai kal subah call yaad dila",
        "kal subah call reminder set kar",
        "haan kal subah call yaad dila dena",
        "pls kal subah call yaad dila",
        "mujhe kal 9am pe call ka reminder de",
        "reminder set kar kal morning 10 baje ke liye",
        "kal jaldi subah mujhe call karna yaad rakhna"
    ],
    "reschedule": [
        "bhai kal meeting Friday 4pm pe shift kar do",
        "kal wali meeting Friday 4pm move kar do",
        "haan kal nahi Friday 4pm rakh lo meeting",
        "meeting ko kal se Friday 4pm kar do",
        "kal meeting ko aage postpone kar do",
        "meeting kal se parso shift kar do please",
        "can we reschedule kal ki meeting Friday ko"
    ],
    "finance": [
        "HDFC ka 1.25 lakh loan foreclosure charges batao",
        "1.25 lakh loan ke charges HDFC me kya hain",
        "bhai HDFC loan 1.25 lakh charges",
        "HDFC me 5000 ka charge aaya hai kya",
        "loan closure ke liye kitne charges honge",
        "bhai monthly fee kitni hai bank me"
    ],
    "ambiguous": [
        "kal thoda jaldi meeting rakh lo",
        "haan kal ya parso meeting rakhte hain",
        "kal meeting rakh lo thoda early",
        "timing fix kar do please",
        "kab time available hai next week"
    ],
    "cancel": [
        "kal ki meeting cancel kar do bhai",
        "team sync cancel kar dena please",
        "haan kal meeting nahi ho sakti cancel kar do",
        "meeting postpone kar do kuch din ke liye",
        "urgent kaam hai cancel kar do kal ki meeting"
    ],
    "callback": [
        "mujhe aaj shaam ko callback de do",
        "please kal morning call kar dena",
        "urgent hai callback immediately karo",
        "kab callback kar sakte ho",
        "aaj hi call back karna important hai"
    ],
    "billing": [
        "5000 ka charge kya hai",
        "subscription ki cost kitni hai monthly",
        "bill me 2000 extra charge kyu aaya",
        "refund kar do yeh charge galat hai",
        "invoice check kar ek baar"
    ],
    "confirmation": [
        "parso 2pm appointment confirm hai na",
        "haan kal 3 baje appointment fixed hai",
        "confirm kar do meeting kal 4pm",
        "appointment time confirm kar",
        "theek hai parso meeting pakka hai"
    ]
}

FILLER_NOISE = ["", "…", ",", " pls", " yaar"]

# -----------------------------
# HELPERS
# -----------------------------
def normalize_script(text: str) -> str:
    tokens = re.split(r"(\s+)", text)
    normalized = []

    for tok in tokens:
        key = tok.lower().strip(".,…")
        if key in HINDI_MAP:
            normalized.append(HINDI_MAP[key])
        else:
            normalized.append(tok)

    return "".join(normalized)

def add_noise(text: str) -> str:
    if random.random() < 0.4:
        text = random.choice(["haan ", "bhai ", ""]) + text
    if random.random() < 0.3:
        text += random.choice(FILLER_NOISE)
    return text

# -----------------------------
# MAIN GENERATION LOOP
# -----------------------------
def generate_sample():
    frame = random.choice(FRAMES)
    base_text = random.choice(REALIZATIONS[frame["type"]])
    noisy_text = add_noise(base_text)
    normalized_text = normalize_script(noisy_text)

    return {
        "input": noisy_text,
        "instruction": INSTRUCTION,
        "output": {
            "intent": frame["intent"],
            "slots": frame["slots"],
            "normalized_text": normalized_text,
            "language_mix": "hinglish",
            "script_rules": {
                "hindi": "devanagari",
                "english": "latin"
            }
        }
    }

# -----------------------------
# WRITE FILE
# -----------------------------
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    for _ in range(N_SAMPLES):
        sample = generate_sample()
        f.write(json.dumps(sample, ensure_ascii=False) + "\n")

print(f"✅ Generated {N_SAMPLES} high-diversity samples → {OUTPUT_FILE}")
