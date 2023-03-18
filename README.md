laGGer - lags but Good Game
---------------------------

laGGer is an open-source game streaming system implemented at the Artificial Intelligence Laboratory of the Faculty of Organization and Informatics, University of Zagreb, Croatia. It is a proof-of-concept system, not developed enough for a production environment.

laGGer allows for streaming Linux games from a X11Docker environment to a web application based on noVNC. It has a video/audio streaming functionality that allows real time sharing of gameplay, camera and microphone input.

Installation
------------

To install it quite a number of packages have to be installed and cofigured. It assumes a Debian Bullseye server machine. An installation script is provided:


```
cd laGGer
./install.sh
```

The installation script assumes that you will use self-signed SSL certificates. In case you want to use your own, edit the script.

In case you want to test and try it out, here you can find an installed `VirtualBox disk image <https://www.dropbox.com/sh/eu619xsmlpmyx5e/AAD3mqXy_BdZqRkS6v9P9ApAa?dl=1>`_.



Configuration
-------------

For laGGer to run properly you have to edit the /config/organization.json file. The default values have been provided which should run fine. In case you want to use different certificates change the "cert" and "key" values in the config file. Also, in case you change the ports, make sure to allow them using ufw.

If you are using laGGer from VirtualBox using the image above, make sure to setup port forwarding. The following two scripts can automate that.

Opening ports:

```
#!/usr/bin/env bash

VBoxManage modifyvm "laGGer" --natpf1 "janus1,tcp,,8088,,8088";
VBoxManage modifyvm "laGGer" --natpf1 "janus1,tcp,,8089,,8089";
VBoxManage modifyvm "laGGer" --natpf1 "janus1,tcp,,8188,,8188";

for i in {49997..50100}; do
    echo "Opening port $i"
    VBoxManage modifyvm "laGGer" --natpf1 "tcp-port$i,tcp,,$i,,$i";
    VBoxManage modifyvm "laGGer" --natpf1 "udp-port$i,udp,,$i,,$i";
done

echo "Done!"
```

Or on Windoze:

```
@echo off
setlocal enabledelayedexpansion

VBoxManage modifyvm "laGGer" --natpf1 "janus1,tcp,,8088,,8088"
VBoxManage modifyvm "laGGer" --natpf1 "janus1,tcp,,8089,,8089"
VBoxManage modifyvm "laGGer" --natpf1 "janus1,tcp,,8188,,8188"

for /L %%i in (49997,1,50100) do (
    echo Opening port %%i
    VBoxManage modifyvm "laGGer" --natpf1 "tcp-port%%i,tcp,,%%i,,%%i"
    VBoxManage modifyvm "laGGer" --natpf1 "udp-port%%i,udp,,%%i,,%%i"
)

echo Done!
```

Running
-------

To run laGGer first run:

```
sudo ./start_root_first.sh
```

And then as a normal user:

```
./start.sh
```

If everything work and no errors happen, you should be able to open the interface at:

```
http://dragon.foi.hr:49998/list_catridges?player_id=player2
```


http://dragon.foi.hr:49998/list_catridges?player_id=ivek


Self signed certificates
------------------------

If you are using the built-in self signed certificates, you need to instruct your browser to trust all ports from your local domain. While there is no built-in option in Firefox or Chrome to accept self-signed certificates for all ports on a single IP address or domain, you can work around this by importing the self-signed certificate into your browser's trusted certificate store. By doing this, the browser will trust the certificate regardless of which port it is used on.

Here's how to import a self-signed certificate in Firefox and Chrome:

#Firefox:

  1.  Open Firefox and click on the menu button (three horizontal lines) in the top-right corner.
  2.  Click on "Options" or "Preferences" (depending on your Firefox version).
  3.  Scroll down to the "Privacy & Security" section.
  4.  In the "Certificates" section, click on "View Certificates."
  5.  In the "Certificate Manager" window, go to the "Authorities" tab.
  6.  Click on "Import" and navigate to the location where your self-signed certificate file is stored (usually in .crt, .cer, or .pem format). Select the certificate and click "Open."
  7.  Check the "Trust this CA to identify websites" box and click "OK."
  8.  Close the "Certificate Manager" window and restart Firefox.

Now, Firefox should trust your self-signed certificate for any port on the specified IP address or domain.

#Chrome:

  1.  Open Chrome and click on the menu button (three vertical dots) in the top-right corner.
  2.  Click on "Settings."
  3.  Scroll down and click on "Privacy and security."
  4.  Click on "Security."
  5.  Scroll down to the "Advanced" section and click on "Manage certificates."
  6.  In the "Certificate Manager" window, go to the "Authorities" tab.
  7.  Click on "Import" and navigate to the location where your self-signed certificate file is stored (usually in .crt, .cer, or .pem format). Select the certificate and click "Open."
  8.  Check the "Trust this certificate for identifying websites" box and click "OK."
  9.  Close the "Certificate Manager" window and restart Chrome.

Now, Chrome should trust your self-signed certificate for any port on the specified IP address or domain.
