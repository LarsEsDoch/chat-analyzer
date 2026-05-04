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


def analyze_vocabulary(file_path, start_filter=None, end_filter=None):
    all_data = get_formatted_data(file_path)

    start = start_filter if start_filter else datetime.min
    end = end_filter if end_filter else datetime.max
    data = [m for m in all_data if start <= m['ts'] <= end]

    if not data:
        print("Keine Nachrichten für die Wortschatz-Analyse gefunden.")
        return

    # 1. Recognizes letter repetition (eee, fff)
    flood_pattern = re.compile(r'(.)\1{2,}')

    # 2. Detects syllable repetition (hihihi, looolooo)
    syllable_pattern = re.compile(r'(\w{2,3})\1{2,}')

    vocab_stats = defaultdict(lambda: {
        'all_words_list': [],
        'unique_words_set': set(),
        'word_lengths': Counter()
    })

    for m in data:
        s_name = m['sender']
        words = re.findall(r'\b[a-zA-ZäöüÄÖÜß]+\b', m['msg'].lower())

        for w in words:
            # Filter check
            is_flood = flood_pattern.search(w)
            is_syllable_spam = syllable_pattern.search(w)

            if not is_flood and not is_syllable_spam and len(w) < 100:
                vocab_stats[s_name]['all_words_list'].append(w)
                vocab_stats[s_name]['unique_words_set'].add(w)
                vocab_stats[s_name]['word_lengths'][len(w)] += 1

    print("=" * 60)
    print(f"WORTSCHATZ-ANALYSE")
    print("=" * 60)

    for name, s in vocab_stats.items():
        total_count = len(s['all_words_list'])
        unique_count = len(s['unique_words_set'])

        # Type-Token-Ratio (TTR)
        ttr = (unique_count / total_count * 100) if total_count > 0 else 0

        # Average word length (letters per word)
        avg_word_len = sum(k * v for k, v in s['word_lengths'].items()) / total_count if total_count > 0 else 0

        longest_words = sorted(list(s['unique_words_set']), key=len, reverse=True)[:5]

        print(f"Name: {name}")
        print(f"  > Benutzte Wörter insgesamt: {total_count}")
        print(f"  > Einzigartige Wörter:       {unique_count}")
        print(f"  > Wortschatz-Vielfalt (TTR): {ttr:.2f}%")
        print(f"  > Ø Buchstaben pro Wort:     {avg_word_len:.2f}")
        print(f"  > Längste Wörter:            {', '.join(longest_words)}")

        # Small distribution of word lengths
        print(f"  > Wortlängen-Profil:")
        for length in range(1, 11):  # Show distribution for 1 to 10 letters
            count = s['word_lengths'][length]
            perc = (count / total_count * 100) if total_count > 0 else 0
            bar = "█" * int(perc / 2)
            print(f"    {length:>2} Bst.: {perc:>5.1f}% {bar}")

        print("-" * 40)

    senders = list(vocab_stats.keys())
    if len(senders) >= 2:
        user1, user2 = senders[0], senders[1]
        set1 = vocab_stats[user1]['unique_words_set']
        set2 = vocab_stats[user2]['unique_words_set']

        # Words that both use
        common_vocabulary = set1.intersection(set2)
        common_count = len(common_vocabulary)

        total_unique_combined = len(set1.union(set2))

        # Jaccard-Coefficient
        similarity = (common_count / total_unique_combined * 100) if total_unique_combined > 0 else 0

        user1_counts = Counter(vocab_stats[user1]['all_words_list'])
        user2_counts = Counter(vocab_stats[user2]['all_words_list'])
        core_vocabulary = [
            w for w in common_vocabulary
            if user1_counts[w] >= 5 and user2_counts[w] >= 5 and w not in STOP_WORDS
        ]

        print("=" * 60)
        print(f"WORTSCHATZ-ÜBERSCHNEIDUNG")
        print("=" * 60)
        print(f"Gemeinsame Wörter: {common_count}")
        print(f"Ähnlichkeits-Index: {similarity:.2f}%")
        print(f"Echter Kern-Wortschatz: {len(core_vocabulary)}")
        print(f"Beispiele: {', '.join(sorted(core_vocabulary, key=len, reverse=True)[:10])}")


def analyze_linguistic_style(file_path, start_filter=None, end_filter=None):
    all_data = get_formatted_data(file_path)

    start = start_filter if start_filter else datetime.min
    end = end_filter if end_filter else datetime.max
    data = [m for m in all_data if start <= m['ts'] <= end]

    if not data: return

    # --- Dictionaries ---
    dict_slang = {'cringe', 'sus', 'digga', 'bro', 'wild', 'slay', 'safe', 'lol', 'lmao', 'fr', 'legit', 'nope'}
    dict_denglisch = {'nice', 'weird', 'crazy', 'random', 'match', 'vibes', 'feeling', 'awkward', 'literally', 'fyi',
                      'asap', 'sad', 'happy', 'cute'}
    dict_educated = {'demnach', 'infolgedessen', 'paradox', 'aspekt', 'faktisch', 'evident', 'hypothetisch', 'kontext',
                     'diskurs', 'essenziell', 'fundiert', 'prinzipiell', 'spezifisch', 'relevanz'}
    dict_support = {'stolz', 'super', 'toll', 'perfekt', 'gut', 'schaffst', 'glaub', 'schön', 'klasse', 'unterstütz',
                    'stark', 'bester', 'beste'}
    dict_self = {'ich', 'mein', 'meine', 'meins', 'mir', 'mich'}
    dict_other = {'du', 'dein', 'deine', 'dir', 'dich'}

    # Regex for questions
    question_pattern = re.compile(
        r'\b(was|wie|wo|warum|weshalb|wieso|wer|wann|hast du|weißt du|kannst du|darfst du|soll ich)\b', re.IGNORECASE)

    style_stats = defaultdict(lambda: {
        'total_words': 0,
        'complex_words': 0,
        'slang_hits': 0,
        'denglisch_hits': 0,
        'educated_hits': 0,
        'support_hits': 0,
        'self_hits': 0,
        'other_hits': 0,
        'questions_asked': 0
    })

    for m in data:
        s_name = m['sender']
        msg_text = m['msg'].lower()
        words = re.findall(r'\b[a-zäöüß]+\b', msg_text)

        style_stats[s_name]['total_words'] += len(words)

        # Check für Fragen (entweder durch Fragezeichen ODER durch Fragestruktur)
        if '?' in m['msg'] or question_pattern.search(msg_text):
            style_stats[s_name]['questions_asked'] += 1

        for w in words:
            if len(w) >= 10: style_stats[s_name]['complex_words'] += 1
            if w in dict_slang: style_stats[s_name]['slang_hits'] += 1
            if w in dict_denglisch: style_stats[s_name]['denglisch_hits'] += 1
            if w in dict_educated: style_stats[s_name]['educated_hits'] += 1
            if w in dict_support: style_stats[s_name]['support_hits'] += 1
            if w in dict_self: style_stats[s_name]['self_hits'] += 1
            if w in dict_other: style_stats[s_name]['other_hits'] += 1
            if w in dict_denglisch: print(w)

    # --- AUSGABE ---
    print("=" * 60)
    print("LINGUISTISCHES & PSYCHOLOGISCHES PROFIL")
    print("=" * 60)

    for name, s in style_stats.items():
        tw = s['total_words'] if s['total_words'] > 0 else 1  # Division by Zero Schutz
        msg_count = sum(1 for m in data if m['sender'] == name)

        # Wir berechnen "Vorkommen pro 10.000 Wörter", das macht seltene Dinge vergleichbar
        rate = lambda x: (x / tw) * 10000

        print(f"Name: {name}")

        print(f"\n  [ Sprach-Stil (Treffer pro 10.000 Wörter) ]")
        print(f"  > Slang/Jugendsprache: {rate(s['slang_hits']):.1f}")
        print(f"  > Denglisch:           {rate(s['denglisch_hits']):.1f}")
        print(f"  > Gehobene Sprache:    {rate(s['educated_hits']):.1f}")
        print(f"  > Komplexität (>9 Bst):{(s['complex_words'] / tw * 100):.1f}% aller Wörter")

        print(f"\n  [ Beziehungs-Dynamik ]")
        # Ego-Fokus Ratio (Ich vs Du)
        ego_ratio = s['self_hits'] / s['other_hits'] if s['other_hits'] > 0 else 0
        focus = "Selbst-Fokus" if ego_ratio > 1.2 else "Du-Fokus" if ego_ratio < 0.8 else "Ausgeglichen"

        print(f"  > Ich-Bezug:           {s['self_hits']} mal ('ich', 'mein'...)")
        print(f"  > Du-Bezug:            {s['other_hits']} mal ('du', 'dein'...)")
        print(f"  > Fokus-Index:         {ego_ratio:.2f} ({focus})")
        print(f"  > Support/Lob-Wörter:  {rate(s['support_hits']):.1f} (pro 10k Wörter)")

        print(f"\n  [ Gesprächsführung ]")
        q_rate = (s['questions_asked'] / msg_count * 100) if msg_count > 0 else 0
        print(f"  > Fragen gestellt:     {s['questions_asked']} ({q_rate:.1f}% aller Nachrichten)")
        print("-" * 40)
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
    wait_start_ts = data[0]['ts']

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

        weekday_names = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]
        day_name = weekday_names[curr['ts'].weekday()]
        stats[s_name]['weekdays'][day_name] += 1

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
            diff = (curr['ts'] - wait_start_ts).total_seconds() / 60
            if diff < 240:
                stats[s_name]['responses'].append(diff)
                #print(s_name + ", " + str(diff) + ": " + msg_text)
            else:
                #print(s_name + ", " + str(diff) + ": " + msg_text + " (" + str(curr['ts']) + ")")
                pass
            wait_start_ts = curr['ts']
            current_burst = 1
            last_sender = s_name
        last_ts = curr['ts']

    # --- Output ---
    print("=" * 60)
    print(f"Chat Analyzer ({data[0]['ts'].date()} bis {data[-1]['ts'].date()})")
    print("=" * 60)

    for name, s in stats.items():
        avg_msg_length = s['total_words'] / s['msg_count'] if s['msg_count'] > 0 else 0
        avg_resp = sum(s['responses']) / len(s['responses']) if s['responses'] else 0
        avg_burst = sum(s['bursts']) / len(s['bursts']) if s['bursts'] else 1
        top_emojis = "".join([e for e, count in s['emojis'].most_common(5)])

        top_words = ", ".join([f"{w} ({c}x)" for w, c in s['common_words'].most_common(10)])

        print(f"Name: {name}")
        print(f"  > Nachrichten: {s['msg_count']}")
        print(f"  > Ø Nachrichten am Stück: {avg_burst:.1f}")
        print(f"  > Ø Antwortzeit: {avg_resp:.1f} Min.")
        print(f"  > Ø Wortanzahl: {avg_msg_length:.1f} Wörter pro Nachricht")
        print(f"  > Top Wörter:  {top_words if top_words else 'Keine'}")
        print(f"  > Top Emojis: {top_emojis if top_emojis else 'Keine'}")
        print(f"  > Zeitliche Verteilung:")
        for slot, count in sorted(s['time_slots'].items()):
            perc = (count / s['msg_count']) * 100
            print(f"    - {slot:<18}: {perc:>5.1f}% ({count} Nachrichten)")
        print(f"  > Aktivität nach Wochentag:")
        weekday_order = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]
        for day in weekday_order:
            count = s['weekdays'][day]
            perc = (count / s['msg_count']) * 100 if s['msg_count'] > 0 else 0
            print(f"    - {day:<10}: {perc:>5.1f}% ({count})")
        print("-" * 40)


def analyze_emojis(file_path, start_filter=None, end_filter=None):
    all_data = get_formatted_data(file_path)

    start = start_filter if start_filter else datetime.min
    end = end_filter if end_filter else datetime.max
    data = [m for m in all_data if start <= m['ts'] <= end]

    if not data:
        print("Keine Daten für Emoji-Analyse gefunden.")
        return

    emoji_stats = defaultdict(lambda: {
        'total_emojis': 0,
        'unique_emojis': Counter(),
        'msg_with_emoji': 0,
        'emoji_combos': Counter()
    })

    for m in data:
        s_name = m['sender']
        # Extract all emojis from the message
        found = [c for c in m['msg'] if emoji.is_emoji(c)]

        if found:
            emoji_stats[s_name]['total_emojis'] += len(found)
            emoji_stats[s_name]['unique_emojis'].update(found)
            emoji_stats[s_name]['msg_with_emoji'] += 1
            # Save the combination if it contains more than one emoji.
            if len(found) > 1:
                combo = "".join(found[:3])
                emoji_stats[s_name]['emoji_combos'][combo] += 1

    print("=" * 60)
    print(f"EMOJI-DIVERSITÄT & VIBE-CHECK")
    print("=" * 60)

    for name, s in emoji_stats.items():
        msg_count = next((m_cnt['msg_count'] for n, m_cnt in defaultdict(int).items() if n == name), 1)
        actual_msg_count = sum(1 for m in data if m['sender'] == name)

        emoji_ratio = (s['total_emojis'] / actual_msg_count) if actual_msg_count > 0 else 0
        diversity = len(s['unique_emojis'])

        print(f"Name: {name}")
        print(f"  > Emojis insgesamt:   {s['total_emojis']}")
        print(f"  > Emoji-Dichte:       {emoji_ratio:.2f} Emojis pro Nachricht")
        print(f"  > Emojis-Diversität:  {diversity} verschiedene Symbole genutzt")

        print(f"  > Top 10 Emojis:")
        top_10 = s['unique_emojis'].most_common(10)
        for emo, count in top_10:
            perc = (count / s['total_emojis'] * 100) if s['total_emojis'] > 0 else 0
            print(f"    - {emo} : {count:>5}x ({perc:>4.1f}%)")

        if s['emoji_combos']:
            common_combos = ", ".join([f"{c}" for c, _ in s['emoji_combos'].most_common(3)])
            print(f"  > Typische Kombis:    {common_combos}")

        print("-" * 40)


def check_occurrence(file_path, search_terms, start_filter=None, end_filter=None, output_occurence=False):
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
                if output_occurence: print(m['sender'] + ": " + m['msg'])

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
analyze_vocabulary('input/chat.txt')
analyze_chat('input/chat.txt')
analyze_emojis('input/chat.txt')
check_occurrence('input/chat.txt', ["Was machst du"])
#check_occurrence('input/chat.txt', ["this"])