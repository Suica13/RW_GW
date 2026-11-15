$ErrorActionPreference='Stop'

Add-Type -AssemblyName System.Drawing

$bitmap = [System.Drawing.Bitmap]::new(1200,170)

$canvas = [System.Drawing.Graphics]::FromImage($bitmap)

$canvas.Clear([System.Drawing.Color]::FromArgb(240,16,29,47))

$canvas.TextRenderingHint = [System.Drawing.Text.TextRenderingHint]::AntiAliasGridFit

$pen = [System.Drawing.Pen]::new([System.Drawing.Color]::Gold,3)

$canvas.DrawRectangle($pen,2,2,1195,165)

$font1 = [System.Drawing.Font]::new('Microsoft YaHei',[single]27,[System.Drawing.FontStyle]::Bold)

$font2 = [System.Drawing.Font]::new('Arial',[single]24,[System.Drawing.FontStyle]::Bold)

$format = [System.Drawing.StringFormat]::new()

$format.Alignment = [System.Drawing.StringAlignment]::Center

$canvas.DrawString('宇宙世纪包：必须启用Main，请勿与其他DLC同时加载！',$font1,[System.Drawing.Brushes]::Gold,[System.Drawing.RectangleF]::new(10,28,1180,60),$format)

$canvas.DrawString('REQUIRES MAIN. DO NOT ENABLE ANY OTHER DLC.',$font2,[System.Drawing.Brushes]::White,[System.Drawing.RectangleF]::new(10,96,1180,55),$format)

$bitmap.Save((Join-Path $PWD 'output/uc/ExclusiveLoadWarning.png'),[System.Drawing.Imaging.ImageFormat]::Png)

$canvas.Dispose()

$bitmap.Dispose()
