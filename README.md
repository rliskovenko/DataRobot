# DataRobot

# Install from local git clone
1. `cd deploy`
2. `vagrant up`
  **NB: _Will copy your ssh public key to VM_**
3. add the following to ~/.ssh/config

```
Host datarobot.vagrant
   HostName 127.0.0.1
	 Port 2222
   User datarobot
	 UserKnownHostsFile /dev/null
	 PasswordAuthentication no
	 StrictHostKeyChecking no
   IdentityFile ~/.ssh/id_rsa
```

4. `ansible-playbook -i ansible/inventories/vagrant.conf ansible/install.yml`
5. `tcping localhost 8080`
		-OR-
	 `echo "GET /" | nc -v 127.0.0.1 8080` => 404 Not Found	

