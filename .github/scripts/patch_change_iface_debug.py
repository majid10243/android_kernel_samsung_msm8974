p = "rtl8812au/os_dep/linux/ioctl_cfg80211.c"
s = open(p).read()

old = ('\tDBG_871X(FUNC_NDEV_FMT" type=%d\\n", FUNC_NDEV_ARG(ndev), type);\n'
       '\n'
       '\tif(adapter_to_dvobj(padapter)->processing_dev_remove == _TRUE)\n')
assert s.count(old) == 1, "function-entry anchor not found/unique"
new = ('\tDBG_871X(FUNC_NDEV_FMT" type=%d\\n", FUNC_NDEV_ARG(ndev), type);\n'
       '\tprintk(KERN_ERR "CHDBG: change_iface ENTRY ndev=%s requested_type=%d\\n", ndev->name, type);\n'
       '\n'
       '\tif(adapter_to_dvobj(padapter)->processing_dev_remove == _TRUE)\n')
s = s.replace(old, new, 1)

old2 = ('\t// Actually route packets through the monitor TX path when switching\n'
        '\t// THIS interface to monitor type, instead of only when a brand new\n'
        '\t// virtual interface is added as monitor (rtw_cfg80211_add_monitor_if).\n'
        '\t// Switch back to the normal station ops when leaving monitor type.\n'
        '\tif (type == NL80211_IFTYPE_MONITOR)\n'
        '\t\tndev->netdev_ops = &rtw_cfg80211_monitor_if_ops;\n'
        '\telse if (old_type == NL80211_IFTYPE_MONITOR)\n'
        '\t\tndev->netdev_ops = &rtw_netdev_ops;\n')
assert s.count(old2) == 1, "netdev_ops swap anchor not found/unique"
new2 = ('\tprintk(KERN_ERR "CHDBG: change_iface SWAP-CHECK ndev=%s old_type=%d new_type=%d\\n",\n'
        '\t\tndev->name, old_type, type);\n'
        '\t// Actually route packets through the monitor TX path when switching\n'
        '\t// THIS interface to monitor type, instead of only when a brand new\n'
        '\t// virtual interface is added as monitor (rtw_cfg80211_add_monitor_if).\n'
        '\t// Switch back to the normal station ops when leaving monitor type.\n'
        '\tif (type == NL80211_IFTYPE_MONITOR) {\n'
        '\t\tndev->netdev_ops = &rtw_cfg80211_monitor_if_ops;\n'
        '\t\tprintk(KERN_ERR "CHDBG: change_iface swapped netdev_ops -> MONITOR ops\\n");\n'
        '\t} else if (old_type == NL80211_IFTYPE_MONITOR) {\n'
        '\t\tndev->netdev_ops = &rtw_netdev_ops;\n'
        '\t\tprintk(KERN_ERR "CHDBG: change_iface swapped netdev_ops -> STATION ops\\n");\n'
        '\t}\n')
s = s.replace(old2, new2, 1)

open(p, "w").write(s)
print("patched change_iface entry + netdev_ops-swap diagnostic tracing OK")
