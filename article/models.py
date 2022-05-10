from django.db import models
from ckeditor.fields import RichTextField

class Article(models.Model):
    author = models.ForeignKey("auth.User",on_delete=models.CASCADE,verbose_name="Yazar") #Makalenin yazarı için bir foreign key belirle ve yazar silindiği durumda tüm makalelerini silmek için cascade yap.
    title = models.CharField(max_length=200,verbose_name="Başlık")
    content = RichTextField(verbose_name="Açıklama")
    created_date = models.DateField(auto_now_add=True,verbose_name="Oluşturulma Tarihi")#Makale oluşturulduğu an oto tarih ata
    etkinlik_poster = models.FileField(blank=True,null=True,verbose_name="Poster")
    etkinlik_tarihi = models.DateField(blank=True,null=True,verbose_name="Etkinlik Tarihi")
    goster = models.BooleanField(default=True,verbose_name="Ana Sayfada Göster")
    def __str__(self): #admin panelindeki menüde article1 yerine başlıgı gösterme
        return self.title
    class Meta:
        verbose_name = 'Etkinlik'
        verbose_name_plural = 'Etkinlikler'
        ordering = ['-id']

class Katilimci(models.Model):
    tc_no = models.IntegerField(primary_key=True,verbose_name="TC Kimlik No")
    etkinlik = models.CharField(max_length=250,blank=True,verbose_name="Etkinlik")
    isim = models.CharField(max_length=50,verbose_name="İsim")
    soy_isim = models.CharField(max_length=50,verbose_name="Soy İsim")
    email = models.EmailField(max_length=50,verbose_name="Email")
    class Meta:
        ordering = ['-tc_no']

class Sertifikalar(models.Model):
    etkinlik_id = models.IntegerField(primary_key=True,verbose_name="Etkinlik ID")
    sertifika = models.FileField(blank=True,null=True,verbose_name="Sertifika")
    kordinat_isim = models.CharField(max_length=50,verbose_name="Kordinat İsim")
    kordinat_tarih = models.CharField(max_length=50,verbose_name="Kordinat Tarih")
    kordinat_qr = models.CharField(max_length=50,verbose_name="Kordinat QR")
    ornek_sertifika = models.FileField(blank=True,null=True,verbose_name="Örnek Sertifika")
    class Meta:
        ordering = ['-etkinlik_id']

class VeritabaniSertifikalar(models.Model):
    sertifika_id=models.IntegerField(primary_key=True,verbose_name="Sertifika ID")
    sertifika_etkinlik_id=models.IntegerField(blank=True,null=True,verbose_name="Etkinlik ID")
    katilimci_email=models.EmailField(blank=True,null=True,max_length=50,verbose_name="Email")
    katilimci_tc=models.IntegerField(blank=True,null=True,verbose_name="TC Kimlik No")
    sertifika_mevcut=models.BooleanField(blank=True,null=True)
    ad_soyad = models.CharField(blank=True,null=True,max_length=100,verbose_name="Ad Soyad")
    class Meta:
        ordering = ['-sertifika_id']


