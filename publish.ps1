# Publie les deux commits du TP3, un push après chaque commit.
# À exécuter dans ce dossier avec PowerShell, depuis le compte GitHub autorisé.
$ErrorActionPreference = 'Continue'
Set-Location -LiteralPath $PSScriptRoot
$safePath = (Resolve-Path -LiteralPath $PSScriptRoot).Path.Replace('\', '/')
# Git voit un autre propriétaire car le dossier .git a été créé dans le sandbox.
# Cette exception est limitée au processus PowerShell courant.
$env:GIT_CONFIG_COUNT = '1'
$env:GIT_CONFIG_KEY_0 = 'safe.directory'
$env:GIT_CONFIG_VALUE_0 = $safePath
$repoUrl = 'https://github.com/AnwarEzzy/nlp-practical-labs.git'
$authorName = 'Anwar Ezzirani'
$authorEmail = 'anwar.ezzirani69@gmail.com'

if (-not (Test-Path -LiteralPath '.git')) {
    git init -b main
    if ($LASTEXITCODE -ne 0) { throw 'git init a échoué.' }
}

$remoteNames = @(git remote)
if ($LASTEXITCODE -ne 0) { throw 'Impossible de lire les dépôts distants.' }
if ($remoteNames -notcontains 'origin') {
    git remote add origin $repoUrl
    if ($LASTEXITCODE -ne 0) { throw 'Impossible de définir origin.' }
} else {
    $origin = git remote get-url origin
    if ($LASTEXITCODE -ne 0 -or $origin.Trim() -ne $repoUrl) {
        throw "origin pointe vers une autre adresse : $origin"
    }
}

$localHead = git rev-parse --verify --quiet HEAD
if ($LASTEXITCODE -eq 0) {
    throw "Ce dépôt contient déjà des commits ($localHead). Publiez ou inspectez cette histoire avant de relancer le script."
}

$remoteMain = git ls-remote --heads origin main
if ($LASTEXITCODE -ne 0) { throw 'GitHub est inaccessible. Aucun commit local créé.' }
if ($remoteMain) {
    # Conserve un éventuel premier commit créé par GitHub sans écraser les fichiers locaux.
    git fetch origin main
    if ($LASTEXITCODE -ne 0) { throw 'Impossible de récupérer la branche distante.' }
    git update-ref refs/heads/main FETCH_HEAD
    if ($LASTEXITCODE -ne 0) { throw 'Impossible de rattacher main à la branche distante.' }
    git reset --mixed HEAD
    if ($LASTEXITCODE -ne 0) { throw 'Impossible de préparer le dépôt local.' }
}

$commits = @(
    @{ Message = 'chore: initialize NLP labs repository with TP3 sources'; Paths = @('.gitignore', 'requirements.txt', 'README.md', 'publish.ps1', 'build_tp3.py', 'execute_tp3.py', 'TP3/README.md', 'TP3/sources') },
    @{ Message = 'feat: complete and execute TP3 NLP notebook'; Paths = @('TP3/*.ipynb') }
)

foreach ($item in $commits) {
    git add -- $item.Paths
    if ($LASTEXITCODE -ne 0) { throw "git add a échoué : $($item.Message)" }
    git -c "user.name=$authorName" -c "user.email=$authorEmail" commit -m $item.Message
    if ($LASTEXITCODE -ne 0) { throw "git commit a échoué : $($item.Message)" }
    git push -u origin main
    if ($LASTEXITCODE -ne 0) { throw "git push a échoué après : $($item.Message)" }
}
