import time
from fabric.api import run

#List of ip-ranges Moldova
iplistmd = [
"5.56.64.0-5.56.127.255",
"31.31.0.0-31.31.31.255",
"37.26.128.0-37.26.143.255",
"37.34.96.0-37.34.127.255",
"37.75.16.0-37.75.31.255",
"37.75.64.0-37.75.127.255",
"37.233.0.0-37.233.63.255",
"37.246.0.0-37.246.255.255",
"46.55.0.0-46.55.127.255",
"46.166.0.0-46.166.63.255",
"62.221.64.0-62.221.127.255",
"77.89.192.0-77.89.255.255",
"77.235.96.0-77.235.127.255",
"79.140.160.0-79.140.175.255",
"80.94.240.0-80.94.255.255",
"80.245.80.0-80.245.95.255",
"81.162.128.0-81.162.191.255",
"83.218.192.0-83.218.223.255",
"84.234.48.0-84.234.63.255",
"87.248.160.0-87.248.191.255",
"87.255.64.0-87.255.95.255",
"89.28.0.0-89.28.127.255",
#"89.149.64.0-89.149.127.255",
"89.187.32.0-89.187.63.255",
"91.242.64.0-91.242.127.255",
"91.242.128.0-91.242.159.255",
"91.250.224.0-91.250.239.255",
"92.39.48.0-92.39.63.255",
"93.115.224.0-93.115.239.255",
"94.103.0.0-94.103.15.255",
"94.139.128.0-94.139.159.255",
"94.243.64.0-94.243.127.255",
"95.65.0.0-95.65.127.255",
"95.153.64.0-95.153.127.255",
"109.185.0.0-109.185.255.255",
"109.198.32.0-109.198.63.255",
"176.123.0.0-176.123.31.255",
"178.17.160.0-178.17.175.255",
"178.18.32.0-178.18.47.255",
"178.76.64.0-178.76.127.255",
"178.132.112.0-178.132.127.255",
"178.132.128.0-178.132.191.255",
"178.168.0.0-178.168.127.255",
"178.175.128.0-178.175.255.255",
"188.0.224.0-188.0.255.255",
"188.131.0.0-188.131.127.255",
"188.138.128.0-188.138.255.255",
"188.237.0.0-188.237.255.255",
"188.244.16.0-188.244.31.255",
"195.22.224.0-195.22.255.255",
"195.138.96.0-195.138.127.255",
"212.0.192.0-212.0.223.255",
"212.28.64.0-212.28.95.255",
"212.56.192.0-212.56.223.255",
"217.12.112.0-217.12.127.255",
"217.19.208.0-217.19.223.255",
"217.26.144.0-217.26.159.255",
"217.26.160.0-217.26.175.255",
]

#List of ip-ranges Ucraine
iplistua = [
"62.16.0.0-62.16.31.255",
"62.64.64.0-62.64.127.255",
"62.80.160.0-62.80.191.255",
"62.149.0.0-62.149.31.255",
"62.221.32.0-62.221.63.255",
"62.244.0.0-62.244.63.255",
"80.70.64.0-80.70.95.255",
"80.73.0.0-80.73.15.255",
"80.77.32.0-80.77.47.255",
"80.78.32.0-80.78.63.255",
"80.84.176.0-80.84.191.255",
"80.90.224.0-80.90.239.255",
"80.91.160.0-80.91.191.255",
"80.92.224.0-80.92.239.255",
"80.93.112.0-80.93.127.255",
"80.243.144.0-80.243.159.255",
"80.245.112.0-80.245.127.255",
"80.249.224.0-80.249.239.255",
"80.252.240.0-80.252.255.255",
"80.254.0.0-80.254.15.255",
"80.255.64.0-80.255.79.255",
"81.17.128.0-81.17.143.255",
"81.21.0.0-81.21.15.255",
"81.23.16.0-81.23.31.255",
"81.24.208.0-81.24.223.255",
"81.25.224.0-81.25.239.255",
"81.30.160.0-81.30.175.255",
"81.90.224.0-81.90.239.255",
"82.144.192.0-82.144.223.255",
"82.193.96.0-82.193.127.255",
"82.207.0.0-82.207.127.255",
"83.137.88.0-83.137.95.255",
"83.143.232.0-83.143.239.255",
"83.170.192.0-83.170.255.255",
"83.218.224.0-83.218.255.255",
"85.90.192.0-85.90.223.255",
"85.114.192.0-85.114.223.255",
"85.159.0.0-85.159.7.255",
"85.198.128.0-85.198.191.255",
"85.202.0.0-85.202.255.255",
"85.223.128.0-85.223.255.255",
"85.238.96.0-85.238.127.255",
"86.111.224.0-86.111.231.255",
"87.236.224.0-87.236.231.255",
"87.238.152.0-87.238.159.255",
"88.81.224.0-88.81.255.255",
"88.208.0.0-88.208.63.255",
"88.214.64.0-88.214.127.255",
"89.105.224.0-89.105.255.255",
"89.110.64.0-89.110.127.255",
"89.185.0.0-89.185.31.255",
"89.187.0.0-89.187.31.255",
"89.209.0.0-89.209.255.255",
"140.232.0.0-140.232.255.255",
"193.0.227.0-193.0.228.255",
"193.0.240.0-193.0.240.255",
"193.0.247.0-193.0.247.255",
"193.9.158.0-193.9.158.255",
"193.16.45.0-193.16.45.255",
"193.16.47.0-193.16.47.255",
"193.16.101.0-193.16.101.255",
"193.16.105.0-193.16.105.255",
"193.16.233.0-193.16.233.255",
"193.16.238.0-193.16.238.255",
"193.16.247.0-193.16.247.255",
"193.17.46.0-193.17.46.255",
"193.17.69.0-193.17.69.255",
"193.17.174.0-193.17.174.255",
"193.17.208.0-193.17.208.255",
"193.17.213.0-193.17.213.255",
"193.17.216.0-193.17.217.255",
"193.17.226.0-193.17.226.255",
"193.17.228.0-193.17.228.255",
"193.17.253.0-193.17.253.255",
"193.19.74.0-193.19.75.255",
"193.19.84.0-193.19.87.255",
"193.19.96.0-193.19.97.255",
"193.19.100.0-193.19.101.255",
"193.19.108.0-193.19.111.255",
"193.19.132.0-193.19.135.255",
"193.19.152.0-193.19.155.255",
"193.19.184.0-193.19.187.255",
"193.19.200.0-193.19.207.255",
"193.19.228.0-193.19.231.255",
"193.19.240.0-193.19.247.255",
"193.19.252.0-193.19.255.255",
"193.22.6.0-193.22.6.255",
"193.22.84.0-193.22.84.255",
"193.22.138.0-193.22.138.255",
"193.22.140.0-193.22.140.255",
"193.23.0.0-193.23.0.255",
"193.23.53.0-193.23.53.255",
"193.23.60.0-193.23.60.255",
"193.23.122.0-193.23.122.255",
"193.23.157.0-193.23.157.255",
"193.23.181.0-193.23.181.255",
"193.23.183.0-193.23.183.255",
"193.23.225.0-193.23.225.255",
"193.24.25.0-193.24.25.255",
"193.24.30.0-193.24.30.255",
"193.24.232.0-193.24.235.255",
"193.25.106.0-193.25.109.255",
"193.25.176.0-193.25.177.255",
"193.25.180.0-193.25.181.255",
"193.25.255.0-193.25.255.255",
"193.26.3.0-193.26.3.255",
"193.26.13.0-193.26.13.255",
"193.26.20.0-193.26.20.255",
"193.26.27.0-193.26.27.255",
"193.26.134.0-193.26.134.255",
"193.27.0.0-193.27.0.255",
"193.27.47.0-193.27.47.255",
"193.27.68.0-193.27.69.255",
"193.27.80.0-193.27.81.255",
"193.27.208.0-193.27.209.255",
"193.27.232.0-193.27.235.255",
"193.27.242.0-193.27.243.255",
"193.28.85.0-193.28.85.255",
"193.28.87.0-193.28.87.255",
"193.28.92.0-193.28.92.255",
"193.28.177.0-193.28.177.255",
"193.28.186.0-193.28.186.255",
"193.28.200.0-193.28.200.255",
"193.29.53.0-193.29.53.255",
"193.29.128.0-193.29.128.255",
"193.29.203.0-193.29.204.255",
"193.29.220.0-193.29.220.255",
"193.30.244.0-193.30.247.255",
"193.41.4.0-193.41.5.255",
"193.41.38.0-193.41.38.255",
"193.41.48.0-193.41.51.255",
"193.41.60.0-193.41.63.255",
"193.41.80.0-193.41.80.255",
"193.41.88.0-193.41.88.255",
"193.41.128.0-193.41.131.255",
"193.41.160.0-193.41.163.255",
"193.41.172.0-193.41.175.255",
"193.41.184.0-193.41.187.255",
"193.41.218.0-193.41.219.255",
"193.41.239.0-193.41.239.255",
"193.43.95.0-193.43.95.255",
"193.43.148.0-193.43.148.255",
"193.43.222.0-193.43.223.255",
"193.43.248.0-193.43.251.255",
"193.47.70.0-193.47.70.255",
"193.47.85.0-193.47.85.255",
"193.47.137.0-193.47.137.255",
"193.47.145.0-193.47.145.255",
"193.47.166.0-193.47.166.255",
"193.58.0.128-193.58.0.255",
"193.58.248.0-193.58.248.255",
"193.58.251.0-193.58.251.255",
"193.58.254.0-193.58.254.255",
"193.84.19.0-193.84.19.255",
"193.84.50.0-193.84.50.255",
"193.84.72.0-193.84.72.255",
"193.84.77.0-193.84.77.255",
"193.84.90.0-193.84.90.255",
"193.93.12.0-193.93.19.255",
"193.93.48.0-193.93.51.255",
"193.93.76.0-193.93.79.255",
"193.93.100.0-193.93.103.255",
"193.93.108.0-193.93.111.255",
"193.93.116.0-193.93.119.255",
"193.93.160.0-193.93.163.255",
"193.93.184.0-193.93.195.255",
"193.93.212.0-193.93.215.255",
"193.93.228.0-193.93.231.255",
"193.93.244.0-193.93.247.255",
"193.108.36.0-193.108.39.255",
"193.108.44.0-193.108.51.255",
"193.108.112.0-193.108.131.255",
"193.108.162.0-193.108.163.255",
"193.108.170.0-193.108.171.255",
"193.108.209.0-193.108.209.255",
"193.108.226.0-193.108.227.255",
"193.108.236.0-193.108.237.255",
"193.108.240.0-193.108.243.255",
"193.108.248.0-193.108.251.255",
"193.109.8.0-193.109.11.255",
"193.109.60.0-193.109.61.255",
"193.109.80.0-193.109.80.255",
"193.109.84.0-193.109.84.255",
"193.109.93.0-193.109.93.255",
"193.109.100.0-193.109.103.255",
"193.109.108.0-193.109.111.255",
"193.109.128.0-193.109.129.255",
"193.109.144.0-193.109.147.255",
"193.109.160.0-193.109.171.255",
"193.109.240.0-193.109.241.255",
"193.109.248.0-193.109.249.255",
"193.110.16.0-193.110.23.255",
"193.110.89.0-193.110.89.255",
"193.110.100.0-193.110.101.255",
"193.110.106.0-193.110.107.255",
"193.110.124.0-193.110.127.255",
"193.110.134.0-193.110.134.255",
"193.110.144.0-193.110.144.255",
"193.110.156.0-193.110.156.255",
"193.110.160.0-193.110.163.255",
"193.110.168.0-193.110.169.255",
"193.110.172.0-193.110.177.255",
"193.110.184.0-193.110.185.255",
"193.110.188.0-193.110.189.255",
"193.111.0.0-193.111.3.255",
"193.111.6.0-193.111.9.255",
"193.111.16.0-193.111.17.255",
"193.111.48.0-193.111.51.255",
"193.111.60.0-193.111.63.255",
"193.111.83.0-193.111.83.255",
"193.111.85.0-193.111.85.255",
"193.111.114.0-193.111.115.255",
"193.111.126.0-193.111.127.255",
"193.111.173.0-193.111.173.255",
"193.111.188.0-193.111.191.255",
"193.111.204.0-193.111.205.255",
"193.111.239.0-193.111.243.255",
"193.111.248.0-193.111.251.255",
"193.138.77.0-193.138.77.255",
"193.138.84.0-193.138.84.255",
"193.138.87.0-193.138.87.255",
"193.138.93.0-193.138.93.255",
"193.138.114.0-193.138.114.255",
"193.138.122.0-193.138.122.255",
"193.138.132.0-193.138.135.255",
"193.138.144.0-193.138.147.255",
"193.138.184.0-193.138.187.255",
"193.138.232.0-193.138.239.255",
"193.138.244.0-193.138.247.255",
"193.151.12.0-193.151.15.255",
"193.151.56.0-193.151.59.255",
"193.151.88.0-193.151.91.255",
"193.151.104.0-193.151.107.255",
"193.151.240.0-193.151.243.255",
"193.164.92.0-193.164.95.255",
"193.164.232.96-193.164.232.127",
"193.178.124.0-193.178.127.255",
"193.178.144.0-193.178.147.255",
"193.178.172.0-193.178.172.255",
"193.178.187.0-193.178.187.255",
"193.178.190.0-193.178.191.255",
"193.178.228.0-193.178.229.255",
"193.178.236.0-193.178.237.255",
"193.178.248.0-193.178.251.255",
"193.189.88.0-193.189.89.255",
"193.189.96.0-193.189.97.255",
"193.189.126.0-193.189.127.255",
"193.192.15.128-193.192.15.191",
"193.193.192.0-193.193.223.255",
"193.201.26.0-193.201.27.255",
"193.201.60.0-193.201.63.255",
"193.201.80.0-193.201.83.255",
"193.201.98.0-193.201.100.255",
"193.201.116.0-193.201.117.255",
"193.201.140.0-193.201.143.255",
"193.201.147.128-193.201.147.159",
"193.201.150.192-193.201.150.255",
"193.201.152.128-193.201.152.255",
"193.201.156.0-193.201.156.127",
"193.201.175.0-193.201.175.255",
"193.201.192.0-193.201.193.255",
"193.201.198.0-193.201.199.255",
"193.201.206.0-193.201.211.255",
"193.201.216.0-193.201.219.255",
"193.201.224.0-193.201.227.255",
"193.202.19.0-193.202.19.255",
"193.202.110.0-193.202.110.255",
"193.203.218.0-193.203.219.255",
"193.203.236.0-193.203.237.255",
"193.222.111.0-193.222.111.255",
"193.223.98.0-193.223.98.255",
"193.227.206.0-193.227.211.255",
"193.227.230.0-193.227.231.255",
"193.227.250.0-193.227.251.255",
"193.238.20.0-193.238.23.255",
"193.238.32.0-193.238.35.255",
"193.238.44.0-193.238.47.255",
"193.238.96.0-193.238.99.255",
"193.238.108.0-193.238.111.255",
"193.238.116.0-193.238.119.255",
"193.238.152.0-193.238.155.255",
"193.238.192.0-193.238.195.255",
"193.239.24.0-193.239.27.255",
"193.239.68.0-193.239.75.255",
"193.239.128.0-193.239.129.255",
"193.239.132.0-193.239.133.255",
"193.239.142.0-193.239.143.255",
"193.239.152.0-193.239.153.255",
"193.239.178.0-193.239.181.255",
"193.239.216.0-193.239.217.255",
"193.239.228.0-193.239.229.255",
"193.239.234.0-193.239.235.255",
"193.239.238.0-193.239.239.255",
"193.239.250.0-193.239.251.255",
"193.239.254.0-193.239.255.255",
"193.243.156.0-193.243.159.255",
"193.254.196.0-193.254.197.255",
"193.254.208.0-193.254.209.255",
"193.254.216.0-193.254.221.255",
"193.254.226.0-193.254.227.255",
"193.254.232.0-193.254.235.255",
"194.6.196.0-194.6.199.255",
"194.6.231.0-194.6.233.255",
"194.8.51.0-194.8.51.255",
"194.8.56.0-194.8.56.255",
"194.9.68.0-194.9.71.255",
"194.24.236.0-194.24.237.255",
"194.24.246.0-194.24.247.255",
"194.29.60.0-194.29.63.255",
"194.29.184.0-194.29.187.255",
"194.29.205.0-194.29.205.255",
"194.30.168.0-194.30.168.255",
"194.30.170.0-194.30.170.255",
"194.30.172.0-194.30.172.255",
"194.42.106.0-194.42.107.255",
"194.42.192.0-194.42.207.255",
"194.44.0.0-194.44.255.255",
"194.50.0.0-194.50.0.255",
"194.50.51.0-194.50.51.255",
"194.50.81.0-194.50.81.255",
"194.50.85.0-194.50.85.255",
"194.50.98.0-194.50.98.255",
"194.50.114.0-194.50.114.255",
"194.50.116.0-194.50.116.255",
"194.50.119.0-194.50.119.255",
"194.50.124.0-194.50.125.255",
"194.50.161.0-194.50.161.255",
"194.50.167.0-194.50.167.255",
"194.50.169.0-194.50.169.255",
"194.50.254.0-194.50.254.255",
"194.54.152.0-194.54.159.255",
"194.54.184.0-194.54.187.255",
"194.63.140.0-194.63.143.255",
"194.79.8.0-194.79.11.255",
"194.79.20.0-194.79.23.255",
"194.79.60.0-194.79.63.255",
"194.88.1.0-194.88.1.255",
"194.88.11.0-194.88.11.255",
"194.88.150.0-194.88.153.255",
"194.88.218.0-194.88.221.255",
"194.93.160.0-194.93.191.255",
"194.105.136.0-194.105.137.255",
"194.105.144.0-194.105.145.255",
"194.106.208.0-194.106.209.255",
"194.106.216.0-194.106.219.255",
"194.114.132.0-194.114.139.255",
"194.116.162.0-194.116.163.255",
"194.116.170.0-194.116.171.255",
"194.116.194.0-194.116.195.255",
"194.116.228.0-194.116.229.255",
"194.116.232.0-194.116.233.255",
"194.116.244.0-194.116.245.255",
"194.117.50.0-194.117.50.127",
"194.117.55.0-194.117.55.127",
"194.125.224.0-194.125.227.255",
"194.125.244.0-194.125.245.255",
"194.125.248.0-194.125.249.255",
"194.126.204.0-194.126.204.255",
"194.143.136.0-194.143.137.255",
"194.143.148.0-194.143.149.255",
"194.145.117.0-194.145.117.255",
"194.145.198.0-194.145.199.255",
"194.145.216.0-194.145.217.255",
"194.145.227.0-194.145.227.255",
"194.145.244.0-194.145.247.255",
"194.146.110.0-194.146.110.255",
"194.146.112.0-194.146.112.255",
"194.146.116.0-194.146.116.255",
"194.146.132.0-194.146.143.255",
"194.146.156.0-194.146.159.255",
"194.146.180.0-194.146.183.255",
"194.146.188.0-194.146.191.255",
"194.146.220.0-194.146.223.255",
"194.146.228.0-194.146.231.255",
"194.150.76.0-194.150.79.255",
"194.150.104.0-194.150.107.255",
"194.150.174.0-194.150.175.255",
"194.150.192.0-194.150.193.255",
"194.150.220.0-194.150.221.255",
"194.150.232.0-194.150.233.255",
"194.153.128.0-194.153.129.255",
"194.153.148.0-194.153.149.255",
"194.183.160.0-194.183.191.255",
"194.187.24.0-194.187.31.255",
"194.187.48.0-194.187.51.255",
"194.187.56.0-194.187.59.255",
"194.187.96.0-194.187.99.255",
"194.187.104.0-194.187.111.255",
"194.187.128.0-194.187.131.255",
"194.187.148.0-194.187.155.255",
"194.187.208.0-194.187.211.255",
"194.187.216.0-194.187.219.255",
"194.187.228.0-194.187.231.255",
"194.213.23.0-194.213.23.255",
"194.242.53.0-194.242.53.255",
"194.242.59.0-194.242.60.255",
"194.242.96.0-194.242.103.255",
"194.242.116.0-194.242.119.255",
"194.246.99.0-194.246.99.255",
"194.246.104.0-194.246.105.255",
"194.246.116.0-194.246.117.255",
"194.246.120.0-194.246.121.255",
"195.5.0.0-195.5.63.255",
"195.5.106.0-195.5.109.255",
"195.5.124.0-195.5.125.255",
"195.10.210.0-195.10.210.255",
"195.10.218.0-195.10.218.255",
"195.12.36.0-195.12.39.255",
"195.13.47.0-195.13.47.255",
"195.16.76.0-195.16.79.255",
"195.20.96.0-195.20.97.255",
"195.20.100.0-195.20.103.255",
"195.20.118.0-195.20.119.255",
"195.20.124.0-195.20.125.255",
"195.20.128.0-195.20.159.255",
"195.22.130.0-195.22.133.255",
"195.22.140.0-195.22.141.255",
"195.22.152.0-195.22.153.255",
"195.24.64.0-195.24.71.255",
"195.24.128.0-195.24.159.255",
"195.26.16.0-195.26.19.255",
"195.28.186.0-195.28.187.255",
"195.34.196.0-195.34.207.255",
"195.35.65.0-195.35.65.255",
"195.35.84.0-195.35.85.255",
"195.38.16.0-195.38.18.255",
"195.39.196.0-195.39.197.255",
"195.39.210.0-195.39.211.255",
"195.39.214.0-195.39.215.255",
"195.39.232.0-195.39.233.255",
"195.39.240.0-195.39.243.255",
"195.39.248.0-195.39.249.255",
"195.39.252.0-195.39.253.255",
"195.43.32.0-195.43.35.255",
"195.43.40.0-195.43.43.255",
"195.46.36.0-195.46.39.255",
"195.47.202.0-195.47.202.255",
"195.47.212.0-195.47.212.255",
"195.47.219.0-195.47.219.255",
"195.47.248.0-195.47.248.255",
"195.47.253.0-195.47.253.255",
"195.49.128.0-195.49.131.255",
"195.49.148.0-195.49.151.255",
"195.49.164.0-195.49.167.255",
"195.49.200.0-195.49.207.255",
"195.58.224.0-195.58.255.255",
"195.60.66.0-195.60.67.255",
"195.60.70.0-195.60.71.255",
"195.60.174.0-195.60.175.255",
"195.60.184.0-195.60.185.255",
"195.60.200.0-195.60.207.255",
"195.60.224.0-195.60.227.255",
"195.62.14.0-195.62.15.255",
"195.62.24.0-195.62.25.255",
"195.64.224.0-195.64.255.255",
"195.66.65.0-195.66.66.255",
"195.66.79.0-195.66.79.255",
"195.66.93.0-195.66.93.255",
"195.66.136.0-195.66.141.255",
"195.66.152.0-195.66.153.255",
"195.66.192.0-195.66.223.255",
"195.68.202.0-195.68.203.255",
"195.68.216.0-195.68.219.255",
"195.68.222.0-195.68.223.255",
"195.68.248.0-195.68.249.255",
"195.69.64.0-195.69.67.255",
"195.69.76.0-195.69.79.255",
"195.69.100.0-195.69.103.255",
"195.69.136.0-195.69.139.255",
"195.69.168.0-195.69.171.255",
"195.69.176.0-195.69.179.255",
"195.69.188.0-195.69.191.255",
"195.69.196.0-195.69.203.255",
"195.69.228.0-195.69.231.255",
"195.72.156.0-195.72.159.255",
"195.78.34.0-195.78.35.255",
"195.78.38.0-195.78.39.255",
"195.78.56.0-195.78.61.255",
"195.78.232.0-195.78.235.255",
"195.78.244.0-195.78.247.255",
"195.78.252.0-195.78.255.255",
"195.80.231.0-195.80.232.255",
"195.85.197.0-195.85.198.255",
"195.85.214.0-195.85.214.255",
"195.85.216.0-195.85.216.255",
"195.85.223.0-195.85.223.255",
"195.85.233.0-195.85.233.255",
"195.85.250.0-195.85.250.255",
"195.90.122.0-195.90.123.255",
"195.95.138.0-195.95.138.255",
"195.95.206.0-195.95.207.255",
"195.95.210.0-195.95.211.255",
"195.95.222.0-195.95.223.255",
"195.95.232.0-195.95.233.255",
"195.114.96.0-195.114.97.255",
"195.114.120.0-195.114.121.255",
"195.114.128.0-195.114.159.255",
"195.123.0.0-195.123.255.255",
"195.128.16.0-195.128.19.255",
"195.128.178.0-195.128.179.255",
"195.128.226.0-195.128.227.255",
"195.128.230.0-195.128.231.255",
"195.128.248.0-195.128.249.255",
"195.128.252.0-195.128.253.255",
"195.135.196.0-195.135.203.255",
"195.135.240.0-195.135.247.255",
"195.137.167.0-195.137.167.255",
"195.137.185.0-195.137.185.255",
"195.137.192.0-195.137.193.255",
"195.137.196.0-195.137.197.255",
"195.137.202.0-195.137.203.255",
"195.137.206.0-195.137.207.255",
"195.137.226.0-195.137.227.255",
"195.137.232.0-195.137.233.255",
"195.137.240.0-195.137.241.255",
"195.137.244.0-195.137.245.255",
"195.137.250.0-195.137.251.255",
"195.138.64.0-195.138.95.255",
"195.138.160.0-195.138.191.255",
"195.140.168.0-195.140.171.255",
"195.140.188.0-195.140.191.255",
"195.140.224.0-195.140.227.255",
"195.140.244.0-195.140.247.255",
"195.144.21.0-195.144.21.255",
"195.144.25.0-195.144.25.255",
"195.144.28.0-195.144.28.255",
"195.149.70.0-195.149.70.255",
"195.149.88.0-195.149.88.255",
"195.149.90.0-195.149.90.255",
"195.149.108.0-195.149.108.255",
"195.149.112.0-195.149.112.255",
"195.149.114.0-195.149.114.255",
"195.149.125.0-195.149.125.255",
"195.160.192.0-195.160.195.255",
"195.160.220.0-195.160.223.255",
"195.160.232.0-195.160.235.255",
"195.160.244.0-195.160.247.255",
"195.170.163.0-195.170.163.255",
"195.170.178.0-195.170.179.255",
"195.177.68.0-195.177.75.255",
"195.177.92.0-195.177.95.255",
"195.177.112.0-195.177.119.255",
"195.177.124.0-195.177.127.255",
"195.177.208.0-195.177.209.255",
"195.177.222.0-195.177.223.255",
"195.177.228.0-195.177.229.255",
"195.177.236.0-195.177.241.255",
"195.178.104.0-195.178.105.255",
"195.178.122.0-195.178.123.255",
"195.178.128.0-195.178.159.255",
"195.182.0.0-195.182.0.255",
"195.182.21.0-195.182.22.255",
"195.182.194.0-195.182.195.255",
"195.182.202.0-195.182.203.255",
"195.182.206.0-195.182.207.255",
"195.184.192.0-195.184.223.255",
"195.189.8.0-195.189.11.255",
"195.189.16.0-195.189.19.255",
"195.189.132.0-195.189.135.255",
"195.189.196.0-195.189.197.255",
"195.189.200.0-195.189.201.255",
"195.190.144.0-195.190.144.255",
"195.190.157.0-195.190.157.255",
"195.206.224.0-195.206.255.255",
"195.214.192.0-195.214.199.255",
"195.225.52.0-195.225.53.255",
"195.225.96.0-195.225.99.255",
"195.225.112.0-195.225.115.255",
"195.225.128.0-195.225.131.255",
"195.225.144.0-195.225.147.255",
"195.225.156.0-195.225.159.255",
"195.225.172.0-195.225.179.255",
"195.225.228.0-195.225.231.255",
"195.230.128.0-195.230.159.255",
"195.234.61.0-195.234.61.255",
"195.234.72.0-195.234.79.255",
"195.234.96.0-195.234.99.255",
"195.234.112.0-195.234.115.255",
"195.234.124.0-195.234.127.255",
"195.234.132.0-195.234.132.255",
"195.234.148.0-195.234.148.255",
"195.234.200.0-195.234.203.255",
"195.234.212.0-195.234.215.255",
"195.234.220.0-195.234.223.255",
"195.238.92.0-195.238.93.255",
"195.242.94.0-195.242.95.255",
"195.242.112.0-195.242.115.255",
"195.242.200.0-195.242.203.255",
"195.244.4.0-195.244.5.255",
"195.244.8.0-195.244.9.255",
"195.245.80.0-195.245.81.255",
"195.245.112.0-195.245.113.255",
"195.245.118.0-195.245.121.255",
"195.245.194.0-195.245.194.255",
"195.245.200.0-195.245.200.255",
"195.245.211.0-195.245.211.255",
"195.245.215.0-195.245.215.255",
"195.245.221.0-195.245.221.255",
"195.245.253.0-195.245.253.255",
"195.248.160.0-195.248.191.255",
"195.250.36.0-195.250.36.255",
"195.250.43.0-195.250.43.255",
"195.250.62.0-195.250.62.255",
"195.254.142.0-195.254.143.255",
"195.254.150.0-195.254.151.255",
"212.1.64.0-212.1.127.255",
"212.3.96.0-212.3.127.255",
"212.8.32.0-212.8.63.255",
"212.9.224.0-212.9.255.255",
"212.15.128.0-212.15.159.255",
"212.26.128.0-212.26.159.255",
"212.35.160.0-212.35.191.255",
"212.40.32.0-212.40.63.255",
"212.42.64.0-212.42.95.255",
"212.58.160.0-212.58.191.255",
"212.66.32.0-212.66.63.255",
"212.68.160.0-212.68.191.255",
"212.82.192.0-212.82.223.255",
"212.86.96.0-212.86.127.255",
"212.86.224.0-212.86.255.255",
"212.90.96.0-212.90.127.255",
"212.90.160.0-212.90.191.255",
"212.109.32.0-212.109.63.255",
"212.110.128.0-212.110.159.255",
"212.111.192.0-212.111.223.255",
"212.113.32.0-212.113.63.255",
"212.115.224.0-212.115.255.255",
"213.130.0.0-213.130.31.255",
"213.133.160.0-213.133.191.255",
"213.154.192.0-213.154.223.255",
"213.156.64.0-213.156.95.255",
"213.159.224.0-213.159.255.255",
"213.160.128.0-213.160.159.255",
"213.169.64.0-213.169.95.255",
"213.179.224.0-213.179.255.255",
"213.186.96.0-213.186.127.255",
"213.186.192.0-213.186.223.255",
"213.200.32.0-213.200.63.255",
"213.227.192.0-213.227.255.255",
"217.9.0.0-217.9.15.255",
"217.12.192.0-217.12.223.255",
"217.20.160.0-217.20.191.255",
"217.24.160.0-217.24.175.255",
"217.25.160.0-217.25.175.255",
"217.25.192.0-217.25.207.255",
"217.27.144.0-217.27.159.255",
"217.65.240.0-217.65.255.255",
"217.66.96.0-217.66.111.255",
"217.73.128.0-217.73.143.255",
"217.76.192.0-217.76.207.255",
"217.77.208.0-217.77.223.255",
"217.112.208.0-217.112.223.255",
"217.117.64.0-217.117.79.255",
"217.144.64.0-217.144.79.255",
"217.146.240.0-217.146.255.255",
"217.147.160.0-217.147.175.255",
"217.175.80.0-217.175.95.255",
"217.196.160.0-217.196.175.255",
"217.198.128.0-217.198.143.255",
"217.199.224.0-217.199.239.255",
]

#created 25.08.2016 for parlament.try.direct
iplist = [
"89.28.84.116",
"89.28.80.80",
"178.18.42.132",
"178.168.31.73",
"95.153.89.251",
"37.233.56.117",
]

#created 25.08.2016 for prm.try.direct
iplist2 = [
"89.28.84.116",
"178.18.42.132",
]


def add_accept_range_rule():
    for iprange in iplistmd:
        run('iptables -A INPUT -i eth0 -m iprange --src-range %s -j ACCEPT' % iprange)
        time.sleep(1)


def remove_accept_range_rule():
    for iprange in iplistmd:
        run('iptables -D INPUT -i eth0 -m iprange --src-range %s -j ACCEPT' % iprange)
        time.sleep(1)

#for parlament.try.direct
def add_accept_list_rule():
    for iprange in iplist:
        run('iptables -A INPUT -i eth0 -s %s/32 -j ACCEPT' % iprange)
        time.sleep(1)

#for parlament.try.direct
def remove_accept_list_rule():
    for iprange in iplist:
        run('iptables -D INPUT -i eth0 -s %s/32 -j ACCEPT' % iprange)
        time.sleep(1)

#for prm.try.direct
def add_accept_list2_rule():
    for iprange in iplist2:
        run('iptables -A INPUT -i eth0 -s %s/32 -j ACCEPT' % iprange)
        time.sleep(1)

#for prm.try.direct
def remove_accept_list2_rule():
    for iprange in iplist2:
        run('iptables -D INPUT -i eth0  -s %s/32 -j ACCEPT' % iprange)
        time.sleep(1)



def add_drop_ip_rule():
    run('iptables -A INPUT -i eth0 -s 10.50.44.23/32 -j DROP')


def remove_drop_ip_rule():
    run('iptables -D INPUT -i eth0 -s 10.50.44.23/32 -j DROP')

def add_accept_ip_rule():
    run('iptables -A INPUT -i eth0 -s 89.28.84.116/32 -j ACCEPT')

def remove_accept_ip_rule():
    run('iptables -D INPUT -i eth0 -s 89.28.84.116/32 -j ACCEPT')

def add_reject_rule():
    run('iptables -A INPUT -i eth0 -j REJECT')

def remove_reject_rule():
    run('iptables -D INPUT -i eth0 -j REJECT')
