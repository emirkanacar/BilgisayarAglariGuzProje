import socket
'''
    Burda router bilgilerimizi tutuyoruz.
    Router bilgilerimizi tutma sebebimiz gelen paketti veriler ile kendi router bilgilerimizi eşleştirip
    daha  rahat işlem yapabilmek.
    Bilgilerimizde paket kapasitemiz, şuan kaç paket olduğu, online durumu ve router IP, Mac gibi bilgileri barındırıyoruz.
'''
routerDetails = {
    "routerUUID": "14b5393b-a107-4144-85b7-465a20e9a390",
    "packetCapacity": 100,
    "currentLoadBuffer": 0,
    "packetMissRate": 5,
    "isOnline": False,
    "routerAddress": "10.0.1.1",
    "routerReceivePort": 1200,
    "routerSendPort": 1201,
    "routerMacAddress": "0c:f6:fd:10:0f:42"
}

'''
    Burda sunucumuzun soketini oluşturuyoruz.
    Socketimiz içine iki tane değer alıyor.
    Değer açıklamaları:
        AF_INET: TCP ve UDP için IPv4 protokolleri
        SOCK_STREAM: TCP bağlantı tipi

    .bind() metodu ile sunucumuza ip adresini ve portunu veriyoruz.
    Bu sayede sunucumuz kendi ip adresini ve portunu biliyor.
    .listen() ile gelen bağlantıları dinliyoruz.
    Gelen bağlantılara göre işlem yapmamız gerekecek.
'''

router = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
router.bind(('localhost', routerDetails["routerReceivePort"]))

router.listen(4)

'''
    Burda sınırsız döngüde gelen bağlantıları .accept() metodu ile kabul ediyoruz.
    .accept() metodu bize bir array döndürüyor.
    [0] => Bağlantı bilgileri
    [1] => Bağlantı yapanın adres bilgileri
    [1][0] => Ip Adresi
    [1][1] => Port
    
    Bu bilgileri kullanarak işlemlerimize devam ediyoruz.
'''
while True:
    connection, address = router.accept()

    '''
        Bura bağlantının geçerli olup olmadığını kontrol ediyoruz.
        Eğer bağlantımız geçerli ise gelen mesajı denetliyoruz.
        Gelen mesajımız boş bir mesaj değil ise işlemlerimize devam ediyoruz.
    '''

    if connection is not None:
        receivedMessage = connection.recv(1024)
        if receivedMessage != b'':
            '''
                Gelen mesajımızı UTF-8 formatında decode ediyoruz.
                Şimdi gelen mesaj aslında paketimiz.
                Paketimizin şeması şu şekilde idi: MacHeader|IPHeader|RMH|RIH|Paket
                
                RIH = Route Ip Header
                RMH = Route Mac Header
                
                Bu paketteki bilgileri alıp daha rahat işlem yapmak için split metodu ile '|' karakterini bölüyoruz.
                Bazen bazı paketlerde sorun çıkabiliyor. Boş string elemanları olabiliyor.
                Bu sorunu kaldırmak içinde boş elemanları kaldırıyoruz.
            '''
            decodeMessage = receivedMessage.decode("UTF-8")
            splitMessage = decodeMessage.split('|')
            splitMessage = [x for x in splitMessage if x]

            '''
                Şimdi split ettiğimizde elimizde bir array var.
                [0] => Mac Header
                [1] => IP Header
                [2] => RIH Route IP Header
                [3] => RMH Route Mac Header
                [4] => Mesaj
                
                Bu bilgileri kullanarak paketimizi parçaladık.
                Artık elimizde rotanın IP şeması, mesaj ve gönderici-alıcı bilgileri bulunuyor.
            '''

            macHeader = splitMessage[0]
            ipHeader = splitMessage[1]
            routePathHeader = splitMessage[2]
            splitRouteHeader = routePathHeader.split('-')

            '''
                RIH veya RMH değerlerini alırken [4:] ifadesini kullandık.
                Bunun sebebi ise şu şekilde.
                Şimdi biz RIH:Ip Adresi şeklinde header kullanıyoruz.
                Ip adreslerini ayrıştırırken "RIH:" ifadesi engel teşkil ediyor o yüzden ilk 4 karakteri almıyoruz.
            '''

            routeIpHeader = splitRouteHeader[1][4:]
            routeMacHeader = splitRouteHeader[0][4:]
            splitIpHeader = routeIpHeader.split(',')
            splitMacHeader = routeMacHeader.split(',')

            '''
                RIH bloğundaki ip adresleri split edip parçalayacağımızı söylemiştik.
                RIH bloğundaki parçaladığımız ip bloğundan kendi ip adresimizi bulmamız lazım.
                Şöyle örnek ile açıklayalım durumu.
                Arraylerin indis değeri 0 dan başlar.
                Biz bloğu split ettiğimizde otomatik olarak bir arraye sahip oluyoruz.
                
                Bizim router ip adresimizin 192.168.1.100 olduğunu varsayalım
                RIH Ip arrayi:
                [0]: 192.168.1.3
                [1]: 192.168.1.47
                [2]: 192.168.1.100 = Eşleştik
                [3]: 192.168.1.107
                
                Şimdi eşleştikten sonra bir kontrol etmemiz gerekiyor çünkü şuan yönlendiricideyiz ve son eleman ile eşleşirsek
                demekki client bilgileri tutulmamış ve paketimiz tam hazırlanamamış.
                
                Şimdi birde indis numarasının bir fazlası her zaman bizim routerımıza erişecek basitçe bizim router0 diye
                routerimiz yok o yüzden [0] = router1 olcağı için indis sayısının bir fazlasını kabul ediyoruz.
                
                Şuan routerimizin sırasını aldık sonda olup olmadığını kontrol ettik.
                İndis sayısının bir fazlasını alarak bir sonraki gidecek yerin ip adresini ve portunu hazırlıyoruz.
            '''

            selectedRouterIndex = 0
            for sRouterIndex, sRouter in enumerate(splitIpHeader):
                if sRouter == str(routerDetails["routerAddress"] + ":" + str(routerDetails["routerReceivePort"])):
                    selectedRouterIndex = sRouterIndex

            if int(selectedRouterIndex) != int(len(splitIpHeader) - 1):
                selectedRouterIndex = selectedRouterIndex + 1

            selectedIpSplit = splitIpHeader[selectedRouterIndex].split(':')
            selectedIp = selectedIpSplit[0]
            selectedPort = selectedIpSplit[1]

            '''
                Header bilgilerini ve mesajı kullanarak bir paket oluşturuyoruz.
                Örnek paket |kontrolcüMac-routerMac|kontrolcüIp-routerIp|RMH|RIH|Mesaj
            '''

            fullHeader = "|" + routerDetails["routerMacAddress"] + "-" + splitMacHeader[selectedRouterIndex] + "|"
            fullHeader = fullHeader + routerDetails["routerAddress"] + "-" + selectedIp + "|"
            fullHeader = fullHeader + splitRouteHeader[0] + "-" + splitRouteHeader[1] + "|"
            messagePacket = fullHeader + splitMessage[-1]

            ''' 
                Burda geçici bir soket tanımlayıp bunu ilk noktamızın portuna bağlıyoruz.
                Bağlantı gerçekleştikten sonra paketi yolluyoruz.
                Paket yollandıktan sonra soketimizi kapatıyoruz.
            '''

            routerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                routerSocket.connect(('localhost', int(selectedPort)))
                routerSocket.send(bytes(messagePacket, "UTF-8"))
                routerSocket.shutdown(0)
            except socket.error:
                print(socket.error)

            print("----------------")
            print("Mesaj geldi! Detaylar:")
            print("Gönderen IP:", routerDetails["routerAddress"])
            print("Alıcı IP:", selectedIp)
            print("Gönderen MAC:", routerDetails["routerMacAddress"])
            print("Alıcı MAC:", splitMacHeader[selectedRouterIndex])
            print("Mesaj:", splitMessage[-1])
            print("----------------")

            connection.close()
    else:
        print("Bağlantı gelmedi")
