$deviceManager = New-Object -ComObject WIA.DeviceManager
foreach ($info in $deviceManager.DeviceInfos) {
    Write-Output "Name: $($info.Properties.Item('Name').Value)"
    Write-Output "Type: $($info.Type)"
}
