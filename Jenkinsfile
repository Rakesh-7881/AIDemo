pipeline {
  agent any

  environment {
    APP_PORT = "5000"
    // Must create this credential in Jenkins (Secret text)
    OPENAI_API_KEY = credentials('OPENAI_API_KEY')
  }

stage('Checkout') {
    steps {
        checkout([
            $class: 'GitSCM',
            branches: [[name: '*/main']],
            userRemoteConfigs: [[
                url: 'https://github.com/Rakesh-7881/AIDemo.git'
            ]],
            gitTool: 'Default' // match the Git installation name in Jenkins Global Tool Config
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
    $port = $env:APP_PORT
    if (-not $env:OPENAI_API_KEY) { Write-Host "OPENAI_API_KEY missing"; exit 1 }

    Start-Process -FilePath ".\\venv\\Scripts\\python.exe" `
                  -ArgumentList "app.py","--port",$port `
                  -WorkingDirectory "$env:WORKSPACE" `
                  -RedirectStandardOutput "$env:WORKSPACE\\app.log" `
                  -RedirectStandardError "$env:WORKSPACE\\app.err" `
                  -NoNewWindow -WindowStyle Hidden
    Write-Host "App started (detached)"
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

  }

  post {
    failure {
      echo "Build failed — check Console Output, app.log and app.err in workspace"
    }
  }
}
