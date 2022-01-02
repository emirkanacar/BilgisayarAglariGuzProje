import socket

routerDetails = {
    "routerUUID": "46d1012a-bce4-40b9-96e4-8a2a58a526cc",
    "packetCapacity": 100,
    "currentLoadBuffer": 0,
    "packetMissRate": 10,
    "isOnline": False,
    "routerAddress": "10.0.1.3",
    "routerReceivePort": 1220,
    "routerSendPort": 1221,
    "routerMacAddress": "ab:bb:06:b3:8a:17"
}

router = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
router.bind(('localhost', routerDetails["routerReceivePort"]))

routerSend = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
routerSend.bind(('localhost', routerDetails["routerSendPort"]))

router.listen(4)

while True:
    connection, address = router.accept()

    if connection is not None:
        receivedMessage = connection.recv(1024)
        if receivedMessage != b'':
            decodeMessage = receivedMessage.decode("UTF-8")
            splitMessage = decodeMessage.split('|')
            splitMessage = [x for x in splitMessage if x]

            macHeader = splitMessage[0]
            ipHeader = splitMessage[1]
            routePathHeader = splitMessage[2]
            splitRouteHeader = routePathHeader.split('-')
            routeIpHeader = splitRouteHeader[1][4:]
            routeMacHeader = splitRouteHeader[0][4:]
            splitIpHeader = routeIpHeader.split(',')
            splitMacHeader = routeMacHeader.split(',')
            selectedRouterIndex = 0
            for sRouterIndex, sRouter in enumerate(splitIpHeader):
                if sRouter == str(routerDetails["routerAddress"] + ":" + str(routerDetails["routerReceivePort"])):
                    selectedRouterIndex = sRouterIndex

            if int(selectedRouterIndex) != int(len(splitIpHeader) - 1):
                selectedRouterIndex = selectedRouterIndex + 1

            selectedIpSplit = splitIpHeader[selectedRouterIndex].split(':')
            selectedIp = selectedIpSplit[0]
            selectedPort = selectedIpSplit[1]

            fullHeader = "|" + routerDetails["routerMacAddress"] + "-" + splitMacHeader[selectedRouterIndex] + "|"
            fullHeader = fullHeader + routerDetails["routerAddress"] + "-" + selectedIp + "|"
            fullHeader = fullHeader + splitRouteHeader[0] + "-" + splitRouteHeader[1] + "|"
            messagePacket = fullHeader + splitMessage[-1]

            routerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                routerSocket.connect(('localhost', int(selectedPort)))
                routerSocket.send(bytes(messagePacket, "UTF-8"))
                routerSocket.shutdown(0)
            except socket.error:
                print(socket.error)

            print("----------------")
            print("Message received")
            print("Source IP:", routerDetails["routerAddress"])
            print("Destination IP:", selectedIp)
            print("Source MAC:", routerDetails["routerMacAddress"])
            print("Destination MAC:", splitMacHeader[selectedRouterIndex])
            print("Message:", splitMessage[-1])
            print("----------------")

            connection.close()
    else:
        print("Bağlantı gelmedi")
