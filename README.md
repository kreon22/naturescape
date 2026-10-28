# Naturescape

A naturescape view to start your day: a full-screen nature photograph with the
clock, today's daylight, weather for a handful of places, space weather and
aurora chances, the Moon, and a few good-news-for-nature headlines.

It's one HTML file. It needs no build step, accounts or API keys.

| Section | Source | Refresh |
|---|---|---|
| Weather, sunrise/sunset, day length | [Open-Meteo](https://open-meteo.com) | 15 min |
| Kp index, forecast, R/S/G scales, solar wind, aurora oval | [NOAA SWPC](https://www.swpc.noaa.gov) | 15 min |
| The Sun now (304 Å) | [NASA SDO](https://sdo.gsfc.nasa.gov) | 15 min |
| Moon phase | calculated on the device | – |
| Picture of the day | Wikimedia Commons featured nature pictures (default), Wikipedia POTD, or NASA APOD | daily |
| Good news | Good News Network (Earth), Positive News (Environment), Reasons to be Cheerful (Environment), plus any RSS you add | hourly |

The aurora line uses your first location's geomagnetic latitude and the higher
of current Kp and the 24-hour forecast peak. It's a rough guide. You still need
darkness and clear skies.

## Ways to run it

### 1. Just open it
Double-click `index.html`, or drag it into Chrome, Edge or Firefox. Open
**Settings** (bottom left; it hides after 5 seconds without mouse movement) to
add your places. Settings are stored in that browser.

### 2. Raspberry Pi or old laptop as a wall display (recommended)
Copy the folder over, then run the little server, which also relays the news
feeds so you don't depend on third-party feed services:

```bash
cd ~/naturescape && python3 serve.py
```

Open `http://localhost:8080/?kiosk=1` on the display. On your phone, use
`http://<pi-name>.local:8080` from the same Wi-Fi.

**Start everything on boot (Raspberry Pi OS Bookworm or newer, desktop version):**

1. Run the server as a user service:

   ```bash
   mkdir -p ~/.config/systemd/user
   cat > ~/.config/systemd/user/naturescape.service <<'EOF'
   [Unit]
   Description=Naturescape dashboard
   [Service]
   ExecStart=/usr/bin/python3 %h/naturescape/serve.py
   Restart=on-failure
   [Install]
   WantedBy=default.target
   EOF
   systemctl --user enable --now naturescape
   sudo loginctl enable-linger $USER
   ```

2. Open Chromium full-screen at login. On current Pi OS (labwc), add this line
   to `~/.config/labwc/autostart`. The browser is `chromium` on Trixie and
   `chromium-browser` on Bookworm:

   ```
   chromium --kiosk --noerrdialogs --disable-infobars --password-store=basic http://localhost:8080/?kiosk=1 &
   ```

   On an older X11 / LXDE install, put the same command (without `&`) in
   `~/.config/lxsession/LXDE-pi/autostart` prefixed with `@`.

3. In `raspi-config` → Display, turn **screen blanking** off.

A Pi 3B+ or newer is plenty. A Pi Zero 2 W works but the photo crossfades will be slow.

### 3. Host it for your phone anywhere
Put `index.html` on any static host (GitHub Pages, Netlify Drop, Cloudflare
Pages). Then on the phone choose **Add to Home Screen**. Without `serve.py`, news
comes through rss2json.com, with api.allorigins.win as a fallback.

## URL options

Handy for setting up a kiosk without a mouse:

- `?loc=Helsinki;Tromsø;Kyoto`: places, first one featured (`;` separated)
- `&units=metric`, `metric-ms` or `imperial`
- `&pic=commons`, `potd` or `apod`
- `&kiosk=1`: keep the screen awake

Example: `http://localhost:8080/?kiosk=1&loc=Oulu;Helsinki&units=metric-ms`

## Display behaviour
- Landscape screens get the photo with a side column. Phones and portrait monitors get the photo first, with the details below.
- The photo drifts very slowly to avoid burn-in. It doesn't drift if the device asks for reduced motion.
- The screen dims from 22:00 to 06:00 (you can turn this off in Settings).
- The mouse cursor and buttons hide after 5 seconds idle.
- If a service is down, the last good weather and news are shown and marked as offline.
