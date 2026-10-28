import re

# --- File 1: os_dep/linux/wifi_regd.c ---
p1 = "rtl8812au/os_dep/linux/wifi_regd.c"
s1 = open(p1).read()

# Helper to dump max_power of a representative 5GHz channel (36, 5180MHz)
# and a representative 2.4GHz channel (1, 2412MHz), right after a point of
# interest, so we can see in dmesg exactly what cfg80211 currently has
# programmed for this wiphy at that moment.
dump_helper = '''
static void CHDBG_dump_power(struct wiphy *wiphy, const char *tag)
{
	struct ieee80211_channel *ch;
	int i;

	if (wiphy->bands[IEEE80211_BAND_5GHZ]) {
		struct ieee80211_supported_band *sband = wiphy->bands[IEEE80211_BAND_5GHZ];
		for (i = 0; i < sband->n_channels; i++) {
			ch = &sband->channels[i];
			if (ch->center_freq == 5180 || ch->center_freq == 5260) {
				printk(KERN_ERR "CHDBG-REGD[%s]: 5GHz freq=%d flags=0x%x max_power=%d max_reg_power=%d\\n",
					tag, ch->center_freq, ch->flags, ch->max_power, ch->max_reg_power);
			}
		}
	}
	if (wiphy->bands[IEEE80211_BAND_2GHZ]) {
		struct ieee80211_supported_band *sband = wiphy->bands[IEEE80211_BAND_2GHZ];
		for (i = 0; i < sband->n_channels; i++) {
			ch = &sband->channels[i];
			if (ch->center_freq == 2412) {
				printk(KERN_ERR "CHDBG-REGD[%s]: 2.4GHz freq=%d flags=0x%x max_power=%d max_reg_power=%d\\n",
					tag, ch->center_freq, ch->flags, ch->max_power, ch->max_reg_power);
			}
		}
	}
}
'''

anchor1 = 'static void _rtw_regd_init_wiphy(struct rtw_regulatory *reg, struct wiphy *wiphy)\n{'
assert s1.count(anchor1) == 1, "anchor1 not found/unique"
s1 = s1.replace(anchor1, dump_helper + '\n' + anchor1, 1)

old2 = (
	'\tregd = _rtw_regdomain_select(reg);\n'
	'\twiphy_apply_custom_regulatory(wiphy, regd);\n'
	'\n'
	'\t/* Hard code flags */\n'
	'\t_rtw_reg_apply_flags(wiphy);\n'
	'\t_rtw_reg_apply_radar_flags(wiphy);\n'
	'\t_rtw_reg_apply_world_flags(wiphy, NL80211_REGDOM_SET_BY_DRIVER, reg);\n'
	'}\n'
)
assert s1.count(old2) == 1, "init_wiphy tail anchor not found/unique"
new2 = (
	'\tregd = _rtw_regdomain_select(reg);\n'
	'\tprintk(KERN_ERR "CHDBG-REGD: calling wiphy_apply_custom_regulatory, regd->alpha2=%c%c n_reg_rules=%d\\n",\n'
	'\t\tregd->alpha2[0], regd->alpha2[1], regd->n_reg_rules);\n'
	'\twiphy_apply_custom_regulatory(wiphy, regd);\n'
	'\tCHDBG_dump_power(wiphy, "after-custom-reg");\n'
	'\n'
	'\t/* Hard code flags */\n'
	'\t_rtw_reg_apply_flags(wiphy);\n'
	'\t_rtw_reg_apply_radar_flags(wiphy);\n'
	'\t_rtw_reg_apply_world_flags(wiphy, NL80211_REGDOM_SET_BY_DRIVER, reg);\n'
	'\tCHDBG_dump_power(wiphy, "end-of-regd-init-wiphy");\n'
	'}\n'
)
s1 = s1.replace(old2, new2, 1)

old3 = (
	'void _rtw_reg_notifier(struct wiphy *wiphy, struct regulatory_request *request)\n'
	'{\n'
	'\tstruct rtw_regulatory *reg = NULL;\n'
	'\n'
	'\tDBG_8192C("%s\\n", __func__);\n'
	'\n'
	'\t_rtw_reg_notifier_apply(wiphy, request, reg);\n'
	'}\n'
)
assert s1.count(old3) == 1, "notifier anchor not found/unique"
new3 = (
	'void _rtw_reg_notifier(struct wiphy *wiphy, struct regulatory_request *request)\n'
	'{\n'
	'\tstruct rtw_regulatory *reg = NULL;\n'
	'\n'
	'\tDBG_8192C("%s\\n", __func__);\n'
	'\tprintk(KERN_ERR "CHDBG-REGD: _rtw_reg_notifier ENTRY initiator=%d alpha2=%c%c\\n",\n'
	'\t\trequest->initiator, request->alpha2[0], request->alpha2[1]);\n'
	'\tCHDBG_dump_power(wiphy, "notifier-before-apply");\n'
	'\n'
	'\t_rtw_reg_notifier_apply(wiphy, request, reg);\n'
	'\tCHDBG_dump_power(wiphy, "notifier-after-apply");\n'
	'}\n'
)
s1 = s1.replace(old3, new3, 1)

open(p1, "w").write(s1)
print("patched wifi_regd.c OK")

# --- File 2: hal/rtl8812a/rtl8812a_hal_init.c (Hal_ReadChannelPlan8812A) ---
p2 = "rtl8812au/hal/rtl8812a/rtl8812a_hal_init.c"
s2 = open(p2).read()

old4 = (
	'\tpadapter->mlmepriv.ChannelPlan = hal_com_config_channel_plan(\n'
	'\t\tpadapter\n'
	'\t\t, hwinfo?hwinfo[EEPROM_ChannelPlan_8812]:0xFF\n'
	'\t\t, padapter->registrypriv.channel_plan\n'
	'\t\t, RT_CHANNEL_DOMAIN_REALTEK_DEFINE\n'
	'\t\t, AutoLoadFail\n'
	'\t);\n'
	'\n'
	'\tDBG_871X("mlmepriv.ChannelPlan = 0x%02x\\n", padapter->mlmepriv.ChannelPlan);\n'
)
assert s2.count(old4) == 1, "Hal_ReadChannelPlan8812A anchor not found/unique"
new4 = (
	'\tprintk(KERN_ERR "CHDBG-REGD: Hal_ReadChannelPlan8812A hw_channel_plan=0x%02x(hwinfo_null=%d) sw_channel_plan=0x%02x AutoLoadFail=%d\\n",\n'
	'\t\thwinfo?hwinfo[EEPROM_ChannelPlan_8812]:0xFF, hwinfo==NULL,\n'
	'\t\tpadapter->registrypriv.channel_plan, AutoLoadFail);\n'
	'\n'
	'\tpadapter->mlmepriv.ChannelPlan = hal_com_config_channel_plan(\n'
	'\t\tpadapter\n'
	'\t\t, hwinfo?hwinfo[EEPROM_ChannelPlan_8812]:0xFF\n'
	'\t\t, padapter->registrypriv.channel_plan\n'
	'\t\t, RT_CHANNEL_DOMAIN_REALTEK_DEFINE\n'
	'\t\t, AutoLoadFail\n'
	'\t);\n'
	'\n'
	'\tDBG_871X("mlmepriv.ChannelPlan = 0x%02x\\n", padapter->mlmepriv.ChannelPlan);\n'
	'\tprintk(KERN_ERR "CHDBG-REGD: final ChannelPlan=0x%02x\\n", padapter->mlmepriv.ChannelPlan);\n'
)
s2 = s2.replace(old4, new4, 1)

open(p2, "w").write(s2)
print("patched rtl8812a_hal_init.c OK")
