$ErrorActionPreference = 'Stop'
try {
    $deviceManager = New-Object -ComObject WIA.DeviceManager
    $device = $null
    
    foreach ($info in $deviceManager.DeviceInfos) {
        if ($info.Properties.Item("Name").Value -like "*CANON*" -or $info.Type -eq 1) {
            $device = $info.Connect()
            break
        }
    }

    if ($null -eq $device) { exit 1 }

    # Configuração explícita do alimentador de páginas (ADF Feeder)
    try { $device.Properties.Item("3088").Value = 1 } catch {} # 1 = Feeder
    try { $device.Properties.Item("3096").Value = 0 } catch {} # 0 = All Pages

    $imageFormatId = "{B96B3CAE-0728-11D3-9D7B-0000F81EF32E}"
    $outputDir = "c:\Users\CLIENTE\Desktop\weverton\agendha-vercel\temp_adf"
    if (-not (Test-Path $outputDir)) { New-Item -ItemType Directory -Path $outputDir | Out-Null }

    $pageCount = 0
    while ($true) {
        try {
            $item = $device.Items.Item(1)
            $image = $item.Transfer($imageFormatId)
            $pageCount++
            $filePath = Join-Path $outputDir "sheet_$pageCount.jpg"
            if (Test-Path $filePath) { Remove-Item $filePath -Force }
            $image.SaveFile($filePath)
            Write-Host "PAGINA_CAPTURADA:" $filePath
            Start-Sleep -Milliseconds 500
        } catch {
            break
        }
    }
    Write-Host "TOTAL_PAGINAS:" $pageCount
} catch {
    Write-Host "ERRO:" $_.Exception.Message
}
