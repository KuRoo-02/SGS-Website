<?php
/**
 * SGS — shared hosting pre-flight check.
 *
 * On cPanel shared hosting you usually cannot SSH in, and the cPanel UI
 * reports what you asked for rather than what PHP actually got. This file
 * reports the real, effective values.
 *
 * HOW TO USE
 *   1. Upload to the domain's document root (public_html/)
 *   2. Visit https://yourdomain.com/sgs-preflight.php
 *   3. Read the verdicts
 *   4. DELETE IT. It exposes server internals — do not leave it published.
 *
 * Safe: read-only apart from one temp file written and removed in the
 * uploads test. Nothing is sent anywhere.
 */

header('Content-Type: text/html; charset=utf-8');

// --- helpers ---------------------------------------------------------------
function to_bytes($val) {
    $val = trim((string)$val);
    if ($val === '' || $val === '-1') return -1;
    $last = strtolower($val[strlen($val) - 1]);
    $num  = (float)$val;
    switch ($last) {
        case 'g': $num *= 1024;
        case 'm': $num *= 1024;
        case 'k': $num *= 1024;
    }
    return (int)$num;
}
$rows = [];
function check($name, $actual, $ok, $want, $note = '') {
    global $rows;
    $rows[] = [$name, $actual, $ok, $want, $note];
}

// --- PHP -------------------------------------------------------------------
$phpv = PHP_VERSION;
check('PHP version', $phpv, version_compare($phpv, '8.1', '>='), '8.1+ (8.2/8.3 ideal)',
      'Elementor drops support for older PHP');

$mem = to_bytes(ini_get('memory_limit'));
check('memory_limit', ini_get('memory_limit'), ($mem < 0 || $mem >= 256*1024*1024), '256M min, 512M ideal',
      'Editor white-screens on long pages below this');

$met = (int)ini_get('max_execution_time');
check('max_execution_time', $met . 's', ($met === 0 || $met >= 120), '120s min, 300s ideal',
      'Saving a long page times out');

$miv = (int)ini_get('max_input_vars');
check('max_input_vars', $miv ?: 'unset', $miv >= 3000, '3000 min, 5000 ideal',
      'MOST IMPORTANT: too low = widgets silently vanish on save');

$pms = to_bytes(ini_get('post_max_size'));
check('post_max_size', ini_get('post_max_size'), $pms >= 32*1024*1024, '32M min, 64M ideal', '');

$umf = to_bytes(ini_get('upload_max_filesize'));
check('upload_max_filesize', ini_get('upload_max_filesize'), $umf >= 32*1024*1024, '32M min, 64M ideal', '');

$mit = (int)ini_get('max_input_time');
check('max_input_time', $mit . 's', ($mit === -1 || $mit >= 120), '120s+', '');

// --- extensions ------------------------------------------------------------
foreach (['curl','mbstring','zip','dom','xml','json','intl'] as $x) {
    check("ext: $x", extension_loaded($x) ? 'loaded' : 'MISSING', extension_loaded($x), 'required', '');
}
$img = extension_loaded('imagick') ? 'imagick' : (extension_loaded('gd') ? 'gd only' : 'NEITHER');
check('image library', $img, $img !== 'NEITHER', 'imagick preferred',
      'gd alone is workable; imagick gives better thumbnails');

// --- functions commonly disabled on shared hosting -------------------------
$disabled = array_filter(array_map('trim', explode(',', (string)ini_get('disable_functions'))));
foreach (['file_get_contents','fsockopen','proc_open','exec'] as $fn) {
    $off = in_array($fn, $disabled, true) || !function_exists($fn);
    $crit = in_array($fn, ['file_get_contents','fsockopen'], true);
    check("function: $fn", $off ? 'disabled' : 'available', $crit ? !$off : true,
          $crit ? 'needed' : 'optional',
          $crit ? 'WordPress/plugin HTTP calls need this' : 'only some plugins need it');
}
check('allow_url_fopen', ini_get('allow_url_fopen') ? 'on' : 'off',
      (bool)ini_get('allow_url_fopen'), 'on', 'Plugin/theme installs may fail without it');

// --- the Authorization header (kills Application Passwords) ----------------
$hasAuth = !empty($_SERVER['HTTP_AUTHORIZATION']) || !empty($_SERVER['REDIRECT_HTTP_AUTHORIZATION']);
$sapi = php_sapi_name();
$cgi  = (stripos($sapi, 'cgi') !== false || stripos($sapi, 'fpm') !== false);
check('PHP SAPI', $sapi, true, 'informational',
      $cgi ? 'CGI/FPM: Authorization header is often stripped' : '');
check('Authorization header', $hasAuth ? 'received' : 'not seen on this request', true,
      'test with auth',
      'Re-test this URL with Basic auth. If still not seen, add the .htaccess rule below.');

// --- writability -----------------------------------------------------------
$root = __DIR__;
check('document root writable', is_writable($root) ? 'yes' : 'no', is_writable($root), 'yes',
      'Needed for plugin/theme installs and .htaccess updates');

$uploadTest = false;
$updir = $root . '/wp-content/uploads';
if (is_dir($updir)) {
    $tmp = $updir . '/.sgs-preflight-test';
    $uploadTest = @file_put_contents($tmp, 'x') !== false;
    if ($uploadTest) @unlink($tmp);
    check('uploads writable', $uploadTest ? 'yes' : 'NO', $uploadTest, 'yes', '');
} else {
    check('uploads dir', 'not found', true, 'n/a', 'WordPress not installed here yet');
}

// --- resources -------------------------------------------------------------
$load = function_exists('sys_getloadavg') ? sys_getloadavg() : null;
check('server load (1m)', $load ? round($load[0], 2) : 'n/a', true, 'informational',
      'Shared hosting: high load means neighbours are busy');
check('CloudLinux LVE', file_exists('/proc/self/cagefs') || is_dir('/usr/share/cagefs') ? 'likely present' : 'not detected',
      true, 'informational', 'LVE caps CPU, memory and entry processes — 508 errors come from here');

// --- WordPress present? ----------------------------------------------------
$wpVer = null;
if (file_exists($root . '/wp-includes/version.php')) {
    include $root . '/wp-includes/version.php';
    $wpVer = $wp_version ?? null;
}
check('WordPress', $wpVer ? "v$wpVer" : 'not installed in this folder', true, 'informational', '');

// --- REST API reachable? ---------------------------------------------------
$restNote = 'skipped (WordPress not detected)';
$restOk = true;
if ($wpVer && function_exists('curl_init')) {
    $scheme = (!empty($_SERVER['HTTPS']) && $_SERVER['HTTPS'] !== 'off') ? 'https' : 'http';
    $url = $scheme . '://' . $_SERVER['HTTP_HOST'] . '/wp-json/';
    $ch = curl_init($url);
    curl_setopt_array($ch, [CURLOPT_RETURNTRANSFER => true, CURLOPT_TIMEOUT => 10,
                            CURLOPT_SSL_VERIFYPEER => false, CURLOPT_NOBODY => false]);
    $body = curl_exec($ch);
    $code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
    curl_close($ch);
    $restOk = ($code === 200);
    $restNote = "GET /wp-json/ returned $code" . ($restOk ? '' : ' — blocked, or permalinks are still Plain');
}
check('REST API', $restOk ? 'reachable' : 'PROBLEM', $restOk, '200 from /wp-json/', $restNote);

// --- render ----------------------------------------------------------------
$fail = 0; $warn = 0;
foreach ($rows as $r) { if (!$r[2]) $fail++; }
?>
<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>SGS — hosting pre-flight</title>
<style>
 body{font:15px/1.6 system-ui,-apple-system,Segoe UI,sans-serif;margin:0;background:#f5f7f9;color:#15191e}
 .wrap{max-width:1000px;margin:0 auto;padding:32px 20px 64px}
 h1{font-size:24px;margin:0 0 4px} .sub{color:#545c66;margin:0 0 24px}
 .banner{padding:14px 18px;border-radius:8px;margin:0 0 24px;font-weight:600}
 .good{background:#eef7e4;color:#3f6619;border:1px solid #cde3b4}
 .bad{background:#fbebef;color:#7a1433;border:1px solid #f0c4ce}
 table{width:100%;border-collapse:collapse;background:#fff;border:1px solid #e1e6eb;border-radius:8px;overflow:hidden}
 th,td{text-align:left;padding:10px 14px;border-bottom:1px solid #eef1f4;vertical-align:top;font-size:14px}
 th{background:#12040a;color:#fff;font-size:12px;letter-spacing:.06em;text-transform:uppercase}
 tr:last-child td{border-bottom:0}
 .ok{color:#3f6619;font-weight:700}.no{color:#a3122f;font-weight:700}
 .note{color:#666d76;font-size:13px}
 code{background:#f0f3f6;padding:1px 5px;border-radius:3px;font-size:13px}
 pre{background:#12040a;color:#e8eef2;padding:16px;border-radius:8px;overflow:auto;font-size:13px}
 .warn{margin-top:28px;padding:16px 18px;background:#fff;border:1px solid #e1e6eb;border-left:4px solid #440115;border-radius:6px}
</style></head><body><div class="wrap">
<h1>SGS — hosting pre-flight</h1>
<p class="sub">Effective PHP values as seen by this server, not what the control panel claims.</p>

<div class="banner <?= $fail ? 'bad' : 'good' ?>">
<?= $fail ? "$fail check(s) need attention before building." : "All checks passed." ?>
</div>

<table>
<tr><th>Check</th><th>Actual</th><th></th><th>Needed</th><th>Note</th></tr>
<?php foreach ($rows as [$n, $a, $ok, $want, $note]): ?>
<tr>
  <td><strong><?= htmlspecialchars($n) ?></strong></td>
  <td><code><?= htmlspecialchars((string)$a) ?></code></td>
  <td class="<?= $ok ? 'ok' : 'no' ?>"><?= $ok ? 'OK' : 'FIX' ?></td>
  <td class="note"><?= htmlspecialchars($want) ?></td>
  <td class="note"><?= htmlspecialchars($note) ?></td>
</tr>
<?php endforeach; ?>
</table>

<div class="warn">
  <strong>If Application Passwords / the REST API return 401</strong>
  <p>Most cPanel hosts run PHP as CGI/FastCGI and drop the <code>Authorization</code> header.
  Add this to <code>.htaccess</code> <em>above</em> the <code># BEGIN WordPress</code> block:</p>
<pre>RewriteEngine On
RewriteCond %{HTTP:Authorization} ^(.*)
RewriteRule .* - [E=HTTP_AUTHORIZATION:%{HTTP:Authorization}]</pre>
</div>

<div class="warn">
  <strong>If a PHP value above cannot be changed</strong>
  <p>Try cPanel &rsaquo; MultiPHP INI Editor, then a <code>.user.ini</code> in the document root,
  then <code>php_value</code> lines in <code>.htaccess</code>. If the host hard-caps it
  (common for <code>memory_limit</code> and <code>max_execution_time</code>), raise a support
  ticket — most will lift limits on request. If they will not, say so before the build starts:
  it changes what is safely buildable.</p>
</div>

<div class="warn">
  <strong>Delete this file now.</strong>
  <p>It exposes server configuration. Remove <code>sgs-preflight.php</code> from the document root.</p>
</div>
</div></body></html>
