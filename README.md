Initially a straight-up port of the old Perl [ISS-RT tools](https://github.com/kraigu/ISS-RT) to Python.

Requires python3.

Requires the [python-rt module](https://github.com/CZ-NIC/python-rt). Built and tested against 1.0.9.

Some functionality (RTIR) requires RT 4.4 with an updated version of RTIR, due to the way incidents queues work. 

Requires a .rtrcp file in your home directory as such:

```
[rt]
username=yourusername
hostname=yourrtinstance
password=guessme
```

TODO
----

* Pretty print function for individual tickets?

License
-------

BSD-new. Original author Mike Patterson <mike.patterson@uwaterloo.ca> for the University of Waterloo, 2016-2018.
