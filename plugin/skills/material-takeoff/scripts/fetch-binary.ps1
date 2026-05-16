# Download the `mto.exe` binary from GitHub Releases on first run. Windows
# equivalent of fetch-binary.sh. Public download, SHA verified against the
# published SHA256SUMS manifest. License gating moves in later.
#
# Output: prints the absolute path to the downloaded binary on stdout.
# Exits non-zero on any failure.

$ErrorActionPreference = "Stop"

$skillDir = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$binRoot  = Join-Path $skillDir "bin"
$version  = (Get-Content (Join-Path $skillDir "bin-version.txt") -Raw).Trim()
$base     = "https://github.com/blackmirror-media/nio-material-take-off/releases/download/$version"

$platform = "win-x64"
$artifact = "mto-win-x64.exe"
$outDir   = Join-Path $binRoot $platform
$outPath  = Join-Path $outDir "mto.exe"

New-Item -ItemType Directory -Force -Path $outDir | Out-Null

if (Test-Path $outPath) {
  Write-Output $outPath
  exit 0
}

$tmp = New-Item -ItemType Directory -Path ([System.IO.Path]::Combine([System.IO.Path]::GetTempPath(), [System.IO.Path]::GetRandomFileName()))
try {
  Write-Host "Downloading $artifact ($version)..." -ErrorAction Continue
  Invoke-WebRequest -Uri "$base/$artifact" -OutFile (Join-Path $tmp $artifact) -UseBasicParsing
  Invoke-WebRequest -Uri "$base/SHA256SUMS" -OutFile (Join-Path $tmp "SHA256SUMS") -UseBasicParsing

  $expected = (Get-Content (Join-Path $tmp "SHA256SUMS") |
               Where-Object { $_ -match " $artifact$" } |
               ForEach-Object { ($_ -split "\s+")[0] }) | Select-Object -First 1
  if (-not $expected) { throw "Checksum entry for $artifact not found in SHA256SUMS." }

  $actual = (Get-FileHash -Algorithm SHA256 (Join-Path $tmp $artifact)).Hash.ToLower()
  if ($expected.ToLower() -ne $actual) {
    throw "Checksum mismatch. expected=$expected actual=$actual"
  }

  Move-Item -Force (Join-Path $tmp $artifact) $outPath
  Write-Output $outPath
}
finally {
  Remove-Item -Recurse -Force $tmp -ErrorAction SilentlyContinue
}
