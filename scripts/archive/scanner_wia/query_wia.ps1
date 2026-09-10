$deviceManager = New-Object -ComObject WIA.DeviceManager
foreach ($info in $deviceManager.DeviceInfos) {
    Write-Output "---"
    Write-Output $info.Properties.Item("Name").Value
    try {
        $device = $info.Connect()
        foreach ($prop in $device.Properties) {
            Write-Output "$($prop.PropertyID) - $($prop.Name): $($prop.Value)"
        }
    } catch {
        Write-Output "Could not connect to this device: $_"
    }
}
