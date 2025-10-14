# systemd 서비스 수정 방법

## 1. 서비스 파일 편집

```bash
sudo nano /etc/systemd/system/ricerica.service
```

## 2. Environment 추가

다음과 같이 수정:

```ini
[Unit]
Description=RICERICA (ERICA-BAB, API BACKEND)
After=network.target

[Service]
Type=exec
User=your-user
Group=your-group
WorkingDirectory=/path/to/meal_api
Environment=MASTER_PROCESS=true
ExecStart=/path/to/venv/bin/uvicorn app.main:app --workers 4 --host 0.0.0.0 --port 5401
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

## 3. 서비스 재시작

```bash
sudo systemctl daemon-reload
sudo systemctl restart ricerica
```

## 4. 로그 확인

```bash
sudo journalctl -u ricerica -f
```

예상 로그:
```
스케줄러 시작 완료 (마스터 프로세스 - PID: XXXXX)
스케줄러 시작 건너뜀 (워커 프로세스 - PID: XXXXX)
스케줄러 시작 건너뜀 (워커 프로세스 - PID: XXXXX)
스케줄러 시작 건너뜀 (워커 프로세스 - PID: XXXXX)
```
