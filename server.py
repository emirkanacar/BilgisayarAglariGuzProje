import socket
import sys

'''
    Sunucumuzun bilgilerini tuttuğumuz yer.
    Ekstra olarak kontrolcününde mac adresini tutuyoruz.
'''

serverIp = "10.0.0.1"
serverMac = "80:38:a8:35:73:db"
controllerMac = "cb:5e:15:78:db:8b"

'''
    Şimdi sunucumuzu açtıktan sonra hangi cliente mesaj gönderceğimizi bilmeliyiz.
    Bu yüzden router bilgilerini tuttuğumuz bir liste oluşturduk.
'''

allClients = {
    "client1": {
        "clientAddress": "10.1.1.1",
        "clientPort": 2100,
        "clientOnline": False,
        "clientMacAddress": "90:e1:6e:a5:13:ea"
    },
    "client2": {
        "clientAddress": "10.1.1.2",
        "clientPort": 2110,
        "clientOnline": False,
        "clientMacAddress": "86:81:3e:a9:46:f2"
    },
    "client3": {
        "clientAddress": "10.1.1.3",
        "clientPort": 2200,
        "clientOnline": False,
        "clientMacAddress": "2b:37:92:21:25:e5"
    }
}

onlineClients = []

'''
    checkOnlineClients()  
    Burdaki fonksiyonumuz yukardaki client listesini kullanarak online durumunu denetliyor.
    Basitçe for döngüsüne sokup online değiller ise socket oluşturuyoruz.
    Bu geçici soket sayesinde bağlanıp ve bağlantının başarılı olduğunu anlayınca online durumunu değiştiriyoruz.
    Sonra soketimizi  kapatıp ekrana "client1 aktif" şeklinde yazı bastırıyoruz.
'''


def checkOnlineClients():
    for key in allClients.keys():
        if not allClients[key]["clientOnline"]:

            socketSend = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            try:
                socketSend.connect(('localhost', allClients[key]["clientPort"]))
                allClients[key]["clientOnline"] = True
                print(key, "aktif.")
            except socket.error as exc:
                print(key, "pasif.")

            socketSend.close()
        else:
            print(key, "pasif.")

'''
    updateOnlineRouters()
    metodu ile yukarıda kontrol ettiğimiz routerleri yeni bir arraye atıyoruz.
    Sebebi ise daha rahat işlem yapmak.
    İçerideki listeyi önceki kalıntıları temizlemek için yapıyoruz.
'''

def updateOnlineRouters():
    onlineClients.clear()

    for key in allClients.keys():
        if allClients[key]["clientOnline"]:
            onlineClients.append(allClients[key])

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

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("localhost", 8000))
server.listen()

'''
    Burada .accept() metodu ile gelen bağlantıları kabul ediyoruz.
    .accept metodu bize bir array döndürüyor.
    [0] => Bağlantı bilgileri
    [1] => Bağlantı yapanın adres bilgileri
    [1][0] => Ip Adresi
    [1][1] => Port
'''

connection, address = server.accept()

'''
    Gelen bağlantı geçerli olana kadar sonsuz döngüye sokuyoruz.
    Gelen bağlantı geçerli olduğunda döngüyü kapatıyoruz.
'''
while True:
    if connection is not None:
        break

'''
    Kontrolcü bağlantısı geçerli olduğunda kullanıcılarımızı denetleyen fonksiyonları denetliyoruz.
'''

print("Kontrolcü bağlantısı başarılı!")
print("Kullanıcı bağlantıları kontrol ediliyor...")
checkOnlineClients()
updateOnlineRouters()

'''
    Sonsuz döngüye sokarak burda gelen bağlantıdaki portu denetliyoruz.
    Gelen bağlantıdaki port kontrolcü portumuzla eşleşiyorsa işlemlere başlıyoruz.
'''

while True:
    if address[1] == 1198:
        '''
            Burda online kullanıcı sayımız bir veya birden fazla ise işlemlere başlıyoruz.
            Normalde arrayler 0 dan başladığı için Kullanıcı0 yazdırmak mantıksız olcacğı için
            indis değerimizin bir fazlası olarak Kullanıcı1 yazdırıyoruz.
            [0] => Kullanıcı1
            [1] => Kullanıcı2
            [2] => Kullanıcı3
        '''
        if len(onlineClients) > 0:
            print("-Kullanıcılar-")
            for clientIndex, client in enumerate(onlineClients):
                print("{}-) {}".format((clientIndex+1), "Kullanıcı" + str(clientIndex+1)))

            '''
                Burda kullanıcıdan hangi kullanıcıya mesaj göndermesi isteyeceğini seçtiriyoruz.
                try except ile gelen verini int olup olmadığımı kontrol ediyoruz.
            '''

            try:
                selectedClient = int(input("Mesaj gönderceğiniz kullanıcı seçin: "))
            except ValueError:
                print("Lütfen Geçerli bir değer girin!")
                break

            '''
                Kullanıcımızdan bir mesaj istiyoruz.
                Bu mesaj boş bir değerse None ile değiştiriyoruz.
                Bunun amacı ise ilerde paketi parçalarken bir sorun çıkmasını önlemek için.
            '''
            getMessage = input("Mesajınızı girin: ")

            if getMessage == '':
                getMessage = "None"

            '''
                Şimdi paketimizi oluşturmaya başlıyoruz.
                IPHeader kısmında Gönderici-Alıcı mantığı ile oluşturuyoruz.
                Örnek: 192.168.1.1-192.168.1.20:4000
                
                MacHeader kısmında Gönderici-Alıcı mantığı ile oluşturuyoruz.
                Örnek: DF:ER:3D:4T:QW-WE:R3:T5 Şeklinde
                
                Paketimiz artık: MacHeader|IPHeader|Paket
                şeklinde oluştu.
                
                Paketimizi gelen bağlantıya .send() metodu ile gönderiyoruz.
                Burda oluşturuduğumuz paketi byte tipinde gönderiyoruz ve UTF-8 formatında gönderiyoruz.
            '''

            try:
                ipHeader = serverIp + "-" + onlineClients[selectedClient - 1]["clientAddress"] + ":" + str(
                onlineClients[selectedClient - 1]["clientPort"])
                ethernetHeader = serverMac + "-" + onlineClients[selectedClient - 1]["clientMacAddress"]
                packet = ethernetHeader + "|" + ipHeader + "|" + getMessage
                connection.send(bytes(packet, "UTF-8"))
            except:
                print("Geçerli client değeri girin!")

        else:
            print("Tüm kullanıcılar pasif!")
            print("Sunucu kapatılıyor!")
            server.close()
            connection.close()
            sys.exit(-1)
