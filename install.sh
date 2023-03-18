#!/usr/bin/env bash

echo "Installing laGGer prerequisites"
echo "-------------------------------"
echo ""

sudo apt -y install python3-pip screen libmicrohttpd-dev libjansson-dev \
	libssl-dev libsrtp2-dev libsofia-sip-ua-dev libglib2.0-dev \
	libopus-dev libogg-dev libcurl4-openssl-dev liblua5.3-dev \
	libconfig-dev pkg-config libtool automake meson ninja-build \
	libcurl4-openssl-dev libusrsctp-dev libusrsctp1 cmake \
	libnanomsg-dev doxygen graphviz boxes openssl curl wget \
	novnc ufw prosody ca-certificates curl gnupg lsb-release \
	build-essential libssl-dev zlib1g-dev libncurses5-dev \
	libncursesw5-dev libreadline-dev libsqlite3-dev libgdbm-dev \
	libdb5.3-dev libbz2-dev libexpat1-dev liblzma-dev tk-dev \
	libffi-dev ffmpeg libswresample-dev libavutil-dev \
	libavformat-dev libswscale-dev libavdevice-dev libvpx-dev \
	certbot ufw nxagent xinit xauth xclip x11-xserver-utils \
	x11-utils catatonit jq weston xwayland xdotool xpra xdg-utils \
	pulseaudio xfishtank x11vnc


echo "Configuring Prosody" | boxes
if [ ! -f prosody.cfg.lua ]; then
    echo "Downloading and installing config file ..." 

    wget -O prosody.cfg.lua https://pastebin.com/raw/j1CLcSLH
    sudo cp prosody.cfg.lua /etc/prosody/prosody.cfg.lua

    sudo systemctl restart prosody
else
    echo "Config file exists, skipping."
fi

echo "Configuring noVNC" | boxes

if [ ! -d noVNC ]; then
    echo "Cloning noVNC repository."
    git clone https://github.com/novnc/noVNC.git
    cd noVNC
    git checkout cbf090fe701adc7776270be6725f886e185d2b85
    cd ..
else
    echo "noVNC cloned, skipping."
fi
    
USERHOME=$(readlink -f ~/)
INSTALLDIR=$(readlink -f .)


if [ ! -d "$USERHOME/bin" ]; then
    mkdir $USERHOME/bin
fi

if echo "$PATH" | grep -q "$USERHOME/bin"; then
    echo "~/bin already on PATH, skipping."
else
    echo 'export PATH=$PATH:'"$USERHOME/bin" | tee -a ~/.bashrc
    source ~/.bashrc
fi


if [ ! -f ~/bin/novnc ]; then
    echo "Linking noVNC launcher." 
    chmod +x $INSTALLDIR/noVNC/utils/launch.sh
    ln -s $INSTALLDIR/noVNC/utils/launch.sh ~/bin/novnc
else
    echo "noVNC configured, skipping."
fi


    

echo "Installing Docker" | boxes

if dpkg -s "docker-ce" >/dev/null 2>&1; then
    echo "Docker already installed, skipping."
else
    sudo mkdir -m 0755 -p /etc/apt/keyrings

    curl -fsSL https://download.docker.com/linux/debian/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg


    echo \
	"deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian \
  	$(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

    sudo chmod a+r /etc/apt/keyrings/docker.gpg

    sudo apt update

    sudo apt -y install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
    sudo usermod -a -G docker $USER

fi



echo "Installing Python 3.6.9" | boxes

if [ ! -d "Python-3.6.9" ]; then
    wget https://www.python.org/ftp/python/3.6.9/Python-3.6.9.tgz
    tar -xf Python-3.6.9.tgz
    cd Python-3.6.9
    ./configure --enable-optimizations
    make -j $(nproc)
    sudo make altinstall
    cd ..
else
    echo "Python-3.6.9. folder exists, skipping."
fi

echo "Creating SSL keys" | boxes

if [ ! -f /etc/ssl/mycerts/server.key ]; then
    echo "Generating SSL keys ..." | boxes

    sudo apt install openssl

    sudo mkdir /etc/ssl/mycerts

    sudo openssl genrsa -out /etc/ssl/mycerts/server.key 2048

    sudo openssl req -new -key /etc/ssl/mycerts/server.key -out /etc/ssl/mycerts/server.csr

    sudo openssl x509 -req -days 365 -in /etc/ssl/mycerts/server.csr -signkey /etc/ssl/mycerts/server.key -out /etc/ssl/mycerts/server.crt

    sudo chown $USER /etc/ssl/mycerts/server.*

    echo "SSL keys generated and installed!" 
else
    echo "SSL keys already installed, skipping key generation!" 
fi



echo "Installing Python dependencies" | boxes

sudo pip3.6 install --upgrade pip

sudo pip3.6 install jinja2==3.0.3 aiohttp-jinja2==1.2.0 spade==3.1.4 pytz flask==2.0.3 aiortc requests

echo "Installing Janus dependencies" | boxes

if [ ! -d libnice ]; then
    git clone https://gitlab.freedesktop.org/libnice/libnice
    cd libnice
    sudo meson --prefix=/usr build && ninja -C build && sudo ninja -C build install
    cd ..
else
    echo "libnice folder exists, skipping."
fi


if [ ! -d libwebsockets ]; then
    git clone https://libwebsockets.org/repo/libwebsockets
    cd libwebsockets
    # If you want the stable version of libwebsockets, uncomment the next line
    # git checkout v4.3-stable
    mkdir build
    cd build
    # See https://github.com/meetecho/janus-gateway/issues/732 re: LWS_MAX_SMP
    # See https://github.com/meetecho/janus-gateway/issues/2476 re: LWS_WITHOUT_EXTENSIONS
    cmake -DLWS_MAX_SMP=1 -DLWS_WITHOUT_EXTENSIONS=0 -DCMAKE_INSTALL_PREFIX:PATH=/usr -DCMAKE_C_FLAGS="-fpic" ..
    make && sudo make install
    cd ../..
else
    echo "libwesockets folder exists, skipping."
fi

if [ ! -d "paho.mqtt.c" ]; then
    git clone https://github.com/eclipse/paho.mqtt.c.git
    cd paho.mqtt.c
    make && sudo prefix=/usr make install
    cd ..
else
    echo "paho.mqtt.c folder exists, skipping."
fi


if [ ! -d "rabbitmq-c" ]; then
    git clone https://github.com/alanxz/rabbitmq-c
    cd rabbitmq-c
    git submodule init
    git submodule update
    mkdir build && cd build
    cmake -DCMAKE_INSTALL_PREFIX=/usr ..
    make && sudo make install
    cd ../..
else
    echo "rabbitmq-c folder exists, skipping."
fi
    

echo "Installing Janus" | boxes 

if [ ! -d "janus-gateway" ]; then
    git clone https://github.com/meetecho/janus-gateway.git
    cd janus-gateway
    sh autogen.sh
    ./configure --prefix=/opt/janus --enable-docs
    make
    sudo make install
    make configs
    cd ..
    # Installing configuration file. If you use different
    # certificates than the ones generated above you will
    # need to edit this file to point to valid certificates
    sudo cp janus.transport.http.jcfg /opt/janus/etc/janus
else
    echo "janus-gateway folder exists, skipping."
fi


echo "Installing x11docker" | boxes


if ! type x11docker > /dev/null; then
    curl -fsSL https://raw.githubusercontent.com/mviereck/x11docker/e9a10da0ea9be043e32cd41f483e42a40be27498/x11docker
    chmod +x x11docker
    sudo ./x11docker --install
    sudo cp x11docker /usr/local/bin
else
    echo "x11docker already installed, skipping."
fi

echo "Building game images" | boxes


cartridges_dir="catridges"

for dir in "$cartridges_dir"/*; do
    if [ -d "$dir" ]; then
        subfolder_name=$(basename "$dir")
        image_tag="lagger/$subfolder_name"
        
        # Check if the Docker image with the tag exists
        if ! docker image inspect "$image_tag" > /dev/null 2>&1; then
            echo "Building Docker image of game: $image_tag"
            docker build -t "$image_tag" "$dir"
        else
            echo "Docker image for game $image_tag already exists, skipping."
        fi
    fi
done


echo "Opening ports" | boxes

# laGGer ports
sudo ufw allow 49996:60000/tcp
sudo ufw allow 49996:60000/udp
# Janus ports
sudo ufw allow 8088:8089/tcp
sudo ufw allow 8088:8089/udp
sudo ufw allow 8188
# Prosody ports
sudo ufw allow 5222:5223/tcp
sudo ufw allow 5222:5223/udp
sudo ufw allow 5269
sudo ufw allow 5443
sudo ufw allow 5280
sudo ufw allow 3478
sudo ufw allow 1883
sudo ufw disable
sudo ufw enable

echo "Done!" | boxes
