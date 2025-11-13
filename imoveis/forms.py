from django import forms
# ✅ 1. IMPORTAÇÕES CORRIGIDAS (todos os modelos necessários)
from .models import Imovel, Imobiliaria, Cidade, Bairro, NichoParceiro, Parceiro 
# Não precisamos mais de 'Decimal' ou 'InvalidOperation'

# Classe MultipleFileInput (sem alteração)
class MultipleFileInput(forms.FileInput):
    def __init__(self, attrs=None):
        default_attrs = {'multiple': True}
        if attrs:
            default_attrs.update(attrs)
        super(forms.FileInput, self).__init__(default_attrs)


# (Este formulário está CORRETO - sem a máscara)
class ImovelForm(forms.ModelForm):
    fotos_galeria = forms.FileField(
        widget=MultipleFileInput(attrs={'class': 'form-control'}), 
        required=False,
        label='Fotos da Galeria (selecione várias)'
    )

    class Meta:
        model = Imovel
        
        fields = [
            'finalidade', 'imobiliaria', 'cidade', 'bairro', 'titulo', 'descricao', 
            'endereco', 'preco', 'telefone_contato', 'quartos', 'suites', 'banheiros', 'salas', 
            'cozinhas', 'closets', 'area', 'foto_principal'
        ]
        
        widgets = {
            'finalidade': forms.Select(attrs={'class': 'form-select'}),
            'imobiliaria': forms.Select(attrs={'class': 'form-select'}),
            'cidade': forms.Select(attrs={'class': 'form-select'}),
            'bairro': forms.Select(attrs={'class': 'form-select'}),
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'endereco': forms.TextInput(attrs={'class': 'form-control'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            
            # Voltaram a ser campos normais
            'preco': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ex: 250000.00'}),
            'telefone_contato': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '(00) 00000-0000'}),
            
            'area': forms.NumberInput(attrs={'class': 'form-control'}),
            'quartos': forms.NumberInput(attrs={'class': 'form-control', 'value': 0}),
            'suites': forms.NumberInput(attrs={'class': 'form-control', 'value': 0}),
            'banheiros': forms.NumberInput(attrs={'class': 'form-control', 'value': 0}),
            'salas': forms.NumberInput(attrs={'class': 'form-control', 'value': 0}),
            'cozinhas': forms.NumberInput(attrs={'class': 'form-control', 'value': 0}),
            'closets': forms.NumberInput(attrs={'class': 'form-control', 'value': 0}),
            'foto_principal': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['imobiliaria'].required = False


# --- FORMULÁRIO ImobiliariaForm (continua igual) ---
class ImobiliariaForm(forms.ModelForm):
    class Meta:
        model = Imobiliaria
        fields = [
            'nome', 'creci', 'endereco', 'cidade',
            'telefone', 'telefone_secundario', 'site', 'rede_social',
        ]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
        self.fields['cidade'].widget.attrs['class'] = 'form-select'
        self.fields['nome'].widget.attrs['placeholder'] = 'Nome Fantasia da Imobiliária'
        self.fields['creci'].widget.attrs['placeholder'] = 'CRECI (ex: 12345-J ou 12345-F)'
        self.fields['endereco'].widget.attrs['placeholder'] = 'Rua, Número e Bairro'
        self.fields['telefone'].widget.attrs['placeholder'] = '(00) 0000-0000'
        self.fields['telefone_secundario'].widget.attrs['placeholder'] = '(00) 90000-0000 (WhatsApp)'
        self.fields['site'].widget.attrs['placeholder'] = 'https://www.suaimobiliaria.com'
        self.fields['rede_social'].widget.attrs['placeholder'] = 'https://www.instagram.com/seuimovel'

# --- ✅ CORREÇÃO NO ParceiroForm ---
class ParceiroForm(forms.ModelForm):
    
    nicho = forms.ModelChoiceField(
        queryset=NichoParceiro.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Qual seu nicho de atuação?"
    )

    class Meta:
        model = Parceiro
        # ✅ 'logo' FOI REMOVIDO DESTA LISTA 'fields'
        fields = [
            'nicho', 'nome', 'descricao', 
            'telefone', 'whatsapp', 'email' 
        ]
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Casa das Telhas ou João da Silva Pintor'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Descreva brevemente seus serviços...'}),
            'telefone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '(00) 0000-0000'}),
            'whatsapp': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '(00) 90000-0000'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            #'logo': forms.FileInput(attrs={'class': 'form-control'}),
        }