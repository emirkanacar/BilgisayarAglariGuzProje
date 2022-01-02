import socket

'''
    Client bilgilerimizi tutuyoruz.
'''

clientDetails = {
    "clientAddress": "10.1.1.2",
    "clientPort": 2110,
    "clientOnline": False,
    "clientMacAddress": "86:81:3e:a9:46:f2"
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

clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
clientSocket.bind(('localhost', clientDetails["clientPort"]))

clientSocket.listen(4)

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
    connection, address = clientSocket.accept()

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
            splitIPHeader = ipHeader.split(',')
            splitMACHeader = macHeader.split(',')

            print("----------------")
            print("Mesaj geldi! Detaylar:")
            print("Gönderen IP:", splitIPHeader[int(len(splitIPHeader) - 2)].split('-')[0])
            print("Gönderen MAC:", splitMACHeader[int(len(splitMACHeader) - 2)].split('-')[0])
            print("Mesaj:", splitMessage[-1])
            print("----------------")
            connection.close()
    else:
        print("Bağlantı koptu!")