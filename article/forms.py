from django import forms
from .models import Article,Katilimci
index_list=[]
etklink_listesi=list(Article.objects.filter().values_list('id',flat=True))
for i in range(1,len(etklink_listesi)+1):
    index_list.append((str(i),str(etklink_listesi[i-1])))

class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ["goster","title","etkinlik_tarihi","content","etkinlik_poster"]
    etkinlik_tarihi = forms.DateField(widget=forms.TextInput(attrs={'type': 'date'}))

class KatilimciForm(forms.ModelForm):
    class Meta:
        model=Katilimci
        fields = ["tc_no","isim","soy_isim","email"]
    def clean(self):
        TCKN=str(self.cleaned_data['tc_no'])
        tc_kontrol(TCKN)
        pass
def tc_kontrol(No):
        Uzunluk=len(No)
        c1=((int(No[0])+int(No[2])+int(No[4])+int(No[6])+int(No[8]))*7-(int(No[1])+int(No[3])+int(No[5])+int(No[7])))%10
        c2=(int(No[0])+int(No[1])+int(No[2])+int(No[3])+int(No[4])+int(No[5])+int(No[6])+int(No[7])+int(No[8])+c1)%10
        if len(No)==11 and c1==int(No[9]) and c2==int(No[10]):
            return True
        else:
            raise forms.ValidationError('Tc Kimlik Numarası Tanımsız: %s' % No)

class EtklinlikSec(forms.Form):
    etkinlikler = forms.ModelChoiceField(queryset=Article.objects.filter().values_list('id',flat=True),empty_label=None,label="Hangi Etkinlik?")
