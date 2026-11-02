<?php
require __DIR__ . '/config.php';
session_start();
$init = !file_exists(FICHIER_MDP);
if (isset($_POST['mdp'])) {
  if ($init) {
    if (strlen($_POST['mdp']) < 10) $erreur = 'Au moins 10 caractères.';
    elseif ($_POST['mdp'] !== ($_POST['mdp2'] ?? '')) $erreur = 'Les deux saisies diffèrent.';
    else { file_put_contents(FICHIER_MDP, password_hash($_POST['mdp'], PASSWORD_DEFAULT)); $_SESSION['admin'] = true; $init = false; }
  } elseif (password_verify($_POST['mdp'], trim(file_get_contents(FICHIER_MDP)))) { session_regenerate_id(true); $_SESSION['admin'] = true; }
  else { sleep(2); $erreur = 'Mot de passe incorrect.'; }
}
if (isset($_GET['sortir'])) { session_destroy(); header('Location: resultats.php'); exit; }
$admin = !empty($_SESSION['admin']);

if ($admin && isset($_GET['csv']) && file_exists(FICHIER_CSV)) {
  header('Content-Type: text/csv; charset=utf-8');
  header('Content-Disposition: attachment; filename="reponses-aidants-' . date('Y-m-d') . '.csv"');
  readfile(FICHIER_CSV); exit;
}

$lignes = [];
if ($admin && file_exists(FICHIER_CSV)) {
  $fp = fopen(FICHIER_CSV, 'r'); fgetcsv($fp, 0, ';');
  while (($l = fgetcsv($fp, 0, ';')) !== false) $lignes[] = $l;
  fclose($fp); $lignes = array_reverse($lignes);
}
$total = count($lignes);
$compte = ['1'=>0,'2'=>0,'3'=>0,'4'=>0];
$rappels = 0;
foreach ($lignes as $l) { for ($i=1;$i<=4;$i++) if (($l[3+$i] ?? '') === 'oui') $compte[(string)$i]++; if (($l[9] ?? '') === 'oui') $rappels++; }
$e = fn($v) => htmlspecialchars(ltrim((string)$v, "'"), ENT_QUOTES, 'UTF-8');
?><!doctype html>
<html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow">
<title>Résultats – Questionnaire aidants</title>
<style>
:root{--navy:#0a2147;--gold:#e8b65a}
*{box-sizing:border-box}body{margin:0;font-family:Inter,system-ui,Arial,sans-serif;background:#f4f1ea;color:#1b2a44}
header{background:var(--navy);color:#fff;padding:16px 20px;display:flex;align-items:center;gap:16px;flex-wrap:wrap}
header img{height:56px}header h1{font-family:Georgia,serif;font-size:20px;margin:0;flex:1}
header a{color:var(--gold);font-size:14px}
main{max-width:1100px;margin:0 auto;padding:20px 16px}
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:12px;margin-bottom:20px}
.k{background:#fff;border-radius:12px;padding:16px;border-top:4px solid var(--gold)}.k b{display:block;font-size:30px;font-family:Georgia,serif;color:var(--navy)}
.card{background:#fff;border-radius:12px;padding:18px;margin-bottom:20px;overflow-x:auto}
.bar{display:flex;align-items:center;gap:10px;margin:10px 0;font-size:15px}.bar span:first-child{flex:0 0 260px}
.track{flex:1;background:#eee6d6;border-radius:20px;height:22px;overflow:hidden}.fill{height:100%;background:linear-gradient(90deg,#f7d78f,#c9923a)}
table{border-collapse:collapse;width:100%;font-size:14px}th,td{text-align:left;padding:9px 8px;border-bottom:1px solid #eee;vertical-align:top}th{background:#0a2147;color:#fff;position:sticky;top:0}
.r{color:#b3261e;font-weight:600}
form.login{max-width:360px;margin:80px auto;background:#fff;padding:28px;border-radius:12px;text-align:center}
form.login input{width:100%;padding:12px;font-size:16px;border:1px solid #ccc;border-radius:8px;margin:12px 0}
form.login button,.btn{background:var(--navy);color:#fff;border:0;padding:12px 20px;border-radius:30px;font-size:15px;cursor:pointer;text-decoration:none;display:inline-block}
@media(max-width:640px){.bar span:first-child{flex-basis:140px;font-size:13px}}
</style></head><body>
<header><img src="logo.png" alt=""><h1>Questionnaire aidants — résultats</h1><?php if($admin):?><a href="?csv=1">Télécharger (Excel / Numbers)</a><a href="?sortir=1">Se déconnecter</a><?php endif;?></header>
<?php if(!$admin): ?>
<form class="login" method="post"><h2 style="font-family:Georgia,serif;color:#0a2147"><?= $init ? 'Créez votre mot de passe' : 'Accès réservé' ?></h2><?php if(!empty($erreur)) echo '<p class="r">'.$erreur.'</p>';?>
<input type="password" name="mdp" placeholder="Mot de passe" autofocus><?php if($init): ?><input type="password" name="mdp2" placeholder="Confirmez le mot de passe"><?php endif; ?><button><?= $init ? 'Enregistrer' : 'Entrer' ?></button></form>
<?php else: ?>
<main>
<div class="kpis">
  <div class="k"><b><?= $total ?></b>réponses</div>
  <div class="k"><b class="r"><?= $rappels ?></b>à rappeler</div>
  <?php arsort($compte); $top = array_key_first($compte); ?>
  <div class="k"><b><?= $total ? $e(CHOIX[$top]) : '—' ?></b><small>principale difficulté</small></div>
</div>
<div class="card"><h2 style="font-family:Georgia,serif;margin-top:0">Ce qui pèse le plus</h2>
<?php foreach (CHOIX as $k=>$lib): $n=$compte[$k]; $p=$total?round($n*100/$total):0; ?>
<div class="bar"><span><?= $e($lib) ?></span><div class="track"><div class="fill" style="width:<?= $p ?>%"></div></div><span><?= $n ?> · <?= $p ?> %</span></div>
<?php endforeach; ?>
<p style="font-size:13px;color:#777">Plusieurs choix possibles par répondant : le total peut dépasser 100 %.</p></div>
<div class="card"><h2 style="font-family:Georgia,serif;margin-top:0">Toutes les réponses</h2>
<?php if(!$total): ?><p>Aucune réponse pour l'instant.</p><?php else: ?>
<table><tr><th>Date</th><th>Prénom</th><th>Contact</th><th>Choix</th><th>Commentaire</th><th>Rappel</th></tr>
<?php foreach($lignes as $l): $ch=[]; for($i=1;$i<=4;$i++) if(($l[3+$i]??'')==='oui') $ch[]=sprintf('%02d',$i); ?>
<tr><td><?= $e(date('d/m/Y H:i', strtotime($l[0]))) ?></td><td><?= $e($l[1]) ?></td><td><a href="mailto:<?= $e($l[2]) ?>"><?= $e($l[2]) ?></a><br><?= $e($l[3]) ?></td><td><?= implode(' · ',$ch) ?></td><td><?= nl2br($e($l[8])) ?></td><td><?= ($l[9]??'')==='oui'?'<span class="r">Oui</span>':'' ?></td></tr>
<?php endforeach; ?></table><?php endif; ?></div>
</main>
<?php endif; ?>
</body></html>
