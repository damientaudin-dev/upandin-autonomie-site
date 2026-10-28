<?php
// Formulaire « Demande de rappel ou de rendez-vous » — envoi à contact@upandin-autonomie.fr
// (redirigé vers Damien et Natacha). Aucune donnée n'est stockée sur le serveur.
header('Content-Type: application/json; charset=utf-8');
header('X-Robots-Tag: noindex');

$DEST = 'contact@upandin-autonomie.fr';
$FROM = 'contact@upandin-autonomie.fr';

if ($_SERVER['REQUEST_METHOD'] !== 'POST') { http_response_code(405); echo '{"ok":false,"fallback":true}'; exit; }
$d = json_decode(file_get_contents('php://input', false, null, 0, 20000), true);
if (!is_array($d)) { http_response_code(400); echo '{"ok":false,"error":"Demande invalide."}'; exit; }
if (!empty($d['website'])) { echo '{"ok":true}'; exit; } // pot de miel anti-robots

session_start();
if (isset($_SESSION['contact_t']) && time() - $_SESSION['contact_t'] < 20) {
  http_response_code(429); echo '{"ok":false,"error":"Merci de patienter quelques secondes avant un nouvel envoi."}'; exit;
}

$c = function ($k, $max = 200) use ($d) {
  $v = isset($d[$k]) && is_scalar($d[$k]) ? (string)$d[$k] : '';
  $v = preg_replace('/[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]/u', '', $v);
  return mb_substr(trim($v), 0, $max);
};
$nom = $c('nom', 120); $tel = $c('tel', 40); $email = $c('email', 160);
$profil = $c('profil', 80); $objet = $c('objet', 80); $message = $c('message', 3000);

if ($nom === '' || ($tel === '' && $email === '')) {
  http_response_code(422); echo '{"ok":false,"error":"Merci d’indiquer votre nom et un téléphone ou un e-mail."}'; exit;
}
if ($email !== '' && !filter_var($email, FILTER_VALIDATE_EMAIL)) {
  http_response_code(422); echo '{"ok":false,"error":"L’adresse e-mail semble incorrecte."}'; exit;
}
$_SESSION['contact_t'] = time();

$corps = "Nouvelle demande depuis le site — " . date('d/m/Y H:i') . "\n\n"
  . "Nom : $nom\nTéléphone : " . ($tel ?: '—') . "\nE-mail : " . ($email ?: '—') . "\n"
  . "Vous êtes : $profil\nDemande : $objet\n\nMessage :\n" . ($message ?: '—') . "\n\n—\nEnvoyé depuis www.upandin-autonomie.fr";
$sujet = '=?UTF-8?B?' . base64_encode("[Site] $objet — $nom") . '?=';
$entetes = "From: Site Up&In <$FROM>\r\nMIME-Version: 1.0\r\nContent-Type: text/plain; charset=UTF-8\r\nContent-Transfer-Encoding: 8bit";
if ($email !== '') $entetes .= "\r\nReply-To: $email";

if (!@mail($DEST, $sujet, $corps, $entetes, "-f$FROM")) { http_response_code(500); echo '{"ok":false,"fallback":true}'; exit; }
echo '{"ok":true}';
