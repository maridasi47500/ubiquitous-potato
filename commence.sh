hey="python3 -m venv ~/path/to/venv"
wow="source ~/path/to/venv/bin/activate"
yesA="python3 -m http.server 8000"
#2
yesB="python3 app.py"
#3
yesC="python3 lumiere_ws_server.py"
#gnome-terminal -x bash -c -- "$hey; $wow;$yesA"
#gnome-terminal -x bash -c -- "$hey; $wow;cd ~/busville;$yesB"
#gnome-terminal -x bash -c -- "$hey; $wow;cd ~/busville;$yesC"
gnome-terminal --tab --title="tab 1" --command="bash -c 'cd ~/busville;$hey; $wow;cd ~/busville;ls;$yesA;'" --tab --title="tab 2" --command="bash -c '$hey; $wow;cd ~/busville;ls;$yesB'" --tab --title="tab 3" --command="bash -c '$hey; $wow;ls;cd ~/busville;$yesC;'"

