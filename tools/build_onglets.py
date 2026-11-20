#!/usr/bin/env python3
"""Découpe l'accueil en pages par onglet (Accueil, Notre approche, Forfaits, L'équipe,
Questions, Documentation, Contact) et met à jour la navigation de tout le site.

Source unique du contenu : tools/source/accueil-complet.html (l'ancien accueil long).
Usage : python3 tools/build_onglets.py   (depuis la racine du site), puis
        python3 tools/build_pages.py     (pages thématiques)."""
import html, json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "tools" / "source" / "accueil-complet.html"
B = "https://www.upandin-autonomie.fr"

src = SRC.read_text(encoding="utf-8")

# ------------------------------------------------------------------ onglets
TABS = [
    ("/", "Accueil"),
    ("/notre-approche", "Notre approche"),
    ("/forfaits", "Forfaits"),
    ("/equipe", "L'équipe"),
    ("/questions", "Questions"),
    ("/documentation", "Documentation"),
]


def nav(current):
    links = []
    for href, label in TABS:
        cur = ' aria-current="page"' if href == current else ""
        links.append(f'      <a href="{href}"{cur}>{label}</a>')
    cur = ' aria-current="page"' if current == "/contact" else ""
    links.append(f'      <a href="/contact" class="btn btn--gold btn--sm"{cur}>Contact</a>')
    return '    <nav class="nav" id="nav" aria-label="Navigation principale">\n' + "\n".join(links) + "\n    </nav>"


# Où se trouve désormais chaque ancienne ancre de l'accueil
ANCHOR_PAGE = {
    "constat": "/notre-approche", "mission": "/notre-approche", "services": "/notre-approche",
    "methode": "/notre-approche", "mires": "/notre-approche", "etp": "/notre-approche",
    "forfaits": "/forfaits", "credit": "/forfaits",
    "plaquette": "/documentation", "barometre": "/documentation", "sondage": "/documentation",
    "equipe": "/equipe", "valeur": "/", "faq": "/questions", "contact": "/contact",
}
ANCHOR_URL = {
    "forfaits": "/forfaits", "equipe": "/equipe", "faq": "/questions", "contact": "/contact",
    "plaquette": "/documentation#plaquette", "barometre": "/documentation#barometre",
    "sondage": "/documentation#sondage", "credit": "/forfaits#credit", "valeur": "/#valeur",
}


def fix_links(text, here):
    """#ancre et /#ancre -> nouvelle page (ancre locale gardée si la section est sur la page)."""
    def rep(m):
        a = m.group(2)
        if a not in ANCHOR_PAGE:
            return m.group(0)
        if ANCHOR_PAGE[a] == here:
            return f'href="#{a}"'
        return f'href="{ANCHOR_URL.get(a, ANCHOR_PAGE[a] + "#" + a)}"'
    return re.sub(r'href="(/)?#([a-z-]+)"', rep, text)


# ------------------------------------------------------------------ découpe de la source
head_end = src.index("</head>")
HEAD = src[:head_end]
body = src[head_end:]
hdr_start = body.index('<header class="topbar"')
hdr_end = body.index("</header>", hdr_start) + len("</header>")
HEADER = body[hdr_start:hdr_end]
main = body[body.index('<main id="contenu">') + len('<main id="contenu">'):body.index("</main>")]
FOOTER_AND_SCRIPTS = body[body.index("<!-- ================= PIED DE PAGE"):body.index("</body>")]

SECTIONS = {}
parts = re.split(r"\n(?=(?:<!-- =+ [^\n]*? =+ -->\n)?<section)", main)
for p in parts:
    m = re.search(r'<section([^>]*)>', p)
    if not m:
        continue
    mid = re.search(r'id="([a-z-]+)"', m.group(1))
    key = mid.group(1) if mid else ("hero" if 'class="hero"' in m.group(1) else None)
    if key:
        SECTIONS[key] = p.strip("\n")
need = "hero constat mission services methode mires etp forfaits credit plaquette barometre sondage equipe valeur faq contact".split()
missing = [k for k in need if k not in SECTIONS]
assert not missing, f"sections introuvables : {missing}"
# Le formulaire est désormais sur la page Contact
SECTIONS["faq"] = SECTIONS["faq"].replace("remplissez le formulaire ci-dessous", 'remplissez le <a href="/contact">formulaire de contact</a>')

LD = json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>', HEAD, re.S).group(1))
GRAPH = {g.get("@id", "").split("#")[-1]: g for g in LD["@graph"]}
HEAD_NO_LD = re.sub(r'<script type="application/ld\+json">.*?</script>\n?', "", HEAD, flags=re.S)


def head_for(path, title, desc, extra_graph):
    url = B + path
    h = HEAD_NO_LD
    t = html.escape(title, quote=False)
    d = html.escape(desc)
    h = re.sub(r"<title>.*?</title>", f"<title>{t}</title>", h, flags=re.S)
    h = re.sub(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{d}">', h)
    h = re.sub(r'<link rel="canonical" href="[^"]*">', f'<link rel="canonical" href="{url}">', h)
    h = re.sub(r'<meta property="og:url" content="[^"]*">', f'<meta property="og:url" content="{url}">', h)
    h = re.sub(r'<meta property="og:title" content="[^"]*">', f'<meta property="og:title" content="{t}">', h)
    h = re.sub(r'<meta property="og:description" content="[^"]*">', f'<meta property="og:description" content="{d}">', h)
    h = re.sub(r'<meta name="twitter:title" content="[^"]*">', f'<meta name="twitter:title" content="{t}">', h)
    h = re.sub(r'<meta name="twitter:description" content="[^"]*">', f'<meta name="twitter:description" content="{d}">', h)
    graph = list(extra_graph)
    if path != "/":
        graph.append({"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Accueil", "item": B + "/"},
            {"@type": "ListItem", "position": 2, "name": title.split(" · ")[0].split(" — ")[0], "item": url}]})
    ld = json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False, indent=1)
    return h.rstrip() + f'\n<script type="application/ld+json">\n{ld}\n</script>\n'


PORTAIL = '<a class="portail" href="https://www.cabinet-upandin-project.com/" title="Revenir au portail Up&amp;In" aria-label="Portail Up&amp;In"><svg viewBox="0 0 24 24" width="16" height="16" aria-hidden="true"><path d="M6 21V5a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2v16M3 21h18M14 12h.01" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg><span>Portail Up&amp;In</span></a>\n      '


def header_for(path):
    h = re.sub(r'<nav class="nav" id="nav".*?</nav>', lambda m: nav(path), HEADER, flags=re.S)
    h = h.replace('<div class="topbar__tools">\n      ', '<div class="topbar__tools">\n      ' + PORTAIL, 1)
    return h.replace('<a href="#top" class="brand"', '<a href="/" class="brand"')


def page_hero(crumb, eyebrow, h1, lead):
    return f"""<section class="page-hero">
  <div class="wrap">
    <nav class="crumbs" aria-label="Fil d'Ariane"><a href="/">Accueil</a> <span aria-hidden="true">›</span> <span>{crumb}</span></nav>
    <p class="eyebrow">{eyebrow}</p>
    <h1>{h1}</h1>
    <p class="lead">{lead}</p>
  </div>
</section>"""


CTA = """<section class="section section--navy">
  <div class="wrap page-cta">
    <div>
      <p class="eyebrow eyebrow--gold">Premier échange gratuit et sans engagement</p>
      <h2>Parlons de votre situation.</h2>
      <p>Du lundi au vendredi, de 9 h à 19 h. Nous vous rappelons si vous le souhaitez.</p>
    </div>
    <div class="page-cta__btns">
      <a href="tel:+33764058945" class="btn btn--gold">07 64 05 89 45</a>
      <a href="/contact" class="btn btn--ghost">Demander un rappel</a>
    </div>
  </div>
</section>"""


def portes(items):
    cards = "".join(
        f'<div><b>{t}</b><p>{p}</p><p style="margin-top:14px"><a href="{href}" class="btn btn--gold btn--sm">{c}</a></p></div>'
        for t, p, href, c in items)
    return f'<section class="section section--navy"><div class="wrap"><div class="vals">{cards}</div></div></section>'


DOC_CARDS = [
    ("Guide", "Accompagner un parent âgé à domicile", "Visites, rendez-vous, intervenants : ce qu'un référent unique change au quotidien.", "/accompagnement-seniors-domicile", "Lire le guide"),
    ("Guide", "Aide aux aidants familiaux", "Charge mentale, épuisement, répit : comment alléger le rôle d'aidant.", "/aide-aux-aidants", "Lire le guide"),
    ("Guide", "Retour à domicile après une hospitalisation", "Préparer la sortie, organiser les premières semaines, éviter la rupture.", "/retour-domicile-apres-hospitalisation", "Lire le guide"),
    ("Repère", "Zone d'intervention", "Bordeaux Métropole et Gironde : où et comment nous intervenons.", "/zone-intervention", "Voir la zone"),
    ("Démonstration", "Le Cercle – Bilan partagé", "Notre outil de coordination sur un dossier fictif : journal des intervenants, transmissions, comptes rendus aux aidants. Version verrouillée.", "/documents/le-cercle-demonstration.html", "Ouvrir la démonstration"),
]


def doc_grid():
    cards = "".join(
        f'<article class="card" style="padding:26px 24px;display:flex;flex-direction:column;gap:10px">'
        f'<p class="eyebrow" style="margin:0">{k}</p><h3 style="margin:0">{t}</h3><p style="margin:0;flex:1">{p}</p>'
        f'<p style="margin:6px 0 0"><a href="{href}" class="link">{c} →</a></p></article>'
        for k, t, p, href, c in DOC_CARDS)
    return f"""<section class="section section--cream" id="guides">
  <div class="wrap">
    <header class="sec-head">
      <p class="eyebrow">Guides et ressources</p>
      <h2>Pour les familles, les aidants et les professionnels.</h2>
      <p>Des repères concrets, enrichis au fil des mois. Nouveaux articles à venir.</p>
    </header>
    <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,260px),1fr));gap:18px">{cards}</div>
  </div>
</section>"""


ORG = GRAPH.get("entreprise")
SITE = GRAPH.get("site")
FAQ = GRAPH.get("faq")
ORG_REF = {"@id": B + "/#entreprise"}

PAGES = [
    dict(path="/", file="index.html",
         title="Up&In Family Office de l'Autonomie · Seniors & aidants, Bordeaux",
         desc="Un référent unique pour coordonner l'accompagnement des seniors à domicile ou en résidence et soutenir les aidants. Bordeaux Métropole et Gironde.",
         graph=[g for g in (ORG, SITE) if g],
         body=lambda: "\n\n".join([
             SECTIONS["hero"],
             portes([
                 ("Notre approche", "Un référent unique, une méthode claire, du premier appel au suivi.", "/notre-approche", "Découvrir"),
                 ("Nos forfaits", "Repères, Relais, Sérénité, Rebond : à la mesure de chaque situation.", "/forfaits", "Voir les forfaits"),
                 ("L'équipe", "Natacha et Damien Taudin, cofondateurs, au Bouscat.", "/equipe", "Nous rencontrer"),
             ]),
             SECTIONS["valeur"],
             CTA])),
    dict(path="/notre-approche", file="notre-approche.html",
         title="Notre approche · Up&In Family Office de l'Autonomie",
         desc="Le constat, notre mission, nos quatre missions et notre méthode en quatre étapes : un référent unique pour l'autonomie des seniors à Bordeaux.",
         graph=[{"@type": "WebPage", "url": B + "/notre-approche", "about": ORG_REF}],
         body=lambda: "\n\n".join([
             page_hero("Notre approche", "Notre approche", "Un référent unique, <em>une méthode claire.</em>",
                       "Un référent. Une vision globale. Une coordination dans la durée."),
             SECTIONS["mission"], SECTIONS["services"], SECTIONS["methode"], SECTIONS["constat"],
             SECTIONS["mires"], SECTIONS["etp"], CTA])),
    dict(path="/forfaits", file="forfaits.html",
         title="Forfaits Repères, Relais, Sérénité, Rebond · Up&In Bordeaux",
         desc="Nos forfaits d'accompagnement des seniors et des aidants à Bordeaux Métropole et en Gironde, et le crédit d'impôt services à la personne.",
         graph=[{"@type": "WebPage", "url": B + "/forfaits", "about": ORG_REF}],
         body=lambda: "\n\n".join([
             page_hero("Forfaits", "Nos forfaits", "Repères, Relais, Sérénité <em>et Rebond.</em>",
                       "Choisissez le niveau d'accompagnement qui vous convient. Le premier échange est gratuit et sans engagement."),
             SECTIONS["forfaits"], SECTIONS["credit"], CTA])),
    dict(path="/equipe", file="equipe.html",
         title="L'équipe · Natacha et Damien Taudin · Up&In Family Office",
         desc="Natacha et Damien Taudin, cofondateurs d'Up&In Family Office de l'Autonomie au Bouscat : un duo complémentaire au service des seniors et des aidants.",
         graph=[{"@type": "AboutPage", "url": B + "/equipe", "about": ORG_REF}],
         body=lambda: "\n\n".join([
             page_hero("L'équipe", "L'équipe", "Derrière Up&amp;In, il y a d'abord une histoire. <em>La nôtre.</em>",
                       "Nous avons compris qu'il manquait quelqu'un pour vous aider à tenir le fil."),
             SECTIONS["equipe"], CTA])),
    dict(path="/questions", file="questions.html",
         title="Questions fréquentes · Up&In Family Office de l'Autonomie",
         desc="Vos questions sur l'accompagnement des seniors et des aidants : intervention, forfaits, crédit d'impôt, zone, premier échange.",
         graph=[json.loads(json.dumps(dict(FAQ, **{"@id": B + "/questions#faq", "url": B + "/questions"})).replace("remplissez le formulaire ci-dessous", "remplissez le formulaire de contact"))] if FAQ else [],
         body=lambda: "\n\n".join([
             page_hero("Questions", "Questions fréquentes", "Questions <em>fréquentes.</em>",
                       "Une autre question ? Le premier échange est gratuit et sans engagement."),
             SECTIONS["faq"], CTA])),
    dict(path="/documentation", file="documentation.html",
         title="Documentation, guides et outils · Up&In Family Office de l'Autonomie",
         desc="Plaquette, guides pour les familles et les aidants, Baromètre de l'Aidant, sondage et démonstration du Cercle : nos ressources gratuites.",
         graph=[{"@type": "CollectionPage", "url": B + "/documentation", "about": ORG_REF}],
         body=lambda: "\n\n".join([
             page_hero("Documentation", "Documentation", "Guides, outils <em>et ressources.</em>",
                       "Tout ce qui peut aider les familles, les aidants et les professionnels à y voir plus clair."),
             SECTIONS["plaquette"], doc_grid(), SECTIONS["barometre"], SECTIONS["sondage"], CTA])),
    dict(path="/contact", file="contact.html",
         title="Contact · Up&In Family Office de l'Autonomie · Le Bouscat",
         desc="Contactez Up&In Family Office de l'Autonomie : 07 64 05 89 45, 06 62 56 53 22, contact@upandin-autonomie.fr. Premier échange gratuit.",
         graph=[{"@type": "ContactPage", "url": B + "/contact", "about": ORG_REF}],
         body=lambda: "\n\n".join([
             page_hero("Contact", "Contact", "Un premier échange, <em>gratuit et sans engagement.</em>",
                       "Du lundi au vendredi, de 9 h à 19 h. Le premier échange est gratuit et sans engagement."),
             SECTIONS["contact"]])),
]

FOOT_LINKS = ('<a href="/accompagnement-seniors-domicile">Seniors à domicile et en résidence</a>'
              '<a href="/aide-aux-aidants">Aide aux aidants</a>'
              '<a href="/retour-domicile-apres-hospitalisation">Retour après l\'hôpital</a>'
              '<a href="/zone-intervention">Zone d\'intervention</a>'
              '<a href="/notre-approche">Notre approche</a><a href="/forfaits">Forfaits</a>'
              '<a href="/forfaits#credit">Crédit d\'impôt</a><a href="/equipe">L\'équipe</a>'
              '<a href="/questions">Questions</a><a href="/documentation">Documentation</a>'
              '<a href="/barometre-aidant">Baromètre de l\'Aidant</a><a href="/sondage">Sondage</a>'
              '<a href="/contact">Contact</a>')


def footer_for(path):
    f = FOOTER_AND_SCRIPTS
    f = re.sub(r"(<h4>Nos accompagnements</h4>\s*)(.*?)(\s*</div>)", lambda m: m.group(1) + FOOT_LINKS + m.group(3), f, count=1, flags=re.S)
    f = f.replace('<a href="#sources">Sources des chiffres</a>',
                  '<a href="#sources">Sources des chiffres</a><a href="https://www.cabinet-upandin-project.com/">Portail Up&amp;In</a><a href="https://www.cabinet-upandin-project.com/conseils">Up&amp;In Conseils</a>')
    return fix_links(f, path)


for p in PAGES:
    out = head_for(p["path"], p["title"], p["desc"], p["graph"])
    out += "</head>\n<body>\n" + '<a class="skip" href="#contenu">Aller au contenu</a>\n\n' + header_for(p["path"])
    out += '\n\n<main id="contenu">\n\n' + fix_links(p["body"](), p["path"]) + "\n\n</main>\n\n" + footer_for(p["path"]) + "</body>\n</html>\n"
    (ROOT / p["file"]).write_text(out, encoding="utf-8")
    print("écrit", p["file"], len(out))

# Plan du site : ajoute les nouvelles pages si absentes
sm_path = ROOT / "sitemap.xml"
sm = sm_path.read_text(encoding="utf-8")
for p in PAGES[1:]:
    loc = B + p["path"]
    if f"<loc>{loc}</loc>" not in sm:
        sm = sm.replace("</urlset>", f"  <url>\n    <loc>{loc}</loc>\n    <lastmod>2026-11-20</lastmod>\n    <changefreq>monthly</changefreq>\n    <priority>0.8</priority>\n  </url>\n</urlset>")
sm_path.write_text(sm, encoding="utf-8")
