$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Drawing
$asset = Split-Path $PSScriptRoot
$repo = (Resolve-Path (Join-Path $asset '../../..')).Path
$rawFolder = Join-Path $repo 'build/garden-models'
$catalog = Get-Content (Join-Path $repo 'art/refs/garden-plants/catalog.html') -Raw -Encoding utf8
$names = [regex]::Matches($catalog,'<figcaption><span>(\d+)</span> ([^<]+) <small>')
if ($names.Count -ne 36) { throw 'Expected 36 plants in the approved catalog.' }
$cell = 320
$caption = 42
$paper = [Drawing.Color]::FromArgb(235,240,245)
$ink = [Drawing.SolidBrush]::new([Drawing.Color]::FromArgb(38,57,53))
$label = [Drawing.Font]::new('Segoe UI',17,[Drawing.FontStyle]::Bold,[Drawing.GraphicsUnit]::Pixel)
$fmt = [Drawing.StringFormat]::new()
$fmt.Alignment = 'Center'
$fmt.LineAlignment = 'Center'
$encoder = [Drawing.Imaging.ImageCodecInfo]::GetImageEncoders() | Where-Object MimeType -eq 'image/jpeg'
$settings = [Drawing.Imaging.EncoderParameters]::new(1)
$settings.Param[0] = [Drawing.Imaging.EncoderParameter]::new([Drawing.Imaging.Encoder]::Quality,[long]92)
foreach ($view in @('front','side','back','top','three-quarter')) {
    $source = [Drawing.Image]::FromFile((Join-Path $rawFolder ($view+'.png')))
    $canvas = [Drawing.Bitmap]::new($cell*6,($cell+$caption)*6)
    $g = [Drawing.Graphics]::FromImage($canvas)
    $g.Clear($paper)
    $g.InterpolationMode = 'HighQualityBicubic'
    $g.TextRenderingHint = 'AntiAliasGridFit'
    for ($i=0; $i -lt $names.Count; $i++) {
        $x = ($i % 6)*$cell
        $row = [int][Math]::Floor($i/6)
        $y = $row*($cell+$caption)
        $dest = [Drawing.Rectangle]::new($x,$y,$cell,$cell)
        $g.DrawImage($source,$dest,$x,($row*$cell),$cell,$cell,[Drawing.GraphicsUnit]::Pixel)
        $rect = [Drawing.RectangleF]::new($x,($y+$cell-5),$cell,$caption)
        $text = $names[$i].Groups[1].Value + '  ' + $names[$i].Groups[2].Value
        $g.DrawString($text,$label,$ink,$rect,$fmt)
    }
    $out = Join-Path $asset ('reports/'+$view+'.jpg')
    $canvas.Save($out,$encoder,$settings)
    $g.Dispose(); $canvas.Dispose(); $source.Dispose()
}
$label.Dispose(); $ink.Dispose(); $fmt.Dispose(); $settings.Dispose()
