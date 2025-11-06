# imoveis/forms.py
from django import forms
# 1. Importamos o modelo Imobiliaria
from .models import Imovel, Imobiliaria 

# 1. A CORREÇÃO CRUCIAL ESTÁ AQUI
class MultipleFileInput(forms.FileInput):
    def __init__(self, attrs=None):
        default_attrs = {'multiple': True}
        if attrs:
            default_attrs.update(attrs)
        
        # 2. USAMOS O MÉTODO __INIT__ DO "AVÔ" (forms.Input) PARA PULAR A TRAVA DE SEGURANÇA
        # DO "PAI" (forms.FileInput)
        super(forms.FileInput, self).__init__(default_attrs)

class ImovelForm(forms.ModelForm):
    fotos_galeria = forms.FileField(
        widget=MultipleFileInput(),
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
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # --- [INÍCIO DA MUDANÇA] ---
        # Torna o campo 'imobiliaria' opcional, 
        # pois um usuário "Particular" não terá uma.
        self.fields['imobiliaria'].required = False
        # --- [FIM DA MUDANÇA] ---
        
        for field_name, field in self.fields.items():
            if not isinstance(field.widget, (forms.Select, forms.Textarea, forms.FileInput)):
                field.widget.attrs['class'] = 'form-control'


# --- NOVO FORMULÁRIO PARA CADASTRO PÚBLICO DE IMOBILIÁRIA ---
class ImobiliariaForm(forms.ModelForm):
    class Meta:
        model = Imobiliaria
        # Lista de campos que você pediu:
        fields = [
            'nome',
            'endereco',
            'cidade',
            'telefone',
            'telefone_secundario',
            'site',
            'rede_social',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Adiciona a classe 'form-control' a todos os campos
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
        
        # Deixa o campo 'cidade' com o estilo 'form-select'
        self.fields['cidade'].widget.attrs['class'] = 'form-select'
        
        # Adiciona placeholders
        self.fields['nome'].widget.attrs['placeholder'] = 'Nome Fantasia da Imobiliária'
        self.fields['telefone'].widget.attrs['placeholder'] = '(00) 0000-0000'
        self.fields['telefone_secundario'].widget.attrs['placeholder'] = '(00) 90000-0000 (WhatsApp)'
        self.fields['site'].widget.attrs['placeholder'] = 'https://www.suaimobiliaria.com'
        self.fields['rede_social'].widget.attrs['placeholder'] = 'https://www.instagram.com/seuimovel'