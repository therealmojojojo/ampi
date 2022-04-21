# ampi
## DYI Raspberry PI based Vinyl Emulator + Amplifier 

Main use cases: 
1. Power 2*Monitor Audio BR2 speakers
1. Run Spotify, Roonlabs bridge
1. NFC card triggers a playlist (album)
1. HW volume button
   - 0-80%
1. HW power on/off switch - there has to be a way to reset pi without using command line (errors will happen)
   - stops/starts the amp but not the pi
1. HW media control buttons
   - play, rewind, ffw, stop
1. Remote control
1. E-ink 2.9'' inch
   - displays current track name
   - when amp is powered off, displays the time and outside temperature


## Making it work

### NFC card reader

Use case: I'm able to read the UID from a NFC card and pass it to AmpiController. 
Unable to make it work using [P532 NFC Reader](https://github.com/gassajor000/pn532pi) python library. The behaviour I've noticed is the following: 
- nfc-poll works reliably by itself
- pn532 library works randomnly and after a while starts failing with OSError when reading or writing. . I've used the examples included in the package. 
- After that OSError nfc-poll stops working
- after restart, nfc-poll starts working reliably. This make me suspect there are some fd that are not closed or something that breaks the communication with the card.

In the end, I wrote a simple python subrocess function that calls nfc-poll directly and does the job. 

### HiFiBerry AMP2

Followed the instructions [here](http://www.waailap.nl/instruction/215/setup-hifiberry-amp2.html) . Worked perfectly. 

### Music providers
#### Roon client
Installed [Roon Bridge](https://help.roonlabs.com/portal/en/kb/articles/linux-install#Overview)
Installed [pyroon](https://github.com/pavoni/pyroon)
Works perfectly. 

#### Spotify
Installed [mopidy](https://mopidy.com/)
Installed [mopidy-spotify](https://pypi.org/project/Mopidy-Spotify/)
Used [jsonrpclib](https://github.com/joshmarshall/jsonrpclib) 
Major issues: 
- errors [ModuleNotFoundError: No module named 'gi'](https://stackoverflow.com/questions/71369726/no-module-named-gi). Module gi does not seem to exist on python 3.10 -> must use python 3.9
- jsonrpclib sends text/xml and application-jsonrpc ContentType by default -> see [open bug](https://github.com/joshmarshall/jsonrpclib/issues/56). Mopidy [expects](https://docs.mopidy.com/en/latest/api/http/) application/json and rejects the request. Solution - [disable csfr_protection](https://github.com/mopidy/mopidy/pull/1714) in mopidy.conf
## BOM

|Component| Price|
|---|---|
|Raspberry Pi 4 B (+ fried Raspberry Pi 3B+)| 120+50|
|Hifiberry AMP2 | 60|
|2.9 inch e-Paper module V1 - waveshare | 15|
|NFC reader - P532 elechouse V3 | 15|
|Volume knob| Free|
|Buttons| Free|
|Hifi Binding Post Connectors | 20| 
|Case | Free (Lego)|


## GPIO configuration

|PIN|ROLE|USED BY|PIN|ROLE|USED BY|
|---|---|---|---|---|---|
|1|3v3 Power|[PN532 NFC v3](https://blog.stigok.com/2017/10/12/setting-up-a-pn532-nfc-module-on-a-raspberry-pi-using-i2c.html)|2|5v Power||
|3|GPIO 2 (I2C1 SDA)| HifiBerry AMP2/[PN532 NFC v3](https://blog.stigok.com/2017/10/12/setting-up-a-pn532-nfc-module-on-a-raspberry-pi-using-i2c.html) |4|5v Power|  |
|5|GPIO 3 (I2C1 SCL)|HifiBerry AMP2/[PN532 NFC v3](https://blog.stigok.com/2017/10/12/setting-up-a-pn532-nfc-module-on-a-raspberry-pi-using-i2c.html)  |6|Ground| [PN532 NFC v3](https://blog.stigok.com/2017/10/12/setting-up-a-pn532-nfc-module-on-a-raspberry-pi-using-i2c.html) |
|7|GPIO 4 (GPCLK0)|HifiBerry AMP2|8|GPIO 14 (UART TX)|
|9|Ground||10|GPIO 15 (UART RX)|
|11|GPIO 17|HifiBerry AMP2|12|GPIO 18 (PCM CLK)|HifiBerry AMP2|
|13|GPIO 27||14|Ground|
|15|GPIO 22||16|GPIO 23| E-Paper !!!|
|17|3v3 Power| E-Paper |18|GPIO 24| E-Paper
|19|GPIO 10 (SPI0 MOSI)| E-paper|20|Ground| E-Paper |
|21|GPIO 9  (SPI0 MISO)||22|GPIO 25| E-Paper |
|23|GPIO 11  (SPI0 SCLK)| E-paper|24|GPIO 8 (SPI0 CE0)| E-Paper
|25|Ground||26|GPIO 7 (SPI0 CE1)|
|27|GPIO 0 (EEPROM SDA)||28|GPIO 1 (EEPROM SCL)|
|29|GPIO 5| Play/Pause Button |30|Ground|
|31|GPIO 6| Stop Button |32|GPIO 12 (PWM0)||
|33|GPIO 13 (PWM1||34|Ground| Buttons |
|35|GPIO 19 (PCM FS)|HifiBerry AMP2|36|GPIO 16| Next Button |
|37|GPIO 26| Back Button |38|GPIO 20 (PCM DIN)|HifiBerry AMP2|
|39|Ground||40|GPIO 21 (PCM DOUT)|HifiBerry AMP2|

### PN532 NFC 
[Guide](https://blog.stigok.com/2017/10/12/setting-up-a-pn532-nfc-module-on-a-raspberry-pi-using-i2c.html)

1. Enable i2c in *raspi-config*

2. Install NFC software
~~~
sudo apt-get install i2c-tools
sudo apt install libnfc6 libnfc-bin libnfc-examples
~~~
3. Connect NFC module
NFC module pin -> Pi GPIO physical pin #
- GND -> 6
- VCC -> 4
- SDA -> 3
- SCL -> 5

Add config in /etc/nfc/libnfc.conf
~~~
device.name = "PN532 over I2C"
device.connstring = "pn532_i2c:/dev/i2c-1"
~~~
4. Check everything
~~~
$ nfc-scan-device -v
nfc-scan-device uses libnfc 1.8.0
1 NFC device(s) found:
- PN532 over I2C:
    pn532_i2c:/dev/i2c-1
chip: PN532 v1.6

$ sudo i2cdetect -y 1
     0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
00:                         -- -- -- -- -- -- -- -- 
10: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
20: -- -- -- -- 24 -- -- -- -- -- -- -- -- -- -- -- 
30: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
40: -- -- -- -- -- -- -- -- -- -- -- -- -- 4d -- -- 
50: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
60: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 

~~~

5. Check NFC card
~~~
$ nfc-poll
nfc-poll uses libnfc 1.8.0
NFC reader: PN532 over I2C opened
NFC device will poll during 36000 ms (20 pollings of 300 ms for 6 modulations)
ISO/IEC 14443A (106 kbps) target:
    ATQA (SENS_RES): 00  44  
       UID (NFCID1): 04  08  7a  01  00  a9  79  
      SAK (SEL_RES): 00  
Waiting for card removing...nfc_initiator_target_is_present: Target Released
done.
~~~


### 2.9'' e-Paper Screen

~~~
EPD    =>    Jetson Nano/RPI(BCM)
VCC    ->    3.3 -> Pin 17
GND    ->    GND -> Pin 20
DIN    ->    10(SPI0_MOSI) -> Pin 19
CLK    ->    11(SPI0_SCK) -> Pin 23
CS     ->    8(SPI0_CS0) -> Pin 24
DC     ->    25 -> Pin 22
RST    ->    17 (taken by AMP2) -> GPIO 23 -> Pin 16
BUSY   ->    24 -> Pin 18
~~~
!!! IMPORTANT 

RST Pin mapping must be changed in /RaspberryPi_JetsonNano/python/lib/waveshare_epd/epdconfig.py

## Links
- [RFID Spotify Pi player](https://fsahli.wordpress.com/2015/11/02/music-cards-rfid-cards-spotify-raspberry-pi/)
- [Plastic Player 2](http://brendandawes.com/projects/plasticplayer2)
- [P532 NFC Reader](https://www.elechouse.com/elechouse/index.php?main_page=product_info&cPath=90_93&products_id=2242)
- [E-Ink 2.9'' screen ](https://www.waveshare.com/wiki/2.9inch_e-Paper_Module)
  - [GIT repo](https://github.com/waveshare/e-Paper)


- GPIO
  - [Raspberry Pi 3+ GPIO](https://pinout.xyz/)
    - [Alt 1](https://www.etechnophiles.com/raspberry-pi-3-gpio-pinout-pin-diagram-and-specs-in-detail-model-b/)
    - [Alt 2](https://www.raspberrypi-spy.co.uk/2012/06/simple-guide-to-the-rpi-gpio-header-and-pins/) 
  - [HiFiberry Amp2](https://www.hifiberry.com/docs/hardware/gpio-usage-of-hifiberry-boards/)
  - [P532 NFC Reader](https://blog.stigok.com/2017/10/12/setting-up-a-pn532-nfc-module-on-a-raspberry-pi-using-i2c.html)
  - [P532 NFC Reader](https://ozeki.hu/p_3023-how-to-setup-a-nfc-reader-on-raspberry-pi.html)
  - [P532 NFC Reader](https://github.com/gassajor000/pn532pi)
  - [2.9'' e-Paper module v1]()

