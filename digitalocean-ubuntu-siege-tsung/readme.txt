for tests by siege run:

sudo siege -b -v -c 30 -r 3 http://ya.ru/

results:
 ....
  HTTP/1.1 200   0.23 secs:    3681 bytes ==> GET  /
  HTTP/1.1 302   0.12 secs:       0 bytes ==> GET  /
  HTTP/1.1 200   0.27 secs:    3685 bytes ==> GET  /
  HTTP/1.1 200   0.25 secs:    3682 bytes ==> GET  /
  done.
  Transactions:		         180 hits
  Availability:		      100.00 %
  Elapsed time:		        1.63 secs
  Data transferred:	        0.32 MB
  Response time:		        0.21 secs
  Transaction rate:	      110.43 trans/sec
  Throughput:		        0.19 MB/sec
  Concurrency:		       22.77
  Successful transactions:         180
  Failed transactions:	           0
  Longest transaction:	        0.68
  Shortest transaction:	        0.1


for tests by tsung go in directory ~/.tsung check file tsung.xml and run:

sudo tsung start

for graphic results copy file /usr/lib/tsung/bin/tsung_stats.pl or ~/tsung_stats.pl for example
into ~/.tsung/log/20160722-1241 where is file tsung.log and run:

sudo perl tsung_stats.pl




