import sys

p = "rtl8812au/hal/rtl8812a/rtl8812a_phycfg.c"
s = open(p).read()
old = (
    "\tOUT s32*    \t\tpowerlevel\n"
    "\t)\n"
    "{\n"
    "#if 0\n"
    "\tHAL_DATA_TYPE\t*pHalData = GET_HAL_DATA(Adapter);\n"
    "\tPMGNT_INFO\t\tpMgntInfo = &(Adapter->MgntInfo);\n"
    "\ts4Byte\t\t\tTxPwrDbm = 13;\n"
    '\tRT_TRACE(COMP_TXAGC, DBG_LOUD, ("PHY_GetTxPowerLevel8812(): TxPowerLevel: %#x\\n", TxPwrDbm));\n'
    "\n"
    "\tif ( pMgntInfo->ClientConfigPwrInDbm != UNSPECIFIED_PWR_DBM )\n"
    "\t\t*powerlevel = pMgntInfo->ClientConfigPwrInDbm;\n"
    "\telse\n"
    "\t\t*powerlevel = TxPwrDbm;\n"
    "#endif\n"
    "}\n"
)
if old not in s:
    print("PHY_GetTxPowerLevel8812 anchor not found")
    sys.exit(1)
new = (
    "\tOUT s32*    \t\tpowerlevel\n"
    "\t)\n"
    "{\n"
    "\tPHAL_DATA_TYPE\tpHalData = GET_HAL_DATA(Adapter);\n"
    "\tBOOLEAN\t\tbIn24G = (pHalData->CurrentChannel <= 14) ? _TRUE : _FALSE;\n"
    "\tu8\t\trate = bIn24G ? MGN_1M : MGN_6M;\n"
    "\n"
    "\t// Raw TX AGC calibration index actually programmed for this channel/\n"
    "\t// rate right now (base + by-rate offset, clamped to the regulatory\n"
    "\t// limit table) - an estimate in dB, not an RF-meter-verified dBm value.\n"
    "\t*powerlevel = (s32) PHY_GetTxPowerIndex_8812A(Adapter, ODM_RF_PATH_A, rate,\n"
    "\t\tpHalData->CurrentChannelBW, pHalData->CurrentChannel);\n"
    '\tprintk(KERN_ERR "CHDBG: PHY_GetTxPowerLevel8812 ch=%d bw=%d rate=0x%x -> raw_index=%d\\n",\n'
    "\t\tpHalData->CurrentChannel, pHalData->CurrentChannelBW, rate, *powerlevel);\n"
    "}\n"
)
s = s.replace(old, new, 1)
open(p, "w").write(s)

p = "rtl8812au/os_dep/linux/ioctl_cfg80211.c"
s = open(p).read()
old = (
    "\n"
    "\t*dbm = (12);\n"
    "\t\n"
    "\treturn 0;\n"
    "}\n"
)
if old not in s:
    print("cfg80211_rtw_get_txpower anchor not found")
    sys.exit(1)
new = (
    "\n"
    "\t{\n"
    "\t\t_adapter *padapter = wiphy_to_adapter(wiphy);\n"
    "\t\ts32 powerlevel = 0;\n"
    "\t\trtw_hal_get_tx_power_level(padapter, &powerlevel);\n"
    "\t\t*dbm = (int) powerlevel;\n"
    "\t}\n"
    "\n"
    "\treturn 0;\n"
    "}\n"
)
s = s.replace(old, new, 1)
open(p, "w").write(s)
print("patched TX power reporting OK")
