$deviceManager = New-Object -ComObject WIA.DeviceManager
foreach ($info in $deviceManager.DeviceInfos) {
    if ($info.Properties.Item("Name").Value -like "*CANON*") {
        Write-Output "Tentando conectar no Canon..."
        try {
            $device = $info.Connect()
            Write-Output "Conectado!"
        } catch {
            Write-Output "Erro: $_"
        }
    }
}
