<?php
header('Content-Type: application/json; charset=utf-8');
require __DIR__ . '/config.php';

function repondre($ok, $msg = '') { echo json_encode(['ok' => $ok, 'message' => $msg]); exit; }
if ($_SERVER['REQUEST_METHOD'] !== 'POST') repondre(false, 'Méthode non autorisée.');

// Anti-spam : champ piège rempli = robot (on fait semblant que tout va bien)
if (!empty($_POST['site_web'])) repondre(true);

// Limite simple : 1 envoi / 30 s par IP
session_start();
if (isset($_SESSION['dernier']) && time() - $_SESSION['dernier'] < 30) repondre(false, 'Merci, votre réponse a déjà été envoyée.');

$propre = fn($v, $max) => mb_substr(trim(strip_tags((string)$v)), 0, $max);
$choix  = array_values(array_intersect(array_keys(CHOIX), (array)($_POST['choix'] ?? [])));
$prenom = $propre($_POST['prenom'] ?? '', 80);
$email  = filter_var(trim($_POST['email'] ?? ''), FILTER_VALIDATE_EMAIL);
$tel    = $propre($_POST['telephone'] ?? '', 30);
$comm   = $propre($_POST['commentaire'] ?? '', 2000);
$rappel = !empty($_POST['rappel']);

if (!$email) repondre(false, 'Adresse e-mail invalide.');
if (empty($_POST['rgpd'])) repondre(false, "Merci d'accepter l'utilisation de vos réponses.");
if (!$choix && $comm === '') repondre(false, 'Cochez au moins une réponse.');

$libelles = array_map(fn($c) => CHOIX[$c], $choix);
$date = date('Y-m-d H:i:s');

// ---- Enregistrement CSV (protège contre l'injection de formules Excel)
$sans = fn($v) => preg_match('/^[=+\-@]/', $v) ? "'" . $v : $v;
$nouveau = !file_exists(FICHIER_CSV);
$fp = fopen(FICHIER_CSV, 'a');
if (!$fp) repondre(false, 'Enregistrement impossible.');
flock($fp, LOCK_EX);
if ($nouveau) { fwrite($fp, "\xEF\xBB\xBF"); fputcsv($fp, ['Date','Prénom','E-mail','Téléphone','Choix 1','Choix 2','Choix 3','Choix 4','Commentaire','Rappel souhaité'], ';'); }
fputcsv($fp, [$date, $sans($prenom), $email, $sans($tel),
  in_array('1',$choix)?'oui':'', in_array('2',$choix)?'oui':'', in_array('3',$choix)?'oui':'', in_array('4',$choix)?'oui':'',
  $sans($comm), $rappel?'oui':''], ';');
flock($fp, LOCK_UN); fclose($fp);
$_SESSION['dernier'] = time();

// ---- Envoi des mails
function envoyer_mail($a, $sujet, $html, $replyTo = null) {
  $h  = "MIME-Version: 1.0\r\nContent-Type: text/html; charset=UTF-8\r\nContent-Transfer-Encoding: 8bit\r\n";
  $h .= 'From: =?UTF-8?B?' . base64_encode(NOM_EXPED) . '?= <' . EXPEDITEUR . ">\r\n";
  $h .= 'Reply-To: ' . ($replyTo ?: EXPEDITEUR) . "\r\n";
  return mail($a, '=?UTF-8?B?' . base64_encode($sujet) . '?=', $html, $h, '-f' . EXPEDITEUR);
}
$e = fn($v) => htmlspecialchars($v, ENT_QUOTES, 'UTF-8');

// 1) Remerciement au répondant
$bonjour = $prenom ? 'Bonjour ' . $e($prenom) . ',' : 'Bonjour,';
$cartes = '';
foreach (CONTACTS as $c) {
  $telLien = preg_replace('/\D/', '', $c['tel']);
  $cartes .= '<td style="width:50%;padding:8px;vertical-align:top"><div style="border:1px solid #c9923a;border-radius:10px;padding:16px">'
    . '<div style="font-family:Georgia,serif;font-size:18px;font-weight:bold;color:#0a2147">' . $e($c['nom']) . '</div>'
    . '<div style="font-size:13px;color:#8a6a2a;margin:2px 0 10px">' . $e($c['titre']) . '</div>'
    . '<div style="font-size:14px;line-height:1.7"><a href="tel:+33' . substr($telLien,1) . '" style="color:#0a2147;text-decoration:none">📞 ' . $e($c['tel']) . '</a><br>'
    . '<a href="mailto:' . $e($c['mail']) . '" style="color:#0a2147">✉️ ' . $e($c['mail']) . '</a></div></div></td>';
}
$merci = '<!doctype html><html><body style="margin:0;background:#f4f1ea;font-family:Arial,Helvetica,sans-serif;color:#1b2a44">'
 . '<table width="100%" cellpadding="0" cellspacing="0"><tr><td align="center" style="padding:24px 12px">'
 . '<table width="600" cellpadding="0" cellspacing="0" style="max-width:600px;width:100%;background:#fff;border-radius:12px;overflow:hidden">'
 . '<tr><td align="center" style="background:#0a2147;padding:28px"><img src="' . LOGO_URL . '" width="170" alt="Up&amp;In Family Office de l\'Autonomie" style="display:block"></td></tr>'
 . '<tr><td style="padding:32px 32px 8px;font-size:16px;line-height:1.65">'
 . '<p style="margin:0 0 14px">' . $bonjour . '</p>'
 . '<p style="margin:0 0 14px">Merci d’avoir pris le temps de répondre à notre questionnaire. Votre témoignage d’aidant nous aide à construire un accompagnement qui répond vraiment aux difficultés des familles.</p>'
 . '<p style="margin:0 0 14px">Nous avons nous-mêmes vécu la perte d’autonomie d’un proche : c’est de là qu’est né <strong>Up&amp;In Family Office de l’Autonomie</strong> — un référent unique, une vision globale et une coordination dans la durée, à domicile comme en résidence.</p>'
 . ($rappel ? '<p style="margin:0 0 14px"><strong>Vous avez souhaité être recontacté(e) : nous revenons vers vous très rapidement.</strong></p>' : '')
 . '</td></tr>'
 . '<tr><td align="center" style="padding:10px 32px 26px"><a href="' . SITE_URL . '" style="display:inline-block;background:#e8b65a;color:#0a2147;font-family:Georgia,serif;font-weight:bold;font-size:17px;padding:14px 30px;border-radius:40px;text-decoration:none">Découvrir notre accompagnement →</a></td></tr>'
 . '<tr><td style="padding:0 24px 8px;font-family:Georgia,serif;font-size:17px;color:#0a2147;text-align:center">Vos interlocuteurs</td></tr>'
 . '<tr><td style="padding:0 24px 20px"><table width="100%" cellpadding="0" cellspacing="0"><tr>' . $cartes . '</tr></table></td></tr>'
 . '<tr><td align="center" style="background:#0a2147;color:#c9d3e6;font-size:13px;line-height:1.7;padding:20px">'
 . 'Up&amp;In Family Office de l’Autonomie · Bordeaux Métropole<br>'
 . '<a href="mailto:contact@upandin-autonomie.fr" style="color:#f0c46e">contact@upandin-autonomie.fr</a> · <a href="' . SITE_URL . '" style="color:#f0c46e">www.upandin-autonomie.fr</a><br>'
 . '<span style="font-size:11px;color:#8d9bb8">Vous recevez ce message suite à votre réponse à notre questionnaire. Pour la suppression de vos données, répondez simplement à ce mail.</span>'
 . '</td></tr></table></td></tr></table></body></html>';
envoyer_mail($email, 'Merci pour votre avis – Up&In Family Office de l’Autonomie', $merci);

// 2) Notification interne
$notif = '<div style="font-family:Arial,sans-serif;font-size:15px;line-height:1.6">'
 . '<h2 style="color:#0a2147">Nouvelle réponse au questionnaire aidants</h2>'
 . '<p><b>Date :</b> ' . $date . '<br><b>Prénom :</b> ' . $e($prenom ?: '—') . '<br><b>E-mail :</b> ' . $e($email) . '<br><b>Téléphone :</b> ' . $e($tel ?: '—') . '</p>'
 . '<p><b>Ce qui pèse le plus :</b><br>' . ($libelles ? '• ' . implode('<br>• ', array_map($e, $libelles)) : '—') . '</p>'
 . '<p><b>Commentaire :</b><br>' . nl2br($e($comm ?: '—')) . '</p>'
 . '<p style="font-size:17px">' . ($rappel ? '🔔 <b style="color:#b3261e">SOUHAITE ÊTRE RECONTACTÉ(E)</b>' : 'Pas de demande de rappel') . '</p>'
 . '<p><a href="' . SITE_URL . '/avis/resultats.php">Voir tous les résultats</a></p></div>';
envoyer_mail(DESTINATAIRES, ($rappel ? '🔔 À rappeler – ' : '') . 'Nouvelle réponse questionnaire' . ($prenom ? ' – ' . $prenom : ''), $notif, $email);

repondre(true);
