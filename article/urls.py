from django.contrib import admin
from django.urls import path

from . import views

app_name = "article"

urlpatterns = [
    path("dashboard/",views.dashboard,name="dashboard"),
    path("etkinlikekle/",views.addEtkinlik,name="addEtkinlik"),
    path("<int:id>",views.detay,name="detay"),
    path("update/<int:id>",views.update,name="update"),
    path("delete/<int:id>",views.delete,name="delete"),
    path("export/<int:id>",views.tablo_indir, name="tablo_indir"),
    path("tumkatilimcilar/",views.tumkatilimcilar, name="tumkatilimcilar"),
    path("sertifika/",views.sertifika, name="sertifika"),
    path("sertifikalar/",views.sertifikalar, name="sertifikalar"),
    path("sertifikapaneli/",views.sertifikapaneli, name="sertifikapaneli"),
    path("sertifikaolustur/<int:id>",views.sertifikaolustur, name="sertifikaolustur"),
    path("sertifikalistesi/<int:id>",views.sertifikalistesi, name="sertifikalistesi"),
    path("katilimciduzenle/<int:id>",views.katilimciduzenle, name="katilimciduzenle"),

]