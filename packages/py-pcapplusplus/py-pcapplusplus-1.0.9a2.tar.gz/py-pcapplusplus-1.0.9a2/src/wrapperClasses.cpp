#include "wrapperClasses.hpp"

#include <arpa/inet.h>
#include <net/if.h>
#include <ifaddrs.h>
#include <algorithm>
#include <iostream>
#include <RawPacket.h>
#include <PcapLiveDevice.h>
#include <PcapLiveDeviceList.h>
#include <NetworkUtils.h>
#include <nanobind/nanobind.h>

bool 
replaceLinkLayerWithFreshEthLayer(pcpp::Packet* packet, pcpp::MacAddress const& srcMac, pcpp::MacAddress const& dstMac)
{
    // replace first layer with clean Eth layer
    if(!packet->removeFirstLayer()) return false;
    if(!packet->insertLayer(nullptr, new pcpp::EthLayer(srcMac, dstMac, PCPP_ETHERTYPE_IP), true)) return false;

    packet->computeCalculateFields();
    return true;
}

int sendEthPackets(std::string const& ethInterface, std::vector<pcpp::Packet*>const& packets, std::string const& destAddr)
{
    pcpp::PcapLiveDevice* dev = pcpp::PcapLiveDeviceList::getInstance().getDeviceByName(ethInterface);
    if (!dev) {
        return 0;
    }

    if (!dev->open()) {
        return 0;
    }

    pcpp::MacAddress dstMac;
    if (pcpp::IPv4Address::isValidIPv4Address(destAddr)) {
        pcpp::IPv4Address destIp(destAddr);
        // send an ARP request to determine dst MAC address
        double arpResTO = 0;
        dstMac = pcpp::NetworkUtils::getInstance().getMacAddress(destIp, dev, arpResTO);
    }
    auto srcMac = dev->getMacAddress();

    int packetSent = 0;
    for (auto packet : packets) {
        if (replaceLinkLayerWithFreshEthLayer(packet, srcMac, dstMac)) {
            packetSent += dev->sendPacket(packet) ? 1 : 0;
        }
    }

    dev->close();
    return packetSent;
}


std::vector<pcpp::Packet>
sniffEth(std::string const& ethInterface, double timeoutSeconds)
{
    pcpp::PcapLiveDevice* dev = pcpp::PcapLiveDeviceList::getInstance().getDeviceByName(ethInterface);
    if (!dev) {
        nanobind::raise("Invalid interface provided");
    }

    if (!dev->open()) {
        nanobind::raise("Error opening pcap live device");
    }

    std::vector<pcpp::Packet> retPackets;
    pcpp::OnPacketArrivesStopBlocking cb = [&retPackets](pcpp::RawPacket* inPacket, pcpp::PcapLiveDevice* device, void*)->bool {
        retPackets.push_back(pcpp::Packet(inPacket));
        return false;
    };

    if (0 == dev->startCaptureBlockingMode(cb, nullptr, timeoutSeconds)) {
        dev->close();
        nanobind::raise("Error while capturing from device");
    }
    dev->close();
    return retPackets;
}

pcpp::IPAddress
getDefaultGateway(std::string const& ifName)
{
    // find interface name and index from IP address
	struct ifaddrs* addrs;
	getifaddrs(&addrs);
    pcpp::IPAddress ret_addr;
	for (struct ifaddrs* curAddr = addrs; curAddr != NULL; curAddr = curAddr->ifa_next)
	{
		if (curAddr->ifa_addr && (curAddr->ifa_flags & IFF_UP) && std::string(curAddr->ifa_name) == ifName)
		{
			if  (curAddr->ifa_addr->sa_family == AF_INET)
			{
				struct sockaddr_in* sockAddr = (struct sockaddr_in*)(curAddr->ifa_addr);
				char addrAsCharArr[32];
				inet_ntop(curAddr->ifa_addr->sa_family, (void *)&(sockAddr->sin_addr), addrAsCharArr, sizeof(addrAsCharArr));
				ret_addr = pcpp::IPAddress(addrAsCharArr);
			}
			else if (curAddr->ifa_addr->sa_family == AF_INET6)
			{
				struct sockaddr_in6* sockAddr = (struct sockaddr_in6*)(curAddr->ifa_addr);
				char addrAsCharArr[40];
				inet_ntop(curAddr->ifa_addr->sa_family, (void *)&(sockAddr->sin6_addr), addrAsCharArr, sizeof(addrAsCharArr));
				ret_addr = pcpp::IPAddress(addrAsCharArr);
			}
		}
	}
    freeifaddrs(addrs);
    if (ret_addr.isZero()) {
        nanobind::raise("Failed to find default gateway");
    }
    return ret_addr;
}

WrappedRawSocketDevice::WrappedRawSocketDevice(std::string const& ifName)
: m_rawSocket(nullptr)
, m_pcapDevice(nullptr)
{
    auto addr = getDefaultGateway(ifName);
    m_rawSocket = std::make_shared<pcpp::RawSocketDevice>(addr);
    if(!m_rawSocket->open()) {
        nanobind::raise("Failed to open Raw socket device with the provided interface ip");
    }
    m_pcapDevice = pcpp::PcapLiveDeviceList::getInstance().getDeviceByName(ifName);
    if (!m_pcapDevice) {
        nanobind::raise("Invalid interface provided");
    }

    if (!m_pcapDevice->open()) {
        nanobind::raise("Error opening pcap live device");
    }
}

WrappedRawSocketDevice::~WrappedRawSocketDevice()
{
    m_rawSocket->close();
    m_pcapDevice->close();
}

std::vector<pcpp::Packet> 
WrappedRawSocketDevice::sniff(double timeoutSeconds)
{
    std::vector<pcpp::Packet> retPackets;
    pcpp::OnPacketArrivesStopBlocking cb = [&retPackets](pcpp::RawPacket* inPacket, pcpp::PcapLiveDevice* device, void*)->bool {
        retPackets.push_back(pcpp::Packet(inPacket));
        return false;
    };

    if (0 == m_pcapDevice->startCaptureBlockingMode(cb, nullptr, timeoutSeconds)) {
        nanobind::raise("Error while capturing from device");
    }
    return retPackets;
}

pcpp::Packet*
WrappedRawSocketDevice::receivePacket(bool blocking, double timeoutSeconds)
{
    auto rawPacket = new pcpp::RawPacket();
    auto res = m_rawSocket->receivePacket(*rawPacket, blocking, timeoutSeconds);
    if (res == pcpp::RawSocketDevice::RecvPacketResult::RecvSuccess) {
        return new pcpp::Packet(rawPacket, true);
    }
    else {
        delete rawPacket;
        return nullptr;
    }
}

bool 
WrappedRawSocketDevice::sendPacket(pcpp::Packet const& packet)
{
    return m_rawSocket->sendPacket(packet.getRawPacket());
}   

int
WrappedRawSocketDevice::sendPackets(std::vector<pcpp::Packet>const& packets)
{
    int packetSent = 0;
    for (auto packet : packets) {
        packetSent += sendPacket(packet) ? 1 : 0;
    }
    return packetSent;
}