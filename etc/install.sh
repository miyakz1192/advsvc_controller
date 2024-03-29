set -x

cd /etc/systemd/system 
sudo rm audio2text.service
sudo rm text2advice.service
sudo rm advice-finished.service
sudo rm summary-finished.service
sudo rm rest-api.service
sudo ln -s ~/advsvc_controller/etc/audio2text.service audio2text.service
sudo ln -s ~/advsvc_controller/etc/text2advice.service text2advice.service
sudo ln -s ~/advsvc_controller/etc/advice-finished.service advice-finished.service
sudo ln -s ~/advsvc_controller/etc/summary-finished.service summary-finished.service
sudo ln -s ~/advsvc_controller/etc/rest-api.service rest-api.service

sudo systemctl enable audio2text.service
sudo systemctl enable text2advice.service
sudo systemctl enable advice-finished.service
sudo systemctl enable summary-finished.service
sudo systemctl enable rest-api.service
