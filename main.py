import re
from collections import Counter, defaultdict
from datetime import datetime
import emoji
import os
from tqdm import tqdm
from wordlists import denglisch, youth_language, educated_language, supporting_language, selfish_language, other_language
import spacy
import torch

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

                        media_patterns = [
                            "<Media omitted>", "<Video note omitted>", "<Sticker omitted>",
                            "<Audio omitted>", "View once voice message omitted"
                        ]

                        deleted_patterns = [
                            "This message was deleted", "You deleted this message"
                        ]

                        if any(p in msg for p in deleted_patterns):
                            current_msg = None
                            continue

                        is_media = any(p in msg for p in media_patterns)


                        clean_msg = msg.replace("<This message was edited>", "").strip()

                        try:
                            ts = datetime.strptime(ts_str, '%m/%d/%y, %H:%M')
                        except ValueError:
                            ts = datetime.strptime(ts_str, '%m/%d/%Y, %H:%M')

                        current_msg = {
                            'ts': ts,
                            'sender': sender.strip(),
                            'msg': clean_msg,
                            'hour': ts.hour,
                            'is_media': is_media
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


def _split_list(lst):
    words = set()
    phrases = []
    for entry in lst:
        e = entry.lower().strip()
        if ' ' in e:
            phrases.append(e)
        else:
            words.add(e)
    return words, phrases


class ChatAnalyzer:
    def __init__(self, file_path):
        self.file_path = file_path
        self.data = get_formatted_data(file_path)
        self._nlp = None

    def _get_nlp(self):
        if self._nlp is None:
            msvc_bin_dir = r"C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Tools\MSVC\14.44.35207\bin\Hostx64\x64"

            if msvc_bin_dir not in os.environ["PATH"]:
                os.environ["PATH"] = msvc_bin_dir + os.pathsep + os.environ["PATH"]
            print(f"CUDA verfügbar: {torch.cuda.is_available()}")
            print(f"Grafikkarte: {torch.cuda.get_device_name(0)}")
            if spacy.prefer_gpu():
                print("GPU-Beschleunigung aktiv!")
            self._nlp = spacy.load("de_dep_news_trf")
            self._nlp.max_length = 5_000_000
        return self._nlp

    def _filter(self, start_filter=None, end_filter=None, include_media=False):
        start = start_filter if start_filter else datetime.min
        end = end_filter if end_filter else datetime.max
        return [
            m for m in self.data
            if start <= m['ts'] <= end
               and (include_media or not m['is_media'])
        ]

    def analyze_chat(self, start_filter=None, end_filter=None):
        data = self._filter(start_filter, end_filter, True)
        if not data:
            print("Keine Nachrichten im Zeitraum gefunden.")
            return

        # --- Statistics ---
        stats = defaultdict(lambda: {
            'msg_count': 0, 'total_words': 0, 'responses': [], 'time_slots': Counter(),
            'emojis': Counter(), 'bursts': [], 'weekdays': Counter(), 'common_words': Counter(),
            'text_msg_count': 0, 'number_count': 0
        })

        current_burst = 0
        last_sender = data[0]['sender']
        last_ts = data[0]['ts']
        wait_start_ts = data[0]['ts']

        for i, curr in enumerate(data):
            s_name = curr['sender']
            msg_text = curr['msg']
            is_media = curr['is_media']

            stats[s_name]['msg_count'] += 1

            if not is_media:
                stats[s_name]['text_msg_count'] += 1
                stats[s_name]['total_words'] += len(msg_text.split())
                stats[s_name]['number_count'] += len(re.findall(r'\d+', msg_text))

                words = re.findall(r'\b\w+\b', msg_text.lower())
                filtered_words = [w for w in words if w not in STOP_WORDS and len(w) > 2]
                stats[s_name]['common_words'].update(filtered_words)

                found_emojis = [e['emoji'] for e in emoji.emoji_list(msg_text)]
                stats[s_name]['emojis'].update(found_emojis)

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

            if s_name == last_sender:
                current_burst += 1
            else:
                stats[last_sender]['bursts'].append(current_burst)
                diff = (curr['ts'] - wait_start_ts).total_seconds() / 60
                if 1 < diff < 240:
                    stats[s_name]['responses'].append(diff)
                    #print("Used: " + s_name + ", " + str(diff) + ": " + msg_text)
                else:
                    #print("Not used: " + s_name + ", " + str(diff) + ": " + msg_text + " (" + str(curr['ts']) + ")")
                    pass
                wait_start_ts = curr['ts']
                current_burst = 1
                last_sender = s_name
            last_ts = curr['ts']

        total_messages_chat = sum(s['msg_count'] for s in stats.values())

        # --- Output ---
        print("=" * 60)
        print(f"Chat Analyzer ({data[0]['ts'].date()} bis {data[-1]['ts'].date()})")
        print("=" * 60)

        for name, s in stats.items():
            if total_messages_chat > 0:
                speaking_time = (s['msg_count'] / total_messages_chat) * 100
            else:
                speaking_time = 0
            avg_msg_length = s['total_words'] / s['text_msg_count'] if s['text_msg_count'] > 0 else 0
            avg_resp = sum(s['responses']) / len(s['responses']) if s['responses'] else 0
            avg_burst = sum(s['bursts']) / len(s['bursts']) if s['bursts'] else 1
            top_emojis = "".join([e for e, count in s['emojis'].most_common(5)])

            top_words = ", ".join([f"{w} ({c}x)" for w, c in s['common_words'].most_common(10)])

            print(f"Name: {name}")
            print(f"  > Nachrichten: {s['msg_count']}")
            print(f"  > Redeanteil: {speaking_time:.1f}%")
            print(f"  > Ø Nachrichten am Stück: {avg_burst:.1f}")
            print(f"  > Ø Antwortzeit: {avg_resp:.1f} Min.")
            print(f"  > Ø Wortanzahl: {avg_msg_length:.1f} Wörter pro Nachricht")
            print(f"  > Benutze Zahlen: {s['number_count']}")
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

    def analyze_vocabulary(self, start_filter=None, end_filter=None):
        data = self._filter(start_filter, end_filter)
        nlp = self._get_nlp()
        if not data:
            print("Keine Nachrichten für die Wortschatz-Analyse gefunden.")
            return

        flood_pattern = re.compile(r'(.)\1{2,}')
        syllable_pattern = re.compile(r'(\w{2,3})\1{2,}')

        vocab_stats = defaultdict(lambda: {
            # Token level (without spaCy)
            'all_words': [],
            'unique_words': set(),
            'word_lengths': Counter(),
            # Lemma level (spaCy)
            'lemma_counts': Counter(),
            'recent_lemmas': set(),
        })

        msgs_per_sender = defaultdict(list)
        for m in data:
            msgs_per_sender[m['sender']].append(m['msg'])

        # --- Token stats (no spaCy needed) ---
        for m in data:
            s_name = m['sender']
            words = re.findall(r'\b[a-zA-ZäöüÄÖÜß]+\b', m['msg'].lower())
            for w in words:
                if not flood_pattern.search(w) and not syllable_pattern.search(w) and len(w) < 100:
                    vocab_stats[s_name]['all_words'].append(w)
                    vocab_stats[s_name]['unique_words'].add(w)
                    vocab_stats[s_name]['word_lengths'][len(w)] += 1

        # --- Lemma stats (one spaCy run per sender) ---
        nlp.max_length = 5_000_000
        for s_name, msgs in msgs_per_sender.items():
            recent_msgs = msgs[max(0, int(len(msgs) * 0.9)):]

            msgs_cleaned = [m[:1000] for m in msgs]
            recent_msgs_cleaned = [m[:1000] for m in recent_msgs]

            for doc in tqdm(nlp.pipe(msgs_cleaned, batch_size=256), total=len(msgs_cleaned), desc=f"Lemmata {s_name}"):
                for token in doc:
                    if token.is_alpha and not token.is_stop:
                        vocab_stats[s_name]['lemma_counts'][token.lemma_.lower()] += 1

            for doc in nlp.pipe(recent_msgs_cleaned, batch_size=128):
                for token in doc:
                    if token.is_alpha:
                        vocab_stats[s_name]['recent_lemmas'].add(token.lemma_.lower())

        # --- Output per person ---
        print("=" * 60)
        print("WORTSCHATZ-ANALYSE")
        print("=" * 60)

        for name, s in vocab_stats.items():
            total_tokens = len(s['all_words'])
            unique_tokens = len(s['unique_words'])
            ttr = (unique_tokens / total_tokens * 100) if total_tokens > 0 else 0
            avg_len = sum(k * v for k, v in s['word_lengths'].items()) / total_tokens if total_tokens > 0 else 0

            lemma_counts = s['lemma_counts']
            unique_lemmas = len(lemma_counts)
            total_lemmas = sum(lemma_counts.values())
            active_vocab = [l for l, c in lemma_counts.items() if c >= 5]
            retention = (len(set(lemma_counts) & s['recent_lemmas']) / unique_lemmas * 100) if unique_lemmas > 0 else 0

            # Heaps' Law: V = K * N^β  (K≈44, β≈0.67 for German)
            estimated_total = int(44 * (total_lemmas ** 0.67)) if total_lemmas > 0 else 0

            longest = sorted(s['unique_words'], key=len, reverse=True)[:5]
            top_lemmas = lemma_counts.most_common(5)

            print(f"Name: {name}")

            print(f"\n  [ Token-Ebene ]")
            print(f"  > Wörter gesamt:         {total_tokens}")
            print(f"  > Einzigartige Wörter:   {unique_tokens}")
            print(f"  > Wortschatz-Vielfalt:   {ttr:.2f}% TTR")
            print(f"  > Ø Buchstaben/Wort:     {avg_len:.2f}")
            print(f"  > Längste Wörter:        {', '.join(longest)}")
            print(f"  > Wortlängen-Profil:")
            for length in range(1, 11):
                count = s['word_lengths'][length]
                perc = (count / total_tokens * 100) if total_tokens > 0 else 0
                bar = "█" * int(perc / 2)
                print(f"    {length:>2} Bst.: {perc:>5.1f}% {bar}")

            print(f"\n  [ Lemma-Ebene (spaCy) ]")
            print(f"  > Einzigartige Grundformen:  {unique_lemmas}")
            print(f"  > Aktiver Wortschatz (≥5x):  {len(active_vocab)}")
            print(f"  > Wortschatz-Erhalt (10%):   {retention:.1f}%")
            print(f"  > Geschätzter Gesamtbesitz:  ~{estimated_total} Wörter")
            print(f"  > Top Grundformen:           {', '.join(f'{l} ({c}x)' for l, c in top_lemmas)}")
            print("-" * 40)

        # --- Overlap analysis (only for 2 people) ---
        senders = list(vocab_stats.keys())
        if len(senders) >= 2:
            u1, u2 = senders[0], senders[1]
            set1 = vocab_stats[u1]['unique_words']
            set2 = vocab_stats[u2]['unique_words']
            common = set1 & set2
            jaccard = len(common) / len(set1 | set2) * 100 if set1 | set2 else 0

            cnt1 = Counter(vocab_stats[u1]['all_words'])
            cnt2 = Counter(vocab_stats[u2]['all_words'])
            core = [w for w in common if cnt1[w] >= 5 and cnt2[w] >= 5 and w not in STOP_WORDS]

            print("=" * 60)
            print("WORTSCHATZ-ÜBERSCHNEIDUNG")
            print("=" * 60)
            print(f"  > Gemeinsame Wörter:    {len(common)}")
            print(f"  > Ähnlichkeits-Index:   {jaccard:.2f}% (Jaccard)")
            print(f"  > Kern-Wortschatz:      {len(core)} Wörter (beide ≥5x)")
            print(f"  > Beispiele:            {', '.join(sorted(core, key=len, reverse=True)[:10])}")

    def analyze_linguistic_style(self, start_filter=None, end_filter=None):
        data = self._filter(start_filter, end_filter)
        nlp = self._get_nlp()
        if not data:
            print("Keine Nachrichten für die  linguistische Analyse gefunden.")
            return

        # --- Prepare word_lists ---
        slang_words, slang_phrases = _split_list(youth_language)
        denglisch_words, denglisch_phrases = _split_list(denglisch)
        educated_words, educated_phrases = _split_list(educated_language)
        support_words, support_phrases = _split_list(supporting_language)
        self_words, self_phrases = _split_list(selfish_language)
        other_words, other_phrases = _split_list(other_language)

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

        # --- spaCy: Question recognition ---
        all_msgs_cleaned = [m['msg'][:1000] for m in data]
        results = []

        for doc in tqdm(nlp.pipe(all_msgs_cleaned, batch_size=128), total=len(all_msgs_cleaned), desc="Analyse"):
            has_question_mark = "?" in doc.text

            # Interrogative pronouns ONLY if they are the first substantive word.
            has_interrogative = (
                    len(doc) > 0 and
                    any(
                        t.morph.get("PronType") == ["Int"]
                        for t in doc[:3]
                    )
            )

            # Aauxiliary at the beginning + direct address
            verb_first_with_addressee = (
                    len(doc) > 0 and
                    doc[0].pos_ in ["VERB", "AUX"] and
                    any(t.text.lower() in {"du", "ihr", "sie", "dich", "dir"} for t in doc)
            )

            # German Question Day at the end ("...or?", "...or")
            has_oder_tag = len(doc) > 0 and doc[-1].text.lower() == "oder"

            results.append(
                has_question_mark or
                has_interrogative or
                verb_first_with_addressee or
                has_oder_tag
            )

        # --- Language Analyzation ---
        for i, m in enumerate(data):
            s_name = m['sender']
            msg_text = m['msg'].lower()
            words = re.findall(r'\b[a-zäöüß]+\b', msg_text)

            style_stats[s_name]['total_words'] += len(words)

            if results[i]:
                style_stats[s_name]['questions_asked'] += 1
                # print("Question:     " + m['msg'])
            else:
                # print("No Question:" + " " * 60 + m['msg'])
                pass

            # Word matching
            for w in words:
                if len(w) >= 10:           style_stats[s_name]['complex_words'] += 1
                if w in slang_words:       style_stats[s_name]['slang_hits'] += 1
                if w in denglisch_words:   style_stats[s_name]['denglisch_hits'] += 1
                if w in educated_words:    style_stats[s_name]['educated_hits'] += 1
                if w in support_words:     style_stats[s_name]['support_hits'] += 1
                if w in self_words:        style_stats[s_name]['self_hits'] += 1
                if w in other_words:       style_stats[s_name]['other_hits'] += 1
                #if w in other_words:     print(s_name + ": " + m['msg'] + "     -->" + w)

            # Phrase matching
            for p in slang_phrases:
                if p in msg_text: style_stats[s_name]['slang_hits'] += 1
            for p in denglisch_phrases:
                if p in msg_text: style_stats[s_name]['denglisch_hits'] += 1
            for p in educated_phrases:
                if p in msg_text: style_stats[s_name]['educated_hits'] += 1
            for p in support_phrases:
                if p in msg_text: style_stats[s_name]['support_hits'] += 1
            for p in self_phrases:
                if p in msg_text: style_stats[s_name]['self_hits'] += 1
            for p in other_phrases:
                if p in msg_text: style_stats[s_name]['other_hits'] += 1

        # --- Output ---
        print("=" * 60)
        print("LINGUISTISCHES & PSYCHOLOGISCHES PROFIL")
        print("=" * 60)

        for name, s in style_stats.items():
            tw = s['total_words'] if s['total_words'] > 0 else 1
            msg_count = sum(1 for m in data if m['sender'] == name)

            pct = lambda x: (x / tw) * 100

            print(f"Name: {name}")
            print(f"\n  [ Sprach-Stil (Anteil am Wortschatz) ]")
            print(f"  > Slang/Jugendsprache: {pct(s['slang_hits']):.2f}%")
            print(f"  > Denglisch:           {pct(s['denglisch_hits']):.2f}%")
            print(f"  > Gehobene Sprache:    {pct(s['educated_hits']):.2f}%")
            print(f"  > Komplexe Wörter:     {(s['complex_words'] / tw * 100):.1f}%")

            print(f"\n  [ Beziehungs-Dynamik ]")
            ego_ratio = s['self_hits'] / s['other_hits'] if s['other_hits'] > 0 else 0
            focus = "Selbst-Fokus" if ego_ratio > 1.2 else "Du-Fokus" if ego_ratio < 0.8 else "Ausgeglichen"
            print(f"  > Ich-Bezug:           {pct(s['self_hits']):.2f}% aller Wörter")
            print(f"  > Du-Bezug:            {pct(s['other_hits']):.2f}% aller Wörter")
            print(f"  > Fokus-Index:         {ego_ratio:.2f} ({focus})")
            print(f"  > Support/Lob-Wörter:  {pct(s['support_hits']):.2f}%")

            print(f"\n  [ Gesprächsführung ]")

            q_rate = (s['questions_asked'] / msg_count * 100) if msg_count > 0 else 0
            print(f"  > Fragen-Quote:        {q_rate:.1f}% aller Nachrichten")
            print("-" * 50)

    def analyze_emojis(self, start_filter=None, end_filter=None):
        data = self._filter(start_filter, end_filter)
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
            found = [e['emoji'] for e in emoji.emoji_list(m['msg'])]

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

    def check_occurrence(self, required_groups, excluded_terms=None, start_filter=None, end_filter=None,
                         output_occurrence=False):
        data = self._filter(start_filter, end_filter)
        if not data:
            print("Keine Daten im gewählten Zeitraum gefunden.")
            return

        excluded_terms = [t.lower() for t in (excluded_terms or [])]
        results = defaultdict(lambda: {
            'total_count': 0,
            'msg_with_term': 0,
            'total_msg_sender': 0,
            'hits_by_term': defaultdict(int)
        })

        for m in data:
            results[m['sender']]['total_msg_sender'] += 1

        for m in data:
            msg_lower = m['msg'].lower()
            s_name = m['sender']

            if any(bad_word in msg_lower for bad_word in excluded_terms):
                continue

            group_matches = []
            temp_term_counts = defaultdict(int)

            for group in required_groups:
                current_group_hits = 0
                for term in group:
                    t_lower = term.lower()
                    count = msg_lower.count(t_lower)
                    if count > 0:
                        current_group_hits += count
                        temp_term_counts[term] += count
                group_matches.append(current_group_hits)

            if all(hits > 0 for hits in group_matches):
                results[s_name]['total_count'] += sum(group_matches)
                results[s_name]['msg_with_term'] += 1

                for term, count in temp_term_counts.items():
                    results[s_name]['hits_by_term'][term] += count

                if output_occurrence:
                    print(f"[TREFFER] {s_name}: {m['msg']}")

        print("=" * 60)
        print("ERWEITERTE TEXT-ANALYSE")
        print("=" * 60)
        logic_str = " UND ".join([f"({'|'.join(g)})" for g in required_groups])
        print(f"LOGIK: {logic_str[:60]:<60} ")
        if excluded_terms:
            print(f"AUSSCHLUSS (NOT): {', '.join(excluded_terms)[:51]:<51}")
        print(f"ZEITRAUM: {data[0]['ts'].date()} bis {data[-1]['ts'].date()}")
        print("=" * 60)

        sorted_senders = sorted(results.items(), key=lambda x: x[1]['msg_with_term'], reverse=True)

        for name, stats in sorted_senders:
            if stats['msg_with_term'] == 0: continue

            quota = (stats['msg_with_term'] / stats['total_msg_sender']) * 100
            avg_intensity = stats['total_count'] / stats['msg_with_term']

            print(f"👤 ANALYSE FÜR SENDER: {name.upper()}")
            print(
                f"  ├─ Nachrichtenfokus: {stats['msg_with_term']} von {stats['total_msg_sender']} gesamt ({quota:.2f}%)")
            print(f"  ├─ Trefferdichte:    {stats['total_count']} Wörter gesamt")
            print(f"  ├─ Ø Intensität:     {avg_intensity:.2f} Begriffe pro Treffer-Nachricht")

            top_words = sorted(stats['hits_by_term'].items(), key=lambda x: x[1], reverse=True)[:3]
            word_str = ", ".join([f"{w} ({c}x)" for w, c in top_words])
            print(f"  └─ Top-Begriffe:     {word_str}")


# --- Calls ---
# Example:
# chat = ChatAnalyzer('input/chat.txt')

# chat.analyze_chat()
# chat.analyze_vocabulary()
# chat.analyze_linguistic_style()
# chat.analyze_emojis()

# check_occurrence(["Hey", "Hi", "Hello"])

# chat.check_occurrence(["Good Night", "gn"], output_occurrence=True, start_filter=datetime(2024, 12, 21), end_filter=datetime(2025, 11, 5))
# analyze_chat('input/chat.txt', start_filter=datetime(2023, 4, 23), end_filter=datetime(2025, 1, 1))

if __name__ == '__main__':
    chat = ChatAnalyzer('input/chat.txt')

    #chat.analyze_chat()
    #chat.analyze_vocabulary()
    #chat.analyze_linguistic_style()
    #chat.analyze_emojis()

    chat.check_occurrence([[""], ["nacht"]], ["abc"], output_occurrence=True, start_filter=datetime(2022, 4,28), end_filter=datetime(2026, 5, 6))

    #chat.analyze_chat(start_filter=datetime(2026, 5,6), end_filter=datetime(2026, 5, 7))

#TODO Add image voice message analyzer (how often)
# veränderung der werte in monats schritten
# diagramm der nachrichten
# wer benutzt mehr zahlen

#FRAGEN
#Wie gut ist mein Code? Gibt es logische Fehler?
#Sollte ich die Ignoranz von Medien wieder wegmachen (würde die Wörter- und Nachrichtenanalyse beeinflussen, aber dafür die Gesamtanzahl an Nachrichten  und die Zeit bis zur Antwort genauer machen)?
#Sind die Werte, die ich per Spacy, Matheformeln und Analysen ermittle, realitätsnah?
#Was sollte ich noch hinzufügen?

#Medien-Nachrichten ignorieren
#Ja, du solltest sie ignorieren – aber differenzierter. Aktuell ignorierst du sie komplett. Besser: Beim Parsen ein Flag setzen:
#pythoncurrent_msg = {
#    ...
#    'is_media': any(p in msg for p in omitted_patterns)
#}
#Dann kannst du je nach Analyse entscheiden:
#
#analyze_chat → Medien mitzählen (genauere Nachrichtenanzahl & Antwortzeiten)
#analyze_vocabulary / analyze_linguistic_style → Medien ausschließen

#Antwortzeiten: Der 1 < diff < 240-Filter ist gut gemeint, aber 4 Stunden als Grenze ist willkürlich. Besser wäre es, das pro Tageszeit zu gewichten oder nur Nachrichten innerhalb derselben „Session" zu zählen.
#Ego-Ratio: Der Selbst-/Fremdbezug ist methodisch sinnvoll, aber mit 639 Einträgen in external_reference_words wie vorhin besprochen unsicher.

#Was noch hinzufügen?
#Du hast selbst gute TODOs. Konkret umsetzbar wären:
#
#Monatliche Verlaufskurve – für msg_count, avg_response_time, question_rate. Zeigt Beziehungsdynamik über Zeit sehr deutlich.
#Initiativ-Analyse – wer startet Gespräche (erste Nachricht nach >2h Pause)?
#Stimmungs-Trend – kombiniere support_hits, self_hits, Emoji-Dichte zu einem einfachen Positivity-Score.
#Medien-Zählung – wie viele Bilder/Voice Messages hat wer geschickt? Ist ein einfacher Counter beim Parsen.