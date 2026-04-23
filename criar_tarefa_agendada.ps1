# Executar como Administrador
$action = New-ScheduledTaskAction `
    -Execute "C:\Users\stefa\AppData\Local\Programs\Python\Python311\python.exe" `
    -Argument "e:\Claude\Projetos\instagram_bot\scheduler.py" `
    -WorkingDirectory "e:\Claude\Projetos\instagram_bot"

$trigger = New-ScheduledTaskTrigger -Daily -At "09:00AM"

$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -ExecutionTimeLimit (New-TimeSpan -Hours 2)

Register-ScheduledTask `
    -TaskName "InstagramBot" `
    -Action $action `
    -Trigger $trigger `
    -Settings $settings `
    -Description "Gera carrossel do Instagram diariamente às 9h" `
    -Force

Write-Host "Tarefa 'InstagramBot' criada com sucesso!" -ForegroundColor Green
