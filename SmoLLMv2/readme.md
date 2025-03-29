
## the run file

```
#!/bin/bash

cd /media/tish/Diffusions/Gradio/SmoLLMv2
source venv/bin/activate
python ./smollm.py
```

## the service

```
[Unit]
Description=SmoLLM v2
After=network.target

[Service]
User=tish
Group=tish

ExecStart=/media/tish/Diffusions/Gradio/SmoLLMv2/start.sh

Restart=Always
RestartSec=10

StandardOutput=journal
StandardError=journal

KillSignal=SIGTERM

[Install]
WantedBy=default.target
```

## the commands

```
python -m venv venv
source venv/bin/activate
pip install gradio
deactivate
sudo nano /etc/systemd/system/smollm.service
sudo systemctl daeomon-reload
sudo systemctl start smollm.service
sudo systemctl restart smollm.service
sudo systemctl edit smollm.service
```
