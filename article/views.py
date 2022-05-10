import pandas as pd
from django.shortcuts import render,redirect,get_object_or_404
from .forms import ArticleForm, KatilimciForm,tc_kontrol,EtklinlikSec
from .models import Article,Katilimci,Sertifikalar,VeritabaniSertifikalar
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from django.http import HttpResponse
import xlwt
import urllib.parse
import cv2 as cv
from PIL  import ImageFont, ImageDraw, Image
import numpy as np
import os
import qrcode
import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
import datetime
import random
from email.mime.image import MIMEImage
from django.core.mail import EmailMultiAlternatives
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

# Create your views here.

def index(request):
    keyword = request.GET.get("keyword")
    if keyword:
        etkinlikler = Article.objects.filter(title__icontains=keyword)
        return render(request,"index.html",{"etkinlikler" : etkinlikler})

    etkinlikler_list = Article.objects.filter(goster=True)
    page = request.GET.get('page', 1)
    paginator = Paginator(etkinlikler_list, 4)
    try:
        etkinlikler = paginator.page(page)
    except PageNotAnInteger:
        etkinlikler = paginator.page(1)
    except EmptyPage:
        etkinlikler = paginator.page(paginator.num_pages)

    return render(request,"index.html",{"etkinlikler" : etkinlikler})

@login_required(login_url = "user:login")
def dashboard(request):
    keyword = request.GET.get("keyword")

    etkinlikler_list = Article.objects.filter(author=request.user)
    page = request.GET.get('page', 1)
    paginator = Paginator(etkinlikler_list, 4)
    try:
        etkinlikler = paginator.page(page)
    except PageNotAnInteger:
        etkinlikler = paginator.page(1)
    except EmptyPage:
        etkinlikler = paginator.page(paginator.num_pages)
    context = {
        "etkinlikler":etkinlikler
    }
    
    if keyword:
        etkinlikler = Article.objects.filter(title__icontains=keyword)
        return render(request,"index.html",{"etkinlikler" : etkinlikler})

    return render(request,"dashboard.html",context)

@login_required(login_url = "user:login")
def addEtkinlik(request):
    keyword = request.GET.get("keyword")
    if keyword:
        etkinlikler = Article.objects.filter(title__icontains=keyword)
        return render(request,"index.html",{"etkinlikler" : etkinlikler})

    form = ArticleForm(request.POST or None,request.FILES or None)
    if form.is_valid():
        etkinlik=form.save(commit=False)
        etkinlik.author = request.user
        etkinlik.etkinlik_tarihi = form.data["etkinlik_tarihi"]
        etkinlik.save()
        messages.success(request,"Etkinlik Oluşturuldu")
        return redirect("article:dashboard")
    return render(request,"etkinlikekle.html",{"form":form})

def detay(request,id):
    print(request.FILES)
    if request.method == 'POST' and request.FILES:
        request.FILES['myfile']
        exel_yukle(request,id=id)
        return redirect('article:detay',id)

    forms = KatilimciForm(request.POST or None)
    addKatilimci(request,id,forms)

    keyword = request.GET.get("keyword")
    if keyword:
        etkinlikler = Article.objects.filter(title__icontains=keyword)
        return render(request,"index.html",{"etkinlikler" : etkinlikler})

    etkinlik = get_object_or_404(Article,id = id)
    return render(request,"detay.html",{"etkinlik":etkinlik,"tablo":tablo(id=id),"form":forms})

@login_required(login_url = "user:login")
def update(request,id):
    keyword = request.GET.get("keyword")
    if keyword:
        etkinlikler = Article.objects.filter(title__icontains=keyword)
        return render(request,"index.html",{"etkinlikler" : etkinlikler})

    etkinlik=get_object_or_404(Article,id=id)
    form = ArticleForm(request.POST or None,request.FILES or None,instance=etkinlik)
    
    if form.is_valid():
        etkinlik=form.save(commit=False)
        etkinlik.author = request.user
        etkinlik.etkinlik_tarihi = form.data["etkinlik_tarihi"]
        etkinlik.save()
        messages.success(request,"Etkinlik Güncellendi")
        return redirect("article:dashboard")
    return render(request,"update.html",{"form":form})

@login_required(login_url = "user:login")
def delete(request,id):
    katilimci_temizle(id)
    etkinlik=get_object_or_404(Article,id=id)
    etkinlik.delete()
    messages.info(request,"Etkinlik Silindi")
    return redirect("article:dashboard")

@login_required(login_url = "user:login")
def exel_yukle(request,id):
    myfile=request.FILES['myfile']
    fs = FileSystemStorage()
    filename = fs.save(myfile.name,myfile)
    uploaded_file_url=fs.url(filename)
    excel_file = urllib.parse.unquote(uploaded_file_url) #urldeki boşlukları görmezden geliyoruz
    empexceldata = pd.read_excel("."+excel_file)
    fs.delete(fs.path(filename)) #işimiz bittikten sonra xls yi sil.
    dbframe = empexceldata
    for dbframe in dbframe.itertuples():
        if tc_kontrol(str(dbframe.tcno)):
            if Katilimci.objects.filter(tc_no=dbframe.tcno).exists():
                a=Katilimci.objects.get(tc_no=dbframe.tcno).etkinlik
                if str(id) in a.split(","):
                    obj = Katilimci.objects.update_or_create(tc_no=dbframe.tcno, defaults={
                                        'isim': dbframe.isim,
                                        'soy_isim': dbframe.soyisim,
                                        'email': dbframe.email})
                else:
                    obj = Katilimci.objects.update_or_create(tc_no=dbframe.tcno, defaults={
                                            'isim': dbframe.isim,
                                            'soy_isim': dbframe.soyisim,
                                            'email': dbframe.email,
                                            'etkinlik': (a+str(id)+',')
                                        })
            else:
                obj = Katilimci.objects.update_or_create(tc_no=dbframe.tcno, defaults={
                                        'isim': dbframe.isim,
                                        'soy_isim': dbframe.soyisim,
                                        'email': dbframe.email,
                                        'etkinlik': (str(id)+',')
                                    })
    messages.success(request,"Veri Tabanı Güncellendi")
    return redirect("article:detay",id=id)

def tablo(id):
    katilimcilar=Katilimci.objects.all()
    bu_etkinlige_katilanlar=[]
    for katilimci in katilimcilar:
        if (str(id) in katilimci.etkinlik.split(",")):
            bu_etkinlige_katilanlar.append(katilimci)
        else:
            pass
    return bu_etkinlige_katilanlar

@login_required(login_url = "user:login")    
def tablo_indir(request,id):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="{}.xls"'.format(id)

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Users')

    # Sheet header, first row
    row_num = 0

    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = ['tcno', 'isim', 'soyisim', 'email', ]

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)

    # Sheet body, remaining rows
    font_style = xlwt.XFStyle()

    rows = Katilimci.objects.all().values_list('tc_no', 'isim', 'soy_isim', 'email','etkinlik')

    for row in rows:
        if (str(id) in row[4].split(",")):
            row_num += 1
            for col_num in range(len(row)-1):
                ws.write(row_num, col_num, row[col_num], font_style)
        else:
            pass
    wb.save(response)
    return response

def addKatilimci(request,id,form):
    forms = form
    if forms.is_valid():
        if Katilimci.objects.filter(tc_no=forms.data['tc_no']).exists():
            a=Katilimci.objects.get(tc_no=forms.data['tc_no']).etkinlik
            if str(id) in a.split(","):
                obj = Katilimci.objects.update_or_create(tc_no=forms.data['tc_no'], defaults={
                                    'isim': forms.data['isim'],
                                    'soy_isim': forms.data['soy_isim'],
                                    'email': forms.data['email']})
            else:
                oobj = Katilimci.objects.update_or_create(tc_no=forms.data['tc_no'], defaults={
                                    'isim': forms.data['isim'],
                                    'soy_isim': forms.data['soy_isim'],
                                    'email': forms.data['email'],
                                    'etkinlik': (a+str(id)+',')
                                    })
        else:
             obj = Katilimci.objects.update_or_create(tc_no=forms.data['tc_no'], defaults={
                                    'isim': forms.data['isim'],
                                    'soy_isim': forms.data['soy_isim'],
                                    'email': forms.data['email'],
                                    'etkinlik': (str(id)+',')
                                    })
        messages.success(request,"Kullanıcı Eklendi")
        return redirect("article:detay",id=id)

@login_required(login_url = "user:login")
def katilimciduzenle(request,id):
    if request.method == "POST":
        secilenler=request.POST.getlist("selected_options")
        for i in secilenler:
            m=Katilimci.objects.get(tc_no=i)
            liste=m.etkinlik.split(",")
            liste.remove(str(id))
            for i in m.etkinlik.split(","):
                guncel=''
                for p in range(0,len(liste)-1):
                    guncel+=liste[p]+',' 
                Katilimci.objects.update_or_create(tc_no=m.tc_no, defaults={
                                                'isim': m.isim,
                                                'soy_isim': m.soy_isim,
                                                'email': m.email,
                                                'etkinlik': (guncel)
                                            })
    katilimcilar_listesi=Katilimci.objects.all()
    bu_etkinlige_katilanlar=[]
    for i in katilimcilar_listesi:
        if str(id) in i.etkinlik.split(','):
            bu_etkinlige_katilanlar.append(i)

    page = request.GET.get('page', 1)
    paginator = Paginator(bu_etkinlige_katilanlar, 15)
    try:
        katilimcilar = paginator.page(page)
    except PageNotAnInteger:
        katilimcilar = paginator.page(1)
    except EmptyPage:
        katilimcilar = paginator.page(paginator.num_pages)
    return render(request,"katilimciduzenle.html",{"tablo":katilimcilar})

@login_required(login_url = "user:login")
def tumkatilimcilar(request):
    if request.method == "POST":
        secilenler=request.POST.getlist("selected_options")
        for i in secilenler:
            Katilimci.objects.filter(tc_no=i).delete()

    katilimcilar_listesi=Katilimci.objects.all()
    page = request.GET.get('page', 1)
    paginator = Paginator(katilimcilar_listesi, 15)
    try:
        katilimcilar = paginator.page(page)
    except PageNotAnInteger:
        katilimcilar = paginator.page(1)
    except EmptyPage:
        katilimcilar = paginator.page(paginator.num_pages)
    return render(request,"tumkatilimcilar.html",{"tablo":katilimcilar})

def katilimci_temizle(id):
    pid=[str(id)]
    for m in tablo(id):
        liste=m.etkinlik.split(",")
        liste.remove(pid[0])
        for i in m.etkinlik.split(","):
            guncel=''
            for p in range(0,len(liste)-1):
                guncel+=liste[p]+',' 
            Katilimci.objects.update_or_create(tc_no=m.tc_no, defaults={
                                            'isim': m.isim,
                                            'soy_isim': m.soy_isim,
                                            'email': m.email,
                                            'etkinlik': (guncel)
                                        })

@login_required(login_url = "user:login")
def sertifika(request):
    form=EtklinlikSec(request.POST or None,request.FILES or None)
    
    if form.is_valid:
        secilen_etkinlik=request.POST.get('etkinlikler')
        if request.method == 'POST' and request.FILES:
            resim=request.FILES['resim']
            fs = FileSystemStorage()
            filename = fs.save(resim.name,resim)
            Sertifikalar.objects.update_or_create(etkinlik_id=int(secilen_etkinlik), defaults={
                                            'sertifika': filename,
                                            'kordinat_isim': request.POST.get("form_x1")+","+request.POST.get("form_y1"),
                                            'kordinat_tarih': request.POST.get("form_x2")+","+request.POST.get("form_y2"),
                                            'kordinat_qr': request.POST.get("form_x3")+","+request.POST.get("form_y3"),
                                        })
            ornek_olustur(int(secilen_etkinlik))
            
         
    return render(request,"sertifika.html",{"form":form})

@login_required(login_url = "user:login")
def sertifikalar(request):
    if request.method == "POST":
        secilenler=request.POST.getlist("selected_options")
        for i in secilenler:
            Sertifikalar.objects.filter(etkinlik_id=i).delete()

    Sertifika_listesi = Sertifikalar.objects.all()
    page = request.GET.get('page', 1)
    paginator = Paginator(Sertifika_listesi, 5)
    try:
        Sertifika = paginator.page(page)
    except PageNotAnInteger:
        Sertifika = paginator.page(1)
    except EmptyPage:
        Sertifika = paginator.page(paginator.num_pages)
    return render(request,"sertifikalar.html",{"tablo":Sertifika})

@login_required(login_url = "user:login")
def sertifikapaneli(request):
    etkinlikler_listesi = Article.objects.all()
    katilimci_sayisi=Katilimci.objects.all()
    counter_list=[]
    sozluk={}
    deneme_list=[]
    
    page = request.GET.get('page', 1)
    paginator = Paginator(etkinlikler_listesi, 10)
    try:
        etkinlikler = paginator.page(page)
    except PageNotAnInteger:
        etkinlikler = paginator.page(1)
    except EmptyPage:
        etkinlikler = paginator.page(paginator.num_pages)
    for a in etkinlikler:
        counter=0
        for i in katilimci_sayisi:
            if str(a.id) in i.etkinlik.split(','):
                counter+=1
        deneme_list.append(a.id)
        counter_list.append(counter)
        sozluk=dict(zip(deneme_list, counter_list))
    context = {
        "etkinlikler":etkinlikler,
        "sozluk":sozluk
    }
    
    return render(request,"sertifikapaneli.html",context)

@login_required(login_url = "user:login")
def sertifikaolustur(request,id):
    if Sertifikalar.objects.filter(etkinlik_id=id).exists():
        kordinatlar_isim = Sertifikalar.objects.get(etkinlik_id=id).kordinat_isim.split(',')
        kordinatlar_tarih = Sertifikalar.objects.get(etkinlik_id=id).kordinat_tarih.split(',')
        kordinatlar_qr = Sertifikalar.objects.get(etkinlik_id=id).kordinat_qr.split(',')
        katilimci_listesi=Katilimci.objects.all()
        mevcut_sertifikalar=VeritabaniSertifikalar.objects.all()
        mevcut_sertifikalar_listesi=[]
        for s in mevcut_sertifikalar:
            mevcut_sertifikalar_listesi.append(s.katilimci_tc)
        for i in katilimci_listesi:
            if str(id) in i.etkinlik.split(",") and (i.tc_no not in mevcut_sertifikalar_listesi):
                name_to_print=i.isim+"    "+i.soy_isim
                date_to_print=datetime.datetime.strptime(str(Article.objects.get(id=id).etkinlik_tarihi), '%Y-%m-%d').strftime('%m/%d/%Y')
                sid=random.randint(111111111111,999999999999)
                url=request.scheme+"://"+request.META['HTTP_HOST']+"/kontrol/"+str(sid)
                VeritabaniSertifikalar.objects.update_or_create(sertifika_id=sid, defaults={"sertifika_etkinlik_id":id,"katilimci_email":i.email,"katilimci_tc":i.tc_no,"sertifika_mevcut":True,"ad_soyad":name_to_print})
                image = cv.imread("."+Sertifikalar.objects.get(etkinlik_id=id).sertifika.url)
                cv_im_rgb = cv.cvtColor(image,cv.COLOR_BGR2RGB)
                pil_im = Image.fromarray(cv_im_rgb)
                draw = ImageDraw.Draw(pil_im)
                font = ImageFont.truetype(settings.FONTS_ROOT + "/Yellowtail-Regular.ttf", 25)
                font1 = ImageFont.truetype(settings.FONTS_ROOT + "/Yellowtail-Regular.ttf", 25) 
                draw.text((int(kordinatlar_isim[0]), int(kordinatlar_isim[1])), name_to_print, font=font , fill='red')
                draw.text((int(kordinatlar_tarih[0]), int(kordinatlar_tarih[1])), date_to_print , font=font1, fill='blue')
                pil_im.paste(qr_code(url), (int(kordinatlar_qr[0]), int(kordinatlar_qr[1])))
                cv_im_processed = cv.cvtColor(np.array(pil_im), cv.COLOR_RGB2BGR)
                uploaded_file_url=os.path.join(settings.MEDIA_ROOT)+"/sertifikalar/"+str(sid)
                cv.imwrite(uploaded_file_url+'.png',cv_im_processed)
            elif (i.tc_no in mevcut_sertifikalar_listesi) and not(VeritabaniSertifikalar.objects.get(katilimci_tc=i.tc_no).sertifika_mevcut):
                name_to_print=i.isim+"    "+i.soy_isim
                date_to_print=datetime.datetime.strptime(str(Article.objects.get(id=id).etkinlik_tarihi), '%Y-%m-%d').strftime('%m/%d/%Y')
                sid=VeritabaniSertifikalar.objects.get(katilimci_tc=i.tc_no).sertifika_id
                url=request.scheme+"://"+request.META['HTTP_HOST']+"/kontrol/"+str(sid)
                VeritabaniSertifikalar.objects.update_or_create(sertifika_id=sid, defaults={"sertifika_etkinlik_id":id,"katilimci_email":i.email,"katilimci_tc":i.tc_no,"sertifika_mevcut":True,"ad_soyad":name_to_print})
                image = cv.imread("."+Sertifikalar.objects.get(etkinlik_id=id).sertifika.url)
                cv_im_rgb = cv.cvtColor(image,cv.COLOR_BGR2RGB)
                pil_im = Image.fromarray(cv_im_rgb)
                draw = ImageDraw.Draw(pil_im)
                font = ImageFont.truetype(settings.FONTS_ROOT + "/Yellowtail-Regular.ttf", 25)
                font1 = ImageFont.truetype(settings.FONTS_ROOT + "/Yellowtail-Regular.ttf", 25) 
                draw.text((int(kordinatlar_isim[0]), int(kordinatlar_isim[1])), name_to_print, font=font , fill='red')
                draw.text((int(kordinatlar_tarih[0]), int(kordinatlar_tarih[1])), date_to_print , font=font1, fill='blue')
                pil_im.paste(qr_code(url), (int(kordinatlar_qr[0]), int(kordinatlar_qr[1])))
                cv_im_processed = cv.cvtColor(np.array(pil_im), cv.COLOR_RGB2BGR)
                uploaded_file_url=os.path.join(settings.MEDIA_ROOT)+"/sertifikalar/"+str(sid)
                cv.imwrite(uploaded_file_url+'.png',cv_im_processed)
    else:
        messages.info(request,"Henüz Sertifika Tanımlanmamış")

    return redirect("article:sertifikapaneli")

@login_required(login_url = "user:login")
def sertifikalistesi(request,id):
    mevcut_sertifikalar_listesi=VeritabaniSertifikalar.objects.filter(sertifika_etkinlik_id=id)
    if request.method == "POST":
        secilenler=request.POST.getlist("selected_options")
        if request.POST.get("mail_gonder")=="1":
            for i in secilenler:
                mail_gonder(i)
        if request.POST.get("sil")=="1":
            for i in secilenler:
                if VeritabaniSertifikalar.objects.get(sertifika_id=i).sertifika_mevcut:
                    sertifika_sil(i,1)
                VeritabaniSertifikalar.objects.filter(sertifika_id=i).delete()
        if request.POST.get("sil_resim")=="1":
            for i in secilenler:
                sertifika_sil(i,2)
        if request.POST.get("google_yukle")=="1":
            for i in secilenler:
                if VeritabaniSertifikalar.objects.get(sertifika_id=i).sertifika_mevcut:
                    google_yukle(i)
    page = request.GET.get('page', 1)
    paginator = Paginator(mevcut_sertifikalar_listesi, 15)
    try:
        mevcut_sertifikalar = paginator.page(page)
    except PageNotAnInteger:
        mevcut_sertifikalar = paginator.page(1)
    except EmptyPage:
        mevcut_sertifikalar = paginator.page(paginator.num_pages)
    return render(request,"sertifikalistesi.html",{"mevcut_sertifikalar":mevcut_sertifikalar})

def sertifika_sil(sertifika_id,islem):
    if VeritabaniSertifikalar.objects.get(sertifika_id=sertifika_id).sertifika_mevcut:
        Dosya_konumu = settings.MEDIA_ROOT+"/sertifikalar"
        Dosya_adı = str(sertifika_id)+".png"
        os.remove(os.path.join(Dosya_konumu, Dosya_adı))
        if islem == 2:
            VeritabaniSertifikalar.objects.update_or_create(sertifika_id=sertifika_id, defaults={"sertifika_mevcut":False})

def ornek_olustur(id):
    kordinatlar_isim = Sertifikalar.objects.get(etkinlik_id=id).kordinat_isim.split(',')
    kordinatlar_tarih = Sertifikalar.objects.get(etkinlik_id=id).kordinat_tarih.split(',')
    kordinatlar_qr = Sertifikalar.objects.get(etkinlik_id=id).kordinat_qr.split(',')
    name_to_print = "Mesut Duman"
    date_to_print = "12/05/2022"
    url="https://www.google.com/search?q="+str(id)
    image = cv.imread("."+Sertifikalar.objects.get(etkinlik_id=id).sertifika.url)
    cv_im_rgb = cv.cvtColor(image,cv.COLOR_BGR2RGB)
    pil_im = Image.fromarray(cv_im_rgb)
    draw = ImageDraw.Draw(pil_im)
    font = ImageFont.truetype(settings.FONTS_ROOT + "/Yellowtail-Regular.ttf", 25)
    font1 = ImageFont.truetype(settings.FONTS_ROOT + "/Yellowtail-Regular.ttf", 25) 
    draw.text((int(kordinatlar_isim[0]), int(kordinatlar_isim[1])), name_to_print, font=font , fill='red')
    draw.text((int(kordinatlar_tarih[0]), int(kordinatlar_tarih[1])), date_to_print , font=font1, fill='blue')
    pil_im.paste(qr_code(url), (int(kordinatlar_qr[0]), int(kordinatlar_qr[1])))
    cv_im_processed = cv.cvtColor(np.array(pil_im), cv.COLOR_RGB2BGR)
    uploaded_file_url=os.path.join(settings.MEDIA_ROOT)+"/"+str(id)
    cv.imwrite(uploaded_file_url+'.png',cv_im_processed)
    filename=(str(id)+'.png')
    Sertifikalar.objects.update_or_create(etkinlik_id=id,defaults={'ornek_sertifika':filename})

def qr_code(url):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=2,
        border=2,
    )
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="Black", back_color="white").convert('RGB')
    return img

def google_yukle(sertifika_id):
    Dosya_konumu = settings.MEDIA_ROOT+"/sertifikalar"
    Dosya_adı = str(sertifika_id)+".png"
   

    SCOPES = ['https://www.googleapis.com/auth/drive']
    creds = None
    json="./drive/token.json"
    filename = Dosya_adı
    path=os.path.join(Dosya_konumu, Dosya_adı)
    if os.path.exists(json):
        creds = Credentials.from_authorized_user_file(json, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open(json, 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('drive', 'v3', credentials=creds)
        file_metadata = {

            'name': str(filename),
            'parents': ['1OT3QPdJ4_cPnIcUEhi1hrhz53ojba1Cs']

        }
        media = MediaFileUpload(path, mimetype='image/jpg')
        file = service.files().create(body=file_metadata,
                                            media_body=media,
                                            fields='id').execute()

    except HttpError as error:
        # TODO(developer) - Handle errors from drive API.
        raise f'An error occurred: {error}'

def kontrol (request,id):
    if VeritabaniSertifikalar.objects.filter(sertifika_id=id).exists():
        sahip=VeritabaniSertifikalar.objects.get(sertifika_id=id).ad_soyad
        messages.success(request,"Sertifika %s Adına Kayıtlı"% sahip)
        return render(request,"kontrol.html")
    else:
        messages.info(request,"Sertifika Mevcut Değil")
        return render(request,"kontrol.html")

def mail_gonder (sertifika_id):
    if VeritabaniSertifikalar.objects.get(sertifika_id=sertifika_id).sertifika_mevcut:
        subject = 'Etkinliğe Katılım Sertifikası'
        image = str(VeritabaniSertifikalar.objects.get(sertifika_id=sertifika_id).sertifika_id)+".png"
        body_html = '''
        <html>
            <body>
                <img src="cid:{image}" />
            </body>
        </html>
        '''.format(image=image)

        from_email = settings.EMAIL_HOST_USER
        to_email = VeritabaniSertifikalar.objects.get(sertifika_id=sertifika_id).katilimci_email

        msg = EmailMultiAlternatives(
            subject,
            body_html,
            from_email=from_email,
            to=[to_email]
        )

        msg.mixed_subtype = 'related'
        msg.attach_alternative(body_html, "text/html")
        img_dir = 'media/sertifikalar'
        file_path = os.path.join(img_dir, image)
        f=open(file_path,"rb")
        img = MIMEImage(f.read(), 'png')
        img.add_header('Content-ID', '<{name}>'.format(name=image))
        img.add_header('Content-Disposition', 'inline', filename=image)   
        msg.attach(img)

        msg.send()
  