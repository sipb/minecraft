

redir: http-redir.service https-redir.service
	sudo cp http-redir.service /etc/systemd/system/http-redir.service
	sudo cp https-redir.service /etc/systemd/system/https-redir.service
	sudo systemctl daemon-reload
	sudo systemctl enable http-redir
	sudo systemctl start http-redir
	sudo systemctl enable https-redir
	sudo systemctl start https-redir
