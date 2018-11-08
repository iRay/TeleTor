 #!/usr/bin/env bash

repository="TeleTor"

logo="
  _____    _     _____
 |_   _|__| | __|_   _|__  _ __
   | |/ _ \ |/ _ \| |/ _ \| '__|
   | |  __/ |  __/| | (_) | |
   |_|\___|_|\___||_|\___/|_|
"

show_logo() {
    $(whiptail --msgbox "${logo}" 12 40 --title "Installation" --clear 3>&1 1>&2 2>&3)
}

check_gui() {
    echo $(which whiptail dialog  2> /dev/null)
}

show_msg() {
    local title=$2
    whiptail --msgbox "${1}" 8 60 --title "${title:=Notification}" --clear
}

validate_url() {
    repo="https://github.com/iRay/${repository}/archive/master.zip"
    if [[ `wget -S --spider ${repo}  2>&1 | grep 'HTTP/1.1 200 OK'` ]]
    then
        echo 0
    else
        echo 1
    fi
}

install() {
if [[ $(check_gui) ]]
        then
            if [[ -f $(pwd)/master.zip ]]
            then
                $(rm $(pwd)/master.zip)
            fi
            show_logo
            user_name=$(whiptail --inputbox "transmission-remote username:" 8 78 --title "TeleTor Bot" --clear 3>&1 1>&2 2>&3)
            status=$?
            if [[ ${status} != 0 ]]; then exit 1
            fi
            user_pass=$(whiptail --passwordbox "transmission-remote password:" 8 78 --title "TeleTor Bot" --clear 3>&1 1>&2 2>&3)
            status=$?
            if [[ ${status} != 0 ]]; then exit 1
            fi
        fi

        is_valid=$(validate_url)

        if [[ "${is_valid}" -eq 0 ]]
        then
            progress 0.2 "Downloading..."
            $(wget -q -O master.zip "https://github.com/iRay/${repository}/archive/master.zip")
            local unnarch=$(unzip master.zip -d $(pwd))
            progress 0.1 "Unpacking..."
        else
            $(whiptail --title  "Error" --msgbox "TeleTor is not available" 07 40 --clear 3>&1 1>&2 2>&3)
            exit 1
        fi

        $(find $(pwd)/${repository}-master/scripts/ -type f -exec sed -i -e "s/username:password/${user_name}:${user_pass}/g" {} \;)
        $(find $(pwd)/${repository}-master/config/ -name config.yaml -exec sed -i '' "s/t_username: ''/t_username: '${user_name}'/g" {} \;)
        $(find $(pwd)/${repository}-master/config/ -name config.yaml -exec sed -i '' "s/t_username: ''/t_password: '${user_pass}'/g" {} \;)

        (chmod +x $(pwd)/${repository}-master/start_bot $(pwd)/${repository}-master/stop_bot)
        (chmod +x $(pwd)/${repository}-master/scripts/*)
        (chmod 777 $(pwd)/${repository}-master/files/)

        show_msg "start/stop scripts have been prepared" "TeleTor"
        access_token=$(whiptail --inputbox "Telegram Bot access token:" 8 78 --title "TeleTor Bot" --clear 3>&1 1>&2 2>&3)
        $(sed -i "s/token: ''/token: '${access_token}'/g" $(pwd)/${repository}-master/config/config.yaml)

        progress 0.3 "Installing dependencies..."
        (cd $(pwd)/${repository}-master && python3.7 -m venv $(pwd)/venv && . $(pwd)/venv/bin/activate && pip install -r requirements.txt)

        show_msg "Installation completed" "TeleTor"
}

progress() {
    {
         for ((i = 0 ; i <= 100 ; i+=20));  do
             sleep $1
             echo $i
         done
    } | whiptail --gauge "$2" 6 60 0
}

install