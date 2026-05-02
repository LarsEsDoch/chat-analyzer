import re
from collections import Counter, defaultdict
from datetime import datetime
import emoji

def analyze_chat_final(file_path, start_filter=None, end_filter=None):
    pattern = re.compile(r'^(\d{1,2}/\d{1,2}/\d{2,4},\s\d{2}:\d{2})\s-\s([^:]+短):\s(.+)$')
    # Falls das obige Pattern bei Namen mit Emojis hakt, hier die robustere Version:
    pattern = re.compile(r'^(\d{1,2}/\d{1,2}/\d{2,4},\s\d{2}:\d{2})\s-\s([^:]+):\s(.+)$')

    data = []

    # Standardwerte setzen, falls nichts angegeben wurde
    if start_filter is None:
        start_filter = datetime.min
    if end_filter is None:
        end_filter = datetime.max

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                match = pattern.match(line.strip())
                if match:
                    ts_str, sender, msg = match.groups()
                    try:
                        ts = datetime.strptime(ts_str, '%m/%d/%y, %H:%M')
                    except ValueError:
                        ts = datetime.strptime(ts_str, '%m/%d/%Y, %H:%M')

                    # --- FILTER LOGIK ---
                    if start_filter <= ts <= end_filter:
                        data.append({
                            'ts': ts,
                            'sender': sender.strip(),
                            'msg': msg.strip(),
                            'hour': ts.hour
                        })

        if not data:
            print(f"Keine Nachrichten im Zeitraum {start_filter.date()} bis {end_filter.date()} gefunden.")
            return

        # --- Statistiken (Rest bleibt wie gehabt) ---
        stats = defaultdict(lambda: {
            'msg_count': 0, 'total_words': 0, 'responses': [],
            'time_slots': Counter(), 'emojis': Counter(), 'bursts': []
        })

        current_burst = 0
        last_sender = data[0]['sender']
        last_ts = data[0]['ts']

        for i, curr in enumerate(data):
            s_name = curr['sender']
            msg_text = curr['msg']

            stats[s_name]['msg_count'] += 1
            stats[s_name]['total_words'] += len(msg_text.split())

            if 6 <= curr['hour'] < 12: slot = "Morgen (06-12)"
            elif 12 <= curr['hour'] < 18: slot = "Mittag/Nachm. (12-18)"
            elif 18 <= curr['hour'] < 23: slot = "Abend (18-23)"
            else: slot = "Nacht (23-06)"
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

        # --- Ausgabe ---
        print("=" * 60)
        print(f"Chat Analyzer ({start_filter.date()} bis {end_filter.date()})")
        print("=" * 60)

        for name, s in stats.items():
            avg_resp = sum(s['responses']) / len(s['responses']) if s['responses'] else 0
            avg_burst = sum(s['bursts']) / len(s['bursts']) if s['bursts'] else 1
            top_emojis = "".join([e for e, count in s['emojis'].most_common(5)])

            print(f"Name: {name}")
            print(f"  > Nachrichten: {s['msg_count']}")
            print(f"  > Ø Nachrichten am Stück: {avg_burst:.1f}")
            print(f"  > Ø Antwortzeit: {avg_resp:.1f} Min.")
            print(f"  > Top Emojis: {top_emojis if top_emojis else 'Keine'}")
            print(f"  > Zeitliche Verteilung:")
            for slot, count in sorted(s['time_slots'].items()):
                perc = (count / s['msg_count']) * 100
                print(f"    - {slot:<18}: {perc:>5.1f}% ({count} Nachrichten)")
            print("-" * 40)

    except FileNotFoundError:
        print("Datei nicht gefunden.")


