$BasePath = "C:\Users\CLIENTE\Desktop\BAHIA_SEM_FOME\weverton\t*cnicos"
$Folders = Get-ChildItem -Path $BasePath -Directory -Recurse | Where-Object { $_.Name -match '^\d{2}\.\d{2}\.\d{4}$' }

foreach ($Folder in $Folders) {
    # Pega o primeiro arquivo que tenha " - " no nome (normalmente os pdfs tem: NOME - ATIVIDADE.pdf)
    $File = Get-ChildItem -Path $Folder.FullName -File | Where-Object { $_.Name -match ' - ' } | Select-Object -First 1
    
    if ($null -ne $File) {
        $BaseName = $File.BaseName
        $Parts = $BaseName -split ' - '
        
        if ($Parts.Length -ge 2) {
            $Atividade = $Parts[-1].Trim()
            $NewFolderName = "$($Folder.Name) $Atividade"
            
            try {
                Rename-Item -Path $Folder.FullName -NewName $NewFolderName -ErrorAction Stop
                Write-Host "Renomeado: $($Folder.FullName) -> $NewFolderName"
            } catch {
                Write-Host "Erro ao renomear $($Folder.FullName): $($_.Exception.Message)"
            }
        }
    } else {
        Write-Host "Aviso: Nenhum arquivo valido encontrado na pasta $($Folder.FullName)"
    }
}
Write-Host "Finalizado"
