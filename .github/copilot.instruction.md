# Project Overview
This app is created to scrap blog data from multiple websites and deliver it to external channels periodically

# Feature
- Scrap multiple websites based on the given URL and fetch the latest data withing the config timerange
- Deliver index consisting blog title, blog source, and date
- Run this program periodically based on config
    - Config: Run Daily
- Supported Channels:
    - Telegram
- Supported Blog Sources:
    - Uber Engineering: https://www.uber.com/en-ID/blog/engineering/
    - Netflix Tech Blog: https://netflixtechblog.com/
    - Airbnb Engineering: https://medium.com/airbnb-engineering/
    - ByteByteGo: https://blog.bytebytego.com/

# Tech Stack
- Programming Language: Python3
- Dependency Management: Poetry
- CronJob: Github Action
- CI/CD: Github Action

# Project Structure
```
sources             # scrapping logic for multiple blog sources
  uber.py
  netflix.py
  airbnb.py
  bytebytego.py
channels            # adapter to supported external channels
  telegram.py    
main.py             # orchestration logic
Makefile            # makefile to setup, run, test, etc
```