INT_NAME=$1
INT_IP=$2

ip tuntap add dev $INT_NAME mode tun
ip addr add $INT_IP dev tun0
ip link set dev $INT_NAME up
