# Deterministic transparent text textures. Run from any working directory.
param([switch]$PreviewOnly)
$ErrorActionPreference='Stop'
Add-Type -AssemblyName System.Drawing
$workspaceRoot=Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$buttonRoot=Join-Path $workspaceRoot 'GW_BattleUniverse_DLC_0093\Resource\Image\Text\Button'
$previewRoot=Join-Path $PSScriptRoot '年代按钮预览'
New-Item -ItemType Directory -Path $previewRoot -Force | Out-Null
$labels=[ordered]@{
    'Button_UC0079.png'='UC.0079'
    'Button_UC0087.png'='UC.0087'
    'Button_CE71.png'='SEED.CE71'
    'Button_CE73.png'='SEED.CE73'
    'Button_AD2308.png'='A.D.2308'
    'Button_UC0093.png'='UC.0093'
}
$scale=4
$family=[Drawing.FontFamily]::new('Arial')
$brush=[Drawing.SolidBrush]::new([Drawing.Color]::White)
$sheet=[Drawing.Bitmap]::new(390,180,[Drawing.Imaging.PixelFormat]::Format32bppArgb)
$sheetGraphics=[Drawing.Graphics]::FromImage($sheet)
$sheetGraphics.Clear([Drawing.Color]::FromArgb(255,24,32,43))
$index=0
try {
    foreach($entry in $labels.GetEnumerator()) {
        $path=[Drawing.Drawing2D.GraphicsPath]::new()
        $format=[Drawing.StringFormat]::GenericTypographic.Clone()
        $path.AddString($entry.Value,$family,[int][Drawing.FontStyle]::Bold,[single](24*$scale),[Drawing.PointF]::new(0,0),$format)
        $bounds=$path.GetBounds()
        $fit=[Math]::Min(1.0,(114*$scale)/$bounds.Width)
        $transform=[Drawing.Drawing2D.Matrix]::new()
        $transform.Translate(-$bounds.X,-$bounds.Y)
        $path.Transform($transform)
        $transform.Dispose()
        $transform=[Drawing.Drawing2D.Matrix]::new()
        $transform.Scale([single]$fit,[single]$fit)
        $path.Transform($transform)
        $transform.Dispose()
        $bounds=$path.GetBounds()
        $transform=[Drawing.Drawing2D.Matrix]::new()
        $transform.Translate([single]((130*$scale-$bounds.Width)/2),[single]((60*$scale-$bounds.Height)/2))
        $path.Transform($transform)
        $hi=[Drawing.Bitmap]::new((130*$scale),(60*$scale),[Drawing.Imaging.PixelFormat]::Format32bppArgb)
        $hiGraphics=[Drawing.Graphics]::FromImage($hi)
        $hiGraphics.Clear([Drawing.Color]::Transparent)
        $hiGraphics.SmoothingMode=[Drawing.Drawing2D.SmoothingMode]::AntiAlias
        $hiGraphics.FillPath($brush,$path)
        $final=[Drawing.Bitmap]::new(130,60,[Drawing.Imaging.PixelFormat]::Format32bppArgb)
        $graphics=[Drawing.Graphics]::FromImage($final)
        $graphics.Clear([Drawing.Color]::Transparent)
        $graphics.CompositingMode=[Drawing.Drawing2D.CompositingMode]::SourceCopy
        $graphics.InterpolationMode=[Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
        $graphics.PixelOffsetMode=[Drawing.Drawing2D.PixelOffsetMode]::HighQuality
        $graphics.DrawImage($hi,[Drawing.Rectangle]::new(0,0,130,60),0,0,$hi.Width,$hi.Height,[Drawing.GraphicsUnit]::Pixel)
        $destination=if($PreviewOnly){ Join-Path $previewRoot $entry.Key }else{ Join-Path $buttonRoot $entry.Key }
        $final.Save($destination,[Drawing.Imaging.ImageFormat]::Png)
        $sheetGraphics.DrawImageUnscaled($final,(($index%3)*130),([Math]::Floor($index/3)*90))
        $labelFont=[Drawing.Font]::new('Arial',10,[Drawing.FontStyle]::Regular,[Drawing.GraphicsUnit]::Pixel)
        $sheetGraphics.DrawString($entry.Key,$labelFont,$brush,[single](($index%3)*130+4),[single]([Math]::Floor($index/3)*90+62))
        $labelFont.Dispose()
        $graphics.Dispose();$final.Dispose();$hiGraphics.Dispose();$hi.Dispose()
        $path.Dispose();$format.Dispose();$transform.Dispose()
        $index++
        Write-Output $destination
    }
    $sheet.Save((Join-Path $previewRoot '年代按钮总览.png'),[Drawing.Imaging.ImageFormat]::Png)
} finally {
    $sheetGraphics.Dispose();$sheet.Dispose();$brush.Dispose();$family.Dispose()
}