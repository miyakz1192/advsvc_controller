set -x

cd /etc/systemd/system 
sudo rm audio2text.service
sudo rm text2advice.service
sudo ln -s ~/advsvc_controller/etc/audio2text.service audio2text.service
sudo ln -s ~/advsvc_controller/etc/text2advice.service text2advice.service

sudo systemctl enable audio2text.service
sudo systemctl enable text2advice.service
