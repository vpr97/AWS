# Load Generator
### file: ./gen.py
## Installation

Install the dependencies 
```sh
pip install aiohttp
pip install aiofiles
pip install asyncio
```
## Steps to run
```sh
python gen.py <upload_url_path> <username> <password> <rate_of_upload> <image_dir> <number_of_requests_to_be_sent>
```
Example
```sh
python gen.py http://localhost:5000/upload user pass 1 ./images 10
```
