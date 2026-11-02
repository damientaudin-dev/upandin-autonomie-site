<?php
// ===== Réglages du questionnaire Up&In Family Office de l'Autonomie =====
if (basename($_SERVER['SCRIPT_FILENAME']) === 'config.php') { http_response_code(403); exit; }

date_default_timezone_set('Europe/Paris');

const SITE_URL      = 'https://www.upandin-autonomie.fr';
const LOGO_URL      = 'https://www.upandin-autonomie.fr/avis/logo.png';
const EXPEDITEUR    = 'contact@upandin-autonomie.fr';          // doit être une adresse du domaine (exigence OVH)
const NOM_EXPED     = "Up&In Family Office de l'Autonomie";
const DESTINATAIRES = 'contact@upandin-autonomie.fr';          // reçoit chaque nouvelle réponse (séparer par des virgules si plusieurs)

// Mot de passe de resultats.php : choisi à la première visite, stocké (haché) dans data/, jamais dans GitHub
const FICHIER_MDP   = __DIR__ . '/data/.motdepasse';

const CHOIX = [
  '1' => 'Les démarches administratives',
  '2' => 'La coordination des professionnels',
  '3' => "L'organisation des rendez-vous",
  '4' => 'Le suivi global de la situation',
];

const CONTACTS = [
  ['nom' => 'Natacha Taudin', 'titre' => 'Présidente et cofondatrice',     'tel' => '06 62 56 53 22', 'mail' => 'natacha.taudin@upandin-autonomie.fr'],
  ['nom' => 'Damien Taudin',  'titre' => 'Directeur général et cofondateur','tel' => '07 64 05 89 45', 'mail' => 'damien.taudin@upandin-autonomie.fr'],
];

const FICHIER_CSV = __DIR__ . '/data/reponses.csv';
