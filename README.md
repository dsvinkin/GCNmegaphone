# GCNmegaphone
GCNmegaphone processes [Gamma-ray Coordinates Network/Transient Astronomy Network (GCN/TAN)][1] VOEvent notices using [pygcn][2].
It listens for Fermi (GBM), INTEGRAL (SPI-ACS), LIGO/Virgo detections, sends notificatons to [Telegram][3] and downloads GBM a SPI-ACS data. 

## Usage

Clone the repo, edit config.yaml, and run `notice_filter.py` in [screen][4]. 
It listens for VOEvents until killed with Control-C.
One needs to provide Telegram bot token and chat_id to recieve alerts, 
see [instruction][5] to create your own bot.


## Config description

```yaml

log_dir:
    <path to store log and VOEvent dump, like "./logs" >
data_dir:
    <path to download data, like "./data" >
http_proxy:
    <e.g., "http://www-proxy:1234">

telegram_proxy:
    <Telegram socks5h proxy>
bot_token:
    <Telegram bot id>
chat_id:
    <chat/channel>

space-track: [login, passw]

```

## Package content
`notice_filter.py` - contains the main loop  
`get_fermi.py` - contains functions for dowloading Fermi (GBM) TTE data  
`gbm_tte.py` - converting GBM TTE data to ascii  
`get_integral.py` - downloading of the SPI-ACS data  
`clock.py` - different date and time conversion functions  
`tle.py` - downloading TLE from space-track.org  
`gbm_map.py` - 

`test/test_notice_filter.py` - testing script for notice_filter.py

| File                | Description   | 
| ------------------- | ------------- | 
| `notice_filter.py`  | The main loop | 
| `get_fermi.py`      | Fermi (GBM) TTE data dowloading  | 
| `gbm_tte.py`        | Converting GBM TTE data to ascii | 
| `gbm_map.py`        | Converting GBM healpix localization to ascii | 
| `get_integral.py`   | INTEGRAL SPI-ACS data dowloading | 
| `clock.py`          | Different date and time conversion functions |
| `tle.py`            | Downloading TLE from space-track.org | 
| `telegram_api.py`   | Sending Telegram messages |
| `path_utils.py`     | Simple path manipulation functions |
| `contour.py`        | Healpix contours extraction functions |

## Depends on

astropy  
pygcn  
lxml  
python-telegram-bot  
PySocks 
healpy
networkx 

## Useful links
[VOEvents in GCN/TAN][6]  
[Technical Details of GCN/TAN Notices][7]  

## Acknowledgments

Nikita Sulimin - intial development of the project during his M.Sc. project. 


[1]: http://gcn.gsfc.nasa.gov
[2]: https://github.com/lpsinger/pygcn
[3]: https://telegram.org
[4]: https://www.tecmint.com/screen-command-examples-to-manage-linux-terminals/
[5]: https://core.telegram.org/bots#6-botfather
[6]: https://gcn.gsfc.nasa.gov/voevent.html
[7]: https://gcn.gsfc.nasa.gov/tech_describe.html