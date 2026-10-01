from transformers import pipeline
import re


# ---------------------------------
# LOAD TRANSFORMER MODEL
# ---------------------------------

model = pipeline(
    "text2text-generation",
    model="google/flan-t5-small"
)


# ---------------------------------
# MEETING SUMMARY
# ---------------------------------

def generate_summary(transcript):

    prompt = (
        "Summarize this meeting in 2 short sentences. "
        "Mention the main topic and important activities.\n\n"
        + transcript
    )

    result = model(
        prompt,
        max_new_tokens=80
    )

    return result[0]["generated_text"]


# ---------------------------------
# KEY DECISIONS
# ---------------------------------

def extract_key_decisions(transcript):

    decisions = []

    lines = transcript.split("\n")

    decision_words = [
        "decided",
        "decision",
        "agreed",
        "we will",
        "let's",
        "approved"
    ]

    for line in lines:

        line = line.strip()

        if ":" not in line:
            continue

        speaker, text = line.split(":", 1)

        text_lower = text.lower()

        if any(
            word in text_lower
            for word in decision_words
        ):

            decisions.append(text.strip())

    return decisions


# ---------------------------------
# ACTION ITEM EXTRACTION
# ---------------------------------

def extract_action_items(transcript):

    action_items = []

    lines = transcript.split("\n")


    for line in lines:

        line = line.strip()

        if ":" not in line:
            continue


        speaker, text = line.split(":", 1)

        speaker = speaker.strip()
        text = text.strip()

        text_lower = text.lower()


        # -----------------------------
        # ACTION WORDS
        # -----------------------------

        action_words = [
            "i'll",
            "i will",
            "i can",
            "prepare",
            "send",
            "test",
            "check",
            "handle",
            "complete",
            "finish",
            "create",
            "update",
            "review",
            "submit",
            "need to",
            "needs to"
        ]


        if not any(
            word in text_lower
            for word in action_words
        ):

            continue


        # -----------------------------
        # OWNER
        # -----------------------------

        missing_owner = False


        if (
            "someone" in text_lower
            or "anyone" in text_lower
            or "somebody" in text_lower
        ):

            owner = "Not Assigned"
            missing_owner = True

        else:

            owner = speaker


        # -----------------------------
        # DEADLINE
        # -----------------------------

        deadline = None


        days = [
            "monday",
            "tuesday",
            "wednesday",
            "thursday",
            "friday",
            "saturday",
            "sunday",
            "tomorrow"
        ]


        for day in days:

            if day in text_lower:

                deadline = day
                break


        # Also detect dates like:
        # 15 October
        # October 15

        if deadline is None:

            date_pattern = (
                r"\b\d{1,2}\s+"
                r"(january|february|march|april|may|june|"
                r"july|august|september|october|november|december)\b"
            )

            date_match = re.search(
                date_pattern,
                text_lower
            )

            if date_match:

                deadline = date_match.group(0)


        missing_deadline = deadline is None


        # -----------------------------
        # PRIORITY
        # -----------------------------

        priority = "Medium"


        if (
            "urgent" in text_lower
            or "asap" in text_lower
            or "tomorrow" in text_lower
        ):

            priority = "High"


        # -----------------------------
        # CONFIDENCE
        # -----------------------------

        confidence = 70


        if deadline is not None:

            confidence += 15


        if not missing_owner:

            confidence += 10


        if confidence > 100:

            confidence = 100


        # -----------------------------
        # ADD ACTION ITEM
        # -----------------------------

        action_items.append({

            "task": text,

            "owner": owner,

            "deadline": (
                deadline
                if deadline
                else "Not specified"
            ),

            "status": "Pending",

            "priority": priority,

            "confidence": confidence,

            "missing_owner": missing_owner,

            "missing_deadline": missing_deadline,

            "duplicate": False

        })


    # ---------------------------------
    # DUPLICATE DETECTION
    # ---------------------------------

    for i in range(len(action_items)):

        for j in range(i + 1, len(action_items)):

            task1 = (
                action_items[i]["task"]
                .lower()
                .split()
            )

            task2 = (
                action_items[j]["task"]
                .lower()
                .split()
            )


            common_words = set(task1).intersection(
                set(task2)
            )


            if len(common_words) >= 3:

                action_items[i]["duplicate"] = True

                action_items[j]["duplicate"] = True


    return action_items