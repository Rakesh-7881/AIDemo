pipeline {
    agent any

    environment {
        APP_PORT = "5000"
        OPENAI_API_KEY = credentials('OPENAI_API_KEY') // keep if your app needs it
    }

    stages {
        stage('Checkout') {
            steps {
                checkout([
                    $class: 'GitSCM',
                    branches: [[name: '*/main']],
                    userRemoteConfigs: [[
                        url: 'https://github.com/Rakesh-7881/AIDemo.git'
                    ]],
                    gitTool: 'Default'
                ])
            }
        }

        stage('Setup Python venv & deps') {
            steps {
                bat '''
                    C:\\Python311\\python -m venv venv
                    venv\\Scripts\\pip install --upgrade pip setuptools wheel
                    venv\\Scripts\\pip install -r requirements.txt
                '''
            }
        }

        stage('Stop old app (if any)') {
            steps {
                powershell '''
                    $port = $env:APP_PORT
                    $pids = @()
                    try {
                        $conns = Get-NetTCPConnection -LocalPort $port -ErrorAction Stop
                        if ($conns) { $pids = $conns | Select-Object -ExpandProperty OwningProcess -Unique }
                    } catch {
                        $lines = netstat -ano | findstr ":$port"
                        foreach ($line in $lines) {
                            $parts = $line -split '\\s+'
                            $pids += $parts[-1]
                        }
                    }
                    foreach ($pid in $pids | Where-Object { $_ -ne $null }) {
                        try { Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue } catch {}
                    }
                    Write-Host "Stopped old processes on port $port (if any)"
                '''
            }
        }

stage('Start app (detached)') {
    steps {
        powershell '''
        Start-Process -NoNewWindow -FilePath "venv\\Scripts\\python.exe" -ArgumentList "app.py --port 5000"
        Start-Sleep -Seconds 5
        '''
    }
}


        stage('Smoke test') {
            steps {
                powershell '''
                    Start-Sleep -Seconds 5
                    try {
                        $r = Invoke-WebRequest -Uri ("http://localhost:"+$env:APP_PORT) -UseBasicParsing -TimeoutSec 5
                        if ($r.StatusCode -eq 200) { Write-Host "OK: app responding" } else { Write-Host "Non-200"; exit 1 }
                    } catch {
                        Write-Host "App did not respond"; exit 1
                    }
                '''
            }
        }
    } // end of stages

    post {
        failure {
            echo "Build failed — check Console Output, app.log and app.err in workspace"
        }
    }
} // end of pipeline
