# Bluetooth ELM327 Setup Guide

## Why Do I See Two COM Ports?

When you pair a Bluetooth ELM327 adapter with Windows, it creates TWO virtual serial ports:

- **COM3** - Outgoing connection (use this one)
- **COM4** - Incoming connection (ignore this one)

**You only need the outgoing port** (usually the lower number).

## How to Find the Correct Port

### Method 1: Windows Device Manager

1. Open **Device Manager** (Win+X, then M)
2. Expand **Ports (COM & LPT)**
3. Look for your ELM327 device - it will show two ports:
   ```
   Standard Serial over Bluetooth link (COM3)    ← Use this (outgoing)
   Standard Serial over Bluetooth link (COM4)    ← Ignore (incoming)
   ```
4. The first one listed is usually the outgoing port

### Method 2: Bluetooth Settings

1. Open **Settings → Bluetooth & devices**
2. Click on your paired ELM327 device
3. Scroll down to **COM Ports**
4. Look for:
   - **Outgoing**: COM3 ← **Use this one**
   - **Incoming**: COM4 ← Ignore

### Method 3: Trial and Error

If unsure, try both in DeepDiag:
- Connect to COM3 first (usually works)
- If no response, disconnect and try COM4
- The correct port will respond to AT commands

## Correct Baudrate

ELM327 adapters commonly use:
- **38400** (most common default)
- **9600** (older adapters)
- **115200** (some newer adapters)

You found **115200** works for your adapter - that's good! DeepDiag will remember this setting.

## Connection Issues

### "Port already in use"
- Another program is using the port
- Close any other OBD software
- Restart Windows if necessary

### "No response from adapter"
- Wrong COM port (try the other one)
- Wrong baudrate (try 38400, 9600, 115200)
- Adapter not powered (plug into OBD-II port)
- Bluetooth connection dropped

### "Permission denied"
- Run DeepDiag as Administrator
- Check port isn't locked by another app

## Best Practices

1. **Pair once**: Pair the Bluetooth adapter in Windows settings first
2. **Use lower port**: Usually COM3 is the outgoing port (correct one)
3. **Note your baudrate**: Your adapter uses 115200 - remember this
4. **Keep it simple**: Don't try to connect to both ports simultaneously
5. **Close other tools**: Only one program can use the COM port at a time

## Testing Your Connection

### Quick Test in Debug Console
```
ATZ          → Should return "ELM327 vX.X"
ATI          → Should return adapter version
ATRV         → Should return voltage (if connected to vehicle)
0100         → Should return data (if vehicle ignition is ON)
```

### Using AI Diagnostic
1. Connect to your ELM327 (COM3 @ 115200)
2. Tools → AI Diagnostic Assistant
3. Select "Auto-diagnose connection issues"
4. Let the AI test everything automatically

## Common ELM327 Bluetooth Adapters

| Adapter Type | Default Baudrate | Notes |
|-------------|------------------|-------|
| Generic v1.5 | 38400 | Most common |
| Generic v2.1 | 38400 | Newer firmware |
| VGATE iCar | 38400 | Popular brand |
| OBDLink | 115200 | Professional grade |
| Veepeak | 38400 | Common on Amazon |
| Your adapter | 115200 | Confirmed working |

## Troubleshooting Chart

```
Start
  |
  ├─ Can you see COM ports? ─── No ──→ Pair Bluetooth adapter in Windows
  |                            Yes ↓
  |
  ├─ Try COM3 @ 115200 ──→ Works? ─── Yes ──→ ✓ You're done!
  |                           No ↓
  |
  ├─ Try COM3 @ 38400 ───→ Works? ─── Yes ──→ ✓ You're done!
  |                           No ↓
  |
  ├─ Try COM4 @ 115200 ──→ Works? ─── Yes ──→ ✓ You're done!
  |                           No ↓
  |
  └─ Try COM4 @ 38400 ───→ Works? ─── Yes ──→ ✓ You're done!
                              No ↓

                    Check adapter is powered
                    Check Bluetooth connection
                    Try different baudrates
```

## Summary

**For your adapter:**
- ✅ Use **COM3** (outgoing port)
- ✅ Set baudrate to **115200**
- ❌ Don't connect to COM4 (incoming port)
- ✅ Only one program can use the port at a time

**To remember your settings:**
DeepDiag will save your connection settings automatically after a successful connection.
