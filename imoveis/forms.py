# imoveis/forms.py
from django import forms
from .models import Imovel, Imobiliaria, Cidade, Bairro 
from decimal import Decimal, InvalidOperation

# Classe MultipleFileInput (sem alteração)
class MultipleFileInput(forms.FileInput):
    def __init__(self, attrs=None):
        default_attrs = {'multiple': True}
        if attrs:
            default_attrs.update(attrs)
        super(forms.FileInput, self).__init__(default_attrs)


class ImovelForm(forms.ModelForm):
    fotos_galeria = forms.FileField(
        widget=MultipleFileInput(attrs={'class': 'form-control'}), 
        required=False,
        label='Fotos da Galeria (selecione várias)'
    )

    # --- ✅ MUDANÇA 1: DEFINIR OS CAMPOS 'PRECO' E 'TELEFONE' AQUI FORA ---
    # Isso força o Django a tratá-los como campos de TEXTO (CharField)
    # permitindo que a máscara e a limpeza funcionem.
    preco = forms.CharField(
        label='Preço (R$)',
        widget=forms.TextInput(attrs={
            'class': 'form-control', 
            'placeholder': 'R$ 0,00'
        })
    )
    
    telefone_contato = forms.CharField(
        label='Telefone para Contato Direto',
        required=False, # <-- Torne opcional se desejar
        widget=forms.TextInput(attrs={
            'class': 'form-control', 
            'placeholder': '(00) 00000-0000'
        })
    )

    class Meta:
        model = Imovel
        
        # --- ✅ MUDANÇA 2: REMOVER 'preco' E 'telefone_contato' DE 'fields' ---
        fields = [
            'finalidade', 'imobiliaria', 'cidade', 'bairro', 'titulo', 'descricao', 
            'endereco', 'quartos', 'suites', 'banheiros', 'salas', 
            'cozinhas', 'closets', 'area', 'foto_principal'
        ]
        
        # --- ✅ MUDANÇA 3: REMOVER 'preco' E 'telefone_contato' DOS 'widgets' ---
        widgets = {
            # Campos de Seleção
            'finalidade': forms.Select(attrs={'class': 'form-select'}),
            'imobiliaria': forms.Select(attrs={'class': 'form-select'}),
            'cidade': forms.Select(attrs={'class': 'form-select'}),
            'bairro': forms.Select(attrs={'class': 'form-select'}),
            
            # Campos de Texto
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'endereco': forms.TextInput(attrs={'class': 'form-control'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            
            # Campos Numéricos (continuam NumberInput)
            'area': forms.NumberInput(attrs={'class': 'form-control'}),
            'quartos': forms.NumberInput(attrs={'class': 'form-control', 'value': 0}),
            'suites': forms.NumberInput(attrs={'class': 'form-control', 'value': 0}),
            'banheiros': forms.NumberInput(attrs={'class': 'form-control', 'value': 0}),
            'salas': forms.NumberInput(attrs={'class': 'form-control', 'value': 0}),
            'cozinhas': forms.NumberInput(attrs={'class': 'form-control', 'value': 0}),
            'closets': forms.NumberInput(attrs={'class': 'form-control', 'value': 0}),

            # Campos de Arquivo
            'foto_principal': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['imobiliaria'].required = False
        
    # --- ✅ MUDANÇA 4: ESTA FUNÇÃO 'clean_preco' AGORA VAI FUNCIONAR ---
    # Ela receberá o texto "250.000,00" (string) e não mais um Decimal.
    def clean_preco(self):
        preco_str = self.cleaned_data.get('preco')
        
        if not preco_str:
            return None 

        # Limpa o valor (ex: "250.000,00" -> "250000.00")
        preco_limpo = preco_str.replace('.', '').replace(',', '.')
        
        try:
            preco_decimal = Decimal(preco_limpo)
            return preco_decimal
        except InvalidOperation:
            raise forms.ValidationError("Valor de preço inválido.")

    # --- BÔNUS: Adicione também a limpeza do telefone ---
    def clean_telefone_contato(self):
        telefone_str = self.cleaned_data.get('telefone_contato')
        if not telefone_str:
            return None
        
        # Remove ( ) - e espaços
        telefone_limpo = telefone_str.translate(str.maketrans('', '', '()- '))
        return telefone_limpo


# --- FORMULÁRIO DE IMOBILIÁRIA (Sem alteração) ---
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