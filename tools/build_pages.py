#!/usr/bin/env python3
"""Génère les pages thématiques du site (même en-tête, pied de page et charte que l'accueil).
Usage : python3 tools/build_pages.py  (depuis la racine du site)"""
import json, html

B = "https://www.upandin-autonomie.fr"
ORG = {"@id": B + "/#entreprise"}

NAV = """    <nav class="nav" id="nav" aria-label="Navigation principale">
      <a href="/accompagnement-seniors-domicile">Seniors</a>
      <a href="/aide-aux-aidants">Aidants</a>
      <a href="/retour-domicile-apres-hospitalisation">Après l'hôpital</a>
      <a href="/zone-intervention">Zone</a>
      <a href="/#forfaits">Forfaits</a>
      <a href="/barometre-aidant">Baromètre</a>
      <a href="/#contact" class="btn btn--gold btn--sm">Contact</a>
    </nav>"""

HEADER = """<a class="skip" href="#contenu">Aller au contenu</a>
<header class="topbar" id="top">
  <div class="wrap topbar__in">
    <a href="/" class="brand" aria-label="Up&In Family Office de l'Autonomie — accueil">
      <img src="/img/mark.png" alt="" width="22" height="38">
      <span class="brand__txt"><b>Up<i>&amp;</i>In</b><small>Family Office de l'Autonomie</small></span>
    </a>
""" + NAV + """
    <div class="topbar__tools">
      <div class="a11y" role="group" aria-label="Taille du texte et contraste">
        <button type="button" data-size="0" aria-pressed="true" title="Texte normal">A</button>
        <button type="button" data-size="1" aria-pressed="false" title="Texte grand">A<sup>+</sup></button>
        <button type="button" data-size="2" aria-pressed="false" title="Texte très grand">A<sup>++</sup></button>
        <button type="button" data-contrast aria-pressed="false" title="Contraste renforcé" aria-label="Contraste renforcé"><svg viewBox="0 0 24 24" width="16" height="16" aria-hidden="true"><circle cx="12" cy="12" r="9" fill="none" stroke="currentColor" stroke-width="2"/><path d="M12 3a9 9 0 0 1 0 18z" fill="currentColor"/></svg></button>
      </div>
      <a class="call" href="tel:+33764058945" aria-label="Appeler le 07 64 05 89 45">
        <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6.6 10.8a15.1 15.1 0 0 0 6.6 6.6l2.2-2.2c.3-.3.7-.4 1-.2 1.1.4 2.3.6 3.6.6.6 0 1 .4 1 1V20c0 .6-.4 1-1 1A17 17 0 0 1 3 4c0-.6.4-1 1-1h3.5c.6 0 1 .4 1 1 0 1.3.2 2.5.6 3.6.1.3 0 .7-.2 1z"/></svg>
      </a>
      <button class="burger" type="button" aria-expanded="false" aria-controls="nav" aria-label="Ouvrir le menu"><span></span><span></span><span></span></button>
    </div>
  </div>
</header>"""

FOOTER = """<footer class="footer">
  <div class="wrap footer__grid">
    <div class="footer__brand">
      <img src="/img/logo-inner.jpg" alt="Up&In Family Office de l'Autonomie" width="140" height="140" loading="lazy">
      <p>Un référent. Une vision globale.<br>Une coordination dans la durée.</p>
    </div>
    <div>
      <h4>Nos accompagnements</h4>
      <a href="/accompagnement-seniors-domicile">Seniors à domicile et en résidence</a><a href="/aide-aux-aidants">Aide aux aidants</a><a href="/retour-domicile-apres-hospitalisation">Retour à domicile après l'hôpital</a><a href="/zone-intervention">Zone d'intervention</a><a href="/#forfaits">Forfaits</a><a href="/barometre-aidant">Baromètre de l'Aidant</a>
    </div>
    <div>
      <h4>Contact</h4>
      <a href="tel:+33764058945">07 64 05 89 45</a><a href="tel:+33662565322">06 62 56 53 22</a><a href="mailto:contact@upandin-autonomie.fr">contact@upandin-autonomie.fr</a>
      <p>Le Bouscat — Bordeaux Métropole<br>Du lundi au vendredi, 9 h – 19 h</p>
    </div>
    <div>
      <h4>Informations</h4>
      <a href="/mentions-legales">Mentions légales</a><a href="/mentions-legales#confidentialite">Confidentialité</a><a href="/plaquette">Plaquette de présentation</a><a href="/sondage">Sondage</a>
      <p class="ns">Structure non soignante. En cas d'urgence : 15 ou 112.</p>
    </div>
  </div>
  <div class="wrap footer__bottom">
    <p>© <span id="year">2026</span> Up&amp;In Family Office de l'Autonomie · Bordeaux</p>
    <a href="#top" class="totop" aria-label="Revenir en haut">↑</a>
  </div>
</footer>
<a class="fab" href="tel:+33764058945" aria-label="Appeler Up&In">
  <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6.6 10.8a15.1 15.1 0 0 0 6.6 6.6l2.2-2.2c.3-.3.7-.4 1-.2 1.1.4 2.3.6 3.6.6.6 0 1 .4 1 1V20c0 .6-.4 1-1 1A17 17 0 0 1 3 4c0-.6.4-1 1-1h3.5c.6 0 1 .4 1 1 0 1.3.2 2.5.6 3.6.1.3 0 .7-.2 1z"/></svg>
  <span>Appeler</span>
</a>
<script src="/js/main.js?v=20261029b" defer></script>"""

CTA = """<section class="section section--navy">
  <div class="wrap page-cta">
    <div>
      <p class="eyebrow eyebrow--gold">Premier échange gratuit et sans engagement</p>
      <h2>Parlons de votre situation.</h2>
      <p>Du lundi au vendredi, de 9 h à 19 h. Nous vous rappelons si vous le souhaitez.</p>
    </div>
    <div class="page-cta__btns">
      <a href="tel:+33764058945" class="btn btn--gold">07 64 05 89 45</a>
      <a href="/#contact" class="btn btn--ghost">Demander un rappel</a>
    </div>
  </div>
</section>"""


def page(slug, title, desc, h1, eyebrow, lead, body, faq, service_name, crumb):
    url = f"{B}/{slug}"
    ld = {"@context": "https://schema.org", "@graph": [
        {"@type": "Service", "@id": url + "#service", "name": service_name, "serviceType": service_name,
         "provider": ORG, "url": url, "description": desc,
         "areaServed": [{"@type": "AdministrativeArea", "name": "Bordeaux Métropole"}, {"@type": "AdministrativeArea", "name": "Gironde"}]},
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Accueil", "item": B + "/"},
            {"@type": "ListItem", "position": 2, "name": crumb, "item": url}]},
    ]}
    if faq:
        ld["@graph"].append({"@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": html.unescape(a.replace('<strong>', '').replace('</strong>', ''))}} for q, a in faq]})
    faq_html = ""
    if faq:
        faq_html = '<section class="section"><div class="wrap narrow"><header class="sec-head"><p class="eyebrow">Questions fréquentes</p><h2>Vos questions</h2></header><div class="faq">' + \
            "".join(f"<details><summary>{q}</summary><p>{a}</p></details>" for q, a in faq) + "</div></div></section>"
    t_esc = title.replace('&', '&amp;')
    return f"""<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{t_esc}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{url}">
<meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1">
<meta name="theme-color" content="#10214C">
<link rel="icon" type="image/png" href="/img/favicon.png">
<link rel="apple-touch-icon" href="/img/apple-touch-icon.png">
<meta property="og:type" content="article">
<meta property="og:locale" content="fr_FR">
<meta property="og:site_name" content="Up&amp;In Family Office de l'Autonomie">
<meta property="og:url" content="{url}">
<meta property="og:title" content="{t_esc}">
<meta property="og:description" content="{desc}">
<meta property="og:image" content="{B}/img/og.jpg">
<meta name="twitter:card" content="summary_large_image">
<meta name="geo.region" content="FR-33">
<meta name="geo.placename" content="Le Bouscat, Bordeaux Métropole">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,500;0,600;0,700;1,500&family=Source+Sans+3:wght@400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/css/style.css?v=20261029b">
<script type="application/ld+json">
{json.dumps(ld, ensure_ascii=False, indent=1)}
</script>
</head>
<body>
{HEADER}
<main id="contenu">
<section class="page-hero">
  <div class="wrap">
    <nav class="crumbs" aria-label="Fil d'Ariane"><a href="/">Accueil</a> <span aria-hidden="true">›</span> <span>{crumb}</span></nav>
    <p class="eyebrow">{eyebrow}</p>
    <h1>{h1}</h1>
    <p class="lead">{lead}</p>
    <div class="hero__cta"><a href="/#contact" class="btn btn--gold">Demander un premier échange</a><a href="tel:+33764058945" class="btn btn--ghost">07 64 05 89 45</a></div>
  </div>
</section>
{body}
{faq_html}
{CTA}
</main>
{FOOTER}
</body>
</html>
"""


def prose(*blocks, cream=False):
    return f'<section class="section{" section--cream" if cream else ""}"><div class="wrap prose">' + "".join(blocks) + "</div></section>"


PAGES = []

# ---------------------------------------------------------------- 1. Seniors
PAGES.append(dict(
    slug="accompagnement-seniors-domicile",
    crumb="Accompagnement des seniors",
    title="Accompagnement des seniors à domicile à Bordeaux · Up&In",
    desc="Un référent unique pour organiser le maintien à domicile ou la vie en résidence d'un parent âgé à Bordeaux : visites, rendez-vous, intervenants.",
    h1="Accompagner un parent âgé à domicile, <em>avec un seul référent.</em>",
    eyebrow="Seniors · Bordeaux Métropole et Gironde",
    lead="Rester chez soi le plus longtemps possible, ou bien vivre en résidence senior, demande une organisation que la famille ne peut pas toujours tenir seule. Up&amp;In Family Office de l'Autonomie devient le coordinateur de la personne âgée : nous connaissons sa situation, ses intervenants et ses habitudes, et nous tenons le fil.",
    service_name="Coordination de l'accompagnement des seniors à domicile et en résidence",
    body=prose(
        "<h2>Ce que nous faisons pour la personne âgée</h2>",
        "<p>Nous ne remplaçons ni l'aide à domicile, ni l'infirmier, ni le médecin traitant. Nous faisons en sorte que <strong>tout ce qui entoure la personne fonctionne ensemble</strong>.</p>",
        '<ul class="ticks">'
        "<li><strong>Des visites régulières</strong> à domicile ou en résidence, pour parler, observer et repérer ce qui change.</li>"
        "<li><strong>L'organisation des rendez-vous</strong> : prise de rendez-vous, rappels, préparation des questions, et accompagnement si besoin.</li>"
        "<li><strong>La coordination des intervenants</strong> : infirmier, kinésithérapeute, pharmacie, aide à domicile, portage de repas, artisans.</li>"
        "<li><strong>L'aide aux démarches</strong> : dossiers, courriers, recherche d'une aide adaptée ou d'une résidence.</li>"
        "<li><strong>Des nouvelles à la famille</strong>, avec l'accord de la personne : compte rendu après chaque visite et synthèse mensuelle.</li>"
        "</ul>",
        "<h2>À domicile comme en résidence senior</h2>",
        "<p>Le maintien à domicile n'est pas la seule situation que nous accompagnons. Quand un parent vit en <strong>résidence senior, en résidence autonomie ou en EHPAD</strong>, nous travaillons avec l'équipe de l'établissement : nous suivons les rendez-vous extérieurs, nous faisons le lien avec la famille éloignée et nous veillons à ce que les besoins de la personne restent entendus.</p>",
        "<h2>Comment se passe un accompagnement</h2>",
        '<ol class="steps steps--compact">'
        "<li><b>01</b><h3>Premier échange</h3><p>Gratuit, par téléphone ou à domicile, pour comprendre la situation.</p></li>"
        "<li><b>02</b><h3>Bilan partagé</h3><p>Une rencontre approfondie : quotidien, entourage, intervenants, fragilités et ressources.</p></li>"
        "<li><b>03</b><h3>Plan et devis</h3><p>Des priorités claires et un forfait adapté. Rien n'est engagé sans votre accord.</p></li>"
        "<li><b>04</b><h3>Suivi dans la durée</h3><p>Visites, coordination, comptes rendus et ajustements au fil du temps.</p></li>"
        "</ol>",
        '<p>Trois forfaits mensuels existent selon le niveau d\'accompagnement souhaité : <a href="/#forfaits">Repères, Relais et Sérénité</a>.</p>',
        '<div class="note-ns"><b>Nous ne sommes pas soignants.</b> Nous ne réalisons aucun acte de soin et ne donnons aucun avis médical. Nous travaillons en complémentarité des équipes de soin.</div>',
    ),
    faq=[
        ("Quelle différence avec une aide à domicile ?", "L'aide à domicile intervient pour les gestes du quotidien (ménage, repas, toilette). Nous, nous organisons et coordonnons l'ensemble : nous pouvons justement vous aider à trouver une aide à domicile et à suivre son intervention."),
        ("Mon parent ne veut pas être « surveillé ». Comment cela se passe-t-il ?", "Nous intervenons avec l'accord de la personne et à son rythme. Les informations transmises à la famille sont décidées avec elle. Notre rôle est de l'aider à garder la main sur sa vie, pas de décider à sa place."),
        ("J'habite loin de Bordeaux. Pouvez-vous être mes yeux sur place ?", "Oui, c'est l'une des situations les plus fréquentes. Vous recevez un compte rendu après chaque visite, une synthèse mensuelle, et un appel immédiat en cas de situation inhabituelle."),
        ("Intervenez-vous en EHPAD ou en résidence senior ?", "Oui. Nous accompagnons aussi bien à domicile qu'en résidence, en lien avec l'équipe de l'établissement."),
    ],
))

# ---------------------------------------------------------------- 2. Aidants
PAGES.append(dict(
    slug="aide-aux-aidants",
    crumb="Aide aux aidants",
    title="Aide aux aidants familiaux à Bordeaux · Up&In Family Office",
    desc="Vous veillez sur un parent âgé ? Nous prenons le relais sur la coordination : rendez-vous, intervenants, démarches. Bordeaux Métropole et Gironde.",
    h1="Aidant d'un parent âgé : <em>vous n'avez pas à tout porter seul.</em>",
    eyebrow="Aidants familiaux · Bordeaux Métropole et Gironde",
    lead="Rendez-vous à caler entre deux journées de travail, appels qui se croisent, informations qui se perdent entre l'hôpital, le médecin et l'infirmière : l'organisation autour d'un parent âgé pèse lourd. Nous prenons le relais sur la coordination, pour que vous puissiez redevenir d'abord un enfant, un conjoint, un proche.",
    service_name="Aide et soutien aux aidants familiaux",
    body=prose(
        "<h2>Ce que nous prenons en charge pour vous</h2>",
        '<ul class="ticks">'
        "<li><strong>La coordination des intervenants</strong> : nous faisons circuler la bonne information entre soignants, aides et prestataires.</li>"
        "<li><strong>Le suivi des rendez-vous</strong> : prise, rappels, préparation et, si besoin, accompagnement.</li>"
        "<li><strong>Les démarches</strong> : orientation vers les bons dispositifs, montage des dossiers, recherche d'une solution adaptée.</li>"
        "<li><strong>Une information claire et régulière</strong> : comptes rendus écrits, synthèse mensuelle, alerte en cas de signal inhabituel.</li>"
        "<li><strong>Du temps pour vous</strong> : écoute, orientation et organisation de temps de répit.</li>"
        "</ul>",
        "<h2>Mesurez votre charge d'aidant</h2>",
        '<p>Combien d\'heures consacrez-vous chaque mois à votre proche, entre la coordination, les démarches et les imprévus ? Notre <a href="/barometre-aidant">Baromètre de l\'Aidant</a> vous aide à faire le point en cinq minutes, gratuitement et sans inscription.</p>',
        "<h2>Une histoire que nous connaissons</h2>",
        "<p>Natacha et Damien Taudin ont créé Up&amp;In Family Office de l'Autonomie après avoir vécu eux-mêmes l'accompagnement d'un parent qui vieillit. Ils savent ce que représente l'inquiétude de « ne pas savoir », et ce qu'apporte une personne qui tient le fil.</p>",
        '<div class="note-ns"><b>Vous êtes épuisé ou inquiet pour votre propre santé ?</b> Parlez-en à votre médecin traitant. En cas d\'urgence, composez le 15 ou le 112.</div>',
        cream=False,
    ),
    faq=[
        ("Je travaille à temps plein. Pouvez-vous gérer les rendez-vous de mon parent ?", "Oui. Nous prenons les rendez-vous, les rappelons, préparons les questions avec votre parent et pouvons l'accompagner. Vous êtes informé par écrit de ce qui a été dit et décidé."),
        ("Remplacez-vous l'aide à domicile ou l'infirmier ?", "Non. Nous ne faisons ni soin, ni ménage, ni toilette. Nous coordonnons les professionnels qui s'en chargent et veillons à ce que tout le monde ait la bonne information."),
        ("Comment savoir si j'ai besoin d'aide ?", "Si vous pensez à votre proche la nuit, si vous jonglez entre plusieurs intervenants ou si vous avez renoncé à des moments pour vous, un premier échange gratuit permet de faire le point. Le Baromètre de l'Aidant peut aussi vous aider à mesurer votre charge."),
        ("Mes frères et sœurs vivent loin. Peuvent-ils être informés aussi ?", "Oui. Avec l'accord de votre parent, les comptes rendus peuvent être adressés à plusieurs membres de la famille, pour que chacun ait la même information."),
    ],
))

# ---------------------------------------------------------------- 3. Après l'hôpital (Rebond)
PAGES.append(dict(
    slug="retour-domicile-apres-hospitalisation",
    crumb="Retour à domicile après l'hôpital",
    title="Retour à domicile après une hospitalisation · Bordeaux · Up&In",
    desc="Sortie d'hôpital, fracture, convalescence : le forfait Rebond organise le retour à domicile d'une personne âgée et coordonne aides et soins.",
    h1="Après l'hôpital, <em>un retour à la maison organisé.</em>",
    eyebrow="Forfait Rebond · Incapacité temporaire",
    lead="Une sortie d'hospitalisation, une fracture ou une convalescence bouleversent l'équilibre d'une personne âgée et de sa famille, souvent du jour au lendemain. Le forfait Rebond met en place rapidement un accompagnement renforcé, qui s'arrête quand la situation redevient stable.",
    service_name="Accompagnement temporaire après hospitalisation (forfait Rebond)",
    body=prose(
        "<h2>Pour quelles situations ?</h2>",
        '<ul class="ticks">'
        "<li>Un <strong>retour à domicile après une hospitalisation</strong> ou un séjour en soins de suite.</li>"
        "<li>Une <strong>fracture</strong> ou une opération qui limite temporairement l'autonomie.</li>"
        "<li>Une <strong>convalescence</strong> qui demande plus de présence et de coordination que d'habitude.</li>"
        "<li>L'<strong>absence temporaire de l'aidant habituel</strong> : hospitalisation, déplacement, épuisement.</li>"
        "</ul>",
        "<h2>Ce que comprend le forfait Rebond</h2>",
        '<ul class="ticks">'
        "<li><strong>L'organisation du retour</strong> : lien avec le service hospitalier, mise en place des aides et du matériel prévus.</li>"
        "<li><strong>Une coordination renforcée</strong> des soins et des aides à domicile pendant la période.</li>"
        "<li><strong>Des visites rapprochées</strong> pour vérifier que tout se passe bien.</li>"
        "<li><strong>Un point chaque semaine</strong> avec la famille.</li>"
        "<li><strong>Un relais possible</strong> vers un forfait mensuel si un suivi dans la durée devient utile.</li>"
        "</ul>",
        "<h2>Anticiper la sortie</h2>",
        "<p>L'idéal est de nous contacter <strong>avant la date de sortie</strong>, dès qu'elle est envisagée par l'équipe soignante. Nous pouvons alors préparer le retour avec vous : qui intervient, quand, et ce qu'il faut prévoir à la maison.</p>",
        '<div class="note-ns"><b>Nous ne sommes pas soignants.</b> Les soins restent assurés par les professionnels de santé prescrits par l\'hôpital ou le médecin traitant. Nous organisons et coordonnons autour d\'eux.</div>',
    ),
    faq=[
        ("Combien de temps dure le forfait Rebond ?", "Il est prévu pour une période courte, le temps que la situation redevienne stable. Sa durée et son contenu sont précisés dans le devis selon la situation."),
        ("Pouvez-vous intervenir rapidement ?", "Oui, c'est le principe du forfait Rebond : un accompagnement mis en place rapidement. Appelez-nous dès que la date de sortie est connue."),
        ("Et si mon parent a besoin d'un suivi après la convalescence ?", "Le forfait Rebond peut se prolonger par un forfait mensuel (Repères, Relais ou Sérénité), sans rupture dans l'accompagnement."),
    ],
))

# ---------------------------------------------------------------- 4. Zone d'intervention
COMMUNES_REG = ["Le Bouscat", "Bordeaux (dont Caudéran)", "Bruges", "Eysines", "Mérignac", "Le Haillan", "Blanquefort", "Saint-Médard-en-Jalles", "Le Taillan-Médoc", "Parempuyre"]
PAGES.append(dict(
    slug="zone-intervention",
    crumb="Zone d'intervention",
    title="Zone d'intervention : Bordeaux Métropole et Gironde · Up&In",
    desc="Basés au Bouscat, nous accompagnons les seniors et leurs aidants sur Bordeaux Métropole avec des visites régulières, et dans toute la Gironde selon le besoin.",
    h1="Où intervenons-nous ? <em>Bordeaux Métropole et Gironde.</em>",
    eyebrow="Zone d'intervention",
    lead="Up&amp;In Family Office de l'Autonomie est basé au Bouscat. Nous accompagnons les seniors et leurs familles sur toute la métropole bordelaise avec des visites régulières, et dans le reste de la Gironde selon le besoin.",
    service_name="Coordination de l'autonomie des seniors — Bordeaux Métropole et Gironde",
    body=prose(
        "<h2>Bordeaux Métropole : des visites régulières</h2>",
        "<p>Sur l'ensemble des communes de Bordeaux Métropole, les visites se font à fréquence régulière selon le forfait choisi. Nous connaissons particulièrement bien le nord-ouest de la métropole, autour de notre base du Bouscat :</p>",
        '<ul class="chips">' + "".join(f"<li>{c}</li>" for c in COMMUNES_REG) + "</ul>",
        "<p>Nous intervenons aussi dans les autres communes de la métropole : Pessac, Talence, Bègles, Villenave-d'Ornon, Gradignan, Cenon, Lormont, Floirac et leurs voisines.</p>",
        "<h2>Gironde : selon le besoin</h2>",
        "<p>Au-delà de la métropole, nous intervenons dans toute la Gironde selon le besoin, par exemple pour un accompagnement ponctuel, un retour d'hospitalisation ou une famille qui vit loin. Les frais de déplacement hors Bordeaux Métropole sont précisés dans le devis.</p>",
        "<h2>À domicile ou en établissement</h2>",
        '<p>Nous intervenons chez la personne, mais aussi en <strong>résidence senior, résidence autonomie, maison partagée ou EHPAD</strong>, en lien avec l\'équipe de l\'établissement. Voir <a href="/accompagnement-seniors-domicile">l\'accompagnement des seniors</a>.</p>',
    ),
    faq=[
        ("Votre adresse au Bouscat accueille-t-elle du public ?", "Non. Nous nous déplaçons chez la personne accompagnée ou dans son établissement. Le premier échange peut se faire par téléphone ou à domicile."),
        ("Intervenez-vous hors de Gironde ?", "Notre zone est Bordeaux Métropole et la Gironde. Pour une famille installée ailleurs dont le parent vit en Gironde, c'est justement là que nous sommes utiles."),
    ],
))

for p in PAGES:
    open(p["slug"] + ".html", "w", encoding="utf-8").write(page(**p))
    print("ok", p["slug"])
