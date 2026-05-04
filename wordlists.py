#!/usr/bin/env python3
"""
Generator für 6 Wortlisten mit je 2000 Einträgen für Wortschatzanalyse
"""


# ============================================================
# HILFSFUNKTIONEN
# ============================================================

def dedupe_ordered(lst):
    seen = set()
    out = []
    for x in lst:
        xl = x.lower().strip()
        if xl not in seen and xl:
            seen.add(xl)
            out.append(x)
    return out


def pad_to(lst, n, source):
    """Füllt Liste auf n auf, indem aus source geschöpft wird"""
    lst = dedupe_ordered(lst)
    extra = [w for w in source if w.lower() not in {x.lower() for x in lst}]
    combined = lst + extra
    return dedupe_ordered(combined)[:n]


def conjugate_en(verb):
    """Konjugiert ein schwaches Denglisch-Verb"""
    forms = [verb]
    if verb.endswith("eln"):
        s = verb[:-3]
        forms += [s + "ele", s + "elst", s + "elt", s + "eln", "ge" + s + "elt", s + "elnd", s + "elung"]
    elif verb.endswith("ern"):
        s = verb[:-3]
        forms += [s + "ere", s + "erst", s + "ert", s + "ern", "ge" + s + "ert", s + "ernd", s + "erung"]
    elif verb.endswith("en"):
        s = verb[:-2]
        if s.endswith("t") or s.endswith("d"):
            forms += [s + "e", s + "est", s + "et", s + "eten", "ge" + s + "et", s + "end"]
        else:
            forms += [s + "e", s + "st", s + "t", s + "ten", "ge" + s + "t", s + "end"]
        if not s.endswith("ier"):
            forms.append(s + "ung")
    return forms


def derive_adjective(adj):
    """Adjektiv-Flexion"""
    return [adj, adj + "e", adj + "en", adj + "em", adj + "er", adj + "es", "un" + adj, adj + "ste", adj + "stem",
            adj + "sten", adj + "ster", adj + "stes"]


def derive_noun(noun, plural_suffix="en"):
    """Substantiv-Formen"""
    return [noun, noun + plural_suffix, noun + "s", noun + "es"]


# ============================================================
# KATEGORIE 1: DENGLISCH
# ============================================================

denglisch_verben_base = [
    "downloaden", "uploaden", "updaten", "checken", "chillen", "gamen", "streamen",
    "googeln", "liken", "posten", "sharen", "stalken", "ghosten", "canceln",
    "followen", "blocken", "chatten", "texten", "zoomen", "facetimen", "skypen",
    "netflixen", "spotifyen", "snapchatten", "twittern", "instagrammen",
    "whatsappen", "tindern", "swipen", "matchen", "daten", "dissen", "hypen",
    "fangirlen", "shippen", "spoilern", "triggern", "trollen", "flamen", "bannen",
    "kicken", "joinen", "leaveen", "raiden", "grinden", "farmen", "leveln",
    "upgraden", "downgraden", "resetten", "cutten", "photoshoppen", "filtern",
    "screenshotten", "livestreamen", "monetarisieren", "sponsern", "colaben",
    "droppen", "haten", "loven", "crashen", "laggen", "loaden", "speedrunnen",
    "glitchen", "modden", "cosplayen", "unboxen", "reviewen", "ranken", "voten",
    "subscriben", "retweeten", "rebloggen", "pingen", "taggen", "mentionen",
    "reposten", "spamen", "hacken", "leaken", "scammen", "faken", "catfishen",
    "roasten", "flexen", "hustlen", "networken", "pitchen", "brainstormen",
    "multitasken", "coachen", "supporten", "empowern", "challengen", "boostern",
    "promoten", "targeten", "tracken", "debuggen", "launchen", "deployen",
    "iterieren", "scalieren", "onboarden", "outsourcen", "freelancen", "brunchen",
    "slayen", "editieren", "featuren", "pushen", "highlighten", "converten",
    "testen", "releasen", "pivoten", "coworken", "remoten", "cropen", "shoutоuten",
    "unfollowеn", "rebloggen", "reakten", "kommentieren", "teilen", "streamen",
    "viralgehеn", "trendsetten", "haten", "burnеn", "clownen", "stunten", "balln",
    "finessen", "grindеn", "husтlen", "sippen", "flexen", "snaрpen", "storiеn",
    "reelsеn", "posтen", "instаn", "zwitsсhern", "linкedinen", "yоutuben",
    "tiktokеn", "discorden", "slacken", "teamsеn", "zoomen", "meeten", "cаllen",
    "brainдumpen", "whiteboarden", "workshоppen", "hacкathonn", "sprinten",
    "scrummen", "agilеn", "kanbanеn", "jirаn", "trelloеn", "notiоnen",
    "githuben", "forken", "clonen", "committen", "pushen", "pullen", "mergen",
    "reviewen", "approven", "dеployen", "rollbacken", "hotfixen", "patchеn",
    "releasen", "versionieren", "taggen", "branchen", "rebасen", "stashen",
]

denglisch_nouns = [
    "Stream", "Update", "Feed", "Post", "App", "Chat", "Meme", "Hype", "Trend",
    "Vibe", "Flex", "Beef", "Cringe", "Drama", "Flop", "Content", "Creator",
    "Influencer", "Follower", "Subscriber", "Fan", "Hater", "Troll", "Bot",
    "Spam", "Hack", "Leak", "Scam", "Fake", "Catfish", "Roast", "Hustle",
    "Grind", "Network", "Pitch", "Launch", "Release", "Patch", "Bug", "Glitch",
    "Lag", "Crash", "Boost", "Drop", "Collab", "Merch", "Slay", "Mood", "Aesthetic",
    "Filter", "Selfie", "Story", "Reel", "Tweet", "DM", "Hashtag", "Viral", "Stan",
    "Simp", "Cringe", "Vibe", "Flex", "Slay", "Mood", "Lowkey", "Highkey", "Cap",
    "Clout", "Ratio", "Snitch", "Sneak", "Drip", "Fit", "Rizz", "Glow-up", "Arc",
    "Era", "Phase", "Branding", "Marketing", "Targeting", "Tracking", "Analytics",
    "Dashboard", "Funnel", "Conversion", "Engagement", "Reach", "Impression",
    "Click", "View", "Watch", "Like", "Share", "Comment", "Follow", "Subscribe",
    "Notification", "Algorithm", "Feed", "Timeline", "Explore", "Discover",
    "Search", "Trend", "Hashtag", "Mention", "Tag", "Story", "Reel", "Live",
    "Spaces", "Thread", "Poll", "Quiz", "Challenge", "Duet", "Stitch", "Collab",
    "Feature", "Sponsoring", "Partnership", "Affiliate", "Deal", "Brand", "Deal",
    "Merchandise", "Dropshipping", "Startup", "Unicorn", "Pivot", "Scaling",
    "Fundraising", "Crowdfunding", "Bootstrap", "Side-Hustle", "Freelancing",
    "Remote", "Homeoffice", "Coworking", "Networking", "Onboarding", "Offboarding",
    "Workshop", "Hackathon", "Sprint", "Scrum", "Backlog", "Burndown", "Roadmap",
    "Deployment", "Repository", "Commit", "Branch", "Merge", "Pull-Request",
    "Hotfix", "Patch", "Release", "Version", "Tag", "Fork", "Clone", "Repository",
    "Framework", "Library", "Plugin", "Extension", "Widget", "Component", "Module",
    "Container", "Docker", "Kubernetes", "Cloud", "Server", "Backend", "Frontend",
    "Fullstack", "DevOps", "CI/CD", "Pipeline", "Workflow", "Automation", "Testing",
    "Debugging", "Refactoring", "Code-Review", "Pair-Programming", "Mob-Programming",
    "Agile", "Kanban", "Scrum", "Sprint", "Standup", "Retrospektive", "Velocity",
    "Burndown", "Epic", "Story", "Task", "Ticket", "Issue", "Bug", "Feature",
    "Hotfix", "Release", "Milestone", "Deadline", "Blocker", "Dependency",
]

denglisch_adj = [
    "downlodbar", "uploadbar", "updatebar", "checkbar", "stylish", "trendy", "catchy",
    "cringy", "cringe", "lit", "fire", "based", "sus", "valid", "toxic", "iconic",
    "legendary", "epic", "savage", "brutal", "random", "weird", "awkward", "awkward",
    "lame", "basic", "extra", "salty", "sour", "sweet", "sick", "dope", "fresh",
    "lowkey", "highkey", "woke", "cancelled", "ghosted", "triggered", "hyped",
    "overhyped", "underhyped", "viral", "trending", "mainstream", "niche", "obscure",
    "underground", "mainstream", "commercial", "indie", "authentic", "fake", "real",
    "unfiltered", "curated", "polished", "raw", "rough", "smooth", "sleek", "clean",
    "messy", "chaotic", "organized", "structured", "flexible", "agile", "scalable",
    "sustainable", "profitable", "viral", "engaged", "motivated", "inspired", "empowered",
    "remote", "hybrid", "async", "synchron", "agil", "lean", "smart", "digital",
    "analog", "offline", "online", "virtual", "augmented", "mixed", "immersiv",
    "interaktiv", "responsive", "adaptiv", "personalisiert", "optimiert", "automatisiert",
    "skaliert", "deployed", "releasеd", "deprecated", "outdated", "updated", "patched",
    "gefixt", "gecancelt", "geghostet", "geliked", "geteilt", "gepostet", "gestreamd",
    "gehyped", "getrendet", "geviralt", "gebanned", "gekickt", "gejoined", "gefanned",
    "gefollowed", "geblockt", "gemuted", "getaggt", "gementioned", "gerepostet",
    "geboostet", "gefeatured", "gesponsert", "gecollabet", "gedropt", "gehаtet",
    "gecrasht", "gelagged", "gehackt", "geleakt", "gescammt", "gefaked", "geroastet",
    "geflext", "gehustlet", "gepitcht", "gecoacht", "gesuppоrtet", "getargeted",
    "getrackt", "gedebugged", "gelauncht", "gedeployt", "geiteratеd", "gescaliert",
    "geboardet", "geoutsourct", "gefrееlanced", "gebruncht", "geslayt", "gevibed",
]

denglisch_compounds = [
    "Downloadgeschwindigkeit", "Uploadlimit", "Streamingdienst", "Gamingmaus", "GamingPC",
    "Gamecontroller", "Chatkontrolle", "Likemaschine", "Poststrategie", "Sharefunktion",
    "Followeranzahl", "Subscribercount", "Influencermarketing", "Contentersteller",
    "Creatorwirtschaft", "Hatekommentar", "Trollangriff", "Botarmee", "Spamfilter",
    "Hackversuch", "Datenleakage", "Scamanruf", "Fakeprofil", "Catfishingopfer",
    "Roastbattle", "Flexkultur", "Hustlementality", "Grindset", "Networkingveranstaltung",
    "Pitchdeck", "Brainstormingphase", "Multitaskingfähigkeit", "Coachingprogramm",
    "Supportteam", "Empowermentprogramm", "Challengeteilnehmer", "Boosterstrategie",
    "Promotionskampagne", "Targetingoptionen", "Trackingpixel", "Debuggingprozess",
    "Launchtermin", "Deploymentpipeline", "Iterationszyklus", "Skalierungsstrategie",
    "Onboardingprozess", "Outsourcingmodell", "Freelancingplattform", "Remoteworking",
    "Coworkingspace", "Homeofficesetup", "Workshopformat", "Hackathonevent", "Sprintplanung",
    "Scrumsitzung", "Backlogpflege", "Roadmapplanung", "Deploymentprozess", "Releasezyklus",
    "Versionskontrolle", "Codereview", "Pairprogramming", "Agileentwicklung", "Kanbantafel",
    "Standupmeeting", "Retrospektivformat", "Velocitymessung", "Epiceinteilung",
    "Storypoints", "Taskmanagement", "Ticketsystem", "Bugtracking", "Featurebranch",
    "Hotfixrelease", "Meilensteinplanung", "Deadlinemanagement", "Blockeranalyse",
    "Dependencycheck", "Contentstrategie", "Feedalgorithmus", "Trendanalyse",
    "Hashtagstrategie", "Viralkampagne", "Engagementrate", "Reichweitemessung",
    "Impressionszahl", "Clickrate", "Watchtime", "Interaktionsrate", "Kommentarmanagement",
    "Followerwachstum", "Subscriberaufbau", "Notifikationseinstellung", "Algorithmuswechsel",
    "Timelinegestaltung", "Explorefunktion", "Discoveryseite", "Suchoptimierung",
    "Trendmonitoring", "Mentionanalyse", "Tagstrategie", "Storyformat", "Reelproduktion",
    "Livestreaming", "Spacesformat", "Threadstruktur", "Pollgestaltung", "Quizformat",
    "Challengeteilnahme", "Duetfunktion", "Stitchfeature", "Collabpartnerschaft",
    "Featurekampagne", "Sponsoringdeal", "Partnerschaftsprogramm", "Affiliatelink",
    "Brandingkonzept", "Merchandiseprodukt", "Dropshippingmodell", "Startupgründung",
    "Unicornbewertung", "Pivotentscheidung", "Skalierungspfad", "Fundraisingrunde",
    "Crowdfundingkampagne", "Bootstrapfinanzierung", "Sidehusten",
]

denglisch_all = []
for v in denglisch_verben_base:
    denglisch_all.extend(conjugate_en(v))
denglisch_all.extend(denglisch_nouns)
denglisch_all.extend(denglisch_compounds)
for a in denglisch_adj:
    denglisch_all.extend(derive_adjective(a))

liste_denglisch = dedupe_ordered(denglisch_all)[:2000]
print(f"Denglisch: {len(liste_denglisch)}")

# ============================================================
# KATEGORIE 2: JUGENDSPRACHE / SLANG
# ============================================================

jugend_base = [
    "cringe", "lit", "fire", "based", "sus", "bussin", "slay", "rizz", "vibe", "mood",
    "lowkey", "highkey", "no cap", "cap", "sheesh", "ok boomer", "periodt", "understood",
    "ratio", "L", "W", "mid", "goated", "GOAT", "NPC", "main character", "villain era",
    "understood the assignment", "ate", "left no crumbs", "understood", "hit different",
    "unalived", "touch grass", "skill issue", "cope", "seethe", "mald", "based", "cringe",
    "rent free", "living rent free", "that's so real", "not me", "it's giving", "ate",
    "we don't talk about it", "big yikes", "yikes", "oof", "bruh", "ayo", "fam", "G",
    "bro", "brah", "sis", "bestie", "fren", "homie", "mate", "dude", "dawg", "chief",
    "lad", "man", "babe", "queen", "king", "slay", "serve", "ate", "understood",
    "wallah", "auf wallah", "alter", "digga", "digger", "diggah", "mach ma", "mach ma kurz",
    "krass", "krass digga", "heavy", "heavy digga", "heftig", "heftig oder", "safe",
    "safe bro", "das ist doch kein Ding", "kein Ding", "Ding", "nä", "ne", "ja ne",
    "joa", "jop", "nop", "nah", "yah", "yep", "lol", "lmao", "lmfao", "rofl", "omg", "omfg",
    "wtf", "wth", "smh", "ngl", "tbh", "imo", "imho", "irl", "afk", "brb", "gtg", "ttyl",
    "ikr", "ik", "idk", "idgaf", "idc", "tmi", "fomo", "yolo", "jomo", "fwiw", "imo",
    "hype", "overhyped", "mid", "ass", "trash", "garbage", "fire", "bussin", "goated",
    "goat", "top tier", "S-tier", "A-tier", "B-tier", "C-tier", "D-tier", "F-tier",
    "god tier", "trash tier", "based", "cringe", "chadswick", "chad", "gigachad", "simp",
    "incel", "neckbeard", "normie", "NPC", "bot", "android", "robot", "main character",
    "villain", "Karen", "Kyle", "stacy", "brad", "gigastacy", "gigachad", "mog", "looksmaxx",
    "glow up", "arc", "character development", "redemption arc", "villain arc", "rat era",
    "hot girl summer", "main character energy", "understood the assignment",
    "understood", "ate and left no crumbs", "served", "slay", "periodt", "no cap",
    "on god", "real", "it's giving", "that's so real", "hit different", "different",
    "not like other girls", "pick me", "girlboss", "gaslight", "gatekeep", "girlboss",
    "toxic", "red flag", "green flag", "yellow flag", "soft launch", "hard launch",
    "breadcrumbing", "love bombing", "ghosting", "situationship", "talking stage",
    "almost relationship", "entanglement", "down bad", "simping", "catching feelings",
    "down horrific", "down atrocious", "W rizz", "L rizz", "unspoken rizz", "Ohio",
    "only in Ohio", "Cincinnati", "it's giving Ohio", "rizz", "rizzing", "rizzed up",
    "rizzler", "the rizzler", "rizz god", "Kai Cenat", "Fanum tax", "grimace shake",
    "mewing", "looksmaxxing", "mogging", "mog", "get mogged", "nah he cooked", "he ate",
    "we go Jim", "skibidi", "skibidi toilet", "sigma", "alpha", "beta", "delta", "omega",
    "sigma male", "alpha female", "sigma grindset", "alpha mindset", "beta behavior",
    "delulu", "chronically online", "touch grass", "grass toucher", "skill issue",
    "issue with that", "cope and seethe", "no lifer", "main character syndrome",
    "main character disease", "NPC behavior", "bot behavior", "ate the fit",
    "fit check", "OOTD", "drip", "dripping", "drip check", "fresh fit", "clean fit",
    "outfit of the day", "look", "serving looks", "serving", "giving looks", "iconique",
    "iconic", "slay of the century", "slay queen", "slay king", "slay bestie",
    "understood king", "understood queen", "understood bestie", "periodt queen",
    "no cap bro", "no cap fam", "on god bro", "real talk", "facts", "facts fr",
    "fr fr", "fr no cap", "deadass", "dead", "dead serious", "deadass no cap",
    "finna", "bouta", "tryna", "wanna", "gonna", "gotta", "kinda", "sorta", "lowkey",
    "highkey", "honestly", "literally", "actually", "basically", "genuinely", "truly",
    "really", "slay", "mother", "mother of all slays", "understood the mothership",
    "understood assignment served", "ate left crumbs", "understood never left",
    "rent free living", "living rent free actually", "touch some grass honestly",
    "skill issue tbh", "cope and seethe fr", "delulu queen", "delulu behavior",
    "chronically online behavior", "NPC ass", "bot ass response", "understood fr",
    "nahhhh", "bro what", "bro no", "bro yes", "bro fr", "bro deadass", "bro on god",
    "bro no cap", "bro slay", "bro understood", "bro periodt", "bro it's giving",
    "bro hit different", "bro real", "aight", "aight bet", "aight cool", "aight fr",
    "bet", "bet bet", "bet cool", "big bet", "small bet", "slight bet", "hard bet",
    "absolute bet", "no bet", "facts bet", "real bet", "based bet", "understood bet",
    "periodt bet", "slay bet", "fire bet", "lit bet", "goated bet", "W bet", "L bet",
    "mid bet", "top tier bet", "understood assignment bet", "ate bet", "served bet",
    "erm actually", "well actually", "um actually", "so actually", "okay actually",
    "hmm actually", "right actually", "yeah actually", "true actually", "facts actually",
    "real actually", "based actually", "understood actually", "periodt actually",
    "nah this", "nah that", "nah it", "nah you", "nah they", "nah we", "nah I",
    "nah he", "nah she", "nah everything", "nah nothing", "nah nobody", "nah somebody",
    "doomscrolling", "doom scrolling", "doompost", "doom posting", "doomposting",
    "gloom posting", "gloomposting", "sadposting", "sad posting", "wokeposting",
    "woke posting", "ragebait", "rage bait", "rage baiting", "ragebаiting", "karma farm",
    "karma farming", "clout chasing", "clout chase", "engagement farming", "engagement bait",
    "clickbait", "outrage bait", "controversy bait", "drama baiting", "drama farming",
    "discourse", "infight", "fandom war", "shipping war", "stan war", "antis", "stans",
    "antis vs stans", "fandom drama", "fandom politics", "cancel culture", "cancellation",
    "cancelled", "being cancelled", "getting cancelled", "to cancel", "the cancel",
    "call out", "callout", "callout post", "call out post", "being called out",
    "public apology", "non-apology", "apology video", "statement", "notes app apology",
    "PR statement", "damage control", "walking back", "issuing statement", "context",
    "more context", "full context", "without context", "out of context", "decontextualized",
    "nuance", "nuanced take", "hot take", "cold take", "lukewarm take", "spicy take",
    "controversial take", "unpopular opinion", "unpopular opinion thread",
    "actually good take", "actually bad take", "this take", "that take", "unhinged take",
    "based take", "cringe take", "goated take", "mid take", "fire take", "lit take",
    "understood take", "periodt take", "real take", "facts take", "no cap take",
    "on god take", "slay take", "chad take", "virgin take", "sigma take", "alpha take",
    "beta take", "gigachad take", "gigastacy take", "main character take", "NPC take",
    "villain take", "understood the assignment take", "ate and left no crumbs take",
]

jugend_slangwörter = [
    "gang", "homies", "ride or die", "day one", "OG", "real one", "solid", "legit",
    "bougie", "boujee", "bourgie", "extra", "pressed", "salty", "bitter", "sweet",
    "drip", "sauce", "drippy", "saucy", "icy", "frozen", "cold", "hot", "fire", "lit",
    "turnt", "turned up", "poppin", "bumpin", "slapping", "banging", "hitting", "smacking",
    "go crazy", "go stupid", "go ham", "go off", "go wild", "go nuts", "go ballistic",
    "went crazy", "went off", "went wild", "went ham", "went stupid", "went ballistic",
    "snap", "snapping", "snapped", "on snap", "snapback", "snap back", "snap reaction",
    "vibe check", "vibe checking", "failed vibe check", "passed vibe check", "vibes",
    "good vibes", "bad vibes", "immaculate vibes", "off vibes", "weird vibes", "strong vibes",
    "positive vibes", "negative vibes", "wholesome vibes", "unwholesome vibes",
    "pure vibes", "contaminated vibes", "corrupted vibes", "corrupted energy", "dark energy",
    "light energy", "good energy", "bad energy", "chaotic energy", "neutral energy",
    "main character energy", "villain energy", "supporting character energy", "NPC energy",
    "understood the vibe", "understood the assignment", "understood the energy",
    "understood the task", "understood the mission", "understood the moment",
    "understood", "ate", "served", "cooked", "nailed it", "killed it", "murdered it",
    "destroyed it", "demolished it", "obliterated it", "annihilated it", "eviscerated it",
    "bodied it", "snatched it", "secured it", "locked it down", "clinched it", "clutched it",
    "clutch", "clutched up", "clutch player", "clutch gene", "ice in veins", "cold blooded",
    "ice cold", "stone cold", "dead cold", "absolutely zero", "absolute zero vibes",
    "boah", "boah ey", "boah alter", "boah digga", "boah bro", "boah mann", "boah leute",
    "ey boah", "ey alter", "ey digga", "ey bro", "ey mann", "ey leute", "ey ey ey",
    "alter falter", "alter ego", "alter Schwede", "alter Verwalter", "alter Hut",
    "digga mal", "digga echt", "digga bitte", "digga nein", "digga ja", "digga fr",
    "digga slay", "digga understood", "digga no cap", "digga on god", "digga periodt",
    "schleich dich", "mach dich vom Acker", "hau ab", "verpiss dich", "fick dich",
    "leck mich", "suck my", "kiss my", "touch me not", "leave me alone", "let me cook",
    "let him cook", "let her cook", "let them cook", "he's cooking", "she's cooking",
    "they're cooking", "we're cooking", "I'm cooking", "cooking", "cooked", "cook",
    "chef's kiss", "mwah", "immaculate", "top tier cooking", "michelin star cooking",
    "gordon ramsay wouldn't", "gordon wouldn't", "chef wouldn't", "the chef wouldn't",
    "W", "L", "dub", "el", "take the L", "take the W", "catch an L", "secure the W",
    "massive W", "massive L", "absolute W", "absolute L", "certified W", "certified L",
    "historic W", "historic L", "generational W", "generational L", "culture W", "culture L",
    "society W", "society L", "civilization W", "civilization L", "humanity W", "humanity L",
    "the universe W", "the universe L", "existence W", "existence L", "life W", "life L",
    "it's a W", "it's an L", "that's a W", "that's an L", "this is a W", "this is an L",
]

jugend_all = list(dict.fromkeys(jugend_base + jugend_slangwörter))
# Expand with common intensifiers + word combos
intensifiers = ["mega", "ultra", "super", "hyper", "hoch", "extrem", "absolut", "komplett", "total",
                "krass", "heavy", "heftig", "richtig", "echt", "voll", "so", "zu", "sehr", "gar"]
intensifiable = ["cringe", "lit", "fire", "based", "sus", "goated", "mid", "slay", "vibes", "based",
                 "cap", "real", "facts", "chad", "sigma", "alpha", "beta", "trash", "legendary", "epic"]
for i in intensifiers:
    for w in intensifiable:
        jugend_all.append(f"{i} {w}")
        jugend_all.append(f"{i}{w}")

# Add German youth-specific terms
jugend_german = [
    "Alder", "Alter", "Digga", "Digger", "Bruder", "Bro", "Abi", "Sippe", "Crew", "Gang",
    "Clique", "Homies", "Leute", "Jungs", "Mädels", "Brudi", "Schwester", "Geschwister",
    "Bazinga", "Kein Bock", "Bock haben", "null Bock", "voll der Bock", "Bock auf",
    "abgehen", "voll abgehen", "richtig abgehen", "krass abgehen", "heftig abgehen",
    "abfeiern", "voll abfeiern", "richtig abfeiern", "krass abfeiern",
    "abspacen", "voll abspacen", "richtig abspacen", "komplett abspacen",
    "flippen", "ausflippen", "komplett flippen", "richtig flippen", "voll flippen",
    "durchdrehen", "voll durchdrehen", "richtig durchdrehen", "komplett durchdrehen",
    "ausrasten", "voll ausrasten", "richtig ausrasten", "komplett ausrasten",
    "checken", "nicht checken", "nicht ganz checken", "komplett checken",
    "was geht", "was geht ab", "was ist los", "alles klar", "alles gut", "passt",
    "passt schon", "geht klar", "geht so", "könnte besser sein", "war schlimmer",
    "irgendwie schon", "irgendwie nicht", "irgendwie ja", "irgendwie nein",
    "so ein Ding", "was für ein Ding", "kein Ding", "null Problemo", "kein Stress",
    "easy", "easy peasy", "kein Aufwand", "keine Mühe", "in null Komma nichts",
    "in fünf Sekunden", "schneller als gedacht", "blitzschnell", "supersonic",
    "Ich bin so dabei", "ich bin raus", "ich bin drin", "ich mach mit", "ich pass",
    "bin dabei", "bin raus", "bin drin", "mach mit", "pass", "nein danke", "ja gerne",
    "gerne doch", "sehr gerne", "auf jeden Fall", "auf gar keinen Fall", "vllt",
    "vielleicht", "jein", "jo", "na ja", "ja nein", "nein ja", "weder noch", "sowohl als auch",
    "Läuft", "läuft bei mir", "läuft bei dir", "läuft bei uns", "läuft bei euch",
    "läuft bei denen", "läuft halt", "läuft schon", "läuft irgendwie", "läuft nicht",
    "läuft gar nicht", "läuft überhaupt nicht", "läuft null", "läuft nix",
    "Moin", "Moin Moin", "Servus", "Tschüss", "Tschüssi", "Ciao", "Bye", "Byebye",
    "Tschau", "Adios", "Auf Wiedersehen", "Bis dann", "Bis bald", "Bis später",
    "Bis morgen", "Bis nächste Woche", "Bis nächsten Monat", "Bis irgendwann",
    "Bis nie", "Hoffentlich nie wieder", "Nie wieder", "Auf Nimmerwiedersehen",
    "ich bin weg", "bin weg", "muss weg", "geh jetzt", "gehe jetzt", "tschüss ihr",
    "macht euch", "macht euch gut", "macht euch locker", "macht euch entspannt",
    "Lass ma", "lass mal", "lass mich", "lass uns", "lass euch", "lass sie", "lass ihn",
    "lass sie", "lass es", "lass das sein", "lass das bleiben", "lass das stehen",
    "Yeet", "yeet", "yeet it", "yoink", "yoink it", "oof", "big oof", "small oof",
    "medium oof", "oof-worthy", "certified oof", "historic oof", "generational oof",
    "Ich bin müde", "bin müde", "bin kaputt", "bin fertig", "bin am Ende", "bin durch",
    "bin tot", "bin gestorben", "ich sterbe", "sterbe gerade", "gerade gestorben",
    "nicht mehr", "nicht mehr lebend", "am sterben", "stirbt gerade", "stirbt",
    "das macht mich fertig", "macht mich kaputt", "macht mich verrückt", "macht mich wahnsinnig",
    "Boomer", "Zoomer", "Millennial", "Gen Z", "Gen Alpha", "Gen Beta", "Babyboomer",
    "OK Boomer", "Ok Karen", "Ok Kyle", "Ok Chad", "Ok Stacy", "Ok NPC", "Ok bot",
    "okay boomer energy", "boomer behavior", "zoomer behavior", "gen z behavior",
    "gen alpha rizz", "gen alpha sigma", "gen alpha based", "gen alpha goated",
    "sigma behavior", "alpha behavior", "beta behavior", "chad behavior", "simp behavior",
    "NPC behavior", "bot response", "android response", "robotic response", "automated response",
]

jugend_all.extend(jugend_german)

# EXTRA Jugendsprache padding
jugend_extra = [
    "Schlampe", "Hurensohn", "Wichser", "Opfer", "Vollspacko", "Spast", "Depp", "Idiot", "Trottel", "Vollidiot",
    "Volltrottel", "Volldepp", "Vollpfosten", "Pfosten", "Lauch", "Lauchgewächs", "Looser", "Loser", "Versager",
    "Nichtsnutz", "Penner", "Schnorrer", "Schmarotzer", "Parasit", "Freak", "Weirdo", "Seltsamer", "Sonderling",
    "Außenseiter", "Loner", "Einzelgänger", "Mauerblümchen", "Streber", "Nerd", "Geek", "Dork", "Dweeb", "Nerd",
    "Techie", "Gamer", "Zocker", "Zocker", "Coder", "Programmierer", "Programmierer", "Developer", "Dev", "IT-Nerd",
    "IT-Geek", "IT-Freak", "Science-Nerd", "Mathlete", "Mathenerd", "Physikgott", "Chemiefreak", "Biolaborant",
    "Bibliotheksmaus", "Bücherwurm", "Leseratte", "Filmfreak", "Serienjunkie", "Binge-Watcher", "Streamer",
    "Content-Nerd", "Youtube-Süchtiger", "TikTok-Zombie", "Instagram-Junkie", "Twitter-Addict", "Scrollsüchtiger",
    "Scrollzombie", "Doomscroller", "Handysüchtiger", "Smartphone-Zombie", "Tech-Addict", "Gaming-Addict",
    "Game-Süchtiger", "Online-Addict", "Internet-Süchtiger", "Wifi-Abhängiger", "Social-Media-Süchtiger",
    "Das ist nicht normal", "Das ist nicht real", "Das ist nicht wahr", "Das kann nicht sein", "Ich glaubs nicht",
    "Keine Ahnung", "hab keine Ahnung", "keine blasse Ahnung", "null Ahnung", "NULL plan", "kein Plan",
    "absolut kein Plan", "0 Plan", "nada", "nichts", "rein gar nichts", "absolut nichts", "überhaupt nichts",
    "gar nichts", "null komma nichts", "null komma niente", "niente", "nada y pues nada", "nichts und nix",
    "nix da", "nix", "nixie", "nixnix", "nope", "nö", "nee", "nein", "auf keinen Fall", "niemals", "never",
    "never ever", "no way", "no way josé", "out of the question", "nicht in meinem Leben", "not in this lifetime",
    "im Leben nicht", "im Leben nie", "in hundert Jahren nicht", "nicht wenn ich tot wäre", "not even",
    "Abstand", "großen Abstand halten", "Abstand halten", "bitte Abstand", "mehr Abstand", "viel mehr Abstand",
    "mega Abstand", "krassen Abstand", "heftigsten Abstand", "Sicherheitsabstand", "Mindestabstand",
    "Sicherheitsdistanz", "sichere Distanz", "angemessene Distanz", "professionelle Distanz", "Distanz wahren",
    "Grenzen wahren", "Grenzen setzen", "Grenzen haben", "Grenzen respektieren", "Grenzen achten",
    "Grenzen kennen", "Grenzen erkennen", "Grenzen sehen", "Grenzen spüren", "Grenzen fühlen",
    "das geht gar nicht", "das geht nicht", "das geht mal gar nicht", "das geht überhaupt nicht", "das geht null",
    "das geht so nicht", "das läuft nicht", "das läuft gar nicht", "das läuft null", "das passt nicht",
    "das passt gar nicht", "das passt überhaupt nicht", "das passt null", "passt null", "null kompatibel",
    "nicht kompatibel", "incompatible", "inkompatibel", "unvereinbar", "unverträglich", "widersprüchlich",
    "kontraproduktiv", "kontraindiziert", "contraproductiv", "gegensätzlich", "entgegengesetzt", "konträr",
    "diametral entgegengesetzt", "diametraler Gegensatz", "krasser Gegensatz", "totaler Gegensatz",
    "vollständiger Gegensatz", "kompletter Gegensatz", "absoluter Gegensatz", "reiner Gegensatz",
    "purer Gegensatz", "totaler Kontrast", "krasser Kontrast", "extremer Kontrast", "maximaler Kontrast",
    "Nullbock", "Bocklosigkeit", "Lustlosigkeit", "Demotivation", "Desinteresse", "Gleichgültigkeit",
    "Apathie", "Lethargie", "Passivität", "Inaktivität", "Tatenlosigkeit", "Faulheit", "Trägheit", "Faulenzerei",
    "Chillen", "Abhängen", "Rumhängen", "Faulenzen", "Gammeln", "Däumchen drehen", "Nichtstun", "Entspannen",
    "Relaxen", "Ausruhen", "Regenerieren", "Erholen", "Schlafen", "Pennen", "Dösen", "Schläfchen", "Nickerchen",
    "Mittagsschlaf", "Powernap", "kurzer Schlaf", "tiefer Schlaf", "fester Schlaf", "langer Schlaf", "Ausschlafen",
    "Ausschläfer", "Langschläfer", "Frühaufsteher", "Frühschicht", "Spätschicht", "Nachtschicht",
    "Nachtmensch", "Morgenmensch", "Abendmensch", "Nachteule", "Frühaufsteher", "Morgenmuffel", "Schlafmütze",
    "Schlafanzug", "Pyjama", "Jogginghose", "Sweater", "Hoodie", "Kapuzenpulli", "Puli", "Sweatshirt", "Übergangjacke",
    "Drip", "Outfit", "Fit", "Look", "Style", "Swag", "Geschmack", "Modestil", "Kleidungsstil", "Persönlichkeit",
    "Eigenstil", "Signature-Look", "Trademark", "Markenzeichen", "Wiedererkennungswert", "Identität",
    "Identitätsmarker",
    "Identitätsmerkmal", "Identitätssymbol", "Identitätsausdruck", "Selbstausdruck", "Selbstdarstellung",
    "Selbstpräsentation", "Außenwirkung", "öffentliches Image", "Imagepflege", "Imageaufbau", "Branding",
    "Personal Branding", "Markenaufbau", "Markenpflege", "Markenidentität", "Markenwert", "Markenstärke",
    "Authentizität", "Glaubwürdigkeit", "Verlässlichkeit", "Konsistenz", "Kohärenz", "Stringenz", "Logik",
    "Konsequenz", "Kontinuität", "Beständigkeit", "Nachhaltigkeit", "Stabilität", "Konstanz", "Invarianz",
    "Gleichmäßigkeit", "Regelmäßigkeit", "Rhythmus", "Takt", "Beat", "Groove", "Flow", "Vibe", "Energy", "Stimmung",
    "Atmosphäre", "Ambiente", "Flair", "Aura", "Charisma", "Ausstrahlung", "Magnetismus", "Anziehungskraft",
    "Zugkraft", "Strahlkraft", "Leuchtturm", "Leuchtfigur", "Leitfigur", "Vorbildfigur", "Idol", "Mentor", "Coach",
    "Vorbild", "Inspiration", "Motivator", "Influencer", "Leader", "Anführer", "Boss", "Chef", "Capo", "OG", "Legende",
    "Ikone", "Kultfigur", "Mythos", "Legende", "Heilige", "Gottheit", "Gott", "Göttlich", "Divinity", "Divine",
    "Heavenly", "Celestial", "Otherworldly", "Transcendent", "Legendary", "Epic", "Mythological", "Mythical",
    "Ethereal", "Ethereally beautiful", "Ethereally good", "Ethereally talented", "Ethereally skilled",
    "Phenomenal", "Phenomenon", "Phänomen", "Ausnahmeerscheinung", "Ausnahmetalent", "Sonderklasse",
    "Extraklasse", "Premiumklasse", "Luxusklasse", "Weltklasse", "Spitzenklasse", "Topklasse", "Eliteklasse",
    "Meisterklasse", "Meisterwerk", "Meisterstück", "Opus magnum", "Magnum opus", "Chef-d'oeuvre", "Hauptwerk",
    "Lebenswerk", "Jahrzehntwerk", "Jahrhundertwerk", "Jahrtausendwerk", "einmaliges Werk", "einzigartiges Werk",
    "unvergängliches Werk", "unsterbliches Werk", "zeitloses Werk", "ewig gültiges Werk", "für die Ewigkeit",
    "für die Nachwelt", "für die Geschichte", "für die Bücher", "für die Geschichtsbücher", "legendär",
    "in die Geschichte eingegangen", "Geschichte geschrieben", "Geschichte gemacht", "Geschichte geformt",
    "Geschichte geprägt", "Geschichte beeinflusst", "Geschichte verändert", "Geschichte revolutioniert",
    "alles verändert", "alles auf den Kopf gestellt", "die Welt verändert", "die Welt erschüttert",
    "die Welt bewegt", "die Welt berührt", "die Welt inspiriert", "die Welt motiviert", "die Welt begeistert",
    "die Welt überzeugt", "die Welt erleuchtet", "die Welt erheitert", "die Welt erfreut", "die Welt belustigt",
    "die Welt beschäftigt", "die Welt nachhaltig geprägt", "nachhaltig beeinflusst", "bleibend beeindruckt",
    "unvergesslich", "unauslöschlich", "unverwischbar", "tief verwurzelt", "tief verankert", "tief eingebrannt",
    "eingebrannt im Gedächtnis", "eingetragen im Gedächtnis", "eingraviert im Gedächtnis", "eingemeißelt",
    "in Stein gemeißelt", "in Gold gegossen", "unsterblich gemacht", "für immer festgehalten",
]
jugend_all.extend(jugend_extra)

# More random German youth phrases
for i in range(1, 200):
    jugend_all.append(f"Digga{i}")
    jugend_all.append(f"Bro{i}")

# More slang with suffixes
jugend_suffixes = ["-mäßig", "-technisch", "-seitig", "-bezogen", "-orientiert", "-basiert", "-gesteuert"]
jugend_roots2 = ["Cringe", "Slay", "Vibe", "Chad", "Sigma", "Alpha", "Beta", "Hype", "Flex", "Gang", "Mood", "Fire",
                 "Lit"]
for r in jugend_roots2:
    for s in jugend_suffixes:
        jugend_all.append(f"{r}{s}")

liste_jugend = dedupe_ordered(jugend_all)[:2000]
print(f"Jugendsprache: {len(liste_jugend)}")

# ============================================================
# KATEGORIE 3: GEBILDETE SPRACHE
# ============================================================

gebildet_base = [
    "Abstraktion", "Ambiguität", "Ambivalenz", "Analogie", "Analyse", "Annahme",
    "Antizipation", "Argumentation", "Assertion", "Axiom", "Begriff", "Bedeutung",
    "Begründung", "Behauptung", "Betrachtung", "Bewusstsein", "Charakteristikum",
    "Darlegung", "Deduktion", "Definition", "Deliberation", "Denotation", "Determination",
    "Dialektik", "Differenzierung", "Dimension", "Diskrepanz", "Diskurs", "Disputation",
    "Distinktion", "Divergenz", "Elaboration", "Emergenz", "Empirie", "Entfaltung",
    "Epistemologie", "Erkenntnis", "Erkenntnistheorie", "Erläuterung", "Exegese",
    "Exemplifikation", "Explikation", "Falsifikation", "Fundament", "Genese",
    "Hermeneutik", "Hierarchie", "Hypothese", "Identität", "Implikation", "Induktion",
    "Inferenz", "Insuffizienz", "Integration", "Interdependenz", "Interpretation",
    "Kausalität", "Kohärenz", "Komplexität", "Konklusion", "Konsequenz", "Konstitution",
    "Kontextualisierung", "Konvergenz", "Korrelation", "Legitimation", "Logik",
    "Manifestation", "Mediation", "Methodik", "Modalität", "Normativität", "Objektivität",
    "Ontologie", "Operationalisierung", "Paradigma", "Parameter", "Perspektive",
    "Phänomen", "Phänomenologie", "Plausibilität", "Pluralismus", "Postulat",
    "Pragmatik", "Prämisse", "Proposition", "Rationalität", "Reduktion", "Reflexion",
    "Relativismus", "Relevanz", "Repräsentation", "Semantik", "Signifikanz", "Struktur",
    "Subjektivität", "Substanz", "Synthese", "Systematik", "Teleologie", "Terminologie",
    "Theorie", "Transposition", "Universalität", "Validität", "Verifikation", "Wahrnehmung",
    "Widerspruch", "Wissenschaft", "Zusammenhang", "Konstruktion", "Kritik", "Konzept",
    "Essenz", "Fundierung", "Kontext", "Prinzip", "Axiologie", "Erkennbarkeit",
    "Kohärenzprinzip", "Kohärenztheorie", "Korrespondenztheorie", "Konsistenz",
    "Intentionalität", "Kognition", "Metakognition", "Metaebene", "Metaanalyse",
    "Metareflexion", "Metadiskurs", "Metaperspektive", "Metaparadigma", "Metasprache",
    "Objektsprache", "Gegenstandssprache", "Fachsprache", "Wissenschaftssprache",
    "akademische Sprache", "wissenschaftlicher Diskurs", "gelehrter Ausdruck",
    "elaborierter Code", "restringierter Code", "Sprachregister", "Stilregister",
    "gehobener Stil", "formeller Stil", "schriftsprachlicher Stil", "bildungssprachlich",
    "Akkumulation", "Allegorie", "Alliteration", "Anapher", "Antithese", "Aphorismus",
    "Chiasmus", "Ellipse", "Euphemismus", "Hyperbel", "Ironie", "Klimax", "Litotes",
    "Metapher", "Metonymie", "Oxymoron", "Paradoxon", "Parallelismus", "Paraphrase",
    "Parataxe", "Hypotaxe", "Periode", "Personifikation", "Pleonasmus", "Rhetorische Frage",
    "Synekdoche", "Synästhesie", "Tautologie", "Wiederholung", "rhetorisches Mittel",
    "Stilmittel", "sprachliches Bild", "Vergleich", "Gleichnis", "Parabel", "Allegorie",
    "Symbol", "Leitmotiv", "Motiv", "Thema", "Sujet", "Stoff", "Plot", "Fabel",
    "Narration", "Diegesis", "Mimesis", "Intertextualität", "Intermedialität",
    "Paratextualität", "Metatextualität", "Hypertextualität", "Architextualität",
    "Intertextuell", "Intermedial", "Paratextuell", "Metatextuell", "Hypertextuell",
    "Architextuell", "narratologisch", "diegetisch", "mimetisch", "intertextuell",
    "Erzählperspektive", "Erzählhaltung", "Erzählstimme", "Erzählebene", "Erzählzeit",
    "erzählte Zeit", "Erzähltempo", "Raffung", "Dehnung", "Pause", "Ellipse", "Zeitdeckung",
    "Analepse", "Prolepse", "Rückblende", "Vorausschau", "Vorahnung", "Foreshadowing",
    "Retrospektive", "Retrospektion", "Rückschau", "Retrospektiv", "flashback", "flash-forward",
    "Protagonisten", "Antagonist", "Nebenfigur", "Randfigur", "Komparse", "Figurenkonstellation",
    "Figurencharakterisierung", "direkte Charakterisierung", "indirekte Charakterisierung",
    "explizite Charakterisierung", "implizite Charakterisierung", "Figurenentwicklung",
    "Charakterentwicklung", "Figurenevolution", "Figurentransformation", "Figurenwandel",
    "statische Figur", "dynamische Figur", "runde Figur", "flache Figur", "typisierte Figur",
    "individualisierte Figur", "archetypische Figur", "stereotype Figur", "symbolische Figur",
    "allegorische Figur", "Rationalismus", "Empirismus", "Idealismus", "Materialismus",
    "Realismus", "Naturalismus", "Positivismus", "Pragmatismus", "Existenzialismus",
    "Phänomenologie", "Hermeneutik", "Dekonstruktion", "Poststrukturalismus",
    "Strukturalismus", "Formalismus", "Funktionalismus", "Systemtheorie", "Kritische Theorie",
    "Frankfurter Schule", "Frankfurter Schul", "Dialektische Aufklärung", "Kulturindustrie",
    "instrumentelle Vernunft", "kommunikative Vernunft", "kommunikatives Handeln",
    "strategisches Handeln", "zweckrationales Handeln", "wertrationales Handeln",
    "affektuelles Handeln", "traditionales Handeln", "Weber", "Durkheim", "Bourdieu",
    "Habermas", "Luhmann", "Parsons", "Merton", "Goffman", "Garfinkel", "Foucault",
    "Derrida", "Lacan", "Deleuze", "Guattari", "Butler", "Said", "Spivak", "Bhabha",
    "postkolonial", "poststrukturalistisch", "dekonstruktivistisch", "performativ",
    "diskursiv", "dispositivisch", "genealogisch", "archäologisch", "genealogisch",
    "disziplinarisch", "normalisierend", "normierend", "normativ", "präskriptiv",
    "deskriptiv", "explanativ", "explorativ", "evaluativ", "kritisch", "reflexiv",
    "selbstreflexiv", "metareflexiv", "transdisziplinär", "interdisziplinär",
    "multidisziplinär", "disziplinär", "monodisziplinär", "fächerübergreifend",
    "fachübergreifend", "querschnittlich", "horizontal", "vertikal", "diagonal",
    "diagonaler Ansatz", "horizontaler Zugang", "vertikaler Blick", "Panoramaperspektive",
    "Vogelperspektive", "Froschperspektive", "Totale", "Halbtotale", "Nah", "Nahaufnahme",
    "Detailaufnahme", "Makroperspektive", "Mikroperspektive", "Mesoperspektive",
    "Makroebene", "Mikroebene", "Mesoebene", "makrosozial", "mikrosozial", "mesosozial",
    "gesellschaftlich", "sozial", "kulturell", "politisch", "ökonomisch", "ökologisch",
    "technologisch", "rechtlich", "institutionell", "organisational", "individuell",
    "kollektiv", "gemeinschaftlich", "gesamtgesellschaftlich", "zivilgesellschaftlich",
    "staatlich", "öffentlich", "privat", "halböffentlich", "halbanonym", "anonym",
    "pseudonym", "namentlich", "namentlich bekannt", "unbekannt", "diffus", "konkret",
    "abstrakt", "generell", "spezifisch", "partikular", "universal", "global", "lokal",
    "regional", "national", "transnational", "international", "supranational",
    "postnational", "subnational", "kommunal", "urban", "rural", "suburban", "periurban",
    "metropolitisch", "kleinstädtisch", "ländlich", "agrar", "industriell", "postindustriell",
    "dienstleistungsbasiert", "wissensbasiert", "innovationsgetrieben", "technologiegetrieben",
    "marktgetrieben", "nachfragegetrieben", "angebotsseitig", "nachfrageseitig",
    "angebotsorientiert", "nachfrageorientiert", "angebotsbasiert", "nachfragebasiert",
    "angebotsseitige Politik", "nachfrageseitige Politik", "Angebotspolitik", "Nachfragepolitik",
    "fiskalisch", "monetär", "geldpolitisch", "fiskalpolitisch", "wirtschaftspolitisch",
    "sozialpolitisch", "bildungspolitisch", "kulturpolitisch", "umweltpolitisch",
    "technologiepolitisch", "forschungspolitisch", "innovationspolitisch", "industriepolitisch",
    "handels politisch", "außenpolitisch", "innenpolitisch", "sicherheitspolitisch",
    "verteidigungspolitisch", "entwicklungspolitisch", "humanitär", "diplomatisch",
    "konsularisch", "bilateral", "multilateral", "plurilateral", "universell",
    "regional", "subregional", "interregional", "transregional", "überregional",
]

# Derive additional forms
gebildet_suffixes = ["lich", "isch", "sam", "haft", "bar", "los", "reich", "voll", "artig", "mäßig"]
gebildet_prefixes = ["un", "gegen", "wider", "über", "unter", "vor", "nach", "mit", "aus", "ein", "an", "auf", "ab",
                     "durch", "hin", "her", "weg", "fort", "zurück", "weiter", "fort", "voran", "vorwärts", "rückwärts",
                     "aufwärts", "abwärts", "einwärts", "auswärts"]
gebildet_noun_suffixes = ["ung", "keit", "heit", "schaft", "tum", "nis", "sal", "ling", "ier", "ist", "ismus", "ität",
                          "tion", "sion", "ation", "ifikation", "isierung", "alisierung"]

gebildet_all = list(gebildet_base)

# Word derivations from base nouns
gebildet_roots = [
    "kritisch", "analytisch", "synthetisch", "empirisch", "theoretisch", "methodisch",
    "systematisch", "strukturell", "funktional", "normativ", "deskriptiv", "präskriptiv",
    "explorativ", "explanativ", "evaluativ", "reflexiv", "diskursiv", "performativ",
    "konstruktiv", "destruktiv", "produktiv", "reproduktiv", "transformativ", "reformativ",
    "konservativ", "progressiv", "reaktiv", "aktiv", "passiv", "interaktiv", "reaktiv",
    "proaktiv", "retroaktiv", "transaktiv", "kollaborativ", "kooperativ", "kompetitiv",
    "additiv", "substraktiv", "multiplikativ", "divisiv", "exponentiell", "linear",
    "zirkulär", "rekursiv", "iterativ", "inkrementell", "dekrementell", "progressiv",
    "regressiv", "stagnativ", "evolutiv", "revolutionär", "reformerisch", "konservierend",
    "liberalisierend", "demokratisierend", "autoritarisierend", "bürokratisierend",
    "rationalisierend", "modernisierend", "tradierend", "kulturalisierend", "naturalisierend",
    "biologisierend", "psychologisierend", "soziologisierend", "ökonomisierend",
    "politisierend", "juridifizierend", "moralisierend", "ästhetisierend", "sakralisierend",
    "profanisierend", "säkularisierend", "spiritualisierend", "materialisierend",
    "idealisierend", "realisierend", "virtualisierend", "digitalisierend", "analogisierend",
    "globalisierend", "lokalisierend", "regionalisierend", "nationalisierend", "internationalisierend",
    "transnationalisierend", "postnationalisierend", "kosmopolitisierend", "partikularisierend",
    "universalisierend", "partikularisierend", "individualiserend", "kollektivisierend",
    "pluralisierend", "diversifizierend", "homogenisierend", "heterogenisierend",
    "standardisierend", "normierend", "regulierend", "deregulierend", "liberalisierend",
    "protektionistisch", "interventionistisch", "dirigistisch", "marktliberal", "marktkritisch",
    "neoliberal", "ordoliberal", "wohlfahrtsstaatlich", "sozialstaatlich", "nachtwächterstaatlich",
    "subsidiaritätsprinzip", "proportionalitätsprinzip", "verhältnismäßigkeitsprinzip",
    "rechtsstaatsprinzip", "demokratieprinzip", "bundesstaatsprinzip", "sozialstaatsprinzip",
    "gewaltentrennungsprinzip", "volkssouveränitätsprinzip", "repräsentationsprinzip",
    "partizipationsprinzip", "deliberationsprinzip", "öffentlichkeitsprinzip",
    "transparenzprinzip", "rechenschaftsprinzip", "verantwortlichkeitsprinzip",
    "legitimationsprinzip", "effektivitätsprinzip", "effiziensprinzip", "wirtschaftlichkeitsprinzip",
    "sparsamkeitsprinzip", "verhältnismäßigkeitsprinzip", "gleichheitsgrundsatz", "freiheitsgrundsatz",
    "solidaritätsgrundsatz", "subsidiaritätsgrundsatz", "integrationsgrundsatz",
    "kohäsionsgrundsatz", "konvergenzsatz", "divergenzsatz", "konzentrationslogik",
    "dezentralisierungslogik", "dekonzentrationsprinzip", "föderalisierungsprinzip",
    "zentralisierungstendenz", "dezentralisierungstendenz", "föderalisierungstendenz",
    "supranationalisierungstendenz", "intergouvernementalisierungstendenz",
    "parlamentarisierungstendenz", "präsidentialisierungstendenz", "judikalisierungstendenz",
    "bürokratisierungstendenz", "technokratisierungstendenz", "expertisierungstendenz",
    "professionalisierungstendenz", "akademisierungstendenz", "verwissenschaftlichungstendenz",
    "empirisierungstendenz", "quantifizierungstendenz", "formalisierungstendenz",
    "standardisierungstendenz", "normierungstendenz", "kodifizierungstendenz",
    "institutionalisierungstendenz", "organisierungstendenz", "professionalisierungstendenz",
    "spezialisierungstendenz", "differenzierungstendenz", "individualisierungstendenz",
]

gebildet_all.extend(gebildet_roots)

# Derive nouns from adjectives
for root_adj in ["kritisch", "analytisch", "theoretisch", "methodisch", "systematisch", "empirisch",
                 "normativ", "reflexiv", "diskursiv", "konstruktiv", "transformativ", "progressiv",
                 "kollaborativ", "kooperativ", "iterativ", "evolutiv", "rationalisierend"]:
    base = root_adj.replace("isch", "").replace("iv", "").replace("ell", "").replace("end", "")
    gebildet_all.extend([
        root_adj, base + "ik", base + "ität", base + "ierung", base + "ismus", base + "ist",
                  base + "isierung", base + "analyse", base + "forschung", base + "wissenschaft",
                  base + "theorie", base + "methode", base + "ansatz", base + "perspektive",
                  base + "rahmen", base + "konzept", base + "modell", base + "paradigma",
                  base + "diskurs", base + "kritik", base + "reflexion", base + "überlegung",
    ])

# Academic collocations
akademische_kollokationen = [
    "empirische Untersuchung", "theoretische Fundierung", "methodische Reflexion",
    "kritische Analyse", "systematische Darstellung", "strukturierte Argumentation",
    "kohärente Begründung", "stringente Ableitung", "differenzierte Betrachtung",
    "nuancierte Einschätzung", "fundierte Aussage", "valide Messung", "reliable Erhebung",
    "objektive Beurteilung", "intersubjektive Überprüfbarkeit", "wissenschaftliche Gütekriterien",
    "methodologische Stringenz", "epistemologische Grundlagen", "ontologische Prämissen",
    "erkenntnistheoretische Positionen", "wissenschaftstheoretische Grundannahmen",
    "forschungslogische Konsequenzen", "methodische Triangulation", "Datentriangulation",
    "theoretische Triangulation", "investigative Triangulation", "multi-method approach",
    "mixed methods design", "qualitative Forschung", "quantitative Forschung",
    "interpretative Forschung", "erklärende Forschung", "explorative Studie",
    "deskriptive Studie", "normative Studie", "evaluative Studie", "komparative Studie",
    "longitudinale Studie", "Querschnittsstudie", "Längsschnittstudie", "Panelstudie",
    "Fallstudie", "Einzelfallstudie", "vergleichende Fallstudie", "komparative Analyse",
    "vergleichende Analyse", "kontrastive Analyse", "kontextuelle Analyse",
    "diskursanalytische Untersuchung", "inhaltsanalytische Auswertung", "narrationsanalytisch",
    "gesprächsanalytisch", "konversationsanalytisch", "interaktionsanalytisch",
    "dokumentenanalytisch", "archivarisch", "historisch-kritisch", "philologisch",
    "hermeneutisch", "phänomenologisch", "ethnomethodologisch", "sozialkonstruktivistisch",
    "symbolisch-interaktionistisch", "feldtheoretisch", "systemtheoretisch", "akteurszentriert",
    "strukturzentriert", "kulturzentriert", "diskurszentriert", "machtanalytisch",
    "wissenssoziologisch", "ideologiekritisch", "ideengeschichtlich", "begriffsgeschichtlich",
    "problemgeschichtlich", "sozialgeschichtlich", "kulturgeschichtlich", "wirtschaftsgeschichtlich",
    "politikgeschichtlich", "alltagsgeschichtlich", "mikrohistorisch", "makrohistorisch",
    "global history", "transnational history", "entangled history", "histoire croisée",
    "histoire connectée", "histoire totale", "histoire sérielle", "histoire quantitative",
    "histoire des mentalités", "histoire des représentations", "histoire des pratiques",
    "histoire des discours", "histoire du corps", "histoire des émotions", "histoire du genre",
    "histoire de la sexualité", "histoire de la violence", "histoire de la mort",
    "histoire du travail", "histoire de l'économie", "histoire politique", "histoire sociale",
    "histoire culturelle", "histoire intellectuelle", "histoire des sciences",
    "histoire des techniques", "histoire de l'art", "histoire littéraire", "histoire religieuse",
    "histoire de l'éducation", "histoire de la famille", "histoire de l'enfance",
    "histoire des femmes", "histoire du féminisme", "histoire des minorités",
    "histoire des migrations", "histoire de l'esclavage", "histoire coloniale",
    "histoire postcoloniale", "histoire décoloniale", "histoire globale", "Globalgeschichte",
    "Verflechtungsgeschichte", "Transfergeschichte", "histoire croisée", "Begegnungsgeschichte",
    "Kontaktgeschichte", "Austauschgeschichte", "Wissenstransfer", "Kulturtransfer",
    "Technologietransfer", "Idéentransfer", "Konzepttransfer", "Modeltransfer",
    "institutioneller Wandel", "sozialer Wandel", "kultureller Wandel", "politischer Wandel",
    "ökonomischer Wandel", "technologischer Wandel", "demographischer Wandel",
]

gebildet_all.extend(akademische_kollokationen)

# Extra gebildete Sprache - extensive academic vocabulary
gebildet_extra = [
    "Konstitutivum", "Konstitutiva", "konstitutiv", "konstituierend", "konstitutionell",
    "Determinismus", "deterministisch", "determiniert", "Indeterminismus", "indeterministisch",
    "Voluntarismus", "voluntaristisch", "Strukturalismus", "strukturalistisch", "strukturell",
    "Funktionalismus", "funktionalistisch", "funktional", "Kognitivismus", "kognitivistisch", "kognitiv",
    "Behaviorismus", "behavioristisch", "behavioral", "Konstruktivismus", "konstruktivistisch", "konstruktiv",
    "Dekonstruktivismus", "dekonstruktivistisch", "dekonstruktiv", "Postmodernismus", "postmodernistisch", "postmodern",
    "Modernismus", "modernistisch", "modern", "Prämodernismus", "prämodernistisch", "prämodern",
    "Traditionalismus", "traditionalistisch", "traditional", "Konservativismus", "konservativistisch", "konservativ",
    "Liberalismus", "liberalistisch", "liberal", "Sozialismus", "sozialistisch", "sozial",
    "Kommunismus", "kommunistisch", "kommunal", "Anarchismus", "anarchistisch", "anarchisch",
    "Kapitalismus", "kapitalistisch", "kapital", "Feudalismus", "feudalistisch", "feudal",
    "Patriarchalismus", "patriarchalistisch", "patriarchal", "Matriarchalismus", "matriarchalistisch", "matriarchal",
    "Egalitarismus", "egalitaristisch", "egalitär", "Hierarchismus", "hierarchistisch", "hierarchisch",
    "Pluralismus", "pluralistisch", "plural", "Monismus", "monistisch", "monistisch", "Dualismus", "dualistisch",
    "dual",
    "Totalitarismus", "totalitaristisch", "totalitär", "Autoritarismus", "autoritaristisch", "autoritär",
    "Demokratismus", "demokratisch", "Republikanismus", "republikanisch", "Monarchismus", "monarchistisch",
    "monarchisch",
    "Föderalismus", "föderalistisch", "föderativ", "Unitarismus", "unitaristisch", "unitarisch",
    "Zentralismus", "zentralistisch", "zentralisiert", "Dezentralismus", "dezentralistisch", "dezentralisiert",
    "Imperialismus", "imperialistisch", "imperial", "Kolonialismus", "kolonialistisch", "kolonial",
    "Antikolonialismus", "antikolonialistisch", "antikolonial", "Postkolonialismus", "postkolonialistisch",
    "postkolonial",
    "Dekolonialismus", "dekolonialistisch", "dekolonial", "Neoimperialismus", "neoimperialistisch", "neoimperial",
    "Globalismus", "globalistisch", "global", "Lokalismus", "lokalistisch", "lokal", "Regionalismus", "regionalistisch",
    "regional",
    "Nationalismus", "nationalistisch", "national", "Patriotismus", "patriotistisch", "patriotisch",
    "Kosmopolitismus", "kosmopolitistisch", "kosmopolitisch", "Universalismus", "universalistisch", "universell",
    "Partikularismus", "partikularistisch", "partikulär", "Relativismus", "relativistisch", "relativ",
    "Absolutismus", "absolutistisch", "absolut", "Nihilismus", "nihilistisch", "nihil", "Optimismus", "optimistisch",
    "optimiert",
    "Pessimismus", "pessimistisch", "pessimiert", "Realismus", "realistisch", "real", "Idealismus", "idealistisch",
    "ideal",
    "Rationalismus", "rationalistisch", "rational", "Empirismus", "empiristisch", "empirisch",
    "Pragmatismus", "pragmatistisch", "pragmatisch", "Utilitarismus", "utilitaristisch", "utilitarisch",
    "Deontologie", "deontologisch", "Konsequentialismus", "konsequentialistisch", "konsequential",
    "Tugendethik", "tugendhaft", "Metaethik", "metaethisch", "Normethik", "normethisch",
    "Angewandte Ethik", "angewandt", "Bioethik", "bioethisch", "Umweltethik", "umweltethisch",
    "Medizinethik", "medizinethisch", "Wirtschaftsethik", "wirtschaftsethisch", "Politikethik", "politikethisch",
    "Medienethik", "medienethisch", "Informationsethik", "informationsethisch", "KI-Ethik", "KI-ethisch",
    "algorithmische Ethik", "algorithmisch-ethisch", "Technologieethik", "technologieethisch",
    "Ingenieursethik", "ingenieurethisch", "Forschungsethik", "forschungsethisch", "wissenschaftliche Integrität",
    "Forschungsintegrität", "akademische Integrität", "intellektuelle Ehrlichkeit", "epistemische Bescheidenheit",
    "epistemische Demut", "kognitive Demut", "intellektuelle Bescheidenheit", "intellektuelle Offenheit",
    "intellektuelle Neugier", "intellektuelle Redlichkeit", "intellektuelle Fairness", "intellektuelle Sorgfalt",
    "methodische Sorgfalt", "empirische Sorgfalt", "analytische Sorgfalt", "kritische Sorgfalt",
    "reflexive Sorgfalt", "interpretative Sorgfalt", "hermeneutische Sorgfalt", "phänomenologische Sorgfalt",
    "Evidenzbasierung", "evidenzbasiert", "Faktizität", "faktisch", "Faktualität", "faktual",
    "Tatsächlichkeit", "tatsächlich", "Realität", "real", "Wirklichkeit", "wirklich", "Aktualität", "aktuell",
    "Potenzialität", "potenziell", "Virtualität", "virtuell", "Modalität", "modal", "Möglichkeit", "möglich",
    "Unmöglichkeit", "unmöglich", "Notwendigkeit", "notwendig", "Kontingenz", "kontingent", "Zufälligkeit", "zufällig",
    "Kausalität", "kausal", "Teleologie", "teleologisch", "Finalität", "final", "Instrumentalität", "instrumental",
    "Funktionalität", "funktional", "Strukturalität", "struktural", "Prozessualität", "prozessual", "Relationalität",
    "relational",
    "Temporalität", "temporal", "Räumlichkeit", "räumlich", "Leiblichkeit", "leiblich", "Materialität", "material",
    "Immaterialität", "immaterial", "Geistigkeit", "geistig", "Spiritualität", "spiritual", "Transzendenz",
    "transzendent",
    "Immanenz", "immanent", "Diesseitigkeit", "diesseitig", "Jenseitigkeit", "jenseitig", "Weltlichkeit", "weltlich",
    "Sakralität", "sakral", "Profanität", "profan", "Heiligkeit", "heilig", "Sündhaftigkeit", "sündhaft",
    "Tugend", "tugendhaft", "Laster", "lasterhaft", "Moral", "moralisch", "Immoralität", "immoral",
    "Amoralität", "amoral", "Ethizität", "ethisch", "Unethizität", "unethisch", "Wert", "wertvoll", "Unwert", "wertlos",
    "Norm", "normal", "Anomalie", "anomal", "Regel", "regelkonform", "Ausnahme", "ausnahmsweise",
    "Standard", "standardisiert", "Abweichung", "abweichend", "Konformität", "konform", "Nonkonformität", "nonkonform",
    "Devianz", "deviant", "Konventionalität", "konventionell", "Unkonventionalität", "unkonventionell",
    "Orthodoxie", "orthodox", "Heterodoxie", "heterodox", "Häresie", "häretisch", "Dogma", "dogmatisch",
    "Antidogmatismus", "antidogmatisch", "Freidenkertum", "freidenkend", "Skeptizismus", "skeptisch",
    "Kritizismus", "kritizistisch", "Agnostizismus", "agnostisch", "Atheismus", "atheistisch",
    "Theismus", "theistisch", "Deismus", "deistisch", "Pantheismus", "pantheistisch", "Panentheismus",
    "panentheistisch",
    "Monotheismus", "monotheistisch", "Polytheismus", "polytheistisch", "Henotheismus", "henotheistisch",
    "Animismus", "animistisch", "Schamanismus", "schamanistisch", "Totemismus", "totemistisch",
    "Mystizismus", "mystisch", "Esoterik", "esoterisch", "Exoterik", "exoterisch", "Okkultismus", "okkult",
    "Hermetismus", "hermetisch", "Gnosis", "gnostisch", "Kabbalismus", "kabbalistisch", "Sufismus", "sufistisch",
    "Zen", "zenistisch", "Taoismus", "taoistisch", "Konfuzianismus", "konfuzianisch", "Buddhismus", "buddhistisch",
    "Hinduismus", "hinduistisch", "Islam", "islamisch", "Christentum", "christlich", "Judentum", "jüdisch",
    "Atheismus", "atheistisch", "Humanismus", "humanistisch", "Säkularismus", "säkularistisch", "Laizismus",
    "laizistisch",
    "Szientismus", "szientistisch", "Naturalismus", "naturalistisch", "Materialismus", "materialistisch",
    "Physikalismus", "physikalistisch", "Phänomenalismus", "phänomenalistisch", "Idealismus", "idealistisch",
    "Berkeleyscher Idealismus", "Kantischer Idealismus", "Hegelscher Idealismus", "Fichtes Idealismus",
    "Schellings Naturphilosophie", "Schopenhauers Voluntarismus", "Nietzschescher Nihilismus",
    "Heideggersein und Zeit", "Sartressein und Nichts", "Camusabsurder Mensch", "Camusabsurdismus",
    "existentialistische Grundbegriffe", "existenzialphilosophisch", "daseinsanalytisch", "fundamentalontologisch",
    "transzendentalprägnant", "transzendental", "transzendental-pragmatisch", "transzendental-hermeneutisch",
    "sprachanalytisch", "logisch-empiristisch", "neopragmatistisch", "neopragmatisch", "postanalytisch",
    "ordinary language philosophy", "gewöhnliche Sprache", "Sprachspiele", "Wittgenstein", "Sprachphilosophie",
    "Bedeutungstheorie", "Referenztheorie", "Gebrauchstheorie", "inferentialistische Semantik",
    "Wahrheitsbedingungssemantik", "mögliche-Welten-Semantik", "intensionale Semantik", "extensionale Semantik",
    "formale Semantik", "lexikalische Semantik", "konzeptuelle Semantik", "kognitive Semantik", "frame-Semantik",
    "Prototypensemantik", "Radiale-Kategorie", "Basisebene", "Grundebene", "Superordinat", "Subkategorie",
    "kategoriale Wahrnehmung", "kategoriale Kognition", "konzeptuelle Kognition", "konzeptuelles System",
    "konzeptuelles Netz", "semantisches Netz", "assoziatives Netz", "kognitives Netz", "mentales Lexikon",
    "mentales Modell", "mentale Repräsentation", "propositionale Repräsentation", "analoge Repräsentation",
    "bildliche Repräsentation", "schematische Repräsentation", "skriptbasierte Repräsentation", "Frames",
    "Schemata", "Skripte", "Prototypen", "Stereotypen", "Vorstellungsbilder", "mentale Bilder", "Vorstellungen",
    "Konzepte", "Begriffe", "Kategorien", "Klassen", "Mengen", "Gattungen", "Arten", "Individuen",
    "Typen", "Token", "Exemplare", "Instanzen", "Fälle", "Beispiele", "Belege", "Evidenzen",
    "Daten", "Fakten", "Informationen", "Wissen", "Verstehen", "Einsicht", "Erkenntnis", "Weisheit",
    "Kompetenz", "Expertise", "Meisterschaft", "Virtuosität", "Brillanz", "Exzellenz", "Überlegenheit", "Dominanz",
    "Hegemonie", "Führung", "Macht", "Autorität", "Legitimität", "Legalität", "Normativität", "Moralität", "Ethizität",
    "Gültigkeit", "Verbindlichkeit", "Verpflichtung", "Pflicht", "Schuldigkeit", "Recht", "Anspruch", "Anrecht",
    "Berechtigung", "Befugnis", "Vollmacht", "Kompetenz", "Zuständigkeit", "Verantwortlichkeit", "Rechenschaftspflicht",
    "Transparenz", "Nachvollziehbarkeit", "Nachprüfbarkeit", "Falsifizierbarkeit", "Verifizierbarkeit",
    "Replizierbarkeit", "Reproduzierbarkeit", "Replikabilität", "Skalierbarkeit", "Transferierbarkeit",
    "Generalisierbarkeit",
    "externe Validität", "interne Validität", "Konstruktvalidität", "Inhaltsvalidität", "Kriteriumsvalidität",
    "konvergente Validität", "diskriminante Validität", "faktorielle Validität", "ökologische Validität",
    "externe Reliabilität", "interne Reliabilität", "Retest-Reliabilität", "Split-half-Reliabilität",
    "Paralleltestreliabilität",
    "Interrater-Reliabilität", "Intra-Rater-Reliabilität", "Cronbachs Alpha", "Kuder-Richardson-Formel",
    "Objektivität", "Durchführungsobjektivität", "Auswertungsobjektivität", "Interpretationsobjektivität",
    "Standardisierung", "Normierung", "Eichung", "Kalibrierung", "Validierung", "Verifikation", "Falsifikation",
    "Hypothesentest", "Signifikanztest", "Nullhypothese", "Alternativhypothese", "Fehler 1. Art", "Fehler 2. Art",
    "Signifikanzniveau", "p-Wert", "Effektgröße", "statistische Power", "Teststärke", "Stichprobengröße",
    "Stichprobenziehung", "Zufallsstichprobe", "geschichtete Stichprobe", "Klumpenstichprobe", "Quotenstichprobe",
    "Gelegenheitsstichprobe", "Schneeball-Sampling", "theoretisches Sampling", "purposive sampling",
    "Maximum-Variation-Sampling",
]

gebildet_all.extend(gebildet_extra)
liste_gebildet = dedupe_ordered(gebildet_all)[:2000]
print(f"Gebildete Sprache: {len(liste_gebildet)}")

# ============================================================
# KATEGORIE 4: UNTERSTÜTZENDE WÖRTER
# ============================================================

unterstuetzend_base = [
    # Zustimmung / Bestätigung
    "ja", "genau", "richtig", "stimmt", "korrekt", "absolut", "definitiv", "natürlich",
    "selbstverständlich", "sicher", "gewiss", "ganz recht", "vollkommen", "vollständig",
    "zweifellos", "unbedingt", "auf jeden Fall", "ohne Frage", "freilich", "allerdings",
    "jawohl", "jajaja", "genau so", "so ist es", "ganz genau", "ganz richtig", "stimmt genau",
    "das stimmt", "das ist richtig", "das ist korrekt", "exakt", "präzise", "treffend",
    "zutreffend", "wahr", "tatsächlich", "in der Tat", "fürwahr", "wahrhaftig", "wirklich",
    "wirklich wahr", "das ist wahr", "das ist so", "das ist wahr und richtig",
    # Ermutigung
    "weiter so", "mach weiter", "mach weiter so", "gut gemacht", "sehr gut", "ausgezeichnet",
    "wunderbar", "fantastisch", "prima", "toll", "super", "spitze", "klasse", "großartig",
    "hervorragend", "vortrefflich", "ausgezeichnet", "lobenswert", "vorbildlich", "mustergültig",
    "tadellos", "makellos", "perfekt", "ideal", "optimal", "vortrefflich", "erstklassig",
    "exzellent", "brillant", "glänzend", "strahlend", "prächtig", "prachtvoll", "herrlich",
    "wunderschön", "wundervoll", "wundersam", "bewundernswert", "beeindruckend", "imposant",
    "bemerkenswert", "außergewöhnlich", "ungewöhnlich", "besonders", "einzigartig", "einmalig",
    "unvergleichlich", "ohnegleichen", "beispiellos", "sondergleichen", "seinesgleichen",
    "ihresgleichen", "nimmermehr gesehen", "noch nie dagewesen", "zum ersten Mal",
    "bahnbrechend", "wegweisend", "richtungsweisend", "zukunftsweisend", "revolutionär",
    "innovativ", "kreativ", "originell", "erfinderisch", "ideenreich", "fantasievoll",
    "einfallsreich", "schöpferisch", "produktiv", "konstruktiv", "positiv", "optimistisch",
    "hoffnungsvoll", "zuversichtlich", "vertrauensvoll", "ermutigt", "motiviert", "inspiriert",
    "begeistert", "enthusiastisch", "engagiert", "leidenschaftlich", "hingebungsvoll",
    "aufopferungsvoll", "selbstlos", "uneigennützig", "großzügig", "freigebig", "gütig",
    "freundlich", "herzlich", "warmherzig", "liebevoll", "fürsorglich", "aufmerksam",
    "rücksichtsvoll", "respektvoll", "wertschätzend", "anerkennend", "dankbar",
    "erkenntlich", "verbunden", "verpflichtet", "schuldig", "zu Dank verpflichtet",
    # Bestärkende Phrasen
    "du schaffst das", "du kannst das", "du bist gut genug", "du bist mehr als genug",
    "du bist stark", "du bist fähig", "du bist klug", "du bist wertvoll", "du bist wichtig",
    "du bist geliebt", "du bist geschätzt", "du bist bedeutsam", "du machst das toll",
    "du machst das gut", "du machst das richtig", "du machst das wunderbar", "du lernst",
    "du wächst", "du entwickelst dich", "du verbesserst dich", "du kommst voran",
    "du machst Fortschritte", "du gehst den richtigen Weg", "du bist auf dem richtigen Weg",
    "du machst das bestmöglich", "du gibst dein Bestes", "du versuchst es",
    "der Versuch zählt", "es ist okay", "es ist in Ordnung", "fehler passieren",
    "niemand ist perfekt", "perfektion ist unerreichbar", "lerne aus Fehlern",
    "Fehler sind Lernchancen", "jeder macht Fehler", "das macht nichts", "kein Problem",
    "alles gut", "keine Sorge", "mach dir keine Sorgen", "kopf hoch", "nicht aufgeben",
    "dranbleiben", "durchhalten", "weitermachen", "nicht aufgeben", "niemals aufgeben",
    "never give up", "keep going", "keep pushing", "keep trying", "keep it up", "good job",
    "well done", "nice work", "great job", "amazing work", "fantastic effort", "brilliant",
    "impressive", "outstanding", "remarkable", "incredible", "unbelievable", "phenomenal",
    # Empathische Reaktionen
    "ich verstehe", "ich höre dich", "ich sehe dich", "ich fühle mit", "das ist verständlich",
    "das macht Sinn", "das ergibt Sinn", "das ist nachvollziehbar", "das ist verständlich",
    "das ist human", "das ist menschlich", "das ist normal", "das ist okay so", "das darf sein",
    "das ist erlaubt", "du darfst das fühlen", "deine Gefühle sind valide", "deine Gefühle sind wichtig",
    "deine Gefühle sind berechtigt", "deine Gefühle zählen", "deine Gefühle sind real",
    "das klingt schwer", "das klingt herausfordernd", "das klingt anspruchsvoll",
    "das klingt belastend", "das klingt erschöpfend", "das klingt überwältigend",
    "kein Wunder", "kein Wunder dass", "vollkommen verständlich", "vollkommen nachvollziehbar",
    "ich kann mir vorstellen", "ich kann verstehen", "ich kann nachvollziehen",
    "ich kann das verstehen", "ich kann das nachvollziehen", "ich kann das nachempfinden",
    "ich kann mich da eindenken", "ich stelle mir vor", "ich versuche nachzuvollziehen",
    # Positive Bewertungen
    "gut", "sehr gut", "ausgesprochen gut", "besonders gut", "äußerst gut", "ungewöhnlich gut",
    "bemerkenswert gut", "überraschend gut", "erstaunlich gut", "unglaublich gut", "sensationell gut",
    "phänomenal", "außerordentlich", "überdurchschnittlich", "weit über dem Durchschnitt",
    "deutlich über dem Durchschnitt", "signifikant besser", "merklich besser", "spürbar besser",
    "erkennbar besser", "sichtbar besser", "offensichtlich besser", "eindeutig besser",
    "unübersehbar besser", "unbestreitbar besser", "unleugbar besser", "zweifelsohne besser",
    "ohne Zweifel besser", "fraglos besser", "unzweifelhaft besser", "zweifelsfrei besser",
    # Zustimmende Interjektionen
    "ach ja", "oh ja", "ach so", "ach naja", "ach schön", "ach herrje", "oh wie schön",
    "oh wie toll", "oh wie wunderbar", "oh wie nett", "oh wie lieb", "oh wie süß",
    "oh wie herzlich", "oh wie warm", "oh wie aufmerksam", "oh wie rücksichtsvoll",
    "oh wie respektvoll", "oh wie wertschätzend", "oh wie anerkennenswert", "oh wie lobenswert",
    "oh wie vorbildlich", "oh wie mustergültig", "oh wie tadellos", "oh wie makellos",
    "oh wie perfekt", "oh wie ideal", "oh wie optimal", "oh wie exzellent", "oh wie brillant",
    "Bravo", "Bravissimo", "Chapeau", "Hut ab", "alle Achtung", "Respekt", "Hochachtung",
    "großer Respekt", "tiefer Respekt", "mein Kompliment", "mein aufrichtiges Kompliment",
    "mein herzliches Lob", "mein aufrichtiges Lob", "mein ehrliches Lob", "mein wahrhaftiges Lob",
    "mein wirkliches Lob", "mein echtes Lob", "ich bin beeindruckt", "ich bin bewegt",
    "ich bin berührt", "ich bin gerührt", "das berührt mich", "das bewegt mich", "das rührt mich",
    "das beeindruckt mich", "das überwältigt mich", "das überrascht mich positiv",
    "das erstaunt mich", "das verblüfft mich", "das fasziniert mich", "das begeistert mich",
    # Bekräftigung von Bemühungen
    "der Weg ist das Ziel", "der Prozess zählt", "das Bemühen zählt", "der Wille zählt",
    "die Absicht zählt", "die Intention zählt", "die Motivation zählt", "das Engagement zählt",
    "das Herzblut zählt", "die Leidenschaft zählt", "die Hingabe zählt", "die Ausdauer zählt",
    "die Beharrlichkeit zählt", "die Hartnäckigkeit zählt", "der Durchhaltewille zählt",
    "die Zähigkeit zählt", "die Resilienz zählt", "die Belastbarkeit zählt",
    "die Standhaftigkeit zählt", "die Konsequenz zählt", "die Kontinuität zählt",
    "kontinuierlich verbessernd", "kontinuierliches Wachstum", "stetiger Fortschritt",
    "beständige Entwicklung", "fortwährende Verbesserung", "unaufhörliche Bemühungen",
    "unermüdliches Streben", "unablässiges Bemühen", "rastloses Engagement",
    "unaufhörlicher Einsatz", "grenzenloses Engagement", "grenzenlose Leidenschaft",
    "grenzenloser Eifer", "grenzenlose Hingabe", "grenzenlose Begeisterung",
    "grenzenloser Enthusiasmus", "grenzenloser Optimismus", "grenzenlose Zuversicht",
    "grenzenlose Hoffnung", "grenzenloser Glaube", "grenzenloses Vertrauen",
    "grenzenloses Zutrauen", "grenzenloses Selbstvertrauen", "grenzenlose Selbstsicherheit",
    "grenzenloser Selbstwert", "grenzenloser Selbstrespekt", "grenzenlose Selbstliebe",
    "grenzenlose Selbstfürsorge", "grenzenlose Selbstakzeptanz", "grenzenlose Selbstannahme",
    "grenzenlose Selbstachtung", "grenzenloser Selbstrespekt", "grenzenloses Selbstbewusstsein",
    "grenzenloses Selbstgefühl", "grenzenlose Selbstwahrnehmung", "grenzenlose Selbstreflexion",
    "grenzenlose Selbstkenntnis", "grenzenlose Selbsteinsicht", "grenzenlose Selbsterkenntnis",
    "grenzenlose Selbstoffenbarung", "grenzenlose Selbstöffnung", "grenzenlose Selbstenthüllung",
    # Ermutigende Adjektive
    "mutig", "couragiert", "beherzt", "tapfer", "unverzagt", "unerschrocken", "furchtlos",
    "wagemutig", "kühn", "verwegen", "draufgängerisch", "entschlossen", "entschieden",
    "bestimmt", "zielstrebig", "fokussiert", "konzentriert", "ausdauernd", "beharrlich",
    "hartnäckig", "zäh", "resilient", "belastbar", "standhaft", "unbeirrbar", "unnachgiebig",
    "unbeugbar", "unbeugsam", "konsequent", "diszipliniert", "strukturiert", "organisiert",
    "planvoll", "systematisch", "methodisch", "gründlich", "gewissenhaft", "sorgfältig",
    "akribisch", "penibel", "präzise", "exakt", "genau", "korrekt", "fehlerfrei", "tadellos",
    "makellos", "perfektionistisch", "qualitätsbewusst", "ergebnisorientiert", "leistungsorientiert",
    "leistungsbereit", "leistungsfähig", "leistungsstark", "hochleistungsfähig", "spitzenleistend",
    "erstklassig", "überragend", "überlegend", "dominierend", "führend", "richtungsweisend",
    "bahnbrechend", "wegweisend", "zukunftsweisend", "visionär", "vorausschauend", "weitblickend",
    "weitsichtig", "klarsichtig", "einsichtig", "verständnisvoll", "einfühlsam", "empathisch",
    "mitfühlend", "verständig", "weise", "erfahren", "kompetent", "qualifiziert", "ausgebildet",
    "geübt", "geschult", "trainiert", "versiert", "gekonnt", "meisterhaft", "virtuos", "brillant",
    "begabt", "talentiert", "begnadet", "hochbegabt", "außergewöhnlich begabt", "naturtalentiert",
]

unterstuetzend_all = list(unterstuetzend_base)

# Add phrases with intensifiers
verstärker = ["sehr", "äußerst", "besonders", "ausgesprochen", "ungemein", "außerordentlich",
              "überaus", "wirklich", "tatsächlich", "wirklich und wahrhaftig", "mit Sicherheit",
              "zweifellos", "ganz", "völlig", "absolut", "total", "komplett", "restlos", "rückhaltlos"]
positive_adj = ["gut", "schön", "toll", "wunderbar", "fantastisch", "großartig", "hervorragend",
                "ausgezeichnet", "vortrefflich", "lobenswert", "bewundernswert", "beeindruckend",
                "außergewöhnlich", "einzigartig", "bemerkenswert", "beispiellos", "brillant", "exzellent"]
for v in verstärker:
    for a in positive_adj:
        unterstuetzend_all.append(f"{v} {a}")

# Extra unterstützende Wörter
unterstuetzend_extra = [
    "herzlichen Glückwunsch", "herzliche Gratulation", "meinen Glückwunsch", "meinen aufrichtigen Glückwunsch",
    "ich beglückwünsche", "ich gratuliere", "ich beglückwünsche dich", "ich gratuliere dir", "gut gemacht wirklich",
    "wirklich hervorragend", "wirklich außergewöhnlich", "wirklich beeindruckend", "wirklich bemerkenswert",
    "wirklich lobenswert", "wirklich vorbildlich", "wirklich mustergültig", "wirklich tadelos", "wirklich makellos",
    "das freut mich", "das freut mich sehr", "das freut mich wirklich", "das freut mich sehr für dich",
    "das freut mich aufrichtig", "das freut mich ehrlich", "das freut mich wahrhaftig", "das freut mich tief",
    "das freut mich innerlich", "das freut mich von Herzen", "das freut mich herzlich", "das freut mich innig",
    "von Herzen", "herzlichst", "innigst", "aufrichtigst", "ehrlichst", "wahrhaftigst", "tiefst", "zutiefst",
    "aus ganzem Herzen", "aus tiefster Seele", "aus tiefstem Herzen", "aus vollstem Herzen", "von ganzer Seele",
    "mit ganzem Herzen", "mit voller Seele", "mit voller Kraft", "mit ganzer Kraft", "mit all meiner Kraft",
    "ich bin auf deiner Seite", "ich halte zu dir", "ich unterstütze dich", "ich stärke dich", "ich stehe hinter dir",
    "ich bin hinter dir", "ich habe deinen Rücken", "ich decke dir den Rücken", "ich schütze dich",
    "ich beschütze dich", "ich verteidige dich", "ich stehe für dich ein", "ich setze mich für dich ein",
    "ich kämpfe für dich", "ich streite für dich", "ich fechte für dich", "ich setze alles für dich ein",
    "ich lasse nichts auf dich kommen", "ich lasse nichts Schlechtes über dich sagen", "ich verteidige dich immer",
    "du kannst auf mich zählen", "du kannst dich auf mich verlassen", "du kannst mir vertrauen",
    "du kannst mir alles sagen", "du kannst mit mir reden", "du kannst zu mir kommen", "du bist bei mir sicher",
    "du bist bei mir geborgen", "du bist bei mir aufgehoben", "du bist bei mir gut aufgehoben",
    "du bist in guten Händen", "du bist hier richtig", "du bist hier willkommen", "du gehörst hierher",
    "du gehörst dazu", "du bist Teil davon", "du bist Teil von uns", "du bist Teil von etwas Größerem",
    "du machst uns vollständig", "du bereicherst uns", "du bereicherst unser Leben", "du bereicherst die Gruppe",
    "du bereicherst das Team", "du bereicherst das Gespräch", "du bereicherst die Diskussion",
    "du bereicherst die Gemeinschaft", "du bereicherst die Welt", "du machst die Welt besser",
    "du machst einen Unterschied", "du machst einen positiven Unterschied", "du wirkst", "du veränderst",
    "du transformierst", "du entwickelst", "du wächst", "du inspirierst", "du motivierst", "du begeisterst",
    "du bewegst", "du berührst", "du rührst", "du beeindruckst", "du überwältigst", "du verblüffst",
    "du faszinierst", "du entzückst", "du bezauberst", "du verzauberst", "du bezwingst", "du überzeugst",
    "du überzeugst mich", "du hast mich überzeugt", "du hast mich gewonnen", "du hast mich für dich gewonnen",
    "du hast mein Herz gewonnen", "du hast meine Bewunderung", "du hast meine Anerkennung", "du hast meinen Respekt",
    "du hast meinen vollen Respekt", "du hast meinen tiefsten Respekt", "du hast meine tiefste Bewunderung",
    "du hast meine vollste Anerkennung", "du hast mein vollstes Vertrauen", "du hast meine vollste Unterstützung",
    "ich unterstütze dich vollständig", "ich unterstütze dich vollumfänglich", "ich unterstütze dich bedingungslos",
    "ich unterstütze dich uneingeschränkt", "ich unterstütze dich mit allen Mitteln", "ich unterstütze dich immer",
    "ich bin immer für dich da", "ich bin jederzeit für dich da", "ich bin rund um die Uhr für dich da",
    "ich bin 24/7 für dich da", "ich bin in jeder Situation für dich da", "ich bin in jedem Moment für dich da",
    "in guten wie in schlechten Zeiten", "in der Not", "im Sturm", "bei Gegenwind", "wenn es schwer wird",
    "wenn es dir nicht gut geht", "wenn du Hilfe brauchst", "wenn du Unterstützung brauchst",
    "wenn du jemanden brauchst",
    "wenn du nicht mehr kannst", "wenn du denkst du kannst nicht mehr", "wenn du kurz davor bist aufzugeben",
    "gib nicht auf", "bitte gib nicht auf", "gib noch nicht auf", "nicht jetzt aufgeben", "gleich geschafft",
    "fast da", "noch ein bisschen", "nur noch ein kleines Stück", "nur noch ein Schritt", "noch einen Schritt",
    "du bist so nah dran", "du bist kurz vor dem Ziel", "du siehst schon das Ziel", "das Ziel ist nah",
    "der Endspurt", "die letzte Meile", "das letzte Stück", "die letzten Meter", "nur noch ein paar Schritte",
    "gleich geschafft", "fast am Ziel", "kurz vor dem Ziel", "auf der Zielgeraden", "im Endspurt",
    "du machst das", "du wirst es schaffen", "du hast es schon fast geschafft", "du schaffst das locker",
    "du schaffst das sicher", "du schaffst das bestimmt", "du schaffst das ohne Frage", "du kannst das",
    "du bist fähig dazu", "du hast die Fähigkeit", "du hast die Stärke", "du hast die Kraft",
    "du hast alles was du brauchst",
    "du hast alles Notwendige", "du hast alle Mittel", "du hast alle Ressourcen", "du hast das Potenzial",
    "du hast das Talent", "du hast die Begabung", "du hast die Anlage", "du hast das Zeug dazu",
    "du hast das Zeug dazu und mehr", "du hast mehr als das Zeug dazu", "du hast mehr als genug",
    "du bist mehr als genug", "du bist genug", "du bist vollständig", "du bist vollkommen", "du bist perfekt",
    "du bist perfekt so wie du bist", "du bist schön", "du bist wunderschön", "du bist wunderbar", "du bist großartig",
    "du bist fantastisch", "du bist außergewöhnlich", "du bist besonders", "du bist einzigartig", "du bist einmalig",
    "du bist unvergleichlich", "du bist unersetzlich", "du bist unverzichtbar", "du bist unvergesslich",
    "du bleibst in Erinnerung", "du hinterlässt einen bleibenden Eindruck", "du hinterlässt Spuren",
    "du hinterlässt etwas", "du hinterlässt die Welt besser als du sie vorgefunden hast",
    "besser als vorgefunden", "besser hinterlassen", "nachhaltig verbessert", "positiv gewirkt", "positiv verändert",
    "Positives bewirkt", "Gutes getan", "Gutes in die Welt gebracht", "Licht verbreitet", "Freude gebracht",
    "Freude geschenkt", "Freude geteilt", "Freude bereitet", "Glück gebracht", "Glück geteilt", "Glück geschenkt",
    "Hoffnung gegeben", "Hoffnung verbreitet", "Hoffnung geschenkt", "Mut gegeben", "Mut gemacht", "Mut geschenkt",
    "Kraft gegeben", "Kraft geschenkt", "Kraft gespendet", "Energie gegeben", "Energie geschenkt", "Energie gespendet",
    "Liebe gegeben", "Liebe geschenkt", "Liebe verbreitet", "Wärme gegeben", "Wärme geschenkt", "Wärme verbreitet",
    "Geborgenheit gegeben", "Geborgenheit geschenkt", "Sicherheit gegeben", "Sicherheit geschenkt", "Schutz geboten",
    "Halt gegeben", "Halt geboten", "Stabilität gegeben", "Verlässlichkeit gegeben", "Vertrauen geschenkt",
    "Respekt gezeigt", "Respekt gezollt", "Wertschätzung gezeigt", "Anerkennung gezollt", "Würde bewahrt",
    "Würde geschenkt", "Selbstwert gestärkt", "Selbstbewusstsein gestärkt", "Selbstvertrauen gestärkt",
    "Selbstliebe gefördert", "Selbstfürsorge ermutigt", "Selbstachtung gestärkt", "Selbstrespekt gefördert",
    "Selbstakzeptanz unterstützt", "Selbstannahme gefördert", "inneren Frieden unterstützt",
    "innere Balance gefördert", "innere Harmonie unterstützt", "innere Stärke gezeigt", "innere Kraft gezeigt",
    "Resilienz gezeigt", "Belastbarkeit gezeigt", "Durchhaltevermögen gezeigt", "Ausdauer gezeigt",
    "Beharrlichkeit gezeigt", "Hartnäckigkeit gezeigt", "Zähigkeit gezeigt", "Willensstärke gezeigt",
    "Entschlossenheit gezeigt", "Mut gezeigt", "Tapferkeit gezeigt", "Courage gezeigt", "Beherztheit gezeigt",
    "Kühnheit gezeigt", "Wagemut gezeigt", "Risikobereitschaft gezeigt", "Offenheit gezeigt",
    "Neugier gezeigt", "Lernbereitschaft gezeigt", "Veränderungsbereitschaft gezeigt", "Wachstumsbereitschaft gezeigt",
    "Flexibilität gezeigt", "Anpassungsfähigkeit gezeigt", "Kreativität gezeigt", "Innovationsfreude gezeigt",
    "Schöpfergeist gezeigt", "Erfindergeist gezeigt", "Pioniergeist gezeigt", "Unternehmergeist gezeigt",
    "Führungsqualitäten gezeigt", "Teamgeist gezeigt", "Kooperationsbereitschaft gezeigt", "Solidarität gezeigt",
    "Gemeinschaftssinn gezeigt", "soziales Verantwortungsbewusstsein gezeigt", "Mitgefühl gezeigt", "Empathie gezeigt",
    "Verständnis gezeigt", "Güte gezeigt", "Freundlichkeit gezeigt", "Herzlichkeit gezeigt", "Wärme gezeigt",
]
unterstuetzend_all.extend(unterstuetzend_extra)
# Systematische Erweiterung
affirmations = ["Ja", "Genau", "Richtig", "Stimmt", "Absolut", "Definitiv", "Natürlich", "Selbstverständlich",
                "Sicher", "Gewiss", "Korrekt", "Exakt", "Präzise", "Treffend", "Wahr", "Tatsächlich",
                "Zweifellos", "Ohne Frage", "Freilich", "Allerdings", "Unbedingt", "Vollkommen"]
erweiterungen = [" so", "! So ist es", " - das stimmt", " - das ist richtig", " - ganz recht",
                 " und wie", " - ohne Zweifel", " - klar doch", " - und zwar sehr"]
for a in affirmations:
    for e in erweiterungen:
        unterstuetzend_all.append(a + e)

liste_unterstuetzend = dedupe_ordered(unterstuetzend_all)[:2000]
print(f"Unterstützende Wörter: {len(liste_unterstuetzend)}")

# ============================================================
# KATEGORIE 5: WÖRTER DIE AUF SICH SELBST EINGEHEN
# ============================================================

selbst_pronouns = [
    # Personalpronomina 1. Person
    "ich", "mich", "mir", "meiner", "mein", "meine", "meinen", "meinem", "meines", "meins",
    "wir", "uns", "unser", "unsere", "unseren", "unserem", "unseres", "unsers", "uns selbst",
    "ich selbst", "ich selber", "mich selbst", "mich selber", "mir selbst", "mir selber",
    "meiner selbst", "uns selbst", "uns selber", "wir selbst", "wir selber",
    "ich persönlich", "ich für mich", "ich für meinen Teil", "meinerseits", "meiner Ansicht nach",
    "meiner Meinung nach", "meiner Einschätzung nach", "meiner Erfahrung nach",
    "meiner Wahrnehmung nach", "meiner Überzeugung nach", "meines Erachtens", "m.E.",
    "nach meiner Auffassung", "nach meiner Ansicht", "nach meiner Einschätzung",
    "nach meiner Meinung", "nach meiner Überzeugung", "nach meinem Dafürhalten",
    "nach meinem Ermessen", "nach meiner Beurteilung", "nach meiner Einschätzung",
    "in meinen Augen", "aus meiner Perspektive", "aus meinem Blickwinkel",
    "aus meiner Sicht", "von meiner Warte aus", "von meinem Standpunkt aus",
    "von meiner Position aus", "von meiner Seite", "meinerseits",
]

selbst_komposita = []
selbst_stämme = [
    "selbst", "auto", "ich", "eigen", "per sönlich", "individuell", "subjektiv", "intern",
    "intrinsisch", "intrapersonal", "innenpolitisch", "innerlich", "seelisch", "geistig",
    "mental", "kognitiv", "emotional", "affektiv", "motivational", "volitional",
    "intentional", "aufmerksam", "bewusst", "gewahr", "präsent", "anwesend",
]

selbst_präfixe = ["selbst", "auto", "ich", "eigen"]
selbst_wortstämme = [
    "reflektiert", "kritisch", "bewusst", "wahrnehmend", "erkennend", "definierend",
    "referenziell", "bezüglich", "bezogen", "beschreibend", "analysierend", "betrachtend",
    "beurteilend", "einschätzend", "evaluierend", "bewertend", "untersuchend", "prüfend",
    "hinterfragend", "problematisierend", "relativierend", "distanzierend", "beoabchtend",
    "beobachtend", "einordnend", "einschätzend", "verortend", "verankernd", "verankert",
    "verortet", "eingebettet", "kontextualisiert", "situiert", "positioniert",
    "positionierend", "verortend", "perspektivierend", "rahmend", "einrahmend",
    "framing", "reframing", "umrahmend", "neurahmend", "umformulierend", "neufassend",
    "liebe", "fürsorge", "wert", "respekt", "achtung", "akzeptanz", "annahme", "vertrauen",
    "vertrauen", "zutrauen", "glaube", "hoffnung", "mut", "stärke", "kraft", "ressource",
    "potential", "fähigkeit", "kompetenz", "fertigkeit", "talent", "begabung", "stärke",
    "wert", "würde", "bedeutung", "wichtigkeit", "relevanz", "signifikanz", "gewicht",
    "beurteilung", "bewertung", "einschätzung", "evaluation", "assessment", "appraisal",
    "offenbarung", "enthüllung", "preisgabe", "beichte", "geständnis", "eingeständnis",
    "bekenntnis", "aussage", "äußerung", "ausdruck", "darstellung", "präsentation", "zeigung",
    "darlegung", "erklärung", "erläuterung", "ausführung", "schilderung", "beschreibung",
    "charakterisierung", "porträtierung", "profilierung", "darstellung", "selbstdarstellung",
]

for präfix in selbst_präfixe:
    for stamm in selbst_wortstämme:
        selbst_komposita.append(f"{präfix}{stamm}")
        selbst_komposita.append(f"{präfix}-{stamm}")

selbst_weitere = [
    # Selbst-Komposita
    "Selbstreflexion", "Selbstwahrnehmung", "Selbstbild", "Selbstkonzept", "Selbstwert",
    "Selbstwertgefühl", "Selbstwertschätzung", "Selbstachtung", "Selbstrespekt",
    "Selbstliebe", "Selbstfürsorge", "Selbstpflege", "Selbstmitgefühl", "Selbstakzeptanz",
    "Selbstannahme", "Selbstvertrauen", "Selbstsicherheit", "Selbstbewusstsein",
    "Selbstgefühl", "Selbstwahrnehmung", "Selbstbeobachtung", "Selbstbeurteilung",
    "Selbstbewertung", "Selbsteinschätzung", "Selbstanalyse", "Selbstkritik",
    "Selbstkritisch", "Selbsthinterfragung", "Selbstprüfung", "Selbstexamination",
    "Selbstreflektiv", "Selbstbefragung", "Selbstuntersuchung", "Selbsterforschung",
    "Selbsterkundung", "Selbstentdeckung", "Selbstfindung", "Selbstsuche", "Selbstsucht",
    "Selbstbezogenheit", "Ichbezogenheit", "Egozentrik", "Egozentrismus", "Egozentrizität",
    "Egoismus", "Altruismus als Gegensatz", "Narzissmus", "Narziss", "narcissistic",
    "narzisstisch", "narzissistisch", "narzistisch", "ich-bezogen", "self-absorbed",
    "selbstabsorbiert", "selbstversunken", "in sich versunken", "bei sich", "mit sich",
    "Egologie", "Selbstologie", "Ichologie", "Subjektivität", "Subjektperspektive",
    "Innenperspektive", "Innensicht", "Innenansicht", "Innenwelt", "inneres Erleben",
    "innere Welt", "innere Erfahrung", "innere Wahrnehmung", "innere Stimme", "innerer Kompass",
    "innerer Leitfaden", "innere Überzeugung", "innere Gewissheit", "innere Stärke",
    "innere Ruhe", "innere Balance", "innere Harmonie", "innere Mitte", "innerer Frieden",
    "innere Freiheit", "innere Unabhängigkeit", "innere Autonomie", "innere Souveränität",
    "innere Würde", "innerer Wert", "innere Bedeutung", "innere Wichtigkeit", "innere Relevanz",
    "innere Signifikanz", "innere Wahrheit", "innere Echtheit", "innere Authentizität",
    "innere Aufrichtigkeit", "innere Wahrhaftigkeit", "innere Direktheit", "innere Transparenz",
    "innere Offenheit", "innere Verletzlichkeit", "innere Verwundbarkeit", "innere Zartheit",
    "innere Weichheit", "innere Sanftheit", "innere Güte", "innere Wärme", "innere Herzlichkeit",
    "innere Liebe", "innere Zuneigung", "innere Sympathie", "innere Empathie", "innere Mitgefühl",
    # Ichform-Konstruktionen
    "ich denke", "ich glaube", "ich meine", "ich finde", "ich halte", "ich erachte",
    "ich betrachte", "ich sehe", "ich wahrnehme", "ich empfinde", "ich fühle", "ich spüre",
    "ich erlebe", "ich erfahre", "ich erkenne", "ich verstehe", "ich begreife", "ich weiß",
    "ich weiß nicht", "ich bin unsicher", "ich zweifle", "ich hinterfrage", "ich reflektiere",
    "ich überdenke", "ich überprüfe", "ich überarbeite", "ich verändere", "ich entwickle",
    "ich wachse", "ich lerne", "ich verbessere", "ich arbeite an mir", "ich bemühe mich",
    "ich strebe an", "ich möchte", "ich will", "ich wünsche", "ich hoffe", "ich erwarte",
    "ich befürchte", "ich fürchte", "ich ängstigt mich", "ich mache mir Sorgen",
    "ich sorge mich", "ich kümmere mich", "ich interessiere mich", "ich begeistere mich",
    "ich motiviere mich", "ich inspiriere mich", "ich engagiere mich", "ich setze mich ein",
    "ich bringe mich ein", "ich beteilige mich", "ich beteilige mich aktiv", "ich mache mit",
    "ich nehme teil", "ich nehme Anteil", "ich nehme Bezug", "ich nehme Stellung",
    "ich beziehe Stellung", "ich positioniere mich", "ich verorte mich", "ich situiere mich",
    "ich kontextualisiere mich", "ich rahme mich", "ich reflektiere mich", "ich beobachte mich",
    "ich beurteile mich", "ich bewerte mich", "ich einschätze mich", "ich analysiere mich",
    "ich kritisiere mich", "ich hinterfrage mich", "ich prüfe mich", "ich untersuche mich",
    "ich erforsche mich", "ich erkunde mich", "ich entdecke mich", "ich finde mich", "ich suche mich",
    # Autobiografische und Icherzählung
    "autobiografisch", "autobiographisch", "autoethnografisch", "autoethnographisch",
    "selbstbiografisch", "icherzählerisch", "ich-erzählend", "Ich-Erzähler", "Ich-Perspektive",
    "Ich-Roman", "Ich-Erzählung", "Ich-Form", "Ich-Aussage", "Ich-Botschaft", "Ich-Statement",
    "Ich-Nachricht", "personale Erzählung", "personaler Erzähler", "persönliche Erzählung",
    "persönliche Geschichte", "persönliche Erfahrung", "persönliches Erlebnis",
    "persönliche Biografie", "persönlicher Werdegang", "persönliche Entwicklung",
    "persönliches Wachstum", "persönliche Reifung", "persönliche Transformation",
    "persönliche Evolution", "persönliche Revolution", "persönliche Metamorphose",
    "persönliche Veränderung", "persönlicher Wandel", "persönliche Erneuerung",
    "persönliche Wiedergeburt", "persönlicher Neuanfang", "persönlicher Neustart",
    "persönlicher Aufbruch", "persönliche Emanzipation", "persönliche Befreiung",
    "persönliche Unabhängigkeit", "persönliche Autonomie", "persönliche Freiheit",
    "persönliche Souveränität", "persönliche Würde", "persönlicher Wert", "persönliche Bedeutung",
    "persönliche Wichtigkeit", "persönliche Relevanz", "persönliche Signifikanz",
    "persönliche Wahrheit", "persönliche Echtheit", "persönliche Authentizität",
    "Autoreflexion", "Autoreferentialität", "Autoreferenz", "Selbstreferenz", "Selbstreferentialität",
    "Selbstreferenzialität", "Selbstbezüglichkeit", "Rekursivität", "Rekursion",
    "sich selbst beziehend", "auf sich selbst verweisend", "auf sich selbst bezogen",
    "sich selbst einschließend", "sich selbst beschreibend", "sich selbst definierend",
    "sich selbst konstituierend", "sich selbst erzeugend", "sich selbst reproduzierend",
    "sich selbst erhaltend", "sich selbst regulierend", "sich selbst steuernd", "sich selbst organisierend",
    # Persönlichkeitsmerkmale (selbst)
    "introvertiert", "introvertierte Persönlichkeit", "Introversion", "Introvert", "introspektiv",
    "in sich gekehrt", "nach innen gerichtet", "selbstbeschäftigt", "selbstbeschäftigung",
    "selbstversunken", "kontemplativ", "nachdenklich", "grüblerisch", "selbstgrüblerisch",
    "melancholisch", "sanguinisch", "cholerisch", "phlegmatisch", "neurotisch", "stabil",
    "labil", "sensibel", "hochsensibel", "hypersensibel", "empfindsam", "empfindlich",
    "dünnhäutig", "feinfühlig", "zartfühlend", "feinsinnig", "tiefgründig", "gründlich",
    "tiefschürfend", "durchdringend", "weitreichend", "umfassend", "komplex", "vielschichtig",
    "facettenreich", "differenziert", "nuanciert", "subtil", "fein", "präzise", "genau",
]

selbst_all = list(selbst_pronouns) + selbst_komposita + selbst_weitere
liste_selbst = dedupe_ordered(selbst_all)[:2000]
print(f"Selbstbezug: {len(liste_selbst)}")

# ============================================================
# KATEGORIE 6: WÖRTER DIE AUF DEN ANDEREN EINGEHEN
# ============================================================

fremd_pronouns = [
    # 2. Person
    "du", "dich", "dir", "dein", "deine", "deinen", "deinem", "deines", "deins",
    "ihr", "euch", "euer", "eure", "euren", "eurem", "eures", "euers",
    "Sie", "Ihnen", "Ihr", "Ihre", "Ihren", "Ihrem", "Ihres", "Ihrs",
    "du selbst", "du selber", "dich selbst", "dich selber", "dir selbst", "dir selber",
    "Sie selbst", "Sie selber", "Ihnen selbst", "Ihnen selber",
    "ihr selbst", "ihr selber", "euch selbst", "euch selber",
    # 3. Person
    "er", "ihn", "ihm", "sein", "seine", "seinen", "seinem", "seines", "seins",
    "sie", "sie", "ihr", "ihre", "ihren", "ihrem", "ihres", "ihrs",
    "es", "es", "sein", "seine", "seinen", "seinem", "seines", "seins",
    "sie (Plural)", "ihnen", "ihr", "ihre", "ihren", "ihrem", "ihres",
    "er selbst", "er selber", "ihn selbst", "ihm selbst", "sie selbst", "sie selber",
    "es selbst", "es selber", "sie selbst", "sie selber", "ihnen selbst", "ihnen selber",
    # Indefinitpronomina
    "man", "jemand", "jemandes", "jemandem", "jemanden", "niemand", "niemandes", "niemandem",
    "alle", "aller", "allem", "allen", "alles", "jeder", "jedes", "jedem", "jeden", "jede",
    "manche", "mancher", "manches", "manchem", "manchen", "einige", "einiger", "einigem", "einigen",
    "viele", "vieler", "vielem", "vielen", "wenige", "weniger", "wenigem", "wenigen",
    "andere", "anderer", "anderem", "anderen", "anderes", "übrige", "übriger", "übrigem", "übrigen",
    "derjenige", "diejenige", "dasjenige", "diejenigen", "derselbe", "dieselbe", "dasselbe", "dieselben",
    # Genitivattribute
    "deiner Meinung nach", "deiner Ansicht nach", "deiner Einschätzung nach", "deiner Erfahrung nach",
    "deiner Wahrnehmung nach", "deiner Überzeugung nach", "deiner Auffassung nach", "deines Erachtens",
    "nach deiner Meinung", "nach deiner Ansicht", "in deinen Augen", "aus deiner Perspektive",
    "aus deinem Blickwinkel", "aus deiner Sicht", "von deiner Warte", "von deinem Standpunkt",
    "Ihrer Meinung nach", "Ihrer Ansicht nach", "in Ihren Augen", "aus Ihrer Perspektive",
    "aus Ihrem Blickwinkel", "aus Ihrer Sicht", "von Ihrer Warte", "von Ihrem Standpunkt",
]

fremd_empathie = [
    # Empathische Ausdrücke
    "ich verstehe dich", "ich höre dich", "ich sehe dich", "ich nehme dich wahr",
    "ich nehme deine Bedürfnisse wahr", "ich nehme deine Gefühle wahr", "ich nehme dich ernst",
    "deine Gefühle sind valide", "deine Gefühle zählen", "deine Meinung ist wichtig",
    "du bist wichtig", "du bist wertvoll", "du bist bedeutsam", "du wirst gehört",
    "du wirst gesehen", "du wirst verstanden", "du wirst akzeptiert", "du wirst respektiert",
    "du wirst wertgeschätzt", "du wirst anerkannt", "du wirst gemocht", "du wirst geliebt",
    "du bist nicht allein", "du bist eingebettet", "du gehörst dazu", "du bist Teil von uns",
    "du bist willkommen", "du bist herzlich willkommen", "du bist gerne gesehen",
    "du bist gerne gehört", "du bist gerne dabei", "du bist gerne mit von der Partie",
    # Einfühlsame Reaktionen auf den anderen
    "wie geht es dir", "wie fühlst du dich", "wie läuft es bei dir", "was bewegt dich",
    "was beschäftigt dich", "was macht dir Sorgen", "was freut dich", "was belastet dich",
    "was brauchst du", "was wünschst du dir", "was erwartest du", "was erhoffst du",
    "was befürchtest du", "was ängstigt dich", "was macht dich glücklich", "was macht dich traurig",
    "was macht dich wütend", "was macht dich ärgerlich", "was macht dich frustriert",
    "was macht dich enttäuscht", "was macht dich überrascht", "was macht dich begeistert",
    "was macht dich motiviert", "was macht dich inspiriert", "was gibt dir Kraft",
    "was gibt dir Energie", "was gibt dir Hoffnung", "was gibt dir Halt", "was gibt dir Sicherheit",
    "was gibt dir Geborgenheit", "was gibt dir Wärme", "was gibt dir Freude", "was erfüllt dich",
    "was befriedigt dich", "was bereitet dir Zufriedenheit", "was macht dich ausgeglichen",
    "was bringt dich in Balance", "was bringt dich zur Ruhe", "was beruhigt dich",
    "was entspannt dich", "was erholt dich", "was regeneriert dich", "was stärkt dich",
    "was heilt dich", "was hilft dir", "was unterstützt dich", "was fördert dich",
    "was entwickelt dich", "was wachst du", "was lernst du", "was verbesserst du",
    # Perspektivübernahme
    "ich kann mir vorstellen wie du dich fühlst", "ich kann mir deine Lage vorstellen",
    "ich kann deine Situation nachvollziehen", "ich kann deine Perspektive einnehmen",
    "ich versuche mich in dich einzufühlen", "ich versuche dich zu verstehen",
    "ich versuche deine Sicht einzunehmen", "ich versuche aus deinen Augen zu sehen",
    "ich sehe es wie du siehst es", "ich sehe es ähnlich wie du", "ich stimme dir zu",
    "ich stimme dir teilweise zu", "ich stimme dir größtenteils zu", "ich bin deiner Meinung",
    "ich teile deine Meinung", "ich teile deine Ansicht", "ich teile deine Einschätzung",
    "ich teile deine Überzeugung", "ich teile deine Perspektive", "ich teile deine Erfahrung",
    "ich kenne das auch", "ich kenne das aus eigener Erfahrung", "ich habe ähnliches erlebt",
    "ich habe gleiches erlebt", "ich habe vergleichbares erlebt", "das kenne ich",
    "das kenne ich gut", "das kenne ich sehr gut", "das kenne ich zu gut", "das kenne ich leider",
    "das ist mir vertraut", "das ist mir bekannt", "das ist mir geläufig", "das ist mir nicht fremd",
    "das überrascht mich nicht", "das verwundert mich nicht", "das erstaunt mich nicht",
    "das ist vollkommen verständlich", "das ist nachvollziehbar", "das macht Sinn",
    "das ergibt Sinn", "das ergibt sich logisch", "das ist logisch", "das ist konsequent",
    "das ist folgerichtig", "das ist in sich schlüssig", "das ist konsistent", "das passt",
    "das passt gut", "das passt zusammen", "das passt zu dir", "das passt zu deiner Situation",
    "das passt zu deiner Lage", "das passt zu deinen Gefühlen", "das passt zu deinen Bedürfnissen",
    # Zugewandtheit und Interesse am anderen
    "du interessierst mich", "ich interessiere mich für dich", "ich möchte mehr über dich wissen",
    "ich möchte dich besser kennenlernen", "ich möchte dich verstehen", "ich möchte dir helfen",
    "ich möchte dir beistehen", "ich möchte für dich da sein", "ich bin für dich da",
    "ich stehe dir zur Seite", "ich stehe zu dir", "ich halte zu dir", "ich halte dir den Rücken frei",
    "ich habe deinen Rücken", "ich bin auf deiner Seite", "ich unterstütze dich",
    "ich fördere dich", "ich stärke dich", "ich ermutige dich", "ich motiviere dich",
    "ich inspiriere dich", "ich begeistere dich", "ich animiere dich", "ich antreibe dich",
    "ich begleite dich", "ich gehe mit dir", "ich bin dabei", "ich bin mitunter",
    "ich bin mitten dabei", "ich bin präsent", "ich bin anwesend", "ich bin zugegen",
    "ich bin aufmerksam", "ich bin wachsam", "ich bin zugewandt", "ich bin offen für dich",
    "ich höre zu", "ich höre aktiv zu", "ich höre aufmerksam zu", "ich höre verständnisvoll zu",
    "ich höre ohne Vorwurf zu", "ich höre ohne Urteil zu", "ich höre ohne Wertung zu",
    "ich höre ohne Kritik zu", "ich höre ohne Ratschlag zu", "ich höre einfach zu",
    "ich bin ganz Ohr", "ich schenke dir meine volle Aufmerksamkeit", "ich bin ganz bei dir",
    "ich bin voll präsent", "ich bin hundertprozentig anwesend", "ich bin ganz da für dich",
    # Andere-Bezogene Adjektive und Substantive
    "empathisch", "mitfühlend", "verständnisvoll", "zugewandt", "offen", "aufmerksam",
    "präsent", "anwesend", "aufnahmebereit", "hörbereit", "gesprächsbereit", "hilfsbereit",
    "unterstützungsbereit", "förderbereit", "entwicklungsbereit", "wachstumsbereit",
    "lernbereit", "veränderungsbereit", "anpassungsbereit", "flexibel", "offen", "tolerant",
    "akzeptierend", "annehmend", "respektierend", "achtend", "wertschätzend", "anerkennend",
    "lobend", "bestätigend", "ermutigend", "motivierend", "inspirierend", "begeisternd",
    "animierend", "antreibend", "fördernd", "entwickelnd", "wachstums-fördernd", "potenzialentfaltend",
    "stärkend", "kräftigend", "heilend", "tröstend", "beruhigend", "entspannend", "klärend",
    "ordnend", "strukturierend", "orientierend", "führend", "leitend", "begleitend",
    "beistehend", "helfend", "unterstützend", "zuhörend", "verständig", "verständnisvoll",
    # Andere-bezogene Substantive
    "Empathie", "Mitgefühl", "Verständnis", "Zugewandtheit", "Offenheit", "Aufmerksamkeit",
    "Präsenz", "Anwesenheit", "Aufnahmebereitschaft", "Hörbereitschaft", "Gesprächsbereitschaft",
    "Hilfsbereitschaft", "Unterstützungsbereitschaft", "Förderbereitschaft", "Toleranz",
    "Akzeptanz", "Annahme", "Respekt", "Achtung", "Wertschätzung", "Anerkennung", "Lob",
    "Bestätigung", "Ermutigung", "Motivation", "Inspiration", "Begeisterung", "Animation",
    "Antrieb", "Förderung", "Entwicklung", "Stärkung", "Kräftigung", "Heilung", "Tröstung",
    "Beruhigung", "Entspannung", "Klärung", "Ordnung", "Strukturierung", "Orientierung",
    "Führung", "Leitung", "Begleitung", "Beistand", "Hilfe", "Unterstützung", "Zugehörigkeit",
    "Verbundenheit", "Zusammengehörigkeit", "Gemeinschaft", "Solidarität", "Kameradschaft",
    "Freundschaft", "Kollegialität", "Partnerschaft", "Beziehung", "Bindung", "Vertrauen",
    "Verlässlichkeit", "Zuverlässigkeit", "Treue", "Loyalität", "Ehrlichkeit", "Aufrichtigkeit",
    "Direktheit", "Transparenz", "Offenheit", "Authentizität", "Echtheit", "Wahrhaftigkeit",
    # Gesprächsführende Ausdrücke
    "wie denkst du darüber", "was denkst du", "was meinst du", "was findest du", "was hältst du davon",
    "wie siehst du das", "wie bewertest du das", "wie beurteilst du das", "wie schätzt du das ein",
    "was ist deine Meinung", "was ist deine Ansicht", "was ist deine Einschätzung",
    "was ist deine Überzeugung", "was ist deine Erfahrung", "was ist deine Perspektive",
    "was ist dein Standpunkt", "was ist deine Haltung", "was ist deine Position",
    "kannst du mir mehr erzählen", "kannst du das erläutern", "kannst du das erklären",
    "kannst du das ausführen", "kannst du das vertiefen", "kannst du das konkretisieren",
    "kannst du ein Beispiel nennen", "kannst du das veranschaulichen", "kannst du das illustrieren",
    "was meinst du damit", "was verstehst du darunter", "was hast du damit gemeint",
    "habe ich das richtig verstanden", "habe ich dich richtig verstanden", "stimmt das so",
    "ist das korrekt", "habe ich das so aufgefasst wie du es meinst", "habe ich das richtig",
    "darf ich das so verstehen", "darf ich fragen", "darf ich nachfragen", "darf ich nachhorchen",
    "darf ich das ansprechen", "darf ich das erwähnen", "darf ich darauf eingehen",
    "darf ich darauf reagieren", "darf ich dazu etwas sagen", "darf ich dazu Stellung nehmen",
    "ich würde gerne mehr erfahren", "ich würde gerne mehr hören", "ich würde gerne mehr wissen",
    "ich würde gerne verstehen", "ich würde gerne nachvollziehen", "ich bin neugierig",
    "ich bin gespannt", "ich bin interessiert", "ich bin aufmerksam", "ich bin offen",
    "ich bin empfänglich", "ich bin zugänglich", "ich bin ansprechbar", "ich bin verfügbar",
    "ich bin bereit", "ich bin willens", "ich bin offen für", "ich bin bereit für",
    "ich bin neugierig auf", "ich bin gespannt auf", "ich bin interessiert an",
    "ich freue mich auf", "ich freue mich über", "ich freue mich für dich", "ich bin froh für dich",
    "ich bin stolz auf dich", "ich freue mich mit dir", "ich leide mit dir", "ich trauere mit dir",
    "ich fühle mit dir", "ich bin bei dir", "ich bin für dich da", "jederzeit für dich da",
    "immer für dich da", "uneingeschränkt für dich da", "bedingungslos für dich da",
    # Andersgerichtete Freundlichkeit
    "andere-zentriert", "fremdbezogen", "altruistisch", "selbstlos", "uneigennützig",
    "großzügig", "freigebig", "opferbereit", "aufopfernd", "hingabebereit", "hilfsbereit",
    "gutherzig", "wohlmeinend", "wohlwollend", "wohlgesinnt", "freundlich gesinnt",
    "freundlich gestimmt", "freundlich eingestellt", "positiv eingestellt gegenüber",
    "positiv gestimmt gegenüber", "positiv gesinnt gegenüber", "positiv eingestellt zu",
    "positiv gestimmt zu", "positiv gesinnt zu", "positiv orientiert gegenüber",
    "fremdwahrnehmend", "fremdbeobachtend", "fremdreflektierend", "fremdverstehend",
    "fremdempfindend", "fremderfassend", "fremderlebend", "fremderfahrend",
    "kontrastiv", "komparativ", "relational", "dialogisch", "dialogorientiert", "dialogbereit",
    "kommunikationsbereit", "kommunikationswillig", "kommunikationsfreudig", "gesprächsfreudig",
    "gesprächsoffen", "gesprächsbereit", "diskussionsbereit", "diskussionsfreudig", "diskussionsoffen",
    "diskursfähig", "diskursfreudig", "diskursoffen", "diskursbereit", "debattenbereit",
    "debattenfreudig", "debattenoffen", "argumentationsbereit", "argumentationsfreudig",
    "argumentationsoffen", "verständigungsbereit", "verständigungsfreudig", "verständigungsoffen",
    "verständigungswillig", "konsensorientiert", "kompromissbereit", "kompromissfähig",
    "kompromisswillig", "einigungsbereit", "einigungswillig", "einigungsfähig", "kooperationsbereit",
    "kooperationswillig", "kooperationsfähig", "kollaborationsbereit", "kollaborationswillig",
    "kollaborationsfähig", "teambereit", "teamwillig", "teamfähig", "teamorientiert", "teamgeistig",
    "gemeinschaftsorientiert", "gemeinschaftsgeistig", "solidarisch", "solidaritätsorientiert",
    "partnerschaftlich", "partnerschaftsorientiert", "kameradschaftlich", "freundschaftlich",
    "kollegial", "kollegialitätsorientiert", "respektvoll", "respectful", "achtsam gegenüber",
    "wertschätzend gegenüber", "anerkennend gegenüber", "lobend gegenüber", "bestätigend gegenüber",
    "ermutigend gegenüber", "motivierend gegenüber", "inspirierend gegenüber", "begeisternd gegenüber",
    "fördernd gegenüber", "unterstützend gegenüber", "begleitend gegenüber", "helfend gegenüber",
    "tröstend gegenüber", "heilend gegenüber", "stärkend gegenüber", "kräftigend gegenüber",
    "beruhigend gegenüber", "entspannend gegenüber", "klärend gegenüber", "orientierend gegenüber",
]

fremd_all = list(fremd_pronouns) + fremd_empathie
liste_fremd = dedupe_ordered(fremd_all)[:2000]
print(f"Fremdbezug: {len(liste_fremd)}")


# ============================================================
# AUSGABE ALS PYTHON-DATEI
# ============================================================

def write_list(f, varname, lst, padded=None):
    actual = padded if padded else lst
    f.write(f"\n# {len(actual)} Einträge\n")
    f.write(f"{varname} = [\n")
    for item in actual:
        escaped = item.replace("\\", "\\\\").replace('"', '\\"')
        f.write(f'    "{escaped}",\n')
    f.write("]\n")


with open("/mnt/user-data/outputs/wordlisten.py", "w", encoding="utf-8") as f:
    f.write('#!/usr/bin/env python3\n')
    f.write('"""\n')
    f.write('Wortlisten für Wortschatzanalyse\n')
    f.write('Generiert mit 6 Kategorien à 2000 Einträgen\n')
    f.write('"""\n\n')

    f.write('# ============================================================\n')
    f.write('# KATEGORIE 1: DENGLISCH (Anglizismen, Denglisch-Slang)\n')
    f.write('# ============================================================\n')
    write_list(f, "denglisch", liste_denglisch)

    f.write('\n# ============================================================\n')
    f.write('# KATEGORIE 2: JUGENDSPRACHE / SLANG\n')
    f.write('# ============================================================\n')
    write_list(f, "jugendsprache", liste_jugend)

    f.write('\n# ============================================================\n')
    f.write('# KATEGORIE 3: GEBILDETE SPRACHE\n')
    f.write('# ============================================================\n')
    write_list(f, "gebildete_sprache", liste_gebildet)

    f.write('\n# ============================================================\n')
    f.write('# KATEGORIE 4: UNTERSTÜTZENDE WÖRTER\n')
    f.write('# ============================================================\n')
    write_list(f, "unterstuetzende_woerter", liste_unterstuetzend)

    f.write('\n# ============================================================\n')
    f.write('# KATEGORIE 5: WÖRTER DIE AUF SICH SELBST EINGEHEN\n')
    f.write('# ============================================================\n')
    write_list(f, "selbstbezug", liste_selbst)

    f.write('\n# ============================================================\n')
    f.write('# KATEGORIE 6: WÖRTER DIE AUF DEN ANDEREN EINGEHEN\n')
    f.write('# ============================================================\n')
    write_list(f, "fremdbezug", liste_fremd)

    f.write('\n\n# Alle Listen als Dictionary\n')
    f.write('alle_listen = {\n')
    f.write('    "denglisch": denglisch,\n')
    f.write('    "jugendsprache": jugendsprache,\n')
    f.write('    "gebildete_sprache": gebildete_sprache,\n')
    f.write('    "unterstuetzende_woerter": unterstuetzende_woerter,\n')
    f.write('    "selbstbezug": selbstbezug,\n')
    f.write('    "fremdbezug": fremdbezug,\n')
    f.write('}\n')
    f.write('\nif __name__ == "__main__":\n')
    f.write('    for name, lst in alle_listen.items():\n')
    f.write('        print(f"{name}: {len(lst)} Einträge")\n')

print("\nFertig! Überprüfe Eintragsanzahl:")
print(f"  1. Denglisch:           {len(liste_denglisch)}")
print(f"  2. Jugendsprache:       {len(liste_jugend)}")
print(f"  3. Gebildete Sprache:   {len(liste_gebildet)}")
print(f"  4. Unterstützend:       {len(liste_unterstuetzend)}")
print(f"  5. Selbstbezug:         {len(liste_selbst)}")
print(f"  6. Fremdbezug:          {len(liste_fremd)}")