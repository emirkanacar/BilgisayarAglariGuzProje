import random
import socket
import sys
import time

'''
Burda değişken tanımlamarını yaptık
Kontrolcünün iletişim portlarını, sabit bir ip adresini ve mac adresini belirledik.
İçeride işimize yarayacak diye kontrolcunun içinde bir zaman değişkeni tuttuk.

AF_INET: TCP ve UDP için IPv4 protokolleri
SOCK_STREAM: TCP bağlantı tipi

'''

currentOnlineRouters = []
controllerSendPORT = 1199
controllerReceivePORT = 1198
controllerMac = "cb:5e:15:78:db:8b"
controllerIp = "10.1.0.0"
lastBufferTime = time.time()

'''
Burdaki değişken ana sunucu ile haberleşmemizi sağlayan ip ve portu içeriyor
'''
mainServer = ("localhost", 8000)

'''
Tüm router bilgilerini bir objede tutarak aslında avantaj elde ediyoruz.
Amacımız tüm routerlerı kontrol etmek olduğu için tüm router bilgilerine ihtiyacımız var.
Tek bir merkezde toplamak kullanılabilirlik açısından daha avantajlı
Yapısal olarakda routera özel bir UUID değeri, paket kapasitesi, şuan kaç paket tuttuğu ve drop atma yüzdesini gösteriyor.
Routerlerin ip adresini, portlarını ve router online durumunu tutuyoruz.
'''

allRouters = {
    "router1": {
        "routerUUID": "14b5393b-a107-4144-85b7-465a20e9a390",
        "packetCapacity": 100,
        "currentLoadBuffer": 0,
        "packetMissRate": 5,
        "isOnline": False,
        "routerAddress": "10.0.1.1",
        "routerReceivePort": 1200,
        "routerSendPort": 1201,
        "routerMacAddress": "0c:f6:fd:10:0f:42"
    },
    "router2": {
        "routerUUID": "ac75dfbb-997c-4311-bf3c-3eca6ae6a252",
        "packetCapacity": 100,
        "currentLoadBuffer": 0,
        "packetMissRate": 5,
        "isOnline": False,
        "routerAddress": "10.0.1.2",
        "routerReceivePort": 1210,
        "routerSendPort": 1211,
        "routerMacAddress": "3a:54:02:5f:6b:2a"
    },
    "router3": {
        "routerUUID": "46d1012a-bce4-40b9-96e4-8a2a58a526cc",
        "packetCapacity": 100,
        "currentLoadBuffer": 0,
        "packetMissRate": 10,
        "isOnline": False,
        "routerAddress": "10.0.1.3",
        "routerReceivePort": 1220,
        "routerSendPort": 1221,
        "routerMacAddress": "ab:bb:06:b3:8a:17"
    },
    "router4": {
        "routerUUID": "a3851842-dd17-4bfa-afdc-b8344391bd6d",
        "packetCapacity": 100,
        "currentLoadBuffer": 0,
        "packetMissRate": 5,
        "isOnline": False,
        "routerAddress": "10.0.1.4",
        "routerReceivePort": 1230,
        "routerSendPort": 1231,
        "routerMacAddress": "62:af:50:77:eb:a0"
    },
    "router5": {
        "routerUUID": "5fa8597c-8c8a-445f-a4c2-278c444ef13c",
        "packetCapacity": 100,
        "currentLoadBuffer": 0,
        "packetMissRate": 5,
        "isOnline": False,
        "routerAddress": "10.0.1.5",
        "routerReceivePort": 1240,
        "routerSendPort": 1241,
        "routerMacAddress": "ef:b7:71:cf:89:95"
    },
    "router6": {
        "routerUUID": "05aa7ddb-92b5-454f-a88e-3e4a66832025",
        "packetCapacity": 100,
        "currentLoadBuffer": 0,
        "packetMissRate": 5,
        "isOnline": False,
        "routerAddress": "10.0.1.6",
        "routerReceivePort": 1250,
        "routerSendPort": 1251,
        "routerMacAddress": "47:4b:00:48:f5:49"
    },
    "router7": {
        "routerUUID": "a9ebb0da-1e03-4f1f-8a40-e457f90c1bbb",
        "packetCapacity": 100,
        "currentLoadBuffer": 0,
        "packetMissRate": 5,
        "isOnline": False,
        "routerAddress": "10.0.1.7",
        "routerReceivePort": 1260,
        "routerSendPort": 1261,
        "routerMacAddress": "44:3d:d9:fc:c4:5f"
    },
    "router8": {
        "routerUUID": "196a092f-3709-4690-b56f-d597cc2cd287",
        "packetCapacity": 100,
        "currentLoadBuffer": 0,
        "packetMissRate": 5,
        "isOnline": False,
        "routerAddress": "10.0.1.8",
        "routerReceivePort": 1270,
        "routerSendPort": 1271,
        "routerMacAddress": "d0:40:70:48:5d:cf"
    }
}

'''
    connectAllRouters()
    Bu fonksiyonda tüm routerlara bağlanıp online olup olmadığını anlıyoruz.
    Online ise isOnline değişkenini True olarak değiştiriyoruz.
'''

def connectAllRouters():
    for key in allRouters.keys():
        if not allRouters[key]["isOnline"]:
            socketSend = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                socketSend.connect(('localhost', allRouters[key]["routerReceivePort"]))
                allRouters[key]["isOnline"] = True
                print(key, "router has online.")
            except socket.error as exc:
                print(key, "router has been offline.")
            socketSend.close()
        else:
            print(key, "router online.")


'''
    updateOnlineRouters()
    Bu fonksiyonda isOnline True olan routerleri alıp currentOnlineRouters arrayine ekliyoruz.
'''
def updateOnlineRouters():
    currentOnlineRouters.clear()

    for key in allRouters.keys():
        if allRouters[key]["isOnline"]:
            currentOnlineRouters.append(allRouters[key])

'''
    routerSchemaGenerator()
    n değişkeni düğüm sayısını söylüyor.
    Düğüm sayısana göre belirli bir pattern oluşturuyoruz.
    Bu düğümlerin birbirine bağlı olup olmadığınıda hesaplıyoruz.
    Düğümler 2-1-2-1 şeklinde ilerleyeceği için bununda büyüklüğünü tutuyoruz ilerde paket iletirken rahatlık sağlasın diye.
'''


'''
    routerSchemaGenerator()
    Bu fonksiyon benzersiz ulaşım patternini oluşturuyor.
    İlk başta routerData objectini tanımlayıp router kada obje oluşturucak.
    Patterndeki her bir sütun için width değeri bir artıyor.
'''
def routerSchemaGenerator(n):
    routerData = {
        "nodes": n,
        "width": 0,
        "routerNodes": []
    }
    width = 0
    nodeId = 1

    '''      
        Eğer router sayısı 1 ve 2 olursa manuel olarak oluşturuluyor.
        Eğer router sayısı 2 den fazla ise algoritma devreye girip kendi kendine patterini oluşturuyor.
        0: Server
        n+1: Client
    '''

    if n == 1:
        routerData["routerNodes"].append({"nodeId": 1, "pairedNodes": "0,2"})
        width = width + 1
    elif n == 2:
        routerData["routerNodes"].append({"nodeId": 1, "pairedNodes": "0,2"})
        routerData["routerNodes"].append({"nodeId": 2, "pairedNodes": "1,3"})
        width = width + 2
    else:
        '''
            Burda ise herşey otonom gerçekleşiyor. İlk başta algoritma router sayısını kalansız olarak 3 e bölüyor.
            Bölümün amacı algoritma router düğümlerini 3'er 3'er oluşturuyor.
            Geri kalan düğümler ise total router sayısından 3'lü düğüm sayısının farkı diff değişkenine aktarılıyor.
            
        '''
        tempPatrn = n // 3
        diff = n - (tempPatrn * 3)

        '''
            3'lü pattern sayısı birden fazla ise for döngüsü ile otomatik oluşturuluyor.
            Sadece bir tane 3lü node var ise manuel oluşturuluyor.
        '''
        if tempPatrn > 1:
            '''
                Burda 3'lü pattern sayısı kadar for döngüsü dönüyor.
                1.Düğüm en üstte kalıyor.
                2.Düğüm ortada kalıyor.
                3.Düğüm en altta kalıyor.
                
                Örnek 7 düğümlü bir pattern oluşturalım.
                2 Kez for döngüsü olacak.
                
                1.For döngüsü
                    - 1.Düğüm Koşulları, Düğümler:
                        1 - Şimdi 1-3 = -2 olduğundan, -2.node yok bu yüzden 0 alıyoruz. Sebebi ise 0'ı server olarak görüyoruz altında kalanları server olarak alıyoruz.
                            Eğer değer - değilde + olarak geliyorsa düğüm + 3 olarak alıyoruz.
                        2 - Her zaman 3'lü düğümde 1. düğümün 2 fazlası olcağından sabit bir olasılık olarak kabul ediyoruz.
                        3 - 1.düğümdeki gibi kontrol sağlayıp aynı koşulları sağlıyoruz.
                        
                    - 2.Düğüm Koşulları, Düğümler:
                        1 - Şimdi 1-3 = -2 olduğundan, -2.node yok bu yüzden 0 alıyoruz. Sebebi ise 0'ı server olarak görüyoruz altında kalanları server olarak alıyoruz.
                            Eğer değer - değilde + olarak geliyorsa düğüm + 3 olarak alıyoruz.
                        2 - Her zaman 3'lü düğümde 1. düğümün 1 fazlası olcağından sabit bir olasılık olarak kabul ediyoruz.
                        3 - 1.düğümdeki gibi kontrol sağlayıp aynı koşulları sağlıyoruz.
                        
                    - 3.Düğüm Koşulları, Düğümler:
                        1 - Düğümün 1 eksiği alıyoruz.
                        2 - Düğümün 2 eksiğini alıyoruz      Burdaki 3 olasılık sabit olasılıktır.
                        3 - Düğümün 1 fazlasını alıyoruz.
                        4 - Düğümün 2 fazlası Router Sayısı + 2 sayısından büyük veya eşit olursa boş değer dönüyor. 
                            Koşul sağlanmazsa düğümün 2 fazlası sağlanır.
                            
                2.For döngüsü
                    - 1.Düğüm Koşulları, Düğümler:
                        1 - Şimdi 1-3 = -2 olduğundan, -2.node yok bu yüzden 0 alıyoruz. Sebebi ise 0'ı server olarak görüyoruz altında kalanları server olarak alıyoruz.
                            Eğer değer - değilde + olarak geliyorsa düğüm + 3 olarak alıyoruz.
                        2 - Her zaman 3'lü düğümde 1. düğümün 2 fazlası olcağından sabit bir olasılık olarak kabul ediyoruz.
                        3 - 1.düğümdeki gibi kontrol sağlayıp aynı koşulları sağlıyoruz.
                        
                    - 2.Düğüm Koşulları, Düğümler:
                        1 - Şimdi 1-3 = -2 olduğundan, -2.node yok bu yüzden 0 alıyoruz. Sebebi ise 0'ı server olarak görüyoruz altında kalanları server olarak alıyoruz.
                            Eğer değer - değilde + olarak geliyorsa düğüm + 3 olarak alıyoruz.
                        2 - Her zaman 3'lü düğümde 1. düğümün 1 fazlası olcağından sabit bir olasılık olarak kabul ediyoruz.
                        3 - 1.düğümdeki gibi kontrol sağlayıp aynı koşulları sağlıyoruz.
                        
                    - 3.Düğüm Koşulları, Düğümler:
                        1 - Düğümün 1 eksiği alıyoruz.
                        2 - Düğümün 2 eksiğini alıyoruz      Burdaki 3 olasılık sabit olasılıktır.
                        3 - Düğümün 1 fazlasını alıyoruz.
                        4 - Düğümün 2 fazlası Router Sayısı + 2 sayısından büyük veya eşit olursa boş değer dönüyor. 
                            Koşul sağlanmazsa düğümün 2 fazlası sağlanır.
                            
                6 Tane node oluşturduk. Geriye bir düğüm kaldı. Bu düğümüde manuel oluşturucaz.
                Son düğüm ise bir önceki düğüm ve client arasında seri bağlı olacağından şuanki düğüm numarasının 1 eksik ve fazlasına bağlı olur
            '''
            for x in range(0, tempPatrn, +1):
                routerData["routerNodes"].append({"nodeId": nodeId, "pairedNodes": "{},{},{}".format( (0 if nodeId - 3 < 1 else nodeId - 3), (nodeId + 2), (nodeId + 3 if nodeId + 3 < n else nodeId - 1))})
                nodeId = nodeId + 1
                routerData["routerNodes"].append({"nodeId": nodeId, "pairedNodes": "{},{},{}".format( (0 if nodeId - 3 < 1 else nodeId - 3), (nodeId + 1), (nodeId + 3 if nodeId + 3 < n else nodeId - 2) )})
                nodeId = nodeId + 1
                routerData["routerNodes"].append({"nodeId": nodeId, "pairedNodes": "{},{},{},{}".format((nodeId - 1), (nodeId - 2), (nodeId + 1), (nodeId + 2 if nodeId + 2 < n + 1 else ''))})
                nodeId = nodeId + 1
                width = width + 2
        else:
            routerData["routerNodes"].append({"nodeId": nodeId, "pairedNodes": "0,{},{}".format((nodeId + 2), (nodeId + 3 if n > 4 else ''))})
            nodeId = nodeId + 1
            routerData["routerNodes"].append({"nodeId": nodeId, "pairedNodes": "0,{},{}".format((nodeId + 1), (nodeId + 3 if n > 4 else ''))})
            nodeId = nodeId + 1
            routerData["routerNodes"].append({"nodeId": nodeId, "pairedNodes": "{},{},{},{}".format((nodeId - 2), (nodeId - 1), (nodeId + 1), (nodeId + 2 if n == 5 else ''))})
            nodeId = nodeId + 1
            width = width + 2


        if diff == 2:
            routerData["routerNodes"].append({"nodeId": nodeId, "pairedNodes": "{},{},{}".format((nodeId - 3), (nodeId - 1), (nodeId + 2))})
            nodeId = nodeId + 1
            width = width + 1
            routerData["routerNodes"].append({"nodeId": nodeId, "pairedNodes": "{},{},{}".format((nodeId - 3), (nodeId - 2), (nodeId + 1))})
            nodeId = nodeId + 1
            width = width + 1
        elif diff == 1:
            routerData["routerNodes"].append({"nodeId": nodeId, "pairedNodes": "{},{}".format((nodeId - 1),(nodeId + 1))})
            nodeId = nodeId + 1
            width = width + 1

    routerData["width"] = width

    '''
        Yukarda oluşturduğumuz düğümlerde ortada kalan düğümler 4 tane düğüme bağlanmak zorunda kalıyor.
        Bu durumun istisnası oluyor bu yüzden 3 düğüm bağlanabiliyor.
        Bu durumundan dolayı örnek "2,4,5," gibi ifade oluşuyor.
        Virgülden dolayı ifadeyi split ile bölerken sıkıntı yaşayabiliyoruz.
        Bu yüzden burda sonda virgül olan değerleri sonunda virgül olmayan versiyonu ile değiştiriyoruz.
    '''

    for nodeIndex, node in enumerate(routerData["routerNodes"]):
        filteredString = routerData["routerNodes"][nodeIndex]["pairedNodes"][:-1] if routerData["routerNodes"][nodeIndex]["pairedNodes"][-1] == ',' else routerData["routerNodes"][nodeIndex]["pairedNodes"]
        routerData["routerNodes"][nodeIndex]["pairedNodes"] = filteredString

    return routerData

'''
    Oluşturduğumuz router düğüm patternleri ile şuanki routerlerimizi eşleştiriyoruz.Örnek:
        - 1 = router1
        - 2 = router2
        - 3 = router3
        
    Bu şekilde tek bir değişkende tutup daha rahat işlem yapabiliyoruz.
'''

def combineRouterNodes(routerSchema):
    for routerIndex, routerData in enumerate(currentOnlineRouters):
        routerSchema["routerNodes"][routerIndex]["routerData"] = routerData
    return routerSchema


'''
    Burdaki fonksiyon yukarda oluşturduğumuz değişkeni alarak routerlerin uygunluk durumuna göre uygun rota belirliyoruz.
    Her düğüm bağlı olduğu düğümlerin listesi alır. Bu listede tüm düğümlerin buffer kapasiteleri kontrol edilir.
    Bu kontrol sonucu uygun olan düğümler başka listeye atanır.
    Bu düğümler arasından rastgele birisi seçilerek yolun belirlendiği listeye atanır.
    Bir sonraki kontrolde ise en son düğüm alınıp yol listesinden yukardaki işlemler tekralanır.
    Bu işlem tekrarlanması routerSayısı+1 yani cliente kadar devam eder.
    Cliente ulaşıldıktan sonra rota yani yol döndürülür.
'''

def createRouterPath(routerSchema):
    nodeCount = len(routerSchema["routerNodes"])
    routerPath = {
        "message": "",
        "route": ""
    }

    routePath = []

    '''
        Burda router sayısı 1 veya 2 ise manuel olarak kontrol ediyoruz.
        Her routerin buffer kapasitesini kontrol edip ona göre yol belirlemesi yapıyor.
        
    '''

    if nodeCount == 1:
        if allRouters["router1"]["currentLoadBuffer"] >= allRouters["router1"]["packetCapacity"]:
            print("Router1 kapasitesi dolu")
        else:
            routePath.append(1)
            routePath.append(2)
    elif nodeCount == 2:
        if allRouters["router1"]["currentLoadBuffer"] >= allRouters["router1"]["packetCapacity"]:
            print("Router1 kapasitesi dolu")
        else:
            if allRouters["router2"]["currentLoadBuffer"] >= allRouters["router2"]["packetCapacity"]:
                print("Router2 kapasitesi dolu!")
            else:
                routePath.append(1)
                routePath.append(2)
                routePath.append(3)
    else:
        '''
            Eğer router sayısı 2 den büyükse burda ilk 2 router kontrol edilip uygunluk durumunu göre ikisinden birisi seçilir.
        '''
        if not allRouters["router1"]["currentLoadBuffer"] <= allRouters["router1"]["packetCapacity"]:
            print("Router1 dolu")
        elif not allRouters["router2"]["currentLoadBuffer"] <= allRouters["router2"]["packetCapacity"]:
            print("Router2 dolu")
        else:
            routePath.append(random.randint(1,2))

        '''
            Burdaki sütun sayısına göre yol belirliyoruz. 4 sütundan oluşuyorsa 4 aşamalı yol olacak.
        '''
        for _ in range(0, int(routerSchema["width"])):
            '''
                İlk iki routerdan birisi seçilmemişse döngüyü kırıyoruz.
            '''
            if len(routePath) > 0:
                '''
                    Şuanki düğümü router yolumuzdaki son düğüm olarak alıyoruz.
                    Düğümün tüm verilerini çekmek için routerSchemada ki indisine göre alıyoruz
                    Örnek 3.düğümde isek arraylerden 0 dan başladığı için 2.düğümü alıyoruz.
                    Sonra aldığımız veriden bağlı olduğu düğüm bilgisini alıyoruz.
                    Aldığımız düğüm verisi ',' karakteri ile bölüp arraye dönüştürüyoruz.
                '''
                currentPathNode = routePath[-1]

                try:
                    currentNode = routerSchema["routerNodes"][int(currentPathNode) - 1]
                except IndexError:
                    break
                splitNodes = currentNode["pairedNodes"].split(',')
                availableNodes = []

                '''
                    Eğer burda for döngüsünde başlangıç değerimiz router değerimizin bir fazlasına eşitse client olarak ekliyoruz.
                    elif de ise paket ileri yönlü olarak gideceği için kendi düğüm numarasından büyük düğüm numaralarını listeye atıyoruz.
                '''

                for sNode in splitNodes:
                    if sNode == nodeCount + 1:
                        routePath.append("Client")
                        break
                    elif int(sNode) > int(currentNode["nodeId"]):
                        availableNodes.append(sNode)

                ''' 
                    Bu döngüde olası düğüm listesindeki düğüm numaraları ile buffer kapasitelerini kontrol ediyoruz.
                    Buffer değeri dolu olanları listeden çıkarıyoruz. 
                '''
                for aNode in availableNodes:
                    routerId = "router" + str(aNode)
                    if allRouters[routerId]["currentLoadBuffer"] >= allRouters[routerId]["packetCapacity"]:
                        availableNodes.remove(int(aNode))

                '''
                    Olası düğüm listesindeki düğümler arasında rastgele seçim yapılarak yönlendiricilerin kullanacağı yol belirlenir.
                '''

                if len(availableNodes) > 0:
                    aLen = len(availableNodes)
                    randNode = random.randint(0, (aLen - 1))
                    routePath.append(availableNodes[randNode])
    return routePath

'''
    routerPathSendMessage()
    fonksiyonu içersine mesaj, router rotası ve paketin gideceği kullanıcının verilerini alıyor.
    Burda Ip Header, Mac Header ve mesaj birleştiriliyor.
    Pakete ekstra RIH(Route Ip Header) ve RMH(Route Mac Header) ekleniyor.
    Bunun en büyük sebebi ise kullanılan rotanın pakette saklanması ve paket her yönlendiriciye uğradığında
    bu headerlar sayesinde bir sonraki noktasını belirliyor.
    Bu headerlar ve mesaj birleştirilip paket oluşturuluyor.
    
    Oluşuturulan paket rotanın ilk noktasına gönderilmek için soket oluşturuluyor.
    Bu soket anlık geçici bir soket kullanıldıktan sonra kapatılıp siliniyor.
    Oluşturulan soket gidecek ilk noktaya bağlandıktan sonra paket soket araclığı ile gönderiliyor.
'''
def routerPathSendMessage(message, routerPath, clientDetails):
    '''
        RIH = Route Ip Header
        RMH = Route Mac Header
        İlk for döngüsünde ekli olan düğümlerin numarasıyla online olan yönlendiri eşleşiyor.
        Ip adresi RIH'a ekleniyor, mac adresi RMH'a ekleniyor.
        Ekstra olarak buffer'a bir ekleniyor.
    '''
    routeIPHeader = "RIH:"
    routeMACHeader = "RMH:"
    for router in routerPath:
        currentRouterId = "router" + str(router)
        currentRouter = allRouters[currentRouterId]
        allRouters[currentRouterId]["currentLoadBuffer"] = allRouters[currentRouterId]["currentLoadBuffer"] + 1
        routeIPHeader = routeIPHeader + currentRouter["routerAddress"] + ":" + str(currentRouter["routerReceivePort"]) + ","
        routeMACHeader = routeMACHeader + currentRouter["routerMacAddress"] + ","

    '''
        Paketin ilk gidecek noktasını belirlemek için rotadaki ilk düğümü alıp online olan yönlendirici ile eşleştirilip
        ip adresi, mac adresi ve portu alınıyor
    '''

    firstRouterId = "router" + str(routerPath[0])
    firstRouter = allRouters[firstRouterId]

    '''
        Burdaki sorunlardan birisi headerlara veri eklerken sonlarında ',' kalabiliyor.
        Buda split ederlen bize sorun çıkarabiliyor bu yüzden sonda ',' olan değerlerin sonundaki virgülü kaldırıyoruz.
    '''

    routeIPHeader = routeIPHeader[:-1] if routeIPHeader[-1] == "," else routeIPHeader
    routeMACHeader = routeMACHeader[:-1] if routeMACHeader[-1] == "," else routeMACHeader

    '''
        Rotada client yönlendirici sayısının bir fazlası şekilde tanımlanıyor.
        Örnek olarak 5 yönlendiricili rotada client numarası 6 olarak tanımlanıyor.
        6 olarak tanımlandığı için içinde yanlış bilgi tutabiliyor.
        Bu durumu düzeltmek için ufak bir hackleme işlemi yapıp dışardan aldığımız client verisini bu içerdeki client
        verileri ile değiştirip paket bilgisini düzenliyoruz.
    '''

    # Hack the route
    hackedIpHeaderSplit = routeIPHeader.split(',')
    hackedIpHeaderSplit[-1] = clientDetails[0]
    hackedMacHeaderSplit = routeMACHeader.split(',')
    hackedMacHeaderSplit[-1] = clientDetails[1]

    routeIPHeader = ",".join(hackedIpHeaderSplit)
    routeMACHeader = ",".join(hackedMacHeaderSplit)

    '''
        Header bilgilerini ve mesajı kullanarak bir paket oluşturuyoruz.
        Örnek paket |kontrolcüMac-routerMac|kontrolcüIp-routerIp|RMH|RIH|Mesaj
    '''

    fullHeader = "|" + controllerMac + "-" + firstRouter["routerMacAddress"] + "|"
    fullHeader = fullHeader + controllerIp + "-" + firstRouter["routerAddress"] + "|"
    fullHeader = fullHeader + routeMACHeader + "-" + routeIPHeader + "|"
    messagePacket = fullHeader + message

    ''' 
        Burda geçici bir soket tanımlayıp bunu ilk noktamızın portuna bağlıyoruz.
        Bağlantı gerçekleştikten sonra paketi yolluyoruz.
        Paket yollandıktan sonra soketimizi kapatıyoruz.
    '''

    routerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        routerSocket.connect(('localhost', firstRouter["routerReceivePort"]))
        routerSocket.send(bytes(messagePacket, "UTF-8"))
        routerSocket.shutdown(0)
    except socket.error:
        print(socket.error)


if __name__ == "__main__":
    '''
        Burda kontrolcü soketlerini oluşturuyoruz.
        Kontrolcüyü sunucuya bağlıyoruz.
    '''

    controller = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    controller.bind(("localhost", controllerReceivePORT))

    controllerSend = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    controllerSend.bind(("localhost", controllerSendPORT))

    controller.connect(mainServer)

    '''
        Burda yukarda kullandığımız online router denetleme fonksiyonlarını kullanıyoruz.
    '''
    connectAllRouters()
    updateOnlineRouters()

    while True:
        '''
            Burda kontrolcü ilk başlarken bir zaman değeri tutmuştuk.
            Bu değer ile şuanki zaman arasındaki fark 60 saniyeyi aşarsa tüm bufferleri temizliyoruz.
            Sonra değişkenin içindeki zamanı şuanki zamanla eşitleyip bir sonraki periyod için hazırlıyoruz.
        '''
        if time.time() - lastBufferTime >= 60:
            for router in currentOnlineRouters:
                router["currentLoadBuffer"] = 0
                print("Tüm buffer temizlendi!")
            lastBufferTime = time.time()

        '''
            Kontrolcüye gelen mesajları almak için .recv() fonksiyonunu kullanıyoruz.
            İçine girdiğimiz değerde mesajın buffer boyutu.
        '''
        receivedMessage = controller.recv(1024)


        '''
            Boş olan mesajı kontrol ediyoruz.
        '''
        if receivedMessage != b'':
            '''
                Gelen mesajı UTF-8 olarak derliyoruz.
                Gelen mesajı '|' karakteri ile split edip bölüyoruz.
                [0] => Mac Header
                [1] => Ip Header
                [2] => Gelen Mesaj
                
                Sunucudan gelen mesaj RIH ve RMH içermiyor sebebi ise sunucudan çıkan paket rota bilgisi içermiyor.
            '''
            decodeMessage = receivedMessage.decode("UTF-8")
            splitMessage = decodeMessage.split("|")
            macHeader = splitMessage[0]
            ipHeader = splitMessage[1]
            message = splitMessage[2]

            sourceMac = macHeader.split("-")[0]
            destinationMac = macHeader.split("-")[1]

            sourceIp = ipHeader.split("-")[0]
            destinationIp = ipHeader.split("-")[1]

            '''
                Burda gelen bilgilere göre mesajı parçalayıp ekrana yazdırıyoruz.
            '''

            print("----------------")
            print("Mesaj geldi! Detaylar:")
            print("Gönderen IP:", sourceIp)
            print("Alıcı IP:", destinationIp)
            print("Gönderen MAC:", sourceMac)
            print("Alıcı MAC:", destinationMac)
            print("Mesaj:", message)
            print("----------------")


            '''
                Online yönlendiri sayısını kontrol edip işlemimize devam ediyoruz.
                Yukarıda tanımladığımız metodları ana metodumuun içinde çağırıp istenilen veriye göre işlem yapıyoruz.
                
            '''
            if len(currentOnlineRouters) > 0:
                onlineRoutersCount = len(currentOnlineRouters)
                createRouteSchema = routerSchemaGenerator(onlineRoutersCount)
                combineRouterData = combineRouterNodes(createRouteSchema)
                routerPath = createRouterPath(combineRouterData)
                clientDetails = (destinationIp, destinationMac)
                routerPathSendMessage(message, routerPath, clientDetails)
                continue

            elif len(currentOnlineRouters) == 0:
                print("Tüm routerler pasif.")
        else:
            print("Sunucu bağlantısı koptu!")
            print("Kontrolcü kapatılıyor!")
            sys.exit(-1)