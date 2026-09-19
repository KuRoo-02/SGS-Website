<#
    Redeploy the SGS draft site to sgs.syahiriyad.com

    Usage:  powershell -ExecutionPolicy Bypass -File .\deploy.ps1

    Follows the pattern in connect.md: Windows sshpass.exe driven from
    PowerShell, credentials from .env.deploy, remote script sent base64-encoded.

    This ships ONLY the website files. Materials/ and .env.deploy are never
    copied, and the internal .md docs are excluded from the web root.
#>

$ErrorActionPreference = 'Stop'
$ProjectRoot = $PSScriptRoot
$SiteDir     = Join-Path $ProjectRoot 'Website'
$Domain      = 'sgs.syahiriyad.com'
$RemoteRoot  = "/var/www/$Domain"

# --- load .env.deploy -------------------------------------------------------
$deploy = @{}
Get-Content (Join-Path $ProjectRoot '.env.deploy') | ForEach-Object {
  if ($_ -match '^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*?)\s*$') { $deploy[$matches[1]] = $matches[2].Trim('"') }
}
$sshpass = (Get-ChildItem "$env:LOCALAPPDATA\Microsoft\WinGet\Packages" -Recurse -Filter sshpass.exe |
  Select-Object -First 1).FullName
if (-not $sshpass) { throw "sshpass.exe not found. Run: winget install xhcoding.sshpass-win32" }
$Target = "$($deploy.VPS_USERNAME)@$($deploy.VPS_HOST)"

function Invoke-Vps([string]$Script) {
  $b64 = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($Script))
  & $sshpass -p $deploy.VPS_PASSWORD ssh -o StrictHostKeyChecking=accept-new $Target "echo $b64 | base64 -d | bash"
}

# --- 1. stage into a space-free path (sshpass splits args on spaces) --------
$Stage = 'C:\Temp\sgs-stage'
$Tgz   = 'C:\Temp\sgs-site.tgz'
if (Test-Path $Stage) { Remove-Item $Stage -Recurse -Force }
if (Test-Path $Tgz)   { Remove-Item $Tgz -Force }
New-Item -ItemType Directory -Path $Stage -Force | Out-Null

foreach ($f in @('index.html','about.html','services.html','news.html','news-article.html','contact.html')) {
  Copy-Item (Join-Path $SiteDir $f) $Stage
}
Copy-Item (Join-Path $SiteDir 'assets') $Stage -Recurse

Write-Host "Staged $((Get-ChildItem $Stage -Recurse -File).Count) files" -ForegroundColor Cyan
tar -czf $Tgz -C $Stage .

# --- 2. upload --------------------------------------------------------------
& $sshpass -p $deploy.VPS_PASSWORD scp -o StrictHostKeyChecking=accept-new $Tgz "$($Target):/tmp/sgs-site.tgz"
if ($LASTEXITCODE -ne 0) { throw "scp failed" }
Write-Host "Uploaded" -ForegroundColor Cyan

# --- 3. swap in atomically, then verify ------------------------------------
Invoke-Vps @"
set -e
NEW=/var/www/.sgs-new
OLD=/var/www/.sgs-old
mkdir -p "`$NEW"
find "`$NEW" -mindepth 1 -delete
tar -xzf /tmp/sgs-site.tgz -C "`$NEW"
chown -R www-data:www-data "`$NEW"
find "`$NEW" -type d -exec chmod 755 {} \;
find "`$NEW" -type f -exec chmod 644 {} \;

# atomic-ish swap so the site is never half-written
if [ -d $RemoteRoot ]; then mv $RemoteRoot "`$OLD"; fi
mv "`$NEW" $RemoteRoot
if [ -d "`$OLD" ]; then find "`$OLD" -mindepth 1 -delete; rmdir "`$OLD"; fi
find /tmp -maxdepth 1 -name sgs-site.tgz -delete

nginx -t >/dev/null 2>&1 && systemctl reload nginx
echo "deployed: `$(find $RemoteRoot -type f | wc -l) files, `$(du -sh $RemoteRoot | cut -f1)"

# reload is asynchronous — give the new workers a moment or the check races it.
# Plain `if`, not `test && break`: under `set -e` a failing && list aborts the script.
sleep 2
code=000
for i in 1 2 3; do
  code=`$(curl -sk -o /dev/null -w "%{http_code}" --resolve ${Domain}:443:127.0.0.1 https://$Domain/ || echo 000)
  if [ "`$code" = "200" ]; then
    break
  fi
  sleep 2
done
echo "origin check: `$code"
"@

# --- 4. public check --------------------------------------------------------
Start-Sleep -Seconds 2
$r = Invoke-WebRequest "https://$Domain/" -UseBasicParsing -TimeoutSec 30
Write-Host "https://$Domain -> $($r.StatusCode) ($($r.RawContentLength) bytes)" -ForegroundColor Green
