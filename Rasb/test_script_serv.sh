while true; do echo "({temperature:$((20+RANDOM%30))},{light:$((RANDOM%1000))},{press:$((900+RANDOM%200))})" | nc 127.0.0.1 55555; sleep 10; done > /dev/null 2>&1
