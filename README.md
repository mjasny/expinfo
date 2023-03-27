
```
sudo apt install python3.7 # at least python3.7

cp expinfo/expinfo.service /etc/systemd/system
systemctl enable --now expinfo

ln -s $(pwd)/expinfo/run_exp /usr/local/bin/run_exp

echo 'export PROMPT_COMMAND='"'"'echo -ne $(</opt/expinfo/prompt) 2> /dev/null'"'" >> /etc/profile

ln -s $(pwd)/expinfo/99-expinfo /etc/update-motd.d/99-expinfo
```
