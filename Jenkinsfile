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
        $port = 5000
        $processes = Get-NetTCPConnection -LocalPort $port | ForEach-Object { Get-Process -Id $_.OwningProcess }
        if ($processes) { $processes | Stop-Process -Force }
        Write-Output "Stopped old processes on port $port (if any)"
        '''
    }
}


stage('Start app (detached)') {
    steps {
        powershell '''
        Start-Process -NoNewWindow -FilePath "venv\\Scripts\\python.exe" -ArgumentList "app.py"
        Start-Sleep -Seconds 5
        Write-Output "App started successfully."
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
