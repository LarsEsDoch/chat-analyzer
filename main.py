import re
from collections import Counter, defaultdict
from datetime import datetime
import emoji

STOP_WORDS = {
    'und', 'zu', 'dem', 'der', 'die', 'das', 'ist', 'ja', 'nein', 'ich', 'du', 'wir', 'ihr', 'sie',
    'ein', 'eine', 'einer', 'eines', 'einem', 'einen', 'mit', 'auf', 'für', 'von', 'als', 'an',
    'um', 'am', 'im', 'in', 'auch', 'so', 'was', 'hat', 'haben', 'hatte', 'war', 'waren', 'wie',
    'aber', 'oder', 'doch', 'dann', 'noch', 'schon', 'mal', 'mich', 'dich', 'dir', 'mir', 'den',
    'nicht', 'wenn', 'kann', 'bei'
}


def get_formatted_data(file_path):
    # Pattern for genuine messages (with colon)
    msg_pattern = re.compile(r'^(\d{1,2}/\d{1,2}/\d{2,4},\s\d{2}:\d{2})\s-\s([^:]+):\s(.+)$')
    # Pattern only for the beginning of the date (to distinguish system messages from multiline messages)
    date_pattern = re.compile(r'^\d{1,2}/\d{1,2}/\d{2,4},\s\d{2}:\d{2}\s-\s')

    data = []
    current_msg = None

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                line_str = line.strip()
                if not line_str: continue

                # Line begins with a date
                if date_pattern.match(line_str):
                    # If there is still  a message in the buffer -> Save
                    if current_msg:
                        data.append(current_msg)
                        current_msg = None

                    # Check for genuine message
                    match = msg_pattern.match(line_str)
                    if match:
                        ts_str, sender, msg = match.groups()

                        omitted_patterns = ["<Media omitted>", "<Video note omitted>", "<Sticker omitted>",
                                            "<Audio omitted>", "View once voice message omitted",
                                            "This message was deleted", "You deleted this message",]
                        if any(p in msg for p in omitted_patterns):
                            current_msg = None
                            continue


                        clean_msg = msg.replace("<This message was edited>", "").strip()

                        try:
                            ts = datetime.strptime(ts_str, '%m/%d/%y, %H:%M')
                        except ValueError:
                            ts = datetime.strptime(ts_str, '%m/%d/%Y, %H:%M')

                        current_msg = {
                            'ts': ts,
                            'sender': sender.strip(),
                            'msg': clean_msg,
                            'hour': ts.hour
                        }
                    # If it has a date but no match (e.g. system message),
                    # current_msg remains None and the line is ignored.

                # Line does not begin with a date -> Multiline
                else:
                    if current_msg:
                        clean_fragment = line_str.replace("<This message was edited>", "").strip()
                        if clean_fragment:
                            current_msg['msg'] += " " + clean_fragment

            # Save last message after loop
            if current_msg:
                data.append(current_msg)

    except FileNotFoundError:
        print(f"Fehler: Die Datei '{file_path}' wurde nicht gefunden.")

    return data


def analyze_chat(file_path, start_filter=None, end_filter=None):
    all_data = get_formatted_data(file_path)

    # Filtering
    start = start_filter if start_filter else datetime.min
    end = end_filter if end_filter else datetime.max
    data = [m for m in all_data if start <= m['ts'] <= end]

    if not data:
        print("Keine Nachrichten im Zeitraum gefunden.")
        return

    # --- Statistics ---
    stats = defaultdict(lambda: {
        'msg_count': 0, 'total_words': 0, 'responses': [], 'time_slots': Counter(),
        'emojis': Counter(), 'bursts': [], 'weekdays': Counter(), 'common_words': Counter()
    })

    current_burst = 0
    last_sender = data[0]['sender']
    last_ts = data[0]['ts']

    for i, curr in enumerate(data):
        s_name = curr['sender']
        msg_text = curr['msg']

        words_in_this_msg = len(re.findall(r'\b\w+\b', msg_text))

        stats[s_name]['msg_count'] += 1
        stats[s_name]['total_words'] += len(msg_text.split())

        words = re.findall(r'\b\w+\b', msg_text.lower())
        filtered_words = [w for w in words if w not in STOP_WORDS and len(w) > 2]
        stats[s_name]['common_words'].update(filtered_words)
        stats[s_name]['total_words'] += len(words)
        if 6 <= curr['hour'] < 12:
            slot = "Morgen (06-12)"
        elif 12 <= curr['hour'] < 18:
            slot = "Mittag/Nachm. (12-18)"
        elif 18 <= curr['hour'] < 23:
            slot = "Abend (18-23)"
        else:
            slot = "Nacht (23-06)"
        stats[s_name]['time_slots'][slot] += 1

        found_emojis = [c for c in msg_text if emoji.is_emoji(c)]
        stats[s_name]['emojis'].update(found_emojis)

        if s_name == last_sender:
            current_burst += 1
        else:
            stats[last_sender]['bursts'].append(current_burst)
            diff = (curr['ts'] - last_ts).total_seconds() / 60
            if diff < 720:
                stats[s_name]['responses'].append(diff)
            current_burst = 1
            last_sender = s_name
        last_ts = curr['ts']

    # --- Output ---
    print("=" * 60)
    print(f"Chat Analyzer ({data[0]['ts'].date()} bis {data[-1]['ts'].date()})")
    print("=" * 60)

    for name, s in stats.items():
        avg_resp = sum(s['responses']) / len(s['responses']) if s['responses'] else 0
        avg_burst = sum(s['bursts']) / len(s['bursts']) if s['bursts'] else 1
        top_emojis = "".join([e for e, count in s['emojis'].most_common(5)])

        top_words = ", ".join([f"{w} ({c}x)" for w, c in s['common_words'].most_common(10)])

        print(f"Name: {name}")
        print(f"  > Nachrichten: {s['msg_count']}")
        print(f"  > Ø Nachrichten am Stück: {avg_burst:.1f}")
        print(f"  > Ø Antwortzeit: {avg_resp:.1f} Min.")
        print(f"  > Top Wörter:  {top_words if top_words else 'Keine'}")
        print(f"  > Top Emojis: {top_emojis if top_emojis else 'Keine'}")
        print(f"  > Zeitliche Verteilung:")
        for slot, count in sorted(s['time_slots'].items()):
            perc = (count / s['msg_count']) * 100
            print(f"    - {slot:<18}: {perc:>5.1f}% ({count} Nachrichten)")
        print("-" * 40)


def check_occurrence(file_path, search_terms, start_filter=None, end_filter=None):
    all_data = get_formatted_data(file_path)

    start = start_filter if start_filter else datetime.min
    end = end_filter if end_filter else datetime.max
    data = [m for m in all_data if start <= m['ts'] <= end]

    results = defaultdict(lambda: {'total_count': 0, 'msg_with_term': 0})

    for m in all_data:
        if start <= m['ts'] <= end:
            s_name = m['sender']
            msg_lower = m['msg'].lower()
            found_in_msg = False

            for term in search_terms:
                t_lower = term.lower()
                if t_lower in msg_lower:
                    results[s_name]['total_count'] += msg_lower.count(t_lower)
                    found_in_msg = True

            if found_in_msg:
                results[s_name]['msg_with_term'] += 1

    # --- Output ---
    print("=" * 60)
    print(f"ANALYSE FÜR: '{', '.join(search_terms)}'")
    print(f"Zeitraum: {data[0]['ts'].date()} bis {data[-1]['ts'].date()}")
    print("=" * 60)

    if not results:
        print("Keine Treffer gefunden.")
        return

    for name, data in results.items():
        print(f"Name: {name}")
        print(f"  > Insgesamt vorkommen:      {data['total_count']} mal")
        print(f"  > Nachrichten mit Begriff:  {data['msg_with_term']}")
        if data['msg_with_term'] > 0:
            avg = data['total_count'] / data['msg_with_term']
        else:
            avg = 0.0
        print(f"  > Ø Intensität pro Nachricht: {avg:.2f}")
        print("-" * 30)

# --- Calls ---
# Example:
# analyze_chat('input/chat.txt', start_filter=datetime(2023, 4, 23), end_filter=datetime(2025, 1, 1))
# check_occurrence('input/chat.txt', ["Hey", "Hi", "Hello"], start_filter=datetime(2024, 6, 7))
analyze_chat('input/chat.txt')
#check_occurrence('input/chat.txt', ["Ich liebe dich", "Ich hab dich lieb"])