1.
    a) Rulati (SI INTELEGETI) example_producer.py si example_consumer.py.

       object_socket.py, example_producer.py si example_consumer.py trebuie sa fie in acelasi folder.

       Atentie sa aveti fisierul .mp4 in locatia mentionata in example_producer.py linia 8.
       ("." se refera la folderul de unde rulati example_producer.py)

    b) Veti observa ca cele 2 fisiere de mai sus nu folosesc socketuri in mod direct.
       Ele folosesc object_socket.py. Acesta este un mic library creat pentru a va oferi experienta de
       a lucra cu cod complet si functional dar scris de altcineva (in cazul aceasta de catre noi) care 
	   poate nu mai lucreaza in aceasi companie asa ca nu va poate raspunde la eventuale intrebari.

       Adaugati documentatie functiilor din object_socket.py (cautati Google documentation style pentry python)
       Evident pentru aceasta cerinta va trebui sa cititi si intelegeti object_socket.py.

2. Folositi object_socket.py (si exemplele example_producer.py si example_consumer.py) pentru a
   face codul de la acest laborator (codul de lane detection) sa citeasca fisierul .mp4 intr-un
   program python, care sa trimita fiecare frame la alt program python care va face procesarea.

   Cu alte cuvinte veti avea un fisier unde veti face video.read() si un altul unde va fi tot
   algoritmul de lane detection. Citirea si procesarea video-ului se vor face in 2 fisiere separate.