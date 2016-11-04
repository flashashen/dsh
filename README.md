*dsh*

---

TODO

- search for .cmd.yml on demand (since this could take a while) and update config with new projects 
- add a docker command. One action should be to update resolve.conf on docker-machine with vpn / non-vpn settings. Could use ansible. Auto-detect vpn status
- fix cmd_prj.py so that the prj 'context' isn't necessary for auto-complete and to issue commands. ex. 'prj perks tail' should work from root prompt.
- worker thread management. start, stop, status. use multiprocessing module