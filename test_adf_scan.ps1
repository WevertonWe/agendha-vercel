$ErrorActionPreference = 'Stop'
try {
    $deviceManager = New-Object -ComObject WIA.DeviceManager
    $device = $null
    
    foreach ($info in $deviceManager.DeviceInfos) {
        if ($info.Properties.Item("Name").Value -like "*CANON*" -or $info.Type -eq 1) {
            Write-Host "Conectando ao scanner Canon ADF:" $info.Properties.Item("Name").Value
            $device = $info.Connect()
            break
        }
    }

    if ($null -eq $device) {
        Write-Host "ERRO: Nenhum scanner encontrado"
        exit 1
    }

    # Configura para Feeder (1 = Feeder, 4 = Duplex)
    try { $device.Properties.Item("3088").Value = 1 } catch {}
    try { $device.Properties.Item("3096").Value = 1 } catch {} # 1 por 1 ou 0 para lote

    $imageFormatId = "{B96B3CAE-0728-11D3-9D7B-0000F81EF32E}"
    $outputDir = "c:\Users\CLIENTE\Desktop\weverton\agendha-vercel\temp_adf"
    if (-not (Test-Path $outputDir)) { New-Item -ItemType Directory -Path $outputDir | Out-Null }

    Write-Host "Iniciando captura de paginas no alimentador ADF..."
    
    $pageCount = 0
    while ($true) {
        try {
            $item = $device.Items.Item(1)
            $image = $item.Transfer($imageFormatId)
            $pageCount++
            $filePath = Join-Path $outputDir "page_$pageCount.jpg"
            if (Test-Path $filePath) { Remove-Item $filePath -Force }
            $image.SaveFile($filePath)
            Write-Host "PAGINA_CAPTURADA:" $filePath
        } catch {
            Write-Host "Fim das paginas no alimentador ADF ou sem mais papel."
            break
        }
    }

    Write-Host "TOTAL_PAGINAS_CAPTURADAS:" $pageCount
} catch {
    Write-Host "ERRO ADF:" $_.Exception.Message
}
