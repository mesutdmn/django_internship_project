
Projeyi yerel ağınızda çalıştırmak için ;

Gereki kütüphaneleri requirements.txt içerisinden otomatik olarak pip yardımıyla kurabilirsiniz.
```
pip install -r requirements.txt
```

Veri tabanını pythonu proje klasöründe çağırarak migrate ediniz;
```
python manage.py makemigrations
python manage.py migrate
```

Sisteme admin girişi yapabilmek için bir yönetici oluşturun;
```
python manage.py createsuperuser
```
Sisteminiz bu işlemlerden sonra tamamlanmış olacaktır. 
