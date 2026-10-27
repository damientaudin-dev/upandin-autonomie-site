<?php
// Réception du sondage — envoie les réponses par e-mail à contact@upandin-autonomie.fr
// Aucune donnée n'est stockée sur le serveur.
header('Content-Type: application/json; charset=utf-8');
header('X-Robots-Tag: noindex');

$DEST = 'contact@upandin-autonomie.fr';
$FROM = 'contact@upandin-autonomie.fr';

if ($_SERVER['REQUEST_METHOD'] !== 'POST') { http_response_code(405); echo '{"ok":false}'; exit; }

$raw = file_get_contents('php://input', false, null, 0, 20000);
$data = json_decode($raw, true);
if (!is_array($data) || !isset($data['reponses']) || !is_array($data['reponses'])) {
  http_response_code(400); echo '{"ok":false}'; exit;
}
// Pot de miel anti-robots : on répond OK sans rien envoyer
if (!empty($data['site'])) { echo '{"ok":true}'; exit; }

// Limite simple : 1 envoi / 20 s par visiteur
session_start();
if (isset($_SESSION['sondage_t']) && time() - $_SESSION['sondage_t'] < 20) { http_response_code(429); echo '{"ok":false}'; exit; }
$_SESSION['sondage_t'] = time();

$clean = function ($v) {
  $v = is_scalar($v) ? (string)$v : '';
  $v = preg_replace('/[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]/u', '', $v);
  return mb_substr(trim($v), 0, 1500);
};
$r = $data['reponses'];
$fmt = function ($k) use ($r, $clean) {
  if (!isset($r[$k])) return '—';
  if (is_array($r[$k])) return implode(' ; ', array_map($clean, array_slice($r[$k], 0, 12)));
  $s = $clean($r[$k]); return $s === '' ? '—' : $s;
};
$rap = isset($r['rappel']) && is_array($r['rappel']) ? $r['rappel'] : [];
$nom = $clean($rap['nom'] ?? ''); $tel = $clean($rap['tel'] ?? '');

$lignes = [
  'Profil'                 => $fmt('profil'),
  'Préoccupations'         => $fmt('soucis'),
  'Services utiles'        => $fmt('services'),
  'Fréquence'              => $fmt('frequence'),
  'Moyens d\'information'  => $fmt('contact'),
  'Budget mensuel'         => $fmt('budget'),
  'Commune'                => $fmt('commune'),
  'Ce qui simplifierait'   => $fmt('libre'),
  'À recontacter'          => ($nom || $tel) ? trim("$nom · $tel", ' ·') : 'Non',
];
$corps = "Nouvelle réponse au sondage — " . date('d/m/Y H:i') . "\n\n";
foreach ($lignes as $k => $v) $corps .= "$k :\n  $v\n\n";
$corps .= "—\nEnvoyé depuis www.upandin-autonomie.fr/sondage";

$sujet = '=?UTF-8?B?' . base64_encode('Sondage — ' . $fmt('profil') . (($nom || $tel) ? ' — à recontacter' : '')) . '?=';
$entetes = "From: Site Up&In <$FROM>\r\nMIME-Version: 1.0\r\nContent-Type: text/plain; charset=UTF-8\r\nContent-Transfer-Encoding: 8bit";

$ok = @mail($DEST, $sujet, $corps, $entetes, "-f$FROM");
if (!$ok) { http_response_code(500); echo '{"ok":false}'; exit; }
echo '{"ok":true}';
