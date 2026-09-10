$BasePath = "C:\Users\CLIENTE\Desktop\BAHIA_SEM_FOME\weverton\t*cnicos"
$Folders = Get-ChildItem -Path $BasePath -Directory -Recurse | Where-Object { $_.Name -match '^\d{2}\.\d{2}\.\d{4}\s+(COLLETUM|ATESTE)$' }

foreach ($Folder in $Folders) {
    # Extrai só a data (os primeiros 10 caracteres)
    $NewFolderName = $Folder.Name.Substring(0, 10)
    
    try {
        Rename-Item -Path $Folder.FullName -NewName $NewFolderName -ErrorAction Stop
        Write-Host "Desfeito: $($Folder.FullName) -> $NewFolderName"
    } catch {
        Write-Host "Erro ao renomear $($Folder.FullName): $($_.Exception.Message)"
    }
}
Write-Host "Reversão concluída!"
