p = "rtl8812au/os_dep/linux/ioctl_cfg80211.c"
s = open(p).read()

old = ('\tprintk(KERN_ERR "CHDBG: change_iface SWAP-CHECK ndev=%s old_type=%d new_type=%d\\n",\n'
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
assert s.count(old) == 1, "swap-check block anchor not found/unique"
new = ('\tprintk(KERN_ERR "CHDBG: change_iface SWAP-CHECK ndev=%s old_type=%d new_type=%d\\n",\n'
       '\t\tndev->name, old_type, type);\n'
       '\t// Actually route packets through the monitor TX path when switching\n'
       '\t// THIS interface to monitor type, instead of only when a brand new\n'
       '\t// virtual interface is added as monitor (rtw_cfg80211_add_monitor_if).\n'
       '\t// Switch back to the normal station ops when leaving monitor type.\n'
       '\tif (type == NL80211_IFTYPE_MONITOR) {\n'
       '\t\tndev->netdev_ops = &rtw_cfg80211_monitor_if_ops;\n'
       '\t\tprintk(KERN_ERR "CHDBG: change_iface swapped netdev_ops -> MONITOR ops\\n");\n'
       '\t\t// ROOT CAUSE FIX: wlan1 is the long-lived station interface. At\n'
       '\t\t// some earlier point (disconnect/close) the driver called\n'
       '\t\t// netif_carrier_off() on it, and nothing in the monitor-mode\n'
       '\t\t// switch path ever calls netif_carrier_on() again. dev_activate()\n'
       '\t\t// (net/sched/sch_generic.c) only promotes the qdisc from the\n'
       '\t\t// built-in noop_qdisc to the real pfifo_fast queue when\n'
       '\t\t// netif_carrier_ok() is true - otherwise it bails out early and\n'
       '\t\t// noop_qdisc (which just kfree_skb()s everything) stays attached\n'
       '\t\t// forever, silently dropping every TX packet before it ever\n'
       '\t\t// reaches this driver. A freshly allocated device (like the old\n'
       '\t\t// separate "mon1" workaround) starts with carrier OK by default,\n'
       '\t\t// which is why that workaround never hit this. Force carrier on\n'
       '\t\t// here, before "ip link set wlan1 up" runs and calls\n'
       '\t\t// dev_activate(), so the real qdisc gets attached properly.\n'
       '\t\tnetif_carrier_on(ndev);\n'
       '\t\tprintk(KERN_ERR "CHDBG: change_iface forced netif_carrier_on for monitor mode\\n");\n'
       '\t} else if (old_type == NL80211_IFTYPE_MONITOR) {\n'
       '\t\tndev->netdev_ops = &rtw_netdev_ops;\n'
       '\t\tprintk(KERN_ERR "CHDBG: change_iface swapped netdev_ops -> STATION ops\\n");\n'
       '\t}\n')
s = s.replace(old, new, 1)

open(p, "w").write(s)
print("patched netif_carrier_on fix for monitor mode OK")
