pipeline {
  agent any
  environment {
    APP_PORT = "5000"
    // Must create this credential in Jenkins (Secret text)
    OPENAI_API_KEY = credentials('OPENAI_API_KEY')
  }
  stages {
    stage('Checkout') {
      steps { checkout scm }
    }

    stage('Setup Python venv & deps') {
      steps {
        powershell '''
          if (-Not (Test-Path venv)) {
            python -m venv venv
          }
          .\\venv\\Scripts\\python.exe -m pip install --upgrade pip
          .\\venv\\Scripts\\python.exe -m pip install -r requirements.txt
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
    '''
  }
}


    stage('Start app (detached)') {
      steps {
        powershell '''
          $port = $env:APP_PORT
          if (-not $env:OPENAI_API_KEY) { Write-Host "OPENAI_API_KEY missing"; exit 1 }
          # Start detached process in workspace so logs and files stay in Jenkins workspace
          Start-Process -FilePath ".\\venv\\Scripts\\python.exe" `
                        -ArgumentList "app.py","--port",$port `
                        -WorkingDirectory $env:WORKSPACE `
                        -RedirectStandardOutput "$env:WORKSPACE\\app.log" `
                        -RedirectStandardError "$env:WORKSPACE\\app.err" `
                        -NoNewWindow -WindowStyle Hidden
        '''
      }
    }

    stage('Smoke test') {
      steps {
        powershell '''
          Start-Sleep -Seconds 2
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
  
stage('Setup Python') {
    steps {
        bat '''
          python -m pip install --upgrade pip setuptools wheel
          pip install --upgrade build
          pip install -r requirements.txt --verbose
        '''
    }
}


  post {
    failure {
      echo "Build failed — check Console Output, app.log and app.err in workspace"
    }
  }
}
